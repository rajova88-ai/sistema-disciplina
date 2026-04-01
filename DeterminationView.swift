import SwiftUI
import Foundation

// ============================================================================
// MODELS
// ============================================================================

struct AIRecommendationModel: Codable {
    let recommendationId: String
    let caseId: String
    let primaryRecommendation: String // "amonestacion", "conciliacion", "consignacion"
    let confidenceScore: Double
    let caseSummary: String
    let keyFindings: [String]
    let applicableArticles: [StatutoryArticleModel]
    let legalJustification: String
    let statuteCitations: [StatuteCitation]
    let alternative1: String?
    let alternative1Confidence: Double?
    let alternative2: String?
    let alternative2Confidence: Double?
    
    enum CodingKeys: String, CodingKey {
        case recommendationId = "recommendation_id"
        case caseId = "case_id"
        case primaryRecommendation = "primary_recommendation"
        case confidenceScore = "confidence_score"
        case caseSummary = "case_summary"
        case keyFindings = "key_findings"
        case applicableArticles = "applicable_articles"
        case legalJustification = "legal_justification"
        case statuteCitations = "statute_citations"
        case alternative1 = "alternative_1"
        case alternative1Confidence = "alternative_1_confidence"
        case alternative2 = "alternative_2"
        case alternative2Confidence = "alternative_2_confidence"
    }
}

struct StatutoryArticleModel: Codable, Identifiable {
    let id: String
    let articleNumber: String
    let articleTitle: String
    let articleText: String
    let sanctionSeverityLevel: Int
    let applicableSanctions: [String]
    
    enum CodingKeys: String, CodingKey {
        case id = "article_id"
        case articleNumber = "article_number"
        case articleTitle = "article_title"
        case articleText = "article_text"
        case sanctionSeverityLevel = "sanction_severity_level"
        case applicableSanctions = "applicable_sanctions"
    }
}

struct StatuteCitation: Codable {
    let article: String
    let citedText: String?
    
    enum CodingKeys: String, CodingKey {
        case article
        case citedText = "cited_text"
    }
}

// ============================================================================
// VISTA PRINCIPAL: DETERMINATION VIEW
// ============================================================================

struct DeterminationView: View {
    @State private var recommendation: AIRecommendationModel?
    @State private var isLoading: Bool = false
    @State private var selectedDecision: String = ""
    @State private var showConfirmationDialog: Bool = false
    @State private var showSuccessAlert: Bool = false
    @State private var errorMessage: String = ""
    
    let caseId: String
    let caseName: String
    
