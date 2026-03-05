/**
 * SavingsCard Component
 * Displays savings amount and savings rate
 */
import { formatRupees } from '../utils/currency'

export default function SavingsCard({ income = 0, expense = 0 }) {
  const savings = income - expense
  const savingsRate = income > 0 ? ((savings / income) * 100).toFixed(1) : 0

  const formattedSavings = formatRupees(savings)

  const savingsColor = savings >= 0 ? 'text-success-600' : 'text-danger-600'

  return (
    <div className="card">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-500 text-sm font-medium mb-2">Total Savings</p>
          <h3 className={`text-3xl font-bold ${savingsColor}`}>{formattedSavings}</h3>
          <div className="flex items-center mt-2">
            <p className="text-gray-400 text-xs">Savings rate: </p>
            <p className={`text-sm font-semibold ml-1 ${savingsColor}`}>{savingsRate}%</p>
          </div>
        </div>
        <div className="bg-primary-100 rounded-full p-3">
          <svg
            className="w-6 h-6 text-primary-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
      </div>
    </div>
  )
}
