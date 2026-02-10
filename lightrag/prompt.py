from __future__ import annotations
from typing import Any

GRAPH_FIELD_SEP = "<SEP>"

PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "English"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"
PROMPTS["DEFAULT_USER_PROMPT"] = "n/a"
PROMPTS["DEFAULT_ENTITY_TYPES"] = ["contract", "function", "variable", "invariant", "critical_invariant", "vulnerability", "assertion", "require"]

PROMPTS["entity_extraction"] = """---Goal---
Given a smart contract code snippet and its related analysis data (in txt format), identify all entities and their relationships, with special attention to critical-invariants and ranks parameters.
Use {language} as output language.

---Steps---
1. Identify all entities. For each entity, extract:
- entity_name: Entity name, same as in code
- entity_type: One of: [{entity_types}]
- entity_description: Detailed description including role, characteristics and criticality (if marked as critical-invariants)
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From step 1 entities, identify all clearly related (source_entity, target_entity) pairs.
For each related pair, extract:
- source_entity: Source entity name
- target_entity: Target entity name
- relationship_description: Explanation of their relationship
- relationship_strength: Relationship strength score (1-10), considering ranks parameter
- relationship_keywords: Keywords summarizing relationship nature
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level keywords summarizing the code's main concepts, themes or patterns.
Format as ("content_keywords"{tuple_delimiter}<high_level_keywords>)

4. Return output in {language} as a list of all entities and relationships, using **{record_delimiter}** as delimiter.

5. When finished, output {completion_delimiter}

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Entity_types: [{entity_types}]
JSON Data:
{input_text}
######################
Output:"""


PROMPTS["entity_extraction_examples"] = [
    """Example 1:

Entity_types: [contract, function, variable, invariant, critical_invariant, vulnerability, assertion, require]
TXT:
```
"code": "pragma solidity ^0.4.24;\ncontract Token {\n    mapping(address => uint) balances;\n    \n    function transfer(address to, uint amount) public {\n        require(balances[msg.sender] >= amount);\n        balances[msg.sender] -= amount;\n        balances[to] += amount;\n    }\n}","transaction-context": "asset transfer","Critical-points": "5+","invariants": "5+ require(balances[msg.sender] >= amount);","critical-invariants": "5+ require(balances[msg.sender] >= amount);","ranks": "5+ require(balances[msg.sender] >= amount);","vulnerabilities": "integer overflow"
```
Output:
("entity"{tuple_delimiter}"Token"{tuple_delimiter}"contract"{tuple_delimiter}"Token contract managing address balances and transfer functions"){record_delimiter}
("entity"{tuple_delimiter}"transfer"{tuple_delimiter}"function"{tuple_delimiter}"Transfer function executing token transfer logic"){record_delimiter}
("entity"{tuple_delimiter}"balances"{tuple_delimiter}"variable"{tuple_delimiter}"Mapping storing address to token balance"){record_delimiter}
("entity"{tuple_delimiter}"require(balances[msg.sender] >= amount)"{tuple_delimiter}"require"{tuple_delimiter}"Require statement ensuring transfer amount doesn't exceed sender balance"){record_delimiter}
("entity"{tuple_delimiter}"require(balances[msg.sender] >= amount)"{tuple_delimiter}"critical_invariant"{tuple_delimiter}"Critical invariant: ensures transfer amount doesn't exceed sender balance"){record_delimiter}
("entity"{tuple_delimiter}"integer overflow"{tuple_delimiter}"vulnerability"{tuple_delimiter}"Integer overflow vulnerability risk in transfer function"){record_delimiter}
("relationship"{tuple_delimiter}"Token"{tuple_delimiter}"transfer"{tuple_delimiter}"Token contract contains transfer function"{tuple_delimiter}"containment"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"Token"{tuple_delimiter}"balances"{tuple_delimiter}"Token contract contains balances mapping"{tuple_delimiter}"containment"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"transfer"{tuple_delimiter}"require(balances[msg.sender] >= amount)"{tuple_delimiter}"transfer function includes critical balance check invariant"{tuple_delimiter}"validation"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"transfer"{tuple_delimiter}"balances"{tuple_delimiter}"transfer function modifies balances mapping"{tuple_delimiter}"modification"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"transfer"{tuple_delimiter}"integer overflow"{tuple_delimiter}"transfer function has integer overflow risk"{tuple_delimiter}"vulnerability"{tuple_delimiter}7){record_delimiter}
("content_keywords"{tuple_delimiter}"token contract, balance management, transfer security, integer overflow, access control"){completion_delimiter}
#############################""",
    """Example 2:

Entity_types: [contract, function, variable, invariant, critical_invariant, vulnerability, assertion, require]
TXT:
```
"code": "pragma solidity >=0.4.24;\ncontract SafeMath {\n    function mul(uint a, uint b) internal pure returns (uint) {\n        if (a == 0) { return 0; }\n        uint c = a * b;\n        assert(c / a == b);\n        return c;\n    }\n}","transaction-context": "arithmetic operations","Critical-points": "6+","invariants": "6+ assert(c / a == b);","critical-invariants": "6+ assert(c / a == b);","ranks": "6+ assert(c / a == b);","vulnerabilities": ""}
```
Output:
("entity"{tuple_delimiter}"SafeMath"{tuple_delimiter}"contract"{tuple_delimiter}"Safe math operations contract preventing arithmetic overflow"){record_delimiter}
("entity"{tuple_delimiter}"mul"{tuple_delimiter}"function"{tuple_delimiter}"Multiplication function with overflow check"){record_delimiter}
("entity"{tuple_delimiter}"a"{tuple_delimiter}"variable"{tuple_delimiter}"First multiplication operand"){record_delimiter}
("entity"{tuple_delimiter}"b"{tuple_delimiter}"variable"{tuple_delimiter}"Second multiplication operand"){record_delimiter}
("entity"{tuple_delimiter}"c"{tuple_delimiter}"variable"{tuple_delimiter}"Multiplication result variable"){record_delimiter}
("entity"{tuple_delimiter}"assert(c / a == b)"{tuple_delimiter}"assertion"{tuple_delimiter}"Assertion verifying multiplication correctness"){record_delimiter}
("entity"{tuple_delimiter}"assert(c / a == b)"{tuple_delimiter}"critical_invariant"{tuple_delimiter}"Critical invariant: multiplication result verification preventing overflow"){record_delimiter}
("relationship"{tuple_delimiter}"SafeMath"{tuple_delimiter}"mul"{tuple_delimiter}"SafeMath contract contains mul function"{tuple_delimiter}"containment"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"mul"{tuple_delimiter}"a"{tuple_delimiter}"mul function uses parameter a"{tuple_delimiter}"parameter"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"mul"{tuple_delimiter}"b"{tuple_delimiter}"mul function uses parameter b"{tuple_delimiter}"parameter"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"mul"{tuple_delimiter}"c"{tuple_delimiter}"mul function calculates and returns c"{tuple_delimiter}"calculation"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"mul"{tuple_delimiter}"assert(c / a == b)"{tuple_delimiter}"mul function includes critical multiplication verification invariant"{tuple_delimiter}"validation"{tuple_delimiter}10){record_delimiter}
("content_keywords"{tuple_delimiter}"safe math, overflow protection, multiplication verification, arithmetic safety"){completion_delimiter}
#############################"""
]

