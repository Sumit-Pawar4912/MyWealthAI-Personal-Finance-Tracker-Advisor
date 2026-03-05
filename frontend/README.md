# MyWelthAI Frontend

React + Vite + Tailwind CSS fintech dashboard application.

## Setup Instructions

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file with API configuration:
```
VITE_API_BASE_URL=http://localhost:5000
VITE_APP_NAME=MyWelthAI
```

### Development

Start the development server:
```bash
npm run dev
```

The application will open at `http://localhost:5173`

### Build

Build for production:
```bash
npm run build
```

### Project Structure

```
src/
├── components/          # Reusable components
│   ├── BalanceCard.jsx
│   ├── IncomeCard.jsx
│   ├── ExpenseCard.jsx
│   ├── SavingsCard.jsx
│   ├── IncomeVsExpenseChart.jsx
│   └── ExpenseCategoryChart.jsx
├── pages/              # Page components
│   ├── Login.jsx
│   ├── Dashboard.jsx
│   ├── AddTransaction.jsx
│   ├── AIAdvice.jsx
│   └── Profile.jsx
├── layout/             # Layout components
│   ├── Layout.jsx
│   ├── Sidebar.jsx
│   └── Navbar.jsx
├── services/           # API services
│   └── apiClient.js
├── assets/             # Images, icons, etc.
├── utils/              # Utility functions
├── App.jsx
├── main.jsx
└── index.css
```

## Features

- ✅ Responsive fintech dashboard UI
- ✅ Beautiful card components with Tailwind CSS
- ✅ Income vs Expense chart
- ✅ Expense category pie chart
- ✅ Recent transactions table
- ✅ Sidebar navigation
- ✅ Top navbar with user menu
- ✅ Professional color palette
- ✅ Reusable components

## Next Steps

1. Set up the Flask backend
2. Connect API endpoints
3. Add authentication
4. Implement transaction management
5. Add financial advice logic
