# ESTRUCTURA COMPLETA DEL PROYECTO XCODE - SwiftUI

```
DisciplinarySystem/
├── DisciplinarySystem.xcodeproj/
│   ├── project.pbxproj                          # Configuración del proyecto
│   ├── project.xcworkspace/
│   │   └── contents.xcworkspacedata
│   └── xcshareddata/
│       └── xcschemes/
│           └── DisciplinarySystem.xcscheme
│
├── DisciplinarySystem/                          # APP TARGET
│   ├── App/
│   │   ├── DisciplinarySystemApp.swift          # @main entry point
│   │   ├── ContentView.swift                    # Root view
│   │   └── AppDelegate.swift
│   │
│   ├── Views/
│   │   ├── Dashboard/
│   │   │   ├── DashboardView.swift              # Main dashboard
│   │   │   ├── CaseStatisticsView.swift        # Estadísticas
│   │   │   └── CaseListView.swift              # Listado de casos
│   │   │
│   │   ├── Cases/
│   │   │   ├── CaseDetailView.swift            # Detalles del caso
│   │   │   ├── NewCaseView.swift               # Crear nuevo caso
│   │   │   ├── CaseEditView.swift              # Editar caso
│   │   │   └── CaseTabView.swift               # Tab navigation
│   │   │
│   │   ├── Hearings/
│   │   │   ├── HearingsView.swift              # Listado de comparecencias
│   │   │   ├── NewHearingView.swift            # Registrar comparecencia
│   │   │   ├── AudioRecorderView.swift         # Grabador de audio
│   │   │   ├── TranscriptView.swift            # Ver transcripción
│   │   │   └── HearingDetailView.swift
│   │   │
│   │   ├── Evidence/
│   │   │   ├── EvidenceView.swift              # Listado de evidencias
│   │   │   ├── EvidenceDetailView.swift
│   │   │   ├── NewEvidenceView.swift           # Agregar evidencia
│   │   │   └── FilePickerView.swift
│   │   │
│   │   ├── Determination/
│   │   │   ├── DeterminationView.swift         # ⭐ CORE - Análisis final
│   │   │   ├── RecommendationCardView.swift    # Tarjeta de recomendación
│   │   │   ├── ArticlesView.swift              # Artículos aplicables
│   │   │   ├── ConfidenceGaugeView.swift       # Indicador de confianza
│   │   │   ├── ValidationView.swift            # Validación del usuario
│   │   │   └── LoadingStateView.swift
│   │   │
│   │   ├── Resolution/
│   │   │   ├── ResolutionView.swift            # Ver resolución
│   │   │   ├── ResolutionGeneratorView.swift   # Generar resolución
│   │   │   ├── ResolutionTemplateView.swift    # Template HTML/PDF
│   │   │   └── ExportResolutionView.swift      # Exportar a PDF
│   │   │
│   │   ├── Settings/
│   │   │   ├── SettingsView.swift              # Configuración general
│   │   │   ├── StatuteUploadView.swift         # Cargar estatutos
│   │   │   ├── UserSettingsView.swift          # Preferencias usuario
│   │   │   └── AboutView.swift
│   │   │
│   │   ├── Components/
│   │   │   ├── LoadingView.swift               # Loading spinner
│   │   │   ├── ErrorView.swift                 # Error display
│   │   │   ├── EmptyStateView.swift            # Empty state
│   │   │   ├── NavigationHeaderView.swift      # Header reusable
│   │   │   ├── StatusBadgeView.swift           # Status badges
│   │   │   ├── ArticleCardView.swift           # Card para artículos
│   │   │   └── ConfirmationDialogView.swift    # Confirmación
│   │   │
│   │   └── Onboarding/
│   │       ├── OnboardingView.swift            # First launch
│   │       ├── SetupWizardView.swift           # Setup inicial
│   │       └── WelcomeView.swift
│   │
│   ├── Models/
│   │   ├── Case.swift                          # CaseModel
│   │   ├── Hearing.swift                       # HearingModel
│   │   ├── Evidence.swift                      # EvidenceModel
│   │   ├── AIRecommendation.swift              # Recomendación IA
│   │   ├── Resolution.swift                    # ResolutionModel
│   │   ├── StatutoryArticle.swift              # Artículo estatutario
│   │   ├── APIResponse.swift                   # API response wrapper
│   │   └── UIModels.swift                      # UI-specific models
│   │
│   ├── ViewModels/
│   │   ├── DashboardViewModel.swift            # Dashboard logic
│   │   ├── CaseViewModel.swift                 # Case management
│   │   ├── HearingViewModel.swift              # Hearing management
│   │   ├── EvidenceViewModel.swift             # Evidence management
│   │   ├── DeterminationViewModel.swift        # ⭐ Determination logic
│   │   ├── ResolutionViewModel.swift           # Resolution generation
│   │   ├── SettingsViewModel.swift             # Settings logic
│   │   └── AppState.swift                      # Global app state
│   │
│   ├── Services/
│   │   ├── APIService.swift                    # HTTP client
│   │   ├── CaseService.swift                   # Case API calls
│   │   ├── HearingService.swift                # Hearing API calls
│   │   ├── DeterminationService.swift          # ⭐ Determination API
│   │   ├── AudioService.swift                  # Audio recording
│   │   ├── StorageService.swift                # Local storage
│   │   ├── NotificationService.swift           # Notifications
│   │   └── AuthenticationService.swift         # Auth
│   │
│   ├── Utilities/
│   │   ├── Constants.swift                     # App constants
│   │   ├── Extensions.swift                    # Swift extensions
│   │   ├── DateFormatter+Extensions.swift
│   │   ├── Color+Extensions.swift
│   │   ├── Localization.swift                  # i18n strings
│   │   ├── Logger.swift                        # Logging
│   │   └── Helpers.swift
│   │
│   ├── Assets/
│   │   ├── Colors.xcassets/
│   │   │   ├── AccentColor
│   │   │   ├── PrimaryColor
│   │   │   ├── SecondaryColor
│   │   │   └── StatusColors/
│   │   │       ├── OpenCase
│   │   │       ├── InProgress
│   │   │       ├── Amonestacion
│   │   │       ├── Conciliacion
│   │   │       └── Consignacion
│   │   │
│   │   ├── Images.xcassets/
│   │   │   ├── AppIcon
│   │   │   ├── LaunchScreen
│   │   │   └── Icons/
│   │   │       ├── dashboard
│   │   │       ├── case
│   │   │       ├── hearing
│   │   │       ├── evidence
│   │   │       ├── determination
│   │   │       ├── resolution
│   │   │       └── settings
│   │   │
│   │   ├── Fonts/
│   │   │   └── (if custom fonts)
│   │   │
│   │   └── Localizable.strings/
│   │       ├── en
│   │       └── es
│   │
│   ├── Styles/
│   │   ├── AppTheme.swift                      # Theme configuration
│   │   ├── Typography.swift                    # Font styles
│   │   ├── Spacing.swift                       # Spacing constants
│   │   └── Shadows.swift                       # Shadow styles
│   │
│   ├── Preview Content/
│   │   ├── PreviewData.swift                   # Mock data for previews
│   │   └── Previews.swift
│   │
│   └── Info.plist                              # App metadata
│
├── DisciplinarySystemTests/                     # UNIT TESTS
│   ├── DisciplinarySystemTests.swift
│   ├── ViewModelTests/
│   │   ├── DeterminationViewModelTests.swift
│   │   ├── CaseViewModelTests.swift
│   │   └── DashboardViewModelTests.swift
│   │
│   ├── ServiceTests/
│   │   ├── APIServiceTests.swift
│   │   ├── DeterminationServiceTests.swift
│   │   └── StorageServiceTests.swift
│   │
│   └── ModelTests/
│       └── ModelTests.swift
│
├── DisciplinarySystemUITests/                   # UI TESTS
│   ├── DisciplinarySystemUITests.swift
│   ├── DashboardUITests.swift
│   ├── DeterminationUITests.swift
│   └── SettingsUITests.swift
│
├── Podfile                                      # CocoaPods (si se usa)
├── Podfile.lock
├── .gitignore
├── README.md
└── ARCHITECTURE.md                              # Arquitectura del app
```

