# FitFindr — planning.md
---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
This tool searches through listings.json and returns listings relevant to the input. The listings are sorted by highest score aka most relevant to the description input. 


**Input parameters:**
- `description` (str): Input of what the user is looking for
- `size` (str): User's size
- `max_price` (float): User's budget


**What it returns:**
It returns a list of matching listing dictionaries sorted by relevance. 
 
**What happens if it fails or returns nothing:**
An empty list is returned. 

---

### Tool 2: suggest_outfit

**What it does:**
It asks the LLM to suggest specific outfit combinations from user's wardrobe using the new item and named pieces. And if there's not items in the wardrobe, LLM will be called for general styling ideas. 

**Input parameters:**
- `new_item` (dict): The item that the user's buying
- `wardrobe` (dict): User's current owned clothes. 

**What it returns:**
 A non-empty string with outfit suggestions.
     

**What happens if it fails or returns nothing:**
If the wardrobe is empty, LLM offers general styling advice for the item


### Tool 3: create_fit_card

**What it does:**
Creates a fit card that gives a caption to the outfit. But functionally, it serves as a guard to an empty or white-space outfit string. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str):  The outfit suggestion string from suggest_outfit().
- `new_item` (dict): The listing dict for the thrifted item.

**What it returns:**
A 2–4 sentence string usable as an Instagram/TikTok caption.


**What happens if it fails or returns nothing:**
If outfit is empty or missing, return a descriptive error message

---

## Planning Loop

**How does your agent decide which tool to call next?**

First, it parses the user's query. Then it calls the search_listings(). If there's no results, it returns the session early. If there is, the first indexed item is stored, and the suggest_outfit() is called. The suggest_outfit() will use that item and the wardrobe to come up with the outfit suggestion. Then create_fit_card() is called with the outfit suggestion and returns the fit card. 

---

## State Management

**How does information from one tool get passed to the next?**

Information gets stored in session types.

In search_listings(), results is stored in ["search_esults"] and gets evaluated on whether it is empty or not. If it is empty, session ["error"] is set and returned. Item is selected and stored in ["selected_item"]

In suggest_outfit(), result is stored in session ["outfit_suggestion"]

In create_fit_card(), result is sstored in session ["fit_card"]
---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | Returns session early |
| suggest_outfit | Wardrobe is empty | Calls the LLM with a prompt for general styling ideas.|
| create_fit_card | Outfit input is missing or incomplete | Returns a descriptive error message string|

---

## Architecture

User query
    │
    ▼
Planning Loop ───────────────────────────────────────────┐
    │                                                    │
    ├─► search_listings(description, size, max_price)    │
    │       │ results=[]                                 │
    │       ├──► [ERROR] "No listings found..." → return │
    │       │                                            │
    │       │ results=[item, ...]                        │
    │       ▼                                            │
    │   Session: selected_item = results[0]              │
    │       │                                            │
    ├─► suggest_outfit(selected_item, wardrobe)          │
    │       │                                            |
    |       ├──►   wardrobe = []; Ask Groq for general styling ideas         
    |       |                                            |
    |       │                                            |
    │   Session: outfit_suggestion = "..."               │
    │       │                                            │
    └─► create_fit_card(outfit_suggestion, selected_item)
            │
            ├──►   outfit = ""; return a descriptive error message  
            │                                            │
        Session: fit_card = "..."                        │
            │                                            └─ error path returns here
            ▼
        Return session

---

## AI Tool Plan

**Milestone 3 — Individual tool implementations:**
I'll give Claude my Tools specs, tool.py and architecture to diagram to implement search_listings() (I'll also feed it with the data loader), suggest_outfit() and create_fit_card() individually at a time. I'll test each of them against 3 queries before trusting it. 

**Milestone 4 — Planning loop and state management:**
I'll also give Claude my planning loop and state management specs, architecture and agent.py to implement run_agent and handle_query individually at a time. I'll test it by running python agent.py with 3 queries before proceeding. 

---

## A Complete Interaction (Step by Step)

FitFindr needs to search for what the user wants through search_listings. Then based on the top result, FitFindr suggests an outfit with what the user have currently in their wardrobe. Then it creates a fit card based on the suggestion. If there's no listings, Fitfindr would tell the user that and does not proceed any further. But if there is a listing, then it does the three steps chronologically. 

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**

The agent calls on search_listing to find 3 matching listings sorted by relevance. It then picks the top results. 

**Step 2:**
It uses the top result to suggest an outfit based on the user's current wardrobe through the suggest_outfit function

**Step 3:**
Creates a fit card based on the outfit and the new item recommended

**Final output to user:**
The user sees the fit card at the very end. 