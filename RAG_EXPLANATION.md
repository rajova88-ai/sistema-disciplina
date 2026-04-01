==============================================================================
SISTEMA RAG (Retrieval-Augmented Generation) - ANÁLISIS DISCIPLINARIO
Arquitectura de Indexación y Búsqueda Estatutaria
==============================================================================

1. INTRODUCCIÓN: ¿POR QUÉ RAG?
==============================

El problema fundamental en sistemas de IA para decisiones legales:
- Las LLMs (Large Language Models) tienen "alucinaciones": generan información
  plausible pero falsa si no están fundamentadas en documentos reales.
- Para un sistema disciplinario, cada recomendación DEBE citar artículos 
  específicos del estatuto institucional.
- RAG (Retrieval-Augmented Generation) asegura que la IA solo utilice
  información del PDF de estatutos.

FLUJO RAG EN ESTE SISTEMA:
┌─────────────────────────────────────────────────────────────────┐
│ 1. INDEXACIÓN (Una sola vez, cuando se carga el PDF)            │
│    PDF Estatutos → Parsing → Extracción Artículos → Vector DB   │
├─────────────────────────────────────────────────────────────────┤
│ 2. RECUPERACIÓN (Al analizar cada caso)                         │
│    Contexto del Caso → Búsqueda Semántica → Artículos Relevantes│
├─────────────────────────────────────────────────────────────────┤
│ 3. GENERACIÓN (IA con contexto acotado)                         │
│    IA + Artículos Recuperados → Recomendación Fundamentada      │
└─────────────────────────────────────────────────────────────────┘


2. FASE 1: INDEXACIÓN DEL PDF DE ESTATUTOS
===========================================

Cuando el administrador carga el PDF de estatutos:

┌─────────────────┐
│ PDF Estatutos   │ (documento de 50-200 páginas)
└────────┬────────┘
         │
         ▼
   ┌──────────────────────────────┐
   │ PARSER PDF (pdfplumber)      │
   │ - Extrae texto por página    │
   │ - Identifica estructura      │
   └──────────┬───────────────────┘
              │
              ▼
   ┌──────────────────────────────┐
   │ SEGMENTACIÓN EN ARTÍCULOS    │
   │ - Busca patrones: "Art. 5.3" │
   │ - Extrae texto del artículo  │
   │ - Identifica sanciones       │
   └──────────┬───────────────────┘
              │
              ▼
   ┌──────────────────────────────┐
   │ EXTRACCIÓN DE INFORMACIÓN    │
   │ - Número de artículo         │
   │ - Título (si existe)         │
   │ - Texto completo             │
   │ - Sanciones aplicables       │
   │ - Nivel de severidad         │
   └──────────┬───────────────────┘
              │
              ▼
   ┌──────────────────────────────┐
   │ VECTORIZACIÓN (EMBEDDINGS)   │
   │ - Usar modelo: all-MiniLM    │
   │ - Crear vector de 384 dims   │
   │ - Guardar en DB              │
   └──────────┬───────────────────┘
              │
              ▼
   ┌──────────────────────────────┐
   │ INDEXACIÓN EN DB             │
   │ statute_articles table:      │
   │ - article_id (UUID)          │
   │ - article_number ("5.3.1")   │
   │ - article_full_text          │
   │ - embedding_vector (BLOB)    │
   │ - applicable_sanctions (JSON)│
   │ - sanction_severity_level    │
   └──────────────────────────────┘


