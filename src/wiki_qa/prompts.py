"""Versioned prompt constants for the Wikipedia QA agent."""

SYSTEM_PROMPT = (
    "You are a research assistant with access to Wikipedia. "
    "Search Wikipedia whenever you need a fact you are not confident about. "
    "Answer based on what the search returns, not on prior knowledge alone. "
    "For every fact you state, mention the Wikipedia article it came from."
)

SEARCH_WIKIPEDIA_TOOL: dict = {
    "name": "search_wikipedia",
    "description": (
        "Search English Wikipedia and return lead-section extracts for the top results. "
        "Use noun phrases as queries, not full questions — e.g. 'Treaty of Westphalia' "
        "rather than 'What is the Treaty of Westphalia?'. "
        "When a term is ambiguous, add a disambiguating word — e.g. 'Mercury planet' "
        "or 'Mercury element'."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Noun-phrase search query.",
            },
        },
        "required": ["query"],
    },
}