    var body: some View {
        ZStack {
            // Fondo
            Color(nsColor: NSColor(white: 0.96, alpha: 1.0))
                .ignoresSafeArea()
            
            VStack(spacing: 0) {
                // Header
                VStack(alignment: .leading, spacing: 12) {
                    Text("Análisis de Determinación Final")
                        .font(.system(size: 24, weight: .bold, design: .default))
                        .foregroundColor(.black)
                    
                    Text(caseName)
                        .font(.system(size: 13, weight: .regular, design: .default))
                        .foregroundColor(.gray)
                    
                    Divider()
                        .background(Color.gray.opacity(0.3))
                }
                .padding(20)
                .background(Color.white)
                
                // Contenido Principal
                ScrollView(.vertical, showsIndicators: true) {
                    VStack(spacing: 16) {
                        if isLoading {
                            LoadingStateView()
                        } else if let recommendation = recommendation {
                            RecommendationContentView(
                                recommendation: recommendation,
                                selectedDecision: $selectedDecision
                            )
                        } else if !errorMessage.isEmpty {
                            ErrorStateView(message: errorMessage)
                        } else {
                            EmptyStateView()
                        }
                    }
                    .padding(20)
                }
                
                // Footer con Acciones
                if let recommendation = recommendation {
                    VStack(spacing: 12) {
                        Divider()
                            .background(Color.gray.opacity(0.2))
                        
                        HStack(spacing: 12) {
                            Button(action: { /* Volver */ }) {
                                Text("Cancelar")
                                    .font(.system(size: 13, weight: .medium))
                                    .frame(maxWidth: .infinity)
                                    .padding(12)
                                    .background(Color(nsColor: NSColor(white: 0.95, alpha: 1.0)))
                                    .foregroundColor(.black)
                                    .cornerRadius(6)
                            }
                            
                            Button(action: {
                                if !selectedDecision.isEmpty {
                                    showConfirmationDialog = true
                                }
                            }) {
                                Text("Confirmar Decisión")
                                    .font(.system(size: 13, weight: .semibold))
                                    .frame(maxWidth: .infinity)
                                    .padding(12)
                                    .background(selectedDecision.isEmpty ? 
                                               Color.gray.opacity(0.3) :
                                               Color(nsColor: NSColor(red: 0.2, green: 0.5, blue: 0.9, alpha: 1.0)))
                                    .foregroundColor(selectedDecision.isEmpty ? .gray : .white)
                                    .cornerRadius(6)
                            }
                            .disabled(selectedDecision.isEmpty)
                        }
                        .padding(20)
                    }
                    .background(Color.white)
                }
            }
        }
        .confirmationDialog(
            "Confirmar Resolución",
            isPresented: $showConfirmationDialog,
            presenting: recommendation,
            actions: { rec in
                Button("Confirmar \(selectedDecision.uppercased())", role: .default) {
                    submitFinalDecision(recommendation: rec)
                }
                Button("Cancelar", role: .cancel) { }
            },
            message: { rec in
                Text("¿Confirma la resolución como \(selectedDecision.uppercased())? Esta acción es definitiva y será registrada en auditoría.")
            }
        )
        .alert("Resolución Registrada", isPresented: $showSuccessAlert) {
            Button("Aceptar") { }
        } message: {
            Text("La resolución ha sido guardada correctamente.")
        }
        .onAppear {
            loadRecommendation()
        }
    }
    
    private func loadRecommendation() {
        isLoading = true
        
        // Llamar a Python backend para generar recomendación
        Task {
            do {
                let recommendation = try await generateAIRecommendation()
                DispatchQueue.main.async {
                    self.recommendation = recommendation
                    isLoading = false
                }
            } catch {
                DispatchQueue.main.async {
                    errorMessage = error.localizedDescription
                    isLoading = false
                }
            }
        }
    }
    
    private func generateAIRecommendation() async throws -> AIRecommendationModel {
        // En Swift, hacer llamada HTTP al servidor Python
        let url = URL(string: "http://localhost:5000/api/determination/\(caseId)")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        let (data, response) = try await URLSession.shared.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw NSError(domain: "HTTP", code: -1, userInfo: [:])
        }
        
        let decoder = JSONDecoder()
        let recommendation = try decoder.decode(AIRecommendationModel.self, from: data)
        return recommendation
    }
    
    private func submitFinalDecision(recommendation: AIRecommendationModel) {
        // Enviar decisión final al servidor
        Task {
            do {
                let url = URL(string: "http://localhost:5000/api/determination/validate")!
                var request = URLRequest(url: url)
                request.httpMethod = "POST"
                request.setValue("application/json", forHTTPHeaderField: "Content-Type")
                
                let payload = [
                    "recommendation_id": recommendation.recommendationId,
                    "final_decision": selectedDecision,
                    "validated_by": "current_user"
                ] as [String : Any]
                
                request.httpBody = try JSONSerialization.data(withJSONObject: payload)
                
                let (_, response) = try await URLSession.shared.data(for: request)
                
                if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
                    DispatchQueue.main.async {
                        showSuccessAlert = true
                    }
                }
            } catch {
                errorMessage = error.localizedDescription
            }
        }
    }
}

// ============================================================================
// SUBVISTAS COMPONENTES
// ============================================================================

struct RecommendationContentView: View {
    let recommendation: AIRecommendationModel
    @Binding var selectedDecision: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            // Tarjeta de Recomendación Principal
            RecommendationCardView(recommendation: recommendation, selectedDecision: $selectedDecision)
            
            // Hallazgos Clave
            KeyFindingsView(findings: recommendation.keyFindings)
            
            // Artículos Aplicables
            ApplicableArticlesView(articles: recommendation.applicableArticles)
            
            // Fundamentación Legal
            LegalJustificationView(justification: recommendation.legalJustification)
            
