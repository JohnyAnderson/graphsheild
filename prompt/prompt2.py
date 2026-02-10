from __future__ import annotations
from typing import Any

GRAPH_FIELD_SEP = "<SEP>"

PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "English"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

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

PROMPTS["summarize_entity_descriptions_zh"] = """你是一个负责生成智能合约实体综合摘要的有用助手。
给定一个或两个实体及其描述列表，所有这些都与同一个智能合约实体或实体组相关。
请将所有描述合并为一个全面的摘要，重点关注它们在智能合约中的角色。
如果提供的描述相互矛盾，请解决矛盾并提供单一、连贯的摘要。
确保使用第三人称写作，并包含实体名称以便我们有完整的上下文。
使用{language}作为输出语言。

#######
---数据---
实体: {entity_name}
描述列表: {description_list}
#######
输出:
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

PROMPTS["entity_continue_extraction_zh"] = """
上次提取中遗漏了许多与智能合约相关的实体和关系。

---记住步骤---

1. 识别所有智能合约实体。对每个实体提取:
- entity_name: 实体名称
- entity_type: 其中之一: [{entity_types}]
- entity_description: 实体在合约中的角色描述
格式: ("entity"{tuple_delimiter}<名称>{tuple_delimiter}<类型>{tuple_delimiter}<描述>)

2. 从实体中识别所有相关的实体对:
- source_entity: 源实体名称
- target_entity: 目标实体名称
- relationship_description: 它们在合约上下文中的关系
- relationship_strength: 1-10分数
- relationship_keywords: 总结关系的关键词
格式: ("relationship"{tuple_delimiter}<源>{tuple_delimiter}<目标>{tuple_delimiter}<描述>{tuple_delimiter}<关键词>{tuple_delimiter}<强度>)

3. 识别总结合约的高级关键词。
格式: ("content_keywords"{tuple_delimiter}<关键词>)

4. 以{language}返回输出，使用**{record_delimiter}**作为分隔符。

5. 完成后输出{completion_delimiter}

---输出---

使用相同格式添加在下面:\n
""".strip()

PROMPTS["entity_if_loop_extraction"] = """
---Goal---

It appears some smart contract entities may have still been missed.

---Output---

Answer ONLY by `YES` OR `NO` if there are still entities that need to be added.
""".strip()

PROMPTS["entity_if_loop_extraction_zh"] = """
---目标---

似乎仍然遗漏了一些智能合约实体。

---输出---

仅回答`YES`或`NO`，表示是否仍有需要添加的实体。
""".strip()

PROMPTS["rag_response"] = """---Role---

You are a helpful assistant responding to user queries about Smart Contract Knowledge Base provided below.

---Goal---

Generate a concise response based on Smart Contract Knowledge Base and follow Response Rules. The Knowledge Base contains extracted entities and relationships from smart contracts. Summarize all relevant information while focusing on contract structure, invariants, vulnerabilities and relationships.

---Conversation History---
{history}

