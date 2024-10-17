import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
import plotly.express as px

# Define the database file name
DB_FILE = 'ceo_dashboard.db'

# Helper function to run SQLite queries
def run_query(query, params=(), fetch=False):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(query, params)
        if fetch:
            return c.fetchall()
        conn.commit()

# Helper function to manually format currency in South African Rands
def format_currency(value):
    return f"R {value:,.2f}"

# Initialize the database and create tables if they don't exist
def initialize_db():
    create_tasks_table = '''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_name TEXT NOT NULL,
        client_name TEXT NOT NULL,
        status TEXT NOT NULL,
        task_length INTEGER NOT NULL,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL
    )
    '''
    create_finances_table = '''
    CREATE TABLE IF NOT EXISTS finances (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        current_balance REAL NOT NULL,
        invoices_issued_30 REAL NOT NULL,
        invoices_issued_quarter REAL NOT NULL,
        invoices_issued_ytd REAL NOT NULL,
        quotes_generated_30 REAL NOT NULL,
        quotes_generated_quarter REAL NOT NULL,
        quotes_generated_ytd REAL NOT NULL
    )
    '''
    create_leads_table = '''
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        linkedin_leads INTEGER NOT NULL,
        web_leads INTEGER NOT NULL,
        briefs_not_started INTEGER NOT NULL,
        quotes_issued INTEGER NOT NULL,
        briefs_completed INTEGER NOT NULL,
        invoices_issued_leads REAL NOT NULL
    )
    '''
    run_query(create_tasks_table)
    run_query(create_finances_table)
    run_query(create_leads_table)

# Call the initialize_db function
initialize_db()