            // Alternativas (si las hay)
            if let alt1 = recommendation.alternative1 {
                AlternativesView(
                    alt1: alt1,
                    conf1: recommendation.alternative1Confidence ?? 0.0,
                    alt2: recommendation.alternative2,
                    conf2: recommendation.alternative2Confidence ?? 0.0
                )
            }
        }
    }
}

struct RecommendationCardView: View {
    let recommendation: AIRecommendationModel
    @Binding var selectedDecision: String
    
    var primaryColor: Color {
        switch recommendation.primaryRecommendation {
        case "amonestacion":
            return Color(nsColor: NSColor(red: 1.0, green: 0.8, blue: 0.2, alpha: 1.0))
        case "conciliacion":
            return Color(nsColor: NSColor(red: 0.3, green: 0.8, blue: 0.4, alpha: 1.0))
        case "consignacion":
            return Color(nsColor: NSColor(red: 0.9, green: 0.3, blue: 0.3, alpha: 1.0))
        default:
            return Color.gray
        }
    }
    
    var recommendationLabel: String {
        switch recommendation.primaryRecommendation {
        case "amonestacion":
            return "AMONESTACIÓN"
        case "conciliacion":
            return "CONCILIACIÓN"
        case "consignacion":
            return "CONSIGNACIÓN"
        default:
            return "DESCONOCIDA"
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            HStack(spacing: 12) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("RECOMENDACIÓN PRINCIPAL")
                        .font(.system(size: 11, weight: .semibold))
                        .foregroundColor(.gray)
                        .tracking(1.0)
                    
                    Text(recommendationLabel)
                        .font(.system(size: 20, weight: .bold, design: .default))
                        .foregroundColor(.black)
                    
                    HStack(spacing: 6) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.system(size: 12))
                            .foregroundColor(primaryColor)
                        
                        Text("\(Int(recommendation.confidenceScore * 100))% Confianza")
                            .font(.system(size: 12, weight: .regular))
                            .foregroundColor(.gray)
                    }
                }
                
                Spacer()
                
                // Indicador de Confianza
                ConfidenceGaugeView(confidence: recommendation.confidenceScore, color: primaryColor)
            }
            
            Divider()
                .background(Color.gray.opacity(0.2))
            
            Text(recommendation.caseSummary)
                .font(.system(size: 13, weight: .regular, design: .default))
                .foregroundColor(.black)
                .lineLimit(nil)
            
            // Selector de Decisión Final
            VStack(alignment: .leading, spacing: 10) {
                Text("Tu Decisión Final")
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundColor(.gray)
                    .tracking(0.5)
                
                HStack(spacing: 10) {
                    ForEach(["amonestacion", "conciliacion", "consignacion"], id: \.self) { option in
                        Button(action: { selectedDecision = option }) {
                            Text(optionLabel(option))
                                .font(.system(size: 11, weight: .semibold))
                                .frame(maxWidth: .infinity)
                                .padding(10)
                                .background(selectedDecision == option ?
                                           getOptionColor(option) :
                                           Color(nsColor: NSColor(white: 0.93, alpha: 1.0)))
                                .foregroundColor(selectedDecision == option ? .white : .black)
                                .cornerRadius(5)
                        }
                        .buttonStyle(PlainButtonStyle())
                    }
                }
            }
            .padding(12)
            .background(Color(nsColor: NSColor(white: 0.99, alpha: 1.0)))
            .cornerRadius(6)
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(8)
        .shadow(color: .black.opacity(0.08), radius: 4, x: 0, y: 2)
    }
    
    private func optionLabel(_ option: String) -> String {
        switch option {
        case "amonestacion": return "Amonestación"
        case "conciliacion": return "Conciliación"
        case "consignacion": return "Consignación"
        default: return option
        }
    }
    
    private func getOptionColor(_ option: String) -> Color {
        switch option {
        case "amonestacion":
            return Color(nsColor: NSColor(red: 1.0, green: 0.8, blue: 0.2, alpha: 1.0))
        case "conciliacion":
            return Color(nsColor: NSColor(red: 0.3, green: 0.8, blue: 0.4, alpha: 1.0))
        case "consignacion":
            return Color(nsColor: NSColor(red: 0.9, green: 0.3, blue: 0.3, alpha: 1.0))
        default:
            return Color.gray
        }
    }
}

