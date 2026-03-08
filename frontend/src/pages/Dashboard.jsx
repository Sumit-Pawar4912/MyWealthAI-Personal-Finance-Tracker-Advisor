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

export default function Dashboard() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [dashboardData, setDashboardData] = useState({
    balance: 0,
    income: 0,
    expense: 0,
    incomeData: null,
    expenseData: null,
    recentTransactions: [],
  })

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

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        setLoading(true)
        const [summaryRes, monthlyRes, txRes] = await Promise.all([
          apiClient.get('/api/dashboard/summary'),
          apiClient.get('/api/dashboard/monthly-data'),
          apiClient.get('/api/transactions?per_page=20'),
        ])

        // DEBUG LINES
        console.log('Monthly Data:', JSON.stringify(monthlyRes.data))
        console.log('Summary:', JSON.stringify(summaryRes.data))

        const summary = summaryRes.data
        const monthly = monthlyRes.data || {}
        const recent = txRes.data.transactions || []

        const monthKeys = Object.keys(monthly)
          .map((k) => ({ key: k, date: new Date(k + '-01') }))
          .sort((a, b) => a.date - b.date)

        const months = monthKeys.map((m) =>
          m.date.toLocaleString(undefined, { month: 'short', year: 'numeric' })
        )

        const income = monthKeys.map((m) => monthly[m.key].income || 0)
        const expenses = monthKeys.map((m) => monthly[m.key].expense || 0)

        const allExpenseRes = await apiClient.get('/api/transactions?per_page=1000')
        const allTransactions = allExpenseRes.data.transactions || []
        const allCategories = {}
        allTransactions.forEach((t) => {
          if (t.type === 'expense') {
            allCategories[t.category] = (allCategories[t.category] || 0) + t.amount
          }
        })

        const summaryCategories = Object.entries(summary.categories || {})
        const categorySource = summaryCategories.length > 0
          ? summaryCategories
          : Object.entries(allCategories)

        setDashboardData({
          balance: summary.cumulative_balance ?? summary.balance ?? 0,
          income: summary.income ?? 0,
          expense: summary.expense ?? 0,
          incomeData: {
            labels: months,
            income: income,
            expenses: expenses,
          },
          expenseData: categorySource.length > 0 ? {
            labels: categorySource.map(([k]) => k),
            values: categorySource.map(([, v]) => v),
          } : null,
          recentTransactions: recent,
        })
      } catch (err) {
        console.error('Failed to fetch dashboard data:', err)
      } finally {
        setLoading(false)
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

        {loading && (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        )}

        {!loading && (
          <>
            <div className="flex justify-between items-center">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
                <p className="text-gray-500 mt-2">Welcome back! Here's your financial overview.</p>
              </div>
              <button
                onClick={async () => {
                  try {
                    const token = localStorage.getItem('authToken')
                    if (!token) { alert('Please log in to download reports'); return }
                    const res = await apiClient.get('/api/report/transactions', { responseType: 'blob' })
                    const url = window.URL.createObjectURL(new Blob([res.data]))
                    const link = document.createElement('a')
                    link.href = url
                    const cd = res.headers['content-disposition'] || ''
                    const match = cd.match(/filename=(.*)/)
                    link.setAttribute('download', match ? match[1].replace(/"/g, '') : 'transactions.csv')
                    document.body.appendChild(link)
                    link.click()
                    link.remove()
                    window.URL.revokeObjectURL(url)
                  } catch (err) {
                    alert('Error: ' + (err.response?.data?.error || err.message || 'Failed to download report'))
                  }
                }}
                className="btn-primary flex items-center gap-2"
              >
                <span>📥</span>
                <span>Download Report</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <BalanceCard balance={dashboardData.balance} />
              <IncomeCard income={dashboardData.income} />
              <ExpenseCard expense={dashboardData.expense} />
              <SavingsCard income={dashboardData.income} expense={dashboardData.expense} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {dashboardData.incomeData
                ? <IncomeVsExpenseChart data={dashboardData.incomeData} />
                : <div className="card flex items-center justify-center h-64 text-gray-500">No income/expense data available</div>
              }
              {dashboardData.expenseData && dashboardData.expenseData.labels.length > 0
                ? <ExpenseCategoryChart data={dashboardData.expenseData} />
                : <div className="card flex items-center justify-center h-64 text-gray-500">No expense category data available</div>
              }
            </div>

            <div className="card">
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-lg font-bold text-gray-900">Recent Transactions</h3>
                <div className="flex items-center gap-4">
                  <button
                    onClick={async () => {
                      try {
                        const token = localStorage.getItem('authToken')
                        if (!token) { alert('Please log in to download reports'); return }
                        const res = await apiClient.get('/api/report/transactions', { responseType: 'blob' })
                        if (res.data.size === 0) { alert('No transactions to download'); return }
                        const url = window.URL.createObjectURL(new Blob([res.data]))
                        const link = document.createElement('a')
                        link.href = url
                        const cd = res.headers['content-disposition'] || ''
                        const match = cd.match(/filename=(.*)/)
                        link.setAttribute('download', match ? match[1].replace(/"/g, '') : 'transactions.csv')
                        document.body.appendChild(link)
                        link.click()
                        link.remove()
                        window.URL.revokeObjectURL(url)
                        alert('Report downloaded successfully!')
                      } catch (err) {
                        alert('Error: ' + (err.response?.data?.error || err.message || 'Failed to download report'))
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

              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Description</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Category</th>
                      <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Date</th>
                      <th className="px-4 py-3 text-right text-sm font-semibold text-gray-700">Amount</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {dashboardData.recentTransactions.length === 0 ? (
                      <tr>
                        <td colSpan="4" className="px-4 py-8 text-center text-gray-500">
                          No transactions found
                        </td>
                      </tr>
                    ) : (
                      dashboardData.recentTransactions.map((transaction) => (
                        <tr key={transaction.id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-4 py-4">
                            <div className="flex items-center space-x-3">
                              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${getCategoryBgColor(transaction.type)}`}>
                                <span className="text-lg">{transaction.type === 'income' ? '↓' : '↑'}</span>
                              </div>
                              <p className="font-medium text-gray-900">{transaction.description}</p>
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
                          <td className={`px-4 py-4 text-right font-semibold ${getCategoryColor(transaction.type)}`}>
                            {transaction.type === 'income' ? '+' : '-'}{formatRupees(transaction.amount)}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {(() => {
              const recent = dashboardData.recentTransactions || []
              const income = dashboardData.income || 0
              const expense = dashboardData.expense || 0
              const today = new Date()
              const daysPassed = today.getDate() || 1
              const avgDaily = expense > 0 ? expense / daysPassed : 0
              const expenseTx = recent.filter((t) => t.type === 'expense')
              const largest = expenseTx.length
                ? expenseTx.reduce((max, t) => (t.amount > (max?.amount || 0) ? t : max), null)
                : null
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
                    <p className="text-xs text-gray-500 mt-2">
                      {largest ? `${largest.category} - ${new Date(largest.date).toLocaleDateString()}` : 'No expense transactions'}
                    </p>
                  </div>
                  <div className="card">
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Budget Remaining</h4>
                    <p className="text-2xl font-bold text-success-600">{formatRupees(budgetRemaining)}</p>
                    <p className="text-xs text-gray-500 mt-2">{budgetPercent}% of monthly income</p>
                  </div>
                </div>
              )
            })()}
          </>
        )}

      </div>
    </Layout>
  )
}