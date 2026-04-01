#!/usr/bin/env python3
# ============================================================================
# SERVIDOR FLASK - SISTEMA DISCIPLINARIO LOCAL
# API REST que integra IA, RAG, y Base de Datos
# ============================================================================

import os
import json
import uuid
import sqlite3
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Importar módulos propios
from determination_module import (
    DeterminationEngine, CaseSummary, Hearing, Evidence
)

# Configuración
load_dotenv()

app = Flask(__name__)
CORS(app)  # Permitir requests desde SwiftUI

# Configuración
DB_PATH = os.getenv('DB_PATH', os.path.expanduser('~/.disciplina/db/disciplina.db'))
OLLAMA_ENDPOINT = os.getenv('OLLAMA_ENDPOINT', 'http://localhost:11434')
STATUTE_DIR = os.path.expanduser('~/.disciplina/statutes')
AUDIO_DIR = os.path.expanduser('~/.disciplina/audios')
RESOLUTION_DIR = os.path.expanduser('~/.disciplina/resolutions')

# Crear directorios si no existen
for directory in [STATUTE_DIR, AUDIO_DIR, RESOLUTION_DIR]:
    os.makedirs(directory, exist_ok=True)

# Inicializar motor de determinación
determination_engine = DeterminationEngine(db_path=DB_PATH)

# ============================================================================
# UTILIDADES
# ============================================================================

def get_db_connection():
    """Obtiene conexión a base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def error_response(message: str, code: int = 400):
    """Respuesta de error estándar"""
    return jsonify({
        'status': 'error',
        'message': message,
        'timestamp': datetime.now().isoformat()
    }), code

def success_response(data: dict = None, message: str = "Success"):
    """Respuesta de éxito estándar"""
    return jsonify({
        'status': 'success',
        'message': message,
        'data': data or {},
        'timestamp': datetime.now().isoformat()
    }), 200

# ============================================================================
# RUTAS: GESTIÓN DE CASOS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check del sistema"""
    try:
        conn = get_db_connection()
        conn.execute("SELECT 1")
        conn.close()
        
        return success_response({
            'system': 'healthy',
            'db': 'connected',
            'ollama': f'{OLLAMA_ENDPOINT}/api/tags',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return error_response(f"System error: {str(e)}", 503)

@app.route('/api/cases', methods=['GET'])
def list_cases():
    """Listar todos los casos"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Obtener parámetros de filtro
        status = request.args.get('status')
        resolution_type = request.args.get('resolution_type')
        
        query = "SELECT * FROM vw_case_summary WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if resolution_type:
            query += " AND resolution_type = ?"
            params.append(resolution_type)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        cases = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return success_response({
            'cases': cases,
            'count': len(cases)
        })
    
    except Exception as e:
        return error_response(str(e), 500)

@app.route('/api/cases/<case_id>', methods=['GET'])
def get_case(case_id: str):
    """Obtener caso específico con todos sus detalles"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Caso base
        cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        case = dict(cursor.fetchone() or {})
        
        if not case:
            conn.close()
            return error_response(f"Caso {case_id} no encontrado", 404)
        
        # Comparecencias
        cursor.execute(
            "SELECT * FROM hearings WHERE case_id = ? ORDER BY hearing_date",
            (case_id,)
        )
        case['hearings'] = [dict(row) for row in cursor.fetchall()]
        
        # Evidencias
        cursor.execute(
            "SELECT * FROM evidence WHERE case_id = ? ORDER BY received_date DESC",
            (case_id,)
        )
        case['evidence'] = [dict(row) for row in cursor.fetchall()]
        
        # Resolución (si existe)
        cursor.execute(
            "SELECT * FROM final_resolutions WHERE case_id = ?",
            (case_id,)
        )
        resolution = cursor.fetchone()
        case['resolution'] = dict(resolution) if resolution else None
        
        # Recomendación de IA (si existe)
        cursor.execute("""
            SELECT * FROM ai_recommendations 
            WHERE case_id = ? 
            ORDER BY generated_at DESC LIMIT 1
        """, (case_id,))
        recommendation = cursor.fetchone()
        case['last_recommendation'] = dict(recommendation) if recommendation else None
        
        conn.close()
        
        return success_response({'case': case})
    
    except Exception as e:
        return error_response(str(e), 500)

@app.route('/api/cases', methods=['POST'])
def create_case():
    """Crear nuevo caso disciplinario"""
    try:
        data = request.get_json()
        
        # Validación básica
        required_fields = ['case_title', 'complainant_name', 'respondent_name',
                          'complaint_date', 'case_description']
        if not all(field in data for field in required_fields):
            return error_response("Campos requeridos faltantes", 400)
        
        case_id = str(uuid.uuid4())
        case_number = f"EXP-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO cases (
                case_id, case_number, case_title, complainant_name,
                respondent_name, complaint_date, case_description,
                created_by, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            case_id,
            case_number,
            data['case_title'],
            data['complainant_name'],
            data['respondent_name'],
            data['complaint_date'],
            data['case_description'],
            data.get('created_by', 'system'),
            'abierto'
        ))
        
        conn.commit()
        conn.close()
        
        return success_response({
            'case_id': case_id,
            'case_number': case_number
        }, 'Case created successfully'), 201
    
    except Exception as e:
        return error_response(str(e), 500)

