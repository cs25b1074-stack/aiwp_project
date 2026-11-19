# Tanish — Uniform Cost Search (UCS)

> Follow `00_GUIDELINES.md` first. If this file and the guidelines disagree, **the guidelines win**.

**Your job:** build `ucs_debt.py`, test it, explain its result, and build the **results table** for the 3 tests.
**Time limit:** 3 hours.

## Time plan
| Time | Task |
| --- | --- |
| 0:00 – 0:30 | Read the guidelines (Step 1) |
| 0:30 – 2:00 | Steps 2–4: understand, write and test UCS (a little longer than BFS/DFS) |
| 2:00 – 2:20 | Step 5: explain your result |
| 2:20 – 3:00 | Step 7: collect everyone's results into one table |

---

## Step 1 — Set up (10 min)
1. Read `00_GUIDELINES.md` (Guidelines 1–4).
2. Copy `starter.py` and rename the copy to `ucs_debt.py`.
3. At the bottom, replace `ALGORITHM` with your function name and `ALGORITHM NAME` with the algorithm's name.

## Step 2 — Understand the idea (15 min)
UCS always expands the state with the **lowest total interest paid so far**, called **g**.
Because it always takes the cheapest partial plan first, the first time it reaches `(0, 0)` is guaranteed to be the **cheapest** plan.

- `g` of a child = `g` of the parent + `interest(parent)` (the interest paid in that month).
- `g_cost` remembers the cheapest `g` found for each state. If a cheaper way to reach a state is found later, we update it.
- OPEN is a list of `(g, state)`. We pick the smallest by looping over it — the same "find the lowest" loop as in our lab A* without heap.

## Step 3 — Write your function (45–60 min)
Write this in the place marked `# ===== WRITE YOUR ALGORITHM FUNCTION HERE =====`. Fill every `___`.

```python
def ucs(start):
    OPEN = [(0, start)]                     # list of (g, state)
    CLOSED = set()
    parent = {start: None}
    g_cost = {start: ___}                   # 1. interest paid to reach the start
    while OPEN:
        best = 0                            # find the item with the LOWEST g
        for i in range(len(OPEN)):
            if OPEN[i] < OPEN[___]:         # 2. compare with the best so far
                best = i
        g, state = OPEN.pop(___)            # 3. take out the cheapest item
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
            new_g = g + ___                 # 4. interest paid this month
            if child not in g_cost or new_g < ___:   # 5. new, or a cheaper route
                g_cost[child] = new_g
                parent[child] = state
                CLOSED.discard(child)       # allow it to be explored again
                OPEN.append((___, child))   # 6. push with its new g
    return None, len(CLOSED)
```

**Hints for the blanks:**
1. a number  2. the variable holding the position of the best so far  3. same as 2
4. the starter function for this month's interest, called on `state`  5. the old best g for this child  6. the child's new g

## Step 4 — Test (20 min)
Run `python3 ucs_debt.py` three times, once for each standard test in Guideline 3, and fill in this table:

| Test | Interest paid | Months | States explored | Matches Guideline 4? |
| --- | --- | --- | --- | --- |
| Test 1 | | | | |
| Test 2 | | | | |
| Test 3 | | | | |

If a number is different: first check you did not change a starter function, then compare your code with the answer key line by line.

## Step 5 — Explain your result (15 min)
Answer these in 2–3 sentences each (they go into the report):
1. UCS found **₹15,497** in Test 1 — the cheapest possible. Why is UCS guaranteed to find the cheapest plan?
2. UCS explored **243** states, A* only **29**, for the same answer. What does A* know that UCS doesn't?
   *(Hint: UCS only knows the interest already paid; A* also estimates the interest still to come.)*

## Step 6 — Send your part to the team (15 min)
Send these to Ritu (report) and Dharmik (slides), and your test table to Tanish:

- **Report paragraph (4–6 sentences):** what UCS does, why it is optimal, its results, and the answers from Step 5.
- **Slide text (3 bullets):** "UCS: always expands the lowest interest so far (g)" · "Always finds the cheapest plan" · "Test 1: ₹15,497, but 243 states".

## Step 7 — Your extra role: the results table (40 min)
1. Collect the Step 4 tables from Ritu, Dharmik and Mithunn.
2. Combine them into one table like Guideline 4's (5 algorithms × 3 tests: interest, months, states).
3. Check every number against Guideline 4. If someone's number differs, tell them which test.
4. Add one sentence under the table for each test: who found the cheapest plan and who explored the fewest states.
5. Send the table to Ritu (report) and Dharmik (slides).

## Viva questions you must be able to answer
1. **What does UCS minimise?** g(n): the total interest paid so far.
2. **Why is UCS optimal?** It always expands the cheapest partial plan, and interest is never negative, so when the goal is popped no cheaper route can exist.
3. **What is `g_cost` for?** It stores the cheapest g found for each state, so a cheaper route found later replaces a worse one.
4. **Why test for the goal when a state is POPPED, not when it is added?** A cheaper route to the goal might still be waiting in OPEN.
5. **How is UCS different from BFS?** BFS treats every month as cost 1 (fewest months); UCS uses the real interest (least money).

---

<details><summary>Answer key: UCS (open only after trying)</summary>

```python
def ucs(start):
    OPEN = [(0, start)]                     # list of (g, state)
    CLOSED = set()
    parent = {start: None}
    g_cost = {start: 0}                     # cheapest interest found so far
    while OPEN:
        best = 0                            # find the item with the LOWEST g
        for i in range(len(OPEN)):
            if OPEN[i] < OPEN[best]:
                best = i
        g, state = OPEN.pop(best)
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
                OPEN.append((new_g, child))
    return None, len(CLOSED)
```
</details>
