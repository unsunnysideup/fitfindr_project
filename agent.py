"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

import os
import json
from dotenv import load_dotenv
from groq import Groq
from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

load_dotenv()


# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    session = _new_session(query, wardrobe)

    # Step 2: Parse query with LLM
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    parse_prompt = f"""Extract search parameters from this clothing search query.
Return ONLY valid JSON with these exact keys: "description", "size", "max_price".
- description: keywords describing the item (string)
- size: clothing size if mentioned, otherwise null
- max_price: maximum price as a number if mentioned, otherwise null

Query: "{query}"

Example output:
{{"description": "vintage graphic tee", "size": "M", "max_price": 30.0}}"""

    try:
        parse_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": parse_prompt}],
            temperature=0,
        )
        raw = parse_response.choices[0].message.content or ""
        clean = raw.strip().strip("```json").strip("```").strip()
        parsed = json.loads(clean)
    except Exception as e:
        session["error"] = f"Could not parse query: {e}"
        return session

    session["parsed"] = parsed

    # Step 3: Search listings
    results = search_listings(
        description=parsed.get("description", query),
        size=parsed.get("size"),
        max_price=parsed.get("max_price"),
    )
    session["search_results"] = results

    if not results:
        session["error"] = "No listings found matching your search. Try different keywords, a higher budget, or a different size."
        return session

    # Step 4: Select top result
    session["selected_item"] = results[0]

    # Step 5: Suggest outfit
    session["outfit_suggestion"] = suggest_outfit(results[0], wardrobe)

    # Step 6: Create fit card
    session["fit_card"] = create_fit_card(session["outfit_suggestion"], results[0])

    # Step 7: Return session
    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

    print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
