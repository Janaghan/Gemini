"""
Google Search tool using Gemini's built-in grounding capability.

This tool leverages Gemini's native Google Search integration
for real-time information retrieval.
"""

from typing import Dict, Any
from google.genai import types

# Define the native Google Search tool
GOOGLE_SEARCH_TOOL = types.Tool(google_search=types.GoogleSearch())

def define_tool():
    """Returns the native tool definition."""
    return GOOGLE_SEARCH_TOOL

def parse_search_results(response) -> Dict[str, Any]:
    """
    Parse search results from Gemini response.
    
    Args:
        response: Response object from Live API
        
    Returns:
        Dict containing strictured queries and results.
    """
    results = {
        "search_performed": False,
        "queries": [],
        "results": [],
    }
    
    if not response.server_content:
        return results
    
    model_turn = response.server_content.model_turn
    if not model_turn:
        return results
    
    for part in model_turn.parts:
        # Only capture execution results (actual search outputs)
        if part.code_execution_result is not None:
            results["search_performed"] = True
            results["results"].append({
                "outcome": part.code_execution_result.outcome,
                "output": part.code_execution_result.output,
            })
    
    return results

def format_search_summary(search_results: Dict[str, Any]) -> str:
    """Format search results into a readable summary."""
    if not search_results["search_performed"]:
        return ""
    
    summary = "\n[Google Search Grounding]\n"
    
    for i, q in enumerate(search_results["queries"], 1):
        summary += f"  Query: {q['code']}\n"
    
    return summary