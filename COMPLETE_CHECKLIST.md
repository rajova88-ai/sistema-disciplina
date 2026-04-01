╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║    SISTEMA DE GESTIÓN DISCIPLINARIA - CHECKLIST COMPLETO 100%            ║
║                                                                            ║
║    Reconstrucción Organizada del Proyecto Completo                        ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝


═══════════════════════════════════════════════════════════════════════════════
FASE 1: BACKEND PYTHON (Semana 1)
═════════════════════════════════════════════════════════════════════════════

🔵 PASO 1: Estructura de Directorios
────────────────────────────────────
□ mkdir -p sistema-disciplina/backend
□ cd backend
□ mkdir -p config models services api database rag ai utils tests
□ mkdir -p data/{statutes,audios,resolutions} embeddings logs

Comando:
```bash
mkdir -p backend/{models,services,api/v1,database,rag,ai,utils,tests,data,embeddings}
```

🔵 PASO 2: Archivos de Configuración
────────────────────────────────────
□ Copiar requirements.txt
□ Crear .env desde .env.example
□ config.py - Configuración centralizada
□ app.py - Flask app factory

✓ Instalación:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

🔵 PASO 3: Base de Datos
────────────────────────
□ database/db.py - Inicialización
□ database/session.py - Session management
□ Ejecutar init_db.py

✓ Inicialización:
```bash
python3 scripts/init_db.py
```

🔵 PASO 4: Modelos SQLAlchemy
──────────────────────────────
□ models/__init__.py
□ models/base.py - Modelo base
□ models/case.py - Case model
□ models/hearing.py - Hearing model
□ models/evidence.py - Evidence model
□ models/recommendation.py - AIRecommendation model
□ models/resolution.py - Resolution model
□ models/statute.py - Statute model
□ models/audit_log.py - Audit log model

🔵 PASO 5: Servicios RAG (Core)
───────────────────────────────
□ rag/embeddings.py - EmbeddingGenerator
□ rag/indexer.py - StatuteIndexer
□ rag/retriever.py - RAGRetriever
□ rag/utils.py - Utilidades

✓ Indexación:
```bash
python3 scripts/index_statute.py ~/Descargas/Estatutos.pdf
```

🔵 PASO 6: Motor de Determinación IA
────────────────────────────────────
□ ai/ollama_client.py - Cliente Ollama
□ ai/prompt_builder.py - Constructor prompts
□ ai/response_parser.py - Parser JSON
□ ai/determination_engine.py - Motor core

✓ Verificar Ollama:
```bash
ollama pull llama3:latest
ollama serve  # En terminal separada
```

🔵 PASO 7: Servicios de Aplicación
──────────────────────────────────
□ services/base_service.py - Base service
□ services/case_service.py
□ services/hearing_service.py
□ services/evidence_service.py
□ services/determination_service.py ⭐
□ services/resolution_service.py
□ services/audio_service.py

🔵 PASO 8: API REST (Endpoints)
──────────────────────────────
□ api/v1/__init__.py
□ api/v1/routes.py - Registro de blueprints
□ api/v1/cases.py - CRUD casos
□ api/v1/hearings.py - CRUD comparecencias
□ api/v1/evidence.py - CRUD evidencias
□ api/v1/determination.py ⭐ - Análisis final
□ api/v1/resolutions.py - CRUD resoluciones
□ api/v1/statutes.py - Gestión estatutos
□ api/v1/health.py - Health check
□ api/errors.py - Error handlers

🔵 PASO 9: Utilidades
─────────────────────
□ utils/logger.py - Logging configurado
□ utils/validators.py - Validaciones
□ utils/serializers.py - JSON serializers
□ utils/pdf_utils.py - Utilidades PDF
□ utils/audio_utils.py - Utilidades audio
□ utils/security.py - Encriptación
□ utils/helpers.py - Funciones auxiliares

🔵 PASO 10: Tests
────────────────
□ tests/conftest.py
□ tests/test_api/test_determination.py
□ tests/test_services/test_determination_service.py
□ tests/test_rag/test_retriever.py

✓ Ejecutar tests:
```bash
pytest -v
```

🔵 PASO 11: Verificación Backend
─────────────────────────────────
□ python3 app.py
□ curl http://localhost:5000/api/v1/health
□ Debe retornar: {"status": "healthy"}


═══════════════════════════════════════════════════════════════════════════════
FASE 2: FRONTEND SWIFTUI (Semana 2)
═════════════════════════════════════════════════════════════════════════════

