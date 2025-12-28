"""
Google Search tool using Gemini's built-in grounding capability.

This tool leverages Gemini's native Google Search integration
for real-time information retrieval.
"""

from google.genai import types

# Define the native Google Search tool
# This tells the Gemini API to use its built-in search capability
GOOGLE_SEARCH_TOOL = types.Tool(google_search=types.GoogleSearch())

def define_tool():
    """Returns the native tool definition."""
    return GOOGLE_SEARCH_TOOL

