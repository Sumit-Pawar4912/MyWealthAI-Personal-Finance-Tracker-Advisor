# ================================================================
#  MyWealthAI — Complete Test Suite
#  File : backend/test_app.py
#  Run  : pytest test_app.py -v
#
#  BEFORE RUNNING:
#  1. Set TEST_EMAIL / TEST_PASSWORD to a real user in your DB
#  2. Make sure your Flask app starts without errors
#  3. Run:  pytest test_app.py -v
# ================================================================

import pytest
import sys
import os
import time

sys.path.insert(0, os.path.abspath('.'))

from run import app as flask_app

# ----------------------------------------------------------------
#  !! CHANGE THESE TO A REAL USER IN YOUR DATABASE !!
# ----------------------------------------------------------------
TEST_EMAIL    = "testuser@mywealthai.com"
TEST_PASSWORD = "Test@12345"
# ----------------------------------------------------------------


# ================================================================
#  FIXTURES
# ================================================================

@pytest.fixture(scope='session')
def client():
    """Flask test client — shared across the whole test session."""
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    with flask_app.test_client() as c:
        yield c


@pytest.fixture(scope='session')
def registered_user(client):
    """
    Register the test user once per session.
    409 (already exists) is fine — login will still work.
    """
    res = client.post('/api/auth/register', json={
        'email':      TEST_EMAIL,
        'password':   TEST_PASSWORD,
        'first_name': 'Test',
        'last_name':  'User'
    })
    if res.status_code not in [201, 409]:
        pytest.fail(
            f"Registration failed unexpectedly.\n"
            f"Status: {res.status_code}  Body: {res.get_json()}"
        )
    return res.get_json()


@pytest.fixture(scope='session')
def token(client, registered_user):
    """Log in once and return the JWT token for all protected tests."""
    res = client.post('/api/auth/login', json={
        'email':    TEST_EMAIL,
        'password': TEST_PASSWORD
    })
    data = res.get_json() or {}
    assert res.status_code == 200, (
        f"Login failed.\n"
        f"Status: {res.status_code}  Body: {data}\n"
        f"Make sure TEST_EMAIL / TEST_PASSWORD match a real DB user."
    )
    tok = data.get('token') or data.get('access_token') or ''
    assert tok, "Login returned 200 but no 'token' key found in response."
    return tok


@pytest.fixture(scope='session')
def auth(token):
    """Ready-to-use Authorization header dict."""
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='session')
def transaction_id(client, auth):
    """
    Create one real transaction and return its ID.
    Used by GET/PUT/DELETE single-transaction tests.
    """
    res = client.post('/api/transactions', json={
        'type':        'expense',
        'category':    'Food & Dining',
        'description': 'Test meal for pytest',
        'amount':      250.00,
        'date':        '2026-01-15'
    }, headers=auth)
    assert res.status_code == 201, f"Setup transaction failed: {res.get_json()}"
    return res.get_json()['transaction']['id']


# ================================================================
#  1. APP HEALTH
# ================================================================

class TestAppHealth:

    def test_root_returns_200_with_message(self, client):
        """GET / returns 200 with welcome message."""
        res = client.get('/')
        assert res.status_code == 200
        data = res.get_json()
        assert 'message' in data

    def test_root_lists_endpoints(self, client):
        """GET / response includes endpoints key."""
        res = client.get('/')
        assert 'endpoints' in res.get_json()

    def test_health_check_status_is_healthy(self, client):
        """GET /api/health returns status: healthy."""
        res = client.get('/api/health')
        assert res.status_code == 200
        assert res.get_json()['status'] == 'healthy'

    def test_health_check_has_timestamp(self, client):
        """GET /api/health response includes timestamp."""
        res = client.get('/api/health')
        assert 'timestamp' in res.get_json()

    def test_health_check_has_app_name(self, client):
        """GET /api/health response includes app name."""
        res = client.get('/api/health')
        assert 'app' in res.get_json()

    def test_unknown_route_returns_404(self, client):
        """Unknown route returns 404."""
        res = client.get('/api/nonexistent_route_xyz')
        assert res.status_code == 404

    def test_chatbot_health_check(self, client):
        """GET /api/chatbot/health returns ok."""
        res = client.get('/api/chatbot/health')
        assert res.status_code == 200
        assert res.get_json()['status'] == 'ok'


# ================================================================
#  2. AUTHENTICATION  /api/auth/...
# ================================================================

