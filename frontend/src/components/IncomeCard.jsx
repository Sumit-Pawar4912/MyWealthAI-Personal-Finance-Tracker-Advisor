/**
 * IncomeCard Component
 * Displays total income for the current period
 */
import { formatRupees } from '../utils/currency'

export default function IncomeCard({ income = 0 }) {
  const formattedIncome = formatRupees(income)

  return (
    <div className="card">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-500 text-sm font-medium mb-2">Total Income</p>
          <h3 className="text-3xl font-bold text-success-600">{formattedIncome}</h3>
          <p className="text-gray-400 text-xs mt-2">This month</p>
        </div>
        <div className="bg-success-100 rounded-full p-3">
          <svg
            className="w-6 h-6 text-success-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 6v6m0 0v6m0-6h6m-6 0H6"
            />
          </svg>
        </div>
      </div>
    </div>
  )
}