PROMPTS["summarize_entity_descriptions"] = """You are a helpful assistant responsible for generating a comprehensive summary of smart contract entities.
Given one or two entities, and a list of descriptions, all related to the same smart contract entity or group of entities.
Please concatenate all of these into a single, comprehensive description focusing on their roles in smart contracts.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we have full context.
Use {language} as output language.

#######
---Data---
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""



PROMPTS["entity_continue_extraction"] = """
MANY entities and relationships related to smart contracts were missed in the last extraction.

---Remember Steps---

1. Identify all smart contract entities. For each identified entity, extract:
- entity_name: Name of the entity
- entity_type: One of: [{entity_types}]
- entity_description: Description of the entity's role in the contract
Format: ("entity"{tuple_delimiter}<name>{tuple_delimiter}<type>{tuple_delimiter}<description>)

2. From the entities, identify all pairs of related entities:
- source_entity: source entity name
- target_entity: target entity name
- relationship_description: how they relate in contract context
- relationship_strength: 1-10 score
- relationship_keywords: keywords summarizing relationship
Format: ("relationship"{tuple_delimiter}<source>{tuple_delimiter}<target>{tuple_delimiter}<desc>{tuple_delimiter}<keywords>{tuple_delimiter}<strength>)

3. Identify high-level keywords summarizing the contract.
Format: ("content_keywords"{tuple_delimiter}<keywords>)

4. Return output in {language} as a single list using **{record_delimiter}** as delimiter.

5. When finished, output {completion_delimiter}

---Output---

Add them below using the same format:\n
""".strip()



PROMPTS["entity_if_loop_extraction"] = """
---Goal---

It appears some smart contract entities may have still been missed.

---Output---

Answer ONLY by `YES` OR `NO` if there are still entities that need to be added.
""".strip()


PROMPTS["rag_response"] = """---Role---
The user query is a Solidity smart contract code statement. You are a smart contract analysis assistant that needs to perform contract invariant generation and vulnerability analysis on the smart contract code based on the provided knowledge base.

---Goal---
Generate comprehensive response through 3-tier analysis, Generate a concise response based on Knowledge Base and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Knowledge Base, and incorporating general knowledge relevant to the Knowledge Base. :
1. Tier 1: Identify critical program points from transaction context
2. Tier 2: Extract invariants based on critical points
3. Tier 3: Evaluate invariants and detect vulnerabilities

When handling relationships with timestamps:
1. Each relationship has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting relationships, consider both the semantic content and the timestamp
3. Don't automatically prefer the most recently created relationships - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Knowledge Base---
{context_data}

---Processing Flow---
1. Transaction Context Identification:
   • Determine contract transaction type (e.g. token transfer, voting)

   • Output format example: [7,4,10,12,17] (token transfer case)


2. Invariant Extraction:
   • Generate Smartcontract invariants from structural analysis

   • Convert all generated invariants into code (e.g. assert(Old(reserve0) == reserve0 + amount0))


