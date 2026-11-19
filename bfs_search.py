def interest(state):
    loan,card=state
    return round(loan*loan_rate/1200)+round(card*card_rate/1200)
def neighbours(state):
    result=[]
    loan,card=state
    extra = income-interest(state)-savings  #REMAINING AFTER SAVINGS AND INTEREST
    #CHOICE 1: REPAY THE MONTHLY AMOUNT AND LEFTOVER GOES TO CARD
    pay_loan=min(extra,loan)
    pay_card=min(extra-pay_loan,card)
    result.append((loan-pay_loan,card-pay_card))
    # CHOICE 2:REPAY CARD MONTHLY PAYMENT AND LEFTOVER GOES TO LOAN
    pay_card=min(extra, card)
    pay_loan=min(extra - pay_card, loan)
    child=(loan - pay_loan, card - pay_card)
    if child not in result:
        result.append(child)
    return result
def show(state):
    print("Loan:",state[0],"  Card:",state[1])
def path_cost(path):
    total=0
    for state in path[:-1]:
        total=total+interest(state)  #INTEREST PAID PER MONTH
    return total
def heuristic(state):
    total=state[0]+state[1]
    low=min(loan_rate, card_rate) / 1200  #LEAST MONTHLY INTEREST RATE
    h=0
    while total>0:
        h=h+total*low-1      #ADDING -1 FOR SAFETY MARGIN TO ROUND
        total=total-payment  #MAXIMUM HIGHEST AMOUNT POSSIBLE TO PAYED/FASTER PAYMENT
    return max(0,h)
graph={}  #ADJACENCY LIST                          
def bfs(start):
    open=[start]
    closed=set()
    parent={start:None}
    while open:
        state=open.pop(0)
        if state==goal:
            path=[]
            while state is not None:
                path.append(state)
                state=parent[state]
            path.reverse()
            return path,len(closed)
        closed.add(state)
        graph[state]=neighbours(state)
        for child in graph.get(state,[]):
            if child not in parent:
                parent[child]=state
                open.append(child)
    return None,len(closed)
income=int(input("Enter monthly income (after expenses): "))
savings=int(input("Enter monthly savings: "))
loan=int(input("Enter loan amount: "))
loan_rate=float(input("Enter loan interest rate (% per year): "))
card=int(input("Enter credit card amount: "))
card_rate=float(input("Enter credit card interest rate (% per year): "))
payment=income-savings   #MOST THAT CAN EVER GO TO THE DEBTS IN A MONTH
start=(loan,card)
goal=(0,0)
if income-interest(start)-savings<=0:
    print("After paying the interest and savings, nothing is left to repay the debt")
else:
    path,explored=bfs(start)         
    print()
    print("Solution found using BFS(Breadth-First-Search)")   
    print("Month".ljust(7),"Loan".ljust(10),"Card")
    print("-"*28)
    month=0
    for state in path:
        print(str(month).ljust(7),str(state[0]).ljust(10),state[1])
        month=month+1
    print("Months to clear the debt:",len(path) - 1)
    print("Total interest paid     :",path_cost(path))
    print("States explored         :",explored)
