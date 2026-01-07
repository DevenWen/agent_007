# prd 0.0.3

## user story
1. 增加一个抽象 Skill, 给它定义 RESTFUL 接口。但它不存数据库，是从 backend 的 prompt/skill 目录中读取的。一个文件一个 skill.
    1.1 SKILL.md 文件中定义了工作的流程，以及调用的工具。它本质上是一个 prompt
    1.2 它是一个 markdown 文件，因此前端渲染这个文件的时候，需要解析 markdown 文件，然后渲染成 html
    1.3 这个 markdown 必须要定义 head 
    ```
    - name: 
    - description: 
    - tools: 
    ```
2. 增加一个 agent crud 能力。支持以下能力
    2.1 指定 agent 的 skill
    2.2 指定 agent 的 name
    2.3 指定 agent 的 description
    2.4 指定 agent 的 tools
    2.5 指定 agent 的 max_iterations
    2.6 指定 agent 的 prompt，其中 prompt 支持 jinja 的占位符模板，可以通过 agent 的 param 来填充
    2.7 指定 agent 的 param (非必填)

3. 增加 ticket 创建能力
    3.1 支持选择 ticket 的 agent
    3.2 选择 agent 后，就需要根据 agent 的 param 定义，填充必要的参数，进行 ticket 创建

4. 添加一个 system prompt 的定义，通过一个 markdown 文件来定义，这个定义在 prompt/system_prompt.md 目录下；


## 技术优化 & bugfix
1. ticket 完成后，它有一个 step 没有完成。分析一下是不是 system prompt 的问题；
2. ticket 进行 Reset 后，需要清空里面的 step，再重新开始；
3. 前端页面创建 ticket 时会失败，无法选择 agent；
4. tools 的 id 就是它的 name，不需要使用 uuid 作为 id，这样无法在 skill 中定义；
