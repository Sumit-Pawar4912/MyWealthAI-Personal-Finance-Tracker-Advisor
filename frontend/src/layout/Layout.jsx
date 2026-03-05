import { useState } from 'react'
import Sidebar from './Sidebar'
import Navbar from './Navbar'

/**
 * Layout Component
 * Main layout wrapper with sidebar and navbar
 */
export default function Layout({ children, userName = 'John Doe' }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar isOpen={sidebarOpen} onToggle={() => setSidebarOpen(!sidebarOpen)} />

      {/* Main Content */}
      <div className={`flex-1 flex flex-col ${!sidebarOpen ? 'ml-0' : ''}`}>
        {/* Navbar */}
        <Navbar userName={userName} />

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <div className="p-8">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