# ============================================================================
# RUTAS: GESTIÓN DE AUDIENCIAS Y TRANSCRIPCIONES
# ============================================================================

@app.route('/api/hearings/<case_id>', methods=['GET'])
def list_hearings(case_id: str):
    """Listar todas las audiencias de un caso"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM hearings WHERE case_id = ? ORDER BY hearing_date",
            (case_id,)
        )
        hearings = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return success_response({'hearings': hearings})
    
    except Exception as e:
        return error_response(str(e), 500)

@app.route('/api/hearings', methods=['POST'])
def create_hearing():
    """Registrar nueva comparecencia/audiencia"""
    try:
        data = request.get_json()
        
        hearing_id = str(uuid.uuid4())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO hearings (
                hearing_id, case_id, hearing_date, hearing_type,
                participant_name, participant_role, recorded_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            hearing_id,
            data['case_id'],
            data['hearing_date'],
            data.get('hearing_type', 'testimonio'),
            data['participant_name'],
            data['participant_role'],
            data.get('recorded_by', 'system')
        ))
        
        conn.commit()
        conn.close()
        
        return success_response({'hearing_id': hearing_id}, 'Hearing created'), 201
    
    except Exception as e:
        return error_response(str(e), 500)

@app.route('/api/hearings/<hearing_id>/transcript', methods=['POST'])
def update_transcript(hearing_id: str):
    """Actualizar transcripción de una audiencia"""
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE hearings
            SET transcript_text = ?, transcript_generated_at = ?,
                transcript_model = ?
            WHERE hearing_id = ?
        """, (
            data['transcript_text'],
            datetime.now().isoformat(),
            data.get('transcript_model', 'whisper_local'),
            hearing_id
        ))
        
        conn.commit()
        conn.close()
        
        return success_response({}, 'Transcript updated')
    
    except Exception as e:
        return error_response(str(e), 500)

# ============================================================================
# RUTAS: MÓDULO DE DETERMINACIÓN FINAL (CORE)
# ============================================================================

