from __future__ import annotations
from typing import Any

GRAPH_FIELD_SEP = "<SEP>"

PROMPTS: dict[str, Any] = {}

PROMPTS["DEFAULT_LANGUAGE"] = "English"
PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS["DEFAULT_ENTITY_TYPES"] = [
    "vulnerability",
    "contract",
    "function",
    "variable",
    "security_issue",
    "mitigation",
    "impact",
    "code_block"
]

PROMPTS["entity_extraction"] = """---Goal---
Given a smart contract vulnerability audit report, identify all security-related entities and their relationships, with special attention to vulnerabilities, impacts, and recommended mitigations.
Use {language} as output language.

---Steps---
1. Identify all entities. For each entity, extract:
- entity_name: Entity name or identifier
- entity_type: One of: [{entity_types}]
- entity_description: Detailed description including severity, impact and context
Format each entity as ("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. From step 1 entities, identify all clearly related (source_entity, target_entity) pairs.
For each related pair, extract:
- source_entity: Source entity name
- target_entity: Target entity name
- relationship_description: Explanation of their relationship
- relationship_strength: Relationship strength score (1-10)
- relationship_keywords: Keywords summarizing relationship nature
Format each relationship as ("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_keywords>{tuple_delimiter}<relationship_strength>)

3. Identify high-level keywords summarizing the report's main security findings.
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
Report Data:
{input_text}
######################
Output:"""

