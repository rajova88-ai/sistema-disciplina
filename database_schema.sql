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
    complaint_channel TEXT, -- 'correo', 'presencial', 'formulario_web'
    
    -- Estado
    status TEXT DEFAULT 'abierto', -- 'abierto', 'investigacion', 'concluido'
    resolution_type TEXT, -- 'amonestacion', 'conciliacion', 'consignacion'
    
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
    file_type TEXT NOT NULL, -- 'denuncia', 'evidencia', 'transcripcion', 'documento_estatutos'
    file_name TEXT NOT NULL,
    file_path TEXT, -- Ruta local en el Mac
    file_hash TEXT, -- SHA256 para validar integridad
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

-- Tabla: COMPARECENCIAS (Audiencias/Testimonios)
CREATE TABLE IF NOT EXISTS hearings (
    hearing_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    hearing_date DATE NOT NULL,
    hearing_type TEXT, -- 'descargo_denunciado', 'testigo', 'pericia'
    participant_name TEXT NOT NULL,
    participant_role TEXT, -- 'denunciante', 'denunciado', 'testigo', 'perito'
    
    -- Archivo de Audio
    audio_file_path TEXT,
    audio_format TEXT, -- 'wav', 'mp3', 'm4a'
    audio_duration_seconds INTEGER,
    audio_uploaded_at TIMESTAMP,
    
    -- Transcripción
    transcript_text TEXT,
    transcript_generated_at TIMESTAMP,
    transcript_model TEXT, -- 'whisper_local', 'manual'
    
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
    evidence_type TEXT NOT NULL, -- 'documento', 'audio', 'video', 'fotografia', 'correo'
    evidence_description TEXT,
    evidence_file_path TEXT,
    file_hash TEXT, -- Para cadena de custodia
    
    -- Referencias Legales
    article_references TEXT, -- JSON array de artículos estatutarios relevantes
    
    -- Auditoría
    received_date DATE NOT NULL,
    received_from TEXT,
    chain_of_custody_log TEXT, -- JSON log de quién accedió y cuándo
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: ANÁLISIS_ESTATUTARIOS (RAG - Relación Artículos vs Caso)
CREATE TABLE IF NOT EXISTS statutory_analysis (
    analysis_id TEXT PRIMARY KEY,
    case_id TEXT NOT NULL,
    statute_article_id TEXT NOT NULL, -- Referencia al artículo en el PDF
    article_number TEXT, -- "Art. 5.3.1"
    article_title TEXT,
    article_text TEXT, -- Extracto del artículo
    article_sanctions TEXT, -- Sanciones asociadas al artículo
    
    -- Análisis de Aplicabilidad
    applicability_score REAL, -- 0.0 a 1.0 (confianza de aplicación)
    reasoning TEXT, -- Por qué este artículo se aplica
    evidence_supporting_ids TEXT, -- JSON array de evidence_ids que soportan
    
    -- Sanción Asociada
    suggested_sanction TEXT, -- 'amonestacion', 'conciliacion', 'consignacion'
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
    model_used TEXT, -- 'ollama_llama3', 'ollama_llama2'
    model_temperature REAL,
    
    -- Recomendación Principal
    primary_recommendation TEXT, -- 'amonestacion', 'conciliacion', 'consignacion'
    confidence_score REAL, -- 0.0 a 1.0
    
    -- Alternativas (si aplica)
    alternative_1 TEXT,
    alternative_1_confidence REAL,
    alternative_2 TEXT,
    alternative_2_confidence REAL,
    
    -- Resumen de Análisis
    case_summary TEXT, -- Resumen ejecutivo del caso
    key_findings TEXT, -- JSON array con hallazgos clave
    applicable_articles TEXT, -- JSON array de artículos aplicables
    
    -- Fundamentación Legal
    legal_justification TEXT, -- Párrafo de justificación vinculado a estatutos
    statute_citations TEXT, -- JSON array de citas: {"article": "5.3.1", "cited_text": "..."}
    
    -- Seguimiento
    user_validated BOOLEAN DEFAULT FALSE,
    user_validation_date TIMESTAMP,
    final_decision TEXT, -- Qué decidió el usuario
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
    resolution_type TEXT NOT NULL, -- 'amonestacion', 'conciliacion', 'consignacion'
    resolution_date DATE NOT NULL,
    resolution_number TEXT UNIQUE, -- "RES-2024-001"
    
    -- Fundamentos
    legal_basis TEXT, -- Artículos de los estatutos citados
    resolution_text TEXT, -- Texto completo de la resolución
    
    -- Sanciones Específicas
    sanction_type TEXT, -- 'verbal', 'escrita', 'suspension_temporal', 'despido'
    sanction_duration_days INTEGER, -- Si es suspensión
    
    -- Acción Remediadora (si aplica)
    remedial_action TEXT, -- Qué debe hacer el denunciado para remediar
    remedial_deadline DATE,
    
    -- Notificación
    notification_date DATE,
    notification_method TEXT, -- 'correo_registrado', 'presencial', 'correo_electronico'
    
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
    statute_version TEXT, -- Versión del documento (ej: "v2024.01")
    statute_upload_date TIMESTAMP,
    
    -- Metadatos del PDF
    pdf_file_path TEXT,
    pdf_hash TEXT, -- Versión criptográfica del PDF
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
    article_number TEXT NOT NULL, -- "5.3.1"
    article_chapter TEXT, -- "Capítulo 5: Faltas Disciplinarias"
    article_title TEXT,
    
    -- Contenido
    article_full_text TEXT NOT NULL,
    article_summary TEXT, -- Resumen extractivo
    article_keywords TEXT, -- JSON array de palabras clave
    
    -- Sanciones Asociadas
    applicable_sanctions TEXT, -- JSON array de sanciones: amonestacion, conciliacion, consignacion
    sanction_severity_level INTEGER, -- 1 (leve), 2 (moderado), 3 (grave)
    
    -- Vectorización (para RAG semántico)
    embedding_vector BLOB, -- Vector de embeddings (para búsqueda semántica)
    
    -- Auditoría
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla: HISTORIAL_ACCESO (Auditoría Completa)
CREATE TABLE IF NOT EXISTS access_log (
    log_id TEXT PRIMARY KEY,
    case_id TEXT,
    accessed_by TEXT NOT NULL,
    access_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    action_type TEXT, -- 'view', 'edit', 'download', 'delete', 'export'
    resource_accessed TEXT, -- 'case', 'hearing', 'evidence', 'resolution'
    ip_address TEXT,
    changes_made TEXT, -- JSON de cambios (si aplica)
    
    FOREIGN KEY (case_id) REFERENCES cases(case_id)
);

-- Tabla: CONFIGURACIÓN_SISTEMA
CREATE TABLE IF NOT EXISTS system_config (
    config_key TEXT PRIMARY KEY,
    config_value TEXT,
    data_type TEXT, -- 'string', 'integer', 'boolean', 'json'
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT
);

-- ============================================================================
-- ÍNDICES PARA OPTIMIZACIÓN Y BÚSQUEDA
-- ============================================================================

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

-- ============================================================================
-- VISTAS (Para facilitar reportes)
-- ============================================================================

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

CREATE VIEW IF NOT EXISTS vw_case_dashboard AS
SELECT 
    'abierto' as estado,
    COUNT(*) as cantidad
FROM cases
WHERE status = 'abierto'
UNION ALL
SELECT 
    'investigacion' as estado,
    COUNT(*) as cantidad
FROM cases
WHERE status = 'investigacion'
UNION ALL
SELECT 
    'concluido' as estado,
    COUNT(*) as cantidad
FROM cases
WHERE status = 'concluido'
UNION ALL
SELECT 
    'amonestacion' as estado,
    COUNT(*) as cantidad
FROM cases
WHERE resolution_type = 'amonestacion' AND status = 'concluido'
UNION ALL
SELECT 
    'conciliacion' as estado,
    COUNT(*) as cantidad
FROM cases
WHERE resolution_type = 'conciliacion' AND status = 'concluido'
UNION ALL
SELECT 
    'consignacion' as estado,
    COUNT(*) as cantidad
FROM cases
WHERE resolution_type = 'consignacion' AND status = 'concluido';

-- ============================================================================
-- INSERTAR CONFIGURACIÓN POR DEFECTO
-- ============================================================================

INSERT OR IGNORE INTO system_config (config_key, config_value, data_type) VALUES
('app_version', '1.0.0', 'string'),
('ollama_endpoint', 'http://localhost:11434', 'string'),
('ollama_model', 'llama3:latest', 'string'),
('whisper_model', 'base', 'string'),
('max_audio_duration_minutes', '120', 'integer'),
('rag_similarity_threshold', '0.6', 'string'),
('enable_digital_signatures', 'true', 'boolean'),
('data_retention_years', '7', 'integer'),
('institution_name', 'Tu Institución', 'string'),
('last_statute_update', '', 'string');
