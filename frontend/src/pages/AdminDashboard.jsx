import { useState, useEffect } from 'react'
import Layout from '../layout/Layout'
import apiClient from '../services/apiClient'

/**
 * Admin Dashboard
 * Admin-only panel for managing users and system statistics
 */
export default function AdminDashboard() {
  const [user, setUser] = useState(null)
  const [stats, setStats] = useState(null)
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selectedUser, setSelectedUser] = useState(null)
  const [resetPassword, setResetPassword] = useState(false)
  const [newPassword, setNewPassword] = useState('')

  // Fetch admin stats and users on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Get current user
        const profileRes = await apiClient.get('/api/auth/profile')
        setUser(profileRes.data.user)

        // Check if admin
        if (!profileRes.data.user.is_admin) {
          setError('Access denied: admin privileges required')
          return
        }

        // Get stats
        const statsRes = await apiClient.get('/api/admin/stats')
        setStats(statsRes.data)

        // Get users
        const usersRes = await apiClient.get('/api/admin/users?per_page=100')
        setUsers(usersRes.data.users)
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load admin data')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  const handleResetPassword = async (userId) => {
    if (!newPassword) {
      alert('Enter a new password')
      return
    }
    try {
      await apiClient.post(`/api/admin/users/${userId}/reset-password`, {
        password: newPassword
      })
      alert('Password reset successfully')
      setResetPassword(false)
      setNewPassword('')
      setSelectedUser(null)
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to reset password')
    }
  }

  const handleToggleAdmin = async (userId) => {
    try {
      const res = await apiClient.post(`/api/admin/users/${userId}/toggle-admin`)
      // Refresh users list
      const usersRes = await apiClient.get('/api/admin/users?per_page=100')
      setUsers(usersRes.data.users)
      setSelectedUser(res.data.user)
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to toggle admin status')
    }
  }

  const handleDeleteUser = async (userId, email) => {
    if (!window.confirm(`Are you sure you want to delete ${email}? This cannot be undone.`)) {
      return
    }
    try {
      await apiClient.delete(`/api/admin/users/${userId}`)
      const usersRes = await apiClient.get('/api/admin/users?per_page=100')
      setUsers(usersRes.data.users)
      setSelectedUser(null)
      alert('User deleted successfully')
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to delete user')
    }
  }

  if (loading) {
    return (
      <Layout userName={user ? `${user.first_name} ${user.last_name}` : 'Admin'}>
        <div className="flex items-center justify-center h-screen">
          <p>Loading...</p>
        </div>
      </Layout>
    )
  }

  if (error) {
    return (
      <Layout userName={user ? `${user.first_name} ${user.last_name}` : 'Admin'}>
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      </Layout>
    )
  }

  return (
    <Layout userName={`${user?.first_name} ${user?.last_name}`}>
      <div className="space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
          <p className="text-gray-500 mt-2">System management and user administration</p>
        </div>

        {/* System Stats */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6">
            <div className="card">
              <p className="text-gray-600 text-sm">Total Users</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{stats.total_users}</p>
            </div>
            <div className="card">
              <p className="text-gray-600 text-sm">Admins</p>
              <p className="text-2xl font-bold text-primary-600 mt-2">{stats.admin_count}</p>
            </div>
            <div className="card">
              <p className="text-gray-600 text-sm">Transactions</p>
              <p className="text-2xl font-bold text-gray-900 mt-2">{stats.total_transactions}</p>
            </div>
            <div className="card">
              <p className="text-gray-600 text-sm">Total Income</p>
              <p className="text-2xl font-bold text-green-600 mt-2">₹{stats.total_income.toFixed(2)}</p>
            </div>
            <div className="card">
              <p className="text-gray-600 text-sm">Total Expenses</p>
              <p className="text-2xl font-bold text-red-600 mt-2">₹{stats.total_expenses.toFixed(2)}</p>
            </div>
          </div>
        )}

        {/* Users Management */}
        <div>
          <h2 className="text-2xl font-bold mb-4">Users Management</h2>
          <div className="card overflow-x-auto">
            <table className="w-full">
              <thead className="border-b">
                <tr>
                  <th className="text-left py-3 px-4">Email</th>
                  <th className="text-left py-3 px-4">Name</th>
                  <th className="text-left py-3 px-4">Status</th>
                  <th className="text-left py-3 px-4">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b hover:bg-gray-50">
                    <td className="py-3 px-4">{u.email}</td>
                    <td className="py-3 px-4">{u.first_name} {u.last_name}</td>
                    <td className="py-3 px-4">
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        u.is_admin ? 'bg-blue-100 text-blue-700' : 'bg-gray-100 text-gray-700'
                      }`}>
                        {u.is_admin ? 'Admin' : 'User'}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <button
                        onClick={() => setSelectedUser(u)}
                        className="text-primary-600 hover:text-primary-700 font-medium"
                      >
                        Manage
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* User Details Modal */}
        {selectedUser && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
            <div className="card max-w-md w-full">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold">{selectedUser.email}</h3>
                <button
                  onClick={() => {
                    setSelectedUser(null)
                    setResetPassword(false)
                    setNewPassword('')
                  }}
                  className="text-gray-500 hover:text-gray-700"
                >
                  ✕
                </button>
              </div>

              <p className="text-gray-600 mb-4">
                {selectedUser.first_name} {selectedUser.last_name}
              </p>

              {resetPassword ? (
                <div className="space-y-3 mb-4">
                  <label className="block">
                    <span className="text-sm font-medium text-gray-700">New Password</span>
                    <input
                      type="password"
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      className="mt-1 input-field"
                      placeholder="Enter new password"
                    />
                  </label>
                  <button
                    onClick={() => handleResetPassword(selectedUser.id)}
                    className="btn-primary w-full"
                  >
                    Confirm Reset
                  </button>
                  <button
                    onClick={() => {
                      setResetPassword(false)
                      setNewPassword('')
                    }}
                    className="btn-secondary w-full"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <div className="space-y-2">
                  <button
                    onClick={() => setResetPassword(true)}
                    className="btn-secondary w-full"
                  >
                    Reset Password
                  </button>
                  <button
                    onClick={() => handleToggleAdmin(selectedUser.id)}
                    className="btn-secondary w-full"
                  >
                    {selectedUser.is_admin ? 'Remove Admin' : 'Make Admin'}
                  </button>
                  <button
                    onClick={() => handleDeleteUser(selectedUser.id, selectedUser.email)}
                    className="btn-danger w-full"
                  >
                    Delete User
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </Layout>
  )
}
