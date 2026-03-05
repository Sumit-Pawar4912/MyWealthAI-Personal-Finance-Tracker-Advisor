/**
 * ExpenseCard Component
 * Displays total expenses for the current period
 */
import { formatRupees } from '../utils/currency'

export default function ExpenseCard({ expense = 0 }) {
  const formattedExpense = formatRupees(expense)

  return (
    <div className="card">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-500 text-sm font-medium mb-2">Total Expenses</p>
          <h3 className="text-3xl font-bold text-danger-600">{formattedExpense}</h3>
          <p className="text-gray-400 text-xs mt-2">This month</p>
        </div>
        <div className="bg-danger-100 rounded-full p-3">
          <svg
            className="w-6 h-6 text-danger-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M20 12H4"
            />
          </svg>
        </div>
      </div>
    </div>
  )
}