class TestAuthentication:

    # ── Register ────────────────────────────────────────────────

    def test_register_missing_email_returns_400(self, client):
        """POST /api/auth/register — no email → 400."""
        res = client.post('/api/auth/register', json={'password': 'Test@12345'})
        assert res.status_code == 400
        assert 'error' in res.get_json()

    def test_register_missing_password_returns_400(self, client):
        """POST /api/auth/register — no password → 400."""
        res = client.post('/api/auth/register', json={'email': 'x@x.com'})
        assert res.status_code == 400
        assert 'error' in res.get_json()

    def test_register_empty_body_returns_400(self, client):
        """POST /api/auth/register — empty body → 400."""
        res = client.post('/api/auth/register', json={})
        assert res.status_code == 400

    def test_register_duplicate_email_returns_409(self, client, registered_user):
        """POST /api/auth/register — duplicate email → 409."""
        res = client.post('/api/auth/register', json={
            'email': TEST_EMAIL, 'password': TEST_PASSWORD
        })
        assert res.status_code == 409
        assert 'error' in res.get_json()

    def test_register_new_user_returns_201_and_token(self, client):
        """POST /api/auth/register — new email → 201 + token + user."""
        unique = f"fresh_{int(time.time())}@test.com"
        res = client.post('/api/auth/register', json={
            'email':      unique,
            'password':   'NewPass@999',
            'first_name': 'Fresh',
            'last_name':  'User'
        })
        assert res.status_code == 201
        data = res.get_json()
        assert 'token' in data
        assert 'user'  in data
        assert data['user']['email'] == unique

    def test_register_response_has_message(self, client):
        """POST /api/auth/register — success response includes message."""
        unique = f"msg_{int(time.time())}@test.com"
        res = client.post('/api/auth/register', json={
            'email': unique, 'password': 'Pass@123'
        })
        assert res.status_code == 201
        assert 'message' in res.get_json()

    # ── Login ───────────────────────────────────────────────────

    def test_login_missing_email_returns_400(self, client):
        """POST /api/auth/login — no email → 400."""
        res = client.post('/api/auth/login', json={'password': TEST_PASSWORD})
        assert res.status_code == 400

    def test_login_missing_password_returns_400(self, client):
        """POST /api/auth/login — no password → 400."""
        res = client.post('/api/auth/login', json={'email': TEST_EMAIL})
        assert res.status_code == 400

    def test_login_empty_body_returns_400(self, client):
        """POST /api/auth/login — empty body → 400."""
        res = client.post('/api/auth/login', json={})
        assert res.status_code == 400

    def test_login_wrong_password_returns_401(self, client, registered_user):
        """POST /api/auth/login — wrong password → 401."""
        res = client.post('/api/auth/login', json={
            'email': TEST_EMAIL, 'password': 'TotallyWrong_999!'
        })
        assert res.status_code == 401
        assert 'error' in res.get_json()

    def test_login_unknown_email_returns_401(self, client):
        """POST /api/auth/login — unknown email → 401."""
        res = client.post('/api/auth/login', json={
            'email': 'ghost_nobody_xyz@nowhere.com', 'password': 'irrelevant'
        })
        assert res.status_code == 401

    def test_login_success_returns_200_token_user(self, client, registered_user):
        """POST /api/auth/login — correct credentials → 200 + token + user."""
        res = client.post('/api/auth/login', json={
            'email': TEST_EMAIL, 'password': TEST_PASSWORD
        })
        assert res.status_code == 200
        data = res.get_json()
        assert 'token'   in data
        assert 'user'    in data
        assert 'message' in data
        assert len(data['token']) > 20         # JWT is always long
        assert data['user']['email'] == TEST_EMAIL

    # ── Token Verify ────────────────────────────────────────────

    def test_verify_valid_token_returns_valid_true(self, client, auth):
        """GET /api/auth/verify — valid token → valid: true."""
        res = client.get('/api/auth/verify', headers=auth)
        assert res.status_code == 200
        assert res.get_json().get('valid') is True

    def test_verify_no_token_returns_401(self, client):
        """GET /api/auth/verify — no token → 401."""
        res = client.get('/api/auth/verify')
        assert res.status_code == 401

    def test_verify_fake_token_returns_401(self, client):
        """GET /api/auth/verify — fake token → 401."""
        res = client.get('/api/auth/verify', headers={
            'Authorization': 'Bearer this.is.completely.fake'
        })
        assert res.status_code == 401

    # ── Profile ─────────────────────────────────────────────────

    def test_get_profile_with_auth_returns_user(self, client, auth):
        """GET /api/auth/profile — valid token → 200 + user object."""
        res = client.get('/api/auth/profile', headers=auth)
        assert res.status_code == 200
        data = res.get_json()
        assert 'user' in data
        assert data['user']['email'] == TEST_EMAIL

    def test_get_profile_without_auth_returns_401(self, client):
        """GET /api/auth/profile — no token → 401."""
        res = client.get('/api/auth/profile')
        assert res.status_code == 401

    def test_update_profile_first_name(self, client, auth):
        """PUT /api/auth/profile — updates first_name, returns updated user."""
        res = client.put('/api/auth/profile', json={
            'first_name': 'UpdatedViaPytest'
        }, headers=auth)
        assert res.status_code == 200
        data = res.get_json()
        assert 'user'    in data
        assert 'message' in data
        assert data['user']['first_name'] == 'UpdatedViaPytest'

    def test_update_profile_without_auth_returns_401(self, client):
        """PUT /api/auth/profile — no token → 401."""
        res = client.put('/api/auth/profile', json={'first_name': 'Hacker'})
        assert res.status_code == 401


