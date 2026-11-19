import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==============================================================================
# Core Functions (from project guidelines)
# ==============================================================================

def interest(state, loan_rate, card_rate):
    loan, card = state
    return round(loan * loan_rate / 1200) + round(card * card_rate / 1200)


def neighbours(state, income, savings, loan_rate, card_rate):
    result = []
    loan, card = state
    extra = income - interest(state, loan_rate, card_rate) - savings

    # Choice 1: Repay Loan first
    pay_loan = min(extra, loan)
    pay_card = min(extra - pay_loan, card)
    result.append((loan - pay_loan, card - pay_card))

    # Choice 2: Repay Card first
    pay_card = min(extra, card)
    pay_loan = min(extra - pay_card, loan)
    child = (loan - pay_loan, card - pay_card)
    if child not in result:
        result.append(child)
    return result


def path_cost(path, loan_rate, card_rate):
    total = 0
    for state in path[:-1]:
        total += interest(state, loan_rate, card_rate)
    return total


def heuristic(state, loan_rate, card_rate, payment):
    if payment <= 0:
        return 0
    total = state[0] + state[1]
    low = min(loan_rate, card_rate) / 1200
    h = 0
    while total > 0:
        h = h + total * low - 1
        total = total - payment
    return max(0, h)


# ==============================================================================
# Search Algorithms
# ==============================================================================

def bfs(start, goal, income, savings, loan_rate, card_rate, payment):
    OPEN = [start]
    CLOSED = set()
    parent = {start: None}
    graph = {}
    while OPEN:
        state = OPEN.pop(0)
        if state == goal:
            path = []
            while state is not None:
                path.append(state)
                state = parent[state]
            return path[::-1], len(CLOSED)
        CLOSED.add(state)
        graph[state] = neighbours(state, income, savings, loan_rate, card_rate)
        for child in graph.get(state, []):
            if child not in parent:
                parent[child] = state
                OPEN.append(child)
    return None, len(CLOSED)


def dfs(start, goal, income, savings, loan_rate, card_rate, payment):
    OPEN = [start]
    CLOSED = set()
    parent = {start: None}
    graph = {}
    while OPEN:
        state = OPEN.pop()
        if state in CLOSED:
            continue
        if state == goal:
            path = []
            while state is not None:
                path.append(state)
                state = parent[state]
            return path[::-1], len(CLOSED)
        CLOSED.add(state)
        graph[state] = neighbours(state, income, savings, loan_rate, card_rate)
        for child in reversed(graph.get(state, [])):
            if child not in CLOSED:
                parent[child] = state
                OPEN.append(child)
    return None, len(CLOSED)


def ucs(start, goal, income, savings, loan_rate, card_rate, payment):
    OPEN = [(0, start)]
    CLOSED = set()
    parent = {start: None}
    g_cost = {start: 0}
    graph = {}
    while OPEN:
        best = 0
        for i in range(len(OPEN)):
            if OPEN[i] < OPEN[best]:
                best = i
        g, state = OPEN.pop(best)
        if state in CLOSED:
            continue
        if state == goal:
            path = []
            while state is not None:
                path.append(state)
                state = parent[state]
            return path[::-1], len(CLOSED)
        CLOSED.add(state)
        graph[state] = neighbours(state, income, savings, loan_rate, card_rate)
        for child in graph.get(state, []):
            new_g = g + interest(state, loan_rate, card_rate)
            if child not in g_cost or new_g < g_cost[child]:
                g_cost[child] = new_g
                parent[child] = state
                CLOSED.discard(child)
                OPEN.append((new_g, child))
    return None, len(CLOSED)


def greedy(start, goal, income, savings, loan_rate, card_rate, payment):
    OPEN = [(heuristic(start, loan_rate, card_rate, payment), start)]
    CLOSED = set()
    parent = {start: None}
    graph = {}
    while OPEN:
        best = 0
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
        graph[state] = neighbours(state, income, savings, loan_rate, card_rate)
        for child in graph.get(state, []):
            if child not in parent:
                parent[child] = state
                OPEN.append((heuristic(child, loan_rate, card_rate, payment), child))
    return None, len(CLOSED)


def astar(start, goal, income, savings, loan_rate, card_rate, payment):
    OPEN = [(heuristic(start, loan_rate, card_rate, payment), 0, start)]
    CLOSED = set()
    parent = {start: None}
    g_cost = {start: 0}
    graph = {}
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
        graph[state] = neighbours(state, income, savings, loan_rate, card_rate)
        for child in graph.get(state, []):
            new_g = g + interest(state, loan_rate, card_rate)
            if child not in g_cost or new_g < g_cost[child]:
                g_cost[child] = new_g
                parent[child] = state
                CLOSED.discard(child)
                OPEN.append((new_g + heuristic(child, loan_rate, card_rate, payment), new_g, child))
    return None, len(CLOSED)


