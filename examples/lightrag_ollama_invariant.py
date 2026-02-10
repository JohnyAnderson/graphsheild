import asyncio
import nest_asyncio
import json
import os
import inspect
import logging
from lightrag import LightRAG, QueryParam
from lightrag.llm.ollama import ollama_model_complete, ollama_embed
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status
from typing import Dict, List, Literal, Tuple

# 定义类型别名提高可读性
KGChoice = Literal["kg1", "kg2", "double"]
SearchMode = Literal["naive", "local", "global", "hybrid"]

nest_asyncio.apply()

WORKING_DIR_KG1 = "../data/data01/abolish/large"
WORKING_DIR_KG2 = "../data/data02/data02_large"
SET_FILE ="../data/contract_generate/contract_code.json"
OUTPUT_FILE = "../result/invariants_analyze.json"
BATCH_SIZE = 10


logging.basicConfig(format="%(levelname)s:%(message)s", level=logging.INFO)

# if not os.path.exists(WORKING_DIR):
#     os.mkdir(WORKING_DIR)


async def initialize_rag_kg1(namespace:str):
    rag_kg1 = LightRAG(
        working_dir=WORKING_DIR_KG1,
        llm_model_func=ollama_model_complete,
        llm_model_name="qwen2.5:7b",
        llm_model_max_async=2,
        llm_model_max_token_size=32768,
        llm_model_kwargs={
            "host": "http://localhost:11434",
            "options": {"num_ctx": 32768},
        },
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: ollama_embed(
                texts, embed_model="nomic-embed-text", host="http://localhost:11434"
            ),
        ),
    )

    await rag_kg1.initialize_storages()
    await initialize_pipeline_status(namespace)

    return rag_kg1

async def initialize_rag_kg2(namespace:str):
    rag_kg2 = LightRAG(
        working_dir=WORKING_DIR_KG2,
        llm_model_func=ollama_model_complete,
        llm_model_name="qwen2.5:7b",
        llm_model_max_async=2,
        llm_model_max_token_size=32768,
        llm_model_kwargs={
            "host": "http://localhost:11434",
            "options": {"num_ctx": 32768},
        },
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: ollama_embed(
                texts, embed_model="nomic-embed-text", host="http://localhost:11434"
            ),
        ),
    )

    await rag_kg2.initialize_storages()
    await initialize_pipeline_status(namespace)
    return rag_kg2

async def initialize_rag_kg3(namespace:str):
    rag_kg3 = LightRAG(
        working_dir=WORKING_DIR_KG2,
        llm_model_func=ollama_model_complete,
        llm_model_name="qwen2.5:7b",
        llm_model_max_async=2,
        llm_model_max_token_size=32768,
        llm_model_kwargs={
            "host": "http://localhost:11434",
            "options": {"num_ctx": 32768},
        },
        embedding_func=EmbeddingFunc(
            embedding_dim=768,
            max_token_size=8192,
            func=lambda texts: ollama_embed(
                texts, embed_model="nomic-embed-text", host="http://localhost:11434"
            ),
        ),
    )

    await rag_kg3.initialize_storages()
    await initialize_pipeline_status(namespace)
    return rag_kg3

async def print_stream(stream):
    async for chunk in stream:
        print(chunk, end="", flush=True)

async def process_contract(
    kg_choice: KGChoice,
    search_mode: SearchMode,
    rag_kg1: LightRAG | None = None,
    rag_kg2: LightRAG | None = None,
    rag_kg3: LightRAG | None = None,
    contract_code: str | None = None,
    invariants: str | None = None
):
    try:
        # 分析过程不变
        if kg_choice == "kg1":
            analysis_result = execute_query(
                query=contract_code, 
                kg_choice=kg_choice, 
                search_mode=search_mode, 
                only_context=False,
                rag_kg1=rag_kg1
            )
        elif kg_choice == "kg2":
            analysis_result = execute_query(
                query=contract_code, 
                kg_choice=kg_choice, 
                search_mode=search_mode, 
                only_context=False,
                rag_kg2=rag_kg2
            )
        elif kg_choice == "double":
            kg1_context, kg2_context = execute_query(
                query=contract_code, 
                kg_choice=kg_choice, 
                search_mode=search_mode, 
                only_context=True,
                rag_kg1=rag_kg1,
                rag_kg2=rag_kg2
            )
            analysis_result = rag_kg3.query(
                contract_code, kg1_context, kg2_context, param=QueryParam(Strategy="double")
            )

        return {
            "contract_code": contract_code,
            "invariants": invariants,
            "analysis_result": str(analysis_result),
            "kg_choice": kg_choice,
            "search_mode": search_mode
        }

    except Exception as e:
        logging.error(f"Error processing contract: {str(e)}")
        return {
            "contract_code": contract_code,
            "error": str(e),
            "kg_choice": kg_choice,
            "search_mode": search_mode
        }

