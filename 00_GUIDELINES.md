# Debt Repayment Planner — Project Guidelines

> **Rule 0: if anything in a work-split file disagrees with this file, follow THIS file.**
> This file is the source of truth. The work-split files are only step-by-step plans.

**Team:** Mithunn · Ritu · Dharmik · Tanish  **Time per person:** at most 3 hours
**Course:** AI with Python  **Aim:** build it ourselves, so every member can explain their own code in the viva.

---

## Guideline 1 — What the project is

### The real-world problem
A person has **two debts**: a **loan** and a **credit card**, each with its own interest rate.
Every month they earn an income, pay the interest, keep some savings, and use **what is left** to repay the debts.

**The question:** each month, which debt should the leftover money repay first — the loan or the card —
so that the **total interest paid until both debts are cleared is as small as possible**?

### What happens every month (in this order)
Example (Test 1): income ₹20,000 · savings ₹5,000 · loan ₹1,00,000 at 14% · card ₹60,000 at 36%.

| Step | What happens | Month 1 amount |
| --- | --- | --- |
| 1 | Income arrives | ₹20,000 |
| 2 | Pay this month's loan interest (100000 × 14 ÷ 1200) | − ₹1,167 |
| 3 | Pay this month's card interest (60000 × 36 ÷ 1200) | − ₹1,800 |
| 4 | Put money into savings | − ₹5,000 |
| 5 | **Left over for repaying** (`extra`) | **₹12,033** |
| 6 | **DECISION:** repay the loan first, or the card first (leftover goes to the other) | |

- If the **card** is repaid first → loan ₹1,00,000, card ₹47,967
- If the **loan** is repaid first → loan ₹87,967, card ₹60,000

Next month the interest is charged on the **new** balances, so this choice changes the interest of every month after it.
Repeat until both debts are ₹0.

### Why the choice matters (real numbers from our program, Test 1)
| Plan | Total interest paid | Months |
| --- | --- | --- |
| Best plan (found by UCS and A*): card first, then loan | **₹15,497** | 12 |
| Plan found by DFS: loan first, then card | ₹24,581 | 13 |

Same person, same money, **₹9,084 difference** — just from the order of repaying.

---

## Guideline 2 — The search problem and the shared starter code

### The search formulation (same idea as the 8-puzzle in our lab)
| Part | 8-puzzle (lab) | Our project |
| --- | --- | --- |
| State | the board tuple | `(loan, card)` e.g. `(100000, 60000)` |
| Start | the scrambled board | `(loan, card)` typed by the user |
| Goal | `(1,2,3,4,5,6,7,8,0)` | `(0, 0)` — no debt left |
| Actions | move the blank | repay the loan first, or the card first |
| Successors | `neighbours(state)` | `neighbours(state)` → a list of 1 or 2 child states |
| Step cost | 1 per move | **the interest paid that month** = `interest(state)` |
| What we minimise | number of moves | **total interest** = `path_cost(path)` |
| Heuristic | `manhattan()` | `heuristic(state)` (only Greedy and A* use it) |

### The 5 algorithms
| Algorithm | Picks next | Finds the cheapest plan? | Owner |
| --- | --- | --- | --- |
| BFS | the oldest state (queue) | no — fewest months only | Ritu |
| DFS | the newest state (stack) | no | Dharmik |
| UCS | lowest interest so far, g | **yes** | Tanish |
| Greedy Best-First | lowest h (estimate of interest still to come) | no | Mithunn |
| A* | lowest f = g + h | **yes**, and with less work than UCS | Mithunn |

### The shared starter code (`starter.py`) — everyone uses exactly this
Copy `starter.py`, rename it to your file name, and write **only your algorithm function** in the marked place.

