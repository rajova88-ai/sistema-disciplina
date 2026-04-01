# ESTRUCTURA COMPLETA DEL BACKEND PYTHON

```
backend/
├── config.py                          # Configuración centralizada
├── app.py                             # Aplicación Flask principal
├── wsgi.py                            # WSGI entry point
│
├── models/
│   ├── __init__.py
│   ├── base.py                        # Modelo base SQLAlchemy
│   ├── case.py                        # Modelo Case
│   ├── hearing.py                     # Modelo Hearing
│   ├── evidence.py                    # Modelo Evidence
│   ├── recommendation.py              # Modelo AI Recommendation
│   ├── resolution.py                  # Modelo Resolution
│   ├── statute.py                     # Modelo Statute
│   └── audit_log.py                   # Modelo Audit Log
│
├── services/
│   ├── __init__.py
│   ├── base_service.py               # Base service class
│   ├── case_service.py               # Lógica de casos
│   ├── hearing_service.py            # Lógica de comparecencias
│   ├── evidence_service.py           # Lógica de evidencias
│   ├── determination_service.py      # ⭐ Lógica de determinación
│   ├── resolution_service.py         # Lógica de resoluciones
│   ├── statute_service.py            # Lógica de estatutos
│   ├── audio_service.py              # Procesamiento de audio
│   └── rag_service.py                # ⭐ Servicio RAG
│
├── api/
│   ├── __init__.py
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── routes.py                 # Rutas principales
│   │   ├── cases.py                  # Endpoints de casos
│   │   ├── hearings.py               # Endpoints de comparecencias
│   │   ├── evidence.py               # Endpoints de evidencias
│   │   ├── determination.py          # ⭐ Endpoints de determinación
│   │   ├── resolutions.py            # Endpoints de resoluciones
│   │   ├── statutes.py               # Endpoints de estatutos
│   │   ├── audit.py                  # Endpoints de auditoría
│   │   └── health.py                 # Health check endpoints
│   │
│   └── errors.py                     # Error handlers
│
├── database/
│   ├── __init__.py
│   ├── db.py                         # Database initialization
│   ├── session.py                    # Session management
│   ├── migrations/
│   │   ├── versions/
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── alembic.ini
│   └── seed_data.py                  # Datos iniciales
│
├── rag/
│   ├── __init__.py
│   ├── indexer.py                    # Indexación de estatutos
│   ├── retriever.py                  # Búsqueda de artículos
│   ├── embeddings.py                 # Manejo de embeddings
│   └── utils.py                      # Utilidades RAG
│
├── ai/
│   ├── __init__.py
│   ├── ollama_client.py              # Cliente de Ollama
│   ├── prompt_builder.py             # Constructor de prompts
│   ├── response_parser.py            # Parser de respuestas
│   └── determination_engine.py       # ⭐ Motor de determinación
│
├── utils/
│   ├── __init__.py
│   ├── logger.py                     # Logging configurado
│   ├── validators.py                 # Validaciones
│   ├── serializers.py                # JSON serializers
│   ├── pdf_utils.py                  # Utilidades PDF
│   ├── audio_utils.py                # Utilidades audio
│   ├── security.py                   # Seguridad/encryption
│   └── helpers.py                    # Funciones auxiliares
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # Pytest configuration
│   ├── test_api/
│   │   ├── test_cases.py
│   │   ├── test_determination.py
│   │   └── test_resolutions.py
│   ├── test_services/
│   │   ├── test_determination_service.py
│   │   ├── test_rag_service.py
│   │   └── test_audio_service.py
│   └── test_rag/
│       ├── test_indexer.py
│       └── test_retriever.py
│
├── data/
│   ├── statutes/                     # PDFs de estatutos
│   ├── audios/                       # Archivos de audio
│   ├── resolutions/                  # PDFs de resoluciones
│   └── exports/                      # Exports generados
│
├── embeddings/
│   ├── statute_embeddings_*.npy      # Archivos de embeddings
│   └── metadata_*.json               # Metadata de embeddings
│
├── logs/
│   └── app.log                       # Logs de aplicación
│
├── static/
│   ├── templates/
│   │   ├── resolution_template.html  # Template de resolución
│   │   └── email_template.html       # Template de email
│   └── css/
│       └── base.css
│
├── requirements.txt                  # Dependencias Python
├── .env.example                      # Variables de entorno
├── .gitignore
├── README.md
└── docker-compose.yml                # (Opcional) Docker setup
```

