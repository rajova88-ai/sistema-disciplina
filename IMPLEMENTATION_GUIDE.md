==============================================================================
GUÍA DE IMPLEMENTACIÓN - SISTEMA DE GESTIÓN DISCIPLINARIA PRIVADO
==============================================================================

TABLA DE CONTENIDOS
═══════════════════
1. Requisitos del Sistema
2. Arquitectura General
3. Setup Inicial
4. Configuración de Ollama
5. Flujo de Carga de Estatutos
6. Flujo de Determinación Final
7. Integración SwiftUI ↔ Python
8. Seguridad y Cumplimiento


═══════════════════════════════════════════════════════════════════════════
1. REQUISITOS DEL SISTEMA
═════════════════════════

Hardware Mínimo:
├─ Mac: macOS 12.0+ (Intel o Apple Silicon)
├─ RAM: 16 GB (8 GB mínimo, no recomendado)
├─ Almacenamiento: 20 GB disponibles
│  (incluye modelos IA: ~7 GB)
└─ Procesador: Intel i7+ o Apple M1+

Software Requerido:
├─ Python 3.10+
├─ Ollama (IA Local)
├─ SQLite3 (incluido en macOS)
├─ Xcode 14+ (para SwiftUI)
└─ Librerías Python específicas

Instalación de Dependencias:
───────────────────────────

# 1. Ollama (IA Local)
Descargar e instalar: https://ollama.ai/download

# 2. Python y venv
$ python3 -m venv venv_disciplina
$ source venv_disciplina/bin/activate

# 3. Dependencias Python
$ pip install -r requirements.txt

Contenido de requirements.txt:
────────────────────────────
flask==2.3.2               # Backend API
flask-cors==4.0.0          # CORS para Swift
sqlite3
requests==2.31.0           # HTTP client
pdfplumber==0.10.0         # Parsing de PDF
PyPDF2==4.0.1              # Manejo adicional PDF
sentence-transformers==2.2.2 # Embeddings vectoriales
numpy==1.24.3              # Cálculos numéricos
scipy==1.11.0              # Similitud coseno
cryptography==41.0.0       # Encriptación
python-dotenv==1.0.0       # Variables de entorno
watchdog==3.0.0            # File monitoring


═══════════════════════════════════════════════════════════════════════════
2. ARQUITECTURA GENERAL
══════════════════════

┌──────────────────────────────────────────────────────────────────┐
│                      CLIENTE (macOS)                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ SwiftUI Interface                                          │ │
│  │ - Dashboard (Casos Abiertos, Concluidos, etc)            │ │
│  │ - Gestión de Expedientes                                  │ │
│  │ - Módulo de Determinación Final                           │ │
│  │ - Visualización de Resoluciones                           │ │
│  └────────────┬───────────────────────────────────────────────┘ │
│               │ HTTP (localhost:5000)                            │
└───────────────┼─────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────────┐
│                  BACKEND (Flask + Python)                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ API REST                                                   │ │
│  │ /api/cases                 (CRUD casos)                    │ │
│  │ /api/hearings              (Gestión comparecencias)        │ │
│  │ /api/determination/:case   (Análisis IA)                  │ │
│  │ /api/resolution            (Crear resolución)             │ │
│  └────────────┬───────────────────────────────────────────────┘ │
│               │                                                  │
│  ┌────────────┴───────────────────────────────────────────────┐ │
│  │ Módulos de Lógica                                          │ │
│  │ - DeterminationEngine        (Motor IA + RAG)             │ │
│  │ - StatuteIndexer            (Indexación PDF)              │ │
│  │ - RAGRetriever              (Búsqueda semántica)          │ │
│  │ - AudioTranscriber          (Whisper local)               │ │
│  └────────────┬───────────────────────────────────────────────┘ │
│               │                                                  │
└───────────────┼─────────────────────────────────────────────────┘
                │
                ▼