```python
def interest(state):
    loan, card = state
    return round(loan * loan_rate / 1200) + round(card * card_rate / 1200)


def neighbours(state):
    result = []
    loan, card = state
    extra = income - interest(state) - savings   # left after interest and savings

    # choice 1: repay the LOAN first, anything left over goes to the card
    pay_loan = min(extra, loan)
    pay_card = min(extra - pay_loan, card)
    result.append((loan - pay_loan, card - pay_card))

    # choice 2: repay the CARD first, anything left over goes to the loan
    pay_card = min(extra, card)
    pay_loan = min(extra - pay_card, loan)
    child = (loan - pay_loan, card - pay_card)
    if child not in result:
        result.append(child)
    return result


def show(state):
    print("Loan:", state[0], "  Card:", state[1])


def path_cost(path):
    total = 0
    for state in path[:-1]:
        total = total + interest(state)          # interest paid in every month
    return total


def heuristic(state):
    total = state[0] + state[1]
    low = min(loan_rate, card_rate) / 1200      # lowest monthly rate
    h = 0
    while total > 0:
        h = h + total * low - 1                 # -1 = safety margin for rounding
        total = total - payment                 # we can't pay faster than this
    return max(0, h)


graph = {}                                  # adjacency list


# ===== WRITE YOUR ALGORITHM FUNCTION HERE =====


income = int(input("Enter monthly income (after expenses): "))
savings = int(input("Enter monthly savings: "))
loan = int(input("Enter loan amount: "))
loan_rate = float(input("Enter loan interest rate (% per year): "))
card = int(input("Enter credit card amount: "))
card_rate = float(input("Enter credit card interest rate (% per year): "))

payment = income - savings                  # most that can ever go to the debts in a month
start = (loan, card)
goal = (0, 0)

if income - interest(start) - savings <= 0:
    print("After paying the interest and savings, nothing is left to repay the debt")
else:
    path, explored = ALGORITHM(start)          # <- change ALGORITHM to your function name
    print()
    print("Solution found using ALGORITHM NAME")   # <- change the name
    month = 0
    for state in path:
        print("Month", month, end="   ")
        show(state)
        month = month + 1
    print("Months to clear the debt:", len(path) - 1)
    print("Total interest paid     :", path_cost(path))
    print("States explored         :", explored)
```

### What each starter function does
| Function | What it does | Example (Test 1, start state) |
| --- | --- | --- |
| `interest(state)` | interest charged this month on both debts | `interest((100000, 60000))` = 1167 + 1800 = **2967** |
| `neighbours(state)` | the 1 or 2 states possible next month | `[(87967, 60000), (100000, 47967)]` → [loan first, card first] |
| `show(state)` | prints one state | `Loan: 100000   Card: 60000` |
| `path_cost(path)` | total interest of a whole plan (adds `interest` of every month) | 15497 for the A* plan |
| `heuristic(state)` | a **lower bound** on the interest still to come (only Greedy and A*) | never more than the true remaining interest |
| `graph` | the adjacency list, filled as the search runs: `graph[state] = neighbours(state)` | |

**Why `neighbours` can return only 1 child:** once one debt is ₹0, "loan first" and "card first" give the same result, so the duplicate is removed.

**Why the heuristic never overestimates (for the viva):**
it charges **all** remaining debt at the **lowest** of the two rates, and assumes the debt shrinks by the **whole** `payment` every month (in reality it shrinks by less, because interest is paid too).
Both assumptions make the estimate smaller than the truth, so A* is guaranteed to find the cheapest plan. The `- 1` is a small safety margin for rounding to whole rupees.

---

## Guideline 3 — Team rules

1. **File names:** `bfs_debt.py`, `dfs_debt.py`, `ucs_debt.py`, `greedy_debt.py`, `astar_debt.py`.
2. **Do not change the starter functions** (`interest`, `neighbours`, `show`, `path_cost`, `heuristic`). If you think one is wrong, tell the team — don't edit your own copy, or our results won't match.
3. **Function shape:** your function takes `start` and returns **two things**: `return path, len(CLOSED)` (or `return None, len(CLOSED)` if no path).
   `path` is the list of states from start to goal, in order.
