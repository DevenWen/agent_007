import { useState, useEffect } from 'react'
import { api } from '../api/client'

export default function ToolsPage() {
    const [tools, setTools] = useState([])
    const [loading, setLoading] = useState(true)
    const [selectedTool, setSelectedTool] = useState(null)

    useEffect(() => {
        loadTools()
    }, [])

    const loadTools = async () => {
        try {
            const data = await api.listTools()
            setTools(data)
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return <div className="flex items-center justify-center h-64 text-slate-400">Loading...</div>
    }

    return (
        <div className="flex gap-6">
            {/* Tool List */}
            <div className="flex-1 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {tools.map(tool => (
                    <div
                        key={tool.id}
                        onClick={() => setSelectedTool(tool)}
                        className={`bg-slate-800 rounded-xl p-5 border cursor-pointer transition ${selectedTool?.id === tool.id
                                ? 'border-indigo-500'
                                : 'border-slate-700 hover:border-slate-600'
                            }`}
                    >
                        <div className="flex items-center gap-3 mb-3">
                            <div className="w-10 h-10 rounded-lg bg-slate-700 flex items-center justify-center text-lg">
                                🔧
                            </div>
                            <h3 className="font-semibold font-mono">{tool.name}</h3>
                        </div>
                        <p className="text-sm text-slate-400">{tool.description}</p>
                    </div>
                ))}
            </div>

            {/* Detail Panel */}
            {selectedTool && (
                <div className="w-96 bg-slate-800 rounded-xl border border-slate-700 p-4 space-y-4">
                    <div className="flex items-center justify-between">
                        <h3 className="font-semibold font-mono">{selectedTool.name}</h3>
                        <button onClick={() => setSelectedTool(null)} className="text-slate-400 hover:text-white">✕</button>
                    </div>

                    <div>
                        <h4 className="text-sm font-medium text-slate-400 mb-2">Description</h4>
                        <p className="text-sm">{selectedTool.description}</p>
                    </div>

                    <div>
                        <h4 className="text-sm font-medium text-slate-400 mb-2">Input Schema</h4>
                        <pre className="bg-slate-900 rounded p-3 text-xs overflow-x-auto">
                            {JSON.stringify(selectedTool.schema_, null, 2)}
                        </pre>
                    </div>
                </div>
            )}
        </div>
    )
}
