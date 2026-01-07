import { NavLink, useLocation } from 'react-router-dom'

const navItems = [
    { path: '/tickets', icon: '📋', label: 'Tickets' },
    { path: '/agents', icon: '🧠', label: 'Agents' },
    { path: '/skills', icon: '🎯', label: 'Skills' },
    { path: '/sessions', icon: '💬', label: 'Sessions' },
    { path: '/tools', icon: '🔧', label: 'Tools' },
]

export default function Layout({ children }) {
    const location = useLocation()

    const getPageTitle = () => {
        const item = navItems.find(n => location.pathname.startsWith(n.path))
        return item?.label || 'Dashboard'
    }

    return (
        <div className="flex h-screen">
            {/* Sidebar */}
            <aside className="w-56 bg-slate-800 border-r border-slate-700 flex flex-col">
                <div className="p-4 border-b border-slate-700">
                    <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-500 to-purple-500 bg-clip-text text-transparent">
                        🤖 Agent Platform
                    </h1>
                </div>

                <nav className="flex-1 p-3 space-y-1">
                    {navItems.map(item => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-3 py-2.5 rounded-lg transition ${isActive
                                    ? 'bg-slate-700 text-white'
                                    : 'text-slate-400 hover:bg-slate-700/50 hover:text-white'
                                }`
                            }
                        >
                            <span>{item.icon}</span>
                            <span>{item.label}</span>
                        </NavLink>
                    ))}
                </nav>

                <div className="p-3 border-t border-slate-700 text-xs text-slate-500">
                    MVP v0.0.1
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col overflow-hidden">
                <header className="h-14 bg-slate-800 border-b border-slate-700 px-6 flex items-center">
                    <h2 className="text-lg font-semibold">{getPageTitle()}</h2>
                </header>

                <div className="flex-1 overflow-auto scroll-area p-6">
                    {children}
                </div>
            </main>
        </div>
    )
}
