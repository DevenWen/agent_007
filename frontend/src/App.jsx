import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import TicketsPage from './pages/TicketsPage'
import AgentsPage from './pages/AgentsPage'
import SessionsPage from './pages/SessionsPage'
import ToolsPage from './pages/ToolsPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/tickets" replace />} />
        <Route path="/tickets" element={<TicketsPage />} />
        <Route path="/agents" element={<AgentsPage />} />
        <Route path="/sessions" element={<SessionsPage />} />
        <Route path="/tools" element={<ToolsPage />} />
      </Routes>
    </Layout>
  )
}

export default App
