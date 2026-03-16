import arxiv

def search_papers(query: str, max_results: int = 5) -> list[str]:
    """
    Cherche des articles sur ArXiv.
    
    Exemple : search_papers("diffusion models")
    → retourne 5 résumés de papers pertinents
    """
    search = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.Relevance  # les plus pertinents d'abord
    )

    results = []
    for paper in search.results():
        # titre + résumé = assez d'info pour le LLM
        text = f"Title: {paper.title}\nSummary: {paper.summary}"
        results.append(text)

    return results

if __name__ == "__main__":
    papers = search_papers("diffusion models")
    for i, paper in enumerate(papers):
        print(f"\n--- Paper {i+1} ---")
        print(paper[:300])