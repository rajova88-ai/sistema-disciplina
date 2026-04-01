#!/usr/bin/env python3
# ============================================================================
# SCRIPT DE INICIALIZACIÓN - BASE DE DATOS
# Crea estructura completa de la BD desde schema
# ============================================================================

import os
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

DB_PATH = os.path.expanduser(os.getenv('DB_PATH', '~/.disciplina/db/disciplina.db'))
DATA_DIR = os.path.expanduser(os.getenv('DATA_DIR', '~/.disciplina/data'))
EMBEDDING_DIR = os.path.expanduser(os.getenv('EMBEDDING_DIR', '~/.disciplina/embeddings'))
LOG_DIR = os.path.expanduser(os.getenv('LOG_DIR', '~/.disciplina/logs'))

# SQL Schema (mismo del archivo database_schema.sql)
SCHEMA_SQL = """
-- ============================================================================
-- SISTEMA DE GESTIÓN DISCIPLINARIA - ESQUEMA SQLite
-- Privado, Local, 100% Auditable
-- ============================================================================

-- Tabla Principal: CASOS
CREATE TABLE IF NOT EXISTS cases (
    case_id TEXT PRIMARY KEY,
    case_number TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Información del Denunciante
    complainant_name TEXT NOT NULL,
    complainant_id TEXT,
    complainant_department TEXT,
    
    -- Información del Denunciado
    respondent_name TEXT NOT NULL,
    respondent_id TEXT,
    respondent_department TEXT,
    respondent_position TEXT,
    
    -- Detalles del Caso
    case_title TEXT NOT NULL,
    case_description TEXT,
    complaint_date DATE NOT NULL,
    complaint_channel TEXT,
    
    -- Estado
    status TEXT DEFAULT 'abierto',
    resolution_type TEXT,
    
    -- Auditoría
    created_by TEXT NOT NULL,
    last_modified_by TEXT,
    legal_review_date TIMESTAMP,
    legal_reviewer TEXT
);

-- Tabla: EXPEDIENTES (Archivos del Caso)
CREATE TABLE IF NOT EXISTS expedient_files (
    file_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT,
    file_hash TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

-- Tabla: COMPARECENCIAS (Audiencias/Testimonios)
CREATE TABLE IF NOT EXISTS hearings (
    hearing_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    hearing_date DATE NOT NULL,
    hearing_type TEXT,
    participant_name TEXT NOT NULL,
    participant_role TEXT,
    
    -- Archivo de Audio
    audio_file_path TEXT,
    audio_format TEXT,
    audio_duration_seconds INTEGER,
    audio_uploaded_at TIMESTAMP,
    
    -- Transcripción
    transcript_text TEXT,
    transcript_generated_at TIMESTAMP,
    transcript_model TEXT,
    
    -- Notas del Investigador
    investigator_notes TEXT,
    
    -- Auditoría
    recorded_by TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: EVIDENCIAS (Pruebas Vinculadas)
CREATE TABLE IF NOT EXISTS evidence (
    evidence_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    evidence_type TEXT NOT NULL,
    evidence_description TEXT,
    evidence_file_path TEXT,
    file_hash TEXT,
    
    -- Referencias Legales
    article_references TEXT,
    
    -- Auditoría
    received_date DATE NOT NULL,
    received_from TEXT,
    chain_of_custody_log TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: ANÁLISIS_ESTATUTARIOS (RAG - Relación Artículos vs Caso)
CREATE TABLE IF NOT EXISTS statutory_analysis (
    analysis_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    statute_article_id TEXT NOT NULL,
    article_number TEXT,
    article_title TEXT,
    article_text TEXT,
    article_sanctions TEXT,
    
    -- Análisis de Aplicabilidad
    applicability_score REAL,
    reasoning TEXT,
    evidence_supporting_ids TEXT,
    
    -- Sanción Asociada
    suggested_sanction TEXT,
    sanction_justification TEXT,
    
    -- Auditoría
    analyzed_by TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: RECOMENDACIONES_IA (Determinación Final)
CREATE TABLE IF NOT EXISTS ai_recommendations (
    recommendation_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    
    -- Timestamp de Análisis
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    model_used TEXT,
    model_temperature REAL,
    
    -- Recomendación Principal
    primary_recommendation TEXT,
    confidence_score REAL,
    
    -- Alternativas
    alternative_1 TEXT,
    alternative_1_confidence REAL,
    alternative_2 TEXT,
    alternative_2_confidence REAL,
    
    -- Resumen de Análisis
    case_summary TEXT,
    key_findings TEXT,
    applicable_articles TEXT,
    
    -- Fundamentación Legal
    legal_justification TEXT,
    statute_citations TEXT,
    
    -- Seguimiento
    user_validated BOOLEAN DEFAULT FALSE,
    user_validation_date TIMESTAMP,
    final_decision TEXT,
    final_decision_date TIMESTAMP,
    
    -- Auditoría
    created_by_system TEXT DEFAULT 'ollama_local',
    validated_by_user TEXT
);

-- Tabla: RESOLUCIONES_FINALES (Cierre del Caso)
CREATE TABLE IF NOT EXISTS final_resolutions (
    resolution_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL UNIQUE,
    
    -- Detalles de la Resolución
    resolution_type TEXT NOT NULL,
    resolution_date DATE NOT NULL,
    resolution_number TEXT UNIQUE,
    
    -- Fundamentos
    legal_basis TEXT,
    resolution_text TEXT,
    
    -- Sanciones Específicas
    sanction_type TEXT,
    sanction_duration_days INTEGER,
    
    -- Acción Remediadora
    remedial_action TEXT,
    remedial_deadline DATE,
    
    -- Notificación
    notification_date DATE,
    notification_method TEXT,
    
    -- Auditoría Completa
    approved_by TEXT NOT NULL,
    approval_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    digital_signature BOOLEAN DEFAULT FALSE,
    signature_timestamp TIMESTAMP,
    
    -- Referencias
    ai_recommendation_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (case_id) REFERENCES cases(case_id),
    FOREIGN KEY (ai_recommendation_id) REFERENCES ai_recommendations(recommendation_id)
);

-- Tabla: ESTATUTOS_INDEXADOS (Para RAG - Parsed PDF)
CREATE TABLE IF NOT EXISTS statute_index (
    statute_id TEXT PRIMARY KEY,
    statute_version TEXT,
    statute_upload_date TIMESTAMP,
    
    -- Metadatos del PDF
    pdf_file_path TEXT,
    pdf_hash TEXT,
    pdf_total_pages INTEGER,
    
    -- Información del Documento
    institution_name TEXT,
    statute_title TEXT,
    statute_effective_date DATE,
    
    -- Estructura
    total_articles INTEGER,
    total_chapters INTEGER,
    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: ARTÍCULOS_ESTATUTARIOS (Parsed from PDF)
CREATE TABLE IF NOT EXISTS statute_articles (
    article_id TEXT PRIMARY KEY,
    statute_id TEXT NOT NULL,
    
    -- Identificación del Artículo
    article_number TEXT NOT NULL,
    article_chapter TEXT,
    article_title TEXT,
    
    -- Contenido
    article_full_text TEXT NOT NULL,
    article_summary TEXT,
    article_keywords TEXT,
    
    -- Sanciones Asociadas
    applicable_sanctions TEXT,
    sanction_severity_level INTEGER,
    
    -- Vectorización
    embedding_vector BLOB,
    
    -- Auditoría
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: HISTORIAL_ACCESO (Auditoría Completa)
CREATE TABLE IF NOT EXISTS access_log (
    log_id TEXT PRIMARY KEY,
    case_id TEXT,
    accessed_by TEXT NOT NULL,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action_type TEXT,
    resource_accessed TEXT,
    ip_address TEXT,
    changes_made TEXT,
    
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

-- Tabla: CONFIGURACIÓN_SISTEMA
CREATE TABLE IF NOT EXISTS system_config (
    config_key TEXT PRIMARY KEY,
    config_value TEXT,
    data_type TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT
);

-- ÍNDICES
CREATE INDEX IF NOT EXISTS idx_cases_status ON cases(status);
CREATE INDEX IF NOT EXISTS idx_cases_resolution_type ON cases(resolution_type);
CREATE INDEX IF NOT EXISTS idx_cases_created_at ON cases(created_at);
CREATE INDEX IF NOT EXISTS idx_cases_respondent ON cases(respondent_id);

CREATE INDEX IF NOT EXISTS idx_hearings_case_id ON hearings(case_id);
CREATE INDEX IF NOT EXISTS idx_hearings_hearing_date ON hearings(hearing_date);

CREATE INDEX IF NOT EXISTS idx_evidence_case_id ON evidence(case_id);
CREATE INDEX IF NOT EXISTS idx_evidence_type ON evidence(evidence_type);

CREATE INDEX IF NOT EXISTS idx_statutory_case_id ON statutory_analysis(case_id);
CREATE INDEX IF NOT EXISTS idx_statutory_article ON statutory_analysis(statute_article_id);

CREATE INDEX IF NOT EXISTS idx_recommendations_case_id ON ai_recommendations(case_id);
CREATE INDEX IF NOT EXISTS idx_recommendations_generated_at ON ai_recommendations(generated_at);

CREATE INDEX IF NOT EXISTS idx_resolutions_case_id ON final_resolutions(case_id);
CREATE INDEX IF NOT EXISTS idx_resolutions_type ON final_resolutions(resolution_type);

CREATE INDEX IF NOT EXISTS idx_statute_articles_statute ON statute_articles(statute_id);
CREATE INDEX IF NOT EXISTS idx_statute_articles_number ON statute_articles(article_number);

CREATE INDEX IF NOT EXISTS idx_access_log_case ON access_log(case_id);
CREATE INDEX IF NOT EXISTS idx_access_log_user ON access_log(accessed_by);
CREATE INDEX IF NOT EXISTS idx_access_log_time ON access_log(access_time);

-- VISTAS
CREATE VIEW IF NOT EXISTS vw_case_summary AS
SELECT 
    c.case_id,
    c.case_number,
    c.case_title,
    c.complainant_name,
    c.respondent_name,
    c.status,
    c.resolution_type,
    c.complaint_date,
    COUNT(DISTINCT h.hearing_id) as total_hearings,
    COUNT(DISTINCT e.evidence_id) as total_evidence,
    fr.resolution_number,
    fr.resolution_date,
    fr.sanction_type
FROM cases c
LEFT JOIN hearings h ON c.case_id = h.case_id
LEFT JOIN evidence e ON c.case_id = e.case_id
LEFT JOIN final_resolutions fr ON c.case_id = fr.case_id
GROUP BY c.case_id;

-- CONFIGURACIÓN POR DEFECTO
INSERT OR IGNORE INTO system_config (config_key, config_value, data_type) VALUES
('app_version', '1.0.0', 'string'),
('ollama_endpoint', 'http://localhost:11434', 'string'),
('ollama_model', 'llama3:latest', 'string'),
('rag_similarity_threshold', '0.6', 'string'),
('institution_name', 'Tu Institución', 'string');
"""


