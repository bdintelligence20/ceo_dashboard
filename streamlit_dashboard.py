import streamlit as st
import pandas as pd
import sqlite3
from datetime import date, datetime
import plotly.express as px
import calendar

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

# Add logo and title
st.image("images/logo.png", width=100)
st.title('CEO Dashboard for Fable Business Analytics')

# Horizontal Tab Navigation with Emojis
tabs = st.tabs(["📋 Tasks & Workload", "💰 Finances", "📈 Leads", "🔍 Overview"])

# Tasks & Workload Section with sub-tabs for Sheet, Kanban, and Calendar views
with tabs[0]:
    st.header("📋 Tasks & Workload")

    # Sub-tabs for the different views
    view_tabs = st.tabs(["📑 Sheet View", "📊 Kanban View", "📅 Calendar View"])

    # Fetch tasks and create a DataFrame
    tasks = run_query("SELECT * FROM tasks", fetch=True)
    tasks_df = pd.DataFrame(tasks, columns=["ID", "Task Name", "Client Name", "Status", "Task Length", "Start Date", "End Date"])

    # Pre-programmed status options
    status_options = ["Not Started", "In Progress", "Complete", "Overdue"]

    # Sheet View: Editable table of tasks
    with view_tabs[0]:
        st.subheader("📑 Sheet View")
        edited_tasks_df = st.data_editor(tasks_df, num_rows="dynamic", key="tasks_editor",
                                         column_config={"Status": {"type": "select", "options": status_options}})

        # Save changes back to the database
        if st.button("💾 Save Changes to Tasks"):
            for index, row in edited_tasks_df.iterrows():
                # Calculate Task Length based on Start Date and End Date
                task_length = (pd.to_datetime(row["End Date"]) - pd.to_datetime(row["Start Date"])).days
                run_query(
                    "UPDATE tasks SET task_name=?, client_name=?, status=?, task_length=?, start_date=?, end_date=? WHERE id=?",
                    (row["Task Name"], row["Client Name"], row["Status"], task_length, row["Start Date"], row["End Date"], row["ID"])
                )
            st.success("✅ Task changes saved successfully!")

    # Kanban View
    with view_tabs[1]:
        st.subheader("📊 Kanban View")
        kanban_columns = st.columns(4)
        kanban_board = {status: [] for status in status_options}
        
        for _, task in tasks_df.iterrows():
            kanban_board[task["Status"]].append(task)

        # Display tasks by status in Kanban columns
        for idx, status in enumerate(status_options):
            with kanban_columns[idx]:
                st.write(f"**{status}**")
                for task in kanban_board[status]:
                    st.write(f"- {task['Task Name']} (Client: {task['Client Name']})")

    # Calendar View with Waterfall (Gantt-style) View
    with view_tabs[2]:
        st.subheader("📅 Calendar View - Waterfall")
        
        # Filter tasks by selected month and year
        calendar_view_df = tasks_df.copy()
        calendar_view_df["Start Date"] = pd.to_datetime(calendar_view_df["Start Date"])
        calendar_view_df["End Date"] = pd.to_datetime(calendar_view_df["End Date"])

        month = st.selectbox("Select Month", range(1, 13), index=datetime.now().month - 1)
        year = st.selectbox("Select Year", range(datetime.now().year, datetime.now().year + 5), index=0)

        # Filter tasks that overlap with the selected month and year
        start_of_month = datetime(year, month, 1)
        end_of_month = datetime(year, month, calendar.monthrange(year, month)[1])
        filtered_tasks = calendar_view_df[
            (calendar_view_df["Start Date"] <= end_of_month) & (calendar_view_df["End Date"] >= start_of_month)
        ]

        if not filtered_tasks.empty:
            # Plot the waterfall calendar view
            fig = px.timeline(
                filtered_tasks,
                x_start="Start Date",
                x_end="End Date",
                y="Task Name",
                color="Status",
                title=f"Tasks for {calendar.month_name[month]} {year}",
                labels={"Start Date": "Start Date", "End Date": "End Date"}
            )
            fig.update_yaxes(categoryorder="total ascending")
            fig.update_layout(xaxis_title="Date", yaxis_title="Tasks")
            st.plotly_chart(fig)
        else:
            st.write("No tasks scheduled for this month.")

