import React, { useState } from "react";
import InputForm from "./components/InputForm";
import Results from "./components/Results";

function App() {
  const [predictionData, setPredictionData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <h1 style={styles.title}>📱 Screen Time Predictor</h1>

        <InputForm
          setPredictionData={setPredictionData}
          setRecommendations={setRecommendations}
        />

        {predictionData && (
          <Results
            predictionData={predictionData}
            recommendations={recommendations}
          />
        )}
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "linear-gradient(to bottom right, #eef2ff, #dbeafe)",
    padding: "20px",
  },

  card: {
    width: "100%",
    maxWidth: "700px",
    backgroundColor: "#ffffff",
    borderRadius: "18px",
    padding: "35px",
    boxShadow: "0px 8px 30px rgba(0, 0, 0, 0.1)",
    display: "flex",
    flexDirection: "column",
    gap: "25px",
  },

  title: {
    textAlign: "center",
    fontSize: "28px",
    fontWeight: "bold",
    color: "#1e3a8a",
    marginBottom: "10px",
  },
};

export default App;