def create_directories():
    """Crea estructura de directorios necesaria"""
    print("\n📁 Creando estructura de directorios...")
    
    directories = [
        os.path.dirname(DB_PATH),
        os.path.join(DATA_DIR, 'statutes'),
        os.path.join(DATA_DIR, 'audios'),
        os.path.join(DATA_DIR, 'resolutions'),
        EMBEDDING_DIR,
        LOG_DIR,
        os.path.join(DATA_DIR, 'exports')
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {directory}")
    
    # Permisos restrictivos
    os.chmod(os.path.dirname(DB_PATH), 0o700)
    print(f"   ✓ Permisos restrictivos aplicados")


def create_database():
    """Crea y estructura la base de datos"""
    print("\n🗄️  Creando base de datos...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Ejecutar schema
        cursor.executescript(SCHEMA_SQL)
        
        conn.commit()
        conn.close()
        
        print(f"   ✓ Base de datos creada: {DB_PATH}")
        return True
    
    except Exception as e:
        print(f"   ❌ Error creando BD: {e}")
        return False


def verify_database():
    """Verifica que la BD se creó correctamente"""
    print("\n✅ Verificando base de datos...")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Verificar tablas
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' 
            ORDER BY name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = [
            'cases', 'hearings', 'evidence', 'statute_articles',
            'ai_recommendations', 'final_resolutions', 'access_log',
            'statutory_analysis', 'statute_index'
        ]
        
        print(f"\n   Tablas creadas: {len(tables)}")
        for table in tables:
            status = "✓" if table in required_tables else "ℹ"
            print(f"   {status} {table}")
        
        # Verificar vistas
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='view'
        """)
        
        views = [row[0] for row in cursor.fetchall()]
        print(f"\n   Vistas: {len(views)}")
        for view in views:
            print(f"   ✓ {view}")
        
        # Verificar índices
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND name NOT LIKE 'sqlite_%'
        """)
        
        indexes = [row[0] for row in cursor.fetchall()]
        print(f"\n   Índices: {len(indexes)}")
        
        # Verificar config
        cursor.execute("SELECT COUNT(*) FROM system_config")
        config_count = cursor.fetchone()[0]
        print(f"\n   Configuración: {config_count} valores iniciales")
        
        conn.close()
        
        all_good = all(table in tables for table in required_tables)
        
        if all_good:
            print("\n   ✅ Base de datos verificada correctamente")
            return True
        else:
            print("\n   ⚠️  Algunas tablas requeridas no se crearon")
            return False
    
    except Exception as e:
        print(f"   ❌ Error verificando BD: {e}")
        return False


def main():
    """Script principal"""
    print("\n" + "="*80)
    print("INICIALIZADOR - SISTEMA DE GESTIÓN DISCIPLINARIA")
    print("="*80)
    
    # Crear directorios
    try:
        create_directories()
    except Exception as e:
        print(f"❌ Error creando directorios: {e}")
        sys.exit(1)
    
    # Crear BD
    if not create_database():
        sys.exit(1)
    
    # Verificar
    if not verify_database():
        sys.exit(1)
    
    print("\n" + "="*80)
    print("✅ SISTEMA INICIALIZADO CORRECTAMENTE")
    print("="*80)
    print(f"\nPróximos pasos:")
    print(f"1. Copiar .env.example a .env y ajustar configuración")
    print(f"2. Ejecutar: python3 scripts/index_statute.py <pdf_path>")
    print(f"3. Ejecutar: python3 app.py")
    print(f"4. Abrir SwiftUI en Xcode\n")


if __name__ == '__main__':
    main()