3. Vulnerability Detection:
   • Evaluate the importance of all the generated invariants and rank them

   • Analyze the user query's contract code for vulnerabilities based on related Knowledge Base


---Response Rules---

• Target format and length: {response_type}

• Use markdown formatting with the following section headings:
   - Transaction Context Identification
   - Invariant Extraction
   - Vulnerability Detection

• Please respond in the same language as the user's question.

• Ensure the response maintains continuity with the conversation history.

• List up to 5 most important reference sources at the end under "References" section. Clearly indicating whether each source is from Knowledge Graph (KG) or Vector Data (DC), and include the file path if available, in the following format: [KG/DC] file_path

• If you don't know the answer, just say so.

• Do not make anything up. Do not include information not provided by the Knowledge Base.

• Additional user prompt: {user_prompt}


Response:
"""



PROMPTS["keywords_extraction"] = """---Role---

You are a helpful assistant tasked with identifying both high-level and low-level keywords in smart contract related queries.

---Goal---

Given the query and conversation history, list both high-level and low-level keywords related to smart contract analysis. High-level keywords focus on overarching concepts (like security, invariants), while low-level keywords focus on specific entities (functions, variables) or vulnerabilities.

---Instructions---

- Consider both current query and relevant conversation history
- Output in JSON format with:
  - "high_level_keywords" for contract-level concepts
  - "low_level_keywords" for specific elements
- The JSON will be parsed, so no extra content

######################
---Examples---
######################
{examples}

#############################
---Real Data---
######################
Conversation History:
{history}

Current Query: {query}
######################
Output:
"""


PROMPTS["keywords_extraction_examples"] = [
    """Example 1:

Query: "How does the reentrancy guard prevent attacks in this contract?"
################
Output:
{
  "high_level_keywords": ["Reentrancy protection", "Security mechanism", "Contract safety"],
  "low_level_keywords": ["nonReentrant modifier", "_notEntered variable", "function calls"]
}
#############################""",
    """Example 2:

Query: "What invariants protect against integer overflow in the SafeMath contract?"
################
Output:
{
  "high_level_keywords": ["Integer overflow", "Arithmetic safety", "Invariants"],
  "low_level_keywords": ["mul function", "assert checks", "uint256 variables"]
}
#############################"""
]


PROMPTS["naive_rag_response"] = """---Role---

You are a helpful assistant responding to user queries about Smart Contract Document Chunks.

---Goal---

Generate a concise response based on Smart Contract Document Chunks, focusing on code segments, invariants, and vulnerabilities. Summarize information while maintaining accuracy to the source material.

---Conversation History---
{history}

---Document Chunks---
{content_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown with sections like "Code Analysis", "Security Considerations"
- Respond in user's language
- Maintain conversation continuity
- List references clearly marked as [DC] for Document Chunks
- Admit when you don't know
- Stay strictly within provided content
"""



PROMPTS["rag_response_double"] = """---Role---

The user query is a Solidity smart contract code statement. You are a smart contract analysis assistant that needs to perform contract invariant generation and vulnerability analysis on the smart contract code based on the provided knowledge base.

---Goal---
Generate comprehensive response through 3-tier analysis, Generate a concise response based on Knowledge Base and follow Response Rules, considering both the conversation history and the current query. Summarize all information in the provided Knowledge Base, and incorporating general knowledge relevant to the Knowledge Base. :
1. Tier 1: Identify critical program points from transaction context
2. Tier 2: Extract invariants based on critical points
3. Tier 3: Evaluate invariants and detect vulnerabilities

When handling relationships with timestamps:
1. Each relationship has a "created_at" timestamp indicating when we acquired this knowledge
2. When encountering conflicting relationships, consider both the semantic content and the timestamp
3. Don't automatically prefer the most recently created relationships - use judgment based on the context
4. For time-specific queries, prioritize temporal information in the content before considering creation timestamps

---Conversation History---
{history}

---Knowledge Base---
Vulnerability Knowledge
{kg1_context}
Smartcontract&Invariants Knowledge
{kg2_context}

---Processing Flow---
1. Transaction Context Identification:
   - Determine contract transaction type (e.g. token transfer, voting)
   - Output format example: [7,4,10,12,17] (token transfer case)

2. Invariant Extraction:
   - Generate Smartcontract invariants from structural analysis
   - Convert all generated invariants into code (e.g. assert(Old(reserve0) == reserve0 + amount0))

3. Vulnerability Detection:
   - Evaluate the importance of all the generated invariants and rank them
   - Analyze the user query's contract code for vulnerabilities based on related Knowledge Base

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with appropriate section headings
- Please respond in the same language as the user's question.
- Ensure the response maintains continuity with the conversation history.
- List up to 5 most important reference sources at the end under "References" section. Clearly indicating whether each source is from Knowledge Graph (KG) or Vector Data (DC), and include the file path if available, in the following format: [KG/DC] file_path
- If you don't know the answer, just say so.
- Do not make anything up. Do not include information not provided by the Knowledge Base.
- Additional user prompt: {user_prompt}

Response:"""
