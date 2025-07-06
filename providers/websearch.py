import requests
import time
import json
import os
from typing import Dict, Any, List
from urllib.parse import quote_plus, urlparse
import random
import re

# Simple in-memory cache for rate limiting
_search_cache = {}
_last_search_time = 0
_rate_limit_delay = 1  # seconds between searches

def web_search(query: str) -> Dict[str, Any]:
    """
    Real web search using SerpAPI for comprehensive results.
    """
    global _last_search_time

    # Check cache first
    if query in _search_cache:
        return _search_cache[query]

    # Rate limiting
    current_time = time.time()
    if current_time - _last_search_time < _rate_limit_delay:
        time.sleep(_rate_limit_delay - (current_time - _last_search_time))
    _last_search_time = time.time()

    try:
        # Use SerpAPI exclusively
        result = _serpapi_search(query)
        if result and result.get("answer"):
            _search_cache[query] = result
            return result

        # If SerpAPI fails, provide helpful guidance
        return _get_helpful_fallback(query)

    except Exception as e:
        print(f"Web search failed: {e}")
        return _get_helpful_fallback(query)

def _serpapi_search(query: str) -> Dict[str, Any] | None:
    """Use SerpAPI for web search"""
    try:
        # Get API key from environment
        api_key = os.getenv("SERPAPI_KEY")
        if not api_key:
            print("SERPAPI_KEY not found in environment variables")
            return None

        url = "https://serpapi.com/search"
        params = {
            "q": query,
            "api_key": api_key,
            "engine": "google",
            "num": 10,  # Get more results for better coverage
            "gl": "us",  # Country for search results
            "hl": "en"   # Language
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # Extract organic search results
        organic_results = data.get("organic_results", [])
        if not organic_results:
            return None

        # Combine multiple results for comprehensive answer
        combined_text = []
        citations = []

        for result in organic_results[:5]:  # Use top 5 results
            if result.get("snippet"):
                combined_text.append(result["snippet"])
            if result.get("link"):
                citations.append(result["link"])

        if combined_text:
            # Join snippets with proper spacing
            answer = " ".join(combined_text)

            # Clean up the answer (remove excessive whitespace, etc.)
            answer = re.sub(r'\s+', ' ', answer).strip()

            return {
                "answer": answer,
                "citations": citations if citations else ["SerpAPI"]
            }

        return None

    except requests.exceptions.RequestException as e:
        print(f"SerpAPI request failed: {e}")
        return None
    except Exception as e:
        print(f"SerpAPI search failed: {e}")
        return None

def _get_helpful_fallback(query: str) -> Dict[str, Any]:
    """Provide helpful fallback responses when search fails"""

    # Check if it's a government/policy related query
    if any(word in query.lower() for word in ["government", "policy", "tn govt", "tamil nadu"]):
        return {
            "answer": f"I couldn't find specific recent information about '{query}' through web search. For the most up-to-date information about government policies, I recommend:\n\n• Checking the official Tamil Nadu government website (www.tn.gov.in)\n• Visiting the Tamil Nadu IT department portal\n• Contacting local government offices directly\n• Checking recent news sources like The Hindu, Times of India, or Economic Times\n\nWould you like me to help you formulate a more specific search query, or do you have additional details about what you're looking for?",
            "citations": ["Annet - HR Research Assistant"]
        }

    # Check if it's a technology/AI related query
    if any(word in query.lower() for word in ["ai", "artificial intelligence", "hardware", "technology", "tech", "latest", "news"]):
        return {
            "answer": f"I couldn't find specific recent information about '{query}' through web search. For the most up-to-date information about technology and AI developments, I recommend:\n\n• Checking tech news sites like TechCrunch, The Verge, or Ars Technica\n• Visiting official company websites (NVIDIA, Intel, AMD, etc.)\n• Following tech industry blogs and newsletters\n• Checking recent conference announcements (CES, GTC, etc.)\n• Consulting specialized AI/ML publications\n\nWould you like me to help you formulate a more specific search query, or do you have additional details about what you're looking for?",
            "citations": ["Annet - HR Research Assistant"]
        }

    # General fallback with more specific guidance
    return {
        "answer": f"I couldn't find specific information about '{query}' through web search. To get better results, try:\n\n• Using more specific keywords\n• Adding date ranges (e.g., '2024', 'recent')\n• Checking official websites directly\n• Using news aggregators like Google News\n• Consulting specialized industry publications\n\nWould you like me to help you rephrase your search query?",
        "citations": ["Annet - HR Research Assistant"]
    }

def clear_search_cache():
    """Clear the search cache"""
    global _search_cache
    _search_cache = {}
    print("Web search cache cleared!")

def get_search_status():
    """Get information about available search APIs"""
    api_key = os.getenv("SERPAPI_KEY")
    status = "configured" if api_key else "not configured"

    return {
        "search_engine": "SerpAPI (Google Search)",
        "api_key_status": status,
        "setup_instructions": [
            "Add SERPAPI_KEY to your .env file",
            "Get your API key from https://serpapi.com/",
            "Free tier includes 100 searches per month"
        ]
    }