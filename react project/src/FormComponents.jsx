import React, { useState } from 'react'
import { sendAssessment } from './api'

export default function FormComponents({ onSubmit }) {
  const [age, setAge] = useState('')
  const [gender, setGender] = useState('Male')
  const [totalHours, setTotalHours] = useState('')
  const [eduRecRatio, setEduRecRatio] = useState('')
  const [device, setDevice] = useState('Smartphone')
  const [healthImpacts, setHealthImpacts] = useState('None')
  const [error, setError] = useState('')

  function parseRatio(input) {
    const v = Number(input)
    if (!isNaN(v) && v > 0) return v
    return null
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    const ageNum = Number(age)
    const total = Number(totalHours)

    if (!age || isNaN(ageNum) || ageNum < 0 || ageNum > 120) {
      setError('Please enter a valid age')
      return
    }
    if (!totalHours || isNaN(total) || total < 0 || total > 24) {
      setError('Please enter a valid total daily screen time in hours (0-24)')
      return
    }

    const ratioVal = parseRatio(eduRecRatio)
    if (ratioVal === null) {
      setError('Please enter a numeric ratio (e.g., 0.4 or 1.2)')
      return
    }

    const payload = {
      age: ageNum,
      gender: gender,
      totalHours: total,
      eduRecRatio: ratioVal,
      primaryDevice: device,
      healthImpacts: healthImpacts.split(',').map(s => s.trim()).filter(Boolean),
      timestamp: Date.now(),
    }
    // Only attempt to send the payload to a backend when VITE_BACKEND_URL is
    // explicitly configured. This avoids accidental network calls if you
    // removed or don't run a backend (e.g., you deleted `backend_sample`).
    const backendUrl = import.meta.env.VITE_BACKEND_URL
    if (backendUrl && typeof sendAssessment === 'function') {
      try {
        const resp = await sendAssessment(payload)
        console.info('Assessment sent to backend:', resp)
        // Pass server response along to the app so it can render server-generated recommendations
        if (onSubmit) onSubmit({ ...payload, serverResponse: resp })
        return
      } catch (err) {
        console.warn('Could not send assessment to backend:', err.message || err)
        // fallback to local behaviour
        if (onSubmit) onSubmit(payload)
        return
      }
    }

    if (onSubmit) onSubmit(payload)
  }

  return (
    <form className="form-card" onSubmit={handleSubmit}>
      <div className="field">
        <label>Enter your age</label>
        <input value={age} onChange={(e) => setAge(e.target.value)} type="number" min="0" max="120" placeholder="e.g. 5" />
      </div>

      <div className="field">
        <label>Enter your gender (Male/Female)</label>
        <select value={gender} onChange={(e) => setGender(e.target.value)}>
          <option>Male</option>
          <option>Female</option>
          <option>Other</option>
          <option>Prefer not to say</option>
        </select>
      </div>

      <div className="field">
        <label>Enter your average daily screen time in hours</label>
        <input value={totalHours} onChange={(e) => setTotalHours(e.target.value)} type="number" min="0" max="24" step="0.1" placeholder="e.g. 6" />
      </div>

      <div className="field">
        <label>Enter your educational to recreational screen time ratio (e.g., 0.4)</label>
        <input value={eduRecRatio} onChange={(e) => setEduRecRatio(e.target.value)} type="text" placeholder="e.g. 0.3 or 1.5" />
        <small style={{color:'#9aa4ad'}}>If &lt;=1 interpreted as educational fraction of total; otherwise as edu:rec ratio.</small>
      </div>

      <div className="field">
        <label>Enter your primary device (Smartphone/Laptop/TV/Tablet)</label>
        <select value={device} onChange={(e) => setDevice(e.target.value)}>
          <option>Smartphone</option>
          <option>Laptop</option>
          <option>TV</option>
          <option>Tablet</option>
          <option>Other</option>
        </select>
      </div>

      <div className="field">
        <label>Enter any health impacts you experience (comma-separated, or type 'None')</label>
        <input value={healthImpacts} onChange={(e) => setHealthImpacts(e.target.value)} type="text" placeholder="e.g. Poor Sleep, Eye Strain" />
      </div>

      {error && <div className="form-error">{error}</div>}

      <div className="form-actions">
        <button type="submit" className="btn-primary">Get Recommendation</button>
      </div>
    </form>
  )
}
