#!/usr/bin/env python3
# ============================================================================
# INDEXADOR DE ESTATUTOS - GENERACIÓN DE EMBEDDINGS PARA RAG
# ============================================================================

import os
import sys
import sqlite3
import json
import uuid
import re
from datetime import datetime
from pathlib import Path

import pdfplumber
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
from dotenv import load_dotenv

# Cargar variables
load_dotenv()

DB_PATH = os.path.expanduser(os.getenv('DB_PATH', '~/.disciplina/db/disciplina.db'))
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
EMBEDDING_DIR = os.path.expanduser(os.getenv('EMBEDDING_DIR', '~/.disciplina/embeddings'))
STATUTE_DIR = os.path.expanduser(os.getenv('STATUTE_DIR', '~/.disciplina/data/statutes'))


class StatuteIndexer:
    """Indexa PDFs de estatutos con embeddings para RAG"""
    
    def __init__(self):
        self.db = sqlite3.connect(DB_PATH)
        self.db.row_factory = sqlite3.Row
        print(f"✓ Modelo de embeddings: {EMBEDDING_MODEL}")
        self.model = SentenceTransformer(EMBEDDING_MODEL)
        print(f"✓ Dimensión de embeddings: {self.model.get_sentence_embedding_dimension()}")
    
    def index_pdf(self, pdf_path: str, statute_version: str = None):
        """
        Indexa un PDF de estatutos:
        1. Parsea PDF
        2. Extrae artículos
        3. Genera embeddings
        4. Guarda en DB
        """
        if not os.path.exists(pdf_path):
            print(f"❌ Archivo no encontrado: {pdf_path}")
            return False
        
        print(f"\n{'='*80}")
        print(f"INDEXANDO ESTATUTO: {os.path.basename(pdf_path)}")
        print(f"{'='*80}\n")
        
        try:
            # 1. EXTRAER TEXTO DEL PDF
            print("1️⃣  Extrayendo texto del PDF...")
            articles = self._extract_articles_from_pdf(pdf_path)
            
            if not articles:
                print("❌ No se encontraron artículos en el PDF")
                return False
            
            print(f"   ✓ {len(articles)} artículos extraídos\n")
            
            # 2. CREAR REGISTRO DE ESTATUTO
            print("2️⃣  Creando registro de estatuto...")
            statute_id = f"statute_{uuid.uuid4().hex[:12]}"
            statute_version = statute_version or f"v{datetime.now().strftime('%Y.%m.%d')}"
            
            pdf_hash = self._calculate_file_hash(pdf_path)
            
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO statute_index (
                    statute_id, statute_version, statute_upload_date,
                    pdf_file_path, pdf_hash, pdf_total_pages,
                    total_articles, indexed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                statute_id,
                statute_version,
                datetime.now().isoformat(),
                pdf_path,
                pdf_hash,
                0,  # Se calcula después
                len(articles),
                datetime.now().isoformat()
            ))
            self.db.commit()
            print(f"   ✓ Estatuto ID: {statute_id}\n")
            
            # 3. GENERAR EMBEDDINGS E INDEXAR
            print("3️⃣  Generando embeddings (puede tomar tiempo)...\n")
            
            embeddings_to_save = []
            
            for i, article in enumerate(tqdm(articles, desc="Procesando artículos")):
                # Generar embedding del texto del artículo
                embedding = self.model.encode(
                    article['full_text'],
                    convert_to_numpy=True,
                    normalize_embeddings=True
                )
                
                article_id = f"article_{uuid.uuid4().hex[:12]}"
                
                # Guardar en DB
                cursor.execute("""
                    INSERT INTO statute_articles (
                        article_id, statute_id, article_number,
                        article_chapter, article_title, article_full_text,
                        article_summary, article_keywords,
                        applicable_sanctions, sanction_severity_level,
                        embedding_vector, extracted_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article_id,
                    statute_id,
                    article['number'],
                    article.get('chapter', 'General'),
                    article.get('title', ''),
                    article['full_text'],
                    article.get('summary', ''),
                    json.dumps(article.get('keywords', [])),
                    json.dumps(article.get('sanctions', ['amonestacion'])),
                    article.get('severity', 1),
                    embedding.tobytes(),  # Guardar como BLOB
                    datetime.now().isoformat()
                ))
                
                embeddings_to_save.append({
                    'article_id': article_id,
                    'article_number': article['number'],
                    'embedding': embedding
                })
            
            self.db.commit()
            print(f"\n   ✓ {len(articles)} artículos indexados con embeddings")
            
            # 4. GUARDAR EMBEDDINGS EN DISCO (para búsquedas rápidas)
            print("\n4️⃣  Guardando embeddings en disco...")
            embedding_file = os.path.join(
                EMBEDDING_DIR,
                f"embeddings_{statute_id}.npy"
            )
            
            embeddings_array = np.array([e['embedding'] for e in embeddings_to_save])
            np.save(embedding_file, embeddings_array)
            
            # Guardar metadata
            metadata_file = embedding_file.replace('.npy', '_metadata.json')
            metadata = {
                'statute_id': statute_id,
                'statute_version': statute_version,
                'created_at': datetime.now().isoformat(),
                'articles': [
                    {
                        'article_id': e['article_id'],
                        'article_number': e['article_number'],
                        'index': i
                    }
                    for i, e in enumerate(embeddings_to_save)
                ]
            }
            
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"   ✓ Embeddings guardados: {embedding_file}")
            print(f"   ✓ Metadata guardada: {metadata_file}")
            
            # 5. RESUMEN FINAL
            print(f"\n{'='*80}")
            print("✅ INDEXACIÓN COMPLETADA")
            print(f"{'='*80}")
            print(f"Estatuto: {statute_version}")
            print(f"Artículos: {len(articles)}")
            print(f"Dimensión embeddings: {embeddings_array.shape}")
            print(f"Espacio en disco: {embeddings_array.nbytes / 1024 / 1024:.2f} MB")
            
            return True
        
        except Exception as e:
            print(f"\n❌ Error indexando PDF: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _extract_articles_from_pdf(self, pdf_path: str) -> list:
        """Extrae artículos del PDF"""
        articles = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() + "\n"
            
            # Patrones para detectar artículos
            # Busca: "Art. 5.3.1", "Artículo 5", "ARTICLE 5.3.1"
            patterns = [
                r'(?:Art\.|Artículo|Article)\s+(\d+(?:\.\d+)*)\s*(?:[-–]|:)?\s*([^\n]+)?',
                r'§\s*(\d+(?:\.\d+)*)\s*(?:[-–]|:)?\s*([^\n]+)?'
            ]
            
            all_matches = []
            for pattern in patterns:
                matches = list(re.finditer(pattern, full_text, re.IGNORECASE))
                all_matches.extend(matches)
            
            # Ordenar por posición
            all_matches.sort(key=lambda x: x.start())
            
            if not all_matches:
                print("⚠️  No se encontraron artículos con patrones estándar")
                return []
            
            # Procesar cada artículo
            for i, match in enumerate(all_matches):
                article_num = match.group(1)
                article_title = match.group(2) or ""
                
                # Extraer texto hasta el siguiente artículo
                start = match.end()
                end = all_matches[i+1].start() if i+1 < len(all_matches) else len(full_text)
                article_text = full_text[start:end].strip()
                
                if len(article_text) < 20:  # Mínimo de caracteres
                    continue
                
                # Procesar información del artículo
                chapter = self._extract_chapter(full_text, match.start())
                sanctions = self._extract_sanctions(article_text)
                severity = self._determine_severity(article_text, sanctions)
                keywords = self._extract_keywords(article_text)
                summary = article_text[:200]  # Primeros 200 chars
                
                articles.append({
                    'number': article_num,
                    'title': article_title,
                    'chapter': chapter,
                    'full_text': article_text[:3000],  # Limitar a 3000 chars
                    'summary': summary,
                    'keywords': keywords,
                    'sanctions': sanctions,
                    'severity': severity
                })
        
        except Exception as e:
            print(f"❌ Error extrayendo del PDF: {e}")
        
        return articles
    
    def _extract_chapter(self, full_text: str, position: int) -> str:
        """Extrae el capítulo/sección del artículo"""
        chapter_pattern = r'(?:CAPÍTULO|SECCIÓN|TÍTULO|CHAPTER)\s+([^\n]{1,100})'
        
        chapters = list(re.finditer(chapter_pattern, full_text[:position], re.IGNORECASE))
        
        if chapters:
            return chapters[-1].group(1).strip()
        return "General"
    
    def _extract_sanctions(self, article_text: str) -> list:
        """Extrae sanciones mencionadas"""
        sanctions = []
        
        sanction_keywords = {
            'amonestacion': ['amonestación', 'amonestación escrita', 'apercibimiento', 'amonestacion'],
            'conciliacion': ['conciliación', 'solución amistosa', 'acuerdo', 'conciliacion'],
            'consignacion': ['consignación', 'elevación', 'autoridad superior', 'despido', 'consignacion']
        }
        
        text_lower = article_text.lower()
        for sanction_type, keywords in sanction_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if sanction_type not in sanctions:
                        sanctions.append(sanction_type)
                    break
        
        return sanctions if sanctions else ['amonestacion']
    
    def _determine_severity(self, article_text: str, sanctions: list) -> int:
        """Determina nivel de severidad (1=leve, 2=moderado, 3=grave)"""
        if 'consignacion' in sanctions:
            return 3
        elif 'conciliacion' in sanctions:
            return 2
        
        # Palabras clave
        if any(word in article_text.lower() for word in ['grave', 'despido', 'inmediato']):
            return 3
        elif any(word in article_text.lower() for word in ['moderado', 'suspensión']):
            return 2
        
        return 1
    
    def _extract_keywords(self, text: str) -> list:
        """Extrae palabras clave del texto"""
        # Palabras comunes a ignorar
        stopwords = {
            'el', 'la', 'de', 'que', 'y', 'a', 'en', 'se', 'será', 'es', 'son',
            'del', 'al', 'los', 'las', 'un', 'una', 'unos', 'unas', 'por',
            'con', 'para', 'o', 'si', 'no', 'como', 'más', 'pero', 'está'
        }
        
        # Extraer palabras de 4+ caracteres
        words = re.findall(r'\b\w{4,}\b', text.lower())
        keywords = list(set(word for word in words if word not in stopwords))[:10]
        
        return keywords
    
    def _calculate_file_hash(self, filepath: str) -> str:
        """Calcula hash SHA256 del archivo"""
        import hashlib
        sha256_hash = hashlib.sha256()
        
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()


def main():
    """Script principal"""
    if len(sys.argv) < 2:
        print("\n" + "="*80)
        print("INDEXADOR DE ESTATUTOS - RAG")
        print("="*80)
        print("\nUso:")
        print("  python3 scripts/index_statute.py <ruta_pdf> [version]")
        print("\nEjemplo:")
        print("  python3 scripts/index_statute.py ~/Descargas/Estatutos_2024.pdf v2024.01")
        print("\n" + "="*80 + "\n")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    statute_version = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Crear indexador
    indexer = StatuteIndexer()
    
    # Indexar
    success = indexer.index_pdf(pdf_path, statute_version)
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
