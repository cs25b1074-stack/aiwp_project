# Ritu — Breadth-First Search (BFS)

> Follow `00_GUIDELINES.md` first. If this file and the guidelines disagree, **the guidelines win**.

**Your job:** build `bfs_debt.py`, test it, explain its result, and put together the **report**.
**Time limit:** 3 hours.

## Time plan
| Time | Task |
| --- | --- |
| 0:00 – 0:30 | Read the guidelines (Step 1) |
| 0:30 – 1:45 | Steps 2–4: understand, write and test BFS |
| 1:45 – 2:00 | Step 5: explain your result |
| 2:00 – 3:00 | Step 7: assemble the report from everyone's parts |

---

## Step 1 — Set up (10 min)
1. Read `00_GUIDELINES.md` (Guidelines 1–4).
2. Copy `starter.py` and rename the copy to `bfs_debt.py`.
3. At the bottom, replace `ALGORITHM` with your function name and `ALGORITHM NAME` with the algorithm's name.

## Step 2 — Understand the idea (15 min)
BFS explores **level by level**: all plans of 1 month, then all plans of 2 months, and so on.
It uses a **queue** (`OPEN.pop(0)` takes the oldest state). The first time it reaches `(0, 0)` is with the **fewest months**.

But BFS treats every month as cost 1. It does **not** look at interest, so among all plans with the fewest months it returns whichever it finds first — not the cheapest.

It is exactly your lab BFS for the 8-puzzle; only `neighbours` and `goal` are different.

## Step 3 — Write your function (45–60 min)
Write this in the place marked `# ===== WRITE YOUR ALGORITHM FUNCTION HERE =====`. Fill every `___`.

```python
def bfs(start):
    OPEN = [___]                            # 1. the queue starts with the start state
    CLOSED = set()
    parent = {start: ___}                   # 2. the start has no parent
    while OPEN:
        state = OPEN.pop(___)               # 3. take from the FRONT of the queue
        if state == goal:
            path = []
            while state is not None:
                path.append(state)
                state = ___                 # 4. move to this state's parent
            return path[::-1], len(CLOSED)
        CLOSED.add(state)
        graph[state] = ___                  # 5. build the adjacency list
        for child in graph.get(state, []):
            if child not in ___:            # 6. never seen before (not in OPEN or CLOSED)
                parent[child] = ___         # 7. remember where the child came from
                OPEN.append(child)          # add to the BACK
    return None, len(CLOSED)
```

**Hints for the blanks:**
1. `start`  2. `None`  3. which index is the front of a list?  4. look it up in the `parent` dictionary
5. the starter function that gives the next states  6. which dictionary holds every state ever added?  7. the state we are expanding

## Step 4 — Test (20 min)
Run `python3 bfs_debt.py` three times, once for each standard test in Guideline 3, and fill in this table:

| Test | Interest paid | Months | States explored | Matches Guideline 4? |
| --- | --- | --- | --- | --- |
| Test 1 | | | | |
| Test 2 | | | | |
| Test 3 | | | | |

If a number is different: first check you did not change a starter function, then compare your code with the answer key line by line.

## Step 5 — Explain your result (15 min)
Answer these in 2–3 sentences each (they go into the report):
1. In Test 1, BFS took 12 months — the same as A*. So why did it pay **₹19,897** instead of **₹15,497**?
   *(Hint: BFS checks months, not money. Look at which child `neighbours` lists first.)*
2. Why did BFS explore **2,599** states in Test 1 when A* explored only 29?
   *(Hint: BFS must look at every plan of 11 months before it can look at any plan of 12 months.)*

## Step 6 — Send your part to the team (15 min)
Send these to Ritu (report) and Dharmik (slides), and your test table to Tanish:

- **Report paragraph (4–6 sentences):** what BFS does, its result in the 3 tests, and the two answers from Step 5.
- **Slide text (3 bullets):** "BFS: level by level, queue" · "Finds fewest months, not least interest" · "Test 1: ₹19,897, 2,599 states".

## Step 7 — Your extra role: the report (1 hour)
Make the report (Google Docs or Word). Use this structure and ask the owners for their parts:

| Section | Content | Who writes it |
| --- | --- | --- |
| 1. Introduction | the real-world problem (Guideline 1) | Ritu |
| 2. Problem formulation | state, actions, cost, goal table (Guideline 2) | Ritu |
| 3. The heuristic | what it is and why it never overestimates (Guideline 2) | Mithunn |
| 4. Algorithms | one paragraph each: BFS, DFS, UCS, Greedy, A* | each owner |
| 5. Results | the table for the 3 tests | Tanish |
| 6. Comparison and winner | why A* is the best (Guideline 4 conclusion) | Mithunn |
| 7. Conclusion and limitations | 2 debts only, fixed income and savings, interest rounded to whole rupees | Ritu |
| 8. Team contributions | who built what | Ritu |

Check that every number in the report matches Guideline 4.

## Viva questions you must be able to answer
1. **What data structure does BFS use and why?** A FIFO queue, so the oldest state is expanded first, which means level by level.
2. **Is BFS optimal here?** Only for the number of months. Not for interest, because it treats every month as cost 1.
3. **Why do we check `child not in parent` and not just `CLOSED`?** `parent` contains every state ever added to OPEN or CLOSED, so a state is never added twice.
4. **Time and space complexity?** O(b^d): b = 2 choices, d = months. BFS stores a whole level, so memory grows fast (2,599 states in Test 1).
5. **What is `graph[state] = neighbours(state)` doing?** Building the adjacency list as we go, because the full graph is never given to us.

---

<details><summary>Answer key: BFS (open only after trying)</summary>

```python
def bfs(start):
    OPEN = [start]                          # queue
    CLOSED = set()
    parent = {start: None}
    while OPEN:
        state = OPEN.pop(0)                 # take from the FRONT
        if state == goal:
            path = []
            while state is not None:
                path.append(state)
                state = parent[state]
            return path[::-1], len(CLOSED)
        CLOSED.add(state)
        graph[state] = neighbours(state)
        for child in graph.get(state, []):
            if child not in parent:         # not in OPEN and not in CLOSED
                parent[child] = state
                OPEN.append(child)          # add to the BACK
    return None, len(CLOSED)
```
</details>
