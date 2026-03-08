import { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import apiClient from '../services/apiClient'

export default function Sidebar({ isOpen = true, onToggle = () => {} }) {
  const location = useLocation()
  const [isAdmin, setIsAdmin] = useState(false)
  const [isMobile, setIsMobile] = useState(window.innerWidth < 1024)

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 1024)
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Auto-close sidebar on mobile when route changes
  useEffect(() => {
    if (isMobile) onToggle(false)
  }, [location.pathname])

  useEffect(() => {
    const checkAdmin = async () => {
      try {
        const res = await apiClient.get('/api/auth/profile')
        setIsAdmin(res.data.user.is_admin)
      } catch (err) {
        setIsAdmin(false)
      }
    }
    checkAdmin()
  }, [])

  const menuItems = [
    { icon: '📊', label: 'Dashboard', path: '/dashboard' },
    { icon: '➕', label: 'Add Transaction', path: '/add-transaction' },
    { icon: '💡', label: 'AI Advice', path: '/ai-advice' },
    { icon: '📈', label: 'Analytics', path: '/analytics' },
    { icon: '💬', label: 'Chat', path: '/chat' },
    { icon: '👤', label: 'Profile', path: '/profile' },
  ]

  const adminMenuItems = [
    { icon: '⚙️', label: 'Admin Panel', path: '/admin' },
  ]

  const isActive = (path) => location.pathname === path

  const sidebarVisible = isMobile ? isOpen : true
  const sidebarWidth = isMobile ? 'w-64' : (isOpen ? 'w-64' : 'w-20')

  return (
    <>
      {/* Mobile Overlay */}
      {isMobile && isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-30"
          onClick={() => onToggle(false)}
        />
      )}

      <aside
        className={`${sidebarWidth} bg-gray-900 text-white transition-all duration-300 min-h-screen flex flex-col fixed left-0 top-0 z-40
          ${isMobile ? (isOpen ? 'translate-x-0' : '-translate-x-full') : 'relative translate-x-0'}
        `}
      >
        {/* Logo Section */}
        <div className="flex items-center justify-between h-16 px-6 border-b border-gray-800">
          {(isOpen || !isMobile) && isOpen && (
            <h1 className="text-2xl font-bold text-primary-400">MyWealthAI</h1>
          )}
          <button
            onClick={() => onToggle(!isOpen)}
            className="text-gray-400 hover:text-white transition-colors ml-auto"
          >
            {isOpen ? '✕' : '☰'}
          </button>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 py-8 px-3 space-y-2">
          {menuItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-4 px-4 py-3 rounded-lg transition-colors duration-200 ${
                isActive(item.path)
                  ? 'bg-primary-600 text-white'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-white'
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              {isOpen && <span className="font-medium">{item.label}</span>}
            </Link>
          ))}

          {isAdmin && (
            <div className="my-4 border-t border-gray-800 pt-4">
              {isOpen && <p className="text-xs font-semibold text-gray-500 uppercase px-4 mb-2">Admin</p>}
              {adminMenuItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`flex items-center space-x-4 px-4 py-3 rounded-lg transition-colors duration-200 ${
                    isActive(item.path)
                      ? 'bg-amber-600 text-white'
                      : 'text-gray-400 hover:bg-gray-800 hover:text-white'
                  }`}
                >
                  <span className="text-xl">{item.icon}</span>
                  {isOpen && <span className="font-medium">{item.label}</span>}
                </Link>
              ))}
            </div>
          )}
        </nav>

        {/* Bottom Section */}
        <div className="border-t border-gray-800 p-4">
          <button className="w-full flex items-center justify-center space-x-2 px-4 py-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
            <span className="text-lg">🚪</span>
            {isOpen && <span>Logout</span>}
          </button>
        </div>
      </aside>
    </>
  )
}