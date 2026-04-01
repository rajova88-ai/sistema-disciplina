#!/usr/bin/env python3
# ============================================================================
# MÓDULO DE DETERMINACIÓN FINAL - SISTEMA DISCIPLINARIO LOCAL
# Análisis IA + Validación de Resolución
# ============================================================================

import json
import sqlite3
import uuid
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import hashlib
import os
import re

# Importar librerías para IA local
try:
    import requests
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


@dataclass
class CaseSummary:
    """Resumen ejecutivo del caso"""
    case_id: str
    case_number: str
    case_title: str
    complainant_name: str
    respondent_name: str
    complaint_date: str
    case_description: str
    days_elapsed: int


@dataclass
class Hearing:
    """Datos de una comparecencia"""
    hearing_id: str
    participant_name: str
    participant_role: str
    hearing_date: str
    transcript_text: str


@dataclass
class Evidence:
    """Datos de una prueba"""
    evidence_id: str
    evidence_type: str
    evidence_description: str
    received_date: str


@dataclass
class StatutoryArticle:
    """Artículo del estatuto aplicable"""
    article_id: str
    article_number: str
    article_title: str
    article_text: str
    sanction_severity_level: int
    applicable_sanctions: List[str]


@dataclass
class AIRecommendation:
    """Recomendación final de la IA"""
    recommendation_id: str
    case_id: str
    primary_recommendation: str  # 'amonestacion', 'conciliacion', 'consignacion'
    confidence_score: float
    case_summary: str
    key_findings: List[str]
    applicable_articles: List[StatutoryArticle]
    legal_justification: str
    statute_citations: List[Dict]
    alternative_1: Optional[str] = None
    alternative_1_confidence: Optional[float] = None
    alternative_2: Optional[str] = None
    alternative_2_confidence: Optional[float] = None