---Knowledge Base---
{context_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with section headings like "Contract Structure", "Key Invariants", "Potential Vulnerabilities"
- Respond in the same language as the user's question
- Maintain continuity with conversation history
- List up to 5 most important reference sources at the end under "References"
- Clearly indicate whether each source is from Knowledge Graph (KG) or Vector Data (DC)
- If you don't know the answer, just say so
- Do not make anything up beyond the Knowledge Base content
"""

PROMPTS["rag_response_zh"] = """---角色---

你是一个有用的助手，负责回应用户关于下面提供的智能合约知识库的查询。

---目标---

基于智能合约知识库生成简洁的响应并遵循响应规则。知识库包含从智能合约中提取的实体和关系。总结所有相关信息，重点关注合约结构、不变量、漏洞和关系。

---对话历史---
{history}

---知识库---
{context_data}

---响应规则---

- 目标格式和长度: {response_type}
- 使用带有"合约结构"、"关键不变量"、"潜在漏洞"等标题的markdown格式
- 使用与用户问题相同的语言回答
- 保持与对话历史的连续性
- 在最后的"参考文献"下列出最多5个最重要的参考来源
- 明确标明每个来源是来自知识图谱(KG)还是向量数据(DC)
- 如果不知道答案，直接说明
- 不要编造超出知识库内容的信息
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

PROMPTS["keywords_extraction_zh"] = """---角色---

你是一个有用的助手，负责识别智能合约相关查询中的高级和低级关键词。

---目标---

根据查询和对话历史，列出与智能合约分析相关的高级和低级关键词。高级关键词关注整体概念(如安全性、不变量)，低级关键词关注特定实体(函数、变量)或漏洞。

---说明---

- 考虑当前查询和相关对话历史
- 以JSON格式输出:
  - "high_level_keywords" 用于合约级概念
  - "low_level_keywords" 用于具体元素
- JSON将被解析，所以不要添加额外内容

######################
---示例---
######################
{examples}

#############################
---真实数据---
######################
对话历史:
{history}

当前查询: {query}
######################
输出:
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

PROMPTS["keywords_extraction_examples_zh"] = [
    """示例1:

查询: "重入保护如何在这个合约中防止攻击?"
################
输出:
{
  "high_level_keywords": ["重入保护", "安全机制", "合约安全性"],
  "low_level_keywords": ["nonReentrant修饰器", "_notEntered变量", "函数调用"]
}
#############################""",
    """示例2:

查询: "SafeMath合约中哪些不变量防止整数溢出?"
################
输出:
{
  "high_level_keywords": ["整数溢出", "算术安全", "不变量"],
  "low_level_keywords": ["mul函数", "assert检查", "uint256变量"]
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

PROMPTS["naive_rag_response_zh"] = """---角色---

你是一个有用的助手，负责回应用户关于智能合约文档块的查询。

---目标---

基于智能合约文档块生成简洁的响应，重点关注代码段、不变量和漏洞。在保持对源材料准确性的同时总结信息。

---对话历史---
{history}

---文档块---
{content_data}

---响应规则---

- 目标格式和长度: {response_type}
- 使用带有"代码分析"、"安全考虑"等部分的markdown格式
- 使用用户的语言回答
- 保持对话连续性
- 列出明确标记为[DC]的文档块参考文献
- 不知道时直接说明
- 严格限制在提供的内容范围内
"""

PROMPTS["mix_rag_response"] = """---Role---

You are a helpful assistant responding to user queries about Smart Contract Data Sources.

---Goal---

Generate a comprehensive response combining information from Knowledge Graph (entities/relationships) and Document Chunks (code segments). Provide holistic analysis of contract structure, behavior and security aspects.

---Conversation History---
{history}

---Data Sources---

1. From Knowledge Graph(KG):
{kg_context}

2. From Document Chunks(DC):
{vector_context}

---Response Rules---

- Target format and length: {response_type}
- Use markdown with clear sections
- Respond in user's language
- Maintain conversation continuity
- Clearly separate and credit KG vs DC sources
- List references with [KG] or [DC] tags
- Admit knowledge gaps
- Never exceed provided information
"""

PROMPTS["mix_rag_response_zh"] = """---角色---

你是一个有用的助手，负责回应用户关于智能合约数据源的查询。

---目标---

生成综合响应，结合知识图谱(实体/关系)和文档块(代码段)的信息。提供合约结构、行为和安全方面的整体分析。

---对话历史---
{history}

---数据源---

1. 来自知识图谱(KG):
{kg_context}

2. 来自文档块(DC):
{vector_context}

---响应规则---

- 目标格式和长度: {response_type}
- 使用带有清晰章节的markdown格式
- 使用用户的语言回答
- 保持对话连续性
- 明确区分并注明KG与DC来源
- 列出带有[KG]或[DC]标签的参考文献
- 承认知识空白
- 绝不超出提供的信息范围
"""