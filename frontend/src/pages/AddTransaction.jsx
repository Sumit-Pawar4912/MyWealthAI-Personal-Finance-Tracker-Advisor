import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Layout from '../layout/Layout'
import apiClient from '../services/apiClient'

/**
 * Add Transaction Page
 * Page for adding new income or expense transactions
 */
export default function AddTransaction() {
  const [user, setUser] = useState(null)
  const [balance, setBalance] = useState(0)
  const [balanceError, setBalanceError] = useState('')
  const navigate = useNavigate()

  // Form state
  const [type, setType] = useState('income')
  const [category, setCategory] = useState('Salary')
  const [amount, setAmount] = useState('')
  const [description, setDescription] = useState('')
  const [date, setDate] = useState(() => new Date().toISOString().slice(0, 10))
  const [submitting, setSubmitting] = useState(false)

  // Fetch user profile and balance on mount
  useEffect(() => {
    const fetchData = async () => {
      try {
        const userResponse = await apiClient.get('/api/auth/profile')
        setUser(userResponse.data.user)

        // Fetch current balance (all-time total)
        const balanceResponse = await apiClient.get('/api/dashboard/current-balance')
        setBalance(balanceResponse.data.balance || 0)
      } catch (err) {
        console.error('Failed to fetch data:', err)
      }
    }
    fetchData()
  }, [])

  // Validate if expense would result in negative balance
  useEffect(() => {
    if (type === 'expense' && amount) {
      const expenseAmount = parseFloat(amount)
      if (expenseAmount > balance) {
        setBalanceError(
          `Insufficient balance! Current balance: ${balance.toFixed(2)}, Expense: ${expenseAmount.toFixed(2)}`
        )
      } else {
        setBalanceError('')
      }
    } else {
      setBalanceError('')
    }
  }, [type, amount, balance])

  return (
    <Layout userName={`${user?.first_name} ${user?.last_name}`.trim() || 'User'}>
      <div className="max-w-2xl">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Add Transaction</h1>
        
        {/* Current Balance Display */}
        {type === 'expense' && (
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-gray-600">Current Balance</p>
            <p className="text-2xl font-bold text-blue-600">₹{balance.toFixed(2)}</p>
          </div>
        )}

        {/* Balance Error Message */}
        {balanceError && (
          <div className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            ⚠️ {balanceError}
          </div>
        )}
        
        <div className="card">
          <form className="space-y-6" onSubmit={async (e) => {
            e.preventDefault()
            setSubmitting(true)
            try {
              const payload = { type, category, description, amount: parseFloat(amount), date }
              const res = await apiClient.post('/api/transactions', payload)
              if (res.status === 201) {
                navigate('/dashboard')
              }
            } catch (err) {
              console.error('Failed to create transaction:', err)
              alert(err.response?.data?.error || 'Failed to create transaction')
            } finally {
              setSubmitting(false)
            }
          }}>
            {/* Transaction Type */}
            <div>
              <label className="label">Transaction Type</label>
              <div className="grid grid-cols-2 gap-4">
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-primary-500">
                  <input type="radio" name="type" value="income" checked={type === 'income'} onChange={() => setType('income')} />
                  <span className="ml-3 font-medium">Income</span>
                </label>
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-primary-500">
                  <input type="radio" name="type" value="expense" checked={type === 'expense'} onChange={() => setType('expense')} />
                  <span className="ml-3 font-medium">Expense</span>
                </label>
              </div>
            </div>

            {/* Category */}
            <div>
              <label className="label">Category</label>
              <select className="input-field" value={category} onChange={(e) => setCategory(e.target.value)}>
                <option>Salary</option>
                <option>Food & Dining</option>
                <option>Transportation</option>
                <option>Entertainment</option>
                <option>Shopping</option>
                <option>Other</option>
              </select>
            </div>

            {/* Amount */}
            <div>
              <label className="label">Amount</label>
              <input type="number" placeholder="0.00" className="input-field" value={amount} onChange={(e) => setAmount(e.target.value)} step="0.01" />
            </div>

            {/* Description */}
            <div>
              <label className="label">Description</label>
              <input type="text" placeholder="Enter transaction description" className="input-field" value={description} onChange={(e) => setDescription(e.target.value)} />
            </div>

            {/* Date */}
            <div>
              <label className="label">Date</label>
              <input type="date" className="input-field" value={date} onChange={(e) => setDate(e.target.value)} />
            </div>

            {/* Buttons */}
            <div className="flex gap-4">
              <button 
                type="submit" 
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed" 
                disabled={submitting || !!balanceError}
              >
                {submitting ? 'Adding...' : 'Add Transaction'}
              </button>
              <button type="button" className="btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  )
}
