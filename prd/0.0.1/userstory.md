# prd 0.0.1

## user story

- 我需要一个 agent 平台，这个平台有以下核心实体：agent、ticket
- ticket 是任务的载体，定义了任务的状态，参数，上下文，子步骤
- agent 是任务的执行者，主要的智力推导实体，当 ticket 进入可运行状态时，主循环会将 ticket 派发给指定的 agent
    - agent 执行一个任务时的过程，叫做 session，session 有状态，有上下文，有记忆
    - agent 需要外部的 tools 来完成任务，这里的 tools 初期可以进行 hardcode 到代码中
    - agent 在遇到需要人力介入的时候，会将 ticket 转入挂起状态，等待人工做信息输入
    - agent 在执行任务的时候，子步骤完成时，需要主动更新给 ticket

- 这个平台我需要一个简单的管理界面
    - 左侧是管理栏，不同的实体有不同的管理界面
    - 右侧是工作台，
    - ticket 界面中，我可以观察到 ticket 的状态，也可以跳转其所在的 session，观察其输出的 log 
    - agent 界面中，我可以看到 agent 的介绍，prompt、可以调用的 tools
    - session 界面中，我可以看到 session 的状态、上下文、记忆，也可以在完成人工介入
    - tools 界面中，我可以看到 tools 的介绍

- 项目技术选型：
    - 前端：react router + tailwindcss
    - 后端：python + fastapi
    - 数据库：sqlite
    - llm：claude_agent_sdk