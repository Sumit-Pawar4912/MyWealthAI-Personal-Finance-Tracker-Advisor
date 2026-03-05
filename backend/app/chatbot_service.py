import os
from groq import Groq


class ChatbotService:

    _groq_client = None

    @classmethod
    def _init_groq(cls):
        if cls._groq_client:
            return True

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return False

        cls._groq_client = Groq(api_key=api_key)
        return True

    @classmethod
    def _get_llama_response(cls, user_message, financial_summary):
        if not cls._init_groq():
            return None

        try:
            prompt = f"""
You are a smart AI Financial Assistant.

User Financial Summary:
- Total Income: ₹{financial_summary['total_income']:,.2f}
- Total Expenses: ₹{financial_summary['total_expense']:,.2f}
- Total Savings: ₹{financial_summary['total_savings']:,.2f}
- Transactions: {financial_summary['transaction_count']}

User Question:
{user_message}

Provide helpful, actionable financial advice.
Keep response under 200 words.
"""

            response = cls._groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful financial assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print("Groq error:", str(e))
            return None