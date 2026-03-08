import { useState, useEffect } from 'react'
import Sidebar from './Sidebar'
import Navbar from './Navbar'

export default function Layout({ children, userName = 'John Doe' }) {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const isMobile = () => window.innerWidth < 1024

  // On desktop, open sidebar by default
  useEffect(() => {
    if (!isMobile()) setSidebarOpen(true)
  }, [])

  // Close sidebar on resize to mobile
  useEffect(() => {
    const handleResize = () => {
      if (isMobile()) setSidebarOpen(false)
      else setSidebarOpen(true)
    }
    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">

      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={(val) => setSidebarOpen(typeof val === 'boolean' ? val : !sidebarOpen)}
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">

        {/* Navbar */}
        <Navbar
          userName={userName}
          onMenuToggle={() => setSidebarOpen(!sidebarOpen)}
        />

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-4 md:p-8">
            {children}
          </div>
        </main>

      </div>
    </div>
  )
}