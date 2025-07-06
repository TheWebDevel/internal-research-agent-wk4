from langchain.tools import tool
from providers.vectorstore import get_retriever
from providers.bedrock import get_llm
from providers.websearch import web_search
from langchain.chains import RetrievalQA
from agent.mcp_insurance_client import get_insurance_client, run_async

@tool
def rag_tool(query: str) -> dict:
    """Search internal HR policy documents using RAG (Retrieval-Augmented Generation) to answer questions about company policies."""
    retriever = get_retriever()
    llm = get_llm()
    try:
        docs_with_scores = retriever.get_relevant_documents(query)
        filtered_docs = []
        for doc in docs_with_scores:
            score = None
            if hasattr(doc, 'metadata') and 'score' in doc.metadata:
                score = doc.metadata['score']
            if score is not None:
                if score >= 0.7:
                    filtered_docs.append(doc)
            else:
                filtered_docs.append(doc)
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        result = qa_chain({"query": query, "input_documents": filtered_docs})
    except Exception:
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
        result = qa_chain({"query": query})
    answer = result.get("result") or result.get("output") or ""
    sources = result.get("source_documents", [])
    citations = []
    for doc in sources:
        meta = getattr(doc, 'metadata', {})
        name = meta.get('source', 'Unknown Source')
        citations.append(name)
    citations = list(dict.fromkeys(citations))
    return {"answer": answer, "tool": "RAG", "citations": citations}

@tool
def websearch_tool(query: str) -> dict:
    """Search the web for public/external information using DuckDuckGo to answer questions about industry trends, best practices, or general information."""
    results = web_search(query)
    answer = results.get("answer", "")
    citations = results.get("citations", [])
    return {"answer": answer, "tool": "WebSearch", "citations": citations}

@tool
def insurance_query_tool(question: str, document_id: str = "1Sb3KD3YJldA9ocCE4KK0CdFBEgh3w0JaGdabi83xY3M") -> dict:
    """Query insurance policy documents from Google Drive to answer specific insurance-related questions for Presidio employees."""
    try:
        client = get_insurance_client()
        content = run_async(client.get_document_content(document_id))

        if not content or (isinstance(content, str) and "error" in content.lower()):
            return {"answer": f"Could not retrieve document content: {content}", "tool": "InsuranceQuery", "citations": []}

        llm = get_llm()
        prompt = f"""You are an insurance policy expert. Here is the content of the insurance policy document:

{content}

Question: {question}

Please answer the question based only on the information in the document above. If the information is not available, state that clearly."""

        answer = llm.invoke(prompt)

        return {
            "answer": answer,
            "tool": "InsuranceQuery",
            "citations": [],  # Remove document ID from citations
            "debug": {
                "document_id": document_id,
                "content_length": len(content) if isinstance(content, str) else 0
            }
        }

    except Exception as e:
        return {"answer": f"Error querying insurance documents: {str(e)}", "tool": "InsuranceQuery", "citations": []}

@tool
def insurance_document_tool(document_id: str) -> dict:
    """Retrieve the full content of a specific insurance policy document from Google Drive by document ID."""
    try:
        client = get_insurance_client()
        content = run_async(client.get_document_content(document_id))

        # Truncate content if too long
        if content and len(content) > 2000:
            content = content[:2000] + "... (truncated)"

        return {"answer": content or "No content retrieved", "tool": "InsuranceDocument", "citations": [f"Document ID: {document_id}"]}
    except Exception as e:
        return {"answer": f"Error retrieving document: {str(e)}", "tool": "InsuranceDocument", "citations": []}

def get_tools():
    return [rag_tool, websearch_tool, insurance_query_tool, insurance_document_tool]