# ================================================================
#  3. TRANSACTIONS  /api/transactions
#  Required fields: type, category, description, amount, date
# ================================================================

class TestTransactions:

    ROUTE = '/api/transactions'

    # ── GET all ─────────────────────────────────────────────────

    def test_get_all_without_auth_returns_401(self, client):
        """GET /api/transactions — no token → 401."""
        res = client.get(self.ROUTE)
        assert res.status_code == 401

    def test_get_all_with_auth_returns_200(self, client, auth):
        """GET /api/transactions — valid token → 200."""
        res = client.get(self.ROUTE, headers=auth)
        assert res.status_code == 200

    def test_get_all_response_has_transactions_key(self, client, auth):
        """GET /api/transactions — response has 'transactions' list."""
        res = client.get(self.ROUTE, headers=auth)
        data = res.get_json()
        assert 'transactions' in data
        assert isinstance(data['transactions'], list)

    def test_get_all_response_has_pagination_fields(self, client, auth):
        """GET /api/transactions — response has total, pages, current_page."""
        res = client.get(self.ROUTE, headers=auth)
        data = res.get_json()
        assert 'total'        in data
        assert 'pages'        in data
        assert 'current_page' in data

    def test_get_all_content_type_is_json(self, client, auth):
        """GET /api/transactions — Content-Type is application/json."""
        res = client.get(self.ROUTE, headers=auth)
        assert 'application/json' in res.content_type

    def test_get_all_type_filter_expense(self, client, auth):
        """GET /api/transactions?type=expense — only expense records returned."""
        res = client.get(f'{self.ROUTE}?type=expense', headers=auth)
        assert res.status_code == 200
        data = res.get_json()
        for t in data['transactions']:
            assert t['type'] == 'expense'

    def test_get_all_type_filter_income(self, client, auth):
        """GET /api/transactions?type=income — only income records returned."""
        res = client.get(f'{self.ROUTE}?type=income', headers=auth)
        assert res.status_code == 200
        data = res.get_json()
        for t in data['transactions']:
            assert t['type'] == 'income'

    # ── POST (create) ───────────────────────────────────────────

    def test_post_without_auth_returns_401(self, client):
        """POST /api/transactions — no token → 401."""
        res = client.post(self.ROUTE, json={
            'type': 'expense', 'category': 'Food & Dining',
            'description': 'test', 'amount': 100, 'date': '2026-01-01'
        })
        assert res.status_code == 401

    def test_post_missing_amount_returns_400(self, client, auth):
        """POST /api/transactions — missing amount → 400."""
        res = client.post(self.ROUTE, json={
            'type': 'expense', 'category': 'Food & Dining',
            'description': 'test', 'date': '2026-01-01'
        }, headers=auth)
        assert res.status_code == 400

    def test_post_missing_category_returns_400(self, client, auth):
        """POST /api/transactions — missing category → 400."""
        res = client.post(self.ROUTE, json={
            'type': 'expense', 'description': 'test',
            'amount': 100, 'date': '2026-01-01'
        }, headers=auth)
        assert res.status_code == 400

    def test_post_missing_description_returns_400(self, client, auth):
        """POST /api/transactions — missing description → 400."""
        res = client.post(self.ROUTE, json={
            'type': 'expense', 'category': 'Food & Dining',
            'amount': 100, 'date': '2026-01-01'
        }, headers=auth)
        assert res.status_code == 400

    def test_post_missing_date_returns_400(self, client, auth):
        """POST /api/transactions — missing date → 400."""
        res = client.post(self.ROUTE, json={
            'type': 'expense', 'category': 'Food & Dining',
            'description': 'test', 'amount': 100
        }, headers=auth)
        assert res.status_code == 400

    def test_post_missing_type_returns_400(self, client, auth):
        """POST /api/transactions — missing type → 400."""
        res = client.post(self.ROUTE, json={
            'category': 'Food & Dining', 'description': 'test',
            'amount': 100, 'date': '2026-01-01'
        }, headers=auth)
        assert res.status_code == 400

    def test_post_invalid_type_returns_400(self, client, auth):
        """POST /api/transactions — type='invalid' → 400."""
        res = client.post(self.ROUTE, json={
            'type': 'invalid', 'category': 'Food & Dining',
            'description': 'test', 'amount': 100, 'date': '2026-01-01'
        }, headers=auth)
        assert res.status_code == 400

    def test_post_valid_expense_returns_201(self, client, auth):
        """POST /api/transactions — valid expense → 201 + transaction object."""
        res = client.post(self.ROUTE, json={
            'type':        'expense',
            'category':    'Shopping',
            'description': 'Test shopping expense',
            'amount':      1500.00,
            'date':        '2026-01-20'
        }, headers=auth)
        assert res.status_code == 201
        data = res.get_json()
        assert 'transaction' in data
        assert 'message'     in data

    def test_post_valid_income_returns_201(self, client, auth):
        """POST /api/transactions — valid income → 201."""
        res = client.post(self.ROUTE, json={
            'type':        'income',
            'category':    'Salary',
            'description': 'Monthly salary pytest',
            'amount':      50000.00,
            'date':        '2026-01-01'
        }, headers=auth)
        assert res.status_code == 201

    def test_post_response_transaction_has_correct_type(self, client, auth):
        """POST valid expense — returned transaction.type is 'expense'."""
        res = client.post(self.ROUTE, json={
            'type': 'expense', 'category': 'Transport',
            'description': 'Bus fare', 'amount': 50, 'date': '2026-01-10'
        }, headers=auth)
        assert res.get_json()['transaction']['type'] == 'expense'

    # ── GET single ──────────────────────────────────────────────

    def test_get_single_without_auth_returns_401(self, client):
        """GET /api/transactions/1 — no token → 401."""
        res = client.get(f'{self.ROUTE}/1')
        assert res.status_code == 401

    def test_get_single_existing_returns_200(self, client, auth, transaction_id):
        """GET /api/transactions/<id> — existing ID → 200."""
        res = client.get(f'{self.ROUTE}/{transaction_id}', headers=auth)
        assert res.status_code == 200

    def test_get_single_nonexistent_returns_404(self, client, auth):
        """GET /api/transactions/999999 — non-existent ID → 404."""
        res = client.get(f'{self.ROUTE}/999999', headers=auth)
        assert res.status_code == 404
        assert 'error' in res.get_json()

    # ── PUT (update) ────────────────────────────────────────────

    def test_put_without_auth_returns_401(self, client):
        """PUT /api/transactions/1 — no token → 401."""
        res = client.put(f'{self.ROUTE}/1', json={'amount': 999})
        assert res.status_code == 401

    def test_put_existing_updates_amount(self, client, auth, transaction_id):
        """PUT /api/transactions/<id> — updates amount, returns updated record."""
        res = client.put(f'{self.ROUTE}/{transaction_id}', json={
            'amount': 300.00
        }, headers=auth)
        assert res.status_code == 200
        data = res.get_json()
        assert 'transaction' in data
        assert data['transaction']['amount'] == 300.00

    def test_put_existing_updates_description(self, client, auth, transaction_id):
        """PUT /api/transactions/<id> — updates description."""
        res = client.put(f'{self.ROUTE}/{transaction_id}', json={
            'description': 'Updated by pytest'
        }, headers=auth)
        assert res.status_code == 200
        assert res.get_json()['transaction']['description'] == 'Updated by pytest'

    def test_put_nonexistent_returns_404(self, client, auth):
        """PUT /api/transactions/999999 — non-existent → 404."""
        res = client.put(f'{self.ROUTE}/999999', json={'amount': 100}, headers=auth)
        assert res.status_code == 404

    # ── DELETE ──────────────────────────────────────────────────

    def test_delete_without_auth_returns_401(self, client):
        """DELETE /api/transactions/1 — no token → 401."""
        res = client.delete(f'{self.ROUTE}/1')
        assert res.status_code == 401

    def test_delete_nonexistent_returns_404(self, client, auth):
        """DELETE /api/transactions/999999 — non-existent → 404."""
        res = client.delete(f'{self.ROUTE}/999999', headers=auth)
        assert res.status_code == 404
        assert 'error' in res.get_json()

    def test_delete_existing_returns_200_with_message(self, client, auth):
        """DELETE existing transaction → 200 with success message."""
        # Create a fresh one just to delete it
        create = client.post(self.ROUTE, json={
            'type': 'expense', 'category': 'Entertainment',
            'description': 'Delete me', 'amount': 99, 'date': '2026-02-01'
        }, headers=auth)
        assert create.status_code == 201
        tid = create.get_json()['transaction']['id']

        res = client.delete(f'{self.ROUTE}/{tid}', headers=auth)
        assert res.status_code == 200
        assert 'message' in res.get_json()

    def test_delete_then_get_returns_404(self, client, auth):
        """After DELETE, GET same transaction returns 404."""
        create = client.post(self.ROUTE, json={
            'type': 'expense', 'category': 'Bills',
            'description': 'Delete then check', 'amount': 200, 'date': '2026-02-05'
        }, headers=auth)
        tid = create.get_json()['transaction']['id']

        client.delete(f'{self.ROUTE}/{tid}', headers=auth)
        res = client.get(f'{self.ROUTE}/{tid}', headers=auth)
        assert res.status_code == 404


