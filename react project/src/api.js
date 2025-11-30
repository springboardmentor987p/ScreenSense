// Simple API helper used by the frontend to send assessment data to a backend.
const DEFAULT_BACKEND = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
const DEFAULT_PATH = '/insights'

function mapToBackendSchema(payload) {
  // Map the frontend payload to the backend InputPayload schema
  return {
    Age: payload.age,
    Gender: payload.gender,
    Avg_Daily_Screen_Time_hr: payload.totalHours,
    Primary_Device: payload.primaryDevice,
    Educational_to_Recreational_Ratio: payload.eduRecRatio,
    Health_Impacts: Array.isArray(payload.healthImpacts) ? payload.healthImpacts.join(', ') : payload.healthImpacts || '',
    Urban_or_Rural: payload.urbanOrRural || 'Urban',
  }
}

export async function sendAssessment(payload, { path = DEFAULT_PATH, baseUrl = DEFAULT_BACKEND } = {}) {
  const url = `${baseUrl.replace(/\/$/, '')}${path}`
  const body = mapToBackendSchema(payload)
  console.log('sendAssessment: calling', url, 'with body:', body)
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    console.log('sendAssessment: response status:', res.status)
    if (!res.ok) {
      const text = await res.text()
      console.error('sendAssessment: error response:', text)
      throw new Error(`Request failed ${res.status}: ${text}`)
    }
    const json = await res.json()
    console.log('sendAssessment: response data:', json)
    return json
  } catch (err) {
    console.error('sendAssessment: exception:', err)
    throw err
  }
}

export default { sendAssessment }
