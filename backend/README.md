# MyWelthAI Backend

Flask REST API backend for the MyWelthAI personal finance tracker application.

## Features

- ✅ User authentication (registration, login, JWT)
- ✅ Transaction management (CRUD operations)
- ✅ Dashboard summary endpoints
- ✅ AI-powered financial advice
- ✅ SQLite database
- ✅ CORS enabled for React frontend
- ✅ RESTful API design

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip (Python package manager)

### Installation

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Create a `.env` file with the following configuration:
```
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DEBUG=True
DATABASE_URL=sqlite:///mywelthai.db
PORT=5000
```

### Running the Backend

Start the Flask development server:
```bash
python run.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/verify` - Verify JWT token

#### Transactions
- `POST /api/transactions` - Create transaction
- `GET /api/transactions` - Get all transactions
- `GET /api/transactions/<id>` - Get specific transaction
- `PUT /api/transactions/<id>` - Update transaction
- `DELETE /api/transactions/<id>` - Delete transaction

#### Dashboard
- `GET /api/dashboard/summary` - Get summary (income, expenses, balance)
- `GET /api/dashboard/monthly-data` - Get 6-month data for charts

#### Advice
- `GET /api/advice` - Get AI financial advice

### Database Models

**User**
- id, email, password_hash, first_name, last_name, phone, created_at, updated_at

**Transaction**
- id, user_id, type (income/expense), category, description, amount, date, created_at

### Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth_routes.py
│   │   ├── transaction_routes.py
│   │   ├── dashboard_routes.py
│   │   └── advice_routes.py
│   └── services/
├── config.py
├── run.py
├── requirements.txt
├── .env
└── README.md
```

## Next Steps

1. Integrate with frontend React application
2. Add more sophisticated financial advice algorithms
3. Implement budget tracking features
4. Add data export functionality
5. Deploy to production

## Testing Endpoints

You can test the API endpoints using cURL, Postman, or any HTTP client.

Example - Register:
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

Example - Login:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```
