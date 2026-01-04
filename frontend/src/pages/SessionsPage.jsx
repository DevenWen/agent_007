import { useState, useEffect } from 'react'
import { api } from '../api/client'
import StatusBadge from '../components/StatusBadge'

const roleStyles = {
    system: 'bg-slate-700/30 border-slate-600',
    assistant: 'bg-indigo-500/20 border-indigo-500/30',
    user: 'bg-purple-500/20 border-purple-500/30',
    tool: 'bg-slate-900 border-slate-700 font-mono text-xs',
}

export default function SessionsPage() {
    const [sessions, setSessions] = useState([])
    const [loading, setLoading] = useState(true)
    const [selectedSession, setSelectedSession] = useState(null)
    const [inputValue, setInputValue] = useState('')

    useEffect(() => {
        loadSessions()
    }, [])

    const loadSessions = async () => {
        try {
            const data = await api.listSessions()
            setSessions(data)
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const loadSessionDetail = async (id) => {
        try {
            const data = await api.getSession(id)
            setSelectedSession(data)
        } catch (err) {
            console.error(err)
        }
    }

    const handleSendMessage = async () => {
        if (!inputValue.trim() || !selectedSession) return
        try {
            await api.addMessage(selectedSession.id, inputValue)
            setInputValue('')
            loadSessionDetail(selectedSession.id)
            loadSessions()
        } catch (err) {
            alert(err.message)
        }
    }

    const formatTime = (iso) => {
        return new Date(iso).toLocaleString('zh-CN', {
            month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
        })
    }

    const parseMessageContent = (msg) => {
        if (msg.role === 'assistant') {
            try {
                const blocks = JSON.parse(msg.content)
                if (Array.isArray(blocks)) {
                    return blocks.map((b, i) => {
                        if (b.type === 'text') return <p key={i}>{b.text}</p>
                        if (b.type === 'tool_use') return (
                            <div key={i} className="mt-2 p-2 bg-slate-800 rounded text-xs">
                                <span className="text-indigo-400">Tool: {b.name}</span>
                            </div>
                        )
                        return null
                    })
                }
            } catch { }
        }
        return msg.content
    }

    if (loading) {
        return <div className="flex items-center justify-center h-64 text-slate-400">Loading...</div>
    }

    return (
        <div className="flex gap-6">
            {/* Session List */}
            <div className="flex-1 space-y-4">
                {sessions.length === 0 ? (
                    <div className="text-center py-12 text-slate-400">No sessions yet.</div>
                ) : (
                    sessions.map(session => (
                        <div
                            key={session.id}
                            onClick={() => loadSessionDetail(session.id)}
                            className={`bg-slate-800 rounded-xl p-4 border cursor-pointer transition ${selectedSession?.id === session.id
                                    ? 'border-indigo-500'
                                    : 'border-slate-700 hover:border-slate-600'
                                }`}
                        >
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-3">
                                    <span className="text-slate-500 font-mono text-sm">#{session.id.slice(-6)}</span>
                                    <StatusBadge status={session.status} />
                                </div>
                                <span className="text-sm text-slate-400">{session.message_count} messages</span>
                            </div>
                            <div className="text-sm text-slate-400">
                                Ticket: {session.ticket_id.slice(0, 8)}
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Detail Panel */}
            {selectedSession && (
                <div className="w-[500px] bg-slate-800 rounded-xl border border-slate-700 flex flex-col max-h-[calc(100vh-12rem)]">
                    <div className="p-4 border-b border-slate-700 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <h3 className="font-semibold">Session #{selectedSession.id.slice(-6)}</h3>
                            <StatusBadge status={selectedSession.status} />
                        </div>
                        <button onClick={() => setSelectedSession(null)} className="text-slate-400 hover:text-white">✕</button>
                    </div>

                    <div className="flex-1 overflow-y-auto scroll-area p-4 space-y-3">
                        {selectedSession.messages?.map(msg => (
                            <div key={msg.id} className={msg.role === 'user' ? 'flex justify-end' : ''}>
                                <div className={`max-w-[90%] border rounded-lg p-3 ${roleStyles[msg.role] || roleStyles.assistant}`}>
                                    <div className="text-xs text-slate-500 mb-1">{msg.role}</div>
                                    <div className="text-sm whitespace-pre-wrap">{parseMessageContent(msg)}</div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {selectedSession.status === 'suspended' && (
                        <div className="p-4 border-t border-slate-700">
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={inputValue}
                                    onChange={(e) => setInputValue(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                                    placeholder="输入您的回复..."
                                    className="flex-1 bg-slate-900 border border-slate-600 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-indigo-500"
                                />
                                <button
                                    onClick={handleSendMessage}
                                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm"
                                >
                                    发送
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
