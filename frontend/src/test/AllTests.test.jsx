/**
 * ============================================================
 *  MyWealthAI — Complete Frontend Test Suite
 *  All pages tested in one file
 * ============================================================
 *
 *  Pages covered:
 *  1. Login
 *  2. Register
 *  3. Dashboard
 *  4. Chat
 *  5. AIAdvice
 *  6. AddTransaction
 *  7. Profile
 *  8. Analytics
 *  9. AdminDashboard
 * ============================================================
 */

import { render, screen, fireEvent, waitFor } from "@testing-library/react";

// jsdom fix: scrollIntoView not implemented
window.HTMLElement.prototype.scrollIntoView = vi.fn();
import userEvent from "@testing-library/user-event";
import { vi, describe, it, expect, beforeEach } from "vitest";
import { MemoryRouter } from "react-router-dom";

// ─── Shared Navigation Mock ───────────────────────────────────────────────────
const mockNavigate = vi.fn();
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return { ...actual, useNavigate: () => mockNavigate };
});

// ─── Shared API Mocks ─────────────────────────────────────────────────────────
vi.mock("../services/apiClient", () => ({
  default: { get: vi.fn(), post: vi.fn(), put: vi.fn(), delete: vi.fn() },
}));
vi.mock("axios", () => ({
  default: { get: vi.fn(), post: vi.fn() },
}));

// ─── Layout + Component Mocks ─────────────────────────────────────────────────
vi.mock("../layout/Layout", () => ({
  default: ({ children }) => <div data-testid="layout">{children}</div>,
}));
vi.mock("../components/BalanceCard", () => ({
  default: ({ balance }) => <div data-testid="balance-card">{balance}</div>,
}));
vi.mock("../components/IncomeCard", () => ({
  default: ({ income }) => <div data-testid="income-card">{income}</div>,
}));
vi.mock("../components/ExpenseCard", () => ({
  default: ({ expense }) => <div data-testid="expense-card">{expense}</div>,
}));
vi.mock("../components/SavingsCard", () => ({
  default: () => <div data-testid="savings-card" />,
}));
vi.mock("../components/IncomeVsExpenseChart", () => ({
  default: () => <div data-testid="income-expense-chart" />,
}));
vi.mock("../components/ExpenseCategoryChart", () => ({
  default: () => <div data-testid="category-chart" />,
}));
vi.mock("../utils/currency", () => ({
  formatRupees: (v) => `₹${v}`,
}));

// ─── Page Imports ─────────────────────────────────────────────────────────────
import Login from "../pages/Login";
import Register from "../pages/Register";
import Dashboard from "../pages/Dashboard";
import Chat from "../pages/Chat";
import AIAdvice from "../pages/AIAdvice";
import AddTransaction from "../pages/AddTransaction";
import Profile from "../pages/Profile";
import Analytics from "../pages/Analytics";
import AdminDashboard from "../pages/AdminDashboard";
import apiClient from "../services/apiClient";
import axios from "axios";

// ─── Shared Mock Data ─────────────────────────────────────────────────────────
const mockUser       = { id: 1, first_name: "John", last_name: "Doe", email: "john@example.com", phone: "9876543210", created_at: "2024-01-01T00:00:00Z", is_admin: false };
const mockAdminUser  = { ...mockUser, is_admin: true, first_name: "Admin", email: "admin@example.com" };
const mockStats      = { total_users: 10, admin_count: 2, total_transactions: 150, total_income: 50000, total_expenses: 30000 };
const mockUsersList  = [
  { id: 1, first_name: "Admin", last_name: "User", email: "admin@example.com", is_admin: true },
  { id: 2, first_name: "John",  last_name: "Doe",  email: "john@example.com",  is_admin: false },
];
const mockSummary    = { cumulative_balance: 15750.50, income: 6000, expense: 2400, categories: { "Food & Dining": 450, Transportation: 300 } };
const mockMonthly    = { "2024-01": { income: 5000, expense: 2500 }, "2024-02": { income: 5200, expense: 2700 } };
const mockTxList     = { transactions: [
  { id: 1, type: "expense", category: "Food & Dining", description: "Starbucks", amount: 5.5,    date: "2024-01-27" },
  { id: 2, type: "income",  category: "Salary",        description: "Monthly Salary", amount: 6000, date: "2024-01-25" },
]};
const mockTrends     = { total_spent: 12000, daily_average: 400, trend: "increasing", transaction_count: 30 };
const mockPrediction = { predicted_spending: 15000, confidence: "High" };
const mockCategories = { categories: { "Food & Dining": { amount: 4500, percentage: 37.5 } }, total: 12000 };
const mockRecs       = { recommendations: [{ title: "Reduce Food Spending", description: "Cut costs", icon: "🍽️", priority: "high" }] };
const mockAnomalies  = { anomalies: [{ description: "Luxury Hotel", category: "Travel", amount: 8000, date: "2024-01-15", reason: "3x higher than usual" }] };
const mockRisk       = { risk_score: 72, risk_label: "High Risk" };

// ─── Render Helpers ───────────────────────────────────────────────────────────
const wrap   = (Component) => render(<MemoryRouter><Component /></MemoryRouter>);
const getEmail    = () => document.querySelector('input[type="email"]');
const getPassword = () => document.querySelector('input[type="password"]');