def execute_query(
    query: str,
    kg_choice: KGChoice,
    search_mode: SearchMode,
    only_context: bool = False,
    rag_kg1: LightRAG | None = None,
    rag_kg2: LightRAG | None = None,
) -> Tuple[str, str] | str:
    """
    执行多知识库查询的封装函数
    
    参数:
        rag_kg1: kg1的RAG实例
        rag_kg2: kg2的RAG实例
        query: 查询文本
        kg_choice: 知识库选择 ("kg1"|"kg2"|"double")
        search_mode: 搜索模式 ("naive"|"local"|"global"|"hybrid")
        only_context: 是否只返回上下文
    
    返回:
        如果是double模式返回元组(context_kg1, context_kg2)
        否则返回单个结果字符串
    """

    param = QueryParam(mode=search_mode, only_need_context=only_context)
    if kg_choice == "kg1":
        result = rag_kg1.query(query, param=param)
        return str(result)
        
    elif kg_choice == "kg2":
        result = rag_kg2.query(query, param=param)
        return str(result)
        
    elif kg_choice == "double":
        context_kg1 =rag_kg1.query(query, param=param, kg_number=1)
        context_kg2 =rag_kg2.query(query, param=param, kg_number=2)
        return (str(context_kg1), str(context_kg2))
    
    else:
        raise ValueError(f"无效的知识库选择: {kg_choice}")

# def print_query_result(
#     rag_kg1: LightRAG,
#     rag_kg2: LightRAG,
#     query: str,
#     kg_choice: KGChoice,
#     search_mode: SearchMode
# ):
#     """
#     打印格式化查询结果
    
#     参数同execute_query
#     """
#     print(f"\n{search_mode.capitalize()} Search_{kg_choice}:")
    
#     if kg_choice == "double":
#         print("\n-----------------context_kg1-------------------\n")
#         context_kg1, context_kg2 = execute_query(
#             rag_kg1, rag_kg2, query, kg_choice, search_mode, True
#         )
#         # print(context_kg1)
#         print("context_kg1 finished\n")
        
#         print("\n-----------------context_kg2-------------------\n")
#         # print(context_kg2)
#         print("context_kg12 finished\n")
#         return context_kg1, context_kg2
#     else:
#         result = execute_query(rag_kg1, rag_kg2, query, kg_choice, search_mode)
#         print(result)
#         return 0,0

def save_results(results: List[Dict], output_file: str, mode: str = 'a'):
    """Save results to JSON file with specified mode"""
    try:
        with open(output_file, mode, encoding='utf-8') as f:
            if mode == 'a' and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                f.write(",\n")  # Add comma for JSON array continuation
            json.dump(results, f, indent=2, ensure_ascii=False)
            if mode == 'w':
                f.write("\n")  # Newline for the first write
    except Exception as e:
        logging.error(f"Error saving results: {str(e)}")

def main():
    kg_choice = "double"
    search_mode = "hybrid"
    
    # 加载 JSON 数据（包含合约代码）
    with open(SET_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if kg_choice == "double":
        rag_kg1 = asyncio.run(initialize_rag_kg1("KG1"))
        rag_kg2 = asyncio.run(initialize_rag_kg2("KG2"))
        rag_kg3 = asyncio.run(initialize_rag_kg3("KG3"))
    elif kg_choice == "kg1":
        rag_kg1 = asyncio.run(initialize_rag_kg1("KG1"))
    elif kg_choice == "kg2":
        rag_kg2 = asyncio.run(initialize_rag_kg2("KG2"))

    batch_results = []
    processed_count = 0
    for i, item in enumerate(data):
        contract_code = item.get("code", "")
        invariants = item.get("invariants", "")
        if not contract_code.strip():
            continue  # 跳过空内容

        logging.info(f"Processing {i+1}/{len(data)}")

        if kg_choice == "double":
            result = asyncio.run(process_contract(
                kg_choice=kg_choice,
                search_mode=search_mode,
                rag_kg1=rag_kg1,
                rag_kg2=rag_kg2,
                rag_kg3=rag_kg3,
                contract_code=contract_code,
                invariants=invariants
            ))
        elif kg_choice == "kg1":
            result = asyncio.run(process_contract(
                kg_choice=kg_choice,
                search_mode=search_mode,
                rag_kg1=rag_kg1,
                contract_code=contract_code,
                invariants=invariants
            ))
        elif kg_choice == "kg2":
            result = asyncio.run(process_contract(
                kg_choice=kg_choice,
                search_mode=search_mode,
                rag_kg2=rag_kg2,
                contract_code=contract_code,
                invariants=invariants
            ))

        # 添加原始 code 内容以及分析结果
        batch_results.append(result)

        processed_count += 1
        if processed_count % BATCH_SIZE == 0:
            save_results(batch_results, OUTPUT_FILE, 'a' if i > BATCH_SIZE else 'w')
            batch_results = []

    if batch_results:
        save_results(batch_results, OUTPUT_FILE, 'a')

    with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
        f.write("\n]")

    logging.info(f"Analysis completed. Processed {processed_count} contracts. Results saved to {OUTPUT_FILE}")
    if kg_choice == "double":
        print("Clearing caches for all knowledge bases...")
        rag_kg1.clear_cache()
        rag_kg2.clear_cache()
        rag_kg3.clear_cache()
    elif kg_choice == "kg1":
        rag_kg1.clear_cache()
    elif kg_choice == "kg2":
        rag_kg2.clear_cache()

if __name__ == "__main__":
    main()