class DeterminationEngine:
    """
    Motor de Determinación: Procesa expediente completo y genera
    recomendación de resolución basada en IA y estatutos.
    """

    def __init__(self, db_path: str = "disciplinary_system.db"):
        """
        Inicializa el motor de determinación.
        
        Args:
            db_path: Ruta a la base de datos SQLite local
        """
        self.db_path = db_path
        self.ollama_endpoint = "http://localhost:11434"
        self.model = "llama3:latest"
        self.rag_threshold = 0.6

    def get_db_connection(self) -> sqlite3.Connection:
        """Obtiene conexión a base de datos con row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # ========================================================================
    # 1. RECOPILACIÓN DE EXPEDIENTE
    # ========================================================================

    def retrieve_case_summary(self, case_id: str) -> CaseSummary:
        """
        Recupera resumen ejecutivo del caso de la base de datos.
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT case_id, case_number, case_title, complainant_name, 
                   respondent_name, complaint_date, case_description
            FROM cases
            WHERE case_id = ?
        """, (case_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise ValueError(f"Caso {case_id} no encontrado")

        complaint_date = datetime.strptime(row['complaint_date'], '%Y-%m-%d')
        days_elapsed = (datetime.now() - complaint_date).days

        return CaseSummary(
            case_id=row['case_id'],
            case_number=row['case_number'],
            case_title=row['case_title'],
            complainant_name=row['complainant_name'],
            respondent_name=row['respondent_name'],
            complaint_date=row['complaint_date'],
            case_description=row['case_description'],
            days_elapsed=days_elapsed
        )

    def retrieve_hearings(self, case_id: str) -> List[Hearing]:
        """
        Recupera todas las comparecencias/audiencias del caso.
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT hearing_id, participant_name, participant_role, 
                   hearing_date, transcript_text
            FROM hearings
            WHERE case_id = ?
            ORDER BY hearing_date ASC
        """, (case_id,))

        rows = cursor.fetchall()
        conn.close()

        return [
            Hearing(
                hearing_id=row['hearing_id'],
                participant_name=row['participant_name'],
                participant_role=row['participant_role'],
                hearing_date=row['hearing_date'],
                transcript_text=row['transcript_text'] or "[Sin transcripción]"
            )
            for row in rows
        ]

    def retrieve_evidence(self, case_id: str) -> List[Evidence]:
        """
        Recupera todas las pruebas del caso.
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT evidence_id, evidence_type, evidence_description, received_date
            FROM evidence
            WHERE case_id = ?
            ORDER BY received_date DESC
        """, (case_id,))

        rows = cursor.fetchall()
        conn.close()

        return [
            Evidence(
                evidence_id=row['evidence_id'],
                evidence_type=row['evidence_type'],
                evidence_description=row['evidence_description'],
                received_date=row['received_date']
            )
            for row in rows
        ]

    # ========================================================================
    # 2. ANÁLISIS ESTATUTARIO (RAG - Búsqueda Artículos Relevantes)
    # ========================================================================

    def retrieve_applicable_articles(
        self, 
        case_id: str, 
        case_summary: str,
        threshold: float = 0.6
    ) -> List[StatutoryArticle]:
        """
        Recupera artículos estatutarios relevantes basado en análisis semántico
        del resumen del caso.
        
        Esta es la búsqueda RAG (Retrieval-Augmented Generation):
        1. Se extrae contexto del caso
        2. Se buscan artículos con similitud semántica
        3. Se filtran por score de aplicabilidad
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Primero, obtener artículos que ya fueron marcados como aplicables
        # para este caso en statutory_analysis
        cursor.execute("""
            SELECT DISTINCT sa.statute_article_id
            FROM statutory_analysis sa
            WHERE sa.case_id = ? AND sa.applicability_score >= ?
            ORDER BY sa.applicability_score DESC
        """, (case_id, threshold))

        applied_article_ids = [row[0] for row in cursor.fetchall()]

        # Si hay artículos previamente analizados, recuperarlos
        applicable_articles = []
        for article_id in applied_article_ids:
            cursor.execute("""
                SELECT article_id, article_number, article_title, 
                       article_full_text, sanction_severity_level, applicable_sanctions
                FROM statute_articles
                WHERE article_id = ?
            """, (article_id,))

            row = cursor.fetchone()
            if row:
                applicable_articles.append(StatutoryArticle(
                    article_id=row['article_id'],
                    article_number=row['article_number'],
                    article_title=row['article_title'],
                    article_text=row['article_full_text'],
                    sanction_severity_level=row['sanction_severity_level'],
                    applicable_sanctions=json.loads(row['applicable_sanctions'] or '[]')
                ))

        conn.close()

        return applicable_articles

    def perform_rag_analysis(
        self,
        case_id: str,
        case_summary_text: str,
        hearings: List[Hearing],
        evidence: List[Evidence]
    ) -> List[StatutoryArticle]:
        """
        Realiza análisis RAG completo:
        1. Procesa textos de caso, transcripciones, evidencias
        2. Busca artículos relevantes en estatutos
        3. Calcula scores de aplicabilidad
        4. Guarda análisis en DB para auditoria
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Construir contexto completo del caso
        context_parts = [
            f"Resumen del Caso: {case_summary_text}"
        ]

        # Agregar transcripciones
        for hearing in hearings:
            context_parts.append(
                f"Declaración de {hearing.participant_name} "
                f"({hearing.participant_role}): {hearing.transcript_text[:500]}"
            )

        # Agregar evidencias
        for ev in evidence:
            context_parts.append(
                f"Evidencia ({ev.evidence_type}): {ev.evidence_description[:300]}"
            )

        full_context = "\n\n".join(context_parts)

        # Obtener todos los artículos disponibles
        cursor.execute("""
            SELECT article_id, article_number, article_title, 
                   article_full_text, sanction_severity_level, applicable_sanctions
            FROM statute_articles
            ORDER BY article_number
        """)

        all_articles = cursor.fetchall()
        applicable_articles = []

        # Para cada artículo, calcular score de aplicabilidad
        for article_row in all_articles:
            article_text = article_row['article_full_text']
            
            # Cálculo simple de relevancia: palabras clave coincidentes
            # (En producción: usar embeddings vectoriales para búsqueda semántica)
            relevance_score = self._calculate_article_relevance(
                full_context,
                article_text
            )

            if relevance_score >= self.rag_threshold:
                # Guardar análisis estatutario en DB
                analysis_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO statutory_analysis (
                        analysis_id, case_id, statute_article_id,
                        article_number, article_title, article_text,
                        article_sanctions, applicability_score,
                        analyzed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    analysis_id,
                    case_id,
                    article_row['article_id'],
                    article_row['article_number'],
                    article_row['article_title'],
                    article_text,
                    article_row['applicable_sanctions'],
                    relevance_score,
                    datetime.now().isoformat()
                ))

                applicable_articles.append(StatutoryArticle(
                    article_id=article_row['article_id'],
                    article_number=article_row['article_number'],
                    article_title=article_row['article_title'],
                    article_text=article_text,
                    sanction_severity_level=article_row['sanction_severity_level'],
                    applicable_sanctions=json.loads(
                        article_row['applicable_sanctions'] or '[]'
                    )
                ))

        conn.commit()
        conn.close()

        return applicable_articles

    def _calculate_article_relevance(self, context: str, article_text: str) -> float:
        """
        Calcula relevancia semántica entre contexto del caso y artículo.
        
        Versión Simple: Basada en palabras clave
        En producción: Usar embeddings vectoriales (sentence-transformers, etc)
        """
        context_lower = context.lower()
        article_lower = article_text.lower()

        # Extraer palabras clave del artículo (sin stopwords)
        article_words = set(re.findall(r'\b\w{4,}\b', article_lower))
        
        # Calcular cobertura de palabras del artículo en el contexto
        matches = sum(1 for word in article_words if word in context_lower)
        
        if len(article_words) == 0:
            return 0.0

        relevance = matches / len(article_words)
        return min(relevance, 1.0)

    # ========================================================================
    # 3. ANÁLISIS CON IA LOCAL (Ollama/Llama3)
    # ========================================================================

    def generate_ai_recommendation(
        self,
        case_id: str,
        case_summary: CaseSummary,
        hearings: List[Hearing],
        evidence: List[Evidence],
        applicable_articles: List[StatutoryArticle]
    ) -> AIRecommendation:
        """
        Genera recomendación de resolución usando IA local (Ollama).
        
        El prompt está diseñado para:
        1. Analizar hechos del caso
        2. Contrastar con artículos estatutarios
        3. Recomendar: Amonestación, Conciliación o Consignación
        4. Proporcionar fundamentación legal
        """

        # Preparar contexto para la IA
        case_context = self._prepare_case_context(
            case_summary,
            hearings,
            evidence,
            applicable_articles
        )

        # Construir prompt especializado para determinación disciplinaria
        prompt = self._build_determination_prompt(
            case_context,
            applicable_articles
        )

        print(f"\n{'='*80}")
        print("ENVIANDO A IA LOCAL (Ollama)...")
        print(f"{'='*80}\n")

        # Llamar a Ollama (IA local)
        try:
            if not OLLAMA_AVAILABLE:
                raise ImportError("requests no disponible")

            response = requests.post(
                f"{self.ollama_endpoint}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "temperature": 0.3,  # Baja temperatura para determinaciones legales
                    "top_p": 0.9,
                    "num_predict": 2000
                },
                timeout=120
            )
            response.raise_for_status()
            ai_response = response.json()['response']

        except Exception as e:
            print(f"⚠️  Error conectando a Ollama: {e}")
            print("Usando lógica de fallback basada en reglas...")
            ai_response = self._rule_based_determination(
                case_summary,
                applicable_articles
            )

        # Parsear respuesta de la IA
        recommendation = self._parse_ai_response(
            ai_response,
            case_id,
            applicable_articles
        )

        # Guardar recomendación en DB
        self._save_recommendation_to_db(recommendation)

        return recommendation

    def _prepare_case_context(
        self,
        case_summary: CaseSummary,
        hearings: List[Hearing],
        evidence: List[Evidence],
        applicable_articles: List[StatutoryArticle]
    ) -> str:
        """Prepara contexto consolidado para la IA"""
        context = f"""
