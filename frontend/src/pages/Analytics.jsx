import { useState, useEffect } from 'react'
import Layout from '../layout/Layout'
import apiClient from '../services/apiClient'
import { formatRupees } from '../utils/currency'

/**
 * Analytics Page
 * Machine Learning powered financial insights
 */
export default function Analytics() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [trends, setTrends] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [categories, setCategories] = useState(null)
  const [recommendations, setRecommendations] = useState([])
  const [anomalies, setAnomalies] = useState([])
  const [error, setError] = useState('')

  // Fetch user and analytics data
  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    try {
      setLoading(true)

      // Fetch user profile
      const userResponse = await apiClient.get('/api/auth/profile')
      setUser(userResponse.data.user)

      // Fetch analytics
      const [trendsRes, predictionRes, categoriesRes, recommendationsRes, anomaliesRes] = await Promise.all([
        apiClient.get('/api/analytics/spending-trends'),
        apiClient.get('/api/analytics/spending-prediction'),
        apiClient.get('/api/analytics/spending-by-category'),
        apiClient.get('/api/analytics/recommendations'),
        apiClient.get('/api/analytics/anomalies'),
      ])

      setTrends(trendsRes.data)
      setPrediction(predictionRes.data)
      setCategories(categoriesRes.data)
      setRecommendations(recommendationsRes.data.recommendations || [])
      setAnomalies(anomaliesRes.data.anomalies || [])
      setError('')
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load analytics')
      console.error('Analytics fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Layout userName={`${user?.first_name} ${user?.last_name}`.trim() || 'User'}>
        <div className="text-center py-8">
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </Layout>
    )
  }

  return (
    <Layout userName={`${user?.first_name} ${user?.last_name}`.trim() || 'User'}>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Financial Analytics</h1>
          <p className="text-gray-500 mt-2">AI-powered insights based on your spending patterns</p>
        </div>

        {error && (
          <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        {/* Spending Trends */}
        {trends && (
          <div className="card">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Spending Trends</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-gray-600 text-sm">Total Spent (30 days)</p>
                <p className="text-2xl font-bold text-gray-900">{formatRupees(trends.total_spent)}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-gray-600 text-sm">Daily Average</p>
                <p className="text-2xl font-bold text-gray-900">{formatRupees(trends.daily_average)}</p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-gray-600 text-sm">Trend</p>
                <p className={`text-2xl font-bold ${trends.trend === 'increasing' ? 'text-danger-600' : 'text-success-600'}`}>
                  {trends.trend === 'increasing' ? '📈 Up' : '📉 Down'}
                </p>
              </div>
              <div className="p-4 bg-gray-50 rounded-lg">
                <p className="text-gray-600 text-sm">Transactions</p>
                <p className="text-2xl font-bold text-gray-900">{trends.transaction_count}</p>
              </div>
            </div>
          </div>
        )}

        {/* Spending Prediction */}
        {prediction && (
          <div className="card">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Next Month Prediction</h2>
            <div className="p-6 bg-gradient-to-r from-primary-50 to-primary-100 rounded-lg">
              <p className="text-gray-600">Predicted Monthly Spending</p>
              <p className="text-4xl font-bold text-primary-600">{formatRupees(prediction.predicted_spending)}</p>
              <p className="text-gray-600 text-sm mt-2">Confidence: <span className="font-semibold text-gray-900">{prediction.confidence}</span></p>
            </div>
          </div>
        )}

        {/* Category Breakdown */}
        {categories && categories.categories && Object.keys(categories.categories).length > 0 && (
          <div className="card">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Spending by Category</h2>
            <div className="space-y-3">
              {Object.entries(categories.categories).map(([category, data]) => (
                <div key={category}>
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-medium text-gray-700">{category}</span>
                    <span className="text-gray-600">{formatRupees(data.amount)} ({data.percentage}%)</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-primary-600 h-2 rounded-full"
                      style={{ width: `${data.percentage}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
            <p className="text-gray-600 text-sm mt-4">Total: {formatRupees(categories.total)}</p>
          </div>
        )}

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <div className="card">
            <h2 className="text-lg font-bold text-gray-900 mb-4">AI Recommendations</h2>
            <div className="space-y-4">
              {recommendations.map((rec, index) => (
                <div
                  key={index}
                  className={`p-4 border-l-4 rounded-lg ${
                    rec.priority === 'high'
                      ? 'bg-red-50 border-red-400'
                      : rec.priority === 'medium'
                      ? 'bg-yellow-50 border-yellow-400'
                      : 'bg-green-50 border-green-400'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl">{rec.icon}</span>
                    <div>
                      <h3 className="font-bold text-gray-900">{rec.title}</h3>
                      <p className="text-gray-700 text-sm mt-1">{rec.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Anomalies */}
        {anomalies.length > 0 && (
          <div className="card">
            <h2 className="text-lg font-bold text-gray-900 mb-4">⚠️ Unusual Transactions</h2>
            <div className="space-y-3">
              {anomalies.map((anomaly, index) => (
                <div key={index} className="p-4 bg-red-50 rounded-lg border border-red-200">
                  <div className="flex justify-between items-start">
                    <div>
                      <p className="font-medium text-gray-900">{anomaly.description}</p>
                      <p className="text-sm text-gray-600 mt-1">{anomaly.category} • {anomaly.date}</p>
                      <p className="text-xs text-red-600 mt-2">{anomaly.reason}</p>
                    </div>
                    <p className="text-lg font-bold text-red-600">{formatRupees(anomaly.amount)}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* No Data */}
        {!loading && !trends && (
          <div className="card text-center py-8">
            <p className="text-gray-600">Add some transactions to see analytics insights</p>
          </div>
        )}
      </div>
    </Layout>
  )
}