CÓDIGO PYTHON PARA INDEXAR ESTATUTOS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```python
import pdfplumber
import sqlite3
import json
import re
from sentence_transformers import SentenceTransformer
import numpy as np

class StatuteIndexer:
    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Local
        
    def index_statute_pdf(self, pdf_path: str, statute_version: str):
        """Indexa un PDF de estatutos en la base de datos"""
        
        # 1. EXTRAE TEXTO DEL PDF
        articles = self._extract_articles_from_pdf(pdf_path)
        print(f"✓ {len(articles)} artículos extraídos")
        
        # 2. PROCESA CADA ARTÍCULO
        statute_id = f"statute_{statute_version}"
        
        for article in articles:
            # Generar embedding del texto del artículo
            embedding = self.model.encode(
                article['full_text'],
                convert_to_numpy=True
            )
            
            # Guardar en DB
            self.db.execute("""
                INSERT INTO statute_articles (
                    article_id, statute_id, article_number,
                    article_chapter, article_title, article_full_text,
                    applicable_sanctions, sanction_severity_level,
                    embedding_vector, extracted_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                article['id'],
                statute_id,
                article['number'],
                article['chapter'],
                article['title'],
                article['full_text'],
                json.dumps(article['sanctions']),
                article['severity'],
                embedding.tobytes(),  # Guardar como BLOB
                datetime.now().isoformat()
            ))
        
        self.db.commit()
        print(f"✓ Estatuto indexado: {statute_id}")
    
    def _extract_articles_from_pdf(self, pdf_path: str) -> list:
        """Extrae artículos individuales del PDF"""
        articles = []
        
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n"
        
        # PATRÓN: Busca "Art. X.Y.Z" o "Artículo X"
        article_pattern = r'(?:Art\.|Artículo)\s+(\d+(?:\.\d+)*)\s*(?:[-–]|:)?\s*([^\n]+)?'
        
        matches = list(re.finditer(article_pattern, full_text, re.IGNORECASE))
        
        for i, match in enumerate(matches):
            article_num = match.group(1)
            article_title = match.group(2) or ""
            
            # Extraer texto del artículo (hasta el siguiente artículo)
            start = match.end()
            end = matches[i+1].start() if i+1 < len(matches) else len(full_text)
            article_text = full_text[start:end].strip()
            
            # PROCESAR: Extraer información del artículo
            sanctions = self._extract_sanctions(article_text)
            severity = self._determine_severity(article_text, sanctions)
            chapter = self._extract_chapter(full_text, match.start())
            
            articles.append({
                'id': f"article_{article_num.replace('.', '_')}",
                'number': article_num,
                'title': article_title,
                'full_text': article_text[:2000],  # Limitar a 2000 chars
                'chapter': chapter,
                'sanctions': sanctions,
                'severity': severity
            })
        
        return articles
    
    def _extract_sanctions(self, article_text: str) -> list:
        """Extrae sanciones mencionadas en el artículo"""
        sanctions = []
        
        sanction_keywords = {
            'amonestacion': ['amonestación', 'amonestación escrita', 'apercibimiento'],
            'conciliacion': ['conciliación', 'solución amistosa', 'acuerdo'],
            'consignacion': ['consignación', 'elevación', 'autoridad superior', 'despido']
        }
        
        text_lower = article_text.lower()
        for sanction_type, keywords in sanction_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if sanction_type not in sanctions:
                        sanctions.append(sanction_type)
        
        return sanctions if sanctions else ['amonestacion']  # Default
    
    def _determine_severity(self, article_text: str, sanctions: list) -> int:
        """Determina nivel de severidad (1=leve, 2=moderado, 3=grave)"""
        
        # Regla 1: Basado en sanciones
        if 'consignacion' in sanctions:
            return 3
        elif 'conciliacion' in sanctions:
            return 2
        else:
            return 1
        
        # Regla 2: Palabras clave en el texto
        severity_indicators = {
            3: ['grave', 'despido', 'inmediato', 'irreversible'],
            2: ['moderado', 'suspensión', 'temporal'],
            1: ['leve', 'menor', 'correctiva']
        }
        
        text_lower = article_text.lower()
        for level, keywords in severity_indicators.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return level
        
        return 1  # Default
    
    def _extract_chapter(self, full_text: str, position: int) -> str:
        """Extrae el capítulo/sección del artículo"""
        # Buscar el capítulo ANTERIOR a este artículo
        chapter_pattern = r'(?:CAPÍTULO|SECCIÓN|TÍTULO)\s+([^\n]+)'
        
        chapters = list(re.finditer(chapter_pattern, full_text[:position], re.IGNORECASE))
        
        if chapters:
            return chapters[-1].group(1).strip()
        return "General"
```


3. FASE 2: RECUPERACIÓN DE ARTÍCULOS RELEVANTES (RAG Retrieval)
===============================================================

Cuando llega un caso nuevo, el sistema busca artículos relevantes:

