import { useState } from 'react'
import StatusBadge from './StatusBadge'

const roleStyles = {
    system: 'bg-slate-700/30 border-slate-600',
    assistant: 'bg-indigo-500/20 border-indigo-500/30',
    user: 'bg-purple-500/20 border-purple-500/30',
    tool: 'bg-slate-900 border-slate-700 font-mono text-xs',
}

export default function SessionView({ session, onSendMessage, onClose }) {
    const [inputValue, setInputValue] = useState('')

    const handleSendMessage = () => {
        if (!inputValue.trim()) return
        onSendMessage(inputValue)
        setInputValue('')
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

    if (!session) return null

    return (
        <div className="w-full bg-slate-800 rounded-xl border border-slate-700 flex flex-col h-full">
            <div className="p-4 border-b border-slate-700 flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <h3 className="font-semibold">Session #{session.id.slice(-6)}</h3>
                    <StatusBadge status={session.status} />
                </div>
                {onClose && (
                    <button onClick={onClose} className="text-slate-400 hover:text-white">✕</button>
                )}
            </div>

            <div className="flex-1 overflow-y-auto scroll-area p-4 space-y-3">
                {session.messages?.map(msg => (
                    <div key={msg.id} className={msg.role === 'user' ? 'flex justify-end' : ''}>
                        <div className={`max-w-[90%] border rounded-lg p-3 ${roleStyles[msg.role] || roleStyles.assistant}`}>
                            <div className="text-xs text-slate-500 mb-1">{msg.role}</div>
                            <div className="text-sm whitespace-pre-wrap">{parseMessageContent(msg)}</div>
                        </div>
                    </div>
                ))}
            </div>

            {session.status === 'suspended' && (
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
    )
}