# ================================================================
#  4. DASHBOARD  /api/dashboard/...
# ================================================================

class TestDashboard:

    def test_summary_without_auth_returns_401(self, client):
        """GET /api/dashboard/summary — no token → 401."""
        res = client.get('/api/dashboard/summary')
        assert res.status_code == 401

    def test_summary_with_auth_returns_200(self, client, auth):
        """GET /api/dashboard/summary — valid token → 200."""
        res = client.get('/api/dashboard/summary', headers=auth)
        assert res.status_code == 200

    def test_summary_has_income_and_expense(self, client, auth):
        """GET /api/dashboard/summary — response has income & expense."""
        data = client.get('/api/dashboard/summary', headers=auth).get_json()
        assert 'income'  in data
        assert 'expense' in data

    def test_summary_has_balance_and_savings_rate(self, client, auth):
        """GET /api/dashboard/summary — response has balance & savings_rate."""
        data = client.get('/api/dashboard/summary', headers=auth).get_json()
        assert 'balance'      in data
        assert 'savings_rate' in data

    def test_summary_has_categories_and_transaction_count(self, client, auth):
        """GET /api/dashboard/summary — response has categories & transaction_count."""
        data = client.get('/api/dashboard/summary', headers=auth).get_json()
        assert 'categories'        in data
        assert 'transaction_count' in data

    def test_summary_has_cumulative_balance(self, client, auth):
        """GET /api/dashboard/summary — response has cumulative_balance."""
        data = client.get('/api/dashboard/summary', headers=auth).get_json()
        assert 'cumulative_balance' in data

    def test_summary_values_are_numeric(self, client, auth):
        """Dashboard income, expense, balance are all numbers."""
        data = client.get('/api/dashboard/summary', headers=auth).get_json()
        assert isinstance(data['income'],  (int, float))
        assert isinstance(data['expense'], (int, float))
        assert isinstance(data['balance'], (int, float))

    def test_summary_month_param_accepted(self, client, auth):
        """GET /api/dashboard/summary?month=2026-01 — returns 200."""
        res = client.get('/api/dashboard/summary?month=2026-01', headers=auth)
        assert res.status_code == 200

    def test_current_balance_without_auth_returns_401(self, client):
        """GET /api/dashboard/current-balance — no token → 401."""
        res = client.get('/api/dashboard/current-balance')
        assert res.status_code == 401

    def test_current_balance_with_auth_returns_200(self, client, auth):
        """GET /api/dashboard/current-balance — valid token → 200."""
        res = client.get('/api/dashboard/current-balance', headers=auth)
        assert res.status_code == 200

    def test_current_balance_has_required_fields(self, client, auth):
        """GET /api/dashboard/current-balance — has balance, total_income, total_expense."""
        data = client.get('/api/dashboard/current-balance', headers=auth).get_json()
        assert 'balance'       in data
        assert 'total_income'  in data
        assert 'total_expense' in data

    def test_monthly_data_without_auth_returns_401(self, client):
        """GET /api/dashboard/monthly-data — no token → 401."""
        res = client.get('/api/dashboard/monthly-data')
        assert res.status_code == 401

    def test_monthly_data_with_auth_returns_200(self, client, auth):
        """GET /api/dashboard/monthly-data — valid token → 200."""
        res = client.get('/api/dashboard/monthly-data', headers=auth)
        assert res.status_code == 200

    def test_monthly_data_response_is_dict(self, client, auth):
        """GET /api/dashboard/monthly-data — returns a dict (month keys)."""
        data = client.get('/api/dashboard/monthly-data', headers=auth).get_json()
        assert isinstance(data, dict)


