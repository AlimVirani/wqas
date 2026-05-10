"""System prompt and tool-definition constants."""

SYSTEM_PROMPT = (
    "You are a research assistant with access to Wikipedia. "
    "Always perform at least one Wikipedia search before answering any factual question, "
    "even when you believe you know the answer. Wikipedia is the source of record for this system. "
    "Answer based on what the search returns, not on prior knowledge alone. "
    "For every fact you state, mention the Wikipedia article it came from. "
    "Distinguish clearly between facts directly stated in the retrieved extracts and facts you are "
    "inferring or assembling across multiple articles. "
    "When the retrieved evidence is fragmentary or indirect, say so explicitly and caveat your answer. "
    "If a question requires information that is simply not present in the retrieved extracts, "
    "state that you cannot answer it from Wikipedia rather than synthesizing a response from related articles."
)

SEARCH_WIKIPEDIA_TOOL: dict[str, object] = {
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