RESUMEN DEL CASO DISCIPLINARIO
================================

Número de Expediente: {case_summary.case_number}
Título: {case_summary.case_title}
Denunciante: {case_summary.complainant_name}
Denunciado: {case_summary.respondent_name}
Fecha de Denuncia: {case_summary.complaint_date}
Días Transcurridos: {case_summary.days_elapsed}

Descripción:
{case_summary.case_description}

COMPARECENCIAS Y TESTIMONIOS
=============================
"""
        for i, hearing in enumerate(hearings, 1):
            context += f"""
Comparecencia {i}: {hearing.participant_name} ({hearing.participant_role})
Fecha: {hearing.hearing_date}
Testimonio:
{hearing.transcript_text[:1000]}...
"""

        context += "\nEVIDENCIAS PRESENTADAS\n"
        context += "=" * 40 + "\n"
        for i, ev in enumerate(evidence, 1):
            context += f"""
{i}. {ev.evidence_type.upper()}
   Descripción: {ev.evidence_description}
   Fecha: {ev.received_date}
"""

        return context

    def _build_determination_prompt(
        self,
        case_context: str,
        applicable_articles: List[StatutoryArticle]
    ) -> str:
        """Construye prompt especializado para análisis disciplinario"""

        articles_text = "\n".join([
            f"""