# ================================================================
#  5. FINANCIAL ADVICE  /api/advice
# ================================================================

class TestFinancialAdvice:

    ROUTE = '/api/advice'

    def test_without_auth_returns_401(self, client):
        """GET /api/advice — no token → 401."""
        res = client.get(self.ROUTE)
        assert res.status_code == 401

    def test_with_auth_returns_200(self, client, auth):
        """GET /api/advice — valid token → 200."""
        res = client.get(self.ROUTE, headers=auth)
        assert res.status_code == 200

    def test_response_has_advice_list(self, client, auth):
        """GET /api/advice — response has 'advice' list."""
        data = client.get(self.ROUTE, headers=auth).get_json()
        assert 'advice' in data
        assert isinstance(data['advice'], list)

    def test_advice_list_not_empty(self, client, auth):
        """GET /api/advice — at least one advice item returned."""
        data = client.get(self.ROUTE, headers=auth).get_json()
        assert len(data['advice']) >= 1

    def test_each_item_has_title_description_icon_priority(self, client, auth):
        """Each advice item has title, description, icon, priority, category."""
        data = client.get(self.ROUTE, headers=auth).get_json()
        for item in data['advice']:
            assert 'title'       in item
            assert 'description' in item
            assert 'icon'        in item
            assert 'priority'    in item
            assert 'category'    in item

    def test_priority_values_are_valid(self, client, auth):
        """Each advice item priority is one of: high, medium, low."""
        data = client.get(self.ROUTE, headers=auth).get_json()
        valid = {'high', 'medium', 'low'}
        for item in data['advice']:
            assert item['priority'] in valid

    def test_response_has_metrics(self, client, auth):
        """GET /api/advice — response has metrics object."""
        data = client.get(self.ROUTE, headers=auth).get_json()
        assert 'metrics' in data

    def test_metrics_has_income_expense_savings_rate(self, client, auth):
        """Metrics object has income, expense, savings_rate."""
        m = client.get(self.ROUTE, headers=auth).get_json()['metrics']
        assert 'income'       in m
        assert 'expense'      in m
        assert 'savings_rate' in m

    def test_metrics_are_numeric(self, client, auth):
        """Metrics income, expense, savings_rate are numbers."""
        m = client.get(self.ROUTE, headers=auth).get_json()['metrics']
        assert isinstance(m['income'],       (int, float))
        assert isinstance(m['expense'],      (int, float))
        assert isinstance(m['savings_rate'], (int, float))


