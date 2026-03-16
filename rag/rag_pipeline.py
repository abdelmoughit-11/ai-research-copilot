from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def answer_question(db, query: str):
    """
    Retourne : (answer, sources, context)
    - answer  : réponse générée
    - sources : extraits utilisés
    - context : texte brut du contexte (pour l'évaluation)
    """

    docs = db.similarity_search(query, k=3)
    context = "\n\n".join([doc.page_content for doc in docs])

    prompt = f"""You are a helpful assistant that answers questions based on documents.

RULES:
- Answer based on the context below
- Be clear, precise and direct
- If context is truly empty, say "Could not find relevant information"

Context:
{context}

Question: {query}

Answer:"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )

    answer = response.choices[0].message.content

    # Sources
    sources = []
    for doc in docs:
        lines = doc.page_content.split("\n")
        title = lines[0][:80] if lines else "Extract"
        summary = " ".join(lines[1:3])[:200] if len(lines) > 1 else lines[0][:200]
        sources.append({"title": title, "summary": summary})

    return answer, sources, context  # ← retourne aussi le contexte