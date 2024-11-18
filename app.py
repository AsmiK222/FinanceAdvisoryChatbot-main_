import streamlit as st  
import pandas as pd
from datetime import datetime
import csv
import os
from groq import Groq


# Set up the Streamlit page configuration at the start
st.set_page_config(page_title="Personal Finance Advisor", layout="wide")

# File to store cash flow data
CASH_FLOW_FILE = 'cash_flow.csv'


# Function to log cash flow to CSV
def log_cash_flow(amount, date, category, flow_type, description=""):
    file_exists = os.path.isfile(CASH_FLOW_FILE)
    with open(CASH_FLOW_FILE, 'a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Amount', 'Date', 'Category', 'Flow Type', 'Description'])
        writer.writerow([amount, date, category, flow_type, description])

# Function to load and filter cash flow data by the current month
def get_current_month_cash_flow():
    if os.path.isfile(CASH_FLOW_FILE):
        df = pd.read_csv(CASH_FLOW_FILE)
        df['Date'] = pd.to_datetime(df['Date'])
        current_month = datetime.now().month
        current_year = datetime.now().year
        filtered_df = df[(df['Date'].dt.month == current_month) & (df['Date'].dt.year == current_year)]
        return filtered_df
    else:
        return pd.DataFrame(columns=['Amount', 'Date', 'Category', 'Flow Type', 'Description'])


def generate_response(prompt):
    if prompt:
        with st.spinner("Generating response... Please wait."):
            try:
                # Initialize Groq client
                client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

                # Create a chat completion
                response = client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )

                # Extract the generated content
                raw_output = response.choices[0].message.content

                # Display the raw output as-is in the chat format
                with st.chat_message("assistant"):
                    st.write(raw_output)

                # Optionally display raw output in an expander for debugging
                with st.expander("View Raw Output (JSON)"):
                    st.code(raw_output, language="json")

            except Exception as e:
                with st.chat_message("assistant"):
                    st.error(f"An error occurred: {e}")
    else:
        st.warning("Please enter a prompt!")



# Main title
st.markdown('<h1 style="text-align: center; color: #333;">Personal Finance Advisor</h1>', unsafe_allow_html=True)

# Center the sections with tabs for Cash Flow, Tax Planning, and Investment Advice
tab1, tab2, tab3 = st.tabs(["💸 Cash Flow", "🧾 Tax Planning Assistance", "📈 Investment Advice"])

# Cash Flow Tab
with tab1:
    st.header("Track Your Expenses and Income")
    st.subheader("Log Your Expenses")

    # Expense Tracker
    expense_amount = st.number_input("Amount Spent (₹)", min_value=0, step=1, key="expense_amount")
    expense_date = st.date_input("Date of Expense", key="expense_date")
    expense_category = st.radio(
        "Expense Category",
        ['Traveling', 'Food', 'Electricity', 'Education', 'Entertainment', 'Others'],
        key="expense_category",
    )

    expense_description = ""
    if expense_category == 'Others':
        expense_description = st.text_input("Specify the Category", key="expense_description")

    if st.button('Log Expense'):
        if expense_amount > 0:
            log_cash_flow(expense_amount, expense_date, expense_category, "Expense", expense_description)
            st.success(f'Logged: ₹{expense_amount} for {expense_category} on {expense_date}')
        else:
            st.warning("Please enter a valid amount.")

    # Income Tracker
    st.subheader("Log Your Income")
    income_amount = st.number_input("Income Received (₹)", min_value=0, step=1, key="income_amount")
    income_date = st.date_input("Date of Income", key="income_date")
    income_category = st.radio(
        "Income Source",
        ['Salary', 'Freelancing', 'Investment', 'Gifts', 'Others'],
        key="income_category",
    )

    income_description = ""
    if income_category == 'Others':
        income_description = st.text_input("Specify the Source", key="income_description")

    if st.button('Log Income'):
        if income_amount > 0:
            log_cash_flow(income_amount, income_date, income_category, "Income", income_description)
            st.success(f'Logged: ₹{income_amount} from {income_category} on {income_date}')
        else:
            st.warning("Please enter a valid amount.")

    # Display Current Month Cash Flow
    st.subheader("Current Month’s Cash Flow")
    cash_flow_df = get_current_month_cash_flow()

    # Visualize Cash Flow Data
    if not cash_flow_df.empty:
        st.dataframe(cash_flow_df, use_container_width=True)
        st.subheader("Expense Breakdown by Category")
        expense_data = cash_flow_df[cash_flow_df['Flow Type'] == 'Expense']
        if not expense_data.empty:
            expense_summary = expense_data.groupby('Category')['Amount'].sum()
            st.bar_chart(expense_summary)
        else:
            st.info("No expenses logged for this month.")

    else:
        st.info("No cash flow data available for the current month.")