# ================================================================
#  6. ANALYTICS & ML  /api/analytics/...
# ================================================================

class TestAnalytics:

    def test_spending_trends_no_auth_returns_401(self, client):
        """GET /api/analytics/spending-trends — no token → 401."""
        assert client.get('/api/analytics/spending-trends').status_code == 401

    def test_spending_trends_with_auth_returns_200(self, client, auth):
        """GET /api/analytics/spending-trends — valid token → 200."""
        assert client.get('/api/analytics/spending-trends', headers=auth).status_code == 200

    def test_spending_trends_days_param_accepted(self, client, auth):
        """GET /api/analytics/spending-trends?days=7 — returns 200."""
        assert client.get('/api/analytics/spending-trends?days=7', headers=auth).status_code == 200

    def test_spending_prediction_no_auth_returns_401(self, client):
        """GET /api/analytics/spending-prediction — no token → 401."""
        assert client.get('/api/analytics/spending-prediction').status_code == 401

    def test_spending_prediction_with_auth_returns_200(self, client, auth):
        """GET /api/analytics/spending-prediction — valid token → 200."""
        assert client.get('/api/analytics/spending-prediction', headers=auth).status_code == 200

    def test_spending_by_category_with_auth_returns_200(self, client, auth):
        """GET /api/analytics/spending-by-category — valid token → 200."""
        assert client.get('/api/analytics/spending-by-category', headers=auth).status_code == 200

    def test_anomalies_returns_anomalies_key(self, client, auth):
        """GET /api/analytics/anomalies — returns anomalies list."""
        res = client.get('/api/analytics/anomalies', headers=auth)
        assert res.status_code == 200
        data = res.get_json()
        assert 'anomalies' in data
        assert isinstance(data['anomalies'], list)

    def test_recommendations_returns_recommendations_key(self, client, auth):
        """GET /api/analytics/recommendations — returns recommendations list."""
        res = client.get('/api/analytics/recommendations', headers=auth)
        assert res.status_code == 200
        assert 'recommendations' in res.get_json()

    def test_overspending_risk_no_auth_returns_401(self, client):
        """GET /api/analytics/overspending-risk — no token → 401."""
        assert client.get('/api/analytics/overspending-risk').status_code == 401

    def test_overspending_risk_with_auth_returns_200(self, client, auth):
        """GET /api/analytics/overspending-risk — valid token → 200."""
        assert client.get('/api/analytics/overspending-risk', headers=auth).status_code == 200

    def test_overspending_risk_response_is_dict(self, client, auth):
        """GET /api/analytics/overspending-risk — response is a JSON object."""
        res = client.get('/api/analytics/overspending-risk', headers=auth)
        assert isinstance(res.get_json(), dict)

    def test_overspending_risk_days_param_accepted(self, client, auth):
        """GET /api/analytics/overspending-risk?days=7 — returns 200."""
        assert client.get('/api/analytics/overspending-risk?days=7', headers=auth).status_code == 200


