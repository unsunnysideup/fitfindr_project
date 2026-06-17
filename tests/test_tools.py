# tests/test_tools.py
from tools import search_listings

def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []   # empty list, no exception

def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)
    assert all(item["price"] <= 10 for item in results)

from tools import suggest_outfit
suggest_outfit({"title": "Vintage Levi's 501 Jeans", "category": "bottoms", "colors": ["blue"], "style_tags": ["vintage", "streetwear"], "condition": "good"}, {"items": []})

suggest_outfit({"title": "Graphic Band Tee", "category": "tops", "colors": ["black"], "style_tags": ["vintage", "grunge"], "condition": "fair"}, {"items": [{"id": "1", "name": "Vintage Levi's 501 Jeans", "category": "bottoms", "colors": ["blue"], "style_tags": ["vintage", "classic"], "notes": "slightly cropped on me"}, {"id": "2", "name": "Black Chelsea Boots", "category": "shoes", "colors": ["black"], "style_tags": ["classic", "edgy"], "notes": None}]})

suggest_outfit({"title": "Mystery Jacket"}, {"items": []})

    
from tools import create_fit_card

item = {"title": "Vintage Levi's 501 Jeans", "price": 45.0, "platform": "depop", "colors": ["blue"], "style_tags": ["vintage", "streetwear"]}
outfit = "Pair with a black graphic tee and white sneakers for a classic streetwear look."

# testing for similarness
create_fit_card(outfit, item)
create_fit_card(outfit, item)
create_fit_card(outfit, item)

# For guard purposes
create_fit_card("", item)
create_fit_card("   ", item)