PROMPTS["entity_extraction_examples_kg2"] = [
    """Example 1:

Entity_types: [vulnerability, contract, function, variable, security_issue, mitigation, impact, code_block]
Report:
```
"bug_id": "H-02",
"bug_description": "2 variables not indexed by marketIndex",
"line": "Staker[622]",
"main_content": [
"In the token contract: batched_stakerNextTokenShiftIndex is indexed by marketIndex...",
"stakerTokenShiftIndex_to_longShortMarketPriceSnapshotIndex_mapping and stakerTokenShiftIndex_to_accumulativeFloatIssuanceSnapshotIndex_mapping are not indexed by marketIndex.",
"This will lead to weird results in _calculateAccumulatedFloat, allocating too much or too little float."
],
"code_blocks": [
"function pushUpdatedMarketPricesToUpdateFloatIssuanceCalculations(...)"
],
"recommended_mitigation": [
"adding an index with marketIndex to the variables",
"Also consider shortening the variable names"
]
```
Output:
("entity"{tuple_delimiter}"H-02"{tuple_delimiter}"vulnerability"{tuple_delimiter}"High severity vulnerability where 2 variables are not indexed by marketIndex, leading to incorrect float allocation"){record_delimiter}
("entity"{tuple_delimiter}"Staker contract"{tuple_delimiter}"contract"{tuple_delimiter}"Contract containing the vulnerability with unindexed variables"){record_delimiter}
("entity"{tuple_delimiter}"pushUpdatedMarketPricesToUpdateFloatIssuanceCalculations"{tuple_delimiter}"function"{tuple_delimiter}"Function containing the vulnerable variable assignments"){record_delimiter}
("entity"{tuple_delimiter}"batched_stakerNextTokenShiftIndex"{tuple_delimiter}"variable"{tuple_delimiter}"Correctly indexed variable by marketIndex"){record_delimiter}
("entity"{tuple_delimiter}"stakerTokenShiftIndex_to_longShortMarketPriceSnapshotIndex_mapping"{tuple_delimiter}"variable"{tuple_delimiter}"Vulnerable variable not indexed by marketIndex"){record_delimiter}
("entity"{tuple_delimiter}"incorrect float allocation"{tuple_delimiter}"impact"{tuple_delimiter}"Impact of vulnerability leading to incorrect float token distribution"){record_delimiter}
("entity"{tuple_delimiter}"add marketIndex indexing"{tuple_delimiter}"mitigation"{tuple_delimiter}"Recommended mitigation to add marketIndex indexing to variables"){record_delimiter}
("relationship"{tuple_delimiter}"H-02"{tuple_delimiter}"Staker contract"{tuple_delimiter}"Vulnerability exists in Staker contract"{tuple_delimiter}"containment"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"H-02"{tuple_delimiter}"pushUpdatedMarketPricesToUpdateFloatIssuanceCalculations"{tuple_delimiter}"Vulnerability manifests in this function"{tuple_delimiter}"manifestation"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"H-02"{tuple_delimiter}"incorrect float allocation"{tuple_delimiter}"Vulnerability leads to this impact"{tuple_delimiter}"cause-effect"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"H-02"{tuple_delimiter}"add marketIndex indexing"{tuple_delimiter}"This mitigation addresses the vulnerability"{tuple_delimiter}"resolution"{tuple_delimiter}10){record_delimiter}
("content_keywords"{tuple_delimiter}"indexing vulnerability, float allocation, market specific variables"){completion_delimiter}
#############################""",
    """Example 2:

Entity_types: [vulnerability, contract, function, variable, security_issue, mitigation, impact, code_block]
Report:
```
"bug_id": "H-11",
"bug_description": "ConstantProductPool.burnSingle swap amount computations should use balance",
"line": "ConstantProductPool[156,175], HybridPool[143,159]",
"main_content": [
"The ConstantProductPool.burnSingle function computes swap amounts incorrectly",
"The token amounts to redeem are computed on balance but swap amount is computed on reserves",
"This could lead to returning slightly less swap amounts when balance > reserve"
],
"code_blocks": [
"amount1 += _getAmountOut(amount0, _reserve0 - amount0, _reserve1 - amount1);"
],
"recommended_mitigation": [
"Call _getAmountOut with the balances instead of reserves"
]
```
Output:
("entity"{tuple_delimiter}"H-11"{tuple_delimiter}"vulnerability"{tuple_delimiter}"High severity vulnerability in burnSingle function with incorrect swap amount computation"){record_delimiter}
("entity"{tuple_delimiter}"ConstantProductPool"{tuple_delimiter}"contract"{tuple_delimiter}"Contract containing the vulnerable burnSingle function"){record_delimiter}
("entity"{tuple_delimiter}"HybridPool"{tuple_delimiter}"contract"{tuple_delimiter}"Contract with similar vulnerability pattern"){record_delimiter}
("entity"{tuple_delimiter}"burnSingle"{tuple_delimiter}"function"{tuple_delimiter}"Function with incorrect swap amount computation"){record_delimiter}
("entity"{tuple_delimiter}"_getAmountOut"{tuple_delimiter}"function"{tuple_delimiter}"Function called with incorrect reserve parameters"){record_delimiter}
("entity"{tuple_delimiter}"incorrect swap amounts"{tuple_delimiter}"impact"{tuple_delimiter}"Impact of vulnerability leading to potential loss of funds"){record_delimiter}
("entity"{tuple_delimiter}"use balances instead of reserves"{tuple_delimiter}"mitigation"{tuple_delimiter}"Recommended fix to use balances in _getAmountOut call"){record_delimiter}
("relationship"{tuple_delimiter}"H-11"{tuple_delimiter}"ConstantProductPool"{tuple_delimiter}"Vulnerability exists in this contract"{tuple_delimiter}"containment"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"H-11"{tuple_delimiter}"burnSingle"{tuple_delimiter}"Vulnerability manifests in this function"{tuple_delimiter}"manifestation"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"H-11"{tuple_delimiter}"incorrect swap amounts"{tuple_delimiter}"Vulnerability leads to this impact"{tuple_delimiter}"cause-effect"{tuple_delimiter}10){record_delimiter}
("relationship"{tuple_delimiter}"burnSingle"{tuple_delimiter}"_getAmountOut"{tuple_delimiter}"Function calls _getAmountOut with incorrect parameters"{tuple_delimiter}"incorrect-call"{tuple_delimiter}8){record_delimiter}
("content_keywords"{tuple_delimiter}"swap computation, reserve mismatch, loss of funds"){completion_delimiter}
#############################"""
]

PROMPTS["summarize_entity_descriptions"] = """You are a helpful assistant responsible for generating a comprehensive summary of smart contract vulnerabilities.
Given one or two entities, and a list of descriptions, all related to the same vulnerability or group of vulnerabilities.
Please concatenate all of these into a single, comprehensive description focusing on their security implications.
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

PROMPTS["summarize_entity_descriptions_zh"] = """你是一个负责生成智能合约漏洞综合摘要的有用助手。
给定一个或两个实体及其描述列表，所有这些都与同一个漏洞或漏洞组相关。
请将所有描述合并为一个全面的摘要，重点关注它们的安全影响。
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
MANY security-related entities and relationships were missed in the last extraction.

---Remember Steps---

1. Identify all security-related entities. For each entity, extract:
- entity_name: Entity name or identifier
- entity_type: One of: [{entity_types}]
- entity_description: Detailed description including severity and impact
Format: ("entity"{tuple_delimiter}<name>{tuple_delimiter}<type>{tuple_delimiter}<description>)

2. From the entities, identify all pairs of related entities:
- source_entity: source entity name
- target_entity: target entity name
- relationship_description: how they relate in security context
- relationship_strength: 1-10 score
- relationship_keywords: keywords summarizing relationship
Format: ("relationship"{tuple_delimiter}<source>{tuple_delimiter}<target>{tuple_delimiter}<desc>{tuple_delimiter}<keywords>{tuple_delimiter}<strength>)

