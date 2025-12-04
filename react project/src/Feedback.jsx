import React, { useState } from 'react'

export default function Feedback({ onBack }) {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [feedbackType, setFeedbackType] = useState('General')
  const [message, setMessage] = useState('')
  const [rating, setRating] = useState(5)
  const [submitted, setSubmitted] = useState(false)
  const [error, setError] = useState('')

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
    <div className="panel feedback">
      <h2>📝 Send Us Your Feedback</h2>
      <p style={{ color: '#666', marginBottom: '20px' }}>
        We'd love to hear from you! Your feedback helps us improve the Kids Screen Time Advisor.
      </p>

      {submitted && (
        <div style={{
          backgroundColor: '#d4edda',
          color: '#155724',
          padding: '12px',
          borderRadius: '6px',
          marginBottom: '20px',
          border: '1px solid #c3e6cb',
        }}>
          ✅ Thank you for your feedback! We appreciate your input.
        </div>
      )}

      <form onSubmit={handleSubmit} style={{ maxWidth: '600px' }}>
        <div className="field">
          <label>Your Name *</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., John Doe"
          />
        </div>

        <div className="field">
          <label>Email Address *</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="e.g., john@example.com"
          />
        </div>

        <div className="field">
          <label>Feedback Type</label>
          <select value={feedbackType} onChange={(e) => setFeedbackType(e.target.value)}>
            <option>General</option>
            <option>Bug Report</option>
            <option>Feature Request</option>
            <option>Suggestion</option>
            <option>Compliment</option>
            <option>Other</option>
          </select>
        </div>

        <div className="field">
          <label>Rating (1-5)</label>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <input
              type="range"
              min="1"
              max="5"
              value={rating}
              onChange={(e) => setRating(Number(e.target.value))}
              style={{ flex: 1 }}
            />
            <span style={{ fontWeight: 'bold', fontSize: '18px', minWidth: '30px' }}>
              {rating} ⭐
            </span>
          </div>
        </div>

        <div className="field">
          <label>Your Feedback Message *</label>
          <textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Tell us what you think... (minimum 10 characters)"
            rows={5}
            style={{
              width: '100%',
              padding: '10px',
              borderRadius: '6px',
              border: '1px solid #ddd',
              fontFamily: 'inherit',
              fontSize: '14px',
            }}
          />
          <small style={{ color: '#999' }}>
            {message.length} / 500 characters
          </small>
        </div>

        {error && <div className="form-error" style={{ marginBottom: '16px' }}>{error}</div>}

        <div style={{ display: 'flex', gap: '12px' }}>
          <button type="submit" className="btn-primary">
            Submit Feedback
          </button>
          <button
            type="button"
            className="btn"
            onClick={onBack}
            style={{ backgroundColor: '#f0f0f0', color: '#333' }}
          >
            Back
          </button>
        </div>
      </form>

      <div style={{
        marginTop: '30px',
        padding: '16px',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
        borderLeft: '4px solid #4e79a7',
      }}>
        <h4>Why Your Feedback Matters</h4>
        <ul style={{ marginTop: '10px', paddingLeft: '20px' }}>
          <li>Help us identify and fix issues</li>
          <li>Share ideas for new features</li>
          <li>Let us know what you like about the app</li>
          <li>Contribute to making this tool better for Indian families</li>
        </ul>
      </div>
    </div>
  )
}