## ARCHIVOS PRINCIPALES A CREAR

### 1. DisciplinarySystemApp.swift
```swift
import SwiftUI

@main
struct DisciplinarySystemApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}
```

### 2. ContentView.swift (Root)
```swift
import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            DashboardView()
                .tabItem {
                    Label("Dashboard", systemImage: "chart.bar.fill")
                }
                .tag(0)
            
            CaseListView()
                .tabItem {
                    Label("Casos", systemImage: "folder.fill")
                }
                .tag(1)
            
            DeterminationView(caseId: "")
                .tabItem {
                    Label("Análisis", systemImage: "brain")
                }
                .tag(2)
            
            SettingsView()
                .tabItem {
                    Label("Configuración", systemImage: "gear")
                }
                .tag(3)
        }
    }
}
```

### 3. Modelos principales

**Case.swift**
```swift
import Foundation

struct Case: Codable, Identifiable {
    let id: String
    let caseNumber: String
    let title: String
    let complainantName: String
    let respondentName: String
    let status: CaseStatus
    let resolutionType: ResolutionType?
    let complaintDate: Date
    let description: String
    let createdAt: Date
    let updatedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id = "case_id"
        case caseNumber = "case_number"
        // ... resto
    }
}

enum CaseStatus: String, Codable {
    case open = "abierto"
    case investigation = "investigacion"
    case closed = "concluido"
}

enum ResolutionType: String, Codable {
    case warning = "amonestacion"
    case reconciliation = "conciliacion"
    case referral = "consignacion"
}
```

