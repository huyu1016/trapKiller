<style>
h1 {
    border-bottom: none
}
h2 {
    border-bottom: none
}
</style>
# solc AST

- `exportedSymbols` 记录所有组件(contract library)对应的id
所有合约以及他们对应的id 
```
    "exportedSymbols" : 
	{
		"father" :  合约或者library名字
		[
			24      在nodes中对应的id
		],
		"test" : 
		[
			44
		],
		"test1" : 
		[
			55
		]
	},
```
- `nodes` 记录每个合约的详细信息(solidity版本信息，合约详细信息)
    - `"nodeType" : "ContractDefinition"` 类型必须为合约定义
    - `"id" : 24`  上面部分对应的id 
    - `"contractDependencies" : []`  合约依赖 第一步判断的重要条件
    - `nodes` 进一步分析所需要的信息 函数信息 变量信息
        - `"nodeType" : "FunctionDefinition"`  类型必须是函数定义
        - `"payable" : true` payable 必须为true
          - `"body"` 包含函数体的关键信息
            - `"statements"` 程序语句类型(顺序 选择 循环)
              -  `IfStatement` 选择
                 - `trueBody` >>>> 递归执行里面的statement
                 - `falseBody` >>>> 递归执行里面的statement
              -  `ForStatement` 循环 >>>> 递归执行里面的statement
              -  `WhileStatement` 循环 >>>> 递归执行里面的statement
              -  `ExpressionStatement` 顺序执行里面的表达式 转账函数的调用只有可能发生在这里
                - `"expression"` 表达式字段
                  - `"nodeType" : "FunctionCall"`  必须为函数调用
                    - `"expression"`
                      - `"nodeType" : "MemberAccess"` .send .call.value .transfer 都是成员函数访问
                      - `"memberName" : "send"` 访问的成员函数的名字 必须为send transfer value 检测完成