import { Navigate } from 'react-router-dom'

/**
 * ProtectedRoute Component
 * Ensures user is logged in before accessing a page
 */
export default function ProtectedRoute({ children }) {
  const token = localStorage.getItem('authToken')

  // If no token, redirect to login
  if (!token) {
    return <Navigate to="/login" replace />
  }

  // If token exists, show the page
  return children
}