🟢 PASO 1: Crear Proyecto Xcode
───────────────────────────────
□ Abrir Xcode
□ File → New → Project
□ iOS → App
□ Name: DisciplinarySystem
□ Organization: Tu Institución
□ Team ID: (si tienes)
□ Interface: SwiftUI
□ Language: Swift
□ Life Cycle: SwiftUI App

🟢 PASO 2: Estructura de Carpetas
──────────────────────────────────
□ Crear carpetas en Xcode:
  □ App/
  □ Views/
    □ Dashboard/
    □ Cases/
    □ Hearings/
    □ Evidence/
    □ Determination/
    □ Resolution/
    □ Settings/
    □ Components/
  □ Models/
  □ ViewModels/
  □ Services/
  □ Utilities/
  □ Styles/
  □ Assets/
  □ Preview Content/

🟢 PASO 3: Modelos Estructurales
─────────────────────────────────
□ Models/Case.swift
□ Models/Hearing.swift
□ Models/Evidence.swift
□ Models/AIRecommendation.swift
□ Models/Resolution.swift
□ Models/StatutoryArticle.swift
□ Models/APIResponse.swift

🟢 PASO 4: ViewModels Core
──────────────────────────
□ ViewModels/AppState.swift - Global state
□ ViewModels/DashboardViewModel.swift
□ ViewModels/CaseViewModel.swift
□ ViewModels/HearingViewModel.swift
□ ViewModels/DeterminationViewModel.swift ⭐
□ ViewModels/ResolutionViewModel.swift
□ ViewModels/SettingsViewModel.swift

🟢 PASO 5: Servicios Swift
──────────────────────────
□ Services/APIService.swift - HTTP client base
□ Services/CaseService.swift
□ Services/HearingService.swift
□ Services/DeterminationService.swift ⭐
□ Services/ResolutionService.swift
□ Services/AudioService.swift
□ Services/StorageService.swift

🟢 PASO 6: Vistas Dashboard
───────────────────────────
□ Views/Dashboard/DashboardView.swift
□ Views/Dashboard/CaseStatisticsView.swift
□ Views/Dashboard/CaseListView.swift

🟢 PASO 7: Vistas de Casos
──────────────────────────
□ Views/Cases/CaseDetailView.swift
□ Views/Cases/NewCaseView.swift
□ Views/Cases/CaseEditView.swift
□ Views/Cases/CaseTabView.swift

🟢 PASO 8: Vistas de Comparecencias
───────────────────────────────────
□ Views/Hearings/HearingsView.swift
□ Views/Hearings/NewHearingView.swift
□ Views/Hearings/AudioRecorderView.swift
□ Views/Hearings/TranscriptView.swift

🟢 PASO 9: Vistas de Evidencias
───────────────────────────────
□ Views/Evidence/EvidenceView.swift
□ Views/Evidence/EvidenceDetailView.swift
□ Views/Evidence/NewEvidenceView.swift

🟢 PASO 10: Vistas de Determinación ⭐⭐⭐
────────────────────────────────────────
□ Views/Determination/DeterminationView.swift
□ Views/Determination/RecommendationCardView.swift
□ Views/Determination/ArticlesView.swift
□ Views/Determination/ConfidenceGaugeView.swift
□ Views/Determination/ValidationView.swift
□ Views/Determination/LoadingStateView.swift

🟢 PASO 11: Vistas de Resoluciones
──────────────────────────────────
□ Views/Resolution/ResolutionView.swift
□ Views/Resolution/ResolutionGeneratorView.swift
□ Views/Resolution/ExportResolutionView.swift

🟢 PASO 12: Vistas de Configuración
───────────────────────────────────
□ Views/Settings/SettingsView.swift
□ Views/Settings/StatuteUploadView.swift
□ Views/Settings/UserSettingsView.swift

🟢 PASO 13: Componentes Reutilizables
─────────────────────────────────────
□ Views/Components/LoadingView.swift
□ Views/Components/ErrorView.swift
□ Views/Components/EmptyStateView.swift
□ Views/Components/StatusBadgeView.swift
□ Views/Components/ArticleCardView.swift

🟢 PASO 14: Estilos y Temas
──────────────────────────
□ Styles/AppTheme.swift
□ Styles/Typography.swift
□ Styles/Spacing.swift
□ Utilities/Color+Extensions.swift

🟢 PASO 15: Assets
──────────────────
□ Crear color sets:
  □ PrimaryColor
  □ SecondaryColor
  □ StatusColors (Open, InProgress, etc)
