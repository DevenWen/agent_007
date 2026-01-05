import { useState, useEffect } from 'react'
import { api } from '../api/client'

export default function AgentsPage() {
    const [agents, setAgents] = useState([])
    const [loading, setLoading] = useState(true)
    const [selectedAgent, setSelectedAgent] = useState(null)

    useEffect(() => {
        loadAgents()
    }, [])

    const loadAgents = async () => {
        try {
            const data = await api.listAgents()
            setAgents(data)
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const loadAgentDetail = async (id) => {
        try {
            const data = await api.getAgent(id)
            setSelectedAgent(data)
        } catch (err) {
            console.error(err)
        }
    }

    if (loading) {
        return <div className="flex items-center justify-center h-64 text-slate-400">Loading...</div>
    }

    return (
        <div className="flex gap-6">
            {/* Agent List */}
            <div className="flex-1 grid gap-4 md:grid-cols-2">
                {agents.length === 0 ? (
                    <div className="text-center py-12 text-slate-400 col-span-2">
                        No agents configured.
                    </div>
                ) : (
                    agents.map(agent => (
                        <div
                            key={agent.id}
                            onClick={() => loadAgentDetail(agent.id)}
                            className={`bg-slate-800 rounded-xl p-5 border cursor-pointer transition ${selectedAgent?.id === agent.id
                                ? 'border-indigo-500'
                                : 'border-slate-700 hover:border-slate-600'
                                }`}
                        >
                            <div className="flex items-center gap-3 mb-3">
                                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-lg">
                                    🧠
                                </div>
                                <h3 className="font-semibold">{agent.name}</h3>
                            </div>
                            <p className="text-sm text-slate-400 line-clamp-2">{agent.description || 'No description'}</p>
                        </div>
                    ))
                )}
            </div>

            {/* Detail Panel */}
            {selectedAgent && (
                <div className="w-96 bg-slate-800 rounded-xl border border-slate-700 p-4 space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="font-semibold">{selectedAgent.name}</h3>
                        <button onClick={() => setSelectedAgent(null)} className="text-slate-400 hover:text-white">✕</button>
                    </div>

                    {selectedAgent.description && (
                        <div>
                            <h4 className="text-sm font-medium text-slate-400 mb-2">Description</h4>
                            <p className="text-sm">{selectedAgent.description}</p>
                        </div>
                    )}

                    <div>
                        <h4 className="text-sm font-medium text-slate-400 mb-2">System Prompt</h4>
                        <pre className="bg-slate-900 rounded p-3 text-sm whitespace-pre-wrap max-h-48 overflow-y-auto scroll-area">
                            {selectedAgent.prompt}
                        </pre>
                    </div>

                    {(selectedAgent.tools?.length > 0 || selectedAgent.tool_ids?.length > 0) && (
                        <div>
                            <h4 className="text-sm font-medium text-slate-400 mb-2">
                                Tools ({selectedAgent.tools?.length || selectedAgent.tool_ids?.length})
                            </h4>
                            <div className="flex flex-wrap gap-2">
                                {selectedAgent.tools ? (
                                    selectedAgent.tools.map(tool => (
                                        <span key={tool.id} className="px-2 py-1 bg-slate-700 rounded text-xs" title={tool.description}>
                                            🔧 {tool.name}
                                        </span>
                                    ))
                                ) : (
                                    selectedAgent.tool_ids.map(id => (
                                        <span key={id} className="px-2 py-1 bg-slate-700 rounded text-xs">
                                            🔧 {id.replace('tool-', '')}
                                        </span>
                                    ))
                                )}
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