# Inject custom CSS for background, typography, and logo space
st.markdown(
    """
    <style>
    body {
        background-color: #25262b;
        font-family: 'Montserrat', sans-serif;
    }
    .css-1aumxhk {
        font-family: 'Montserrat', sans-serif;
    }
    .css-12ttj6m {
        background-color: #25262b;
    }
    .css-qbe2hs {
        background-color: #25262b;
    }
    .css-1offfwp {
        background-color: #25262b;
    }
    .css-1v0mbdj {
        background-color: #25262b;
    }
    .css-18ni7ap {
        background-color: #25262b;
    }
    .css-1offfwp .stTabs div[data-baseweb="tab-list"] button {
        background-color: #25262b;
        font-family: 'Montserrat', sans-serif;
        color: white;
    }
    .css-1aumxhk, .css-1v0mbdj {
        font-family: 'Montserrat', sans-serif;
    }
    .stApp {
        background-color: #25262b;
    }
    header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 0;
    }
    #logo {
        width: 100px;
        height: auto;
    }
    h1, h2, h3, h4, h5, h6, p, div, input, select, textarea {
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Add space for logo at the top left
st.markdown("""
<header>
    <img id="logo" src="logo (1).png" alt="Logo" />
</header>
""", unsafe_allow_html=True)

# Title
st.title('CEO Dashboard for Fable Business Analytics')

# Horizontal Tab Navigation
tabs = st.tabs(["Tasks & Workload", "Finances", "Leads", "Overview"])

# Tasks & Workload Section
with tabs[0]:
    st.header("Tasks & Workload")
    
    # Input form for tasks
    with st.form("Task Form"):
        task_name = st.text_input("Task Name")
        client_name = st.text_input("Client Name")
        status = st.selectbox("Status", ["Complete", "In Progress", "Not Started", "Overdue"])
        task_length = st.number_input("Task Length (in days)", min_value=0)
        start_date = st.date_input("Start Date", value=date.today())
        end_date = st.date_input("End Date", value=date.today())
        submit_task = st.form_submit_button("Submit Task")
    
    if submit_task:
        run_query(
            "INSERT INTO tasks (task_name, client_name, status, task_length, start_date, end_date) VALUES (?, ?, ?, ?, ?, ?)",
            (task_name, client_name, status, task_length, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        )
        st.success(f"Task '{task_name}' for client '{client_name}' added successfully!")
    
    # Display Tasks
    tasks = run_query("SELECT * FROM tasks", fetch=True)
    tasks_df = pd.DataFrame(tasks, columns=["ID", "Task Name", "Client Name", "Status", "Task Length", "Start Date", "End Date"])
    st.dataframe(tasks_df)

# Finances Section
with tabs[1]:
    st.header("Finances")

    with st.form("Finances Form"):
        current_balance = st.number_input("Current Balance", min_value=0.0, format="%.2f")
        invoices_issued_30 = st.number_input("Invoices Issued (Last 30 Days)", min_value=0.0, format="%.2f")
        invoices_issued_quarter = st.number_input("Invoices Issued (Quarter)", min_value=0.0, format="%.2f")
        invoices_issued_ytd = st.number_input("Invoices Issued (YTD)", min_value=0.0, format="%.2f")
        quotes_generated_30 = st.number_input("Quotes Generated (Last 30 Days)", min_value=0.0, format="%.2f")
        quotes_generated_quarter = st.number_input("Quotes Generated (Quarter)", min_value=0.0, format="%.2f")
        quotes_generated_ytd = st.number_input("Quotes Generated (YTD)", min_value=0.0, format="%.2f")
        submit_finances = st.form_submit_button("Submit Finances")
    
    if submit_finances:
        run_query(
            "INSERT INTO finances (current_balance, invoices_issued_30, invoices_issued_quarter, invoices_issued_ytd, quotes_generated_30, quotes_generated_quarter, quotes_generated_ytd) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (current_balance, invoices_issued_30, invoices_issued_quarter, invoices_issued_ytd, quotes_generated_30, quotes_generated_quarter, quotes_generated_ytd)
        )
        st.success("Financial data updated successfully!")

# Leads Section
with tabs[2]:
    st.header("Leads")

    with st.form("Leads Form"):
        linkedin_leads = st.number_input("LinkedIn Leads", min_value=0)
        web_leads = st.number_input("Website Leads", min_value=0)
        briefs_not_started = st.number_input("Briefs Not Started", min_value=0)
        quotes_issued = st.number_input("Quotes Issued", min_value=0)
        briefs_completed = st.number_input("Briefs Completed", min_value=0)
        invoices_issued_leads = st.number_input("Invoices Issued (Leads)", min_value=0.0, format="%.2f")
        submit_leads = st.form_submit_button("Submit Leads")
    
    if submit_leads:
        run_query(
            "INSERT INTO leads (linkedin_leads, web_leads, briefs_not_started, quotes_issued, briefs_completed, invoices_issued_leads) VALUES (?, ?, ?, ?, ?, ?)",
            (linkedin_leads, web_leads, briefs_not_started, quotes_issued, briefs_completed, invoices_issued_leads)
        )
        st.success("Leads data updated successfully!")

# Overview Section (Improved Visualizations using Plotly)
with tabs[3]:
    st.header("Overview")
    
    # Tasks Summary
    st.subheader("Tasks Overview")
    tasks = run_query("SELECT * FROM tasks", fetch=True)
    tasks_df = pd.DataFrame(tasks, columns=["ID", "Task Name", "Client Name", "Status", "Task Length", "Start Date", "End Date"])
    st.dataframe(tasks_df)
    
    if not tasks_df.empty:
        # Plotly bar chart for task status distribution
        status_counts = tasks_df['Status'].value_counts().reset_index()
        status_counts.columns = ['Task Status', 'Count']  # Rename the columns for clarity

        # Plotly bar chart for task status distribution
        status_chart = px.bar(
            status_counts,
            x='Task Status',
            y='Count',
            labels={'Task Status': 'Task Status', 'Count': 'Number of Tasks'},
            title="Task Status Distribution",
            text='Count'
        )
        st.plotly_chart(status_chart)

    # Financial Overview
    st.subheader("Financial Overview")
    finances = run_query("SELECT * FROM finances ORDER BY id DESC LIMIT 1", fetch=True)
    if finances:
        finances_df = pd.DataFrame(finances, columns=["ID", "Current Balance", "Invoices Issued (30 Days)", "Invoices Issued (Quarter)", "Invoices Issued (YTD)", "Quotes Generated (30 Days)", "Quotes Generated (Quarter)", "Quotes Generated (YTD)"])
        
        # Format the currency values for display in ZAR
        finances_df["Current Balance"] = finances_df["Current Balance"].apply(format_currency)
        finances_df["Invoices Issued (30 Days)"] = finances_df["Invoices Issued (30 Days)"].apply(format_currency)
        finances_df["Invoices Issued (Quarter)"] = finances_df["Invoices Issued (Quarter)"].apply(format_currency)
        finances_df["Invoices Issued (YTD)"] = finances_df["Invoices Issued (YTD)"].apply(format_currency)
        finances_df["Quotes Generated (30 Days)"] = finances_df["Quotes Generated (30 Days)"].apply(format_currency)
        finances_df["Quotes Generated (Quarter)"] = finances_df["Quotes Generated (Quarter)"].apply(format_currency)
        finances_df["Quotes Generated (YTD)"] = finances_df["Quotes Generated (YTD)"].apply(format_currency)

        st.dataframe(finances_df)
        
        # Plotly bar chart for financial data trends
        financial_data = finances_df.melt(id_vars=["ID"], var_name="Indicator", value_name="Amount")
        finance_chart = px.bar(
            financial_data, 
            x='Indicator', 
            y='Amount', 
            labels={'Indicator': 'Financial Metric', 'Amount': 'Value (ZAR)'}, 
            title="Financial Trends",
            text='Amount'
        )
        st.plotly_chart(finance_chart)

    # Leads Overview
    st.subheader("Leads Overview")
    leads = run_query("SELECT * FROM leads ORDER BY id DESC LIMIT 1", fetch=True)
    if leads:
        leads_df = pd.DataFrame(leads, columns=["ID", "LinkedIn Leads", "Website Leads", "Briefs Not Started", "Quotes Issued", "Briefs Completed", "Invoices Issued (Leads)"])
        st.dataframe(leads_df)
        
        # Prepare lead metrics for visualization
        leads_data = leads_df.melt(id_vars=["ID"], var_name="Metric", value_name="Value")
        
        # Plotly bar chart for leads metrics
        leads_chart = px.bar(
            leads_data, 
            x='Metric', 
            y='Value', 
            labels={'Metric': 'Leads Metric', 'Value': 'Count'}, 
            title="Leads Distribution",
            text='Value'
        )
        st.plotly_chart(leads_chart)

