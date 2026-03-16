import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from research_agent import research_agent, pdf_agent
from evaluation.evaluation import evaluate_rag_response, get_score_color, get_score_label

# ── Configuration ────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Research Copilot",
    page_icon="🔬",
    layout="wide"
)

st.markdown("""
<style>
    .answer-box {
        background-color: #0f172a;
        border-radius: 10px;
        padding: 20px;
        border: 1px solid #1e293b;
        line-height: 1.8;
    }
    .source-card {
        background-color: #1e1e2e;
        border-left: 4px solid #7c3aed;
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 10px;
    }
    .source-title { font-weight: 600; font-size: 0.95rem; color: #a78bfa; }
    .source-summary { font-size: 0.82rem; color: #94a3b8; margin-top: 4px; }
    .eval-card {
        background-color: #0f172a;
        border-radius: 10px;
        padding: 16px;
        border: 1px solid #1e293b;
        margin-bottom: 8px;
    }
    .eval-metric {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #1e293b;
    }
    .tip-box {
        background-color: #1c1c2e;
        border-left: 4px solid #22c55e;
        padding: 10px 16px;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #86efac;
        margin-bottom: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []

# ── Layout ───────────────────────────────────────────────────────
col_main, col_side = st.columns([2, 1])

# ════════════════════════════════════════
# FONCTION AFFICHAGE ÉVALUATION
# ════════════════════════════════════════
def show_evaluation(scores: dict):
    """Affiche les scores d'évaluation de manière visuelle"""

    st.markdown("### 📊 RAG Evaluation")

    # Score moyen en grand
    avg = scores.get("average", 0)
    color = get_score_color(avg)
    label = get_score_label(avg)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric(
            "Overall Score",
            f"{avg:.0%}",
            delta=label
        )
    with col2:
        faith = scores.get("faithfulness", 0)
        st.metric(
            f"{get_score_color(faith)} Faithfulness",
            f"{faith:.0%}",
            help="La réponse est-elle basée sur les sources ?"
        )
    with col3:
        rel = scores.get("relevancy", 0)
        st.metric(
            f"{get_score_color(rel)} Relevancy",
            f"{rel:.0%}",
            help="La réponse répond-elle à la question ?"
        )
    with col4:
        ctx = scores.get("context_recall", 0)
        st.metric(
            f"{get_score_color(ctx)} Context",
            f"{ctx:.0%}",
            help="Le contexte était-il suffisant ?"
        )
    with col5:
        ans = scores.get("answer_score", 0)
        st.metric(
            f"{get_score_color(ans)} Answer",
            f"{ans:.0%}",
            help="Qualité globale de la réponse"
        )

    # Barres de progression
    st.markdown("---")
    metrics = {
        "Faithfulness": scores.get("faithfulness", 0),
        "Relevancy": scores.get("relevancy", 0),
        "Context recall": scores.get("context_recall", 0),
        "Answer score": scores.get("answer_score", 0),
    }
    for name, score in metrics.items():
        st.progress(score, text=f"{name}: {score:.0%}")

    # Feedback global
    if scores.get("overall_feedback"):
        st.info(f"💬 {scores['overall_feedback']}")

    # Détails des raisons
    with st.expander("🔍 Voir les détails de l'évaluation"):
        if scores.get("faithfulness_reason"):
            st.markdown(f"**Faithfulness :** {scores['faithfulness_reason']}")
        if scores.get("relevancy_reason"):
            st.markdown(f"**Relevancy :** {scores['relevancy_reason']}")
        if scores.get("context_recall_reason"):
            st.markdown(f"**Context recall :** {scores['context_recall_reason']}")


# ════════════════════════════════════════
# COLONNE PRINCIPALE
# ════════════════════════════════════════
with col_main:
    st.markdown("# 🔬 AI Research Copilot")
    st.caption("Powered by Groq (Llama 3.3) + ArXiv + FAISS + RAG Evaluation")

    mode = st.radio(
        "Choose mode:",
        ["🌐 ArXiv Search", "📄 PDF Analysis"],
        horizontal=True
    )

    st.markdown("")

    # ════════════════════════
    # MODE ARXIV
    # ════════════════════════
    if mode == "🌐 ArXiv Search":

        st.markdown("""
        <div class="tip-box">
        💡 <strong>Tip :</strong> Utilise des termes techniques précis en anglais.<br>
        Ex: <em>"transformer attention mechanism NLP"</em>
        </div>
        """, unsafe_allow_html=True)

        query = st.text_input(
            "Ask a research question:",
            placeholder="e.g. transformer attention mechanism deep learning"
        )

        # Option évaluation
        run_eval = st.checkbox(
            "📊 Évaluer la qualité de la réponse",
            value=True,
            help="Analyse automatiquement la qualité de la réponse RAG"
        )

        if st.button("🔍 Search & Analyze", type="primary", use_container_width=True):
            if query.strip():
                with st.status("Searching ArXiv...", expanded=True) as status:
                    st.write("🔍 Searching ArXiv papers...")
                    st.write("📚 Creating vector database...")
                    st.write("🤖 Generating answer with Groq...")
                    if run_eval:
                        st.write("📊 Evaluating response quality...")

                    try:
                        answer, sources, num_papers, context = research_agent(query)

                        # Évaluation
                        scores = None
                        if run_eval:
                            scores = evaluate_rag_response(query, answer, context)

                        status.update(
                            label=f"Done! Analyzed {num_papers} papers ✅",
                            state="complete"
                        )

                        # Sauvegarder
                        st.session_state.history.insert(0, {
                            "mode": "ArXiv",
                            "query": query,
                            "answer": answer,
                            "sources": sources,
                            "num": num_papers,
                            "scores": scores
                        })

                        # Afficher réponse
                        st.markdown("### 📝 Answer")
                        st.markdown(
                            f'<div class="answer-box">{answer}</div>',
                            unsafe_allow_html=True
                        )

                        # Afficher évaluation
                        if scores:
                            st.markdown("")
                            show_evaluation(scores)

                        # Afficher sources
                        if sources:
                            st.markdown(f"### 📚 Sources ({len(sources)} papers)")
                            for i, s in enumerate(sources):
                                st.markdown(f"""
                                <div class="source-card">
                                    <div class="source-title">📄 {i+1}. {s['title']}</div>
                                    <div class="source-summary">{s['summary']}...</div>
                                </div>
                                """, unsafe_allow_html=True)

                    except Exception as e:
                        status.update(label="Error ❌", state="error")
                        st.error(f"Erreur : {str(e)}")
            else:
                st.warning("Please enter a question.")

    # ════════════════════════
    # MODE PDF
    # ════════════════════════
    elif mode == "📄 PDF Analysis":

        uploaded_pdf = st.file_uploader(
            "Upload your PDF",
            type=["pdf"]
        )

        if uploaded_pdf:
            st.success(f"PDF chargé : {uploaded_pdf.name} ({uploaded_pdf.size // 1024} KB)")

        pdf_query = st.text_input(
            "Ask a question about your PDF:",
            placeholder="e.g. What is the main contribution of this paper?"
        )

        run_eval_pdf = st.checkbox(
            "📊 Évaluer la qualité de la réponse",
            value=True,
            key="eval_pdf"
        )

        if st.button("📄 Analyze PDF", type="primary", use_container_width=True):
            if not uploaded_pdf:
                st.warning("⚠️ Please upload a PDF first.")
            elif not pdf_query.strip():
                st.warning("⚠️ Please enter a question.")
            else:
                with st.status("Analyzing PDF...", expanded=True) as status:
                    st.write("📖 Reading PDF pages...")
                    st.write("📚 Creating vector database...")
                    st.write("🤖 Generating answer with Groq...")
                    if run_eval_pdf:
                        st.write("📊 Evaluating response quality...")

                    try:
                        answer, sources, num_pages, context = pdf_agent(
                            uploaded_pdf, pdf_query
                        )

                        scores = None
                        if run_eval_pdf:
                            scores = evaluate_rag_response(pdf_query, answer, context)

                        status.update(
                            label=f"Done! Analyzed {num_pages} pages ✅",
                            state="complete"
                        )

                        st.session_state.history.insert(0, {
                            "mode": "PDF",
                            "query": pdf_query,
                            "answer": answer,
                            "sources": sources,
                            "num": num_pages,
                            "scores": scores
                        })

                        st.markdown("### 📝 Answer")
                        st.markdown(
                            f'<div class="answer-box">{answer}</div>',
                            unsafe_allow_html=True
                        )

                        if scores:
                            st.markdown("")
                            show_evaluation(scores)

                        if sources:
                            st.markdown(f"### 📄 Sources ({len(sources)} extraits)")
                            for i, s in enumerate(sources):
                                st.markdown(f"""
                                <div class="source-card">
                                    <div class="source-title">📌 Extrait {i+1} — {s['title']}</div>
                                    <div class="source-summary">{s['summary']}...</div>
                                </div>
                                """, unsafe_allow_html=True)

                    except Exception as e:
                        status.update(label="Error ❌", state="error")
                        st.error(f"Erreur : {str(e)}")

# ════════════════════════════════════════
# COLONNE LATÉRALE
# ════════════════════════════════════════
with col_side:

    st.markdown("### 🕐 Historique")

    if not st.session_state.history:
        st.caption("Aucune recherche pour le moment.")
    else:
        for i, item in enumerate(st.session_state.history[:5]):
            icon = "🌐" if item["mode"] == "ArXiv" else "📄"
            with st.expander(f"{icon} {item['query'][:35]}...", expanded=(i == 0)):
                st.markdown(f"**Mode :** {item['mode']} | **Items :** {item['num']}")

                # Afficher le score moyen dans l'historique
                if item.get("scores"):
                    avg = item["scores"].get("average", 0)
                    color = "🟢" if avg >= 0.8 else "🟡" if avg >= 0.6 else "🔴"
                    st.markdown(f"**Score RAG :** {color} {avg:.0%}")

                st.markdown(item['answer'][:200] + "...")

        if st.button("🗑️ Effacer", use_container_width=True):
            st.session_state.history = []
            st.rerun()

    st.markdown("---")

    st.markdown("### 💡 Exemples ArXiv")
    examples = [
        "transformer attention mechanism NLP",
        "denoising diffusion probabilistic models",
        "reinforcement learning human feedback",
        "large language models fine tuning",
        "graph neural network",
    ]
    for ex in examples:
        st.code(ex, language=None)

    st.markdown("### 📊 Guide scores")
    st.markdown("""
    - 🟢 **80-100%** — Excellent
    - 🟡 **60-79%** — Good
    - 🟠 **40-59%** — Fair
    - 🔴 **0-39%** — Poor
    """)