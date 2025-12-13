import React, { useState } from 'react'

export default function Feedback({ onBack }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [feedbackType, setFeedbackType] = useState('General')
  const [message, setMessage] = useState('')
  const [rating, setRating] = useState(5)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')
  const [focusedField, setFocusedField] = useState(null)

  function handleSubmit(e) {
    e.preventDefault()
    setError('')

    // Validation
    if (!name.trim()) {
      setError('Please enter your name')
      return
    }
    if (!email.trim()) {
      setError('Please enter your email')
      return
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError('Please enter a valid email address')
      return
    }
    if (!message.trim()) {
      setError('Please enter your feedback message')
      return
    }

    // Log feedback (in a real app, this would be sent to a backend)
    const feedback = {
      name,
      email,
      feedbackType,
      message,
      rating,
      timestamp: new Date().toLocaleString(),
    }
    console.log('Feedback submitted:', feedback)

    // Show success and reset form
    setSubmitted(true)
    setTimeout(() => {
      setName('')
      setEmail('')
      setFeedbackType('General')
      setMessage('')
      setRating(5)
      setSubmitted(false)
    }, 2000)
  }

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f8f9fa', padding: '20px' }}>
      <div style={{ maxWidth: '700px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '30px', textAlign: 'center' }}>
          <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '10px' }}>
            📝 We'd Love Your Feedback!
          </h1>
          <p style={{ color: '#666', fontSize: '16px', maxWidth: '500px', margin: '0 auto' }}>
            Your insights help us create a better app for families managing kids' screen time
          </p>
        </div>

        {submitted && (
          <div style={{
            backgroundColor: '#d4edda',
            color: '#155724',
            padding: '16px',
            borderRadius: '8px',
            marginBottom: '30px',
            border: '2px solid #c3e6cb',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            animation: 'slideIn 0.3s ease-out',
          }}>
            <div style={{ fontSize: '18px', fontWeight: 'bold' }}>✅ Thank You!</div>
            <div style={{ marginTop: '8px' }}>Your feedback has been received and will help us improve.</div>
          </div>
        )}

        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          padding: '30px',
          marginBottom: '20px',
        }}>
          <form onSubmit={handleSubmit}>
            {/* Name Field */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                marginBottom: '8px',
                color: '#333',
                fontSize: '14px',
              }}>
                Your Name <span style={{ color: '#e15759' }}>*</span>
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                onFocus={() => setFocusedField('name')}
                onBlur={() => setFocusedField(null)}
                placeholder="e.g., Ravi Kumar"
                style={{
                  width: '100%',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  border: focusedField === 'name' ? '2px solid #4e79a7' : '2px solid #ddd',
                  fontSize: '15px',
                  fontFamily: 'inherit',
                  boxSizing: 'border-box',
                  transition: 'border-color 0.2s',
                }}
              />
            </div>

            {/* Email Field */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                marginBottom: '8px',
                color: '#333',
                fontSize: '14px',
              }}>
                Email Address <span style={{ color: '#e15759' }}>*</span>
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                onFocus={() => setFocusedField('email')}
                onBlur={() => setFocusedField(null)}
                placeholder="your.email@example.com"
                style={{
                  width: '100%',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  border: focusedField === 'email' ? '2px solid #4e79a7' : '2px solid #ddd',
                  fontSize: '15px',
                  fontFamily: 'inherit',
                  boxSizing: 'border-box',
                  transition: 'border-color 0.2s',
                }}
              />
            </div>

            {/* Feedback Type */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                marginBottom: '8px',
                color: '#333',
                fontSize: '14px',
              }}>
                Feedback Type
              </label>
              <select
                value={feedbackType}
                onChange={(e) => setFeedbackType(e.target.value)}
                onFocus={() => setFocusedField('type')}
                onBlur={() => setFocusedField(null)}
                style={{
                  width: '100%',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  border: focusedField === 'type' ? '2px solid #4e79a7' : '2px solid #ddd',
                  fontSize: '15px',
                  fontFamily: 'inherit',
                  backgroundColor: 'white',
                  cursor: 'pointer',
                  transition: 'border-color 0.2s',
                }}
              >
                <option>👍 General Feedback</option>
                <option>🐛 Bug Report</option>
                <option>💡 Feature Request</option>
                <option>🚀 Suggestion</option>
                <option>⭐ Compliment</option>
                <option>🤔 Other</option>
              </select>
            </div>

            {/* Rating */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                marginBottom: '12px',
                color: '#333',
                fontSize: '14px',
              }}>
                How helpful is this app? <span style={{ marginLeft: '8px' }}>{getRatingEmoji(rating)}</span>
              </label>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <input
                  type="range"
                  min="1"
                  max="5"
                  value={rating}
                  onChange={(e) => setRating(Number(e.target.value))}
                  style={{
                    flex: 1,
                    cursor: 'pointer',
                    height: '6px',
                  }}
                />
                <div style={{
                  fontSize: '20px',
                  fontWeight: 'bold',
                  minWidth: '50px',
                  textAlign: 'center',
                  padding: '8px 12px',
                  backgroundColor: getRatingColor(rating),
                  borderRadius: '6px',
                  color: 'white',
                }}>
                  {rating}/5
                </div>
              </div>
              <div style={{
                marginTop: '8px',
                fontSize: '12px',
                color: '#999',
                textAlign: 'center',
              }}>
                {getRatingText(rating)}
              </div>
            </div>

            {/* Message */}
            <div style={{ marginBottom: '24px' }}>
              <label style={{
                display: 'block',
                fontWeight: '600',
                marginBottom: '8px',
                color: '#333',
                fontSize: '14px',
              }}>
                Your Message <span style={{ color: '#e15759' }}>*</span>
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                onFocus={() => setFocusedField('message')}
                onBlur={() => setFocusedField(null)}
                placeholder="Share your thoughts, suggestions, or report any issues..."
                rows={5}
                style={{
                  width: '100%',
                  padding: '12px 14px',
                  borderRadius: '8px',
                  border: focusedField === 'message' ? '2px solid #4e79a7' : '2px solid #ddd',
                  fontFamily: 'inherit',
                  fontSize: '15px',
                  boxSizing: 'border-box',
                  resize: 'vertical',
                  transition: 'border-color 0.2s',
                }}
              />
              <div style={{
                marginTop: '8px',
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '12px',
                color: '#999',
              }}>
                <span>{message.length} / 500 characters</span>
                <span>{message.split(' ').filter(w => w.trim().length > 0).length} words</span>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div style={{
                backgroundColor: '#f8d7da',
                color: '#721c24',
                padding: '12px 14px',
                borderRadius: '8px',
                marginBottom: '20px',
                border: '1px solid #f5c6cb',
                fontSize: '14px',
              }}>
                ⚠️ {error}
              </div>
            )}

            {/* Buttons */}
            <div style={{ display: 'flex', gap: '12px' }}>
              <button
                type="submit"
                style={{
                  flex: 1,
                  padding: '12px 20px',
                  backgroundColor: '#4e79a7',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'background-color 0.2s',
                }}
                onMouseEnter={(e) => e.target.style.backgroundColor = '#3d5f80'}
                onMouseLeave={(e) => e.target.style.backgroundColor = '#4e79a7'}
              >
                ✓ Submit Feedback
              </button>
              <button
                type="button"
                onClick={onBack}
                style={{
                  flex: 1,
                  padding: '12px 20px',
                  backgroundColor: '#f0f0f0',
                  color: '#333',
                  border: '2px solid #ddd',
                  borderRadius: '8px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.target.style.backgroundColor = '#e8e8e8'
                  e.target.style.borderColor = '#999'
                }}
                onMouseLeave={(e) => {
                  e.target.style.backgroundColor = '#f0f0f0'
                  e.target.style.borderColor = '#ddd'
                }}
              >
                ← Back
              </button>
            </div>
          </form>
        </div>

        {/* Info Section */}
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.08)',
          padding: '24px',
          borderLeft: '5px solid #4e79a7',
        }}>
          <h3 style={{ marginTop: 0, marginBottom: '16px', fontSize: '18px' }}>
            💬 Why Your Feedback Matters
          </h3>
          <ul style={{
            margin: 0,
            paddingLeft: '20px',
            lineHeight: '1.8',
            color: '#555',
          }}>
            <li>🔧 <strong>Fix Issues:</strong> Help us identify and resolve bugs</li>
            <li>✨ <strong>New Features:</strong> Share ideas for features you'd like to see</li>
            <li>👍 <strong>Improve Experience:</strong> Tell us what works well</li>
            <li>🌟 <strong>Make Impact:</strong> Help us create the best screen time management tool for Indian families</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

// Helper functions
function getRatingEmoji(rating) {
  const emojis = ['', '😞', '😐', '🙂', '😊', '🤩']
  return emojis[rating] || ''
}

function getRatingColor(rating) {
  const colors = ['', '#dc3545', '#fd7e14', '#ffc107', '#28a745', '#17a2b8']
  return colors[rating] || '#999'
}

function getRatingText(rating) {
  const texts = [
    '',
    'Not helpful - needs major improvements',
    'Could be better',
    'Good - meets basic needs',
    'Great - very useful',
    'Excellent - highly recommend!',
  ]
  return texts[rating] || ''
}
