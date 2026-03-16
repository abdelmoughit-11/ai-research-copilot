from pypdf import PdfReader

def extract_text_from_pdf(uploaded_file) -> list[str]:
    """
    Lit un PDF uploadé via Streamlit et retourne
    une liste de chunks de texte (1 chunk par page).
    
    Args:
        uploaded_file : fichier uploadé par st.file_uploader
    
    Returns:
        liste de strings, chaque string = texte d'une page
    """
    reader = PdfReader(uploaded_file)
    
    chunks = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        
        if text and text.strip():  # ignorer les pages vides
            # Ajouter le numéro de page pour les sources
            chunk = f"[Page {i+1}]\n{text.strip()}"
            chunks.append(chunk)
    
    return chunks


def split_into_chunks(pages: list[str], chunk_size: int = 1000) -> list[str]:
    """
    Découpe les pages en morceaux plus petits pour
    de meilleurs embeddings.
    
    Pourquoi ? Une page entière = trop long pour un embedding précis.
    Des petits chunks = recherche sémantique plus précise.
    """
    chunks = []
    
    for page_text in pages:
        # Si la page est courte, la garder entière
        if len(page_text) <= chunk_size:
            chunks.append(page_text)
        else:
            # Découper en morceaux avec overlap
            words = page_text.split()
            current_chunk = []
            current_size = 0
            
            for word in words:
                current_chunk.append(word)
                current_size += len(word) + 1
                
                if current_size >= chunk_size:
                    chunks.append(" ".join(current_chunk))
                    # Overlap : garder les 50 derniers mots
                    current_chunk = current_chunk[-50:]
                    current_size = sum(len(w) + 1 for w in current_chunk)
            
            if current_chunk:
                chunks.append(" ".join(current_chunk))
    
    return chunks