4. **Use the lab pattern:** `OPEN`, `CLOSED`, `parent`, `graph[state] = neighbours(state)`, `for child in graph.get(state, []):`.
5. **Write your function yourself.** Each work-split file has a skeleton with blanks and an answer key. Use the answer key only to check, after you have tried.
6. **Run all 3 standard tests** below and compare with Guideline 4. Your numbers must match exactly.
7. **Input:** type each value and press Enter (6 values). **Output:** keep the starter's output lines unchanged (only change the algorithm name).

### The 3 standard tests
| Test | Income | Savings | Loan | Loan rate | Card | Card rate | Note |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Test 1** | 20000 | 5000 | 100000 | 14 | 60000 | 36 | card is more expensive |
| **Test 2** | 15000 | 3000 | 50000 | 12 | 40000 | 42 | card is much more expensive |
| **Test 3** | 20000 | 5000 | 100000 | 30 | 60000 | 18 | loan is more expensive |

---

## Guideline 4 — Expected outcome

### Deliverables
| # | Deliverable | Owner |
| --- | --- | --- |
| 1 | `bfs_debt.py` | Ritu |
| 2 | `dfs_debt.py` | Dharmik |
| 3 | `ucs_debt.py` | Tanish |
| 4 | `greedy_debt.py`, `astar_debt.py` | Mithunn |
| 5 | `compare_all.py` (all 5 algorithms, one comparison table) + live demo | Mithunn |
| 6 | Results table for the 3 tests | Tanish |
| 7 | Report | Ritu (everyone sends their part) |
| 8 | Slides | Dharmik (everyone sends their part) |

### Expected results — your output must match these numbers
| Algorithm | Test 1: interest / months / states | Test 2: interest / months / states | Test 3: interest / months / states |
| --- | --- | --- | --- |
| BFS | 19,897 / 12 / 2,599 | 11,578 / 9 / 335 | 20,911 / 13 / 3,511 |
| DFS | 24,581 / 13 / 13 | 11,578 / 9 / 9 | 20,911 / 13 / 13 |
| UCS | **15,497** / 12 / 243 | **6,636** / 9 / 36 | **20,911** / 13 / 529 |
| Greedy Best-First | 24,581 / 13 / 13 | 11,578 / 9 / 9 | 20,911 / 13 / 13 |
| A* | **15,497** / 12 / **29** | **6,636** / 9 / **17** | **20,911** / 13 / **87** |

**A\* plan for Test 1 (month by month):**
```
Month 0   Loan: 100000   Card: 60000
Month 1   Loan: 100000   Card: 47967
Month 2   Loan: 100000   Card: 35573
Month 3   Loan: 100000   Card: 22807
Month 4   Loan: 100000   Card: 9658
Month 5   Loan: 96115   Card: 0
Month 6   Loan: 82236   Card: 0
...
Month 12   Loan: 0   Card: 0
Months to clear the debt: 12
Total interest paid     : 15497
States explored         : 29
```

### The conclusion we must be able to defend
> **A\* is the best algorithm.** It always finds the cheapest plan (same as UCS), but explores far fewer states
> (29 vs 243 in Test 1), because its heuristic tells it early which plans are going to be expensive.
> BFS finds the fewest months, not the least interest, and explores the most states.
> DFS and Greedy are fast but just follow the first choice they meet, so they often pay much more —
> they only "get lucky" when the loan happens to be the more expensive debt (Test 3).

### Done means
- [ ] Every algorithm file runs and matches the expected table for all 3 tests
- [ ] `compare_all.py` prints all 5 rows for any input
- [ ] Report and slides contain the problem, formulation, 5 algorithms, results table and the conclusion
- [ ] Every member can answer the viva questions in their own work-split file

---

## Team timeline (each person ≤ 3 hours)
| Time | Everyone |
| --- | --- |
| 0:00 – 0:30 | Read this file. Run `starter.py`'s helpers in your head on Test 1 (Guideline 1 table). |
| 0:30 – 2:00 | Build and test your algorithm (your work-split file, steps 1–5). |
| 2:00 – 2:30 | Send your write-up and slide text to Ritu and Dharmik; send your test results to Tanish. |
| 2:30 – 3:00 | Do your extra role (report / slides / results table / comparison + demo), then one team rehearsal. |
