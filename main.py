"""
Main project runner for the Debt Repayment Planner.
Team: Mithunn · Ritu · Dharmik · Tanish
Course: AI with Python
"""

import subprocess
import sys


def main():
    print("=" * 60)
    print("💰 Debt Repayment Planner — AI Search Optimizer")
    print("Team: Mithunn · Ritu · Dharmik · Tanish")
    print("=" * 60)
    print("Choose an option:")
    print("  1. Run Terminal Comparison Table (compare_all.py)")
    print("  2. Launch Streamlit Web UI (streamlit_app.py)")
    print("=" * 60)

    try:
        choice = input("Enter choice [1/2] (default: 1): ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\nExiting.")
        return

    if choice == "2":
        print("\nLaunching Streamlit web application...")
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"])
    else:
        print("\nRunning Terminal Comparison...")
        import compare_all


if __name__ == "__main__":
    main()

