import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import our algorithms
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# ===== CORE ALGORITHM FUNCTIONS (copied from our project) =====

def interest(state, loan_rate, card_rate):
    loan, card = state
    return round(loan * loan_rate / 1200) + round(card * card_rate / 1200)


def neighbours(state, income, savings, loan_rate, card_rate):
    result = []
    loan, card = state
    extra = income - interest(state, loan_rate, card_rate) - savings

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
    return f"Loan: ₹{state[0]:,}  Card: ₹{state[1]:,}"


def path_cost(path, loan_rate, card_rate):
    total = 0
    for state in path[:-1]:
        total = total + interest(state, loan_rate, card_rate)
    return total


def heuristic(state, loan_rate, card_rate, payment):
    total = state[0] + state[1]
    low = min(loan_rate, card_rate) / 1200
    h = 0
    while total > 0:
        h = h + total * low - 1
        total = total - payment
    return max(0, h)


# ===== ALGORITHM IMPLEMENTATIONS =====

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


def run_all_algorithms(income, savings, loan, loan_rate, card, card_rate):
    """Run all 5 algorithms and return results"""
    payment = income - savings
    start = (loan, card)
    goal = (0, 0)

    # Check if repayment is possible
    if income - interest(start, loan_rate, card_rate) - savings <= 0:
        return None, "After paying interest and savings, nothing is left to repay the debt"

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
            total_interest = path_cost(path, loan_rate, card_rate)
            months = len(path) - 1
            results.append({
                "Algorithm": name,
                "Interest Paid": f"₹{total_interest:,}",
                "Interest Value": total_interest,
                "Months": months,
                "States Explored": explored,
                "Path": path
            })

    return results, None


# ===== STREAMLIT UI =====