┌──────────────────────────────────────────────────────────────────┐
│                   SISTEMA LOCAL (Mac)                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Ollama Service (Puerto 11434)                              │ │
│  │ - Llama 3 (o Llama 2)                                      │ │
│  │ - Temperatura: 0.3 (bajo para decisiones legales)          │ │
│  │ - Context Window: 4096 tokens                              │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Sentence Transformers (Para embeddings)                    │ │
│  │ - Modelo: all-MiniLM-L6-v2 (384 dims, 22MB)              │ │
│  │ - Local, sin dependencias de red                           │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ SQLite Database                                            │ │
│  │ - Archivo: ~/.disciplina/disciplina.db                     │ │
│  │ - Tamaño: ~50-100 MB (escalable)                           │ │
│  │ - Encriptado con SQLCipher (opcional)                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Sistema de Archivos                                        │ │
│  │ - Audios: ~/.disciplina/audios/                            │ │
│  │ - Estatutos: ~/.disciplina/statutes/                       │ │
│  │ - Resoluciones: ~/.disciplina/resolutions/                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
3. SETUP INICIAL
════════════════

PASO 1: Instalar Ollama
──────────────────────
$ brew install ollama  # O descargar desde ollama.ai

PASO 2: Descargar Modelo de IA
──────────────────────────────
$ ollama pull llama3:latest
# Descarga ~7-8 GB (dependiendo del modelo)
# Llama 3 es más precisao que Llama 2 para tareas legales

PASO 3: Crear directorios del sistema
──────────────────────────────────────
$ mkdir -p ~/.disciplina/{db,audios,statutes,resolutions,exports}
$ chmod 700 ~/.disciplina  # Permisos estrictos

PASO 4: Clonar/Descargar código
────────────────────────────────
$ git clone https://github.com/tu-repo/sistema-disciplina.git
$ cd sistema-disciplina

PASO 5: Instalar dependencias Python
─────────────────────────────────────
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt

PASO 6: Inicializar Base de Datos
──────────────────────────────────
$ python3 scripts/init_db.py

Esto crea:
├─ disciplina.db (SQLite con todas las tablas)
├─ Tablas vacías pero estructuradas
├─ Índices para optimización
└─ Vistas para reportes

PASO 7: Arrancar Backend Flask
───────────────────────────────
$ python3 app.py

Logs esperados:
────────────────
* Running on http://127.0.0.1:5000
* Ollama endpoint: http://localhost:11434
* Database: ~/.disciplina/db/disciplina.db
* Ready for connections from SwiftUI

PASO 8: Compilar y ejecutar SwiftUI
────────────────────────────────────
$ open DisciplinarySystem.xcodeproj
# En Xcode: Product → Run (⌘R)


═══════════════════════════════════════════════════════════════════════════
4. CONFIGURACIÓN DE OLLAMA
══════════════════════════

Verificar que Ollama está corriendo:
────────────────────────────────────
$ curl http://localhost:11434/api/tags
# Respuesta JSON con modelos disponibles

Configuración óptima para decisiones legales:
──────────────────────────────────────────────

Crear archivo: ~/.ollama/Modelfile.disciplina
──────────────────────────────────────────────

FROM llama3:latest

# Comportamiento para análisis disciplinario
PARAMETER temperature 0.3     # Bajo: salidas consistentes y legales
PARAMETER top_p 0.9          # Evitar salidas muy creativas
PARAMETER top_k 40           # Limitar opciones
PARAMETER repeat_penalty 1.1 # Evitar repeticiones

# Contexto amplio para casos complejos
PARAMETER num_ctx 4096

# Instrucción del sistema (custom)
SYSTEM """
Eres un experto legal especializado en derecho disciplinario administrativo.

Tu rol:
- Analizar casos disciplinarios basándote ÚNICAMENTE en artículos estatutarios
- Hacer recomendaciones de resolución OBJETIVAS y FUNDAMENTADAS
- Considerar el principio de proporcionalidad
- Citar específicamente los artículos aplicables

Prohibido:
- Inventar artículos o regulaciones
- Tomar decisiones políticas
- Sesgos personales en el análisis
- Recomendar sanciones no contempladas

Formato de respuesta:
- JSON válido SIEMPRE
- Fundamentación clara y citada
- Alternativas consideradas
- Confianza/certidumbre de la recomendación
"""

Registrar modelo personalizado:
───────────────────────────────
$ ollama create disciplina-analyzer -f ~/.ollama/Modelfile.disciplina

