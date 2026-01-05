import { useState, useEffect } from 'react'
import { api } from '../api/client'
import StatusBadge from '../components/StatusBadge'
import SessionView from '../components/SessionView'

export default function SessionsPage() {
    const [sessions, setSessions] = useState([])
    const [loading, setLoading] = useState(true)
    const [selectedSession, setSelectedSession] = useState(null)

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

    const handleSendMessage = async (content) => {
        if (!content.trim() || !selectedSession) return
        try {
            await api.addMessage(selectedSession.id, content)
            loadSessionDetail(selectedSession.id)
            loadSessions()
        } catch (err) {
            alert(err.message)
        }
    }

    if (loading) {
        return <div className="flex items-center justify-center h-64 text-slate-400">Loading...</div>
    }

    return (
        <div className="flex gap-6 h-[calc(100vh-8rem)]">
            {/* Session List */}
            <div className={`flex-1 space-y-4 overflow-y-auto scroll-area ${selectedSession ? 'hidden md:block' : ''}`}>
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
                <div className="w-full md:w-[600px] h-full">
                    <SessionView
                        session={selectedSession}
                        onSendMessage={handleSendMessage}
                        onClose={() => setSelectedSession(null)}
                    />
                </div>
            )}
        </div>
    )
}
