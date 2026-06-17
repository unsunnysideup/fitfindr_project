# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

**macOS / Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows:**
```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Tool Inventory

Your README submission must document each tool's name, inputs, and return value. **These must exactly match your actual function signatures in `tools.py`.** Your documented interfaces will be checked against your actual function signatures in `tools.py` — if the parameter count or types contradict what's in the code, you may not receive full credit for that tool.

---

## Interaction Walkthrough

<!-- Walk through a complete interaction step by step: natural language query → each tool call (and why) → final fit card.
     Walk through this carefully — it's how graders follow your agent's reasoning without a live demo.
     Use a specific example — do not leave this as a template. -->

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1 — Tool called:**
- Tool: search_listing
- Input: Query; Groq parses to extract the following parameters: description, size, and max_price aka budget
- Why this tool: It allows the agent to find the clothing item that most aligns with what the user wants by sorting the listings to highest relevance
- Output: The most relevant clothing piece corresponding to all the parameters

**Step 2 — Tool called:**
- Tool: suggest_outfit()
- Input: The most relevant clothing piece from search_listing() and user's wardrobe
- Why this tool: It allows the agent to call upon Groq to come up with an outfit with the corresponding relevant clothing piece as well as user's wardrobe. If user doesn't have their wardrobe inputted, then Groq comes up with basic styling ideas. 
- Output: An outfit aka one method of styling with the clothing piece. 

**Step 3 — Tool called:**
- Tool: create_fit_card()
- Input: The outfit from suggest_outfit() and the dictionary corresponding to the most relevant clothing piece. 
- Why this tool: Agent creates an insta-worthy caption for the user. But functionally, it serves as a guard to an empty or white-space outfit string.
- Output: A 2-4 sentence caption

**Final output to user:**
The user gets the item's name, an outfit idea, and an insta/tiktok worthy caption. 
---

## Error Handling and Fail Points

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Returns session early |
| suggest_outfit | Wardrobe is empty | Calls the LLM with a prompt for general styling ideas.|
| create_fit_card | Outfit input is missing or incomplete | Returns a descriptive error message string|

---

## Spec Reflection

<!-- Answer both questions with at least 2–3 sentences each. -->

**One way planning.md helped during implementation:** 
Planning helps me understand the problem and know how to implement it and consider edge cases. It allows me to understand what the input and outcome
is and how they should be implemented.  

**One divergence from your spec, and why:**
Instead of having to pick the most relevant piece from the top 3 in search_listings(), I went with picking the most relevant piece from the sorted listings with most relevancy. This is because I don't really see the need to return the top 3 since the user doesn't really get to choose. 

---

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