Usar en código:
───────────────
# En determination_module.py
self.model = "disciplina-analyzer"  # En lugar de "llama3:latest"


═══════════════════════════════════════════════════════════════════════════
5. FLUJO DE CARGA DE ESTATUTOS
══════════════════════════════

PASO 1: Administrador carga PDF
──────────────────────────────
En SwiftUI: Settings → Statutes → Upload PDF

PASO 2: Backend procesa PDF
───────────────────────────
```python
# app.py
@app.route('/api/statutes/upload', methods=['POST'])
def upload_statute():
    pdf_file = request.files['statute']
    
    # 1. Validar PDF
    if not pdf_file.filename.endswith('.pdf'):
        return {"error": "Solo archivos PDF"}, 400
    
    # 2. Guardar en disco
    pdf_path = f"{STATUTE_DIR}/statute_{datetime.now().timestamp()}.pdf"
    pdf_file.save(pdf_path)
    
    # 3. Indexar
    indexer = StatuteIndexer(DB_PATH)
    
    try:
        indexer.index_statute_pdf(
            pdf_path,
            statute_version=request.form.get('version', 'default')
        )
        
        return {
            "status": "success",
            "articles_indexed": 142,  # Ejemplo
            "message": "Estatuto indexado correctamente"
        }
    
    except Exception as e:
        return {"error": str(e)}, 500
```

PASO 3: Verificación de indexación
──────────────────────────────────
```sql
SELECT COUNT(*) FROM statute_articles;
-- Resultado: 142 artículos indexados

SELECT article_number, article_title 
FROM statute_articles LIMIT 5;
-- Verifica que se extrajeron correctamente
```

PASO 4: Test de búsqueda RAG
────────────────────────────
```python
retriever = RAGRetriever(DB_PATH)
test_context = "El empleado fue tratado injustamente sin procedimiento"

articles = retriever.retrieve_applicable_articles(test_context, top_k=5)

# Imprime artículos encontrados
for art in articles:
    print(f"Art {art['article_number']}: {art['similarity_score']:.2f}")
```


═══════════════════════════════════════════════════════════════════════════
6. FLUJO DE DETERMINACIÓN FINAL (Resumen de Ejecución)
══════════════════════════════════════════════════════

