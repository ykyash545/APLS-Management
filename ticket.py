import streamlit as st
import psycopg2
import csv
from io import StringIO

# Database connection details (replace with yours)
DB_HOST = "alps-dot3.postgres.database.azure.com"
DB_NAME = "crud-test"
DB_USER = "manishabharati"
DB_PASSWORD = "Windows10@"

conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
)

# Create tables if they don't exist (modify as needed)
cursor = conn.cursor()

create_ticket_table = """
CREATE TABLE IF NOT EXISTS tickets (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'Open',
    assigned_to_group INTEGER
);
"""
cursor.execute(create_ticket_table)

create_group_table = """
CREATE TABLE IF NOT EXISTS groups (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);
"""
cursor.execute(create_group_table)

# Function to add a new ticket
def add_ticket(title, description, status, assigned_to_group=None):
    cursor.execute("INSERT INTO tickets (title, description, status, assigned_to_group) VALUES (%s, %s, %s, %s)", (title, description, status, assigned_to_group))
    conn.commit()
    st.success("Ticket added successfully!")

# Function to close a ticket
def close_ticket(ticket_id):
    cursor.execute("UPDATE tickets SET status = 'Closed' WHERE id = %s", (ticket_id,))
    conn.commit()
    st.success(f"Ticket with ID {ticket_id} closed successfully!")

# Function to export ticket details to CSV
def export_tickets():
    cursor.execute("SELECT * FROM tickets")
    tickets = cursor.fetchall()
    if tickets:
        with StringIO() as buffer:
            writer = csv.writer(buffer)
            writer.writerow(["ID", "Title", "Description", "Status", "Assigned Group"])
            writer.writerows(tickets)
            csv_data = buffer.getvalue()
        st.download_button(label="Export CSV", data=csv_data, file_name="tickets.csv", mime="text/csv")

# Streamlit App
st.title("Ticketing System Dashboard")

# Form to add a new ticket
new_ticket_form = st.form("new_ticket")
title = new_ticket_form.text_input("Title")
description = new_ticket_form.text_area("Description")

# Add a dropdown menu for selecting status
status_options = ("Open", "Pending", "Resolved")
status = new_ticket_form.selectbox("Status", options=status_options)

# Fetch group names
cursor.execute("SELECT name FROM groups")
group_records = cursor.fetchall()
if group_records:
    group_options = [group[0] for group in group_records]
else:
    group_options = []

# Add a dropdown menu for selecting assigned group
assigned_to_group = new_ticket_form.selectbox("Assign to Group", options=["IT","Sofware Devlopment","ML Team","SOC",""] + group_options)

submit_button = new_ticket_form.form_submit_button("Submit Ticket")

if submit_button:
    # Get group id if assigned
    if assigned_to_group:
        cursor.execute("SELECT id FROM groups WHERE name = %s", (assigned_to_group,))
        assigned_group_id = cursor.fetchone()
        if assigned_group_id:
            assigned_group_id = assigned_group_id[0]
        else:
            assigned_group_id = None
        add_ticket(title, description, status, assigned_group_id)
    else:
        add_ticket(title, description, status)

# Form to close a ticket
close_ticket_form = st.form("close_ticket")
close_ticket_id = close_ticket_form.text_input("Enter Ticket ID to Close")
close_button = close_ticket_form.form_submit_button("Close Ticket")

if close_button:
    # Validate input to ensure it's a valid integer
    try:
        ticket_id = int(close_ticket_id)
        close_ticket(ticket_id)
    except ValueError:
        st.error("Invalid ticket ID. Please enter an integer.")

# Export button to download ticket details
export_tickets()

# Display existing tickets in card-like layout
st.header("Open Tickets")
cursor.execute("SELECT t.id, t.title, t.description, t.status, g.name FROM tickets t LEFT JOIN groups g ON t.assigned_to_group = g.id WHERE t.status = 'Open'")
open_tickets = cursor.fetchall()

if open_tickets:
    for ticket in open_tickets:
        st.subheader(f"Ticket ID: {ticket[0]}")
        st.write(f"**Title:** {ticket[1]}")
        st.write(f"**Status:** {ticket[3]}")
        st.write(f"**Assigned Group:** {ticket[4] if ticket[4] else 'Unassigned'}")
        st.write(f"**Description:** {ticket[2]}")
        st.write("---")
else:
    st.info("No open tickets found.")

st.header("Closed Tickets")
cursor.execute("SELECT t.id, t.title, t.description, t.status, g.name FROM tickets t LEFT JOIN groups g ON t.assigned_to_group = g.id WHERE t.status = 'Closed'")
closed_tickets = cursor.fetchall()

if closed_tickets:
    for ticket in closed_tickets:
        st.subheader(f"Ticket ID: {ticket[0]}")
        st.write(f"**Title:** {ticket[1]}")
        st.write(f"**Status:** {ticket[3]}")
        st.write(f"**Assigned Group:** {ticket[4] if ticket[4] else 'Unassigned'}")
        st.write(f"**Description:** {ticket[2]}")
        st.write("---")
else:
    st.info("No closed tickets found.")

cursor.close()
conn.close()
