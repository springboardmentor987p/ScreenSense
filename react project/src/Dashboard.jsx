import React, { useEffect, useState } from 'react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  Legend,
  ScatterChart,
  Scatter,
} from 'recharts'

function parseHealthList(s) {
  if (!s) return []
  if (typeof s !== 'string') return []
  return s.split(',').map(x => x.trim()).filter(Boolean)
}

function eduFractionFromRatio(r) {
  const v = Number(r)
  if (isNaN(v)) return 0
  if (v <= 1) return v
  return v / (1 + v)
}

export default function Dashboard() {
  const [rows, setRows] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedGender, setSelectedGender] = useState('All')
  const [selectedDevice, setSelectedDevice] = useState('All')
  const [selectedUrbanRural, setSelectedUrbanRural] = useState('All')
  const [hoveredBar, setHoveredBar] = useState(null)

  useEffect(() => {
    const backend = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000'
    console.log('Dashboard: fetching data from', `${backend}/data`)
    fetch(`${backend}/data`)
      .then((r) => {
        console.log('Dashboard: response status', r.status)
        return r.json()
      })
      .then((data) => {
        console.log('Dashboard: loaded', data?.length || 0, 'records')
        setRows(data || [])
      })
      .catch((err) => {
        console.warn('Could not load dataset for dashboard:', err)
        setRows([])
      })
      .finally(() => setLoading(false))
  }, [])

  // Apply filters
  const filteredRows = rows.filter((r) => {
    const genderMatch = selectedGender === 'All' || r.Gender === selectedGender
    const deviceMatch = selectedDevice === 'All' || r.Primary_Device === selectedDevice
    const urbanMatch = selectedUrbanRural === 'All' || r.Urban_or_Rural === selectedUrbanRural
    return genderMatch && deviceMatch && urbanMatch
  })

  // Get unique values for filters
  const genders = ['All', ...new Set(rows.map((r) => r.Gender).filter(Boolean))]
  const devices = ['All', ...new Set(rows.map((r) => r.Primary_Device).filter(Boolean))]
  const urbanRuralOptions = ['All', ...new Set(rows.map((r) => r.Urban_or_Rural).filter(Boolean))]

  // ===== Aggregations on FILTERED data =====

  const byAgeMap = {}
  const byAgeGenderMap = {}
  const byGenderMap = {}
  const deviceCounts = {}
  const healthCounts = {}
  const exceededByAge = {}
  const exceededByGender = {}
  const genderEduRecMap = {}

  filteredRows.forEach((r) => {
    const age = Number(r.Age)
    const gender = r.Gender || 'Unknown'
    const avg = Number(r.Avg_Daily_Screen_Time_hr) || 0
    const device = r.Primary_Device || 'Other'
    const exceeded = String(r.Exceeded_Recommended_Limit).toLowerCase() === 'true'
    const ratio = r.Educational_to_Recreational_Ratio
    const urbanRural = r.Urban_or_Rural || 'Urban'

    // By Age
    if (!byAgeMap[age]) byAgeMap[age] = { age, count: 0, sum: 0, sumEdu: 0 }
    byAgeMap[age].count += 1
    byAgeMap[age].sum += avg
    const eduFrac = eduFractionFromRatio(ratio)
    byAgeMap[age].sumEdu += avg * eduFrac

    // By Age & Gender
    if (!byAgeGenderMap[age]) byAgeGenderMap[age] = {}
    if (!byAgeGenderMap[age][gender]) {
      byAgeGenderMap[age][gender] = { count: 0, sum: 0 }
    }
    byAgeGenderMap[age][gender].count += 1
    byAgeGenderMap[age][gender].sum += avg

    // By Gender
    if (!byGenderMap[gender]) byGenderMap[gender] = { count: 0, sum: 0, exceededCount: 0, healthImpacts: {} }
    byGenderMap[gender].count += 1
    byGenderMap[gender].sum += avg
    if (exceeded) byGenderMap[gender].exceededCount += 1

    // Device
    deviceCounts[device] = (deviceCounts[device] || 0) + 1

    // Health
    const healths = parseHealthList(r.Health_Impacts)
    if (healths.length === 0) {
      healthCounts['None'] = (healthCounts['None'] || 0) + 1
      byGenderMap[gender].healthImpacts['None'] = (byGenderMap[gender].healthImpacts['None'] || 0) + 1
    } else {
      healths.forEach((h) => {
        healthCounts[h] = (healthCounts[h] || 0) + 1
        byGenderMap[gender].healthImpacts[h] = (byGenderMap[gender].healthImpacts[h] || 0) + 1
      })
    }

    // Exceeded by Age
    exceededByAge[age] = exceededByAge[age] || { age, count: 0, total: 0 }
    exceededByAge[age].total += 1
    if (exceeded) exceededByAge[age].count += 1

    // Exceeded by Gender
    exceededByGender[gender] = exceededByGender[gender] || { gender, count: 0, total: 0 }
    exceededByGender[gender].total += 1
    if (exceeded) exceededByGender[gender].count += 1

    // Gender Education/Recreational
    if (!genderEduRecMap[gender]) genderEduRecMap[gender] = { eduSum: 0, recSum: 0, count: 0 }
    genderEduRecMap[gender].eduSum += avg * eduFrac
    genderEduRecMap[gender].recSum += avg * (1 - eduFrac)
    genderEduRecMap[gender].count += 1
  })

  const ages = Object.values(byAgeMap).sort((a, b) => a.age - b.age)
  const ageSeries = ages.map((a) => ({
    age: a.age,
    avgHours: +(a.sum / a.count).toFixed(2),
    eduHours: +(a.sumEdu / a.count).toFixed(2),
    recHours: +((a.sum / a.count) - (a.sumEdu / a.count)).toFixed(2),
  }))

  const ageGenderSeriesFixed = ages.map((a) => {
    const row = { age: a.age }
    if (byAgeGenderMap[a.age]) {
      Object.entries(byAgeGenderMap[a.age]).forEach(([gender, data]) => {
        row[gender] = +(data.sum / data.count).toFixed(2)
      })
    }
    return row
  })

  const deviceData = Object.keys(deviceCounts).map((k) => ({ name: k, value: deviceCounts[k] }))
  const healthData = Object.keys(healthCounts)
    .map((k) => ({ name: k, value: healthCounts[k] }))
    .sort((a, b) => b.value - a.value)

  const exceededByAgeData = Object.values(exceededByAge).sort((a, b) => a.age - b.age)
  const exceededByGenderData = Object.values(exceededByGender)

  const genderEduRecData = Object.entries(genderEduRecMap).map(([gender, data]) => ({
    gender,
    Educational: +(data.eduSum / data.count).toFixed(2),
    Recreational: +(data.recSum / data.count).toFixed(2),
  }))

  const healthByGenderData = Object.entries(byGenderMap).map(([gender, data]) => ({
    gender,
    ...data.healthImpacts,
  }))

  const scatterData = filteredRows.map((r, i) => ({
    x: Number(r.Age),
    y: Number(r.Avg_Daily_Screen_Time_hr),
    id: i,
  }))

  const pieColors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f', '#edc949', '#b07aa1', '#ff9da7']
  const lineColors = ['#4e79a7', '#f28e2b', '#e15759', '#76b7b2', '#59a14f']

  if (loading) return <div className="panel">Loading dashboard…</div>

  const statsTotal = filteredRows.length
  const statsAvgScreenTime = statsTotal > 0 ? (filteredRows.reduce((sum, r) => sum + Number(r.Avg_Daily_Screen_Time_hr), 0) / statsTotal).toFixed(2) : 0
  const statsExceeded = filteredRows.filter((r) => String(r.Exceeded_Recommended_Limit).toLowerCase() === 'true').length
  const statsExceededPercent = statsTotal > 0 ? ((statsExceeded / statsTotal) * 100).toFixed(1) : 0

  return (
    <div className="dashboard-container" style={{ padding: '20px', backgroundColor: '#f8f9fa' }}>
      <h2 style={{ marginBottom: '20px', fontSize: '28px', fontWeight: 'bold' }}>📊 Screen Time Analytics Dashboard</h2>

      {/* Filter Controls */}
      <div style={{
        display: 'flex',
        gap: '20px',
        flexWrap: 'wrap',
        marginBottom: '30px',
        backgroundColor: 'white',
        padding: '16px',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      }}>
        <div>
          <label style={{ fontWeight: 'bold', marginRight: '8px' }}>Filter by Gender:</label>
          <select
            value={selectedGender}
            onChange={(e) => setSelectedGender(e.target.value)}
            style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #ddd', cursor: 'pointer' }}
          >
            {genders.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ fontWeight: 'bold', marginRight: '8px' }}>Filter by Device:</label>
          <select
            value={selectedDevice}
            onChange={(e) => setSelectedDevice(e.target.value)}
            style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #ddd', cursor: 'pointer' }}
          >
            {devices.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label style={{ fontWeight: 'bold', marginRight: '8px' }}>Filter by Area:</label>
          <select
            value={selectedUrbanRural}
            onChange={(e) => setSelectedUrbanRural(e.target.value)}
            style={{ padding: '8px 12px', borderRadius: '4px', border: '1px solid #ddd', cursor: 'pointer' }}
          >
            {urbanRuralOptions.map((ur) => (
              <option key={ur} value={ur}>
                {ur}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={() => {
            setSelectedGender('All')
            setSelectedDevice('All')
            setSelectedUrbanRural('All')
          }}
          style={{
            padding: '8px 16px',
            borderRadius: '4px',
            border: 'none',
            backgroundColor: '#f28e2b',
            color: 'white',
            cursor: 'pointer',
            fontWeight: 'bold',
          }}
        >
          Reset Filters
        </button>
      </div>

      {/* Summary Stats */}
      <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginBottom: '30px' }}>
        <div style={{ flex: 1, minWidth: '200px', backgroundColor: '#4e79a7', color: 'white', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{statsTotal}</div>
          <div style={{ fontSize: '14px' }}>Total Records</div>
        </div>
        <div style={{ flex: 1, minWidth: '200px', backgroundColor: '#59a14f', color: 'white', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{statsAvgScreenTime}h</div>
          <div style={{ fontSize: '14px' }}>Avg Daily Hours</div>
        </div>
        <div style={{ flex: 1, minWidth: '200px', backgroundColor: '#e15759', color: 'white', padding: '16px', borderRadius: '8px', textAlign: 'center' }}>
          <div style={{ fontSize: '24px', fontWeight: 'bold' }}>{statsExceeded}</div>
          <div style={{ fontSize: '14px' }}>Exceeded Limit ({statsExceededPercent}%)</div>
        </div>
      </div>

      {/* Row 1 */}
      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '30px' }}>
        <div style={{ flex: '1', minWidth: '400px', backgroundColor: 'white', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h4>Health Impacts by Gender</h4>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={healthByGenderData} margin={{ top: 16, right: 24, left: 8, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="gender" />
              <YAxis />
              <Tooltip cursor={{ fill: 'rgba(0,0,0,0.1)' }} />
              <Legend />
              {['None', 'Poor Sleep', 'Eye Strain', 'Anxiety', 'Obesity Risk'].map((h, idx) => (
                <Bar key={h} dataKey={h} stackId="a" fill={pieColors[idx % pieColors.length]} />
              ))}
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={{ flex: '1', minWidth: '400px', backgroundColor: 'white', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h4>Average Screen Time by Age & Gender</h4>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={ageGenderSeriesFixed} margin={{ top: 16, right: 24, left: 8, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="age" />
              <YAxis />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              {Object.keys(byGenderMap).map((gender, idx) => (
                <Line key={gender} type="monotone" dataKey={gender} stroke={lineColors[idx % lineColors.length]} strokeWidth={2} />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 2 */}
      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '30px' }}>
        <div style={{ flex: '1', minWidth: '400px', backgroundColor: 'white', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h4>Average Daily Screen Time by Age</h4>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={ageSeries} margin={{ top: 16, right: 24, left: 8, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="age" />
              <YAxis />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              <Line type="monotone" dataKey="avgHours" stroke="#4e79a7" name="Avg Daily Hours" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ flex: '0 0 360px', backgroundColor: 'white', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h4>Primary Device Distribution</h4>
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={deviceData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label={({ name, value }) => `${name}: ${value}`}
              >
                {deviceData.map((entry, idx) => (
                  <Cell key={`c-${idx}`} fill={pieColors[idx % pieColors.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 3 */}
      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '30px' }}>
        <div style={{ flex: '1', minWidth: '400px', backgroundColor: 'white', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h4>Exceeded Recommended Limit by Age</h4>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={exceededByAgeData} margin={{ top: 16, right: 24, left: 8, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="age" />
              <YAxis />
              <Tooltip cursor={{ fill: 'rgba(225, 87, 89, 0.1)' }} />
              <Bar dataKey="count" fill="#e15759" name="Count" onMouseEnter={(data) => setHoveredBar(data.age)} onMouseLeave={() => setHoveredBar(null)} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={{ flex: '1', minWidth: '400px', backgroundColor: 'white', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h4>Health Impacts Distribution</h4>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={healthData} layout="vertical" margin={{ top: 8, right: 30, left: 120, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={100} />
              <Tooltip cursor={{ fill: 'rgba(0,0,0,0.05)' }} />
              <Bar dataKey="value" fill="#4e79a7" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 4 */}
      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '30px' }}>
        <div style={{ flex: '1', minWidth: '400px', backgroundColor: 'white', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h4>Educational vs Recreational Time by Age</h4>
          <ResponsiveContainer width="100%" height={280}>
            <LineChart data={ageSeries} margin={{ top: 16, right: 24, left: 8, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="age" />
              <YAxis />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Legend />
              <Line type="monotone" dataKey="eduHours" stroke="#59a14f" name="Educational" strokeWidth={2} dot={{ r: 4 }} />
              <Line type="monotone" dataKey="recHours" stroke="#f28e2b" name="Recreational" strokeWidth={2} dot={{ r: 4 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div style={{ flex: '0 0 360px', backgroundColor: 'white', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h4>Education/Recreational by Gender</h4>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={genderEduRecData} margin={{ top: 16, right: 24, left: 8, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="gender" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="Educational" fill="#59a14f" />
              <Bar dataKey="Recreational" fill="#f28e2b" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 5 */}
      <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap', marginBottom: '30px' }}>
        <div style={{ flex: '1', minWidth: '400px', backgroundColor: 'white', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h4>Age vs Screen Time (Scatter)</h4>
          <ResponsiveContainer width="100%" height={280}>
            <ScatterChart margin={{ top: 16, right: 24, left: 8, bottom: 8 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="x" name="Age" type="number" />
              <YAxis dataKey="y" name="Screen Time (hr)" />
              <Tooltip cursor={{ strokeDasharray: '3 3' }} />
              <Scatter data={scatterData} fill="#4e79a7" opacity={0.6} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>

        <div style={{ flex: '1', minWidth: '400px', backgroundColor: 'white', padding: '16px', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
          <h4>Exceeded Limit by Gender</h4>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={exceededByGenderData} margin={{ top: 16, right: 24, left: 8, bottom: 40 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="gender" />
              <YAxis />
              <Tooltip cursor={{ fill: 'rgba(225, 87, 89, 0.1)' }} />
              <Bar dataKey="count" fill="#e15759" name="Exceeded" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div style={{ backgroundColor: 'white', padding: '16px', borderRadius: '8px', textAlign: 'center', marginTop: '20px' }}>
        <p style={{ fontSize: '12px', color: '#666' }}>📌 Hover over charts to explore data. Use filters to drill down into specific demographics.</p>
      </div>
    </div>
  )
}

