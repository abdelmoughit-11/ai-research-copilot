from groq import Groq
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def evaluate_rag_response(question: str, answer: str, context: str) -> dict:
    """
    Évalue la qualité d'une réponse RAG selon 4 métriques :
    
    1. Faithfulness   : la réponse est-elle fidèle aux sources ?
    2. Relevancy      : la réponse répond-elle à la question ?
    3. Context recall : les bons passages ont-ils été trouvés ?
    4. Answer score   : note globale de la réponse
    
    Returns:
        dict avec scores entre 0 et 1 + explication
    """

    eval_prompt = f"""You are an expert RAG evaluation system.
Evaluate the following RAG response and return ONLY a valid JSON object.

QUESTION: {question}

CONTEXT USED:
{context[:2000]}

ANSWER GIVEN:
{answer}

Evaluate on these 4 metrics (score between 0.0 and 1.0):

1. faithfulness: Is the answer based only on the provided context? 
   (1.0 = fully grounded, 0.0 = completely hallucinated)

2. relevancy: Does the answer actually address the question?
   (1.0 = perfectly relevant, 0.0 = completely off-topic)

3. context_recall: Did the context contain enough information to answer well?
   (1.0 = context was perfect, 0.0 = context was useless)

4. answer_score: Overall quality of the answer
   (1.0 = excellent, 0.0 = terrible)

Return ONLY this JSON format, nothing else:
{{
    "faithfulness": 0.0,
    "relevancy": 0.0,
    "context_recall": 0.0,
    "answer_score": 0.0,
    "faithfulness_reason": "explanation",
    "relevancy_reason": "explanation",
    "context_recall_reason": "explanation",
    "overall_feedback": "short overall feedback"
}}"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": eval_prompt}],
            temperature=0.0  # 0 = déterministe pour l'évaluation
        )

        raw = response.choices[0].message.content.strip()

        # Nettoyer la réponse si elle contient du texte en plus
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()

        scores = json.loads(raw)

        # Calculer la moyenne globale
        scores["average"] = round(
            (scores["faithfulness"] +
             scores["relevancy"] +
             scores["context_recall"] +
             scores["answer_score"]) / 4, 2
        )

        return scores

    except Exception as e:
        # Retourner des scores par défaut si l'évaluation échoue
        return {
            "faithfulness": 0.5,
            "relevancy": 0.5,
            "context_recall": 0.5,
            "answer_score": 0.5,
            "average": 0.5,
            "faithfulness_reason": "Evaluation failed",
            "relevancy_reason": "Evaluation failed",
            "context_recall_reason": "Evaluation failed",
            "overall_feedback": f"Evaluation error: {str(e)}"
        }


def get_score_color(score: float) -> str:
    """Retourne une couleur selon le score"""
    if score >= 0.8:
        return "🟢"  # Excellent
    elif score >= 0.6:
        return "🟡"  # Correct
    elif score >= 0.4:
        return "🟠"  # Faible
    else:
        return "🔴"  # Mauvais


def get_score_label(score: float) -> str:
    """Retourne un label selon le score"""
    if score >= 0.8:
        return "Excellent"
    elif score >= 0.6:
        return "Good"
    elif score >= 0.4:
        return "Fair"
    else:
        return "Poor"