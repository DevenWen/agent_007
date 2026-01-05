import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api/client'
import SessionView from '../components/SessionView'

export default function SessionDetailPage() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [session, setSession] = useState(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)

    useEffect(() => {
        loadSession()
    }, [id])

    const loadSession = async () => {
        try {
            setLoading(true)
            const data = await api.getSession(id)
            setSession(data)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleSendMessage = async (content) => {
        try {
            await api.addMessage(session.id, content)
            loadSession()
        } catch (err) {
            alert(err.message)
        }
    }

    if (loading) return <div className="flex items-center justify-center h-64 text-slate-400">Loading...</div>

    if (error) return (
        <div className="flex flex-col items-center justify-center h-64 text-slate-400">
            <p className="text-red-500 mb-4">Error: {error}</p>
            <button
                onClick={() => navigate('/sessions')}
                className="text-indigo-400 hover:text-indigo-300"
            >
                Back to Sessions
            </button>
        </div>
    )

    return (
        <div className="max-w-4xl mx-auto h-[calc(100vh-8rem)]">
            <SessionView
                session={session}
                onSendMessage={handleSendMessage}
            />
        </div>
    )
}