struct ConfidenceGaugeView: View {
    let confidence: Double
    let color: Color
    
    var body: some View {
        ZStack {
            Circle()
                .stroke(Color.gray.opacity(0.2), lineWidth: 4)
            
            Circle()
                .trim(from: 0, to: confidence)
                .stroke(color, style: StrokeStyle(lineWidth: 4, lineCap: .round))
                .rotationEffect(.degrees(-90))
            
            VStack(spacing: 4) {
                Text("\(Int(confidence * 100))%")
                    .font(.system(size: 14, weight: .bold, design: .monospaced))
                    .foregroundColor(.black)
                
                Text("confianza")
                    .font(.system(size: 9, weight: .regular))
                    .foregroundColor(.gray)
            }
        }
        .frame(width: 80, height: 80)
    }
}

struct KeyFindingsView: View {
    let findings: [String]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("HALLAZGOS CLAVE")
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.gray)
                .tracking(0.5)
            
            VStack(alignment: .leading, spacing: 8) {
                ForEach(findings.indices, id: \.self) { index in
                    HStack(alignment: .top, spacing: 10) {
                        Text("\(index + 1).")
                            .font(.system(size: 12, weight: .semibold))
                            .foregroundColor(Color(nsColor: NSColor(red: 0.2, green: 0.5, blue: 0.9, alpha: 1.0)))
                            .frame(width: 20, alignment: .leading)
                        
                        Text(findings[index])
                            .font(.system(size: 12, weight: .regular))
                            .foregroundColor(.black)
                            .lineLimit(nil)
                    }
                }
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(8)
    }
}

struct ApplicableArticlesView: View {
    let articles: [StatutoryArticleModel]
    @State private var expandedArticles: Set<String> = []
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("ARTÍCULOS APLICABLES")
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.gray)
                .tracking(0.5)
            
            VStack(spacing: 10) {
                ForEach(articles) { article in
                    ArticleCardView(
                        article: article,
                        isExpanded: expandedArticles.contains(article.id),
                        onTap: {
                            if expandedArticles.contains(article.id) {
                                expandedArticles.remove(article.id)
                            } else {
                                expandedArticles.insert(article.id)
                            }
                        }
                    )
                }
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(8)
    }
}

struct ArticleCardView: View {
    let article: StatutoryArticleModel
    let isExpanded: Bool
    let onTap: () -> Void
    
    var severityColor: Color {
        switch article.sanctionSeverityLevel {
        case 3:
            return Color(nsColor: NSColor(red: 0.9, green: 0.3, blue: 0.3, alpha: 1.0))
        case 2:
            return Color(nsColor: NSColor(red: 1.0, green: 0.8, blue: 0.2, alpha: 1.0))
        default:
            return Color(nsColor: NSColor(red: 0.3, green: 0.8, blue: 0.4, alpha: 1.0))
        }
    }
    
    var severityLabel: String {
        switch article.sanctionSeverityLevel {
        case 3: return "Grave"
        case 2: return "Moderado"
        default: return "Leve"
        }
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack(spacing: 10) {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Art. \(article.articleNumber)")
                        .font(.system(size: 12, weight: .semibold, design: .monospaced))
                        .foregroundColor(Color(nsColor: NSColor(red: 0.2, green: 0.5, blue: 0.9, alpha: 1.0)))
                    
                    Text(article.articleTitle)
                        .font(.system(size: 13, weight: .semibold))
                        .foregroundColor(.black)
                        .lineLimit(2)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text(severityLabel)
                        .font(.system(size: 10, weight: .semibold))
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(severityColor.opacity(0.2))
                        .foregroundColor(severityColor)
                        .cornerRadius(4)
                    
                    Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                        .font(.system(size: 12, weight: .semibold))
                        .foregroundColor(.gray)
                }
            }
            