# Finances Section with editable table
with tabs[1]:
    st.header("💰 Finances")
    finances = run_query("SELECT * FROM finances", fetch=True)
    finances_df = pd.DataFrame(finances, columns=["ID", "Current Balance", "Invoices Issued (30 Days)", "Invoices Issued (Quarter)", "Invoices Issued (YTD)", "Quotes Generated (30 Days)", "Quotes Generated (Quarter)", "Quotes Generated (YTD)"])
    edited_finances_df = st.data_editor(finances_df, num_rows="dynamic", key="finances_editor")

    if st.button("💾 Save Changes to Finances"):
        for index, row in edited_finances_df.iterrows():
            run_query(
                "UPDATE finances SET current_balance=?, invoices_issued_30=?, invoices_issued_quarter=?, invoices_issued_ytd=?, quotes_generated_30=?, quotes_generated_quarter=?, quotes_generated_ytd=? WHERE id=?",
                (row["Current Balance"], row["Invoices Issued (30 Days)"], row["Invoices Issued (Quarter)"], row["Invoices Issued (YTD)"], row["Quotes Generated (30 Days)"], row["Quotes Generated (Quarter)"], row["Quotes Generated (YTD)"], row["ID"])
            )
        st.success("✅ Finance changes saved successfully!")

# Leads Section with editable table
with tabs[2]:
    st.header("📈 Leads")
    leads = run_query("SELECT * FROM leads", fetch=True)
    leads_df = pd.DataFrame(leads, columns=["ID", "LinkedIn Leads", "Website Leads", "Briefs Not Started", "Quotes Issued", "Briefs Completed", "Invoices Issued (Leads)"])
    edited_leads_df = st.data_editor(leads_df, num_rows="dynamic", key="leads_editor")

    if st.button("💾 Save Changes to Leads"):
        for index, row in edited_leads_df.iterrows():
            run_query(
                "UPDATE leads SET linkedin_leads=?, web_leads=?, briefs_not_started=?, quotes_issued=?, briefs_completed=?, invoices_issued_leads=? WHERE id=?",
                (row["LinkedIn Leads"], row["Website Leads"], row["Briefs Not Started"], row["Quotes Issued"], row["Briefs Completed"], row["Invoices Issued (Leads)"], row["ID"])
            )
        st.success("✅ Lead changes saved successfully!")

# Overview Section with visualizations
with tabs[3]:
    st.header("🔍 Overview")

    # Task Status Visualization
    st.subheader("Tasks Overview")
    tasks = run_query("SELECT * FROM tasks", fetch=True)
    tasks_df = pd.DataFrame(tasks, columns=["ID", "Task Name", "Client Name", "Status", "Task Length", "Start Date", "End Date"])
    if not tasks_df.empty:
        status_counts = tasks_df['Status'].value_counts().reset_index()
        status_counts.columns = ['Task Status', 'Count']
        status_chart = px.bar(
            status_counts,
            x='Task Status',
            y='Count',
            labels={'Task Status': 'Task Status', 'Count': 'Number of Tasks'},
            title="Task Status Distribution",
            text='Count'
        )
        st.plotly_chart(status_chart)

    # Financial Data Visualization
    st.subheader("Financial Overview")
    finances = run_query("SELECT * FROM finances ORDER BY id DESC LIMIT 1", fetch=True)
    if finances:
        finances_df = pd.DataFrame(finances, columns=["ID", "Current Balance", "Invoices Issued (30 Days)", "Invoices Issued (Quarter)", "Invoices Issued (YTD)", "Quotes Generated (30 Days)", "Quotes Generated (Quarter)", "Quotes Generated (YTD)"])
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

    # Leads Metrics Visualization
    st.subheader("Leads Overview")
    leads = run_query("SELECT * FROM leads ORDER BY id DESC LIMIT 1", fetch=True)
    if leads:
        leads_df = pd.DataFrame(leads, columns=["ID", "LinkedIn Leads", "Website Leads", "Briefs Not Started", "Quotes Issued", "Briefs Completed", "Invoices Issued (Leads)"])
        leads_data = leads_df.melt(id_vars=["ID"], var_name="Metric", value_name="Value")
        leads_chart = px.bar(
            leads_data, 
            x='Metric', 
            y='Value', 
            labels={'Metric': 'Leads Metric', 'Value': 'Count'}, 
            title="Leads Distribution",
            text='Value'
        )
        st.plotly_chart(leads_chart)