**AIRecommendation.swift**
```swift
import Foundation

struct AIRecommendation: Codable, Identifiable {
    let id: String
    let caseId: String
    let primaryRecommendation: String
    let confidenceScore: Double
    let caseSummary: String
    let keyFindings: [String]
    let applicableArticles: [StatutoryArticle]
    let legalJustification: String
    let statuteCitations: [StatuteCitation]
    let alternative1: String?
    let alternative1Confidence: Double?
    let alternative2: String?
    let alternative2Confidence: Double?
    
    enum CodingKeys: String, CodingKey {
        case id = "recommendation_id"
        // ... resto
    }
}

struct StatuteCitation: Codable {
    let article: String
    let citedText: String?
}
```

### 4. ViewModels

**DeterminationViewModel.swift**
```swift
import SwiftUI
import Combine

class DeterminationViewModel: ObservableObject {
    @Published var recommendation: AIRecommendation?
    @Published var isLoading = false
    @Published var error: String?
    @Published var selectedDecision: String = ""
    
    private let service = DeterminationService()
    
    func generateRecommendation(for caseId: String) {
        isLoading = true
        error = nil
        
        Task {
            do {
                let rec = try await service.generateRecommendation(caseId: caseId)
                DispatchQueue.main.async {
                    self.recommendation = rec
                    self.isLoading = false
                }
            } catch {
                DispatchQueue.main.async {
                    self.error = error.localizedDescription
                    self.isLoading = false
                }
            }
        }
    }
    
    func submitValidation() {
        guard let rec = recommendation, !selectedDecision.isEmpty else { return }
        
        Task {
            do {
                try await service.validateRecommendation(
                    recommendationId: rec.id,
                    finalDecision: selectedDecision
                )
            } catch {
                DispatchQueue.main.async {
                    self.error = error.localizedDescription
                }
            }
        }
    }
}
```

### 5. Services

**DeterminationService.swift**
```swift
import Foundation

class DeterminationService {
    private let apiService = APIService()
    
    func generateRecommendation(caseId: String) async throws -> AIRecommendation {
        let url = URL(string: "http://localhost:5000/api/determination/\(caseId)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        
        let response = try JSONDecoder().decode(
            APIResponse<AIRecommendation>.self,
            from: data
        )
        
        return response.data
    }
    
    func validateRecommendation(
        recommendationId: String,
        finalDecision: String
    ) async throws {
        let url = URL(string: "http://localhost:5000/api/determination/validate")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let payload = [
            "recommendation_id": recommendationId,
            "final_decision": finalDecision,
            "validated_by": "current_user"
        ] as [String : Any]
        
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        
        let (_, _) = try await URLSession.shared.data(for: request)
    }
}
```

### 6. Assets

**AppTheme.swift**
```swift
import SwiftUI

struct AppTheme {
    static let primary = Color(red: 0.2, green: 0.5, blue: 0.9)
    static let secondary = Color(red: 0.95, green: 0.95, blue: 0.95)
    static let success = Color(red: 0.3, green: 0.8, blue: 0.4)
    static let warning = Color(red: 1.0, green: 0.8, blue: 0.2)
    static let danger = Color(red: 0.9, green: 0.3, blue: 0.3)
}
```

## Info.plist Required Keys

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" ...>
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>es</string>
    
    <key>CFBundleDisplayName</key>
    <string>Sistema Disciplinario</string>
    
    <key>CFBundleIdentifier</key>
    <string>com.institucion.disciplinario</string>
    
    <key>CFBundleVersion</key>
    <string>1</string>
    
    <key>CFBundleShortVersionString</key>
    <string>1.0.0</string>
    
    <key>MinimumOSVersion</key>
    <string>14.0</string>
    
    <key>NSLocalNetworkUsageDescription</key>
    <string>La app necesita acceso a la red local para conectarse al servidor.</string>
    
    <key>NSBonjourServices</key>
    <array>
        <string>_http._tcp</string>
    </array>
</dict>
</plist>
```