ARTÍCULO {art.article_number}: {art.article_title}
Nivel de Severidad: {['LEVE', 'MODERADO', 'GRAVE'][art.sanction_severity_level - 1]}
Sanciones Aplicables: {', '.join(art.applicable_sanctions)}
Texto: {art.article_text[:500]}
"""
            for art in applicable_articles[:5]  # Máximo 5 artículos para context window
        ])

        prompt = f"""
SISTEMA DE ANÁLISIS DISCIPLINARIO - DETERMINACIÓN FINAL

Tu rol: Eres un experto legal especializado en derecho disciplinario administrativo.
Tu tarea: Analizar el caso disciplinario a continuación y proporcionar una recomendación 
de resolución fundamentada en los artículos estatutarios aplicables.

CONTEXTO DEL CASO:
{case_context}

ARTÍCULOS ESTATUTARIOS APLICABLES:
{articles_text}

INSTRUCCIONES DE ANÁLISIS:
1. Analiza OBJETIVAMENTE los hechos presentados
2. Identifica violaciones específicas de los artículos listados
3. Considera el nivel de severidad (LEVE/MODERADO/GRAVE)
4. Presenta tu recomendación en uno de estos formatos ÚNICAMENTE:
   - AMONESTACION: Sanción administrativa menor, correctiva
   - CONCILIACION: Acuerdo entre partes, remediación voluntaria
   - CONSIGNACION: Elevación a instancia superior o castigo grave

FORMATO DE RESPUESTA (OBLIGATORIO - Sigue EXACTAMENTE este formato JSON):

{{
    "recomendacion_principal": "AMONESTACION|CONCILIACION|CONSIGNACION",
    "confianza": 0.85,
    "resumen_caso": "Párrafo ejecutivo de 2-3 líneas",
    "hallazgos_clave": [
        "Hallazgo 1",
        "Hallazgo 2",
        "Hallazgo 3"
    ],
    "articulos_aplicables": [
        {{"articulo": "5.3.1", "razon": "Por qué aplica este artículo"}}
    ],
    "justificacion_legal": "Párrafo de 4-5 líneas fundamentando la recomendación en los estatutos",
    "alternativa_1": "AMONESTACION|CONCILIACION|CONSIGNACION",
    "confianza_alternativa_1": 0.60,
    "alternativa_2": "AMONESTACION|CONCILIACION|CONSIGNACION",
    "confianza_alternativa_2": 0.40
}}

