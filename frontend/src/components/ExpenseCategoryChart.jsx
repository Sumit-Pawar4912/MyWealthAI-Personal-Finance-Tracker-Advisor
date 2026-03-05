import { Pie } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

/**
 * ExpenseCategoryChart Component
 * Pie chart showing expense breakdown by category
 */
export default function ExpenseCategoryChart({ data = null }) {
  const defaultData = {
    labels: ['Food & Dining', 'Transportation', 'Entertainment', 'Utilities', 'Healthcare', 'Shopping'],
    values: [450, 300, 200, 150, 100, 250],
  }

  const chartData = data || defaultData

  const COLORS = ['#0ea5e9', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899']

  const config = {
    labels: chartData.labels,
    datasets: [
      {
        data: chartData.values,
        backgroundColor: COLORS,
        borderColor: '#ffffff',
        borderWidth: 2,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: { size: 12, weight: 500 },
        },
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const value = context.raw
            const total = context.dataset.data.reduce((a, b) => a + b, 0)
            const percentage = ((value / total) * 100).toFixed(1)
            return `₹${value} (${percentage}%)`
          },
        },
      },
    },
  }

  return (
    <div className="card">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Expense Categories</h3>
      <Pie data={config} options={options} />
    </div>
  )
}
