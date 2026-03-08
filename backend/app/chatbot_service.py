"""
Chatbot Service for MyWelthAI
Powered by Groq LLaMA 3.3 70B
"""

import os
from groq import Groq
from app.database import db
from app.models import User, Transaction
from sqlalchemy import func


class ChatbotService:

    _groq_client = None

    # ── Groq client init ───────────────────────────────────────────────────────
    @classmethod
    def _init_groq(cls):
        if cls._groq_client:
            return True
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("[ChatbotService] ERROR: GROQ_API_KEY not set in .env")
            return False
        try:
            cls._groq_client = Groq(api_key=api_key)
            return True
        except Exception as e:
            print(f"[ChatbotService] ERROR initialising Groq client: {e}")
            return False

    # ── Fetch user financial summary from DB ───────────────────────────────────
    @classmethod
    def _get_financial_summary(cls, user_id):
        try:
            transactions = Transaction.query.filter_by(user_id=user_id).all()

            total_income  = sum(t.amount for t in transactions if t.type == 'income')
            total_expense = sum(t.amount for t in transactions if t.type == 'expense')
            total_savings = total_income - total_expense

            # Category breakdown
            category_totals = {}
            for t in transactions:
                if t.type == 'expense':
                    category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

            top_category = max(category_totals, key=category_totals.get) if category_totals else "N/A"

            return {
                'total_income':      total_income,
                'total_expense':     total_expense,
                'total_savings':     total_savings,
                'transaction_count': len(transactions),
                'top_category':      top_category,
                'category_totals':   category_totals,
            }
        except Exception as e:
            print(f"[ChatbotService] ERROR fetching financial summary: {e}")
            return {
                'total_income':      0,
                'total_expense':     0,
                'total_savings':     0,
                'transaction_count': 0,
                'top_category':      'N/A',
                'category_totals':   {},
            }

    # ── Detect intent from user message ───────────────────────────────────────
    @classmethod
    def _detect_intent(cls, message):
        msg = message.lower()
        if any(w in msg for w in ['balance', 'how much', 'total']):
            return 'balance'
        if any(w in msg for w in ['spend', 'spent', 'expense', 'cost']):
            return 'spending'
        if any(w in msg for w in ['income', 'earn', 'salary', 'revenue']):
            return 'income'
        if any(w in msg for w in ['save', 'saving', 'savings']):
            return 'savings'
        if any(w in msg for w in ['advice', 'tip', 'suggest', 'recommend', 'help', 'improve']):
            return 'advice'
        if any(w in msg for w in ['category', 'categories', 'where', 'most']):
            return 'category'
        return 'general'

    # ── Call Groq LLaMA 3.3 ───────────────────────────────────────────────────
    @classmethod
    def _get_llama_response(cls, user_message, financial_summary):
        if not cls._init_groq():
            return None

        try:
            category_text = ""
            if financial_summary.get('category_totals'):
                lines = [f"  • {cat}: ₹{amt:,.2f}"
                         for cat, amt in financial_summary['category_totals'].items()]
                category_text = "Expense Breakdown:\n" + "\n".join(lines)

            prompt = f"""You are a smart AI Financial Assistant for MyWealthAI app.

User Financial Summary:
- Total Income:   ₹{financial_summary['total_income']:,.2f}
- Total Expenses: ₹{financial_summary['total_expense']:,.2f}
- Total Savings:  ₹{financial_summary['total_savings']:,.2f}
- Transactions:   {financial_summary['transaction_count']}
- Top Spending Category: {financial_summary['top_category']}
{category_text}

User Question: {user_message}

Instructions:
- Give helpful, specific, actionable financial advice
- Use the actual numbers from the summary above
- Keep response under 200 words
- Be friendly and encouraging
- Use Indian Rupee (₹) for currency
"""

            response = cls._groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful, friendly financial assistant for an Indian personal finance app called MyWealthAI."},
                    {"role": "user",   "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"[ChatbotService] Groq API error: {e}")
            return None

    # ── Main public method called by chatbot_routes.py ─────────────────────────
    @classmethod
    def get_response(cls, user_id, user_message):
        """
        Main entry point called by chatbot_routes.py
        Returns dict: { response, intent, data }
        """
        try:
            # 1. Get user's financial data
            financial_summary = cls._get_financial_summary(user_id)

            # 2. Detect intent
            intent = cls._detect_intent(user_message)

            # 3. Try Groq LLaMA 3.3 first
            ai_response = cls._get_llama_response(user_message, financial_summary)

            # 4. Fallback if Groq fails or key is missing
            if not ai_response:
                ai_response = cls._fallback_response(intent, financial_summary)

            return {
                'response': ai_response,
                'intent':   intent,
                'data':     financial_summary,
            }

        except Exception as e:
            print(f"[ChatbotService] ERROR in get_response: {e}")
            return {
                'response': "I'm sorry, I encountered an error. Please try again.",
                'intent':   'error',
                'data':     {},
            }

    # ── Fallback responses if Groq API is unavailable ─────────────────────────
    @classmethod
    def _fallback_response(cls, intent, summary):
        income  = summary['total_income']
        expense = summary['total_expense']
        savings = summary['total_savings']

        fallbacks = {
            'balance':  f"Your current balance is ₹{savings:,.2f} "
                        f"(Income: ₹{income:,.2f} - Expenses: ₹{expense:,.2f}).",
            'spending': f"Your total spending is ₹{expense:,.2f}. "
                        f"Top category: {summary['top_category']}.",
            'income':   f"Your total income recorded is ₹{income:,.2f}.",
            'savings':  f"You have saved ₹{savings:,.2f} so far. "
                        f"That's {(savings/income*100):.1f}% of your income!" if income > 0
                        else "Add some income transactions to track your savings.",
            'advice':   f"With ₹{income:,.2f} income and ₹{expense:,.2f} expenses, "
                        f"try to keep expenses below 70% of income for healthy savings.",
            'category': f"Your highest spending category is {summary['top_category']}.",
            'general':  f"You have ₹{savings:,.2f} in savings from "
                        f"{summary['transaction_count']} transactions. How can I help?",
        }

        return fallbacks.get(intent, fallbacks['general'])