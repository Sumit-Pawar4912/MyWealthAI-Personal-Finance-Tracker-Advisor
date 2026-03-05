import { Link } from 'react-router-dom'

/**
 * Home Page
 * Landing page with information about MyWelthAI
 */
export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Navigation Bar */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-primary-600">MyWealthAI</span>
          </div>
          <div className="flex space-x-4">
            <Link
              to="/login"
              className="px-6 py-2 bg-gray-100 text-gray-900 rounded-lg hover:bg-gray-200 font-medium"
            >
              Sign In
            </Link>
            <Link
              to="/register"
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          <div>
            <h1 className="text-5xl font-bold text-gray-900 mb-6">
              Take Control of Your <span className="text-primary-600">Financial Future</span>
            </h1>
            <p className="text-xl text-gray-600 mb-8">
              MyWelthAI is an intelligent financial management platform powered by AI. Track expenses, get personalized financial advice, and make smarter money decisions.
            </p>
            <div className="flex gap-4">
              <Link
                to="/register"
                className="px-8 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-semibold text-lg"
              >
                Start Free Today
              </Link>
              <button className="px-8 py-3 bg-white text-primary-600 border-2 border-primary-600 rounded-lg hover:bg-primary-50 font-semibold text-lg">
                Watch Demo
              </button>
            </div>
          </div>
          <div className="bg-gradient-to-br from-primary-100 to-primary-50 rounded-2xl p-8 h-96 flex items-center justify-center">
            <div className="text-center">
              <img src="/assets/rupee-note.svg" alt="Indian currency illustration" className="w-80 lg:w-96 h-auto mx-auto" />
              <p className="text-gray-600 mt-4 font-semibold">Smart Financial Management</p>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            Powerful Features for Your Financial Goals
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="p-8 bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl hover:shadow-lg transition">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Smart Dashboard</h3>
              <p className="text-gray-700">
                Real-time overview of your income, expenses, and savings with beautiful charts and analytics.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="p-8 bg-gradient-to-br from-green-50 to-green-100 rounded-xl hover:shadow-lg transition">
              <div className="text-4xl mb-4">🤖</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">AI Financial Advice</h3>
              <p className="text-gray-700">
                Get personalized financial recommendations based on your spending patterns and goals.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="p-8 bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl hover:shadow-lg transition">
              <div className="text-4xl mb-4">📈</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Advanced Analytics</h3>
              <p className="text-gray-700">
                ML-powered spending predictions, anomaly detection, and trend analysis for better insights.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="p-8 bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-xl hover:shadow-lg transition">
              <div className="text-4xl mb-4">➕</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Easy Tracking</h3>
              <p className="text-gray-700">
                Quickly add income and expense transactions with automatic categorization and tagging.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="p-8 bg-gradient-to-br from-red-50 to-red-100 rounded-xl hover:shadow-lg transition">
              <div className="text-4xl mb-4">⚠️</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Smart Alerts</h3>
              <p className="text-gray-700">
                Get notified about unusual spending patterns and anomalies to avoid overspending.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="p-8 bg-gradient-to-br from-pink-50 to-pink-100 rounded-xl hover:shadow-lg transition">
              <div className="text-4xl mb-4">👤</div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Personal Profile</h3>
              <p className="text-gray-700">
                Manage your profile, view transaction history, and access all your financial data securely.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            How It Works
          </h2>

          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="bg-primary-600 text-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                1
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Register</h3>
              <p className="text-gray-600">
                Create your free account in seconds with your email and password.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-600 text-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                2
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Add Transactions</h3>
              <p className="text-gray-600">
                Start logging your income and expenses to build your financial profile.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-600 text-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                3
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Get Insights</h3>
              <p className="text-gray-600">
                View analytics dashboard and ML-powered predictions about your finances.
              </p>
            </div>

            <div className="text-center">
              <div className="bg-primary-600 text-white rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                4
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Take Action</h3>
              <p className="text-gray-600">
                Use AI recommendations to improve your spending and reach your financial goals.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="bg-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            Why Choose MyWelthAI?
          </h2>

          <div className="grid md:grid-cols-2 gap-12">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">✨ Key Benefits</h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <span className="text-green-600 text-2xl">✓</span>
                  <div>
                    <p className="font-semibold text-gray-900">100% Free to Start</p>
                    <p className="text-gray-600 text-sm">No credit card required for basic features</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-600 text-2xl">✓</span>
                  <div>
                    <p className="font-semibold text-gray-900">Secure & Private</p>
                    <p className="text-gray-600 text-sm">Your data is encrypted and never shared</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-600 text-2xl">✓</span>
                  <div>
                    <p className="font-semibold text-gray-900">AI-Powered Insights</p>
                    <p className="text-gray-600 text-sm">Machine learning analyzes your patterns</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-600 text-2xl">✓</span>
                  <div>
                    <p className="font-semibold text-gray-900">Indian Rupee Support</p>
                    <p className="text-gray-600 text-sm">All amounts displayed in INR (₹)</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-600 text-2xl">✓</span>
                  <div>
                    <p className="font-semibold text-gray-900">Mobile Friendly</p>
                    <p className="text-gray-600 text-sm">Access your finances on any device</p>
                  </div>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-6">📊 What You Get</h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3">
                  <span className="text-primary-600 text-2xl">📈</span>
                  <div>
                    <p className="font-semibold text-gray-900">Financial Dashboard</p>
                    <p className="text-gray-600 text-sm">Visualize your income, expenses, and savings</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-primary-600 text-2xl">🤖</span>
                  <div>
                    <p className="font-semibold text-gray-900">AI Recommendations</p>
                    <p className="text-gray-600 text-sm">Personalized financial advice just for you</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-primary-600 text-2xl">📊</span>
                  <div>
                    <p className="font-semibold text-gray-900">Advanced Analytics</p>
                    <p className="text-gray-600 text-sm">Spending trends, predictions, and anomalies</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-primary-600 text-2xl">➕</span>
                  <div>
                    <p className="font-semibold text-gray-900">Easy Expense Tracking</p>
                    <p className="text-gray-600 text-sm">Quick logging with auto-categorization</p>
                  </div>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-primary-600 text-2xl">🔒</span>
                  <div>
                    <p className="font-semibold text-gray-900">Secure Authentication</p>
                    <p className="text-gray-600 text-sm">JWT-based security for your account</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center text-gray-900 mb-16">
            Built with Modern Technology
          </h2>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Frontend</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• React 18 with Hooks</li>
                <li>• Vite 5 (Lightning fast)</li>
                <li>• Tailwind CSS</li>
                <li>• Chart.js for visualizations</li>
                <li>• React Router for navigation</li>
              </ul>
            </div>

            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Backend</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Flask 3.0</li>
                <li>• SQLAlchemy ORM</li>
                <li>• SQLite Database</li>
                <li>• JWT Authentication</li>
                <li>• RESTful API</li>
              </ul>
            </div>

            <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-200">
              <h3 className="text-xl font-bold text-gray-900 mb-4">Machine Learning</h3>
              <ul className="space-y-2 text-gray-600">
                <li>• Scikit-learn</li>
                <li>• Pandas for data analysis</li>
                <li>• NumPy for computations</li>
                <li>• Random Forest models</li>
                <li>• Statistical analysis</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-r from-primary-600 to-primary-700 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to Take Control of Your Finances?
          </h2>
          <p className="text-xl text-primary-100 mb-8 max-w-2xl mx-auto">
            Join thousands of users managing their money smarter with MyWelthAI. Start for free today!
          </p>
          <Link
            to="/register"
            className="inline-block px-8 py-4 bg-white text-primary-600 rounded-lg hover:bg-gray-100 font-bold text-lg transition"
          >
            Get Started Now →
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div>
              <h3 className="text-white font-bold mb-4">MyWelthAI</h3>
              <p className="text-sm">
                Your intelligent financial companion powered by AI.
              </p>
            </div>
            <div>
              <h4 className="text-white font-bold mb-4">Product</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Features</a></li>
                <li><a href="#" className="hover:text-white">Pricing</a></li>
                <li><a href="#" className="hover:text-white">Security</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-bold mb-4">Company</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">About</a></li>
                <li><a href="#" className="hover:text-white">Blog</a></li>
                <li><a href="#" className="hover:text-white">Contact</a></li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-bold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="hover:text-white">Privacy</a></li>
                <li><a href="#" className="hover:text-white">Terms</a></li>
                <li><a href="#" className="hover:text-white">Cookies</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 pt-8 text-center text-sm">
            <p>&copy; 2026 MyWelthAI. All rights reserved. Made with ❤️ for your financial freedom.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
