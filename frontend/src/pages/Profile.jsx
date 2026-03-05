import { useState, useEffect } from 'react'
import Layout from '../layout/Layout'
import apiClient from '../services/apiClient'

/**
 * Profile Page
 * User profile and settings page
 */
export default function Profile() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
  })
  const [saving, setSaving] = useState(false)
  const [successMessage, setSuccessMessage] = useState('')

  // Fetch user profile on mount
  useEffect(() => {
    fetchUserProfile()
  }, [])

  const fetchUserProfile = async () => {
    try {
      setLoading(true)
      const response = await apiClient.get('/api/auth/profile')
      setUser(response.data.user)
      setFormData({
        first_name: response.data.user.first_name || '',
        last_name: response.data.user.last_name || '',
        email: response.data.user.email || '',
        phone: response.data.user.phone || '',
      })
      setError('')
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load profile')
      console.error('Profile fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setSuccessMessage('')

    try {
      const response = await apiClient.put('/api/auth/profile', formData)
      setUser(response.data.user)
      setSuccessMessage('Profile updated successfully!')
      setTimeout(() => setSuccessMessage(''), 3000)
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update profile')
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <Layout userName={user?.first_name || 'User'}>
        <div className="text-center py-8">
          <p className="text-gray-600">Loading profile...</p>
        </div>
      </Layout>
    )
  }

  return (
    <Layout userName={`${user?.first_name} ${user?.last_name}`.trim() || 'User'}>
      <div className="max-w-2xl">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Profile Settings</h1>
        
        {error && (
          <div className="p-4 bg-red-100 border border-red-400 text-red-700 rounded mb-6">
            {error}
          </div>
        )}

        {successMessage && (
          <div className="p-4 bg-green-100 border border-green-400 text-green-700 rounded mb-6">
            {successMessage}
          </div>
        )}
        
        <div className="card mb-6">
          <h2 className="text-lg font-bold text-gray-900 mb-6">Personal Information</h2>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-2 gap-6">
              <div>
                <label className="label">First Name</label>
                <input 
                  type="text" 
                  name="first_name"
                  value={formData.first_name}
                  onChange={handleChange}
                  className="input-field" 
                />
              </div>
              <div>
                <label className="label">Last Name</label>
                <input 
                  type="text" 
                  name="last_name"
                  value={formData.last_name}
                  onChange={handleChange}
                  className="input-field" 
                />
              </div>
            </div>
            <div>
              <label className="label">Email</label>
              <input 
                type="email" 
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="input-field"
                disabled
              />
            </div>
            <div>
              <label className="label">Phone</label>
              <input 
                type="tel" 
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="input-field" 
              />
            </div>
            <button 
              type="submit" 
              disabled={saving}
              className="btn-primary disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Save Changes'}
            </button>
          </form>
        </div>

        <div className="card">
          <h2 className="text-lg font-bold text-gray-900 mb-6">Account</h2>
          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-600">Member Since</p>
              <p className="text-gray-900">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'N/A'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  )
}
