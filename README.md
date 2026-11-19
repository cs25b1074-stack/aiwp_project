# 💰 Debt Repayment Planner — AI Search Optimizer

> **Find the mathematically optimal way to pay off your Loan & Credit Card using AI search algorithms**

---

## 🎯 The Problem

You have **two debts**: a **Loan** and a **Credit Card**, each with different interest rates. Every month you:

1. **Income** arrives
2. **Pay interest** on both debts
3. **Save** a fixed amount
4. **Use leftover** to repay debts — **but which one first?**

| Monthly Flow | Example |
|--------------|---------|
| Income | ₹20,000 |
| Loan Interest (14%) | −₹1,167 |
| Card Interest (36%) | −₹1,800 |
| Savings | −₹5,000 |
| **Leftover** | **₹12,033** |
| **Decision: Loan first or Card first?** | ← **Critical!** |

**The impact is huge:**
| Strategy | Total Interest | Months |
|----------|----------------|--------|
| **Card First (Optimal)** | **₹15,497** | 12 |
| Loan First | ₹24,581 | 13 |
| **Savings: ₹9,084** | | |

---

## 🧠 The Solution: AI Search Algorithms

We model debt repayment as a **search problem**:

| Search Concept | Debt Equivalent |
|----------------|-----------------|
| **State** | (Loan Balance, Card Balance) |
| **Start** | Your initial debts |
| **Goal** | (0, 0) — Debt free! |
| **Actions** | Pay Loan First / Pay Card First |
| **Step Cost** | Interest paid that month |
| **Path Cost (g)** | Total interest so far |
| **Heuristic (h)** | Estimated remaining interest |
| **f = g + h** | A* evaluation function |

---

## 🏆 Algorithms Implemented

| Algorithm | Strategy | Optimal? | Test 1 Interest | States (Test 1) |
|-----------|----------|----------|-----------------|-----------------|
| **A\*** | f = g + h (Best of both) | ✅ **Yes** | **₹15,497** | **29** |
| **UCS** | Lowest g (cost so far) | ✅ **Yes** | **₹15,497** | 243 |
| **BFS** | Fewest months (queue) | ❌ No | ₹19,897 | 2,599 |
| **DFS** | First path found (stack) | ❌ No | ₹24,581 | 13 |
| **Greedy** | Lowest h (estimate) | ❌ No | ₹24,581 | 13 |

> **A* wins:** Finds optimal plan *and* explores 8× fewer states than UCS using an admissible heuristic.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation
```bash
git clone https://github.com/cs25b1074-stack/aiwp_project.git
cd aiwp_project
git checkout main  # This branch
pip install -r requirements.txt
```

### Run the Project
```bash
python main.py
```

**Choose your interface:**
1. **Terminal Comparison** — Runs all 5 algorithms, prints comparison table
2. **Streamlit Web UI** — Interactive visual dashboard with charts

---

## 📊 Web UI Features (`streamlit_app.py`)

### Tab 1: Algorithm Comparison
- **Input sidebar** — Income, savings, loan amount/rate, card amount/rate
- **Comparison table** — Interest, months, states explored for all 5 algorithms
- **Bar charts** — Visual comparison of interest & states explored
- **Smart insight** — Tells you exactly which debt to pay first

### Tab 2: Monthly Repayment Schedule
- **Algorithm selector** — Choose which algorithm's plan to view
- **Interactive charts** — Loan, Card, and Total Debt over time
- **Month-by-month table** — Formatted balances & interest per month

---

## 📁 Project Structure (main branch)

```
aiwp_project/
├── 📄 main.py              # Terminal runner (choose CLI or Web UI)
├── 📄 streamlit_app.py     # Streamlit web UI with visualizations
├── 📄 compare_all.py       # Core logic: runs all 5 algorithms
├── 📄 requirements.txt     # Python dependencies
├── 📄 .gitignore           # Git ignore rules
└── 📄 README.md            # This file
```

> **Note:** Individual algorithm files (`ucs_debt.py`, `bfs_debt.py`, etc.) are on the `tanish` branch. This `main` branch contains the unified runner and web UI that imports from `compare_all.py`.

---

## 🧪 Standard Test Cases

| Test | Income | Savings | Loan | Loan Rate | Card | Card Rate | Optimal |
|------|--------|---------|------|-----------|------|-----------|---------|
| **Test 1** | ₹20,000 | ₹5,000 | ₹1,00,000 | 14% | ₹60,000 | 36% | **Card First** |
| **Test 2** | ₹15,000 | ₹3,000 | ₹50,000 | 12% | ₹40,000 | 42% | **Card First** |
| **Test 3** | ₹20,000 | ₹5,000 | ₹1,00,000 | 30% | ₹60,000 | 18% | **Loan First** |

---

## 💡 Key Insight for Your Debt

> **Always pay the HIGHER interest rate debt first!**

The math is unambiguous:
- **Card rate > Loan rate** → Pay **Card first** every month
- **Loan rate > Card rate** → Pay **Loan first** every month
- **Equal rates** → Order doesn't matter

This is exactly what **A* and UCS** discover automatically through search.

---

## 👥 Team

| Member | Role |
|--------|------|
| **Mithunn** | Greedy, A*, compare_all.py, Streamlit UI |
| **Ritu** | BFS |
| **Dharmik** | DFS |
| **Tanish** | UCS |

---

## 📜 License

Educational project for **AI with Python** course.

---

## 🎉 Run It Now!

```bash
git checkout main
pip install -r requirements.txt
python main.py
# Choose [1] for terminal or [2] for web UI
```

**Web UI opens at http://localhost:8501** — enter your debts and see the optimal plan! 💰