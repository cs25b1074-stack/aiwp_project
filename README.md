# 🏦 Debt Repayment Optimizer

> **Find the mathematically optimal way to pay off your Loan & Credit Card — using AI search algorithms**

---

## 🎯 The Problem

You have **two debts**: a Loan and a Credit Card, each with different interest rates. Every month you earn income, pay interest on both debts, put money into savings, and use whatever's left to repay the debts.

**The critical question:** *Which debt should you pay first each month — the Loan or the Card — to minimize total interest paid?*

| Monthly Flow | Example (Test 1) |
|--------------|------------------|
| Income arrives | ₹20,000 |
| Pay Loan interest (14%) | −₹1,167 |
| Pay Card interest (36%) | −₹1,800 |
| Put into savings | −₹5,000 |
| **Leftover for repayment** | **₹12,033** |
| **DECISION: Loan first or Card first?** | ← **This choice changes everything!** |

**The difference is staggering:**
| Strategy | Total Interest | Months |
|----------|---------------|--------|
| **Card First (Optimal)** | **₹15,497** | 12 |
| Loan First | ₹24,581 | 13 |
| **You save ₹9,084 just by choosing the right order!** | | |

---

## 🧠 The Solution: AI Search Algorithms

We formulate debt repayment as a **search problem** and compare **5 classic algorithms**:

| Search Concept | Debt Repayment |
|----------------|----------------|
| **State** | (Loan Balance, Card Balance) |
| **Start** | Your initial debts |
| **Goal** | (0, 0) — Debt free! |
| **Actions** | Pay Loan First / Pay Card First |
| **Step Cost** | Interest paid that month |
| **Path Cost (g)** | Total interest so far |
| **Heuristic (h)** | Estimated remaining interest |
| **f = g + h** | A* evaluation function |

### 🏆 Algorithm Comparison

| Algorithm | Strategy | Optimal? | Test 1 Interest | Test 1 States |
|-----------|----------|----------|-----------------|---------------|
| **A\*** | f = g + h (Best of both) | ✅ **Yes** | **₹15,497** | **29** |
| **UCS** | Lowest g (cost so far) | ✅ **Yes** | **₹15,497** | 243 |
| **BFS** | Fewest months (queue) | ❌ No | ₹19,897 | 2,599 |
| **DFS** | First path found (stack) | ❌ No | ₹24,581 | 13 |
| **Greedy** | Lowest h (estimate) | ❌ No | ₹24,581 | 13 |

> **A* wins:** Always finds the optimal plan *and* explores 8× fewer states than UCS by using a smart heuristic that never overestimates.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation
```bash
# Clone the repo
git clone https://github.com/cs25b1074-stack/aiwp_project.git
cd aiwp_project

# Switch to the complete branch
git checkout tanish

# Install dependencies
pip install -r requirements.txt
```

### Run the Interactive Web App
```bash
streamlit run streamlit_app.py
```
Open **http://localhost:8501** (or the port shown) in your browser.

### Run Individual Algorithms
```bash
# Test with standard inputs (Test 1)
echo -e "20000\n5000\n100000\n14\n60000\n36" | python ucs_debt.py
echo -e "20000\n5000\n100000\n14\n60000\n36" | python astar_debt.py

# Compare all 5 algorithms at once
echo -e "20000\n5000\n100000\n14\n60000\n36" | python compare_all.py
```

---

## 📊 Features

### 🎮 Interactive Web UI (`streamlit_app.py`)
- **Sidebar inputs** with 3 preset test cases + custom values
- **Algorithm comparison table** with optimal highlighting
- **Key metrics cards** showing best algorithm, min interest, months, states
- **Month-by-month repayment plan** with formatted balances
- **Dynamic explanation** — shows actual states explored for YOUR inputs
- **Smart insights** — tells you exactly which debt to pay first
- **Clean, professional UI** — works in light & dark mode

### 📈 Three Standard Test Cases (from project guidelines)

| Test | Income | Savings | Loan | Loan Rate | Card | Card Rate | Optimal Strategy |
|------|--------|---------|------|-----------|------|-----------|------------------|
| **Test 1** | ₹20,000 | ₹5,000 | ₹1,00,000 | 14% | ₹60,000 | 36% | **Card First** |
| **Test 2** | ₹15,000 | ₹3,000 | ₹50,000 | 12% | ₹40,000 | 42% | **Card First** |
| **Test 3** | ₹20,000 | ₹5,000 | ₹1,00,000 | 30% | ₹60,000 | 18% | **Loan First** |

---

## 📁 Project Structure

```
aiwp_project/
├── 📄 bfs_debt.py         # BFS implementation (Ritu)
├── 📄 dfs_debt.py         # DFS implementation (Dharmik)
├── 📄 ucs_debt.py         # UCS implementation (Tanish) ← Your part
├── 📄 greedy_debt.py      # Greedy Best-First (Mithunn)
├── 📄 astar_debt.py       # A* Search (Mithunn)
├── 📄 compare_all.py      # Runs all 5 + comparison table
├── 📄 streamlit_app.py    # Interactive web UI
├── 📄 requirements.txt    # Python dependencies
└── 📄 README.md           # This file
```

---

## 🎓 Viva-Ready Explanations

### UCS (Your Algorithm)
| Question | Answer |
|----------|--------|
| **What does UCS minimize?** | g(n): Total interest paid so far |
| **Why is UCS optimal?** | Expands cheapest partial plan first; interest never negative |
| **What is `g_cost` for?** | Stores cheapest g found for each state; allows updating |
| **Why test goal on POP not PUSH?** | Cheaper route to goal might still be in OPEN |
| **How is UCS different from BFS?** | BFS treats each month as cost 1; UCS uses real interest |

### A* (The Winner)
- **Heuristic:** All remaining debt at lowest rate, paid at max possible speed
- **Never overestimates** → Guaranteed optimal
- **f = g + h** combines actual cost + smart estimate
- **8× more efficient** than UCS (29 vs 243 states in Test 1)

---

## 💡 Key Insight for YOUR Debt

> **Always pay the HIGHER interest rate debt first!**

The math is unambiguous:
- If **Card rate > Loan rate** → Pay **Card first** every month
- If **Loan rate > Card rate** → Pay **Loan first** every month
- If **Equal** → Order doesn't matter

This is exactly what A* and UCS discover automatically through search.

---

## 🤝 Team

| Member | Algorithm | File |
|--------|-----------|------|
| **Ritu** | BFS | `bfs_debt.py` |
| **Dharmik** | DFS | `dfs_debt.py` |
| **Tanish** | **UCS** | `ucs_debt.py` |
| **Mithunn** | Greedy + A* | `greedy_debt.py`, `astar_debt.py` |
| **Mithunn** | Compare + UI | `compare_all.py`, `streamlit_app.py` |

---

## 📜 License

Educational project for **AI with Python** course.

---

## 🎉 Try It Now!

```bash
git checkout tanish
pip install -r requirements.txt
streamlit run streamlit_app.py
```

**Then open http://localhost:8501 and enter your own debts to see the optimal plan!** 💰