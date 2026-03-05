/**
 * BalanceCard Component
 * Displays the user's total account balance
 */
import { formatRupees } from '../utils/currency'

export default function BalanceCard({ balance = 0 }) {
  const formattedBalance = formatRupees(balance)

  return (
    <div className="card bg-gradient-to-br from-primary-600 to-primary-700 text-white">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-primary-100 text-sm font-medium mb-2">Total Balance</p>
          <h2 className="text-4xl font-bold">{formattedBalance}</h2>
        </div>
        <div className="bg-white bg-opacity-20 rounded-full p-3">
          <svg
            className="w-6 h-6"
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