┌─ USUARIO ABRE MÓDULO DETERMINACIÓN
│  ├─ Selecciona caso
│  └─ Presiona botón "Análisis de Determinación"
│
├─ BACKEND INICIA ANÁLISIS
│  ├─ 1. Recupera datos caso
│  ├─ 2. Recupera comparecencias y transcripciones
│  ├─ 3. Recupera evidencias
│  ├─ 4. Construye contexto consolidado
│  └─ 5. Busca artículos aplicables (RAG)
│
├─ IA ANALIZA CON CONTEXTO
│  ├─ Recibe: Contexto + Artículos relevantes
│  ├─ Temperatura baja (0.3) para consistencia
│  ├─ Genera recomendación JSON
│  └─ Parsea respuesta
│
├─ GUARDAR RECOMENDACIÓN
│  ├─ Guardar en table: ai_recommendations
│  ├─ Log de auditoría
│  └─ Timestamp
│
├─ ENVIAR A UI
│  ├─ Mostrar recomendación principal
│  ├─ Mostrar confianza
│  ├─ Mostrar hallazgos clave
│  ├─ Listar artículos aplicables
│  └─ Permitir cambio de decisión
│
├─ USUARIO VALIDA
│  ├─ Puede aceptar recomendación
│  ├─ O elegir alternativa
│  └─ Presiona "Confirmar Decisión"
│
└─ CREAR RESOLUCIÓN FINAL
   ├─ Guardar en table: final_resolutions
   ├─ Generar número único (RES-YYYY-####)
   ├─ Actualizar estado caso a "concluido"
   ├─ Generar PDF descargable
   └─ Notificar partes


═══════════════════════════════════════════════════════════════════════════
7. INTEGRACIÓN SwiftUI ↔ Python
═════════════════════════════════

Comunicación HTTP REST
──────────────────────

SwiftUI → Flask (GET):
```swift
let url = URL(string: "http://localhost:5000/api/determination/case_001")!
let (data, _) = try await URLSession.shared.data(from: url)
let recommendation = try JSONDecoder().decode(AIRecommendationModel.self, from: data)
```

Flask ← Ollama:
```python
response = requests.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "disciplina-analyzer",
        "prompt": prompt_text,
        "stream": False
    }
)
ai_response = response.json()['response']
```

Flujo de Datos:
───────────────
SwiftUI                Flask Backend           Ollama AI
   │                        │                      │
   ├─ GET /determination ──→ │                      │
   │                        ├─ Query DB ───────────┐
   │                        │                      │
   │                        ├─ RAG Search          │
   │                        │  (embeddings local)  │
   │                        │                      │
   │                        ├─ Build Prompt ───────┐
   │                        │                      │
   │                        ├─ POST /api/generate ─→ │
   │                        │                      ├─ Llama 3
   │                        │                      ├─ Analiza
   │                        │                      ├─ JSON response
   │  ← JSON Response ──────┤                      │
   │  (recomendación)       ├─ Parse JSON ←────────┤
   │                        │ Save to DB
   │                        │


═══════════════════════════════════════════════════════════════════════════
8. SEGURIDAD Y CUMPLIMIENTO NORMATIVO
════════════════════════════════════════

Privacidad Total
────────────────
✓ CERO datos en la nube
✓ Ollama corre en localhost (no en línea)
✓ PDF de estatutos almacenado localmente
✓ SQLite en ~/.disciplina (protegido)

Encriptación
────────────
# Usar SQLCipher para DB encriptada
$ pip install sqlcipher3

Conexión encriptada:
```python
import sqlcipher3

db = sqlcipher3.connect('~/.disciplina/disciplina.db')
db.execute(f"PRAGMA key='{ENCRYPTION_PASSWORD}'")  # Contraseña fuerte
```

Control de Acceso
─────────────────
```sql
-- Tabla de usuarios y permisos
CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT,  -- bcrypt
    role TEXT,  -- 'admin', 'investigator', 'reviewer'
    department TEXT,
    last_login TIMESTAMP
);

CREATE TABLE user_permissions (
    permission_id TEXT PRIMARY KEY,
    user_id TEXT,
    resource TEXT,  -- 'case_view', 'case_create', 'determination', 'resolution_approve'
    granted BOOLEAN,
    granted_at TIMESTAMP
);
```

Auditoría Completa
──────────────────
Tabla: access_log (definida en schema)

```python
def log_access(case_id: str, action: str, user_id: str):
    """Registra cada acceso a un caso"""
    db.execute("""
        INSERT INTO access_log (
            log_id, case_id, accessed_by, action_type,
            access_time, ip_address, changes_made
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        str(uuid.uuid4()),
        case_id,
        user_id,
        action,
        datetime.now().isoformat(),
        request.remote_addr,
        json.dumps(changes)
    ))
```

Cumplimiento Legal
──────────────────
✓ GDPR: Sin transferencia de datos
✓ Derecho al Olvido: Borrado de datos personales (con restricciones legales)
✓ Trazabilidad: Auditoría de cada decisión
✓ Firmas Digitales: Capacidad para firmar electrónicamente resoluciones

Retención de Datos
──────────────────
Política: Mantener por 7 años (configurable)

```python
def archive_old_cases():
    """Archiva casos mayores a 7 años"""
    cutoff_date = (datetime.now() - timedelta(days=2555)).date()
    
    db.execute("""
        UPDATE cases 
        SET archived = TRUE 
        WHERE created_at < ? AND status = 'concluido'
    """, (cutoff_date,))
```

Encriptación de Audios
──────────────────────
```python
from cryptography.fernet import Fernet

key = Fernet.generate_key()  # Guardar seguramente
cipher = Fernet(key)

# Encriptar audio grabado
with open('hearing.wav', 'rb') as f:
    encrypted = cipher.encrypt(f.read())

# Almacenar encriptado
with open('~/.disciplina/audios/hearing.enc', 'wb') as f:
    f.write(encrypted)
```


═══════════════════════════════════════════════════════════════════════════
9. TESTS Y VALIDACIÓN
═════════════════════

Test de RAG:
────────────
```python
# test_rag.py
def test_statute_retrieval():
    """Verifica que RAG recupera artículos correctos"""
    
    retriever = RAGRetriever(DB_PATH)
    
    # Caso de prueba: discriminación
    context = "Empleado fue rechazado sin motivo válido"
    articles = retriever.retrieve_applicable_articles(context)
    
    # Verificar
    assert len(articles) > 0
    assert any('discriminación' in a['article_title'].lower() 
              for a in articles)
    assert all(a['similarity_score'] > 0.6 for a in articles)

def test_ai_recommendation():
    """Verifica que IA genera respuestas válidas"""
    
    engine = DeterminationEngine()
    
    case_summary = CaseSummary(...)
    hearings = [Hearing(...)]
    evidence = [Evidence(...)]
    articles = [StatutoryArticle(...)]
    
    rec = engine.generate_ai_recommendation(
        "case_001", case_summary, hearings, evidence, articles
    )
    
    # Verificar
    assert rec.primary_recommendation in ['amonestacion', 'conciliacion', 'consignacion']
    assert 0.0 <= rec.confidence_score <= 1.0
    assert len(rec.case_summary) > 50
    assert len(rec.legal_justification) > 100

def test_database_integrity():
    """Verifica integridad de la base de datos"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar tablas
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )
    tables = {row[0] for row in cursor.fetchall()}
    
    required_tables = {
        'cases', 'hearings', 'evidence', 'statute_articles',
        'ai_recommendations', 'final_resolutions', 'access_log'
    }
    
    assert required_tables.issubset(tables)
    conn.close()
```

Performance:
────────────
Tiempos esperados:

Carga del caso:                 < 100 ms
Búsqueda RAG (embeddings):      200-500 ms
Análisis IA (Llama 3):          5-15 segundos
Generación de respuesta:        < 200 ms
Guardado en DB:                 < 50 ms

TOTAL ESPERADO:                 5-20 segundos


═══════════════════════════════════════════════════════════════════════════
10. DEPLOYMENT EN PRODUCCIÓN
════════════════════════════

Consideraciones:
────────────────
1. Usar SQLCipher para encriptación en reposo
2. Implementar autenticación (OAuth2 local o LDAP)
3. Monitoreo de logs (acceso, cambios, errores)
4. Backups diarios encriptados
5. VPN local si conecta múltiples Macs
6. Certificados SSL para HTTPS (si es en red local)
7. Política de contraseñas fuerte
8. Auditoría externa anual

Backup automatizado:
────────────────────
```bash
# backup.sh
#!/bin/bash
BACKUP_DIR="/Volumes/ExternalDrive/disciplina_backups"
DB_PATH="$HOME/.disciplina/db/disciplina.db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup encriptado
tar --encrypt -czvf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz.gpg" \
    "$HOME/.disciplina"

# Mantener solo últimos 30 backups
ls -t "$BACKUP_DIR"/backup_*.tar.gz.gpg | tail -n +31 | xargs rm -f
```


═══════════════════════════════════════════════════════════════════════════
CONCLUSIÓN
═════════════════════════════════════════════════════════════════════════════

Este sistema proporciona:

✓ Privacidad Total: 100% local, cero datos en nube
✓ IA Fundamentada: Cada decisión citada en estatutos
✓ Auditoría Completa: Trazabilidad de cada acción
✓ Interfaz Profesional: Apple-style, sobria y clara
✓ Cumplimiento Legal: Apto para decisiones administrativas
✓ Escalabilidad: Soporta cientos de casos
✓ Seguridad: Encriptación, control de acceso, logs

Próximos pasos:
───────────────
1. Setup inicial siguiendo pasos 1-8
2. Cargar PDF de estatutos institucionales
3. Crear usuarios y asignar permisos
4. Realizar tests con casos de prueba
5. Obtener feedback de administradores
6. Ajustar prompts de IA según contexto institucional
7. Capacitar personal en el sistema
8. Deploy en producción

¡Sistema listo para gobernar procesos disciplinarios con legalidad y transparencia!