3. Identify high-level security keywords summarizing the report.
Format: ("content_keywords"{tuple_delimiter}<keywords>)

4. Return output in {language} as a single list using **{record_delimiter}** as delimiter.

5. When finished, output {completion_delimiter}

---Output---

Add them below using the same format:\n
""".strip()

PROMPTS["entity_continue_extraction_zh"] = """
上次提取中遗漏了许多与安全相关的实体和关系。

---记住步骤---

1. 识别所有安全相关实体。对每个实体提取:
- entity_name: 实体名称或标识符
- entity_type: 其中之一: [{entity_types}]
- entity_description: 包含严重性和影响的详细描述
格式: ("entity"{tuple_delimiter}<名称>{tuple_delimiter}<类型>{tuple_delimiter}<描述>)

2. 从实体中识别所有相关的实体对:
- source_entity: 源实体名称
- target_entity: 目标实体名称
- relationship_description: 它们在安全上下文中的关系
- relationship_strength: 1-10分数
- relationship_keywords: 总结关系的关键词
格式: ("relationship"{tuple_delimiter}<源>{tuple_delimiter}<目标>{tuple_delimiter}<描述>{tuple_delimiter}<关键词>{tuple_delimiter}<强度>)

3. 识别总结报告的高级安全关键词。
格式: ("content_keywords"{tuple_delimiter}<关键词>)

4. 以{language}返回输出，使用**{record_delimiter}**作为分隔符。

5. 完成后输出{completion_delimiter}

---输出---

使用相同格式添加在下面:\n
""".strip()

PROMPTS["entity_if_loop_extraction"] = """
---Goal---

It appears some security-related entities may have still been missed.

---Output---

Answer ONLY by `YES` OR `NO` if there are still entities that need to be added.
""".strip()

PROMPTS["entity_if_loop_extraction_zh"] = """
---目标---

似乎仍然遗漏了一些安全相关实体。

---输出---

仅回答`YES`或`NO`，表示是否仍有需要添加的实体。
""".strip()

PROMPTS["rag_response"] = """---Role---

You are a helpful assistant responding to user queries about Smart Contract Vulnerability Reports provided below.

---Goal---

Generate a concise response based on Vulnerability Reports and follow Response Rules. The reports contain extracted security entities and relationships. Summarize all relevant information while focusing on vulnerabilities, impacts, and mitigations.

---Conversation History---
{history}

---Vulnerability Reports---
{context_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown formatting with section headings like "Vulnerabilities", "Security Impacts", "Recommended Mitigations"
- Respond in the same language as the user's question
- Maintain continuity with conversation history
- List up to 5 most important reference sources at the end under "References"
- Clearly indicate whether each source is from Knowledge Graph (KG) or Vector Data (DC)
- If you don't know the answer, just say so
- Do not make anything up beyond the Reports content
"""

PROMPTS["rag_response_zh"] = """---角色---

你是一个有用的助手，负责回应用户关于下面提供的智能合约漏洞报告的查询。

---目标---

基于智能合约漏洞报告生成简洁的响应并遵循响应规则。报告包含提取的安全实体和关系。总结所有相关信息，重点关注漏洞、影响和修复措施。

---对话历史---
{history}

---漏洞报告---
{context_data}

---响应规则---

- 目标格式和长度: {response_type}
- 使用带有"漏洞"、"安全影响"、"推荐修复措施"等标题的markdown格式
- 使用与用户问题相同的语言回答
- 保持与对话历史的连续性
- 在最后的"参考文献"下列出最多5个最重要的参考来源
- 明确标明每个来源是来自知识图谱(KG)还是向量数据(DC)
- 如果不知道答案，直接说明
- 不要编造超出报告内容的信息
"""

PROMPTS["keywords_extraction"] = """---Role---

You are a helpful assistant tasked with identifying both high-level and low-level keywords in smart contract vulnerability related queries.

---Goal---

Given the query and conversation history, list both high-level and low-level keywords related to smart contract security analysis. High-level keywords focus on overarching security concepts (like vulnerabilities, invariants), while low-level keywords focus on specific entities (functions, variables) or security issues.

---Instructions---

- Consider both current query and relevant conversation history
- Output in JSON format with:
  - "high_level_keywords" for security-level concepts
  - "low_level_keywords" for specific security elements
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

你是一个有用的助手，负责识别智能合约漏洞相关查询中的高级和低级关键词。

---目标---

根据查询和对话历史，列出与智能合约安全分析相关的高级和低级关键词。高级关键词关注整体安全概念(如漏洞、不变量)，低级关键词关注特定实体(函数、变量)或安全问题。

---说明---

- 考虑当前查询和相关对话历史
- 以JSON格式输出:
  - "high_level_keywords" 用于安全级概念
  - "low_level_keywords" 用于具体安全元素
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

Query: "How does the unindexed variable vulnerability impact float token allocation?"
################
Output:
{
  "high_level_keywords": ["Indexing vulnerability", "Token allocation", "Security impact"],
  "low_level_keywords": ["batched_stakerNextTokenShiftIndex", "marketIndex", "_calculateAccumulatedFloat"]
}
#############################""",
    """Example 2:

Query: "What are the risks of incorrect swap amount computation in burnSingle?"
################
Output:
{
  "high_level_keywords": ["Swap computation", "Fund loss", "Reserve mismatch"],
  "low_level_keywords": ["burnSingle", "_getAmountOut", "ConstantProductPool"]
}
#############################"""
]

