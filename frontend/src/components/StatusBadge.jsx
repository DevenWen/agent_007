const statusStyles = {
    pending: 'bg-yellow-500/20 text-yellow-400',
    running: 'bg-blue-500/20 text-blue-400 animate-pulse-dot',
    active: 'bg-blue-500/20 text-blue-400 animate-pulse-dot',
    suspended: 'bg-orange-500/20 text-orange-400',
    completed: 'bg-green-500/20 text-green-400',
    failed: 'bg-red-500/20 text-red-400',
}

const statusIcons = {
    pending: '⏳',
    running: '▶',
    active: '▶',
    suspended: '⏸',
    completed: '✓',
    failed: '✕',
}

export default function StatusBadge({ status, large = false }) {
    const style = statusStyles[status] || 'bg-slate-500/20 text-slate-400'
    const icon = statusIcons[status] || '?'
    const sizeClass = large ? 'px-3 py-1.5 text-sm' : 'px-2 py-0.5 text-xs'

    return (
        <span className={`inline-flex items-center gap-1 rounded-full font-medium ${sizeClass} ${style}`}>
            <span>{icon}</span>
            <span className="capitalize">{status}</span>
        </span>
    )
}
