import React, { useState } from "react";
import axios from "axios";

const InputForm = ({ setPredictionData, setRecommendations }) => {
  const [formData, setFormData] = useState({
    age: "",
    gender: "Male",
    device_type: "Phone",
    educational_screentime: "",
    recreational_screentime: ""
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const predictRes = await axios.post("http://127.0.0.1:8000/predict", formData);
      setPredictionData(predictRes.data);

      const recRes = await axios.post("http://127.0.0.1:8000/recommend", formData);
      setRecommendations(recRes.data.recommendations);
    } catch (err) {
      console.error(err);
      alert("Error fetching prediction. Make sure the backend is running.");
    }
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      <h2 style={styles.header}>✨ Enter Child Screen Time Details</h2>

      {/* Age */}
      <div style={styles.group}>
        <label style={styles.label}>Age</label>
        <input
          type="number"
          name="age"
          value={formData.age}
          onChange={handleChange}
          style={styles.input}
          required
        />
      </div>

      {/* Gender */}
      <div style={styles.group}>
        <label style={styles.label}>Gender</label>
        <select
          name="gender"
          value={formData.gender}
          onChange={handleChange}
          style={styles.select}
        >
          <option>Male</option>
          <option>Female</option>
        </select>
      </div>

      {/* Device Type */}
      <div style={styles.group}>
        <label style={styles.label}>Device Type</label>
        <select
          name="device_type"
          value={formData.device_type}
          onChange={handleChange}
          style={styles.select}
        >
          <option>Phone</option>
          <option>Tablet</option>
          <option>TV</option>
        </select>
      </div>

      {/* Educational Time */}
      <div style={styles.group}>
        <label style={styles.label}>Educational Screen Time (hrs)</label>
        <input
          type="number"
          step="0.1"
          name="educational_screentime"
          value={formData.educational_screentime}
          onChange={handleChange}
          style={styles.input}
          required
        />
      </div>

      {/* Recreational Time */}
      <div style={styles.group}>
        <label style={styles.label}>Recreational Screen Time (hrs)</label>
        <input
          type="number"
          step="0.1"
          name="recreational_screentime"
          value={formData.recreational_screentime}
          onChange={handleChange}
          style={styles.input}
          required
        />
      </div>

      {/* Button */}
      <button type="submit" style={styles.button}>
        🚀 Predict
      </button>
    </form>
  );
};

const styles = {
  form: {
    display: "flex",
    flexDirection: "column",
    gap: "18px",
    padding: "25px",
    borderRadius: "18px",
    background: "linear-gradient(to right, #e0f2fe, #f0f9ff)",
    boxShadow: "0px 8px 25px rgba(0,0,0,0.1)",
  },

  header: {
    textAlign: "center",
    color: "#0f172a",
    marginBottom: "10px",
    fontWeight: "700",
  },

  group: {
    display: "flex",
    flexDirection: "column",
    gap: "6px",
  },

  label: {
    fontSize: "15px",
    fontWeight: "600",
    color: "#1e293b",
  },

  input: {
    padding: "12px",
    borderRadius: "10px",
    border: "1px solid #cbd5e1",
    fontSize: "15px",
    outline: "none",
    background: "#fff",
    transition: "0.25s",
  },

  select: {
    padding: "12px",
    borderRadius: "10px",
    border: "1px solid #cbd5e1",
    fontSize: "15px",
    background: "#fff",
  },

  button: {
    marginTop: "10px",
    padding: "14px",
    background:
      "linear-gradient(90deg, #3b82f6, #2563eb)",
    color: "white",
    border: "none",
    borderRadius: "12px",
    cursor: "pointer",
    fontSize: "17px",
    fontWeight: "600",
    transition: "0.3s",
  },
};

export default InputForm;



