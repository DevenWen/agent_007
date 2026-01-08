# prd 0.0.3

## user story
1. session 中显示的对话信息中没有带上 thinking 的信息。支持 session 的 message 中带有 thinking 信息。thinking 信息通过 <thinking /> 标签进行定义。
2. 【FIXED】ticket 执行过程中。step 没有被逐步完成，分析原因。是否是因为系统的 tool 没有支持创建步骤
3. agent 创建页面中，没有支持定义参数。定义参数包括：
    3.1 field_name, type, description, default_value, required 
    3.2 最后转换成 json_schema 保存到 agent 中
4. 创建 ticket 的时候，表单需要根据 agent 的 json_schema 进行表单渲染
5. agent 需要定义输出。输出包括：json_format, text

## 技术优化
1. 【FIXED】解决 anthropic 的 API 调用问题，
    1.1 为什么 minimax 的 API 调用会错误？
    1.2 glm 的 API 也会调用错误？