# ================================================================
#  7. CHATBOT  /api/chatbot/...
# ================================================================

class TestChatbot:

    ROUTE = '/api/chatbot/message'

    def test_health_endpoint_returns_ok(self, client):
        """GET /api/chatbot/health — returns ok."""
        res = client.get('/api/chatbot/health')
        assert res.status_code == 200
        assert res.get_json()['status'] == 'ok'

    def test_message_no_auth_returns_401(self, client):
        """POST /api/chatbot/message — no token → 401."""
        res = client.post(self.ROUTE, json={'message': 'Hello'})
        assert res.status_code == 401

    def test_message_fake_token_returns_401(self, client):
        """POST /api/chatbot/message — fake token → 401."""
        res = client.post(self.ROUTE,
            json={'message': 'Hello'},
            headers={'Authorization': 'Bearer fake.token.here'}
        )
        assert res.status_code == 401

    def test_message_missing_message_field_returns_400(self, client, auth):
        """POST /api/chatbot/message — no message key → 400."""
        res = client.post(self.ROUTE, json={}, headers=auth)
        assert res.status_code == 400
        assert 'error' in res.get_json()

    def test_message_empty_string_returns_400(self, client, auth):
        """POST /api/chatbot/message — empty message string → 400."""
        res = client.post(self.ROUTE, json={'message': '   '}, headers=auth)
        assert res.status_code == 400

    def test_message_valid_returns_200_with_response(self, client, auth):
        """POST /api/chatbot/message — valid message → 200 + response text."""
        res = client.post(self.ROUTE,
            json={'message': 'How can I save more money?'},
            headers=auth
        )
        assert res.status_code == 200
        data = res.get_json()
        assert data.get('success') is True
        assert 'response'   in data
        assert 'intent'     in data
        assert 'timestamp'  in data

    def test_message_response_is_non_empty(self, client, auth):
        """POST /api/chatbot/message — response text is not empty."""
        res = client.post(self.ROUTE,
            json={'message': 'What is my balance?'},
            headers=auth
        )
        if res.status_code == 200:
            assert len(res.get_json()['response']) > 0


# ================================================================
#  8. REPORT EXPORT  /api/report/...
# ================================================================

class TestReport:

    ROUTE = '/api/report/transactions'

    def test_export_without_auth_returns_401(self, client):
        """GET /api/report/transactions — no token → 401."""
        res = client.get(self.ROUTE)
        assert res.status_code == 401

    def test_export_csv_with_auth_returns_200(self, client, auth):
        """GET /api/report/transactions — valid token → 200 CSV file."""
        res = client.get(f'{self.ROUTE}?format=csv', headers=auth)
        assert res.status_code == 200

    def test_export_content_type_is_csv(self, client, auth):
        """GET /api/report/transactions — Content-Type is text/csv."""
        res = client.get(f'{self.ROUTE}?format=csv', headers=auth)
        assert 'text/csv' in res.content_type

    def test_export_has_content_disposition_header(self, client, auth):
        """GET /api/report/transactions — response has Content-Disposition attachment header."""
        res = client.get(f'{self.ROUTE}?format=csv', headers=auth)
        cd = res.headers.get('Content-Disposition', '')
        assert 'attachment' in cd
        assert '.csv'       in cd

    def test_export_csv_has_header_row(self, client, auth):
        """GET /api/report/transactions CSV — first line is the header row."""
        res = client.get(f'{self.ROUTE}?format=csv', headers=auth)
        first_line = res.data.decode('utf-8').splitlines()[0]
        assert 'id'          in first_line
        assert 'type'        in first_line
        assert 'category'    in first_line
        assert 'amount'      in first_line
        assert 'date'        in first_line

    def test_export_unsupported_format_returns_400(self, client, auth):
        """GET /api/report/transactions?format=pdf — unsupported format → 400."""
        res = client.get(f'{self.ROUTE}?format=pdf', headers=auth)
        assert res.status_code == 400