@app.route('/api/determination/<case_id>', methods=['GET'])
def generate_determination(case_id: str):
    """
    ENDPOINT PRINCIPAL: Genera análisis de determinación final
    
    Flujo:
    1. Recupera datos del caso
    2. Busca artículos aplicables (RAG)
    3. Genera recomendación con IA
    4. Retorna al usuario para validación
    """
    try:
        print(f"\n{'='*80}")
        print(f"INICIANDO DETERMINACIÓN PARA CASO: {case_id}")
        print(f"{'='*80}\n")
        
        # 1. RECUPERAR INFORMACIÓN DEL CASO
        print("1. Recuperando información del caso...")
        case_summary = determination_engine.retrieve_case_summary(case_id)
        print(f"   ✓ Caso: {case_summary.case_number}")
        
        # 2. RECUPERAR COMPARECENCIAS Y EVIDENCIAS
        print("2. Recuperando comparecencias y evidencias...")
        hearings = determination_engine.retrieve_hearings(case_id)
        evidence = determination_engine.retrieve_evidence(case_id)
        print(f"   ✓ Comparecencias: {len(hearings)}")
        print(f"   ✓ Evidencias: {len(evidence)}")
        
        # 3. ANÁLISIS RAG - BUSCAR ARTÍCULOS APLICABLES
        print("3. Realizando análisis RAG (búsqueda de artículos)...")
        applicable_articles = determination_engine.perform_rag_analysis(
            case_id,
            case_summary.case_description,
            hearings,
            evidence
        )
        print(f"   ✓ Artículos encontrados: {len(applicable_articles)}")
        
        # 4. GENERAR RECOMENDACIÓN CON IA
        print("4. Generando recomendación con IA local...")
        recommendation = determination_engine.generate_ai_recommendation(
            case_id,
            case_summary,
            hearings,
            evidence,
            applicable_articles
        )
        print(f"   ✓ Recomendación: {recommendation.primary_recommendation.upper()}")
        print(f"   ✓ Confianza: {recommendation.confidence_score*100:.1f}%")
        
        # 5. RETORNAR AL CLIENTE
        print("\n5. Enviando respuesta al cliente...")
        
        return success_response({
            'recommendation': {
                'recommendation_id': recommendation.recommendation_id,
                'case_id': recommendation.case_id,
                'primary_recommendation': recommendation.primary_recommendation,
                'confidence_score': recommendation.confidence_score,
                'case_summary': recommendation.case_summary,
                'key_findings': recommendation.key_findings,
                'applicable_articles': [
                    {
                        'article_id': art.article_id,
                        'article_number': art.article_number,
                        'article_title': art.article_title,
                        'article_text': art.article_text,
                        'sanction_severity_level': art.sanction_severity_level,
                        'applicable_sanctions': art.applicable_sanctions
                    }
                    for art in recommendation.applicable_articles
                ],
                'legal_justification': recommendation.legal_justification,
                'statute_citations': recommendation.statute_citations,
                'alternative_1': recommendation.alternative_1,
                'alternative_1_confidence': recommendation.alternative_1_confidence,
                'alternative_2': recommendation.alternative_2,
                'alternative_2_confidence': recommendation.alternative_2_confidence
            }
        })
    
    except Exception as e:
        print(f"\n❌ Error en determinación: {str(e)}")
        import traceback
        traceback.print_exc()
        return error_response(str(e), 500)

@app.route('/api/determination/validate', methods=['POST'])
def validate_determination():
    """
    Valida la recomendación de IA y la aprueba
    El usuario confirma su decisión (puede cambiar la recomendación)
    """
    try:
        data = request.get_json()
        
        recommendation_id = data.get('recommendation_id')
        final_decision = data.get('final_decision')  # amonestacion, conciliacion, consignacion
        validated_by = data.get('validated_by', 'unknown')
        
        # Validar decisión
        valid_decisions = ['amonestacion', 'conciliacion', 'consignacion']
        if final_decision not in valid_decisions:
            return error_response(f"Decisión inválida: {final_decision}", 400)
        
        # Guardar validación en DB
        determination_engine.user_validates_recommendation(
            recommendation_id,
            final_decision,
            validated_by
        )
        
        print(f"✓ Validación registrada: {final_decision.upper()} por {validated_by}")
        
        return success_response({
            'recommendation_id': recommendation_id,
            'final_decision': final_decision,
            'validated_at': datetime.now().isoformat()
        }, 'Determination validated')
    
    except Exception as e:
        return error_response(str(e), 500)

