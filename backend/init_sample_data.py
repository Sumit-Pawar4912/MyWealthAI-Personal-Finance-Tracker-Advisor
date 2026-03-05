"""
Sample data initialization script
Run this after setting up the backend to populate sample data
"""

from app import app
from app.database import db
from app.models import User, Transaction
from datetime import datetime, timedelta

def initialize_sample_data():
    """Initialize database with sample data"""
    
    with app.app_context():
        # Clear existing data
        print("Clearing existing data...")
        Transaction.query.delete()
        User.query.delete()
        db.session.commit()
        
        # Create sample user
        print("Creating sample user...")
        user = User(
            email='demo@example.com',
            first_name='John',
            last_name='Doe',
            phone='+1 (555) 123-4567'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ User created: {user.email}")
        
        # Create sample transactions for the current month
        print("Creating sample transactions...")
        
        today = datetime.utcnow().date()
        start_of_month = datetime(today.year, today.month, 1).date()
        
        sample_transactions = [
            # Income
            {
                'type': 'income',
                'category': 'Salary',
                'description': 'Monthly salary',
                'amount': 6000,
                'date': start_of_month + timedelta(days=2)
            },
            {
                'type': 'income',
                'category': 'Freelance',
                'description': 'Website project',
                'amount': 800,
                'date': start_of_month + timedelta(days=10)
            },
            
            # Expenses
            {
                'type': 'expense',
                'category': 'Food & Dining',
                'description': 'Grocery store',
                'amount': 120,
                'date': start_of_month + timedelta(days=1)
            },
            {
                'type': 'expense',
                'category': 'Food & Dining',
                'description': 'Restaurant lunch',
                'amount': 35.50,
                'date': start_of_month + timedelta(days=3)
            },
            {
                'type': 'expense',
                'category': 'Food & Dining',
                'description': 'Coffee shop',
                'amount': 5.50,
                'date': start_of_month + timedelta(days=5)
            },
            {
                'type': 'expense',
                'category': 'Transportation',
                'description': 'Gas',
                'amount': 65,
                'date': start_of_month + timedelta(days=2)
            },
            {
                'type': 'expense',
                'category': 'Transportation',
                'description': 'Car maintenance',
                'amount': 150,
                'date': start_of_month + timedelta(days=8)
            },
            {
                'type': 'expense',
                'category': 'Entertainment',
                'description': 'Movie tickets',
                'amount': 30,
                'date': start_of_month + timedelta(days=4)
            },
            {
                'type': 'expense',
                'category': 'Entertainment',
                'description': 'Concert tickets',
                'amount': 85,
                'date': start_of_month + timedelta(days=9)
            },
            {
                'type': 'expense',
                'category': 'Utilities',
                'description': 'Electricity bill',
                'amount': 120,
                'date': start_of_month + timedelta(days=1)
            },
            {
                'type': 'expense',
                'category': 'Utilities',
                'description': 'Internet bill',
                'amount': 50,
                'date': start_of_month + timedelta(days=1)
            },
            {
                'type': 'expense',
                'category': 'Healthcare',
                'description': 'Pharmacy',
                'amount': 45,
                'date': start_of_month + timedelta(days=6)
            },
            {
                'type': 'expense',
                'category': 'Shopping',
                'description': 'Clothing store',
                'amount': 120,
                'date': start_of_month + timedelta(days=7)
            },
            {
                'type': 'expense',
                'category': 'Shopping',
                'description': 'Electronics',
                'amount': 250,
                'date': start_of_month + timedelta(days=11)
            },
        ]
        
        for tx_data in sample_transactions:
            transaction = Transaction(
                user_id=user.id,
                type=tx_data['type'],
                category=tx_data['category'],
                description=tx_data['description'],
                amount=tx_data['amount'],
                date=tx_data['date']
            )
            db.session.add(transaction)
            print(f"  ✅ {tx_data['type'].capitalize()}: {tx_data['description']} - ${tx_data['amount']}")
        
        db.session.commit()
        
        # Calculate and display summary
        print("\n" + "="*50)
        print("📊 SAMPLE DATA SUMMARY")
        print("="*50)
        
        transactions = Transaction.query.filter_by(user_id=user.id).all()
        total_income = sum(t.amount for t in transactions if t.type == 'income')
        total_expense = sum(t.amount for t in transactions if t.type == 'expense')
        balance = total_income - total_expense
        savings_rate = (balance / total_income * 100) if total_income > 0 else 0
        
        print(f"Total Transactions: {len(transactions)}")
        print(f"Total Income: ${total_income:.2f}")
        print(f"Total Expenses: ${total_expense:.2f}")
        print(f"Balance: ${balance:.2f}")
        print(f"Savings Rate: {savings_rate:.1f}%")
        print("="*50)
        
        print("\n✅ Sample data initialized successfully!")
        print("\nYou can now login with:")
        print("  Email: demo@example.com")
        print("  Password: password123")

if __name__ == '__main__':
    initialize_sample_data()