□ Crear image assets:
  □ AppIcon
  □ Icons para cada módulo
□ Localizable.strings (EN/ES)

🟢 PASO 16: Archivo Principal
──────────────────────────────
□ App/DisciplinarySystemApp.swift
□ App/ContentView.swift (Root)

🟢 PASO 17: Tests SwiftUI
─────────────────────────
□ DisciplinarySystemTests/
□ DisciplinarySystemUITests/

🟢 PASO 18: Info.plist
──────────────────────
□ Configurar valores correctos
□ Minimum OS Version: 14.0
□ NSLocalNetworkUsageDescription


═══════════════════════════════════════════════════════════════════════════════
FASE 3: INTEGRACIÓN (Semana 3)
═══════════════════════════════════════════════════════════════════════════════

⚡ PASO 1: Verificación Backend
──────────────────────────────
□ python3 app.py
□ Debe escuchar en 127.0.0.1:5000
□ Verificar con: curl http://localhost:5000/api/v1/health

⚡ PASO 2: Verificación Frontend
───────────────────────────────
□ Compilar en Xcode (⌘B)
□ Ejecutar simulador (⌘R)
□ Verificar que hace requests a localhost:5000

⚡ PASO 3: Flujo Completo
────────────────────────
□ Backend recibe GET /api/v1/determination/:case_id
□ Backend busca artículos (RAG)
□ Backend llama Ollama
□ Frontend recibe respuesta
□ Usuario valida decisión
□ Sistema crea resolución

⚡ PASO 4: Testing End-to-End
──────────────────────────────
□ Crear caso de prueba
□ Agregar comparecencia con audio
□ Agregar evidencias
□ Ejecutar determinación
□ Verificar recomendación
□ Validar decisión
□ Generar resolución


═══════════════════════════════════════════════════════════════════════════════
ESTRUCTURA FINAL DE ARCHIVOS
═════════════════════════════════════════════════════════════════════════════

sistema-disciplina/
│
├── backend/
│   ├── config.py
│   ├── app.py
│   ├── requirements.txt
│   ├── .env.example
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── case.py
│   │   ├── hearing.py
│   │   ├── evidence.py
│   │   ├── recommendation.py
│   │   ├── resolution.py
│   │   ├── statute.py
│   │   └── audit_log.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── base_service.py
│   │   ├── case_service.py
│   │   ├── determination_service.py
│   │   ├── audio_service.py
│   │   └── resolution_service.py
│   │
│   ├── api/
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── determination.py
│   │   │   ├── cases.py
│   │   │   └── health.py
│   │   └── errors.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── indexer.py
│   │   ├── retriever.py
│   │   ├── embeddings.py
│   │   └── utils.py
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── ollama_client.py
│   │   ├── prompt_builder.py
│   │   ├── response_parser.py
│   │   └── determination_engine.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   ├── validators.py
│   │   └── security.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── db.py
│   │   └── session.py
│   │
│   ├── data/
│   │   ├── statutes/
│   │   ├── audios/
│   │   └── resolutions/
│   │
│   ├── embeddings/
│   │
│   ├── scripts/
│   │   ├── init_db.py
│   │   └── index_statute.py
│   │
│   └── tests/
│       ├── conftest.py
│       └── test_api/
│
├── frontend/
│   └── DisciplinarySystem/
│       ├── DisciplinarySystem.xcodeproj/
│       │
│       ├── DisciplinarySystem/
│       │   ├── App/
│       │   │   ├── DisciplinarySystemApp.swift
│       │   │   └── ContentView.swift
│       │   │
│       │   ├── Views/
│       │   │   ├── Dashboard/
│       │   │   ├── Cases/
│       │   │   ├── Determination/
│       │   │   ├── Resolution/
│       │   │   ├── Settings/
│       │   │   └── Components/
│       │   │
│       │   ├── Models/
│       │   │   ├── Case.swift
│       │   │   ├── AIRecommendation.swift
│       │   │   └── Resolution.swift
│       │   │
│       │   ├── ViewModels/
│       │   │   ├── AppState.swift
│       │   │   ├── DeterminationViewModel.swift
│       │   │   └── DashboardViewModel.swift
│       │   │
│       │   ├── Services/
│       │   │   ├── APIService.swift
│       │   │   ├── DeterminationService.swift
│       │   │   └── AudioService.swift
│       │   │
│       │   ├── Styles/
│       │   │   ├── AppTheme.swift
│       │   │   └── Typography.swift
│       │   │
│       │   ├── Assets/
│       │   │   ├── Colors.xcassets/
│       │   │   ├── Images.xcassets/
│       │   │   └── Localizable.strings
│       │   │
│       │   └── Info.plist
│       │
│       ├── DisciplinarySystemTests/
│       └── DisciplinarySystemUITests/
│
├── docs/
│   ├── README.md
│   ├── ARCHITECTURE.md
│   ├── RAG_EXPLANATION.md
│   ├── IMPLEMENTATION_GUIDE.md
│   └── API_DOCUMENTATION.md
│
└── .gitignore


