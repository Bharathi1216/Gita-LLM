import { useState, useEffect, useRef } from 'react'
import './App.css'

// [FLOWFORGE ERROR 3: Frontend Build / Unresolved Import Error]
// To disable this error, comment out or remove the import below:
import { GitaNavbar } from './components/GitaNavbar'

// Typewriter component for animating bot messages
const Typewriter = ({ text, speed = 15, onComplete, messageId }) => {
  const [display, setDisplay] = useState('')
  const typedMessagesRef = useRef(new Set())

  useEffect(() => {
    if (typedMessagesRef.current.has(messageId)) {
      setDisplay(text)
      return
    }

    typedMessagesRef.current.add(messageId)
    setDisplay('')
    let i = 0

    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplay(prev => prev + text.charAt(i))
        i++
      } else {
        clearInterval(timer)
        onComplete && onComplete()
      }
    }, speed)

    return () => clearInterval(timer)
  }, [text, speed, onComplete, messageId])

  return <span>{display}</span>
}

function App() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [userId, setUserId] = useState(null)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    setMessages([{ 
      sender: 'bot',
      text: 'I am ready. Tell me your troubles.',
      id: 'welcome-msg'
    }])

    fetch('http://127.0.0.1:5000/api/survey', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    })
      .then(res => res.json())
      .then(data => setUserId(data.user_id))
      .catch(() => null)
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(scrollToBottom, [messages, loading])

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMsg = { sender: 'user', text: input, id: Date.now() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.text, user_id: userId })
      })

      const data = await response.json()
      const botMsg = {
        sender: 'bot',
        text: data?.response || 'Please try again.',
        verse: data?.data || null,
        id: Date.now() + 1
      }

      setMessages(prev => [...prev, botMsg])
    } catch {
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: 'The divine connection is faint. Please check the backend.',
        id: Date.now() + 1
      }])
    }

    setLoading(false)
  }

  // ================= RENDER =================
  return (
    <div className="main-wrapper">
      <div className="app-container">

        {/* [FLOWFORGE ERROR 3: Component reference]
            To disable this error, comment out the line below: */}
        <GitaNavbar />

        <header className="chat-header">
          <h1>GITA <span>AI</span></h1>
          <div className="status-dot"></div>
        </header>

        <div className="messages-area">
          <div className="message-container">

            {messages.map((msg, index) => {
              const isLatest = index === messages.length - 1
              const isWelcome = msg.id === 'welcome-msg'

              return (
                <div key={msg.id} className={`message-row ${msg.sender}`}>
                  <div className={`bubble ${msg.sender}`}>

                    {/* -------- MESSAGE TEXT -------- */}
                    <div className="message-text">
                      {msg.sender === 'bot' && isLatest && !isWelcome
                        ? (
                          <Typewriter
                            text={msg.text}
                            messageId={msg.id}
                            onComplete={scrollToBottom}
                          />
                        ) : (
                          msg.text
                        )}
                    </div>

                    {/* -------- VERSE CARD -------- */}
                    {msg.verse && msg.verse.english && (
                      <div className="verse-card">
                        <div className="card-header">
                          VERSE {msg.verse.id.replace('BG_', '')}
                        </div>

                        <div className="card-content">

                          {/* Sanskrit ONLY if present */}
                          {msg.verse.sanskrit && (
                            <p className="sanskrit">
                              {isLatest
                                ? (
                                  <Typewriter
                                    text={msg.verse.sanskrit}
                                    speed={10}
                                    messageId={msg.id + '-sa'}
                                  />
                                ) : msg.verse.sanskrit}
                            </p>
                          )}

                          {/* English Translation */}
                          <div className="translation">
                            <strong>Translation</strong>
                            {isLatest
                              ? (
                                <Typewriter
                                  text={msg.verse.english}
                                  speed={5}
                                  messageId={msg.id + '-en'}
                                />
                              ) : msg.verse.english}
                          </div>

                          {/* Tamil ONLY if present */}
                          {msg.verse.tamil && (
                            <div className="translation">
                              <strong>Tamil</strong>
                              {isLatest
                                ? (
                                  <Typewriter
                                    text={msg.verse.tamil}
                                    speed={5}
                                    messageId={msg.id + '-ta'}
                                  />
                                ) : msg.verse.tamil}
                            </div>
                          )}

                        </div>
                      </div>
                    )}

                  </div>
                </div>
              )
            })}

            {/* -------- LOADING -------- */}
            {loading && (
              <div className="message-row bot">
                <div className="bubble bot" style={{ padding: '15px 20px' }}>
                  <span className="typing-indicator"></span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* -------- INPUT -------- */}
        <div className="input-area">
          <div className="input-wrapper">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              placeholder="Ask Krishna for guidance..."
              onKeyPress={e => e.key === 'Enter' && sendMessage()}
              disabled={loading}
              autoFocus
            />
            <button onClick={sendMessage} disabled={loading || !input.trim()}>
              SEND
            </button>
          </div>
        </div>

      </div>
    </div>
  )
}

export default App
