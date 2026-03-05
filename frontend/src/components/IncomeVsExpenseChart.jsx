import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

/**
 * IncomeVsExpenseChart Component
 * Bar chart comparing income vs expenses over months
 */
export default function IncomeVsExpenseChart({ data = null }) {
  const defaultData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    income: [5000, 5200, 5100, 5500, 5800, 6000],
    expenses: [3000, 3200, 3100, 3300, 3500, 3700],
  }

  const chartData = data || defaultData

  const chartConfig = {
    labels: chartData.labels,
    datasets: [
      {
        label: 'Income',
        data: chartData.income,
        backgroundColor: '#10b981',
        borderColor: '#059669',
        borderWidth: 1,
        borderRadius: 8,
        tension: 0.4,
      },
      {
        label: 'Expenses',
        data: chartData.expenses,
        backgroundColor: '#ef4444',
        borderColor: '#dc2626',
        borderWidth: 1,
        borderRadius: 8,
        tension: 0.4,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: { size: 12, weight: 500 },
        },
      },
      title: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function (context) {
            const value = context.raw
            return `₹${value.toLocaleString()}`
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          callback: function (value) {
            return '₹' + value.toLocaleString()
          },
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  }

  return (
    <div className="card">
      <h3 className="text-lg font-bold text-gray-900 mb-4">Income vs Expenses</h3>
      <Bar data={chartConfig} options={options} />
    </div>
  )
}