# Tax Planning Assistance Tab
with tab2:
    st.header("Tax Planning Assistance")
    st.subheader("Input Your Tax Details")

    # Input for Annual Income/Salary
    annual_income = st.number_input("Annual Income/Salary (₹)", min_value=0, step=1000, key="annual_income")
    income_sources = st.multiselect(
        "Additional Income Sources",
        ['Freelancing', 'Investment', 'Other'],
        key="income_sources",
    )
    medical_expenses = st.number_input("Medical Expenses (₹)", min_value=0, step=1, key="medical_expenses")
    mortgage_interest = st.number_input("Mortgage Interest Paid (₹)", min_value=0, step=1, key="mortgage_interest")
    charitable_contributions = st.number_input("Charitable Contributions (₹)", min_value=0, step=1, key="charitable_contributions")

    filing_status = st.selectbox(
        "Filing Status",
        ['Single', 'Married Filing Jointly', 'Married Filing Separately', 'Head of Household'],
        key="filing_status",
    )
    credits = st.multiselect(
        "Eligible Tax Credits",
        ['Child Tax Credit', 'Education Credit', 'Retirement Savings Contribution Credit', 'Other'],
        key="credits",
    )
    specific_questions = st.text_area("Specific Questions/Concerns", key="specific_questions")

    if st.button('Generate Tax Planning Advice'):
        prompt = (
            f"So based on these given data generate me a tax planning advice, assuming I'm an Indian. "
            f"Annual Income: {annual_income}, Income Sources: {', '.join(income_sources)}, "
            f"Deductions: Medical Expenses: {medical_expenses}, Mortgage Interest: {mortgage_interest}, "
            f"Charitable Contributions: {charitable_contributions}, Filing Status: {filing_status}, "
            f"Tax Credits: {', '.join(credits)}, Specific Questions: {specific_questions}, "
        )
        generate_response(prompt)

# Investment Advice Tab
with tab3:
    st.header("Personalized Investment Advice")
    st.subheader("Enter Your Preferences")

    # Input for investment preferences
    risk_tolerance = st.select_slider(
        "Risk Tolerance", options=["Low", "Moderate", "High"], key="risk_tolerance"
    )
    investment_horizon = st.slider(
        "Investment Horizon (Years)", min_value=1, max_value=30, key="investment_horizon"
    )
    investment_goals = st.multiselect(
        "Investment Goals",
        ['Retirement', 'Buying a House', 'Education', 'Vacation', 'Emergency Fund', 'Other'],
        key="investment_goals",
    )
    initial_investment = st.number_input("Initial Investment (₹)", min_value=0, step=1000, key="initial_investment")
    monthly_contribution = st.number_input("Monthly Contribution (₹)", min_value=0, step=100, key="monthly_contribution")

    if st.button('Generate Investment Advice'):
        prompt = (
            f"So based on these given data generate me an investing advice, assuming I'm an Indian. "
            f"Risk Tolerance: {risk_tolerance}, Investment Horizon: {investment_horizon}, "
            f"Investment Goals: {', '.join(investment_goals)}, Initial Investment: {initial_investment}, "
            f"Monthly Contribution: {monthly_contribution}"
        )
        generate_response(prompt)
