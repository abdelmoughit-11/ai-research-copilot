from dotenv import load_dotenv
from tools.arxiv_search import search_papers
from rag.vector_store import create_vector_db
from rag.rag_pipeline import answer_question

load_dotenv()

def research_agent(query: str):
    print(f"Searching papers for: {query}")
    papers = search_papers(query, max_results=8)

    if not papers:
        return "No relevant papers found.", [], 0, ""

    print(f"Found {len(papers)} papers. Creating vector DB...")
    db = create_vector_db(papers)

    print("Generating answer with Groq...")
    answer, sources, context = answer_question(db, query)

    return answer, sources, len(papers), context


def pdf_agent(uploaded_file, query: str):
    from tools.pdf_reader import extract_text_from_pdf, split_into_chunks

    print("Reading PDF...")
    pages = extract_text_from_pdf(uploaded_file)

    if not pages:
        return "Could not extract text from PDF.", [], 0, ""

    chunks = split_into_chunks(pages, chunk_size=800)
    db = create_vector_db(chunks)
    answer, sources, context = answer_question(db, query)

    return answer, sources, len(pages), context