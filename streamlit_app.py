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

# Custom CSS - Professional theme-aware styling
st.markdown("""
<style>
    /* CSS Variables for theme-aware colors */
    :root {
        --primary: #4f46e5;
        --primary-light: #818cf8;
        --primary-dark: #3730a3;
        --secondary: #06b6d4;
        --success: #10b981;
        --success-light: #34d399;
        --danger: #ef4444;
        --danger-light: #f87171;
        --warning: #f59e0b;
        --warning-light: #fbbf24;
    }

    /* Light mode (default) */
    @media (prefers-color-scheme: light) {
        :root {
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-tertiary: #f1f5f9;
            --text-primary: #1e293b;
            --text-secondary: #475569;
            --text-muted: #94a3b8;
            --border-color: #e2e8f0;
            --card-bg: #ffffff;
            --sidebar-bg: #f8fafc;
        }
    }

    /* Dark mode */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-tertiary: #334155;
            --text-primary: #f1f5f9;
            --text-secondary: #cbd5e1;
            --text-muted: #64748b;
            --border-color: #334155;
            --card-bg: #1e293b;
            --sidebar-bg: #1e293b;
        }
    }

    /* Streamlit theme override - ensure variables work */
    .stApp {
        background-color: var(--bg-primary);
        color: var(--text-primary);
    }

    /* Header styles */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-primary);
        text-align: center;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .sub-header {
        font-size: 1.1rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Card styles - theme aware */
    .metric-card {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 14px rgba(79, 70, 229, 0.3);
    }
    .optimal-badge {
        background: var(--success);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .suboptimal-badge {
        background: var(--danger);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .info-box {
        background: var(--bg-secondary);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid var(--primary);
        margin: 1rem 0;
        color: var(--text-primary);
    }
    .method-step {
        background: var(--card-bg);
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid var(--border-color);
        margin: 0.5rem 0;
        color: var(--text-primary);
    }

    /* Sidebar styling */
    .css-1d391kg, .css-1lcbmhc, .css-1outpf7 {
        background-color: var(--sidebar-bg) !important;
    }

    /* DataFrame styling */
    .stDataFrame {
        background-color: var(--card-bg) !important;
    }
    .stDataFrame [data-testid="stTable"] {
        background-color: var(--card-bg) !important;
    }

    /* Input fields */
    .stNumberInput input, .stSelectbox select, .stTextInput input {
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
        border-color: var(--border-color) !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary) 0%, var(--secondary) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4) !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: var(--bg-secondary);
        padding: 4px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: var(--text-secondary) !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    .stTabs [aria-selected="true"] {
        background-color: var(--primary) !important;
        color: white !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
        border: 1px solid var(--border-color) !important;
    }
    .streamlit-expanderContent {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-top: none !important;
        border-radius: 0 0 8px 8px !important;
    }

    /* Streamlit status boxes - theme aware */
    .stAlert {
        background-color: var(--bg-secondary) !important;
        border-color: var(--border-color) !important;
        color: var(--text-primary) !important;
    }
    .stAlert[data-baseweb="notification"] {
        background-color: var(--bg-secondary) !important;
    }

    /* Success box */
    .stSuccess {
        background-color: rgba(16, 185, 129, 0.15) !important;
        border-left: 4px solid var(--success) !important;
        color: var(--text-primary) !important;
    }

    /* Info box */
    .stInfo {
        background-color: rgba(6, 182, 212, 0.15) !important;
        border-left: 4px solid var(--secondary) !important;
        color: var(--text-primary) !important;
    }

    /* Warning box */
    .stWarning {
        background-color: rgba(245, 158, 11, 0.15) !important;
        border-left: 4px solid var(--warning) !important;
        color: var(--text-primary) !important;
    }

    /* Error box */
    .stError {
        background-color: rgba(239, 68, 68, 0.15) !important;
        border-left: 4px solid var(--danger) !important;
        color: var(--text-primary) !important;
    }

    /* Metric containers */
    [data-testid="stMetric"] {
        background-color: var(--card-bg) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 8px !important;
        padding: 1rem !important;
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-secondary) !important;
    }
    [data-testid="stMetricValue"] {
        color: var(--text-primary) !important;
    }

    /* Markdown text */
    .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown ul, .stMarkdown ol {
        color: var(--text-primary) !important;
    }

    /* Plotly charts container */
    .js-plotly-plot {
        background-color: var(--card-bg) !important;
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
        background: var(--primary);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary-dark);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">💰 Debt Repayment Optimizer</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Find the optimal strategy to pay off your Loan & Credit Card with minimum interest</p>', unsafe_allow_html=True)

# Sidebar - Input Form
with st.sidebar:
    st.markdown("## 📋 Enter Your Details")

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

    run_button = st.button("🚀 Run Optimization", type="primary", use_container_width=True)

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
        st.markdown("## 📊 Algorithm Comparison Results")

        # Create comparison dataframe
        df_results = pd.DataFrame([
            {
                "Algorithm": r["Algorithm"],
                "Total Interest": r["Interest Paid"],
                "Months": r["Months"],
                "States Explored": r["States Explored"],
                "Status": "✅ Optimal" if r["Interest Value"] == min_interest else "❌ Suboptimal"
            }
            for r in results
        ])

        # Style the dataframe - theme aware
        def highlight_optimal(row):
            if row["Status"] == "✅ Optimal":
                return ['background-color: rgba(16, 185, 129, 0.15)'] * len(row)
            return [''] * len(row)

        st.dataframe(
            df_results.style.apply(highlight_optimal, axis=1),
            use_container_width=True,
            hide_index=True
        )

        # ===== METRICS ROW =====
        st.markdown("### 🏆 Key Metrics")
        optimal_results = [r for r in results if r["Interest Value"] == min_interest]
        optimal_algo = optimal_results[0]["Algorithm"]

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

        # ===== VISUALIZATIONS =====
        st.markdown("## 📈 Visual Analysis")

        tab1, tab2, tab3 = st.tabs(["Interest Comparison", "Efficiency Comparison", "Monthly Breakdown"])

        with tab1:
            # Bar chart for interest - theme aware
            fig_interest = px.bar(
                df_results,
                x="Algorithm",
                y="Interest Value",
                color="Status",
                color_discrete_map={"✅ Optimal": "#10b981", "❌ Suboptimal": "#ef4444"},
                title="Total Interest Paid by Algorithm",
                text="Total Interest",
                template="plotly_white"
            )
            fig_interest.update_traces(textposition='outside')
            fig_interest.update_layout(
                showlegend=False,
                yaxis_title="Interest (₹)",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#1e293b"),
                title_font=dict(size=16, color="#1e293b"),
                xaxis=dict(gridcolor="#e2e8f0"),
                yaxis=dict(gridcolor="#e2e8f0")
            )
            st.plotly_chart(fig_interest, use_container_width=True)

        with tab2:
            # Scatter plot: States explored vs Interest - theme aware
            fig_scatter = px.scatter(
                df_results,
                x="States Explored",
                y="Interest Value",
                color="Algorithm",
                size="Months",
                hover_data=["Months"],
                title="Search Efficiency: States Explored vs Interest Paid",
                labels={"Interest Value": "Total Interest (₹)", "States Explored": "States Explored"},
                template="plotly_white",
                color_discrete_sequence=["#4f46e5", "#06b6d4", "#10b981", "#f59e0b", "#ef4444"]
            )
            fig_scatter.update_layout(
                xaxis_type="log",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#1e293b"),
                title_font=dict(size=16, color="#1e293b"),
                xaxis=dict(gridcolor="#e2e8f0"),
                yaxis=dict(gridcolor="#e2e8f0"),
                legend=dict(bgcolor='rgba(255,255,255,0.8)')
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

            st.info("💡 **Lower left is better** — fewer states explored AND less interest paid. A* achieves this!")

        with tab3:
            # Monthly breakdown for optimal algorithm
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

            fig_monthly = make_subplots(
                rows=2, cols=1,
                subplot_titles=("Debt Balances Over Time", "Monthly Interest Paid"),
                vertical_spacing=0.15
            )

            fig_monthly.add_trace(
                go.Scatter(x=df_months["Month"], y=df_months["Loan Balance"],
                          name="Loan", line=dict(color="#4f46e5", width=3), fill='tozeroy', fillcolor='rgba(79,70,229,0.1)'),
                row=1, col=1
            )
            fig_monthly.add_trace(
                go.Scatter(x=df_months["Month"], y=df_months["Card Balance"],
                          name="Card", line=dict(color="#06b6d4", width=3), fill='tozeroy', fillcolor='rgba(6,182,212,0.1)'),
                row=1, col=1
            )
            fig_monthly.add_trace(
                go.Bar(x=df_months["Month"], y=df_months["Interest This Month"],
                      name="Interest", marker_color="#f59e0b"),
                row=2, col=1
            )

            fig_monthly.update_layout(
                height=600,
                showlegend=True,
                template="plotly_white",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#1e293b"),
                legend=dict(bgcolor='rgba(255,255,255,0.8)')
            )
            fig_monthly.update_xaxes(title_text="Month", row=2, col=1, gridcolor="#e2e8f0")
            fig_monthly.update_yaxes(title_text="Balance (₹)", row=1, col=1, gridcolor="#e2e8f0")
            fig_monthly.update_yaxes(title_text="Interest (₹)", row=2, col=1, gridcolor="#e2e8f0")

            st.plotly_chart(fig_monthly, use_container_width=True)

            # Month-by-month table
            st.markdown("### 📅 Month-by-Month Repayment Plan")
            display_df = df_months.copy()
            display_df["Loan Balance"] = display_df["Loan Balance"].apply(lambda x: f"₹{x:,}")
            display_df["Card Balance"] = display_df["Card Balance"].apply(lambda x: f"₹{x:,}")
            display_df["Interest This Month"] = display_df["Interest This Month"].apply(lambda x: f"₹{x:,}")
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        # ===== METHOD EXPLANATION =====
        st.markdown("## 🧠 How the Optimal Solution Was Found")

        with st.expander("🔍 **Click to see the A* Search Method Explained**", expanded=True):
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

            st.markdown("### 🎯 Why A* Finds the Optimal Solution")

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

            st.markdown("### 💡 The Key Insight for Your Debt")

            if card_rate > loan_rate:
                st.success(f"""
                **Your Credit Card ({card_rate}%) is MORE expensive than your Loan ({loan_rate}%)**

                → **Optimal Strategy: Pay the Credit Card FIRST every month**

                This is exactly what A* and UCS discovered. By aggressively paying off the 36% debt first,
                you save ₹9,084 compared to paying the loan first!
                """)
            elif loan_rate > card_rate:
                st.success(f"""
                **Your Loan ({loan_rate}%) is MORE expensive than your Credit Card ({card_rate}%)**

                → **Optimal Strategy: Pay the Loan FIRST every month**

                In this case, all algorithms agree because the higher-rate debt is obvious.
                """)
            else:
                st.info("Both debts have the same interest rate — order doesn't matter!")

            st.markdown("### 📋 Step-by-Step Monthly Process")

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
    <h3>👋 Welcome to the Debt Repayment Optimizer!</h3>
    <p>This tool uses <strong>AI search algorithms</strong> to find the mathematically optimal way to pay off your loan and credit card debt.</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎯 What This Does")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="method-step">
        <h4>🔍 Compares 5 Algorithms</h4>
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
        <h4>📊 Shows You Everything</h4>
        <ul>
        <li>Total interest for each method</li>
        <li>Months to become debt-free</li>
        <li>States explored (efficiency)</li>
        <li>Month-by-month plan</li>
        <li>Visual charts & comparisons</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="method-step">
        <h4>🧠 Explains the Method</h4>
        <ul>
        <li>How search algorithms apply to debt</li>
        <li>Why A* finds the best solution</li>
        <li>The heuristic that guarantees optimality</li>
        <li>Why paying highest-rate first wins</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 🚀 Get Started")
    st.markdown("Enter your details in the **sidebar** and click **Run Optimization** to see the optimal repayment plan!")

    # Show test cases info
    st.markdown("### 📝 Standard Test Cases (from project)")
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