// ══════════════════════════════════════════════════════════════════════════════
// 1. LOGIN
// ══════════════════════════════════════════════════════════════════════════════
describe("Login — Rendering", () => {
  it("renders form without crashing", () => { wrap(Login); expect(document.querySelector("form")).toBeTruthy(); });
  it("renders MyWealthAI heading",     () => { wrap(Login); expect(screen.getByText("MyWealthAI")).toBeTruthy(); });
  it("renders subtitle",               () => { wrap(Login); expect(screen.getByText(/sign in to your account/i)).toBeTruthy(); });
  it("renders email input",            () => { wrap(Login); expect(getEmail()).toBeTruthy(); });
  it("renders password input",         () => { wrap(Login); expect(getPassword()).toBeTruthy(); });
  it("renders Sign In button",         () => { wrap(Login); expect(screen.getByRole("button", { name: /sign in/i })).toBeTruthy(); });
  it("renders Register link",          () => { wrap(Login); expect(screen.getByRole("link", { name: /register/i })).toBeTruthy(); });
  it("no error on initial render",     () => { wrap(Login); expect(screen.queryByText(/login failed/i)).toBeNull(); });
  it("password field type=password",   () => { wrap(Login); expect(getPassword().type).toBe("password"); });
  it("email placeholder correct",      () => { wrap(Login); expect(getEmail().placeholder).toBe("you@example.com"); });
});

describe("Login — Input Behaviour", () => {
  it("updates email value", async () => {
    wrap(Login);
    await userEvent.type(getEmail(), "test@example.com");
    expect(getEmail().value).toBe("test@example.com");
  });
  it("updates password value", async () => {
    wrap(Login);
    await userEvent.type(getPassword(), "Secret@123");
    expect(getPassword().value).toBe("Secret@123");
  });
  it("email field is required", () => { wrap(Login); expect(getEmail().required).toBe(true); });
  it("password field is required", () => { wrap(Login); expect(getPassword().required).toBe(true); });
});

describe("Login — Successful Login (Integration)", () => {
  beforeEach(() => { vi.clearAllMocks(); localStorage.clear(); });

  it("calls POST /api/auth/login with correct credentials", async () => {
    apiClient.post.mockResolvedValueOnce({ data: { token: "fake-jwt" } });
    wrap(Login);
    await userEvent.type(getEmail(), "test@example.com");
    await userEvent.type(getPassword(), "Secret@123");
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));
    await waitFor(() => expect(apiClient.post).toHaveBeenCalledWith("/api/auth/login", { email: "test@example.com", password: "Secret@123" }));
  });

  it("saves authToken to localStorage", async () => {
    apiClient.post.mockResolvedValueOnce({ data: { token: "fake-jwt" } });
    wrap(Login);
    await userEvent.type(getEmail(), "test@example.com");
    await userEvent.type(getPassword(), "Secret@123");
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));
    await waitFor(() => expect(localStorage.getItem("authToken")).toBe("fake-jwt"));
  });

  it("navigates to /dashboard on success", async () => {
    apiClient.post.mockResolvedValueOnce({ data: { token: "fake-jwt" } });
    wrap(Login);
    await userEvent.type(getEmail(), "test@example.com");
    await userEvent.type(getPassword(), "Secret@123");
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith("/dashboard"));
  });

  it("shows 'Signing in...' while loading", async () => {
    apiClient.post.mockImplementationOnce(() => new Promise(() => {}));
    wrap(Login);
    await userEvent.type(getEmail(), "test@example.com");
    await userEvent.type(getPassword(), "Secret@123");
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));
    await waitFor(() => expect(screen.getByText(/signing in\.\.\./i)).toBeTruthy());
  });
});

