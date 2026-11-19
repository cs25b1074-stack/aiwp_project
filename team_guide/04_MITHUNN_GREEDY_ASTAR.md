# Mithunn — Greedy Best-First Search + A* Search

> Follow `00_GUIDELINES.md` first. If this file and the guidelines disagree, **the guidelines win**.

**Your job:** build `greedy_debt.py` and `astar_debt.py`, test it, explain its result, and build **`compare_all.py`** and run the **live demo**.
**Time limit:** 3 hours.

## Time plan
| Time | Task |
| --- | --- |
| 0:00 – 0:20 | Read the guidelines, especially the heuristic (Guideline 2) |
| 0:20 – 1:00 | Greedy Best-First: write and test |
| 1:00 – 1:50 | A*: write and test |
| 1:50 – 2:10 | Step 5: explain both results |
| 2:10 – 3:00 | Step 7: `compare_all.py`, the winner section of the report, and the demo |

---

## Step 1 — Set up (10 min)
1. Read `00_GUIDELINES.md` (Guidelines 1–4).
2. Copy `starter.py` and rename the copy to `greedy_debt.py` and `astar_debt.py`.
3. At the bottom, replace `ALGORITHM` with your function name and `ALGORITHM NAME` with the algorithm's name.

## Step 2 — Understand the idea (15 min)
Both algorithms use `heuristic(state)` = **h**, a lower bound on the interest still to come.

- **Greedy Best-First** expands the state with the lowest **h only**. It ignores the interest already paid.
  OPEN is a list of `(h, state)`.
- **A\*** expands the state with the lowest **f = g + h**: interest already paid **plus** the estimate of interest still to come.
  OPEN is a list of `(f, g, state)`, with `g_cost` exactly like UCS.

**Key insight for Greedy:** our h only looks at the **total** debt. After paying, both choices (loan first / card first) leave the **same total**, so they get the **same h** and Greedy cannot tell them apart. It picks the first one (loan first), just like DFS.

**Key insight for A\*:** h never overestimates, so A\* still finds the cheapest plan — but it adds the future interest early, so expensive plans look expensive straight away and are never expanded. Same answer as UCS, far fewer states.

## Step 3 — Write your function (45–60 min)
Write this in the place marked `# ===== WRITE YOUR ALGORITHM FUNCTION HERE =====`. Fill every `___`.

```python
def greedy(start):
    OPEN = [(heuristic(start), start)]      # list of (h, state)
    CLOSED = set()
    parent = {start: None}
    while OPEN:
        best = 0                            # find the item with the LOWEST h
        for i in range(len(OPEN)):
            if OPEN[i] < OPEN[best]:
                best = i
        h, state = OPEN.pop(best)
        if state in CLOSED:
            continue
        if state == goal:
            path = []
            while state is not None:
                path.append(state)
                state = parent[state]
            return path[::-1], len(CLOSED)
        CLOSED.add(state)
        graph[state] = neighbours(state)
        for child in graph.get(state, []):
            if child not in parent:
                parent[child] = state
                OPEN.append((___, child))   # 1. push with the child's h
    return None, len(CLOSED)


def astar(start):
    OPEN = [(heuristic(start), 0, start)]   # list of (f, g, state)
    CLOSED = set()
    parent = {start: None}
    g_cost = {start: 0}
    while OPEN:
        best = 0                            # find the item with the LOWEST f
        for i in range(len(OPEN)):
            if OPEN[i] < OPEN[best]:
                best = i
        f, g, state = OPEN.pop(best)
        if state in CLOSED:                 # an old, worse copy -> skip
            continue
        if state == goal:
            path = []
            while state is not None:
                path.append(state)
                state = parent[state]
            return path[::-1], len(CLOSED)
        CLOSED.add(state)
        graph[state] = neighbours(state)
        for child in graph.get(state, []):
            new_g = g + ___                 # 2. interest paid this month
            if child not in g_cost or new_g < g_cost[child]:
                g_cost[child] = new_g
                parent[child] = state
                CLOSED.discard(child)
                OPEN.append((___, new_g, child))   # 3. f = g + h of the child
    return None, len(CLOSED)
```

**Hints for the blanks:**
1. the starter function, called on `child`  2. `interest(...)` of the state being expanded  3. `new_g` plus the child's heuristic
Write each in its own file (`greedy_debt.py`, `astar_debt.py`), each starting from `starter.py`.

## Step 4 — Test (20 min)
Run `python3 greedy_debt.py` and `astar_debt.py` three times, once for each standard test in Guideline 3, and fill in this table:

| Test | Interest paid | Months | States explored | Matches Guideline 4? |
| --- | --- | --- | --- | --- |
| Test 1 | | | | |
| Test 2 | | | | |
| Test 3 | | | | |

If a number is different: first check you did not change a starter function, then compare your code with the answer key line by line.

