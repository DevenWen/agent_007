import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import SessionView from '../components/SessionView'

// Mock StatusBadge since it's a separate component
vi.mock('../components/StatusBadge', () => ({
    default: ({ status }) => <div data-testid="status-badge">{status}</div>
}))

describe('SessionView', () => {
    const mockSession = {
        id: 'sec-123456',
        status: 'suspended',
        messages: [
            { id: '1', role: 'user', content: 'Hello' },
            { id: '2', role: 'assistant', content: 'Hi there' }
        ]
    }

    it('renders session details', () => {
        render(<SessionView session={mockSession} />)

        expect(screen.getByText(/Session #123456/)).toBeInTheDocument()
        expect(screen.getByTestId('status-badge')).toHaveTextContent('suspended')
        expect(screen.getByText('Hello')).toBeInTheDocument()
        expect(screen.getByText('Hi there')).toBeInTheDocument()
    })

    it('renders input when suspended', () => {
        render(<SessionView session={mockSession} />)
        expect(screen.getByPlaceholderText('输入您的回复...')).toBeInTheDocument()
    })

    it('does not render input when not suspended', () => {
        render(<SessionView session={{ ...mockSession, status: 'completed' }} />)
        expect(screen.queryByPlaceholderText('输入您的回复...')).not.toBeInTheDocument()
    })

    it('calls onSendMessage when sending message', () => {
        const onSendMessage = vi.fn()
        render(<SessionView session={mockSession} onSendMessage={onSendMessage} />)

        const input = screen.getByPlaceholderText('输入您的回复...')
        fireEvent.change(input, { target: { value: 'New message' } })
        fireEvent.click(screen.getByText('发送'))

        expect(onSendMessage).toHaveBeenCalledWith('New message')
    })

    it('calls onClose when close button clicked', () => {
        const onClose = vi.fn()
        render(<SessionView session={mockSession} onClose={onClose} />)

        fireEvent.click(screen.getByText('✕'))
        expect(onClose).toHaveBeenCalled()
    })
})