def solve_all(income, savings, loan, loan_rate, card, card_rate):
    payment = income - savings
    start = (loan, card)
    goal = (0, 0)

    initial_interest = interest(start, loan_rate, card_rate)
    if income - initial_interest - savings <= 0:
        return None, "After paying the interest and savings, nothing is left to repay the debt"

    algorithms = [
        ("BFS", bfs),
        ("DFS", dfs),
        ("UCS", ucs),
        ("Greedy Best-First", greedy),
        ("A*", astar)
    ]

    results = []
    for name, algo in algorithms:
        path, explored = algo(start, goal, income, savings, loan_rate, card_rate, payment)
        if path:
            tot_interest = path_cost(path, loan_rate, card_rate)
            months = len(path) - 1
            results.append({
                "Algorithm": name,
                "Interest Paid (₹)": tot_interest,
                "Months": months,
                "States Explored": explored,
                "Path": path
            })
    return results, None


# ==============================================================================
# Streamlit Application
# ==============================================================================

st.set_page_config(
    page_title="Debt Repayment Planner",
    layout="wide"
)

st.title("Debt Repayment Planner")

# Presets
PRESETS = {
    "Test 1: Card Higher Rate (14% Loan vs 36% Card)": {
        "income": 20000, "savings": 5000,
        "loan": 100000, "loan_rate": 14.0,
        "card": 60000, "card_rate": 36.0
    },
    "Test 2: Card Much Higher Rate (12% Loan vs 42% Card)": {
        "income": 15000, "savings": 3000,
        "loan": 50000, "loan_rate": 12.0,
        "card": 40000, "card_rate": 42.0
    },
    "Test 3: Loan Higher Rate (30% Loan vs 18% Card)": {
        "income": 20000, "savings": 5000,
        "loan": 100000, "loan_rate": 30.0,
        "card": 60000, "card_rate": 18.0
    },
    "Custom Configuration": None
}

with st.sidebar:
    st.subheader("Parameters and Inputs")

    selected_preset = st.selectbox(
        "Preset:",
        list(PRESETS.keys()),
        index=0
    )

    preset_data = PRESETS[selected_preset]

    if "current_preset" not in st.session_state or st.session_state.current_preset != selected_preset:
        st.session_state.current_preset = selected_preset
        if preset_data is not None:
            st.session_state.inp_income = preset_data["income"]
            st.session_state.inp_savings = preset_data["savings"]
            st.session_state.inp_loan = preset_data["loan"]
            st.session_state.inp_loan_rate = preset_data["loan_rate"]
            st.session_state.inp_card = preset_data["card"]
            st.session_state.inp_card_rate = preset_data["card_rate"]

    if "inp_income" not in st.session_state:
        st.session_state.inp_income = 20000
        st.session_state.inp_savings = 5000
        st.session_state.inp_loan = 100000
        st.session_state.inp_loan_rate = 14.0
        st.session_state.inp_card = 60000
        st.session_state.inp_card_rate = 36.0

    st.markdown("**Monthly Cashflow**")
    income = st.number_input(
        "Monthly Income (after expenses)",
        min_value=1000,
        value=st.session_state.inp_income,
        step=1000
    )
    savings = st.number_input(
        "Monthly Savings",
        min_value=0,
        value=st.session_state.inp_savings,
        step=500
    )

    st.markdown("**Loan Details**")
    loan = st.number_input(
        "Loan Amount",
        min_value=0,
        value=st.session_state.inp_loan,
        step=10000
    )
    loan_rate = st.number_input(
        "Loan Interest Rate (% per year)",
        min_value=0.0,
        max_value=100.0,
        value=float(st.session_state.inp_loan_rate),
        step=0.5
    )

    st.markdown("**Credit Card Details**")
    card = st.number_input(
        "Credit Card Amount",
        min_value=0,
        value=st.session_state.inp_card,
        step=5000
    )
    card_rate = st.number_input(
        "Card Interest Rate (% per year)",
        min_value=0.0,
        max_value=100.0,
        value=float(st.session_state.inp_card_rate),
        step=0.5
    )

    st.divider()

    init_int = interest((loan, card), loan_rate, card_rate)
    leftover = income - init_int - savings
    st.write(f"**Max Payment Available:** ₹{income - savings:,}")
    st.write(f"**Month 1 Interest:** ₹{init_int:,}")
    st.write(f"**Principal Leftover:** ₹{leftover:,}")

    compare_clicked = st.button("Compare", type="primary", use_container_width=True)

# Keep comparison active once run
if "has_run" not in st.session_state:
    st.session_state.has_run = False

if compare_clicked:
    st.session_state.has_run = True

if not st.session_state.has_run:
    st.info("Click 'Compare' in the sidebar to run the algorithms and view results.")
