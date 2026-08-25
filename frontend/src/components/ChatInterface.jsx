import { useState, useRef, useEffect, useCallback } from 'react'
import { Send, RefreshCw, Database, Wifi, WifiOff, ChevronDown } from 'lucide-react'
import Message from './Message'
import { sendChat, refreshData, getHealth } from '../api'

const SUGGESTED_QUERIES = [
  "How's our pipeline looking for this quarter?",
  "Show me top deals by value",
  "Which work orders are delayed or at risk?",
  "What's our win rate and revenue this month?",
  "Which sectors are performing best?",
  "Summarize for a leadership update",
  "Are there any projects over budget?",
  "What deals are closing this week?",
]

const WELCOME_MESSAGE = {
  role: 'assistant',
  content: `# 👋 Welcome to Skylark Drones BI Agent

I'm your AI-powered Business Intelligence assistant connected to your **monday.com** boards.

**I can help you with:**
- 📊 Pipeline health & deal analysis
- 🏗️ Work order status & operational metrics  
- 💰 Revenue insights & sector performance
- 📋 Leadership update summaries
- ⚠️ Identifying risks, delays, or anomalies

**Try asking me something like:**
- *"How's our energy sector pipeline this quarter?"*
- *"Which projects are behind schedule?"*
- *"Give me a leadership update summary"*

> 💡 Data is fetched live from monday.com. Use the **Refresh** button to get the latest data.`,
}

