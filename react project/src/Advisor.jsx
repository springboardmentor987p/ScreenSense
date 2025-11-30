import React from 'react'

function recommendedHours(age) {
  if (age <= 2) return 0
  if (age <= 5) return 1
  if (age <= 12) return 1.5
  return 2
}

// Converts eduRecRatio into fraction of total that is educational
function ratioToFraction(ratio) {
  // If ratio <= 1 we treat as fraction educational-of-total
  if (ratio <= 1) return ratio
  // Otherwise interpret as edu:rec -> fraction = ratio / (1 + ratio)
  return ratio / (1 + ratio)
}

export default function Advisor({ data, onBack }) {
  if (!data) {
    return (
      <div className="panel">
        <h2>Screen Time Advisor</h2>
        <p>No data yet. Please fill the form to get personalized recommendations.</p>
        <button className="btn-primary" onClick={onBack}>Go to Form</button>
      </div>
    )
  }

  const recRecommendation = recommendedHours(data.age)

  const fractionEdu = ratioToFraction(Number(data.eduRecRatio))
  const educationalHours = +(data.totalHours * fractionEdu).toFixed(2)
  const recreationalHours = +(data.totalHours - educationalHours).toFixed(2)

  const status = recreationalHours > recRecommendation ? 'Above recommended' : 'Within recommended'

  return (
    <div className="panel advisor">
      <h2>Personalized Recommendation</h2>
      <p><strong>Age:</strong> {data.age} years</p>
      <p><strong>Gender:</strong> {data.gender}</p>
      <p><strong>Primary device:</strong> {data.primaryDevice}</p>
      <p><strong>Total screen time:</strong> {data.totalHours} hour(s) / day</p>
      <p><strong>Educational hours:</strong> {educationalHours} hour(s) / day</p>
      <p><strong>Recreational hours:</strong> {recreationalHours} hour(s) / day</p>

      <div className="recommend">
        <h3>Recommended recreational screen time</h3>
        <div className="rec-hours">{recRecommendation} hour(s) / day</div>
        <div className={`status ${status === 'Above recommended' ? 'warn' : 'ok'}`}>
          {status}
        </div>
      </div>

      {data.healthImpacts && data.healthImpacts.length > 0 && (
        <div className="panel">
          <h4>Reported health impacts</h4>
          <ul>
            {data.healthImpacts.map((h, i) => <li key={i}>{h}</li>)}
          </ul>
        </div>
      )}

      {/** Prefer server-provided recommendations (check common response shapes),
          otherwise fall back to built-in suggestions. */}
      <div className="tips">
        <h4>Recommendations</h4>
        <ul>
          {(() => {
            const resp = data.serverResponse
            console.log('Advisor: serverResponse:', resp)
            const serverList = (resp && (resp.recommendations || (resp.details && resp.details.recommendations) || resp.insights)) || null
            console.log('Advisor: serverList extracted:', serverList)
            if (serverList && Array.isArray(serverList) && serverList.length > 0) {
              return serverList.map((r, i) => <li key={i}>{r}</li>)
            }

            // If no recommendations came from the server, show a helpful message
            return (
              <li>
                Server recommendations are not available. Ensure your backend is running on port 8000 and
                that the frontend environment variable `VITE_BACKEND_URL` is set (restart dev server after changing it).
              </li>
            )
          })()}
        </ul>
      </div>

      <div className="actions">
        <button className="btn" onClick={onBack}>Edit details</button>
      </div>

      {/* Removed debug server response rendering per UX cleanup request */}
    </div>
  )
}