IMPORTANTE: 
- Responde SOLO con JSON válido, sin markdown ni explicaciones adicionales
- Tu recomendación debe estar FUNDAMENTADA EN LOS ARTÍCULOS PRESENTADOS
- Los scores de confianza deben ser realistas (0.0 a 1.0)
"""
        return prompt

    def _parse_ai_response(
        self,
        ai_response: str,
        case_id: str,
        applicable_articles: List[StatutoryArticle]
    ) -> AIRecommendation:
        """Parsea respuesta JSON de la IA"""

        try:
            # Extraer JSON de la respuesta
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                ai_data = json.loads(json_match.group())
            else:
                raise ValueError("No se encontró JSON en respuesta de IA")

            # Mapear nombres de sanciones a formato consistente
            sanction_map = {
                "AMONESTACION": "amonestacion",
                "CONCILIACION": "conciliacion",
                "CONSIGNACION": "consignacion"
            }

            primary = sanction_map.get(
                ai_data.get('recomendacion_principal', 'AMONESTACION').upper(),
                'amonestacion'
            )

            recommendation = AIRecommendation(
                recommendation_id=str(uuid.uuid4()),
                case_id=case_id,
                primary_recommendation=primary,
                confidence_score=float(ai_data.get('confianza', 0.5)),
                case_summary=ai_data.get('resumen_caso', ''),
                key_findings=ai_data.get('hallazgos_clave', []),
                applicable_articles=applicable_articles,
                legal_justification=ai_data.get('justificacion_legal', ''),
                statute_citations=ai_data.get('articulos_aplicables', []),
                alternative_1=sanction_map.get(
                    ai_data.get('alternativa_1', '').upper(),
                    None
                ),
                alternative_1_confidence=float(
                    ai_data.get('confianza_alternativa_1', 0.0)
                ),
                alternative_2=sanction_map.get(
                    ai_data.get('alternativa_2', '').upper(),
                    None
                ),
                alternative_2_confidence=float(
                    ai_data.get('confianza_alternativa_2', 0.0)
                )
            )

            return recommendation

        except json.JSONDecodeError as e:
            print(f"Error parseando JSON: {e}")
            print(f"Respuesta recibida: {ai_response[:500]}")
            # Fallback a determinación basada en reglas
            return self._rule_based_determination(
                CaseSummary(case_id, '', '', '', '', '', '', 0),
                applicable_articles
            )

    def _rule_based_determination(
        self,
        case_summary: CaseSummary,
        applicable_articles: List[StatutoryArticle]
    ) -> AIRecommendation:
        """
        Fallback: Determinación basada en reglas si la IA no está disponible.
        Analiza severidad de artículos para recomendar resolución.
        """
        # Calcular severidad promedio
        if not applicable_articles:
            primary = "amonestacion"
            confidence = 0.4
        else:
            avg_severity = sum(a.sanction_severity_level 
                              for a in applicable_articles) / len(applicable_articles)

            if avg_severity >= 2.5:
                primary = "consignacion"
                confidence = 0.75
            elif avg_severity >= 1.5:
                primary = "conciliacion"
                confidence = 0.70
            else:
                primary = "amonestacion"
                confidence = 0.65

        return AIRecommendation(
            recommendation_id=str(uuid.uuid4()),
            case_id=case_summary.case_id,
            primary_recommendation=primary,
            confidence_score=confidence,
            case_summary="Recomendación generada por análisis de reglas (IA no disponible)",
            key_findings=["Análisis basado en severidad de artículos aplicables"],
            applicable_articles=applicable_articles,
            legal_justification="Se determinó por nivel de severidad de violaciones",
            statute_citations=[],
            alternative_1="amonestacion" if primary != "amonestacion" else "conciliacion",
            alternative_1_confidence=0.4
        )

    def _save_recommendation_to_db(self, recommendation: AIRecommendation) -> None:
        """Guarda recomendación en base de datos para auditoría"""
        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ai_recommendations (
                recommendation_id, case_id, primary_recommendation,
                confidence_score, case_summary, key_findings,
                applicable_articles, legal_justification,
                statute_citations, alternative_1, alternative_1_confidence,
                alternative_2, alternative_2_confidence,
                generated_at, model_used, model_temperature
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            recommendation.recommendation_id,
            recommendation.case_id,
            recommendation.primary_recommendation,
            recommendation.confidence_score,
            recommendation.case_summary,
            json.dumps(recommendation.key_findings),
            json.dumps([asdict(a) for a in recommendation.applicable_articles]),
            recommendation.legal_justification,
            json.dumps(recommendation.statute_citations),
            recommendation.alternative_1,
            recommendation.alternative_1_confidence,
            recommendation.alternative_2,
            recommendation.alternative_2_confidence,
            datetime.now().isoformat(),
            self.model,
            0.3
        ))

        conn.commit()
        conn.close()

    # ========================================================================
    # 4. VALIDACIÓN Y CONFIRMACIÓN DEL USUARIO
    # ========================================================================

    def user_validates_recommendation(
        self,
        recommendation_id: str,
        final_decision: str,
        validated_by: str
    ) -> bool:
        """
        Registra validación del usuario de la recomendación de IA.
        El usuario puede aceptar o cambiar la recomendación.
        """
        valid_decisions = ['amonestacion', 'conciliacion', 'consignacion']

        if final_decision not in valid_decisions:
            raise ValueError(f"Decisión inválida: {final_decision}")

        conn = self.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE ai_recommendations
            SET user_validated = TRUE,
                user_validation_date = ?,
                final_decision = ?,
                validated_by_user = ?
            WHERE recommendation_id = ?
        """, (
            datetime.now().isoformat(),
            final_decision,
            validated_by,
            recommendation_id
        ))

        conn.commit()
        conn.close()

        return True

    def create_final_resolution(
        self,
        case_id: str,
        final_decision: str,
        resolution_text: str,
        approved_by: str,
        sanction_type: str = None,
        sanction_duration_days: int = None,
        remedial_action: str = None,
        remedial_deadline: str = None
    ) -> str:
        """
        Crea resolución final del caso basada en la decisión validada.
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()

        resolution_id = str(uuid.uuid4())
        resolution_number = self._generate_resolution_number(cursor)

        cursor.execute("""
            INSERT INTO final_resolutions (
                resolution_id, case_id, resolution_type,
                resolution_number, resolution_text,
                sanction_type, sanction_duration_days,
                remedial_action, remedial_deadline,
                resolution_date, approved_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            resolution_id,
            case_id,
            final_decision,
            resolution_number,
            resolution_text,
            sanction_type,
            sanction_duration_days,
            remedial_action,
            remedial_deadline,
            datetime.now().strftime('%Y-%m-%d'),
            approved_by
        ))

        # Actualizar estado del caso
        cursor.execute("""
            UPDATE cases
            SET status = 'concluido',
                resolution_type = ?,
                last_modified_by = ?
            WHERE case_id = ?
        """, (final_decision, approved_by, case_id))

        conn.commit()
        conn.close()

        return resolution_id

    def _generate_resolution_number(self, cursor: sqlite3.Cursor) -> str:
        """Genera número único de resolución"""
        year = datetime.now().year
        cursor.execute("""
            SELECT COUNT(*) FROM final_resolutions
            WHERE resolution_date LIKE ?
        """, (f"{year}%",))

        count = cursor.fetchone()[0] + 1
        return f"RES-{year}-{count:04d}"


