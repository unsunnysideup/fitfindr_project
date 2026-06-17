"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os
import re

from dotenv import load_dotenv


from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    STOPWORDS = {"nothing", "a", "an", "the", "in", "is", "it", "with", "and", "or", "but", "no", "not", "some", "few", "very", "great", "good", "nice"}

    try:
        listings = load_listings()
    except Exception:
        return []

    keywords = set(re.sub(r"[^\w\s]", "", description.lower()).split()) - STOPWORDS

    if not keywords:
        return []

    candidates = []
    for listing in listings:
        if max_price is not None:
            try:
                if float(listing.get("price", 0)) > max_price:
                    continue
            except (TypeError, ValueError):
                continue

        if size is not None:
            listing_size = (listing.get("size") or "").lower()
            if size.lower() not in listing_size:
                continue

        candidates.append(listing)

    def score(listing: dict) -> int:
        searchable = " ".join([
            listing.get("title", ""),
            listing.get("description", ""),
            listing.get("category", ""),
            listing.get("brand") or "",
            " ".join(listing.get("style_tags", [])),
            " ".join(listing.get("colors", [])),
        ]).lower()
        return sum(1 for kw in keywords if re.search(rf"\b{re.escape(kw)}\b", searchable))

    scored = [(listing, score(listing)) for listing in candidates]
    scored = [(l, s) for l, s in scored if s > 0]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [l for l, _ in scored]

# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    items = wardrobe.get("items", [])

    if not items:
        prompt = f"""A user is considering buying this secondhand item:

Item: {new_item.get('title')}
Category: {new_item.get('category')}
Colors: {', '.join(new_item.get('colors', []))}
Style tags: {', '.join(new_item.get('style_tags', []))}
Condition: {new_item.get('condition')}

They don't have a wardrobe on file. Give them 1-2 general outfit ideas for this piece — what kinds of items pair well with it, what vibe it suits, and how they could style it."""

    else:
        wardrobe_lines = "\n".join(
            f"- {item.get('name')} ({item.get('category')}, {', '.join(item.get('colors', []))}, {', '.join(item.get('style_tags', []))})"
            + (f" — {item.get('notes')}" if item.get('notes') else "")
            for item in items
        )

        prompt = f"""A user is considering buying this secondhand item:

Item: {new_item.get('title')}
Category: {new_item.get('category')}
Colors: {', '.join(new_item.get('colors', []))}
Style tags: {', '.join(new_item.get('style_tags', []))}
Condition: {new_item.get('condition')}

Their current wardrobe:
{wardrobe_lines}

Suggest 1-2 specific outfit combinations using the new item and named pieces from their wardrobe. Be concrete — reference items by name."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or "No suggestion returned."
    except Exception as e:
        return f"Could not generate outfit suggestion: {e}"


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    if not outfit or not outfit.strip():
        return "Could not generate fit card: outfit suggestion was empty or missing."

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = f"""You are writing an Instagram/TikTok OOTD caption for a thrifted outfit.

Thrifted item: {new_item.get('title')}
Price: ${new_item.get('price')}
Platform: {new_item.get('platform')}
Colors: {', '.join(new_item.get('colors', []))}
Style tags: {', '.join(new_item.get('style_tags', []))}

Outfit idea: {outfit}

Write a 2-4 sentence caption that:
- Feels casual and authentic, like a real person posting their OOTD
- Mentions the item name, price, and platform naturally, once each
- Captures the specific vibe of the outfit
- Does NOT sound like a product description or ad

Just write the caption, nothing else."""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=1.2,
        )
        return response.choices[0].message.content or "No caption returned."
    except Exception as e:
        return f"Could not generate fit card: {e}"
