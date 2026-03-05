import { useState, useEffect } from 'react'
import Layout from '../layout/Layout'
import apiClient from '../services/apiClient'

/**
 * AI Advice Page
 * Page displaying AI-generated financial advice
 */
export default function AIAdvice() {
  const [user, setUser] = useState(null)
  const [overspendingRisk, setOverspendingRisk] = useState(null)

  // Fetch user profile on mount
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await apiClient.get('/api/auth/profile')
        setUser(response.data.user)
      } catch (err) {
        console.error('Failed to fetch user:', err)
      }
    }
    fetchUser()
    // Fetch overspending risk
    const fetchRisk = async () => {
      try {
        const res = await apiClient.get('/api/analytics/overspending-risk')
        setOverspendingRisk(res.data)
      } catch (err) {
        console.error('Failed to fetch overspending risk:', err)
      }
    }
    fetchRisk()
  }, [])
  const adviceItems = [
    {
      title: 'Increase Savings Rate',
      description: 'Your current savings rate is 20%. Try to increase it to 25% by reducing discretionary spending.',
      icon: '💰',
      priority: 'high',
    },
    {
      title: 'Food Spending Alert',
      description: 'Food & dining expenses increased by 15% this month. Consider meal planning to save money.',
      icon: '🍽️',
      priority: 'medium',
    },
    {
      title: 'Transportation Opportunity',
      description: 'You could save $150/month by optimizing transportation habits.',
      icon: '🚗',
      priority: 'medium',
    },
  ]

  return (
    <Layout userName={`${user?.first_name} ${user?.last_name}`.trim() || 'User'}>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">AI Financial Advice</h1>
          <p className="text-gray-500 mt-2">Personalized recommendations based on your spending patterns</p>
        </div>

        <div className="grid gap-6">
          {overspendingRisk && (
            <div className="card border-l-4 border-primary-600">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-bold">Overspending Risk</h3>
                  <p className="text-sm text-gray-600">Score: {overspendingRisk.risk_score ?? '—'} — {overspendingRisk.risk_label ?? '—'}</p>
                </div>
              </div>
            </div>
          )}
          {adviceItems.map((advice, index) => (
            <div key={index} className="card border-l-4 border-primary-600">
              <div className="flex items-start gap-4">
                <span className="text-4xl">{advice.icon}</span>
                <div className="flex-1">
                  <h3 className="text-lg font-bold text-gray-900 mb-2">{advice.title}</h3>
                  <p className="text-gray-600">{advice.description}</p>
                  <div className="mt-4 flex items-center gap-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      advice.priority === 'high'
                        ? 'bg-danger-100 text-danger-600'
                        : 'bg-yellow-100 text-yellow-600'
                    }`}>
                      {advice.priority.charAt(0).toUpperCase() + advice.priority.slice(1)} Priority
                    </span>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </Layout>
  )
}