PROMPTS["keywords_extraction_examples_zh"] = [
    """示例1:

查询: "未索引变量漏洞如何影响float代币分配?"
################
输出:
{
  "high_level_keywords": ["索引漏洞", "代币分配", "安全影响"],
  "low_level_keywords": ["batched_stakerNextTokenShiftIndex", "marketIndex", "_calculateAccumulatedFloat"]
}
#############################""",
    """示例2:

查询: "burnSingle中错误交换量计算有哪些风险?"
################
输出:
{
  "high_level_keywords": ["交换计算", "资金损失", "储备不匹配"],
  "low_level_keywords": ["burnSingle", "_getAmountOut", "ConstantProductPool"]
}
#############################"""
]

PROMPTS["naive_rag_response"] = """---Role---

You are a helpful assistant responding to user queries about Smart Contract Vulnerability Document Chunks.

---Goal---

Generate a concise response based on Vulnerability Document Chunks, focusing on security issues, code segments, and mitigations. Summarize information while maintaining accuracy to the source material.

---Conversation History---
{history}

---Document Chunks---
{content_data}

---Response Rules---

- Target format and length: {response_type}
- Use markdown with sections like "Security Issues", "Vulnerable Code", "Mitigations"
- Respond in user's language
- Maintain conversation continuity
- List references clearly marked as [DC] for Document Chunks
- Admit when you don't know
- Stay strictly within provided content
"""

PROMPTS["naive_rag_response_zh"] = """---角色---

你是一个有用的助手，负责回应用户关于智能合约漏洞文档块的查询。

---目标---

基于智能合约漏洞文档块生成简洁的响应，重点关注安全问题、代码段和修复措施。在保持对源材料准确性的同时总结信息。

---对话历史---
{history}

---文档块---
{content_data}

---响应规则---

- 目标格式和长度: {response_type}
- 使用带有"安全问题"、"漏洞代码"、"修复措施"等部分的markdown格式
- 使用用户的语言回答
- 保持对话连续性
- 列出明确标记为[DC]的文档块参考文献
- 不知道时直接说明
- 严格限制在提供的内容范围内
"""

PROMPTS["mix_rag_response"] = """---Role---

You are a helpful assistant responding to user queries about Smart Contract Vulnerability Data Sources.

---Goal---

Generate a comprehensive response combining information from Knowledge Graph (security entities/relationships) and Document Chunks (vulnerability details). Provide holistic analysis of security issues, impacts and mitigation strategies.

---Conversation History---
{history}

---Data Sources---

1. From Knowledge Graph(KG):
{kg_context}

2. From Document Chunks(DC):
{vector_context}

---Response Rules---

- Target format and length: {response_type}
- Use markdown with clear security-focused sections
- Respond in user's language
- Maintain conversation continuity
- Clearly separate and credit KG vs DC sources
- List references with [KG] or [DC] tags
- Admit knowledge gaps
- Never exceed provided information
"""

PROMPTS["mix_rag_response_zh"] = """---角色---

你是一个有用的助手，负责回应用户关于智能合约漏洞数据源的查询。

---目标---

生成综合响应，结合知识图谱(安全实体/关系)和文档块(漏洞详情)的信息。提供安全问题、影响和修复策略的整体分析。

---对话历史---
{history}

---数据源---

1. 来自知识图谱(KG):
{kg_context}

2. 来自文档块(DC):
{vector_context}

---响应规则---

- 目标格式和长度: {response_type}
- 使用带有清晰安全章节的markdown格式
- 使用用户的语言回答
- 保持对话连续性
- 明确区分并注明KG与DC来源
- 列出带有[KG]或[DC]标签的参考文献
- 承认知识空白
- 绝不超出提供的信息范围
"""
