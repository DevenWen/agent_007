import React, { useState, useEffect } from "react";
import DynamicForm from "./DynamicForm";

export default function CreateTicketModal({ isOpen, onClose, onCreated }) {
    const [agents, setAgents] = useState([]);
    const [selectedAgentId, setSelectedAgentId] = useState("");
    const [params, setParams] = useState({});
    const [context, setContext] = useState("{}");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    // Fetch agents on mount/open
    useEffect(() => {
        if (isOpen) {
            fetchAgents();
            // Reset state
            setSelectedAgentId("");
            setParams({});
            setContext("{}");
            setError(null);
        }
    }, [isOpen]);

    const fetchAgents = async () => {
        try {
            const res = await fetch("http://localhost:8000/api/v1/agents");
            if (!res.ok) throw new Error("Failed to fetch agents");
            const data = await res.json();
            setAgents(data);
        } catch (err) {
            console.error(err);
            setError("Failed to load agents");
        }
    };

    const selectedAgent = agents.find((a) => a.id === selectedAgentId);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            let parsedContext = {};
            try {
                parsedContext = JSON.parse(context);
            } catch (err) {
                throw new Error("Invalid Context JSON");
            }

            // 如果没有 schema，params 可能是通过 raw textarea 输入的（这里暂未实现 raw input fallback for params, assume schema exists or empty）
            // 如果 user story 要求无 schema 回退：
            // "JSON Fallback: If an agent has no params_schema, a JSON text area is provided"

            let finalParams = params;
            if (!selectedAgent?.params_schema) {
                // 如果没有 schema，params 应该是一个 JSON string，需要解析
                // 这里我们需要一个 raw params input
                // 为了简化，我们暂时复用 context 的逻辑或者 params state 当作 string
                if (typeof params === 'string') {
                    try {
                        finalParams = JSON.parse(params);
                    } catch (e) {
                        throw new Error("Invalid Params JSON");
                    }
                }
            }

            const res = await fetch("http://localhost:8000/api/v1/tickets", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    agent_id: selectedAgentId,
                    params: finalParams,
                    context: parsedContext,
                }),
            });

            if (!res.ok) {
                const errData = await res.json();
                throw new Error(errData.detail || "Failed to create ticket");
            }

            const newTicket = await res.json();
            onCreated(newTicket);
            onClose();
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
                <div className="fixed inset-0 transition-opacity" aria-hidden="true">
                    <div className="absolute inset-0 bg-gray-500 opacity-75" onClick={onClose}></div>
                </div>

                <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">
                    &#8203;
                </span>

                <div className="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                    <div className="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                        <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white" id="modal-title">
                            Create New Ticket
                        </h3>

                        {error && (
                            <div className="mt-2 p-2 bg-red-50 text-red-700 text-sm rounded">
                                {error}
                            </div>
                        )}

                        <form onSubmit={handleSubmit} className="mt-4 space-y-4">
                            {/* Agent Selection */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                    Select Agent
                                </label>
                                <select
                                    value={selectedAgentId}
                                    onChange={(e) => {
                                        setSelectedAgentId(e.target.value);
                                        setParams({}); // reset params
                                    }}
                                    className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                    required
                                >
                                    <option value="">-- Choose an Agent --</option>
                                    {agents.map((agent) => (
                                        <option key={agent.id} value={agent.id}>
                                            {agent.name}
                                        </option>
                                    ))}
                                </select>
                            </div>

                            {selectedAgent && (
                                <>
                                    {/* Dynamic Params Form */}
                                    <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                                        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-2">
                                            Task Parameters
                                        </h4>
                                        {selectedAgent.params_schema ? (
                                            <DynamicForm
                                                schema={selectedAgent.params_schema}
                                                value={params}
                                                onChange={setParams}
                                            />
                                        ) : (
                                            <div>
                                                <div className="bg-yellow-50 text-yellow-800 text-xs p-2 rounded mb-2">
                                                    This agent has no parameter schema. Please input JSON manually.
                                                </div>
                                                <textarea
                                                    value={typeof params === 'string' ? params : JSON.stringify(params, null, 2)}
                                                    onChange={(e) => setParams(e.target.value)}
                                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white font-mono"
                                                    rows={4}
                                                    placeholder="{}"
                                                />
                                            </div>
                                        )}
                                    </div>

                                    {/* Context Input */}
                                    <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
                                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                                            Additional Context (JSON)
                                        </label>
                                        <textarea
                                            value={context}
                                            onChange={(e) => setContext(e.target.value)}
                                            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white font-mono"
                                            rows={3}
                                        />
                                    </div>
                                </>
                            )}

                            <div className="mt-5 sm:mt-6 sm:grid sm:grid-cols-2 sm:gap-3 sm:grid-flow-row-dense">
                                <button
                                    type="submit"
                                    disabled={loading || !selectedAgentId}
                                    className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:col-start-2 sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {loading ? "Creating..." : "Create Ticket"}
                                </button>
                                <button
                                    type="button"
                                    onClick={onClose}
                                    className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:col-start-1 sm:text-sm dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:hover:bg-gray-600"
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
}