## ARCHIVOS CLAVE DEL BACKEND

### 1. config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-cambiar-en-produccion')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # Database
    DB_PATH = os.path.expanduser(os.getenv('DB_PATH', '~/.disciplina/db/disciplina.db'))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Ollama
    OLLAMA_ENDPOINT = os.getenv('OLLAMA_ENDPOINT', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3:latest')
    OLLAMA_TEMPERATURE = float(os.getenv('OLLAMA_TEMPERATURE', '0.3'))
    
    # Embeddings
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
    EMBEDDING_DIMENSION = 384
    
    # RAG
    RAG_SIMILARITY_THRESHOLD = float(os.getenv('RAG_SIMILARITY_THRESHOLD', '0.6'))
    RAG_TOP_K = int(os.getenv('RAG_TOP_K', '5'))
    
    # Directorios
    DATA_DIR = os.path.expanduser(os.getenv('DATA_DIR', '~/.disciplina/data'))
    STATUTE_DIR = os.path.join(DATA_DIR, 'statutes')
    AUDIO_DIR = os.path.join(DATA_DIR, 'audios')
    EMBEDDING_DIR = os.path.expanduser(os.getenv('EMBEDDING_DIR', '~/.disciplina/embeddings'))
    
    # Servidor
    FLASK_HOST = os.getenv('FLASK_HOST', '127.0.0.1')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5000').split(',')


class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configuración para testing"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()
```

### 2. app.py (Flask Main)

```python
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

from config import get_config
from database.db import db, init_db
from api.v1 import routes
from api.errors import register_error_handlers
from utils.logger import setup_logger

load_dotenv()

def create_app():
    """Application factory"""
    
    config = get_config()
    app = Flask(__name__)
    app.config.from_object(config)
    
    # Setup logging
    setup_logger(app)
    
    # Initialize database
    db.init_app(app)
    
    # Setup CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints
    routes.register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        init_db()
    
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db}
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(
        host=app.config['FLASK_HOST'],
        port=app.config['FLASK_PORT'],
        debug=app.config['DEBUG']
    )
```

### 3. services/determination_service.py (Core)

```python
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional

from models.recommendation import AIRecommendation
from models.case import Case
from rag.retriever import RAGRetriever
from ai.determination_engine import DeterminationEngine
from database.db import db
from utils.logger import logger


class DeterminationService:
    """Servicio de determinación final"""
    
    def __init__(self):
        self.rag_retriever = RAGRetriever()
        self.determination_engine = DeterminationEngine()
    
    def generate_recommendation(self, case_id: str) -> Dict:
        """
        Genera recomendación de IA para un caso:
        1. Recupera datos del caso
        2. Busca artículos aplicables (RAG)
        3. Llama a IA local
        4. Guarda recomendación
        """
        
        logger.info(f"Generando recomendación para caso: {case_id}")
        
        try:
            # 1. Recuperar caso
            case = db.session.query(Case).filter_by(case_id=case_id).first()
            if not case:
                raise ValueError(f"Caso {case_id} no encontrado")
            
            # 2. Construir contexto
            context = self._build_case_context(case)
            
            # 3. Buscar artículos aplicables (RAG)
            applicable_articles = self.rag_retriever.retrieve_articles(
                context,
                threshold=0.6,
                top_k=5
            )
            
            logger.info(f"Artículos encontrados: {len(applicable_articles)}")
            
            # 4. Generar recomendación con IA
            recommendation = self.determination_engine.generate_recommendation(
                case_id=case_id,
                context=context,
                articles=applicable_articles
            )
            
            # 5. Guardar en DB
            ai_rec = AIRecommendation(
                recommendation_id=str(uuid.uuid4()),
                case_id=case_id,
                primary_recommendation=recommendation['primary'],
                confidence_score=recommendation['confidence'],
                case_summary=recommendation['summary'],
                key_findings=json.dumps(recommendation.get('findings', [])),
                legal_justification=recommendation['justification'],
                statute_citations=json.dumps(recommendation.get('citations', []))
            )
            
            db.session.add(ai_rec)
            db.session.commit()
            
            logger.info(f"Recomendación guardada: {ai_rec.recommendation_id}")
            
            return {
                'recommendation_id': ai_rec.recommendation_id,
                'primary_recommendation': ai_rec.primary_recommendation,
                'confidence_score': ai_rec.confidence_score,
                'case_summary': ai_rec.case_summary,
                'legal_justification': ai_rec.legal_justification
            }
        
        except Exception as e:
            logger.error(f"Error generando recomendación: {e}")
            raise
    
    def _build_case_context(self, case: Case) -> str:
        """Construye contexto consolidado del caso"""
        context_parts = [
            f"Caso: {case.case_number}",
            f"Título: {case.case_title}",
            f"Descripción: {case.case_description}",
            f"Denunciado: {case.respondent_name}"
        ]
        
        # Agregar comparecencias
        for hearing in case.hearings:
            if hearing.transcript_text:
                context_parts.append(
                    f"Testimonio de {hearing.participant_name}: "
                    f"{hearing.transcript_text[:500]}"
                )
        
        # Agregar evidencias
        for evidence in case.evidence:
            context_parts.append(
                f"Evidencia: {evidence.evidence_description[:200]}"
            )
        
        return "\n\n".join(context_parts)