            if isExpanded {
                Divider()
                    .background(Color.gray.opacity(0.2))
                
                Text(article.articleText)
                    .font(.system(size: 11, weight: .regular, design: .default))
                    .foregroundColor(.black)
                    .lineLimit(nil)
                
                HStack(spacing: 8) {
                    ForEach(article.applicableSanctions, id: \.self) { sanction in
                        Text(sanction)
                            .font(.system(size: 10, weight: .semibold))
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.gray.opacity(0.1))
                            .foregroundColor(.gray)
                            .cornerRadius(3)
                    }
                }
            }
        }
        .padding(12)
        .background(Color(nsColor: NSColor(white: 0.98, alpha: 1.0)))
        .cornerRadius(6)
        .onTapGesture(perform: onTap)
    }
}

struct LegalJustificationView: View {
    let justification: String
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("FUNDAMENTACIÓN LEGAL")
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.gray)
                .tracking(0.5)
            
            Text(justification)
                .font(.system(size: 12, weight: .regular, design: .default))
                .foregroundColor(.black)
                .lineLimit(nil)
                .padding(16)
                .background(Color(nsColor: NSColor(white: 0.99, alpha: 1.0)))
                .cornerRadius(6)
                .border(Color.gray.opacity(0.2), width: 1)
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(8)
    }
}

struct AlternativesView: View {
    let alt1: String
    let conf1: Double
    let alt2: String?
    let conf2: Double
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("ALTERNATIVAS CONSIDERADAS")
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.gray)
                .tracking(0.5)
            
            HStack(spacing: 10) {
                AlternativeOptionView(sanction: alt1, confidence: conf1)
                
                if let alt2 = alt2 {
                    AlternativeOptionView(sanction: alt2, confidence: conf2)
                }
            }
        }
        .padding(16)
        .background(Color.white)
        .cornerRadius(8)
    }
}

struct AlternativeOptionView: View {
    let sanction: String
    let confidence: Double
    
    var body: some View {
        VStack(alignment: .center, spacing: 8) {
            Text(sanction.capitalized)
                .font(.system(size: 12, weight: .semibold))
                .foregroundColor(.black)
            
            Text("\(Int(confidence * 100))%")
                .font(.system(size: 14, weight: .bold, design: .monospaced))
                .foregroundColor(.gray)
        }
        .frame(maxWidth: .infinity)
        .padding(12)
        .background(Color(nsColor: NSColor(white: 0.95, alpha: 1.0)))
        .cornerRadius(6)
    }
}

struct LoadingStateView: View {
    @State private var isAnimating = false
    
    var body: some View {
        VStack(spacing: 16) {
            ProgressView()
                .frame(width: 40, height: 40)
            
            Text("Analizando caso y generando recomendación...")
                .font(.system(size: 13, weight: .regular))
                .foregroundColor(.gray)
            
            Text("Procese: Recuperación de datos → Análisis RAG → IA")
                .font(.system(size: 11, weight: .regular, design: .monospaced))
                .foregroundColor(.gray.opacity(0.6))
        }
        .padding(40)
        .frame(maxWidth: .infinity)
        .background(Color.white)
        .cornerRadius(8)
    }
}

struct ErrorStateView: View {
    let message: String
    
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "exclamationmark.triangle.fill")
                .font(.system(size: 32))
                .foregroundColor(Color(nsColor: NSColor(red: 0.9, green: 0.3, blue: 0.3, alpha: 1.0)))
            
            Text("Error en Análisis")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.black)
            
            Text(message)
                .font(.system(size: 12, weight: .regular))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
        }
        .padding(20)
        .frame(maxWidth: .infinity)
        .background(Color.white)
        .cornerRadius(8)
    }
}

struct EmptyStateView: View {
    var body: some View {
        VStack(spacing: 12) {
            Image(systemName: "doc.text.magnifyingglass")
                .font(.system(size: 32))
                .foregroundColor(.gray)
            
            Text("Sin Recomendación Disponible")
                .font(.system(size: 14, weight: .semibold))
                .foregroundColor(.black)
            
            Text("Presione el botón de Análisis para generar una recomendación")
                .font(.system(size: 12, weight: .regular))
                .foregroundColor(.gray)
                .multilineTextAlignment(.center)
        }
        .padding(20)
        .frame(maxWidth: .infinity)
        .background(Color.white)
        .cornerRadius(8)
    }
}

// ============================================================================
// PREVIEW
// ============================================================================

#Preview {
    DeterminationView(
        caseId: "case_001",
        caseName: "Expediente #2024-001: Conducta Inapropiada"
    )
}