## Step 5 — Explain your result (15 min)
Answer these in 2–3 sentences each (they go into the report):
1. Greedy paid **₹24,581** in Test 1, the same as DFS. Why? *(Hint: the key insight above.)*
2. A\* paid **₹15,497** (same as UCS) but explored **29** states instead of **243**. Explain why h makes this possible.
3. Why does h never overestimate? (Use Guideline 2.)

## Step 6 — Send your part to the team (15 min)
Send these to Ritu (report) and Dharmik (slides), and your test table to Tanish:

- **Report sections (you write them):** section 3 "The heuristic" and section 6 "Comparison and winner" (Guideline 4 conclusion), plus one paragraph each for Greedy and A\*.
- **Slide text:** slide 8 (Greedy, A\*, heuristic) and slide 10 (the winner + demo).

## Step 7 — Your extra role: `compare_all.py` and the live demo (50 min)
1. Copy `starter.py` to `compare_all.py`.
2. Paste in all 5 functions: your two, plus `bfs`, `dfs`, `ucs` from Ritu, Dharmik and Tanish.
3. Replace the output part at the bottom with:
```python
if income - interest(start) - savings <= 0:
    print("After paying the interest and savings, nothing is left to repay the debt")
else:
    print()
    print("Algorithm                  Interest paid   Months   States explored")
    for name, algorithm in [("BFS", bfs), ("DFS", dfs), ("UCS", ucs),
                            ("Greedy Best-First", greedy), ("A*", astar)]:
        path, explored = algorithm(start)
        print(name.ljust(26), str(path_cost(path)).ljust(15), str(len(path) - 1).ljust(8), explored)
```
4. Run Test 1. All 5 rows must match Guideline 4.
5. **Demo plan (2 minutes):** run `compare_all.py` with Test 1 → point at A\* (cheapest, fewest states among the optimal ones) → run `astar_debt.py` with Test 1 to show the month-by-month plan → run Test 3 to show that when the loan is more expensive, every algorithm agrees.

## Viva questions you must be able to answer
1. **What is the heuristic and is it admissible?** h = all remaining debt charged at the lowest rate, assuming it falls by the whole payment each month. Both assumptions under-estimate, so h ≤ true remaining interest: admissible.
2. **Why is A\* optimal?** With an admissible h, A\* never skips a cheaper plan, so the first time it pops the goal it has the cheapest plan.
3. **Why is A\* faster than UCS?** UCS only sees interest already paid; A\* also adds a lower bound on the future interest, so plans heading for expensive futures are recognised early and never expanded.
4. **Why does Greedy fail?** It uses only h. Both choices leave the same total debt, so h ties and Greedy just takes the first choice; it also ignores interest already paid.
5. **Why do we update `g_cost` and `CLOSED.discard(child)`?** If a cheaper route to an already-seen state is found, we record it and allow the state to be explored again.

---

<details><summary>Answer key: Greedy Best-First (open only after trying)</summary>

```python
def greedy(start):
    OPEN = [(heuristic(start), start)]      # list of (h, state)
    CLOSED = set()
    parent = {start: None}
    while OPEN:
        best = 0                            # find the item with the LOWEST h
        for i in range(len(OPEN)):
            if OPEN[i] < OPEN[best]:
                best = i
        h, state = OPEN.pop(best)
        if state in CLOSED:
            continue
        if state == goal:
            path = []
            while state is not None:
                path.append(state)
                state = parent[state]
            return path[::-1], len(CLOSED)
        CLOSED.add(state)
        graph[state] = neighbours(state)
        for child in graph.get(state, []):
            if child not in parent:
                parent[child] = state
                OPEN.append((heuristic(child), child))
    return None, len(CLOSED)
```
</details>

<details><summary>Answer key: A* (open only after trying)</summary>

```python
def astar(start):
    OPEN = [(heuristic(start), 0, start)]   # list of (f, g, state)
    CLOSED = set()
    parent = {start: None}
    g_cost = {start: 0}
    while OPEN:
        best = 0                            # find the item with the LOWEST f
        for i in range(len(OPEN)):
            if OPEN[i] < OPEN[best]:
                best = i
        f, g, state = OPEN.pop(best)
        if state in CLOSED:                 # an old, worse copy -> skip
            continue
        if state == goal:
            path = []
            while state is not None:
                path.append(state)
                state = parent[state]
            return path[::-1], len(CLOSED)
        CLOSED.add(state)
        graph[state] = neighbours(state)
        for child in graph.get(state, []):
            new_g = g + interest(state)     # interest paid this month
            if child not in g_cost or new_g < g_cost[child]:
                g_cost[child] = new_g
                parent[child] = state
                CLOSED.discard(child)
                OPEN.append((new_g + heuristic(child), new_g, child))
    return None, len(CLOSED)
```
</details>
