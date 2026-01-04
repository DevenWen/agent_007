# Agent Platform - Quick Start Guide

从零开始运行 Agent Platform MVP。

## 前置要求

- **Python 3.11+** 
- **Node.js 18+**
- **uv** (Python 包管理器)

```bash
# 安装 uv (如果没有)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## 1. 克隆仓库

```bash
git clone <repo-url> agent_007
cd agent_007
```

---

## 2. 启动后端

```bash
cd backend

# 安装依赖
uv sync

# 配置环境变量 (二选一)

# 方式 A: 直接使用 Anthropic API
export ANTHROPIC_API_KEY=your-anthropic-api-key

# 方式 B: 使用代理服务 (如 MiniMax)
export ANTHROPIC_API_KEY=your-proxy-key
export ANTHROPIC_BASE_URL=https://your-proxy-url
export ANTHROPIC_MODEL=your-model-name

# 启动服务器
uv run uvicorn app.main:app --reload --port 8000
```

✅ 验证: 访问 http://localhost:8000/health 应返回 `{"status":"ok"}`

---

## 3. 启动前端

打开**新终端**:

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

✅ 验证: 访问 http://localhost:5173 应看到管理界面

---

## 4. 创建第一个 Agent

通过 API 创建测试 Agent:

```bash
curl -X POST http://localhost:8000/api/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Hello Agent",
    "prompt": "你是一个友好的助手。当用户给你任务时，先用 add_step 添加步骤，完成后调用 complete_task。",
    "tool_ids": ["tool-read-file", "tool-write-file", "tool-exec-cmd"]
  }'
```

---

## 5. 创建 Ticket 测试

```bash
# 获取刚创建的 Agent ID
AGENT_ID=$(curl -s http://localhost:8000/api/agents | jq -r '.[0].id')

# 创建 Ticket
curl -X POST http://localhost:8000/api/tickets \
  -H "Content-Type: application/json" \
  -d "{
    \"agent_id\": \"$AGENT_ID\",
    \"params\": {\"task\": \"say hello\"},
    \"context\": {\"goal\": \"Test the agent\"}
  }"
```

Ticket 创建后，调度器会自动派发给 Agent 执行。

---

## 6. 观察执行

在前端界面 (http://localhost:5173):

1. 点击 **Tickets** 查看任务列表
2. 点击某个 Ticket 查看详情
3. 观察 Status 变化: `pending` → `running` → `completed`/`failed`
4. 点击 **Sessions** 查看对话历史

---

## 项目结构

```
agent_007/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── models/   # ORM 模型
│   │   ├── routers/  # API 路由
│   │   ├── scheduler/# 调度器
│   │   └── tools/    # 内置工具
│   └── data/         # SQLite 数据库
├── frontend/         # React 前端
└── doc/              # 文档
```

---

## 常见问题

### Q: Claude API 返回 500 错误?
可能是代理服务问题，检查 `ANTHROPIC_BASE_URL` 和模型名称是否正确。

### Q: Ticket 一直是 pending 状态?
调度器每 2 秒轮询一次，等待几秒后刷新页面。

### Q: 如何重置数据库?
```bash
rm backend/data/agent_platform.db
# 重启后端会自动重建
```
