import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'
import StatusBadge from '../components/StatusBadge'
import AutoRefreshControl from '../components/AutoRefreshControl'
import CreateTicketModal from '../components/CreateTicketModal'

export default function TicketsPage() {
    const [tickets, setTickets] = useState([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [selectedTicket, setSelectedTicket] = useState(null)
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)

    useEffect(() => {
        loadTickets()
    }, [])

    const loadTickets = async () => {
        try {
            // invisible loading if we have data (for auto refresh)
            if (tickets.length === 0) setLoading(true)
            const data = await api.listTickets()
            setTickets(data)

            // Also refresh selectedTicket if one is selected
            if (selectedTicket) {
                const updatedTicket = await api.getTicket(selectedTicket.id)
                setSelectedTicket(updatedTicket)
            }
        } catch (err) {
            console.error(err)
            // setError(err.message) // Don't block UI on background refresh fail
            if (tickets.length === 0) setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const loadTicketDetail = async (id) => {
        try {
            const data = await api.getTicket(id)
            setSelectedTicket(data)
        } catch (err) {
            setError(err.message)
        }
    }

    const handleResume = async (id) => {
        try {
            await api.resumeTicket(id)
            loadTickets()
            if (selectedTicket?.id === id) {
                loadTicketDetail(id)
            }
        } catch (err) {
            alert(err.message)
        }
    }

    const handleReset = async (id) => {
        if (!confirm('确定要重置此 Ticket 吗？这将归档当前 Session。')) return
        try {
            await api.resetTicket(id)
            loadTickets()
            if (selectedTicket?.id === id) {
                loadTicketDetail(id)
            }
        } catch (err) {
            alert(err.message)
        }
    }

    const formatTime = (iso) => {
        return new Date(iso).toLocaleString('zh-CN', {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        })
    }

    if (loading && tickets.length === 0) {
        return <div className="flex items-center justify-center h-64 text-slate-400">Loading...</div>
    }

    if (error && tickets.length === 0) {
        return <div className="text-red-400 p-4">Error: {error}</div>
    }

    return (
        <div className="space-y-6">
            {/* Header Actions */}
            <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-white">Tickets</h2>
                <div className="flex items-center gap-4">
                    <AutoRefreshControl onRefresh={loadTickets} />
                    <button
                        onClick={() => setIsCreateModalOpen(true)}
                        className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors"
                    >
                        + Create Ticket
                    </button>
                </div>
            </div>

            <div className="flex gap-6">
                {/* Ticket List */}
                <div className="flex-1 space-y-4">
                    {tickets.length === 0 ? (
                        <div className="text-center py-12 text-slate-400">
                            No tickets yet. Create one to get started!
                        </div>
                    ) : (
                        tickets.map(ticket => (
                            <div
                                key={ticket.id}
                                onClick={() => loadTicketDetail(ticket.id)}
                                className={`bg-slate-800 rounded-xl p-4 border cursor-pointer transition ${selectedTicket?.id === ticket.id
                                    ? 'border-indigo-500'
                                    : 'border-slate-700 hover:border-slate-600'
                                    }`}
                            >
                                <div className="flex items-center gap-3 mb-2">
                                    <span className="text-slate-500 font-mono text-sm">#{ticket.id.slice(0, 8)}</span>
                                    <StatusBadge status={ticket.status} />
                                </div>
                                <div className="flex items-center gap-2 text-sm text-slate-400">
                                    <span className="px-2 py-0.5 bg-slate-700 rounded text-xs">🧠 {ticket.agent_name}</span>
                                    <span>•</span>
                                    <span>{formatTime(ticket.updated_at)}</span>
                                </div>
                            </div>
                        ))
                    )}
                </div>

                {/* Detail Panel */}
                {selectedTicket && (
                    <div className="w-96 bg-slate-800 rounded-xl border border-slate-700 p-4 space-y-4 overflow-y-auto max-h-[calc(100vh-200px)]">
                        <div className="flex items-center justify-between">
                            <h3 className="font-semibold">Ticket #{selectedTicket.id.slice(0, 8)}</h3>
                            <button onClick={() => setSelectedTicket(null)} className="text-slate-400 hover:text-white">✕</button>
                        </div>

                        <div className="flex items-center justify-between">
                            <StatusBadge status={selectedTicket.status} large />
                            <div className="flex gap-2">
                                {selectedTicket.status === 'suspended' && (
                                    <button
                                        onClick={() => handleResume(selectedTicket.id)}
                                        className="px-3 py-1.5 bg-green-600 hover:bg-green-500 rounded-lg text-sm"
                                    >
                                        ▶ Resume
                                    </button>
                                )}
                                <button
                                    onClick={() => handleReset(selectedTicket.id)}
                                    className="px-3 py-1.5 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm"
                                >
                                    ↺ Reset
                                </button>
                            </div>
                        </div>

                        {/* Session Navigation Button */}
                        <div className="border-t border-slate-700 pt-3">
                            {selectedTicket.current_session_id ? (
                                <Link
                                    to={`/sessions/${selectedTicket.current_session_id}`}
                                    className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg transition-colors border border-slate-600"
                                >
                                    <span>💬</span>
                                    <span>Go to Active Session</span>
                                </Link>
                            ) : (
                                <button disabled className="w-full px-4 py-2 bg-slate-800 text-slate-500 rounded-lg border border-slate-700 cursor-not-allowed">
                                    No Active Session
                                </button>
                            )}

                            {/* Session History List */}
                            {selectedTicket.sessions && selectedTicket.sessions.length > 0 && (
                                <div className="mt-3 text-sm">
                                    <h4 className="text-slate-400 mb-1">Session History ({selectedTicket.sessions.length})</h4>
                                    <ul className="space-y-1">
                                        {selectedTicket.sessions.map(s => (
                                            <li key={s.id}>
                                                <Link to={`/sessions/${s.id}`} className="block p-2 rounded hover:bg-slate-700 text-slate-300 flex justify-between">
                                                    <span>{formatTime(s.created_at)}</span>
                                                    <StatusBadge status={s.status} />
                                                </Link>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>

                        <div className="bg-slate-700/50 rounded-lg p-3 space-y-2 text-sm">
                            <div className="flex justify-between">
                                <span className="text-slate-400">Agent</span>
                                <span>{selectedTicket.agent_name}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-slate-400">Created</span>
                                <span>{formatTime(selectedTicket.created_at)}</span>
                            </div>
                        </div>

                        {selectedTicket.steps?.length > 0 && (
                            <div>
                                <h4 className="text-sm font-medium text-slate-400 mb-2">Steps</h4>
                                <div className="space-y-2">
                                    {selectedTicket.steps.map((step, i) => (
                                        <div key={i} className="flex items-center gap-3 p-2 bg-slate-700/30 rounded">
                                            <StatusBadge status={step.status} />
                                            <span className="text-sm">{step.title}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {selectedTicket.context && (
                            <div>
                                <h4 className="text-sm font-medium text-slate-400 mb-2">Context</h4>
                                <pre className="bg-slate-900 rounded p-2 text-xs overflow-x-auto">
                                    {JSON.stringify(selectedTicket.context, null, 2)}
                                </pre>
                            </div>
                        )}

                        {selectedTicket.params && (
                            <div>
                                <h4 className="text-sm font-medium text-slate-400 mb-2">Params</h4>
                                <pre className="bg-slate-900 rounded p-2 text-xs overflow-x-auto">
                                    {JSON.stringify(selectedTicket.params, null, 2)}
                                </pre>
                            </div>
                        )}

                        {selectedTicket.error_message && (
                            <div className="p-3 bg-red-500/20 border border-red-500/30 rounded-lg">
                                <p className="text-sm text-red-400">{selectedTicket.error_message}</p>
                            </div>
                        )}
                    </div>
                )}
            </div>

            <CreateTicketModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onCreated={() => {
                    loadTickets()
                }}
            />
        </div>
    )
}