export default function ChatInterface() {
  const [messages, setMessages] = useState([WELCOME_MESSAGE])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [health, setHealth] = useState(null)
  const [showSuggestions, setShowSuggestions] = useState(true)
  const [notification, setNotification] = useState(null)
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  // Conversation history for context
  const conversationHistory = messages
    .filter((m) => m.role !== 'assistant' || m !== WELCOME_MESSAGE)
    .map((m) => ({ role: m.role, content: m.content }))

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [])

  // Only scroll when USER sends a message (not when AI replies)
  // This keeps the view stable after AI responds


  // Fetch health status on mount
  useEffect(() => {
    getHealth()
      .then(setHealth)
      .catch(() => setHealth({ status: 'unreachable' }))
  }, [])

  const showNotif = (msg, type = 'info') => {
    setNotification({ msg, type })
    setTimeout(() => setNotification(null), 4000)
  }

  const handleSend = async (text) => {
    const userMessage = (text || input).trim()
    if (!userMessage || isLoading) return

    setInput('')
    setShowSuggestions(false)
    setMessages((prev) => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)
    // Scroll only when user sends — AI reply stays in place
    setTimeout(() => scrollToBottom(), 50)

    try {
      const data = await sendChat(userMessage, conversationHistory)
      setMessages((prev) => [...prev, { role: 'assistant', content: data.reply }])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `⚠️ **Error:** ${err.message}\n\nPlease check that the backend server is running and configured correctly.`,
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleRefresh = async () => {
    setIsRefreshing(true)
    try {
      const data = await refreshData()
      setHealth((prev) => ({ ...prev, data_loaded: data.success }))
      if (data.success) {
        const summary = data.data_summary
        showNotif(
          `✅ Data refreshed: ${summary?.work_orders?.total ?? 0} work orders, ${summary?.deals?.total ?? 0} deals`,
          'success'
        )
      } else {
        showNotif(`❌ ${data.message}`, 'error')
      }
    } catch (err) {
      showNotif(`❌ Refresh failed: ${err.message}`, 'error')
    } finally {
      setIsRefreshing(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const isConnected = health && health.status !== 'unreachable'
  const dataLoaded = health?.data_loaded

  return (
    <div className="flex flex-col h-screen bg-slate-950">
      {/* Header */}
      <header className="flex items-center justify-between px-6 py-4 bg-slate-900 border-b border-slate-800 flex-shrink-0">
        <div className="flex items-center gap-3">
          {/* Logo */}
          <div className="w-9 h-9 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">SD</span>
          </div>
          <div>
            <h1 className="font-bold text-white text-lg leading-tight">Skylark Drones</h1>
            <p className="text-slate-400 text-xs">Business Intelligence Agent</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          {/* Data status badge */}
          {health && (
            <div className="hidden sm:flex items-center gap-2 text-xs">
              <Database size={13} className={dataLoaded ? 'text-green-400' : 'text-yellow-400'} />
              <span className={dataLoaded ? 'text-green-400' : 'text-yellow-400'}>
                {dataLoaded
                  ? `${health.data_summary?.work_orders?.total ?? 0} WOs · ${health.data_summary?.deals?.total ?? 0} Deals`
                  : 'Data not loaded'}
              </span>
            </div>
          )}

          {/* Connection indicator */}
          <div className="flex items-center gap-1.5 text-xs">
            {isConnected ? (
              <Wifi size={13} className="text-green-400" />
            ) : (
              <WifiOff size={13} className="text-red-400" />
            )}
            <span className={isConnected ? 'text-green-400' : 'text-red-400'}>
              {isConnected ? 'Connected' : 'Offline'}
            </span>
          </div>

          {/* Refresh button */}
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-700 hover:bg-slate-600 disabled:opacity-50 rounded-lg text-xs text-white transition-colors"
          >
            <RefreshCw size={13} className={isRefreshing ? 'animate-spin' : ''} />
            {isRefreshing ? 'Refreshing…' : 'Refresh'}
          </button>
        </div>
      </header>

      {/* Notification toast */}
      {notification && (
        <div
          className={`mx-4 mt-3 px-4 py-2.5 rounded-lg text-sm font-medium animate-fade-in flex-shrink-0 ${
            notification.type === 'success'
              ? 'bg-green-900/60 border border-green-700 text-green-300'
              : notification.type === 'error'
              ? 'bg-red-900/60 border border-red-700 text-red-300'
              : 'bg-blue-900/60 border border-blue-700 text-blue-300'
          }`}
        >
          {notification.msg}
        </div>
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4">
        {messages.map((msg, i) => (
          <Message key={i} role={msg.role} content={msg.content} />
        ))}
        {isLoading && <Message isLoading />}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested queries */}
      {showSuggestions && messages.length === 1 && (
        <div className="px-4 pb-3 flex-shrink-0">
          <p className="text-xs text-slate-500 mb-2 flex items-center gap-1">
            <ChevronDown size={12} /> Try a query
          </p>
          <div className="flex flex-wrap gap-2">
            {SUGGESTED_QUERIES.map((q) => (
              <button
                key={q}
                onClick={() => handleSend(q)}
                disabled={isLoading}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-blue-500 rounded-full text-xs text-slate-300 hover:text-white transition-all disabled:opacity-50"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input area */}
      <div className="px-4 pb-4 flex-shrink-0">
        <div className="flex items-end gap-2 bg-slate-800 border border-slate-700 focus-within:border-blue-500 rounded-2xl px-4 py-3 transition-colors">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a business question… (Enter to send, Shift+Enter for newline)"
            rows={1}
            disabled={isLoading}
            className="flex-1 bg-transparent text-white placeholder-slate-500 text-sm resize-none outline-none leading-relaxed max-h-32 overflow-y-auto disabled:opacity-50"
            style={{ height: 'auto' }}
            onInput={(e) => {
              e.target.style.height = 'auto'
              e.target.style.height = Math.min(e.target.scrollHeight, 128) + 'px'
            }}
          />
          <button
            onClick={() => handleSend()}
            disabled={isLoading || !input.trim()}
            className="w-9 h-9 flex items-center justify-center bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 rounded-xl text-white transition-colors flex-shrink-0"
          >
            <Send size={16} />
          </button>
        </div>
        <p className="text-center text-xs text-slate-600 mt-2">
          Powered by Gemini AI · Data from monday.com
        </p>
      </div>
    </div>
  )
}
