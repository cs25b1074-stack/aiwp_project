# Dharmik — Depth-First Search (DFS)

> Follow `00_GUIDELINES.md` first. If this file and the guidelines disagree, **the guidelines win**.

**Your job:** build `dfs_debt.py`, test it, explain its result, and put together the **slides**.
**Time limit:** 3 hours.

## Time plan
| Time | Task |
| --- | --- |
| 0:00 – 0:30 | Read the guidelines (Step 1) |
| 0:30 – 1:45 | Steps 2–4: understand, write and test DFS |
| 1:45 – 2:00 | Step 5: explain your result |
| 2:00 – 3:00 | Step 7: make the slides from everyone's parts |

---

## Step 1 — Set up (10 min)
1. Read `00_GUIDELINES.md` (Guidelines 1–4).
2. Copy `starter.py` and rename the copy to `dfs_debt.py`.
3. At the bottom, replace `ALGORITHM` with your function name and `ALGORITHM NAME` with the algorithm's name.

## Step 2 — Understand the idea (15 min)
DFS goes **as deep as possible down the first choice** before trying anything else.
It uses a **stack** (`OPEN.pop()` takes the newest state).

In our problem the first choice in `neighbours` is "repay the **loan** first". DFS keeps taking it month after month until the debt is cleared, and returns that first plan it finds. It never compares plans, so it is fast but often expensive.

It is exactly your lab DFS for the 8-puzzle; only `neighbours` and `goal` are different.

## Step 3 — Write your function (45–60 min)
Write this in the place marked `# ===== WRITE YOUR ALGORITHM FUNCTION HERE =====`. Fill every `___`.

```python
def dfs(start):
    OPEN = [start]                          # the stack
    CLOSED = set()
    parent = {start: None}
    while OPEN:
        state = OPEN.___()                  # 1. take from the END (newest first)
        if state in CLOSED:                 # 2. already explored -> skip it
            ___
        if state == goal:
            path = []
            while state is not None:
                path.append(state)
                state = parent[state]
            return path[::-1], len(CLOSED)
        CLOSED.add(state)
        graph[state] = neighbours(state)
        for child in ___(graph.get(state, [])):   # 3. so the FIRST choice is explored first
            if child not in ___:            # 4. not explored yet
                parent[child] = state
                OPEN.append(child)          # add to the END
    return None, len(CLOSED)
```

**Hints for the blanks:**
1. the list method that removes the last item  2. the keyword that jumps to the next loop round
3. the built-in that reverses a list (a stack pops the last item pushed, so push in reverse)  4. the set of explored states

## Step 4 — Test (20 min)
Run `python3 dfs_debt.py` three times, once for each standard test in Guideline 3, and fill in this table:

| Test | Interest paid | Months | States explored | Matches Guideline 4? |
| --- | --- | --- | --- | --- |
| Test 1 | | | | |
| Test 2 | | | | |
| Test 3 | | | | |

If a number is different: first check you did not change a starter function, then compare your code with the answer key line by line.

## Step 5 — Explain your result (15 min)
Answer these in 2–3 sentences each (they go into the report):
1. In Test 1, DFS paid **₹24,581** — ₹9,084 more than A*. Which debt did it repay first, and why was that a bad choice?
2. In Test 3, DFS paid the **same** as A* (₹20,911). Why did it "get lucky" there?
   *(Hint: compare the loan and card interest rates in Test 3.)*
3. Why did DFS explore only 13 states?

## Step 6 — Send your part to the team (15 min)
Send these to Ritu (report) and Dharmik (slides), and your test table to Tanish:

- **Report paragraph (4–6 sentences):** what DFS does, its result in the 3 tests, and the answers from Step 5.
- **Slide text (3 bullets):** "DFS: deepest first, stack" · "Follows the first choice (loan first)" · "Test 1: ₹24,581 — ₹9,084 more than A*".

## Step 7 — Your extra role: the slides (1 hour)
Make about 10 slides (Google Slides or PowerPoint):

| # | Slide | Content from |
| --- | --- | --- |
| 1 | Title, team names | Dharmik |
| 2 | The problem (income → interest → savings → repay) | Guideline 1 |
| 3 | Why the order matters (₹15,497 vs ₹24,581) | Guideline 1 |
| 4 | The search problem (state, actions, cost, goal) | Guideline 2 |
| 5 | BFS | Ritu |
| 6 | DFS | Dharmik |
| 7 | UCS | Tanish |
| 8 | Greedy and A* + the heuristic | Mithunn |
| 9 | Results table (3 tests) | Tanish |
| 10 | Winner: A* and why + live demo | Mithunn |

Keep one idea per slide and big text. Check every number against Guideline 4.

## Viva questions you must be able to answer
1. **What data structure does DFS use?** A LIFO stack: the newest state is expanded first.
2. **Why `reversed(...)`?** A stack pops the last item pushed. Pushing the children in reverse makes the first child come out first.
3. **Is DFS optimal?** No. It returns the first plan it reaches, not the cheapest.
4. **Why does DFS skip a state that is already in CLOSED when popped?** The same state can be pushed twice from different branches; we only explore it once.
5. **When would DFS give the best answer here?** When the first choice it tries (loan first) happens to be the best one, e.g. when the loan has the higher rate (Test 3).

---

<details><summary>Answer key: DFS (open only after trying)</summary>

```python
def dfs(start):
    OPEN = [start]                          # stack
    CLOSED = set()
    parent = {start: None}
    while OPEN:
        state = OPEN.pop()                  # take from the END (newest first)
        if state in CLOSED:                 # already explored -> skip
            continue
        if state == goal:
            path = []
            while state is not None:
                path.append(state)
                state = parent[state]
            return path[::-1], len(CLOSED)
        CLOSED.add(state)
        graph[state] = neighbours(state)
        for child in reversed(graph.get(state, [])):   # first choice explored first
            if child not in CLOSED:
                parent[child] = state
                OPEN.append(child)          # add to the END
    return None, len(CLOSED)
```
</details>
