import { useState } from "react";
import confetti from "canvas-confetti";
import "./App.css";

function App() {
  const [form, setForm] = useState({
    age: "",
    gender: "",
    device: "",
    edu_time: "",
    rec_time: "",
  });

  const [result, setResult] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      const response = await fetch("http://127.0.0.1:8000/Recommendations ", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      const data = await response.json();

      if (Array.isArray(data.Result)) {
        setResult(data.Result.join("\n"));
      } else {
        setResult(data.Result);
      }

      // 🎉 CONFETTI (paper blast)
      confetti({
        particleCount: 300,
        spread: 90,
        origin: { y: 0.6 }
      });

    } catch (err) {
      console.error(err);
      setResult("⚠️ Backend not responding.");
    }
  };

  return (
    <div className="page">
      <div className="card">
        <h2 className="title">📚 Student Recommendation System</h2>

        <form onSubmit={handleSubmit} className="form">
          <input type="number" name="age" placeholder="Age" value={form.age} onChange={handleChange} required />
          <select name="gender" value={form.gender} onChange={handleChange} required>
            <option value="">Gender</option>
            <option>Male</option>
            <option>Female</option>
          </select>
          <select name="device" value={form.device} onChange={handleChange} required>
            <option value="">Primary Device</option>
            <option>Smartphone</option>
            <option>Laptop</option>
            <option>Tablet</option>
            <option>TV</option>
          </select>
          <input type="number" name="edu_time" placeholder="Study Time" value={form.edu_time} onChange={handleChange} required />
          <input type="number" name="rec_time" placeholder="Recreation Time" value={form.rec_time} onChange={handleChange} required />

          <button className="btn">Get Recommendation</button>
        </form>

        {result && <pre className="output">{result}</pre>}
      </div>
    </div>
  );
}

export default App;
