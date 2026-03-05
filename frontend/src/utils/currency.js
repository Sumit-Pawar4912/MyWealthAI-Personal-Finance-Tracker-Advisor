/**
 * Currency Utility Functions
 * Handles currency formatting for Indian Rupees
 */

/**
 * Format amount as Indian Rupees
 * @param {number} amount - Amount in rupees
 * @returns {string} Formatted rupee string
 */
export const formatRupees = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

/**
 * Format amount as just the number with Indian locale
 * @param {number} amount - Amount to format
 * @returns {string} Formatted number
 */
export const formatNumber = (amount) => {
  return new Intl.NumberFormat('en-IN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

/**
 * Get rupee symbol
 * @returns {string} Rupee symbol
 */
export const getRupeeSymbol = () => {
  return '₹'
}

// Currency conversion rates (1 USD = X INR)
// In production, fetch these from an API
export const USD_TO_INR_RATE = 83.12 // Current approximate rate