┌─────────────────────────────┐
│ Contexto del Caso:          │
│ - Descripción denuncia      │
│ - Transcripciones           │
│ - Evidencias                │
└────────┬────────────────────┘
         │
         ▼
   ┌─────────────────────────────┐
   │ GENERACIÓN DE QUERY VECTOR  │
   │ Embedding de contexto del   │
   │ caso (mismo modelo que       │
   │ indexación)                 │
   └────────┬────────────────────┘
            │
            ▼
   ┌─────────────────────────────┐
   │ BÚSQUEDA SEMÁNTICA          │
   │ Calcula similitud coseno:   │
   │ query_vec · article_vec     │
   │ Ranking por similitud       │
   └────────┬────────────────────┘
            │
            ▼
   ┌─────────────────────────────┐
   │ FILTRADO POR THRESHOLD      │
   │ Solo artículos con          │
   │ similitud > 0.6             │
   │ (configurable)              │
   └────────┬────────────────────┘
            │
            ▼
   ┌─────────────────────────────┐
   │ RANKING Y CONTEXTUALIZACION │
   │ Top 5-10 artículos más      │
   │ relevantes                  │
   └─────────────────────────────┘


CÓDIGO PYTHON PARA BÚSQUEDA RAG:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

```python
import sqlite3
import numpy as np
from sentence_transformers import SentenceTransformer

class RAGRetriever:
    def __init__(self, db_path: str):
        self.db = sqlite3.connect(db_path)
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.similarity_threshold = 0.6
    
    def retrieve_applicable_articles(self, case_context: str, top_k: int = 5):
        """
        Recupera artículos relevantes basado en contexto del caso.
        
        Args:
            case_context: Texto consolidado del caso
            top_k: Cantidad de artículos a retornar
        """
        
        # 1. Generar embedding del contexto del caso
        context_vector = self.model.encode(
            case_context,
            convert_to_numpy=True
        )
        
        # 2. Recuperar todos los artículos de la DB
        cursor = self.db.execute("""
            SELECT article_id, article_number, article_title,
                   article_full_text, embedding_vector,
                   applicable_sanctions, sanction_severity_level
            FROM statute_articles
            WHERE statute_id = (
                SELECT statute_id FROM statute_index 
                ORDER BY statute_upload_date DESC LIMIT 1
            )
        """)
        
        articles = cursor.fetchall()
        scored_articles = []
        
        # 3. Calcular similitud con cada artículo
        for article in articles:
            article_vector = np.frombuffer(
                article['embedding_vector'],
                dtype=np.float32
            )
            
            # Similitud coseno: dot(a,b) / (||a|| * ||b||)
            similarity = self._cosine_similarity(context_vector, article_vector)
            
            if similarity >= self.similarity_threshold:
                scored_articles.append({
                    'article_id': article['article_id'],
                    'article_number': article['article_number'],
                    'article_title': article['article_title'],
                    'article_text': article['article_full_text'],
                    'sanctions': json.loads(article['applicable_sanctions']),
                    'severity': article['sanction_severity_level'],
                    'similarity_score': similarity
                })
        
        # 4. Ordenar por similitud y retornar top_k
        scored_articles.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return scored_articles[:top_k]
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcula similitud coseno entre dos vectores"""
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0.0
        
        return float(dot_product / (norm_vec1 * norm_vec2))
```


4. FASE 3: GENERACIÓN CON IA (RAG Generation)
==============================================

La IA recibe SOLO los artículos recuperados:

┌────────────────────────────────┐
│ PROMPT PARA LA IA:             │
│                                │
│ "Analiza este caso:            │
│ [CONTEXTO DEL CASO]            │
│                                │
│ USANDO SOLO ESTOS ARTÍCULOS:   │
│ [Art 5.3.1: ...texto...]       │
│ [Art 5.3.2: ...texto...]       │
│ [Art 5.4.1: ...texto...]       │
│                                │
│ ¿Cuál es tu recomendación?"    │
└────────────────────────────────┘

VENTAJA: La IA NO PUEDE INVENTAR artículos. Solo usa los recuperados.


5. GARANTÍA DE TRAZABILIDAD
===========================

Cada recomendación se guarda con AUDITORÍA COMPLETA:

statutory_analysis table:
├─ analysis_id: UUID único
├─ case_id: Caso que genera la análisis
├─ statute_article_id: Artículo analizado
├─ applicability_score: Similitud calculada (0.0-1.0)
├─ reasoning: Por qué aplica este artículo
├─ evidence_supporting_ids: Evidencias que lo soportan
└─ analyzed_at: Timestamp del análisis