```

### 4. rag/retriever.py (Core RAG)

```python
import sqlite3
import numpy as np
from typing import List, Dict

from config import get_config
from utils.logger import logger


class RAGRetriever:
    """Recuperador de artículos estatutarios (RAG)"""
    
    def __init__(self):
        self.config = get_config()
        self.db_path = self.config.DB_PATH
    
    def retrieve_articles(
        self,
        query: str,
        threshold: float = 0.6,
        top_k: int = 5
    ) -> List[Dict]:
        """
        Recupera artículos relevantes basado en similitud semántica.
        
        Flujo:
        1. Genera embedding de la query
        2. Busca contra embeddings almacenados
        3. Calcula similitud coseno
        4. Filtra por threshold
        5. Retorna top-k
        """
        
        from rag.embeddings import EmbeddingGenerator
        
        logger.info(f"Buscando artículos relevantes (threshold={threshold}, k={top_k})")
        
        try:
            # 1. Generar embedding de query
            generator = EmbeddingGenerator()
            query_embedding = generator.encode(query)
            
            # 2. Recuperar artículos de DB
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT article_id, article_number, article_title,
                       article_full_text, applicable_sanctions,
                       sanction_severity_level, embedding_vector
                FROM statute_articles
                ORDER BY article_number
            """)
            
            articles = cursor.fetchall()
            scored_articles = []
            
            # 3. Calcular similitud
            for article in articles:
                article_embedding = np.frombuffer(
                    article['embedding_vector'],
                    dtype=np.float32
                )
                
                similarity = self._cosine_similarity(
                    query_embedding,
                    article_embedding
                )
                
                if similarity >= threshold:
                    scored_articles.append({
                        'article_id': article['article_id'],
                        'article_number': article['article_number'],
                        'article_title': article['article_title'],
                        'article_text': article['article_full_text'],
                        'sanctions': json.loads(article['applicable_sanctions']),
                        'severity': article['sanction_severity_level'],
                        'similarity': similarity
                    })
            
            # 4. Ordenar y retornar top-k
            scored_articles.sort(key=lambda x: x['similarity'], reverse=True)
            result = scored_articles[:top_k]
            
            logger.info(f"Encontrados {len(result)} artículos relevantes")
            
            conn.close()
            return result
        
        except Exception as e:
            logger.error(f"Error en búsqueda RAG: {e}")
            raise
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calcula similitud coseno"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
```

### 5. api/v1/determination.py (API Endpoints)

```python
from flask import Blueprint, request, jsonify
from services.determination_service import DeterminationService
from utils.logger import logger

determination_bp = Blueprint('determination', __name__, url_prefix='/api/v1/determination')

determination_service = DeterminationService()


@determination_bp.route('/<case_id>', methods=['GET'])
def get_determination(case_id):
    """Genera análisis de determinación final"""
    try:
        result = determination_service.generate_recommendation(case_id)
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@determination_bp.route('/validate', methods=['POST'])
def validate_determination():
    """Valida recomendación"""
    data = request.get_json()
    
    try:
        result = determination_service.validate_recommendation(
            recommendation_id=data['recommendation_id'],
            final_decision=data['final_decision'],
            validated_by=data.get('validated_by', 'unknown')
        )
        
        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
```