@app.route('/api/resolution', methods=['POST'])
def create_resolution():
    """
    Crea la resolución final del caso
    Se ejecuta después de que el usuario valida la recomendación
    """
    try:
        data = request.get_json()
        
        case_id = data['case_id']
        final_decision = data['final_decision']
        resolution_text = data['resolution_text']
        approved_by = data.get('approved_by', 'system')
        
        # Crear resolución final
        resolution_id = determination_engine.create_final_resolution(
            case_id=case_id,
            final_decision=final_decision,
            resolution_text=resolution_text,
            approved_by=approved_by,
            sanction_type=data.get('sanction_type'),
            sanction_duration_days=data.get('sanction_duration_days'),
            remedial_action=data.get('remedial_action'),
            remedial_deadline=data.get('remedial_deadline')
        )
        
        print(f"✓ Resolución creada: {resolution_id}")
        
        return success_response({
            'resolution_id': resolution_id,
            'case_id': case_id,
            'decision': final_decision,
            'created_at': datetime.now().isoformat()
        }, 'Resolution created'), 201
    
    except Exception as e:
        return error_response(str(e), 500)

# ============================================================================
# RUTAS: DASHBOARD Y REPORTES
# ============================================================================

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    """Obtiene datos para el dashboard"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Estadísticas generales
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM cases
            GROUP BY status
        """)
        
        status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Casos por tipo de resolución
        cursor.execute("""
            SELECT resolution_type, COUNT(*) as count
            FROM cases
            WHERE status = 'concluido'
            GROUP BY resolution_type
        """)
        
        resolution_counts = {row['resolution_type']: row['count'] 
                            for row in cursor.fetchall()}
        
        conn.close()
        
        return success_response({
            'by_status': status_counts,
            'by_resolution': resolution_counts,
            'total_cases': sum(status_counts.values())
        })
    
    except Exception as e:
        return error_response(str(e), 500)

@app.route('/api/audit-log/<case_id>', methods=['GET'])
def get_audit_log(case_id: str):
    """Obtiene log de auditoría para un caso"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM access_log
            WHERE case_id = ?
            ORDER BY access_time DESC
        """, (case_id,))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return success_response({'logs': logs})
    
    except Exception as e:
        return error_response(str(e), 500)

# ============================================================================
# RUTAS: GESTIÓN DE ESTATUTOS
# ============================================================================

@app.route('/api/statutes/upload', methods=['POST'])
def upload_statute():
    """Cargar y indexar PDF de estatutos"""
    try:
        if 'statute' not in request.files:
            return error_response("No statute file provided", 400)
        
        pdf_file = request.files['statute']
        
        if not pdf_file.filename.endswith('.pdf'):
            return error_response("Only PDF files allowed", 400)
        
        # Guardar en disco
        pdf_path = os.path.join(
            STATUTE_DIR,
            f"statute_{datetime.now().timestamp()}.pdf"
        )
        pdf_file.save(pdf_path)
        
        print(f"✓ PDF guardado: {pdf_path}")
        
        # Nota: La indexación se haría aquí con StatuteIndexer
        # Por ahora, solo guardamos el archivo
        
        return success_response({
            'pdf_path': pdf_path,
            'filename': pdf_file.filename
        }, 'Statute uploaded'), 201
    
    except Exception as e:
        return error_response(str(e), 500)

# ============================================================================
# MANEJO DE ERRORES
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return error_response("Endpoint not found", 404)

@app.errorhandler(500)
def internal_error(error):
    return error_response("Internal server error", 500)

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*80)
    print("SISTEMA DE GESTIÓN DISCIPLINARIA - SERVIDOR FLASK")
    print("="*80)
    print(f"Database: {DB_PATH}")
    print(f"Ollama: {OLLAMA_ENDPOINT}")
    print(f"Statute DIR: {STATUTE_DIR}")
    print(f"Audio DIR: {AUDIO_DIR}")
    print(f"Resolution DIR: {RESOLUTION_DIR}")
    print("="*80 + "\n")
    
    # Modo debug para desarrollo
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    app.run(
        host='127.0.0.1',
        port=5000,
        debug=DEBUG,
        use_reloader=DEBUG
    )
