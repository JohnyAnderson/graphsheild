import json
import requests

OLLAMA_MODEL = 'qwen2.5:7b'
OLLAMA_URL = 'http://localhost:11434/api/generate'

def call_ollama(prompt: str) -> str:
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    return response.json()["response"].strip()

def evaluate_analysis_with_model(data_item):
    bug_description = data_item["bug_description"].strip()
    analysis_result = data_item["analysis_result"].strip()

    # Prompt 编写，明确任务
    prompt = f"""
你是一个智能合约审计专家。请根据以下规则判断 analysis_result 中的 bug 描述是否覆盖了 bug_description 中提到的内容：

规则如下：
- 如果 bug_description 是none，无论 analysis_result 的内容是什么都输出 "correct"
- 如果 analysis_result 中的"Potential Vulnerabilities"部分的提到的漏洞问题涉及了 bug_description 中的全部bug类型，则输出 "correct"
- 如果 analysis_result 中的"Potential Vulnerabilities"部分的提到的漏洞问题涉及了部分 bug_description 中提到的bug类型（即只提到了其中部分），输出 "partly correct"
- 如果 analysis_result 中的"Potential Vulnerabilities"部分的提到的漏洞问题和 bug_description 中的bug一点也不涉及，则输出 "worry"
- 只要 analysis_result 中的"Potential Vulnerabilities"部分的提到的漏洞问题和bug_description 中的bug有一点可能为能的关联，就认为是涉及了。

相关背景知识：
​1.​特权升级​​(Privilege Escalation)	
漏洞成因：权限检查缺失或逻辑错误，使攻击者能越权调用敏感函数	
2.​​状态更新不一致​​(Inconsistent State Update)	
漏洞成因：多步操作中部分成功，导致合约状态与预期不符
​3.​原子性违规​​(Atomicity Violation)
漏洞成因：本应原子执行的操作被意外中断或分割	
​4.​跨链桥不一致​​(Cross-Bridge Inconsistency)	
漏洞成因：跨链消息验证失败或状态同步延迟
​5.​业务逻辑漏洞​​(Business Logic Flaw)	
漏洞成因：合约逻辑设计缺陷，违反业务预期
​6.​价格操纵​​(Price Manipulation)	
漏洞成因：预言机或定价机制依赖可操纵数据源

分析思路示例：
bug_description:
privilege escalation\ninconsistent state update\natomicity violation\n
analysis_result:
### Contract Structure\n\nThe `ExampleSlidingWindowOracle` contract is a custom sliding window oracle designed to provide moving average price calculations in Uniswap V2 pairs. It uses historical price observations stored over a specified period (`windowSize`) with a granularity determined by the `granularity` parameter. The contract supports the computation of prices based on cumulative price data and implements several key functions for updating and querying these prices.\n\n### Key Invariants\n\n1. **Observation Timestamps**: Observations are recorded at regular intervals defined by `periodSize`, ensuring consistent updates.\n2. **Price Calculation Consistency**: Prices are calculated using a sliding window approach, ensuring they reflect the average price over the specified period.\n3. **Historical Observation Validity Check**: Before computing the amount out, it checks that the historical observation is within the valid time range.\n\n### Potential Vulnerabilities\n\n1. **Time Manipulation**: The contract relies on `block.timestamp` for generating timestamps and updating observations. Malicious actors could manipulate timestamp values to alter price calculations.\n2. **Cumulative Price Overflows**: While overflow handling is managed through fixed-point arithmetic, care must be taken to ensure that cumulative price updates do not cause overflows or underflows.\n\n### Reference Sources\n\n1. **SafeMath Library** (KG): Used for safe arithmetic operations to prevent overflows and underflows.\n2. **UniswapV2Library** (KG): Provides utility functions to interact with Uniswap V2 pairs, such as sorting tokens and fetching cumulative prices.\n3. **FixedPoint Library** (KG): Supports fixed-point arithmetic for precise price calculations.\n4. **UniswapV2OracleLibrary** (KG): Offers methods to retrieve current cumulative prices from Uniswap V2 pairs.\n5. **Pair For Function in Uniswap V2 Core** (KG): Identifies the correct pair address for a given token pair.\n\nThis contract is designed to provide accurate and reliable price data by leveraging historical observations over a defined period, making it suitable for scenarios requiring more precise pricing information than simple oracles can offer.
1. 漏洞定义解析
（1）特权升级（Privilege Escalation）
​​定义​​：攻击者通过非法手段获取超出其权限级别的系统控制权。
​​典型表现​​：未经验证调用管理员函数、权限检查逻辑存在时间依赖性漏洞、函数可见性设置错误（如误设public而非private）
（2）状态更新不一致（Inconsistent State Update）
​​定义​​：合约状态在多步骤操作中未保持完整性和一致性。
​​关键特征​​：部分操作成功导致脏数据、未遵循Checks-Effects-Interactions模式、重入攻击引发的状态混乱
（3）原子性违规（Atomicity Violation）
​​定义​​：本应原子化执行的操作被意外中断或分割。
​​常见场景​​：、跨合约调用间发生交易回滚、闪电贷攻击中的中间状态暴露、未使用reentrancy guard的重入问题
2. 漏洞关联分析
（1）时间操纵 → 特权升级
​​传导路径​​：时间戳篡改 → 时间敏感权限检查失效 → 非法获取特权
​​实例场景​​：若合约使用block.timestamp作为权限过期检查依据（如require(block.timestamp < adminExpireTime)），攻击者通过操纵时间戳可使本应过期的权限持续有效。

（2）累积价格溢出 → 状态更新不一致
​​传导路径​​：算术溢出 → 价格状态异常 → 依赖该状态的所有功能失效
​​典型表现​​：溢出导致预言机价格变为极大值/极小值、清算模块基于错误价格触发错误清算、准备金计算出现负数导致合约锁死
（3）共同诱发原子性违规
故为correct

请只输出一个词作为结果：correct / partly correct / worry

以下是内容：
bug_description:
{bug_description}

analysis_result:
{analysis_result}
    """.strip()

    result = call_ollama(prompt).lower()
    print("result:\n",result)

    result = result.split()[0]  # 只取第一个词，防止额外解释

    # 限定输出值
    if result not in ["correct", "partly", "worry"]:
        result = "worry"
    if result == "partly":
        result = "partly correct"

    return result

def evaluate_all_contracts(json_file_path):

    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for item in data:
        result = evaluate_analysis_with_model(item)
        item["evaluation_result"] = result

    with open(json_file_path.replace(".json", "_evaluated.json"), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return data

if __name__ == "__main__":
    json_file_path = "../../result/test.json"
    evaluated_data = evaluate_all_contracts(json_file_path)
    print("Evaluation completed. Results saved to:", json_file_path.replace(".json", "_evaluated.json"))
    for item in evaluated_data:
        print(f"Bug Description: {item['bug_description']}, Evaluation Result: {item['evaluation_result']}")