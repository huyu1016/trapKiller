<style>
h1 {
    border-bottom: none
}
h2 {
    border-bottom: none
}
</style>

# review 整理  
|  **review内容**  | **类型** | **建议** | **个人意见** |
|  ----  | ----  | ----  | ----  |
| **Listing 1 take lot of space**  | **写作** | `prefer figures and listing on top of the page and not in text` |`无` |
| **the word 'backdoor' definition is too strong**  | **写作** | `use another term instead of 'backdoor'` |
| **In Subsection 4.1 and Subsection 4.3, the use of a by-product CFG is not motivated**  | **写作** | `add some text` |`无` |
| **In Subsection 4.2, the claim "DefectChecker is much faster and more accurate than them" is not supported by any evidence**  | **写作** | `add a reference` |`无` |
| **In Subsection 4.2 DeFiDefender performs symbolic execution by using DefectChecker and that the latter only supports solc version 0.4.25, but then  say that DeFiDefender supports solc version up-to version 0.8.12**  | **写作+实验** | `clarify` |`描述自动化脚本 实现方式？` |
| **In Subsection 4.4, all equations are not well-formed**  | **写作** | `to explain the DCTs simply by words or to replace equations with pictures` |`无` |
| **In Section 5, the evaluation should follow the classic pattern consisting in RQ and Answer**  | **写作** | `更改类型为RQ和Answer的方式 ` |`无` |
| **In Subsection 5.2, the ground truth for the first experiment has been provided by the authors, it is definitely not a good practice**  | **实验** | `using a ground truth defined by external collaborators` |`使用第三方的数据集？` |
| **In Subsection 5.2, a demographics (reporting smart-contracts information like loc, solc version, etc.) of the dataset would be helpful. Furthermore, the average size of the considered smart-contracts seems small**  | **实验** | `列出数据集特征 扩大数据集数量` |`关键点在于新的label数据集如何获取 分析数据集特征比较容易` |
| **In Subsection 5.2, you consider DeFi-related smart-contracts only, but I do not see why**  | **写作** | `给出解释` |`paper已经给出了解释 不知道是否需要进一步阐明` |
| **In Subsection 5.4, please summarize the results of the experiment at the end.**  | **写作** | `总结` |`无` |
| **In Subsection 5.5, looking at the results of the second experiment it seems to me quite unlikely that half of the considered smart-contracts contain DCTs, this means that half of DeFi apps out there can be considered malicious, or, perhaps, that your approach produces too much false positives. Please comment on that.**  | **实验+写作** | `结果解释` | `结果不太可能 需要调整实验结果还是通过writing 让结果能讲通？ 但好像paper后面有解释` |
| **In Subsection 6.4, as also you point out, some DCTs (like TS and SP) are just known smart-contracts vulnerabilities with additional (little) constraints. One may ask why we cannot just use state-of-the-art vulnerability detection tools instead of DeFiDefender**  | **实验** | `make a comparison between vulnerability detection tools and DeFiDefendern` |`做实验去评估` |
| **Section 3.1: The first sentence is hard to understand.**  | **写作** | `修改表达` |`无` |
| **Section 4.2: This is an almost identical repetition from section 2.3**  | **写作** | `different example` |`无` |
| **Section 4.2: What does "millions of contacts of Ethereum are compiled using different compiler versions" mean?**  | **写作** | `进一步说明` |`无` |
| **Section 4.3 Instruction a is read by Instruction b**  | **写作** | `修改表达` |`无` |
| **Section 4.4 "contract call graph" is different from a regular call graph or just use the word call graph**  | **写作** | `修改表达` |`换了新的实现方式 是否需要详细说明？` |
| **Section 5.1: smart contracts should be specified to "Ethereum smart contracts" or something similar**  | **写作** | `无` |`有点无理取闹了` |
| **Section 5.2: What does "verified" in that context mean? Please provide a definition in the manuscript**  | **写作** | `给一个定义` |`这里的验证是什么意思？` |
| **Section 5.4: The limited number of false positives and false negatives for the first trap opens the possibility to discuss them in detail to give more insight into the approach.**  | **写作** | `给出解释` |`这个很好解释 就是单纯的这个模式好检测` |
| **Table 4: # Percentage appears to be wrong**  | **写作** | `use "Frequency"` |`无` |
| **Section 5.4：The presented number of true positives (26) does not match the number from Table 3 and also does not make sense inside the section.**  | **写作** | `排印错误` |`无` |
| **Section 5.5, paragraph 3: The presented data might be better presented in a diagram or table.**  | **写作** | `presented in a diagram or table` |`无` |
| **Section 6.5: What does "improve the performance" mean? How can these steps reduce the bias?**  | **写作或实验？** | `具体说明` |`无` |

