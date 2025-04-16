from langchain_core.tools import tool

@tool
def search_web(query: str) -> str:
    """Search the web for information.
    
    Args:
        query: The search query.
        
    Returns:
        Information found from the search.
    """
    # This is a placeholder implementation
    # In production, you would integrate with a real search API
    return f"Found information about: {query}" 