else:
    results, error_msg = solve_all(income, savings, loan, loan_rate, card, card_rate)

    if error_msg:
        st.error(error_msg)
    else:
        min_interest = min(r["Interest Paid (₹)"] for r in results)
        worst_interest = max(r["Interest Paid (₹)"] for r in results)
        astar_result = next(r for r in results if r["Algorithm"] == "A*")
        ucs_result = next(r for r in results if r["Algorithm"] == "UCS")

        # Summary Metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Best Algorithm", "A* Search")
        m2.metric("Lowest Interest", f"₹{min_interest:,}")
        m3.metric("Duration to Clear", f"{astar_result['Months']} Months")
        m4.metric("States Explored (A* vs UCS)", f"{astar_result['States Explored']} vs {ucs_result['States Explored']}")

        st.write("")

        tab1, tab2 = st.tabs(["Algorithm Comparison", "Month-by-Month Plan"])

        # Tab 1: Comparison
        with tab1:
            st.subheader("Comparison Table")

            table_rows = []
            for r in results:
                is_opt = (r["Interest Paid (₹)"] == min_interest)
                table_rows.append({
                    "Algorithm": r["Algorithm"],
                    "Total Interest Paid": f"₹{r['Interest Paid (₹)']:,}",
                    "Months": r["Months"],
                    "States Explored": r["States Explored"],
                    "Optimal Plan": "Yes" if is_opt else "No"
                })

            df_display = pd.DataFrame(table_rows)
            st.dataframe(df_display, hide_index=True, use_container_width=True)

            st.divider()

            # Comparison Graphs
            c1, c2 = st.columns(2)

            with c1:
                st.markdown("**Total Interest Paid (Lower is Better)**")
                fig_int = go.Figure(data=[
                    go.Bar(
                        x=[r["Algorithm"] for r in results],
                        y=[r["Interest Paid (₹)"] for r in results],
                        text=[f"₹{r['Interest Paid (₹)']:,}" for r in results],
                        textposition="auto"
                    )
                ])
                fig_int.update_layout(
                    yaxis_title="Total Interest (₹)",
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=320
                )
                st.plotly_chart(fig_int, use_container_width=True)

            with c2:
                st.markdown("**States Explored (Lower is Better)**")
                fig_states = go.Figure(data=[
                    go.Bar(
                        x=[r["Algorithm"] for r in results],
                        y=[r["States Explored"] for r in results],
                        text=[f"{r['States Explored']}" for r in results],
                        textposition="auto"
                    )
                ])
                fig_states.update_layout(
                    yaxis_title="States Count",
                    margin=dict(l=20, r=20, t=20, b=20),
                    height=320
                )
                st.plotly_chart(fig_states, use_container_width=True)

            if card_rate > loan_rate:
                opt_choice = "Card first"
            elif loan_rate > card_rate:
                opt_choice = "Loan first"
            else:
                opt_choice = "Either"

            st.info(f"Optimal Strategy: Repay {opt_choice}. A* and UCS find the cheapest plan (₹{min_interest:,}), but A* explores {astar_result['States Explored']} states compared to {ucs_result['States Explored']} for UCS.")

        # Tab 2: Month by Month
        with tab2:
            st.subheader("Monthly Repayment Schedule")

            selected_algo = st.selectbox(
                "Select algorithm:",
                [r["Algorithm"] for r in results],
                index=4
            )

            chosen = next(r for r in results if r["Algorithm"] == selected_algo)
            chosen_path = chosen["Path"]

            plan_records = []
            for m, state in enumerate(chosen_path):
                l_bal, c_bal = state
                month_int = interest(state, loan_rate, card_rate) if m < len(chosen_path) - 1 else 0
                plan_records.append({
                    "Month": m,
                    "Loan Balance (₹)": l_bal,
                    "Credit Card Balance (₹)": c_bal,
                    "Total Debt (₹)": l_bal + c_bal,
                    "Interest Charged (₹)": month_int
                })

            df_plan = pd.DataFrame(plan_records)

            fig_curve = go.Figure()
            fig_curve.add_trace(go.Scatter(
                x=df_plan["Month"], y=df_plan["Loan Balance (₹)"],
                mode="lines+markers", name="Loan Balance"
            ))
            fig_curve.add_trace(go.Scatter(
                x=df_plan["Month"], y=df_plan["Credit Card Balance (₹)"],
                mode="lines+markers", name="Card Balance"
            ))
            fig_curve.add_trace(go.Scatter(
                x=df_plan["Month"], y=df_plan["Total Debt (₹)"],
                mode="lines+markers", name="Total Debt", line=dict(dash="dot")
            ))
            fig_curve.update_layout(
                xaxis_title="Month",
                yaxis_title="Balance (₹)",
                margin=dict(l=20, r=20, t=20, b=20),
                height=320
            )
            st.plotly_chart(fig_curve, use_container_width=True)

            st.dataframe(
                df_plan.style.format({
                    "Loan Balance (₹)": "₹{:,.0f}",
                    "Credit Card Balance (₹)": "₹{:,.0f}",
                    "Total Debt (₹)": "₹{:,.0f}",
                    "Interest Charged (₹)": "₹{:,.0f}"
                }),
                hide_index=True,
                use_container_width=True
            )