═══════════════════════════════════════════════════════════════════════════════
CHECKLIST POR PRIORIDAD
═══════════════════════════════════════════════════════════════════════════════

🔴 CRÍTICO (Debe funcionar)
──────────────────────────
□ Backend app.py
□ Database schema + init_db.py
□ RAG retriever (búsqueda de artículos)
□ AI determination engine (Ollama)
□ API endpoint /api/v1/determination/<case_id>
□ SwiftUI DeterminationView
□ Services de conexión Swift-Python

🟡 IMPORTANTE (Funcionalidad core)
─────────────────────────────────
□ CRUD de casos
□ Gestión de comparecencias
□ Gestión de evidencias
□ Generación de resoluciones
□ Dashboard con estadísticas
□ Settings para cargar estatutos

🟢 NICE-TO-HAVE (Pulido)
───────────────────────
□ Tests automatizados
□ Exportación a PDF
□ Notificaciones
□ Búsqueda avanzada
□ Analytics


═══════════════════════════════════════════════════════════════════════════════
TIMELINE ESTIMADO
═════════════════════════════════════════════════════════════════════════════

Semana 1 (Backend):
└─ Día 1-2: Setup, config, BD
└─ Día 3-4: Modelos, RAG
└─ Día 5: Determination engine
└─ Día 6-7: API endpoints, tests

Semana 2 (Frontend):
└─ Día 1-2: Proyecto Xcode, estructura
└─ Día 3-4: Vistas principales
└─ Día 5-6: DeterminationView
└─ Día 7: Estilos, polish

Semana 3 (Integración):
└─ Día 1-2: Integración API
└─ Día 3-4: Testing e2e
└─ Día 5-6: Bug fixes
└─ Día 7: Deploy, documentación


═══════════════════════════════════════════════════════════════════════════════
COMANDOS RÁPIDOS
════════════════════════════════════════════════════════════════════════════════

# Inicializar todo
mkdir -p backend/{models,services,api/v1,rag,ai,utils,database,scripts}
mkdir -p backend/{data,embeddings,logs}
mkdir -p ~/.disciplina/{db,data,embeddings}

# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python3 scripts/init_db.py
python3 scripts/index_statute.py ~/path/to/statute.pdf
python3 app.py

# Frontend
cd ../frontend
open DisciplinarySystem.xcodeproj
# ⌘R en Xcode

# Testing
cd backend
pytest -v
pytest tests/test_api/test_determination.py -v

# Ollama
ollama pull llama3:latest
ollama serve


═══════════════════════════════════════════════════════════════════════════════
VALIDACIÓN FINAL
════════════════════════════════════════════════════════════════════════════════

✅ Checklist Final:

Backend:
□ $ python3 app.py → Running on http://127.0.0.1:5000
□ $ curl http://localhost:5000/api/v1/health → {"status": "healthy"}
□ Base de datos creada con todas las tablas
□ Ollama corriendo: $ ollama serve
□ Estatutos indexados en DB
□ Embeddings generados en ~/.disciplina/embeddings

Frontend:
□ Proyecto compilable sin errores
□ Simulador inicia sin crashes
□ API requests conectan a 127.0.0.1:5000
□ Vistas principales cargan datos

Integración:
□ Crear caso → Aparece en dashboard
□ Agregar comparecencia → Se graba audio
□ Ejecutar determinación → Recibe recomendación
□ Validar → Se crea resolución
□ Exportar → PDF descargable


═══════════════════════════════════════════════════════════════════════════════
¡ÉXITO! Sistema 100% Funcional Completo
═════════════════════════════════════════════════════════════════════════════════

Una vez completado este checklist, tendrás:
✓ Backend Python totalmente funcional
✓ Frontend SwiftUI profesional
✓ RAG integrado para búsqueda semántica
✓ IA local (Ollama) para determinaciones
✓ Base de datos SQLite auditable
✓ API REST entre componentes
✓ Sistema privado 100% local
✓ Listo para producción

¡A construir! 🚀
