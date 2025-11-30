import React from 'react'
import FormComponents from './FormComponents'

export default function Home({ onSubmit }) {
  return (
    <div className="home">
      <section className="intro panel">
        <h2>Welcome</h2>
        <p>
          Use the Screen Time Advisor to get simple, age-appropriate
          recommendations for balancing educational and recreational
          screen use.
        </p>
      </section>

      <section className="panel">
        <h3>Tell us about the child</h3>
        <FormComponents onSubmit={onSubmit} />
      </section>
    </div>
  )
}
