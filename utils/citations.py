def format_citations(citations):
    if not citations:
        return ""
    return "\n".join(f"- {c}" for c in citations)