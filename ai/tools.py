from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults

# Web search using Duckduckgo
@tool
def web_search(query: str):
    """
    Searches the internet for a question/ query
    Args:
        query: the question/ query to be searched
    """
    search = DuckDuckGoSearchResults()
    return search.run(query)

llm_tools = [web_search]