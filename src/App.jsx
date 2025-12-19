import { useState, useEffect, useRef } from 'react'
import './App.css'

// --- ROBUST TYPEWRITER (Fixed Repeating Bug) ---
const Typewriter = ({ text, speed = 15, onComplete }) => {
  const [display, setDisplay] = useState('')
  const hasStartedRef = useRef(false) // Track if we started typing

  useEffect(() => {
    // If we already typed this text, don't restart (prevents repeating)
    if (hasStartedRef.current && display === text) return;
    
    hasStartedRef.current = true;
    setDisplay(''); // Start fresh
    
    let i = 0
    const timer = setInterval(() => {
      if (i < text.length) {
        setDisplay((prev) => prev + text.charAt(i))
        i++
      } else {
        clearInterval(timer)
        if (onComplete) onComplete()
      }
    }, speed)
    
    return () => clearInterval(timer)
  }, [text, speed, onComplete])

  return <span>{display}</span>
}

function App() {
  const [input, setInput] = useState('')
  // ⚠️ Start with empty array so we don't animate the first message on load
  const [messages, setMessages] = useState([]) 
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef(null)

  // Add the welcome message ONCE when the app loads
  useEffect(() => {
    setMessages([{ 
      sender: 'bot', 
      text: 'I am ready. Tell me your troubles.',
      id: 'welcome-msg' // Static ID prevents re-renders
    }])
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, loading])

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMsg = { sender: 'user', text: input, id: Date.now() }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch('http://127.0.0.1:5000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg.text }),
      })
      
      const data = await response.json()

      const botMsg = { 
        sender: 'bot', 
        text: data.response, 
        verse: data.data,
        id: Date.now() + 1
      }
      setMessages((prev) => [...prev, botMsg])

    } catch (error) {
      setMessages((prev) => [...prev, { 
        sender: 'bot', 
        text: 'The divine connection is faint. Please check the backend.',
        id: Date.now() + 1
      }])
    }

    setLoading(false)
  }

  return (
    <div className="main-wrapper">
      <div className="app-container">
        
        <header className="chat-header">
          <h1>GITA <span>AI</span></h1>
          <div className="status-dot"></div>
        </header>

        <div className="messages-area">
          <div className="message-container">
            {messages.map((msg, index) => {
              // Only animate the VERY LAST message
              const isLatest = index === messages.length - 1;
              // Don't animate the welcome message to be safe
              const isWelcome = msg.id === 'welcome-msg';

              return (
                <div key={msg.id} className={`message-row ${msg.sender}`}>
                  <div className={`bubble ${msg.sender}`}>
                    
                    <div className="message-text">
                      {msg.sender === 'bot' && isLatest && !isWelcome ? (
                        <Typewriter text={msg.text} onComplete={scrollToBottom} />
                      ) : (
                        msg.text
                      )}
                    </div>
                    
                    {msg.verse && (
                      <div className="verse-card">
                        <div className="card-header">
                          VERSE {msg.verse.id.replace('BG_', '')}
                        </div>
                        <div className="card-content">
                          <p className="sanskrit">
                            {isLatest ? <Typewriter text={msg.verse.sanskrit} speed={10} /> : msg.verse.sanskrit}
                          </p>
                          <div className="translation">
                            <strong>Translation</strong>
                            {isLatest ? <Typewriter text={msg.verse.english} speed={5} /> : msg.verse.english}
                          </div>
                          <div className="translation">
                            <strong>Tamil</strong>
                            {isLatest ? <Typewriter text={msg.verse.tamil} speed={5} /> : msg.verse.tamil}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )
            })}

            {loading && (
              <div className="message-row bot">
                <div className="bubble bot" style={{padding: '15px 20px'}}>
                  <span className="typing-indicator"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        <div className="input-area">
          <div className="input-wrapper">
            <input 
              type="text" 
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask Krishna for guidance..."
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
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