st.set_page_config(
    page_title="Debt Repayment Optimizer",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Balanced, aesthetic, uniform color scheme
st.markdown("""
<style>
    /* CSS Variables - Single cohesive color palette */
    :root {
        /* Primary brand color - deep indigo */
        --brand: #3b4ba0;
        --brand-light: #5a6fc8;
        --brand-dark: #2d3a7a;
        --brand-pale: #eef0f8;
        --brand-pale-dark: #2d3a7a33;

        /* Semantic colors - muted, professional */
        --success: #1e8a49;
        --success-bg: #e8f5ed;
        --success-bg-dark: #1e8a4933;
        --danger: #c0392b;
        --danger-bg: #fdf2f2;
        --danger-bg-dark: #c0392b33;
        --warning: #b7950b;
        --warning-bg: #fef9e7;
        --warning-bg-dark: #b7950b33;

        /* Light mode (default) */
        --bg-primary: #fafbfc;
        --bg-secondary: #f0f2f5;
        --bg-tertiary: #e4e8ee;
        --card-bg: #ffffff;
        --sidebar-bg: #f0f2f5;
        --text-primary: #1a1d23;
        --text-secondary: #4a4f5a;
        --text-muted: #8a8f9a;
        --border-color: #d0d5dd;
        --border-focus: #3b4ba0;
    }

    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #16181c;
            --bg-secondary: #1e2126;
            --bg-tertiary: #2a2e35;
            --card-bg: #1e2126;
            --sidebar-bg: #1e2126;
            --text-primary: #f0f2f5;
            --text-secondary: #b0b5bd;
            --text-muted: #7a7f8a;
            --border-color: #3a3f4a;
            --border-focus: #5a6fc8;
            --brand-pale: #2d3a7a33;
            --success-bg: #1e8a4933;
            --danger-bg: #c0392b33;
            --warning-bg: #b7950b33;
        }
    }

    /* Global app styling */
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }

    /* Header - clean, no gradient text */
    .main-header {
        font-size: 2.25rem;
        font-weight: 700;
        color: var(--brand);
        text-align: center;
        margin-bottom: 0.25rem;
        letter-spacing: -0.02em;
    }
    .sub-header {
        font-size: 1rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 400;
    }

    /* Section headers */
    .section-header {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--border-color);
    }

    /* Cards - uniform, subtle */
    .metric-card {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        padding: 1.25rem;
        border-radius: 10px;
        text-align: center;
        transition: border-color 0.2s, box-shadow 0.2s;
    }
    .metric-card:hover {
        border-color: var(--brand);
        box-shadow: 0 2px 8px rgba(59, 75, 160, 0.08);
    }
    .metric-card h3 {
        font-size: 0.75rem;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin: 0 0 0.5rem 0;
    }
    .metric-card h2 {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--brand);
        margin: 0;
    }

    .optimal-badge {
        background: var(--success-bg);
        color: var(--success);
        padding: 0.2rem 0.6rem;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .suboptimal-badge {
        background: var(--danger-bg);
        color: var(--danger);
        padding: 0.2rem 0.6rem;
        border-radius: 16px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    .info-box {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-left: 3px solid var(--brand);
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        color: var(--text-primary);
    }

    .method-step {
        background: var(--card-bg);
        border: 1px solid var(--border-color);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        color: var(--text-primary);
    }

    /* Sidebar */
    .css-1d391kg, .css-1lcbmhc, .css-1outpf7,
    [data-testid="stSidebar"] {
        background-color: var(--sidebar-bg) !important;
    }
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-primary) !important;
    }

    /* DataFrame */
    .stDataFrame {
        background-color: var(--card-bg) !important;
    }
    .stDataFrame [data-testid="stTable"] {
        background-color: var(--card-bg) !important;
    }
    .stDataFrame table {
        color: var(--text-primary) !important;
    }
    .stDataFrame th {
        background-color: var(--bg-secondary) !important;
        color: var(--text-secondary) !important;
        border-color: var(--border-color) !important;
    }
    .stDataFrame td {
        border-color: var(--border-color) !important;
    }

    /* Input fields */
    .stNumberInput input, .stSelectbox select, .stTextInput input,
    .stNumberInput > div > div, .stSelectbox > div > div {
        background-color: var(--card-bg) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-color) !important;
    }
    .stNumberInput input:focus, .stSelectbox select:focus, .stTextInput input:focus {
        border-color: var(--border-focus) !important;
        box-shadow: 0 0 0 3px var(--brand-pale) !important;
    }

    /* Labels */
    label, .stSelectbox label, .stNumberInput label {
        color: var(--text-secondary) !important;
        font-weight: 500 !important;
    }

    /* Buttons - clean, single color */
    .stButton > button {
        background: var(--brand) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.625rem 1.25rem !important;
        transition: background-color 0.2s, transform 0.1s !important;
    }
    .stButton > button:hover {
        background: var(--brand-dark) !important;
        transform: translateY(-1px) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background-color: var(--bg-secondary);
        padding: 4px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
        padding: 0.5rem 1rem !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--card-bg) !important;
        color: var(--brand) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-color) !important;
        font-weight: 500 !important;
    }
    .streamlit-expanderContent {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
        color: var(--text-primary) !important;
    }

    /* Status boxes - subtle, professional */
    .stAlert {
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        color: var(--text-primary) !important;
    }

    .stSuccess {
        background-color: var(--success-bg) !important;
        border-left: 3px solid var(--success) !important;
        color: var(--text-primary) !important;
    }
    .stInfo {
        background-color: var(--brand-pale) !important;
        border-left: 3px solid var(--brand) !important;
        color: var(--text-primary) !important;
    }
    .stWarning {
        background-color: var(--warning-bg) !important;
        border-left: 3px solid var(--warning) !important;
        color: var(--text-primary) !important;
    }
    .stError {
        background-color: var(--danger-bg) !important;
        border-left: 3px solid var(--danger) !important;
        color: var(--text-primary) !important;
    }

    /* Markdown text */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown ul, .stMarkdown ol,
    .stMarkdown strong, .stMarkdown em {
        color: var(--text-primary) !important;
    }

    /* Table in markdown */
    .stMarkdown table {
        border-collapse: collapse;
        width: 100%;
    }
    .stMarkdown th, .stMarkdown td {
        padding: 0.5rem 0.75rem;
        border: 1px solid var(--border-color);
        color: var(--text-primary);
    }
    .stMarkdown th {
        background: var(--bg-secondary);
        font-weight: 600;
        color: var(--text-secondary);
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: var(--bg-secondary);
    }
    ::-webkit-scrollbar-thumb {
        background: var(--bg-tertiary);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-muted);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">Debt Repayment Optimizer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Find the optimal strategy to pay off your Loan & Credit Card with minimum interest</p>', unsafe_allow_html=True)

# Sidebar - Input Form
with st.sidebar:
    st.markdown("## Enter Your Details")

    # Quick test presets
    st.markdown("### Quick Test Cases")
    test_case = st.selectbox(
        "Choose a preset or enter custom values:",
        ["Custom", "Test 1: Card more expensive (₹100k @ 14%, ₹60k @ 36%)",
         "Test 2: Card much more expensive (₹50k @ 12%, ₹40k @ 42%)",
         "Test 3: Loan more expensive (₹100k @ 30%, ₹60k @ 18%)"]
    )

    if test_case == "Test 1: Card more expensive (₹100k @ 14%, ₹60k @ 36%)":
        income, savings, loan, loan_rate, card, card_rate = 20000, 5000, 100000, 14, 60000, 36
    elif test_case == "Test 2: Card much more expensive (₹50k @ 12%, ₹40k @ 42%)":
        income, savings, loan, loan_rate, card, card_rate = 15000, 3000, 50000, 12, 40000, 42
    elif test_case == "Test 3: Loan more expensive (₹100k @ 30%, ₹60k @ 18%)":
        income, savings, loan, loan_rate, card, card_rate = 20000, 5000, 100000, 30, 60000, 18
    else:
        st.markdown("### Monthly Income & Savings")
        income = st.number_input("Monthly Income (after expenses)", min_value=1000, value=20000, step=1000)
        savings = st.number_input("Monthly Savings", min_value=0, value=5000, step=500)

        st.markdown("### Loan Details")
        loan = st.number_input("Loan Amount (₹)", min_value=0, value=100000, step=10000)
        loan_rate = st.number_input("Loan Interest Rate (% per year)", min_value=0.0, max_value=50.0, value=14.0, step=0.5)

        st.markdown("### Credit Card Details")
        card = st.number_input("Credit Card Amount (₹)", min_value=0, value=60000, step=10000)
        card_rate = st.number_input("Card Interest Rate (% per year)", min_value=0.0, max_value=50.0, value=36.0, step=0.5)

    # Display selected values
    st.markdown("---")
    st.markdown("### Current Settings")
    st.write(f"**Income:** ₹{income:,}")
    st.write(f"**Savings:** ₹{savings:,}")
    st.write(f"**Loan:** ₹{loan:,} @ {loan_rate}%")
    st.write(f"**Card:** ₹{card:,} @ {card_rate}%")
    payment = income - savings
    extra = payment - interest((loan, card), loan_rate, card_rate)
    st.write(f"**Available for repayment:** ₹{payment:,}")
    st.write(f"**Extra after interest:** ₹{extra:,}")

    run_button = st.button("Run Optimization", type="primary", use_container_width=True)

# Main content area
if run_button:
    with st.spinner("Running all 5 search algorithms..."):
        results, error = run_all_algorithms(income, savings, loan, loan_rate, card, card_rate)

    if error:
        st.error(error)
    else:
        # Find optimal (minimum interest)
        min_interest = min(r["Interest Value"] for r in results)

        # ===== RESULTS TABLE =====
        st.markdown('<h2 class="section-header">Algorithm Comparison Results</h2>', unsafe_allow_html=True)

        # Create comparison dataframe
        df_results = pd.DataFrame([
            {
                "Algorithm": r["Algorithm"],
                "Total Interest": r["Interest Paid"],
                "Months": r["Months"],
                "States Explored": r["States Explored"],
                "Status": "Optimal" if r["Interest Value"] == min_interest else "Suboptimal"
            }
            for r in results
        ])

        # Style the dataframe - theme aware
        def highlight_optimal(row):
            if row["Status"] == "Optimal":
                return ['background-color: var(--success-bg)'] * len(row)
            return [''] * len(row)

        st.dataframe(
            df_results.style.apply(highlight_optimal, axis=1),
            use_container_width=True,
            hide_index=True
        )

        # ===== KEY METRICS =====
        st.markdown('<h2 class="section-header">Key Metrics</h2>', unsafe_allow_html=True)
        # Find algorithms with minimum interest
        min_interest = min(r["Interest Value"] for r in results)
        optimal_results = [r for r in results if r["Interest Value"] == min_interest]
        # Among those with lowest interest, pick the one with fewest states explored
        best_result = min(optimal_results, key=lambda r: r["States Explored"])
        optimal_algo = best_result["Algorithm"]

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Best Algorithm</h3>
                <h2>{optimal_algo}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Minimum Interest</h3>
                <h2>₹{min_interest:,}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Months to Clear</h3>
                <h2>{optimal_results[0]["Months"]}</h2>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>States Explored</h3>
                <h2>{optimal_results[0]["States Explored"]}</h2>
            </div>
            """, unsafe_allow_html=True)

        # ===== MONTHLY REPAYMENT PLAN =====
        st.markdown('<h2 class="section-header">Month-by-Month Repayment Plan</h2>', unsafe_allow_html=True)
        optimal_path = optimal_results[0]["Path"]

        months_data = []
        for i, state in enumerate(optimal_path):
            loan_amt, card_amt = state
            if i < len(optimal_path) - 1:
                month_interest = interest(state, loan_rate, card_rate)
            else:
                month_interest = 0
            months_data.append({
                "Month": i,
                "Loan Balance": loan_amt,
                "Card Balance": card_amt,
                "Interest This Month": month_interest
            })

        df_months = pd.DataFrame(months_data)

        # Display table
        display_df = df_months.copy()
        display_df["Loan Balance"] = display_df["Loan Balance"].apply(lambda x: f"₹{x:,}")
        display_df["Card Balance"] = display_df["Card Balance"].apply(lambda x: f"₹{x:,}")
        display_df["Interest This Month"] = display_df["Interest This Month"].apply(lambda x: f"₹{x:,}")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # ===== METHOD EXPLANATION =====
        st.markdown('<h2 class="section-header">How the Optimal Solution Was Found</h2>', unsafe_allow_html=True)

        with st.expander("Click to see the A* Search Method Explained", expanded=True):
            st.markdown("""
            ### The Problem as a Search Problem

            | Search Concept | Debt Repayment Equivalent |
            |---------------|--------------------------|
            | **State** | (Loan Balance, Card Balance) e.g., (₹1,00,000, ₹60,000) |
            | **Start State** | Your initial debt amounts |
            | **Goal State** | (0, 0) — Both debts cleared |
            | **Actions** | Each month: Pay **Loan First** OR **Card First** |
            | **Step Cost** | Interest paid that month |
            | **Path Cost (g)** | Total interest paid so far |
            | **Heuristic (h)** | Estimated minimum remaining interest |
            | **f = g + h** | A* evaluation function |
            """)

            st.markdown("### Why A* Finds the Optimal Solution")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                <div class="method-step">
                <h4>1. UCS (Uniform Cost Search)</h4>
                <p>Expands the state with <strong>lowest interest paid so far (g)</strong>. Guaranteed optimal but explores blindly in all directions — 243 states in Test 1.</p>
                </div>

                <div class="method-step">
                <h4>2. Greedy Best-First</h4>
                <p>Expands the state with <strong>lowest estimated remaining interest (h)</strong>. Fast (13 states) but not optimal — ignores interest already paid.</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class="method-step">
                <h4>3. A* Search (Best of Both)</h4>
                <p>Expands state with <strong>lowest f = g + h</strong>. Combines actual cost so far with intelligent estimate of remaining cost. <strong>Optimal AND efficient</strong> — only 29 states!</p>
                </div>

                <div class="method-step">
                <h4>4. The Heuristic (h)</h4>
                <p>Assumes <strong>all remaining debt</strong> at <strong>lowest interest rate</strong>, paid at <strong>maximum possible rate</strong>. This <strong>never overestimates</strong>, so A* is guaranteed optimal.</p>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("### The Key Insight for Your Debt")

            if card_rate > loan_rate:
                st.success(f"""
                **Your Credit Card ({card_rate}%) is MORE expensive than your Loan ({loan_rate}%)**

                → **Optimal Strategy: Pay the Credit Card FIRST every month**

                This is exactly what A* and UCS discovered. By aggressively paying off the higher-rate debt first,
                you save significantly compared to paying the loan first!
                """)
            elif loan_rate > card_rate:
                st.success(f"""
                **Your Loan ({loan_rate}%) is MORE expensive than your Credit Card ({card_rate}%)**

                → **Optimal Strategy: Pay the Loan FIRST every month**

                In this case, all algorithms agree because the higher-rate debt is obvious.
                """)
            else:
                st.info("Both debts have the same interest rate — order doesn't matter!")

            st.markdown("### Step-by-Step Monthly Process")

            # Show the monthly calculation for first month
            extra_first = income - interest((loan, card), loan_rate, card_rate) - savings
            st.markdown(f"""
            **Month 1 Calculation:**
            1. Income arrives: ₹{income:,}
            2. Pay loan interest: -₹{round(loan * loan_rate / 1200):,} ({loan:,} × {loan_rate}% ÷ 12)
            3. Pay card interest: -₹{round(card * card_rate / 1200):,} ({card:,} × {card_rate}% ÷ 12)
            4. Put into savings: -₹{savings:,}
            5. **Leftover for repayment: ₹{extra_first:,}**
            6. **DECISION:** Pay **{"CARD" if card_rate > loan_rate else "LOAN"} first** (higher interest rate) → leftover goes to other
            """)

            # Show neighbours
            next_states = neighbours((loan, card), income, savings, loan_rate, card_rate)
            st.markdown("**Possible next states:**")
            for i, (nl, nc) in enumerate(next_states):
                strat = "Loan First" if i == 0 else "Card First"
                st.write(f"  {strat}: Loan ₹{nl:,}, Card ₹{nc:,}")

else:
    # Welcome screen
    st.markdown("""
    <div class="info-box">
    <h3>Welcome to the Debt Repayment Optimizer</h3>
    <p>This tool uses <strong>AI search algorithms</strong> to find the mathematically optimal way to pay off your loan and credit card debt.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### What This Does")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="method-step">
        <h4>Compares 5 Algorithms</h4>
        <ul>
        <li>BFS — Fewest months</li>
        <li>DFS — First path found</li>
        <li>UCS — Guaranteed optimal</li>
        <li>Greedy — Fast heuristic</li>
        <li><strong>A* — Optimal + Efficient</strong></li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="method-step">
        <h4>Shows You Everything</h4>
        <ul>
        <li>Total interest for each method</li>
        <li>Months to become debt-free</li>
        <li>States explored (efficiency)</li>
        <li>Month-by-month plan</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="method-step">
        <h4>Explains the Method</h4>
        <ul>
        <li>How search algorithms apply to debt</li>
        <li>Why A* finds the best solution</li>
        <li>The heuristic that guarantees optimality</li>
        <li>Why paying highest-rate first wins</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### Get Started")
    st.markdown("Enter your details in the **sidebar** and click **Run Optimization** to see the optimal repayment plan!")

    # Show test cases info
    st.markdown("### Standard Test Cases (from project)")
    test_df = pd.DataFrame({
        "Test": ["Test 1", "Test 2", "Test 3"],
        "Income": ["₹20,000", "₹15,000", "₹20,000"],
        "Savings": ["₹5,000", "₹3,000", "₹5,000"],
        "Loan": ["₹1,00,000 @ 14%", "₹50,000 @ 12%", "₹1,00,000 @ 30%"],
        "Card": ["₹60,000 @ 36%", "₹40,000 @ 42%", "₹60,000 @ 18%"],
        "Optimal Strategy": ["Card First", "Card First", "Loan First"],
        "Min Interest": ["₹15,497", "₹6,636", "₹20,911"]
    })
    st.dataframe(test_df, use_container_width=True, hide_index=True)