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

def astar(start):
    OPEN = [(heuristic(start), 0, start)]
    CLOSED = set()
    parent = {start: None}
    g_cost = {start: 0}
    while OPEN:
        best = 0
        for i in range(len(OPEN)):
            if OPEN[i] < OPEN[best]:
                best = i
        f, g, state = OPEN.pop(best)
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
            new_g = g + interest(state)
            if child not in g_cost or new_g < g_cost[child]:
                g_cost[child] = new_g
                parent[child] = state
                CLOSED.discard(child)
                OPEN.append((new_g + heuristic(child), new_g, child))
    return None, len(CLOSED)


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
    path, explored = astar(start)          # <- change ALGORITHM to your function name
    print()
    print("Solution found using A* Search")   # <- change the name
    month = 0
    for state in path:
        print("Month", month, end="   ")
        show(state)
        month = month + 1
    print("Months to clear the debt:", len(path) - 1)
    print("Total interest paid     :", path_cost(path))
    print("States explored         :", explored)