Esto permite:
✓ Auditoría: Saber qué artículos se consideraron
✓ Reproducibilidad: Recalcular análisis con nuevos datos
✓ Apelación: Revisar decisión a nivel de artículos
✓ Cumplimiento Legal: Prueba de fundamentación


6. MEJORAS AVANZADAS (Roadmap)
==============================

Versión 1.0 (Actual):
- Búsqueda simple por similitud coseno
- Vector embeddings en DB como BLOB
- Top-K recuperación estática

Versión 1.1 (Próxima):
- Vector DB especializado (Weaviate/Qdrant local)
- Reranking de artículos con modelo CrossEncoder
- Query expansion automática

Versión 2.0 (Futuro):
- Análisis de conexiones entre artículos
- Knowledge Graph de estatutos
- Predicción de patrones de decisiones


7. FLUJO COMPLETO DE EJEMPLO
============================

CASO: "Discriminación en contratación"

┌─ FASE 1: Indexación
│  PDF cargado: "Estatutos_2024.pdf"
│  Artículos indexados: 142
│  Embeddings almacenados: 142 vectores
│
├─ FASE 2: Nuevo caso llega
│  Contexto: "Empleado X denuncia trato discriminatorio..."
│  Query generado: embedding de 384 dimensiones
│
├─ FASE 3: RAG Retrieval
│  Búsqueda contra 142 artículos
│  Scores encontrados:
│    Art 5.2.1 "No discriminación": 0.78 ✓
│    Art 5.2.2 "Trato equitativo": 0.71 ✓
│    Art 5.3.1 "Sanciones faltas leves": 0.65 ✓
│    Art 3.1.1 "Contratación": 0.62 ✓
│    Art 2.1.0 "Introducción": 0.41 ✗ (< threshold)
│
│  Retorna: Top 4 artículos con similitud > 0.6
│
├─ FASE 4: IA con contexto acotado
│  Prompt: "Caso de discriminación + artículos 5.2.1, 5.2.2, 5.3.1, 3.1.1"
│  IA responde: "CONCILIACION (confianza 85%)"
│    Razonamiento: 
│    - Art 5.2.1 prohibe discriminación → VIOLACIÓN
│    - Art 5.2.2 requiere trato equitativo → INCUMPLIDO
│    - Art 5.3.1 sugiere amonestación para faltas leves
│    - PERO: Daño a empleado requiere remediación
│    - RECOMENDACIÓN: Conciliación + capacitación
│
└─ FASE 5: Usuario valida
   Administrador revisa recomendación
   Confirma "CONCILIACION"
   Sistema crea Resolución #RES-2024-015
   Guarda en DB con auditoría completa


8. VALIDACIÓN DE CALIDAD RAG
============================

Para asegurar que RAG funciona correctamente:

```python
def validate_rag_quality(case_id: str, retrieved_articles: list) -> dict:
    """
    Valida que los artículos recuperados sean relevantes.
    Retorna métricas de calidad.
    """
    
    metrics = {
        'retrieval_success': False,
        'average_similarity': 0.0,
        'articles_above_threshold': 0,
        'coverage': 0.0
    }
    
    if not retrieved_articles:
        return metrics
    
    # Artículos recuperados
    metrics['articles_above_threshold'] = len(retrieved_articles)
    
    # Similitud promedio
    avg_similarity = sum(a['similarity_score'] 
                        for a in retrieved_articles) / len(retrieved_articles)
    metrics['average_similarity'] = avg_similarity
    
    # Coverage: % de artículos considerados
    total_articles = get_total_statute_articles()
    metrics['coverage'] = len(retrieved_articles) / total_articles
    
    # Validación de relevancia (manual)
    # Un revisor verifica si los artículos tienen sentido
    metrics['retrieval_success'] = (
        metrics['articles_above_threshold'] >= 2 and
        metrics['average_similarity'] >= 0.65
    )
    
    return metrics
```


9. CONCLUSIÓN
=============

RAG asegura:
✓ IA fundamentada en estatutos reales
✓ Sin alucinaciones legales
✓ Auditoría y trazabilidad completa
✓ Replicabilidad de decisiones
✓ Cumplimiento normativo

El sistema es 100% privado y local:
- PDF almacenado en Mac
- Modelos de IA (Ollama) en localhost
- DB SQLite local
- Cero datos en la nube
