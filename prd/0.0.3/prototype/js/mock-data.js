// Mock Data for v0.0.3

const mockData = {
    skills: [
        {
            name: "code_reviewer",
            description: "Review code changes for security and style issues",
            tools: ["read_file", "search_code", "http_request"],
            content: "You are a code reviewer. Check for: 1. Security... 2. Style..."
        },
        {
            name: "data_analyst",
            description: "Analyze datasets and produce reports",
            tools: ["read_file", "python_interpreter"],
            content: "You are a data analyst. Use python to analyze..."
        }
    ],
    agents: [
        {
            id: "agent-001",
            name: "Security Auditor",
            description: "Code review agent focused on security",
            skillName: "code_reviewer",
            maxIterations: 10,
            defaultParams: {
                repository: "https://github.com/example/repo",
                branch: "main"
            },
            toolNames: ["read_file", "search_code", "http_request", "jira_ticket_create"],
            paramsSchema: {
                type: "object",
                properties: {
                    repository: { type: "string", description: "Repo URL" },
                    branch: { type: "string", description: "Branch name" },
                    scan_depth: { type: "integer", default: 1, minimum: 1, maximum: 3 }
                },
                required: ["repository", "branch"]
            },
            prompt: "Override: Focus ONLY on SQL Injection.",
            created_at: "2024-01-20T10:00:00Z"
        },
        {
            id: "agent-002",
            name: "Sales Analyst",
            description: "Monthly sales report generator",
            skillName: "data_analyst",
            maxIterations: 20,
            defaultParams: {
                year: 2024
            },
            toolNames: ["read_file", "python_interpreter"],
            paramsSchema: {
                type: "object",
                properties: {
                    year: { type: "integer" },
                    month: { type: "integer" }
                },
                required: ["year", "month"]
            },
            created_at: "2024-01-21T09:00:00Z"
        }
    ],
    tickets: [
        {
            id: "ticket-101",
            status: "running",
            agentId: "agent-001",
            agentName: "Security Auditor",
            params: { repository: "https://github.com/example/auth", branch: "dev", scan_depth: 2 },
            context: { goal: "Audit auth module" },
            steps: [
                { title: "Clone Repo", status: "completed" },
                { title: "Scan Files", status: "running", result: "Scanning 45 files..." }
            ],
            createdAt: "2024-01-22T08:00:00Z",
            updatedAt: "2024-01-22T08:05:00Z"
        }
    ]
};
