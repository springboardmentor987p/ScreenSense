import { useState } from 'react'
import './App.css'
import './index.css'
import Sidebar from './Sidebar'
import Home from './Home'
import Advisor from './Advisor'
import Dashboard from './Dashboard'

function App() {
  const [route, setRoute] = useState('home')
  const [formData, setFormData] = useState(null)

  function handleNav(to) {
    setRoute(to)
  }

  function handleSubmit(data) {
    setFormData(data)
    setRoute('advisor')
  }

  return (
    <div className="app-root">
      <aside className="app-sidebar">
        <Sidebar onNavigate={handleNav} active={route} />
      </aside>
      <main className="app-main">
        <header className="app-header">
          <h1 className="brand">Indian Kids Screen Time</h1>
          <p className="subtitle">Healthy digital habits for growing children</p>
        </header>

        <section className="content">
          {route === 'home' && <Home onSubmit={handleSubmit} onNavigate={handleNav} />}
          {route === 'advisor' && <Advisor data={formData} onBack={() => setRoute('home')} />}
          {route === 'dashboard' && <Dashboard />}
        </section>
      </main>
    </div>
  )
}

export default App