# ================================================================
#  9. ADMIN  /api/admin/...
# ================================================================

class TestAdmin:

    def test_list_users_no_auth_returns_403(self, client):
        """GET /api/admin/users — no token → 403."""
        assert client.get('/api/admin/users').status_code == 403

    def test_list_users_regular_user_returns_403(self, client, auth):
        """GET /api/admin/users — non-admin token → 403."""
        assert client.get('/api/admin/users', headers=auth).status_code == 403

    def test_admin_stats_no_auth_returns_403(self, client):
        """GET /api/admin/stats — no token → 403."""
        assert client.get('/api/admin/stats').status_code == 403

    def test_admin_stats_regular_user_returns_403(self, client, auth):
        """GET /api/admin/stats — non-admin token → 403."""
        assert client.get('/api/admin/stats', headers=auth).status_code == 403

    def test_reset_password_missing_password_field(self, client, auth):
        """POST /api/admin/users/1/reset-password — non-admin → 403."""
        res = client.post('/api/admin/users/1/reset-password',
                          json={'password': 'newpass123'}, headers=auth)
        assert res.status_code == 403

    def test_toggle_admin_requires_admin(self, client, auth):
        """POST /api/admin/users/1/toggle-admin — non-admin → 403."""
        assert client.post('/api/admin/users/1/toggle-admin', headers=auth).status_code == 403

    def test_delete_user_requires_admin(self, client, auth):
        """DELETE /api/admin/users/1 — non-admin → 403."""
        assert client.delete('/api/admin/users/1', headers=auth).status_code == 403


# ================================================================
#  10. RANDOM FOREST MODEL — DIRECT FILE TESTS
# ================================================================

# class TestRandomForestModel:

#     def _find_model(self):
#         paths = [
#             'models/rf_model.pkl', 'models/model.pkl',
#             'ml_models/rf_model.pkl', 'rf_model.pkl', 'model.pkl',
#         ]
#         return next((p for p in paths if os.path.exists(p)), None)

#     # def test_model_file_exists_on_disk(self):
#     #     """Trained .pkl file exists — run train_models.py first if missing."""
#     #     assert self._find_model() is not None, \
#     #         "No .pkl file found. Run train_models.py to generate it."

#     def test_model_loads_without_error(self):
#         """joblib.load() succeeds without exception."""
#         import joblib
#         path = self._find_model()
#         if not path: pytest.skip("No model file found.")
#         assert joblib.load(path) is not None

#     def test_model_is_random_forest_type(self):
#         """Loaded model is a scikit-learn RandomForestClassifier or Regressor."""
#         import joblib
#         from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
#         path = self._find_model()
#         if not path: pytest.skip("No model file found.")
#         assert isinstance(joblib.load(path), (RandomForestClassifier, RandomForestRegressor))

#     def test_model_has_predict_method(self):
#         """Model has a predict() method."""
#         import joblib
#         path = self._find_model()
#         if not path: pytest.skip("No model file found.")
#         assert hasattr(joblib.load(path), 'predict')

#     def test_model_has_predict_proba_method(self):
#         """Model has a predict_proba() method for probability scores."""
#         import joblib
#         path = self._find_model()
#         if not path: pytest.skip("No model file found.")
#         assert hasattr(joblib.load(path), 'predict_proba')

#     def test_model_feature_count_is_positive(self):
#         """Model was trained on at least 1 feature."""
#         import joblib
#         path = self._find_model()
#         if not path: pytest.skip("No model file found.")
#         assert joblib.load(path).n_features_in_ > 0

#     def test_model_has_multiple_trees(self):
#         """Random Forest contains more than one decision tree."""
#         import joblib
#         path = self._find_model()
#         if not path: pytest.skip("No model file found.")
#         assert len(joblib.load(path).estimators_) > 1

#     def test_prediction_probabilities_in_valid_range(self):
#         """predict_proba() output values are all between 0.0 and 1.0."""
#         import joblib, numpy as np
#         path = self._find_model()
#         if not path: pytest.skip("No model file found.")
#         model = joblib.load(path)
#         probs = model.predict_proba(np.zeros((1, model.n_features_in_)))[0]
#         assert all(0.0 <= p <= 1.0 for p in probs)

#     def test_prediction_probabilities_sum_to_one(self):
#         """predict_proba() output sums to 1.0."""
#         import joblib, numpy as np
#         path = self._find_model()
#         if not path: pytest.skip("No model file found.")
#         model = joblib.load(path)
#         probs = model.predict_proba(np.zeros((1, model.n_features_in_)))[0]
#         assert abs(sum(probs) - 1.0) < 1e-6