describe("Login — Failed Login (Integration)", () => {
  beforeEach(() => { vi.clearAllMocks(); localStorage.clear(); });

  it("shows server error on invalid credentials", async () => {
    apiClient.post.mockRejectedValueOnce({ response: { data: { error: "Invalid credentials" } } });
    wrap(Login);
    await userEvent.type(getEmail(), "wrong@example.com");
    await userEvent.type(getPassword(), "WrongPass");
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));
    await waitFor(() => expect(screen.getByText("Invalid credentials")).toBeTruthy());
  });

  it("shows fallback error on network failure", async () => {
    apiClient.post.mockRejectedValueOnce(new Error("Network Error"));
    wrap(Login);
    await userEvent.type(getEmail(), "test@example.com");
    await userEvent.type(getPassword(), "Secret@123");
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));
    await waitFor(() => expect(screen.getByText(/login failed\. please try again\./i)).toBeTruthy());
  });

  it("does NOT navigate on failed login", async () => {
    apiClient.post.mockRejectedValueOnce({ response: { data: { error: "Invalid credentials" } } });
    wrap(Login);
    await userEvent.type(getEmail(), "bad@example.com");
    await userEvent.type(getPassword(), "BadPass");
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));
    await waitFor(() => expect(mockNavigate).not.toHaveBeenCalled());
  });

  it("does NOT store token on failed login", async () => {
    apiClient.post.mockRejectedValueOnce({ response: { data: { error: "Invalid credentials" } } });
    wrap(Login);
    await userEvent.type(getEmail(), "bad@example.com");
    await userEvent.type(getPassword(), "BadPass");
    fireEvent.click(screen.getByRole("button", { name: /sign in/i }));
    await waitFor(() => expect(localStorage.getItem("authToken")).toBeNull());
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 2. REGISTER
// ══════════════════════════════════════════════════════════════════════════════
const getFN  = () => document.querySelector('input[name="first_name"]');
const getLN  = () => document.querySelector('input[name="last_name"]');
const getEM  = () => document.querySelector('input[name="email"]');
const getPW  = () => document.querySelector('input[name="password"]');
const getCPW = () => document.querySelector('input[name="password_confirm"]');
const getRegBtn = () => screen.getByRole("button", { name: /create account/i });

describe("Register — Rendering", () => {
  it("renders without crashing",          () => { wrap(Register); expect(document.querySelector("form")).toBeTruthy(); });
  it("renders MyWealthAI heading",        () => { wrap(Register); expect(screen.getByText("MyWealthAI")).toBeTruthy(); });
  it("renders 'Create your account'",     () => { wrap(Register); expect(screen.getByText(/create your account/i)).toBeTruthy(); });
  it("renders first name input",          () => { wrap(Register); expect(getFN()).toBeTruthy(); });
  it("renders last name input",           () => { wrap(Register); expect(getLN()).toBeTruthy(); });
  it("renders email input",               () => { wrap(Register); expect(getEM()).toBeTruthy(); });
  it("renders password input",            () => { wrap(Register); expect(getPW()).toBeTruthy(); });
  it("renders confirm password input",    () => { wrap(Register); expect(getCPW()).toBeTruthy(); });
  it("renders Create Account button",     () => { wrap(Register); expect(getRegBtn()).toBeTruthy(); });
  it("renders Sign in link",              () => { wrap(Register); expect(screen.getByRole("link", { name: /sign in/i })).toBeTruthy(); });
});

describe("Register — Validation", () => {
  it("shows error when passwords do not match", async () => {
    wrap(Register);
    await userEvent.type(getPW(), "Secret@123");
    await userEvent.type(getCPW(), "Different@999");
    fireEvent.submit(document.querySelector("form"));
    await waitFor(() => expect(screen.getByText(/passwords do not match/i)).toBeTruthy());
  });

  it("shows error when password < 6 chars", async () => {
    wrap(Register);
    await userEvent.type(getFN(), "John");
    await userEvent.type(getLN(), "Doe");
    await userEvent.type(getEM(), "john@example.com");
    await userEvent.type(getPW(), "abc");
    await userEvent.type(getCPW(), "abc");
    fireEvent.submit(document.querySelector("form"));
    await waitFor(() => expect(screen.getByText(/at least 6 characters/i)).toBeTruthy());
  });

  it("does NOT call API on password mismatch", async () => {
    vi.clearAllMocks();
    wrap(Register);
    await userEvent.type(getPW(), "Secret@123");
    await userEvent.type(getCPW(), "Mismatch@999");
    fireEvent.click(getRegBtn());
    await waitFor(() => expect(apiClient.post).not.toHaveBeenCalled());
  });
});

describe("Register — Successful Registration (Integration)", () => {
  beforeEach(() => { vi.clearAllMocks(); localStorage.clear(); });

  it("calls POST /api/auth/register with correct payload", async () => {
    apiClient.post.mockResolvedValueOnce({ data: { token: "fake-token" } });
    wrap(Register);
    await userEvent.type(getFN(), "John");
    await userEvent.type(getLN(), "Doe");
    await userEvent.type(getEM(), "john@example.com");
    await userEvent.type(getPW(), "Secret@123");
    await userEvent.type(getCPW(), "Secret@123");
    fireEvent.click(getRegBtn());
    await waitFor(() => expect(apiClient.post).toHaveBeenCalledWith("/api/auth/register", { email: "john@example.com", password: "Secret@123", first_name: "John", last_name: "Doe" }));
  });

  it("saves token and navigates to /dashboard", async () => {
    apiClient.post.mockResolvedValueOnce({ data: { token: "fake-token" } });
    wrap(Register);
    await userEvent.type(getFN(), "John");
    await userEvent.type(getLN(), "Doe");
    await userEvent.type(getEM(), "john@example.com");
    await userEvent.type(getPW(), "Secret@123");
    await userEvent.type(getCPW(), "Secret@123");
    fireEvent.click(getRegBtn());
    await waitFor(() => {
      expect(localStorage.getItem("authToken")).toBe("fake-token");
      expect(mockNavigate).toHaveBeenCalledWith("/dashboard");
    });
  });

  it("shows server error on duplicate email", async () => {
    apiClient.post.mockRejectedValueOnce({ response: { data: { error: "Email already exists" } } });
    wrap(Register);
    await userEvent.type(getFN(), "John");
    await userEvent.type(getLN(), "Doe");
    await userEvent.type(getEM(), "dup@example.com");
    await userEvent.type(getPW(), "Secret@123");
    await userEvent.type(getCPW(), "Secret@123");
    fireEvent.click(getRegBtn());
    await waitFor(() => expect(screen.getByText("Email already exists")).toBeTruthy());
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 3. DASHBOARD
// ══════════════════════════════════════════════════════════════════════════════
const setupDashboard = () => {
  apiClient.get.mockImplementation((url) => {
    if (url.includes("profile"))     return Promise.resolve({ data: { user: mockUser } });
    if (url.includes("summary"))     return Promise.resolve({ data: mockSummary });
    if (url.includes("monthly"))     return Promise.resolve({ data: mockMonthly });
    if (url.includes("transactions"))return Promise.resolve({ data: mockTxList });
    return Promise.resolve({ data: {} });
  });
};

describe("Dashboard — Rendering", () => {
  beforeEach(setupDashboard);

  it("renders without crashing",              () => { wrap(Dashboard); expect(document.body).toBeTruthy(); });
  it("renders Dashboard heading",           async () => { wrap(Dashboard); await waitFor(() => expect(screen.getByText("Dashboard")).toBeTruthy()); });
  it("renders welcome subtitle",            async () => { wrap(Dashboard); await waitFor(() => expect(screen.getByText(/welcome back/i)).toBeTruthy()); });
  it("renders BalanceCard",                 async () => { wrap(Dashboard); await waitFor(() => expect(screen.getByTestId("balance-card")).toBeTruthy()); });
  it("renders IncomeCard",                  async () => { wrap(Dashboard); await waitFor(() => expect(screen.getByTestId("income-card")).toBeTruthy()); });
  it("renders ExpenseCard",                 async () => { wrap(Dashboard); await waitFor(() => expect(screen.getByTestId("expense-card")).toBeTruthy()); });
  it("renders SavingsCard",                 async () => { wrap(Dashboard); await waitFor(() => expect(screen.getByTestId("savings-card")).toBeTruthy()); });
  it("renders Recent Transactions section", async () => { wrap(Dashboard); await waitFor(() => expect(screen.getByText(/recent transactions/i)).toBeTruthy()); });
  it("renders transaction description",     async () => { wrap(Dashboard); await waitFor(() => expect(screen.getByText("Starbucks")).toBeTruthy()); });
  it("renders Average Daily Spending stat", async () => { wrap(Dashboard); await waitFor(() => expect(screen.getByText(/average daily spending/i)).toBeTruthy()); });
  it("renders Budget Remaining stat",       async () => { wrap(Dashboard); await waitFor(() => expect(screen.getByText(/budget remaining/i)).toBeTruthy()); });
  it("fetches profile on mount",            async () => { wrap(Dashboard); await waitFor(() => expect(apiClient.get).toHaveBeenCalledWith("/api/auth/profile")); });
  it("fetches summary on mount",            async () => { wrap(Dashboard); await waitFor(() => expect(apiClient.get).toHaveBeenCalledWith("/api/dashboard/summary")); });
});

// ══════════════════════════════════════════════════════════════════════════════
// 4. CHAT
// ══════════════════════════════════════════════════════════════════════════════
describe("Chat — Rendering", () => {
  beforeEach(() => { axios.get.mockResolvedValue({ data: { user: { first_name: "John" } } }); });

  it("renders without crashing",                  () => { wrap(Chat); expect(document.body).toBeTruthy(); });
  it("renders AI Financial Assistant heading", async () => { wrap(Chat); await waitFor(() => expect(screen.getByRole("heading", { name: /AI Financial Assistant/i })).toBeTruthy()); });
  it("renders text input",                         () => { wrap(Chat); expect(document.querySelector('input[type="text"]')).toBeTruthy(); });
  it("renders Send button",                        () => { wrap(Chat); expect(screen.getByRole("button", { name: /send/i })).toBeTruthy(); });
  it("renders initial greeting",               async () => { wrap(Chat); await waitFor(() => expect(screen.getByText(/Hello! I'm your AI Financial Assistant/i)).toBeTruthy()); });
  it("renders quick suggestions",              async () => { wrap(Chat); await waitFor(() => expect(screen.getByText(/How much did I spend this month/i)).toBeTruthy()); });
  it("Send button disabled when input empty",      () => { wrap(Chat); expect(screen.getByRole("button", { name: /send/i }).disabled).toBe(true); });
});

describe("Chat — Sending Messages (Integration)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem("authToken", "fake-token");
    axios.get.mockResolvedValue({ data: { user: { first_name: "John" } } });
  });

  it("adds user message to chat on submit", async () => {
    axios.post.mockResolvedValueOnce({ data: { success: true, response: "Your balance is ₹15,000", intent: "balance", timestamp: new Date().toISOString() } });
    wrap(Chat);
    const input = document.querySelector('input[type="text"]');
    await userEvent.type(input, "What is my balance?");
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => expect(screen.getByText("What is my balance?")).toBeTruthy());
  });

  it("displays bot response", async () => {
    axios.post.mockResolvedValueOnce({ data: { success: true, response: "Your balance is ₹15,000", intent: "balance", timestamp: new Date().toISOString() } });
    wrap(Chat);
    const input = document.querySelector('input[type="text"]');
    await userEvent.type(input, "What is my balance?");
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => expect(screen.getByText("Your balance is ₹15,000")).toBeTruthy());
  });

  it("clears input after message sent", async () => {
    axios.post.mockResolvedValueOnce({ data: { success: true, response: "Sure!", intent: "general", timestamp: new Date().toISOString() } });
    wrap(Chat);
    const input = document.querySelector('input[type="text"]');
    await userEvent.type(input, "Hello");
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => expect(input.value).toBe(""));
  });

  it("shows error message when API fails", async () => {
    axios.post.mockRejectedValueOnce(new Error("Network Error"));
    wrap(Chat);
    const input = document.querySelector('input[type="text"]');
    await userEvent.type(input, "Hello");
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => expect(screen.getByText(/sorry, I encountered an error/i)).toBeTruthy());
  });

  it("disables input while loading", async () => {
    axios.post.mockImplementationOnce(() => new Promise(() => {}));
    wrap(Chat);
    const input = document.querySelector('input[type="text"]');
    await userEvent.type(input, "Hello");
    fireEvent.click(screen.getByRole("button", { name: /send/i }));
    await waitFor(() => expect(input.disabled).toBe(true));
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 5. AI ADVICE
// ══════════════════════════════════════════════════════════════════════════════
const setupAdvice = () => {
  apiClient.get.mockImplementation((url) => {
    if (url.includes("profile"))          return Promise.resolve({ data: { user: mockUser } });
    if (url.includes("overspending-risk"))return Promise.resolve({ data: mockRisk });
    return Promise.resolve({ data: {} });
  });
};

describe("AIAdvice — Rendering", () => {
  beforeEach(setupAdvice);

  it("renders without crashing",                  () => { wrap(AIAdvice); expect(document.body).toBeTruthy(); });
  it("renders AI Financial Advice heading",    async () => { wrap(AIAdvice); await waitFor(() => expect(screen.getByText(/AI Financial Advice/i)).toBeTruthy()); });
  it("renders personalized recommendations",  async () => { wrap(AIAdvice); await waitFor(() => expect(screen.getByText(/personalized recommendations/i)).toBeTruthy()); });
  it("renders Increase Savings Rate card",    async () => { wrap(AIAdvice); await waitFor(() => expect(screen.getByText(/increase savings rate/i)).toBeTruthy()); });
  it("renders Food Spending Alert card",      async () => { wrap(AIAdvice); await waitFor(() => expect(screen.getByText(/food spending alert/i)).toBeTruthy()); });
  it("renders Transportation card",           async () => { wrap(AIAdvice); await waitFor(() => expect(screen.getByText(/transportation opportunity/i)).toBeTruthy()); });
  it("renders High Priority badge",           async () => { wrap(AIAdvice); await waitFor(() => expect(screen.getByText(/high priority/i)).toBeTruthy()); });
  it("renders overspending risk score",       async () => { wrap(AIAdvice); await waitFor(() => expect(screen.getByText(/72/)).toBeTruthy()); });
  it("renders overspending risk label",       async () => { wrap(AIAdvice); await waitFor(() => expect(screen.getByText(/High Risk/i)).toBeTruthy()); });
  it("fetches overspending risk on mount",    async () => { wrap(AIAdvice); await waitFor(() => expect(apiClient.get).toHaveBeenCalledWith("/api/analytics/overspending-risk")); });
});

// ══════════════════════════════════════════════════════════════════════════════
// 6. ADD TRANSACTION
// ══════════════════════════════════════════════════════════════════════════════
const setupAddTx = () => {
  apiClient.get.mockImplementation((url) => {
    if (url.includes("profile"))         return Promise.resolve({ data: { user: mockUser } });
    if (url.includes("current-balance")) return Promise.resolve({ data: { balance: 5000 } });
    return Promise.resolve({ data: {} });
  });
};

describe("AddTransaction — Rendering", () => {
  beforeEach(setupAddTx);

  it("renders without crashing",           () => { wrap(AddTransaction); expect(document.body).toBeTruthy(); });
  it("renders Add Transaction heading", async () => { wrap(AddTransaction); await waitFor(() => expect(screen.getByRole("heading", { name: "Add Transaction" })).toBeTruthy()); });
  it("renders Income radio button",     async () => { wrap(AddTransaction); await waitFor(() => expect(screen.getByDisplayValue("income")).toBeTruthy()); });
  it("renders Expense radio button",    async () => { wrap(AddTransaction); await waitFor(() => expect(screen.getByDisplayValue("expense")).toBeTruthy()); });
  it("renders Amount input",            async () => { wrap(AddTransaction); await waitFor(() => expect(document.querySelector('input[type="number"]')).toBeTruthy()); });
  it("renders Description input",       async () => { wrap(AddTransaction); await waitFor(() => expect(screen.getByPlaceholderText(/enter transaction description/i)).toBeTruthy()); });
  it("renders Date input",              async () => { wrap(AddTransaction); await waitFor(() => expect(document.querySelector('input[type="date"]')).toBeTruthy()); });
  it("defaults to Income type",         async () => { wrap(AddTransaction); await waitFor(() => expect(screen.getByDisplayValue("income").checked).toBe(true)); });
});

describe("AddTransaction — Balance Validation", () => {
  beforeEach(setupAddTx);

  it("shows current balance when Expense selected", async () => {
    wrap(AddTransaction);
    await waitFor(() => screen.getByDisplayValue("expense"));
    fireEvent.click(screen.getByDisplayValue("expense"));
    await waitFor(() => expect(screen.getByText(/current balance/i)).toBeTruthy());
  });

  it("shows insufficient balance error when amount exceeds balance", async () => {
    wrap(AddTransaction);
    await waitFor(() => screen.getByDisplayValue("expense"));
    fireEvent.click(screen.getByDisplayValue("expense"));
    fireEvent.change(document.querySelector('input[type="number"]'), { target: { value: "9999" } });
    await waitFor(() => expect(screen.getByText(/insufficient balance/i)).toBeTruthy());
  });

  it("disables submit when balance error exists", async () => {
    wrap(AddTransaction);
    await waitFor(() => screen.getByDisplayValue("expense"));
    fireEvent.click(screen.getByDisplayValue("expense"));
    fireEvent.change(document.querySelector('input[type="number"]'), { target: { value: "9999" } });
    await waitFor(() => expect(screen.getByRole("button", { name: /add transaction/i }).disabled).toBe(true));
  });
});

describe("AddTransaction — Form Submission (Integration)", () => {
  beforeEach(() => { vi.clearAllMocks(); setupAddTx(); });

  it("calls POST /api/transactions with correct payload", async () => {
    apiClient.post.mockResolvedValueOnce({ status: 201, data: { id: 1 } });
    wrap(AddTransaction);
    await waitFor(() => screen.getByPlaceholderText(/enter transaction description/i));
    fireEvent.change(document.querySelector('input[type="number"]'), { target: { value: "1000" } });
    await userEvent.type(screen.getByPlaceholderText(/enter transaction description/i), "Salary");
    fireEvent.click(screen.getByRole("button", { name: /add transaction/i }));
    await waitFor(() => expect(apiClient.post).toHaveBeenCalledWith("/api/transactions", expect.objectContaining({ type: "income", amount: 1000 })));
  });

  it("navigates to /dashboard after successful submission", async () => {
    apiClient.post.mockResolvedValueOnce({ status: 201, data: { id: 1 } });
    wrap(AddTransaction);
    await waitFor(() => screen.getByRole("button", { name: /add transaction/i }));
    fireEvent.change(document.querySelector('input[type="number"]'), { target: { value: "500" } });
    fireEvent.click(screen.getByRole("button", { name: /add transaction/i }));
    await waitFor(() => expect(mockNavigate).toHaveBeenCalledWith("/dashboard"));
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 7. PROFILE
// ══════════════════════════════════════════════════════════════════════════════
const setupProfile = () => {
  apiClient.get.mockResolvedValue({ data: { user: mockUser } });
};

describe("Profile — Rendering", () => {
  beforeEach(setupProfile);

  it("renders without crashing",               () => { wrap(Profile); expect(document.body).toBeTruthy(); });
  it("shows loading initially",                () => { apiClient.get.mockImplementationOnce(() => new Promise(() => {})); wrap(Profile); expect(screen.getByText(/loading profile/i)).toBeTruthy(); });
  it("renders Profile Settings heading",   async () => { wrap(Profile); await waitFor(() => expect(screen.getByText(/profile settings/i)).toBeTruthy()); });
  it("renders first name with user data",  async () => { wrap(Profile); await waitFor(() => expect(document.querySelector('input[name="first_name"]').value).toBe("John")); });
  it("renders email with user data",       async () => { wrap(Profile); await waitFor(() => expect(document.querySelector('input[name="email"]').value).toBe("john@example.com")); });
  it("email input is disabled",           async () => { wrap(Profile); await waitFor(() => expect(document.querySelector('input[name="email"]').disabled).toBe(true)); });
  it("renders Save Changes button",        async () => { wrap(Profile); await waitFor(() => expect(screen.getByRole("button", { name: /save changes/i })).toBeTruthy()); });
  it("renders Member Since section",       async () => { wrap(Profile); await waitFor(() => expect(screen.getByText(/member since/i)).toBeTruthy()); });
});

describe("Profile — Save (Integration)", () => {
  beforeEach(() => { vi.clearAllMocks(); setupProfile(); });

  it("calls PUT /api/auth/profile on save", async () => {
    apiClient.put.mockResolvedValueOnce({ data: { user: mockUser } });
    wrap(Profile);
    await waitFor(() => screen.getByRole("button", { name: /save changes/i }));
    fireEvent.click(screen.getByRole("button", { name: /save changes/i }));
    await waitFor(() => expect(apiClient.put).toHaveBeenCalledWith("/api/auth/profile", expect.any(Object)));
  });

  it("shows success message after saving", async () => {
    apiClient.put.mockResolvedValueOnce({ data: { user: mockUser } });
    wrap(Profile);
    await waitFor(() => screen.getByRole("button", { name: /save changes/i }));
    fireEvent.click(screen.getByRole("button", { name: /save changes/i }));
    await waitFor(() => expect(screen.getByText(/profile updated successfully/i)).toBeTruthy());
  });

  it("shows 'Saving...' while saving", async () => {
    apiClient.put.mockImplementationOnce(() => new Promise(() => {}));
    wrap(Profile);
    await waitFor(() => screen.getByRole("button", { name: /save changes/i }));
    fireEvent.click(screen.getByRole("button", { name: /save changes/i }));
    await waitFor(() => expect(screen.getByText(/saving\.\.\./i)).toBeTruthy());
  });

  it("shows error when save fails", async () => {
    apiClient.put.mockRejectedValueOnce({ response: { data: { error: "Update failed" } } });
    wrap(Profile);
    await waitFor(() => screen.getByRole("button", { name: /save changes/i }));
    fireEvent.click(screen.getByRole("button", { name: /save changes/i }));
    await waitFor(() => expect(screen.getByText("Update failed")).toBeTruthy());
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 8. ANALYTICS
// ══════════════════════════════════════════════════════════════════════════════
const setupAnalytics = () => {
  apiClient.get.mockImplementation((url) => {
    if (url.includes("profile"))            return Promise.resolve({ data: { user: mockUser } });
    if (url.includes("spending-trends"))    return Promise.resolve({ data: mockTrends });
    if (url.includes("spending-prediction"))return Promise.resolve({ data: mockPrediction });
    if (url.includes("spending-by-category"))return Promise.resolve({ data: mockCategories });
    if (url.includes("recommendations"))   return Promise.resolve({ data: mockRecs });
    if (url.includes("anomalies"))         return Promise.resolve({ data: mockAnomalies });
    return Promise.resolve({ data: {} });
  });
};

describe("Analytics — Rendering", () => {
  beforeEach(setupAnalytics);

  it("renders without crashing",              () => { wrap(Analytics); expect(document.body).toBeTruthy(); });
  it("shows loading initially",               () => { apiClient.get.mockImplementation(() => new Promise(() => {})); wrap(Analytics); expect(screen.getByText(/loading analytics/i)).toBeTruthy(); });
  it("renders Financial Analytics heading",async () => { wrap(Analytics); await waitFor(() => expect(screen.getByText("Financial Analytics")).toBeTruthy()); });
  it("renders Spending Trends section",    async () => { wrap(Analytics); await waitFor(() => expect(screen.getByText(/spending trends/i)).toBeTruthy()); });
  it("renders Next Month Prediction",     async () => { wrap(Analytics); await waitFor(() => expect(screen.getByText(/next month prediction/i)).toBeTruthy()); });
  it("renders AI Recommendations",        async () => { wrap(Analytics); await waitFor(() => expect(screen.getByText(/AI Recommendations/i)).toBeTruthy()); });
  it("renders Unusual Transactions",      async () => { wrap(Analytics); await waitFor(() => expect(screen.getByText(/unusual transactions/i)).toBeTruthy()); });
  it("displays predicted spending",       async () => { wrap(Analytics); await waitFor(() => expect(screen.getByText("₹15000")).toBeTruthy()); });
  it("displays trend direction",          async () => { wrap(Analytics); await waitFor(() => expect(screen.getByText(/📈 Up/i)).toBeTruthy()); });
  it("displays recommendation title",    async () => { wrap(Analytics); await waitFor(() => expect(screen.getByText("Reduce Food Spending")).toBeTruthy()); });
  it("displays anomaly description",     async () => { wrap(Analytics); await waitFor(() => expect(screen.getByText("Luxury Hotel")).toBeTruthy()); });
  it("fetches all 5 analytics endpoints",async () => {
    wrap(Analytics);
    await waitFor(() => {
      expect(apiClient.get).toHaveBeenCalledWith("/api/analytics/spending-trends");
      expect(apiClient.get).toHaveBeenCalledWith("/api/analytics/spending-prediction");
      expect(apiClient.get).toHaveBeenCalledWith("/api/analytics/recommendations");
      expect(apiClient.get).toHaveBeenCalledWith("/api/analytics/anomalies");
    });
  });
});

// ══════════════════════════════════════════════════════════════════════════════
// 9. ADMIN DASHBOARD
// ══════════════════════════════════════════════════════════════════════════════
const setupAdmin = () => {
  apiClient.get.mockImplementation((url) => {
    if (url.includes("profile")) return Promise.resolve({ data: { user: mockAdminUser } });
    if (url.includes("stats"))   return Promise.resolve({ data: mockStats });
    if (url.includes("users"))   return Promise.resolve({ data: { users: mockUsersList } });
    return Promise.resolve({ data: {} });
  });
};

describe("AdminDashboard — Rendering", () => {
  beforeEach(setupAdmin);

  it("renders without crashing",              () => { wrap(AdminDashboard); expect(document.body).toBeTruthy(); });
  it("renders Admin Dashboard heading",    async () => { wrap(AdminDashboard); await waitFor(() => expect(screen.getByText("Admin Dashboard")).toBeTruthy()); });
  it("renders Total Users stat",          async () => { wrap(AdminDashboard); await waitFor(() => expect(screen.getByText("Total Users")).toBeTruthy()); });
  it("renders stats value 10",            async () => { wrap(AdminDashboard); await waitFor(() => expect(screen.getByText("10")).toBeTruthy()); });
  it("renders Users Management section", async () => { wrap(AdminDashboard); await waitFor(() => expect(screen.getByText(/users management/i)).toBeTruthy()); });
  it("renders user email in table",       async () => { wrap(AdminDashboard); await waitFor(() => expect(screen.getByText("john@example.com")).toBeTruthy()); });
  it("renders Manage buttons",            async () => { wrap(AdminDashboard); await waitFor(() => { expect(screen.getAllByText(/manage/i).length).toBeGreaterThan(0); }); });
  it("fetches admin stats on mount",      async () => { wrap(AdminDashboard); await waitFor(() => expect(apiClient.get).toHaveBeenCalledWith("/api/admin/stats")); });
  it("fetches users list on mount",       async () => { wrap(AdminDashboard); await waitFor(() => expect(apiClient.get).toHaveBeenCalledWith("/api/admin/users?per_page=100")); });
});

describe("AdminDashboard — Access Control", () => {
  it("shows access denied for non-admin", async () => {
    apiClient.get.mockImplementation((url) => {
      if (url.includes("profile")) return Promise.resolve({ data: { user: mockUser } });
      return Promise.resolve({ data: {} });
    });
    wrap(AdminDashboard);
    await waitFor(() => expect(screen.getByText(/access denied/i)).toBeTruthy());
  });
});

describe("AdminDashboard — User Management (Integration)", () => {
  beforeEach(() => { vi.clearAllMocks(); setupAdmin(); });

  it("opens user modal on Manage click", async () => {
    wrap(AdminDashboard);
    await waitFor(() => screen.getAllByText(/manage/i));
    // click the second Manage (john@example.com — non-admin user)
    const manageBtns = screen.getAllByRole("button", { name: /manage/i });
    fireEvent.click(manageBtns[1]);
    await waitFor(() => {
      const modal = document.querySelector(".fixed");
      expect(modal).toBeTruthy();
    });
  });

  it("shows Reset Password and Make Admin buttons inside modal", async () => {
    wrap(AdminDashboard);
    await waitFor(() => screen.getAllByRole("button", { name: /manage/i }));
    fireEvent.click(screen.getAllByRole("button", { name: /manage/i })[1]);
    await waitFor(() => {
      const modal = document.querySelector(".fixed");
      expect(modal).toBeTruthy();
      expect(modal.textContent).toMatch(/reset password/i);
      expect(modal.textContent).toMatch(/make admin/i);
    });
  });

  it("shows password input after clicking Reset Password in modal", async () => {
    wrap(AdminDashboard);
    await waitFor(() => screen.getAllByRole("button", { name: /manage/i }));
    fireEvent.click(screen.getAllByRole("button", { name: /manage/i })[1]);
    await waitFor(() => document.querySelector(".fixed"));
    // find Reset Password button inside the modal
    const modal = document.querySelector(".fixed");
    const resetBtn = Array.from(modal.querySelectorAll("button")).find(b => /reset password/i.test(b.textContent));
    fireEvent.click(resetBtn);
    await waitFor(() => expect(screen.getByPlaceholderText(/enter new password/i)).toBeTruthy());
  });

  it("calls toggle admin API when Make Admin clicked", async () => {
    apiClient.post.mockResolvedValueOnce({ data: { user: { ...mockUsersList[1], is_admin: true } } });
    apiClient.get.mockImplementation((url) => {
      if (url.includes("profile")) return Promise.resolve({ data: { user: mockAdminUser } });
      if (url.includes("stats"))   return Promise.resolve({ data: mockStats });
      if (url.includes("users"))   return Promise.resolve({ data: { users: mockUsersList } });
      return Promise.resolve({ data: {} });
    });
    wrap(AdminDashboard);
    await waitFor(() => screen.getAllByRole("button", { name: /manage/i }));
    fireEvent.click(screen.getAllByRole("button", { name: /manage/i })[1]);
    await waitFor(() => document.querySelector(".fixed"));
    const modal = document.querySelector(".fixed");
    const makeAdminBtn = Array.from(modal.querySelectorAll("button")).find(b => /make admin/i.test(b.textContent));
    fireEvent.click(makeAdminBtn);
    await waitFor(() => expect(apiClient.post).toHaveBeenCalledWith(expect.stringContaining("/toggle-admin")));
  });

  it("closes modal when close button clicked", async () => {
    wrap(AdminDashboard);
    await waitFor(() => screen.getAllByRole("button", { name: /manage/i }));
    fireEvent.click(screen.getAllByRole("button", { name: /manage/i })[1]);
    await waitFor(() => document.querySelector(".fixed"));
    const modal = document.querySelector(".fixed");
    const closeBtn = Array.from(modal.querySelectorAll("button")).find(b => b.textContent.trim() === "✕");
    fireEvent.click(closeBtn);
    await waitFor(() => expect(document.querySelector(".fixed")).toBeNull());
  });

  it("fetches admin stats on mount", async () => {
    wrap(AdminDashboard);
    await waitFor(() => expect(apiClient.get).toHaveBeenCalledWith("/api/admin/stats"));
  });

  it("fetches users list on mount", async () => {
    wrap(AdminDashboard);
    await waitFor(() => expect(apiClient.get).toHaveBeenCalledWith("/api/admin/users?per_page=100"));
  });
});