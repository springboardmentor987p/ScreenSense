const Results = ({ predictionData, recommendations }) => {
  const { predicted_screen_time, risk_score, high_risk, total_screen_time } = predictionData;

  const riskColor = high_risk ? "#f44336" : risk_score > 0.5 ? "#ff9800" : "#4caf50";

  return (
    <div style={{ marginTop: "30px", padding: "20px", border: "1px solid #ccc", borderRadius: "8px" }}>
      <h3>Prediction Results</h3>
      <p>Total Screen Time: <strong>{total_screen_time} hrs</strong></p>
      <p>Predicted Screen Time: <strong>{predicted_screen_time.toFixed(2)} hrs</strong></p>
      <p>Risk Score: <strong style={{ color: riskColor }}>{(risk_score * 100).toFixed(1)}%</strong></p>
      <p>High Risk: <strong>{high_risk ? "Yes" : "No"}</strong></p>

      <h3 style={{ marginTop: "20px" }}>Recommendations</h3>
      <ul>
        {recommendations.map((rec, idx) => (
          <li key={idx}>{rec}</li>
        ))}
      </ul>
    </div>
  );
};

export default Results;
