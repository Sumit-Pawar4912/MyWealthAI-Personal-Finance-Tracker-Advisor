import { useState, useEffect } from 'react'
import Layout from '../layout/Layout'
import BalanceCard from '../components/BalanceCard'
import IncomeCard from '../components/IncomeCard'
import ExpenseCard from '../components/ExpenseCard'
import SavingsCard from '../components/SavingsCard'
import IncomeVsExpenseChart from '../components/IncomeVsExpenseChart'
import ExpenseCategoryChart from '../components/ExpenseCategoryChart'
import apiClient from '../services/apiClient'
import { formatRupees } from '../utils/currency'

/**
 * Dashboard Page
 * Main dashboard displaying financial overview and charts
 */
export default function Dashboard() {
  const [user, setUser] = useState(null)
  // Sample data - In real app, this would come from API
  const [dashboardData, setDashboardData] = useState({
    balance: 15750.50,
    income: 6000,
    expense: 2400,
    incomeData: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      income: [5000, 5200, 5100, 5500, 5800, 6000],
      expenses: [2500, 2700, 2600, 2400, 2800, 2400],
    },
    expenseData: {
      labels: ['Food & Dining', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping'],
      values: [450, 300, 200, 150, 100, 1200],
    },
    recentTransactions: [
      {
        id: 1,
        type: 'expense',
        category: 'Food & Dining',
        description: 'Starbucks Coffee',
        amount: 5.50,
        date: '2024-01-27',
      },
      {
        id: 2,
        type: 'expense',
        category: 'Transportation',
        description: 'Gas',
        amount: 45.00,
        date: '2024-01-26',
      },
      {
        id: 3,
        type: 'income',
        category: 'Salary',
        description: 'Monthly Salary',
        amount: 6000.00,
        date: '2024-01-25',
      },
      {
        id: 4,
        type: 'expense',
        category: 'Entertainment',
        description: 'Movie Ticket',
        amount: 15.00,
        date: '2024-01-24',
      },
      {
        id: 5,
        type: 'expense',
        category: 'Utilities',
        description: 'Electricity Bill',
        amount: 85.00,
        date: '2024-01-23',
      },
    ],
  })

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
  }, [])

  // Fetch dashboard data from backend
  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [summaryRes, monthlyRes, txRes] = await Promise.all([
          apiClient.get('/api/dashboard/summary'),
          apiClient.get('/api/dashboard/monthly-data'),
          apiClient.get('/api/transactions?per_page=20'),
        ])

        const summary = summaryRes.data
        const monthly = monthlyRes.data || {}
        const recent = txRes.data.transactions || []

        // Normalize and sort month keys chronologically (old -> new)
        const monthKeys = Object.keys(monthly)
          .map((k) => ({ key: k, date: new Date(k + '-01') }))
          .sort((a, b) => a.date - b.date)
        const months = monthKeys.map((m) => {
          const d = m.date
          return d.toLocaleString(undefined, { month: 'short', year: 'numeric' })
        })

        const income = monthKeys.map((m) => monthly[m.key].income || 0)
        const expenses = monthKeys.map((m) => monthly[m.key].expense || 0)

        // Build expense category data
        const expenseCategories = Object.entries(summary.categories || {}).map(([k, v]) => ({ label: k, value: v }))

        setDashboardData((prev) => ({
          ...prev,
          balance: summary.cumulative_balance ?? summary.balance ?? prev.balance,
          income: summary.income ?? prev.income,
          expense: summary.expense ?? prev.expense,
          incomeData: {
            labels: months.length ? months : prev.incomeData.labels,
            income: income.length ? income : prev.incomeData.income,
            expenses: expenses.length ? expenses : prev.incomeData.expenses,
          },
          expenseData: {
            labels: expenseCategories.length ? expenseCategories.map((c) => c.label) : prev.expenseData.labels,
            values: expenseCategories.length ? expenseCategories.map((c) => c.value) : prev.expenseData.values,
          },
          recentTransactions: recent,
        }))
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err)
      }
    }

    fetchDashboard()
  }, [])

  const getCategoryColor = (type) => {
    return type === 'income' ? 'text-success-600' : 'text-danger-600'
  }

  const getCategoryBgColor = (type) => {
    return type === 'income' ? 'bg-success-100' : 'bg-danger-100'
  }

  return (
    <Layout userName={`${user?.first_name} ${user?.last_name}`.trim() || 'User'}>
      <div className="space-y-8">
        {/* Page Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-500 mt-2">Welcome back! Here's your financial overview.</p>
          </div>
          <button 
            onClick={async () => {
              try {
                const token = localStorage.getItem('authToken')
                if (!token) {
                  alert('Please log in to download reports')
                  return
                }
                const res = await apiClient.get('/api/report/transactions', { responseType: 'blob' })
                const url = window.URL.createObjectURL(new Blob([res.data]))
                const link = document.createElement('a')
                link.href = url
                const cd = res.headers['content-disposition'] || ''
                const match = cd.match(/filename=(.*)/)
                const filename = match ? match[1].replace(/"/g, '') : 'transactions.csv'
                link.setAttribute('download', filename)
                document.body.appendChild(link)
                link.click()
                link.remove()
                window.URL.revokeObjectURL(url)
              } catch (err) {
                console.error('Failed to download report:', err)
                const errorMsg = err.response?.data?.error || err.message || 'Failed to download report'
                alert('Error: ' + errorMsg)
              }
            }}
            className="btn-primary flex items-center gap-2"
          >
            <span>📥</span>
            <span>Download Report</span>
          </button>
        </div>

        {/* Summary Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <BalanceCard balance={dashboardData.balance} />
          <IncomeCard income={dashboardData.income} />
          <ExpenseCard expense={dashboardData.expense} />
          <SavingsCard income={dashboardData.income} expense={dashboardData.expense} />
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <IncomeVsExpenseChart data={dashboardData.incomeData} />
          <ExpenseCategoryChart data={dashboardData.expenseData} />
        </div>

        {/* Recent Transactions */}
        <div className="card">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-bold text-gray-900">Recent Transactions</h3>
            <div className="flex items-center gap-4">
              <button 
                onClick={async () => {
                  try {
                    const token = localStorage.getItem('authToken')
                    if (!token) {
                      alert('Please log in to download reports')
                      return
                    }
                    const res = await apiClient.get('/api/report/transactions', { responseType: 'blob' })
                    if (res.data.size === 0) {
                      alert('No transactions to download')
                      return
                    }
                    const url = window.URL.createObjectURL(new Blob([res.data]))
                    const link = document.createElement('a')
                    link.href = url
                    const cd = res.headers['content-disposition'] || ''
                    const match = cd.match(/filename=(.*)/)
                    const filename = match ? match[1].replace(/"/g, '') : 'transactions.csv'
                    link.setAttribute('download', filename)
                    document.body.appendChild(link)
                    link.click()
                    link.remove()
                    window.URL.revokeObjectURL(url)
                    alert('Report downloaded successfully!')
                  } catch (err) {
                    console.error('Failed to download report:', err)
                    const errorMsg = err.response?.data?.error || err.message || 'Failed to download report'
                    alert('Error: ' + errorMsg)
                  }
                }} 
                className="btn-secondary flex items-center gap-2"
              >
                <span>📥</span>
                <span>Download Report</span>
              </button>
              <a href="/add-transaction" className="text-primary-600 hover:text-primary-700 font-medium">
                View All →
              </a>
            </div>
          </div>

          {/* Transactions Table */}
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                    Description
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                    Category
                  </th>
                  <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">
                    Date
                  </th>
                  <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">
                    Amount
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {dashboardData.recentTransactions.map((transaction) => (
                  <tr key={transaction.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-4 py-4">
                      <div className="flex items-center space-x-3">
                        <div
                          className={`w-10 h-10 rounded-full flex items-center justify-center ${getCategoryBgColor(
                            transaction.type
                          )}`}
                        >
                          <span className="text-lg">
                            {transaction.type === 'income' ? '↓' : '↑'}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">
                            {transaction.description}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-4">
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                        {transaction.category}
                      </span>
                    </td>
                    <td className="px-4 py-4 text-gray-500 text-sm">
                      {new Date(transaction.date).toLocaleDateString()}
                    </td>
                    <td className={`px-4 py-4 text-right font-semibold ${getCategoryColor(
                      transaction.type
                    )}`}>
                      {transaction.type === 'income' ? '+' : '-'}
                      {formatRupees(transaction.amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Stats */}
        {
          (() => {
            const recent = dashboardData.recentTransactions || []
            const income = dashboardData.income || 0
            const expense = dashboardData.expense || 0
            const today = new Date()
            const daysPassed = today.getDate() || 1
            const avgDaily = expense > 0 ? expense / daysPassed : 0

            // Largest expense from recent transactions
            const expenseTx = recent.filter((t) => t.type === 'expense')
            let largest = null
            if (expenseTx.length) {
              largest = expenseTx.reduce((max, t) => (t.amount > (max?.amount || 0) ? t : max), null)
            }

            const budgetRemaining = Math.max(0, income - expense)
            const budgetPercent = income > 0 ? Math.round((budgetRemaining / income) * 100) : 0

            return (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="card">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Average Daily Spending</h4>
                  <p className="text-2xl font-bold text-gray-900">{formatRupees(avgDaily)}</p>
                  <p className="text-xs text-gray-500 mt-2">{`Based on ${daysPassed} days this month`}</p>
                </div>
                <div className="card">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Largest Expense</h4>
                  <p className="text-2xl font-bold text-danger-600">{largest ? formatRupees(largest.amount) : '—'}</p>
                  <p className="text-xs text-gray-500 mt-2">{largest ? `${largest.category} - ${new Date(largest.date).toLocaleDateString()}` : 'No expense transactions'}</p>
                </div>
                <div className="card">
                  <h4 className="text-sm font-semibold text-gray-700 mb-2">Budget Remaining</h4>
                  <p className="text-2xl font-bold text-success-600">{formatRupees(budgetRemaining)}</p>
                  <p className="text-xs text-gray-500 mt-2">{budgetPercent}% of monthly income</p>
                </div>
              </div>
            )
          })()
        }
      </div>
    </Layout>
  )
}