# ============================================================================
# SCRIPT DE PRUEBA
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("MÓDULO DE DETERMINACIÓN FINAL - TEST")
    print("="*80 + "\n")

    engine = DeterminationEngine()

    # Ejemplo de uso (requiere caso en DB)
    try:
        # Este flujo se ejecutaría desde la interfaz UI
        case_id = "case_001"  # Reemplazar con ID real

        # 1. Recuperar información del caso
        case_summary = engine.retrieve_case_summary(case_id)
        print(f"✓ Caso recuperado: {case_summary.case_number}")

        # 2. Recuperar comparecencias y evidencias
        hearings = engine.retrieve_hearings(case_id)
        evidence = engine.retrieve_evidence(case_id)
        print(f"✓ Comparecencias: {len(hearings)}")
        print(f"✓ Evidencias: {len(evidence)}")

        # 3. Análisis RAG de artículos aplicables
        applicable_articles = engine.perform_rag_analysis(
            case_id,
            case_summary.case_description,
            hearings,
            evidence
        )
        print(f"✓ Artículos aplicables: {len(applicable_articles)}")

        # 4. Generar recomendación de IA
        recommendation = engine.generate_ai_recommendation(
            case_id,
            case_summary,
            hearings,
            evidence,
            applicable_articles
        )

        print(f"\n{'='*80}")
        print("RECOMENDACIÓN DE IA")
        print(f"{'='*80}")
        print(f"Decisión Principal: {recommendation.primary_recommendation.upper()}")
        print(f"Confianza: {recommendation.confidence_score*100:.1f}%")
        print(f"\nResumen: {recommendation.case_summary}")
        print(f"\nFundamentación Legal:\n{recommendation.legal_justification}")

        # 5. Usuario valida y decide
        engine.user_validates_recommendation(
            recommendation.recommendation_id,
            final_decision="amonestacion",
            validated_by="usuario_admin"
        )
        print("\n✓ Validación del usuario registrada")

    except Exception as e:
        print(f"Error en test: {e}")
        import traceback
        traceback.print_exc()
