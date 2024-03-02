import streamlit as st
import psycopg2
import pandas as pd
import secrets
import string
from passlib.hash import pbkdf2_sha256
from PIL import Image
def generate_random_password(length=10):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password

# Function to create a database connection
def create_connection():
    conn = psycopg2.connect(
        dbname='crud-test',
        user='manishabharati',
        password='Windows10@',
        host='alps-dot3.postgres.database.azure.com',
        port='5432'
    )
    return conn

# Function to create a table if it doesn't exist
def create_table(conn):
    query = '''
    CREATE TABLE IF NOT EXISTS records (
        id SERIAL PRIMARY KEY,
        patient_id TEXT NOT NULL,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        address TEXT,
        dob DATE,
        email TEXT,
        phone TEXT,
        doctor_id INTEGER  -- Add doctor_id column
    )
    '''
    conn.cursor().execute(query)
    conn.commit()

      # Create Users table
    query_users = '''
    CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        username TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
    '''
    conn.cursor().execute(query_users)
    
    conn.commit()

# Function to add a new record
def add_record(patient_id, name, age, address, dob, email, phone):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO records (patient_id, name, age, address, dob, email, phone) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                       (patient_id, name, age, address, dob, email, phone))
        st.success('Record added successfully!')

# Function to view all records
def view_records():
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records")
        rows = cursor.fetchall()
    if not rows:
        st.warning('No records found!')
    else:
        st.write('## Records')
        for row in rows:
            st.write(f"**ID:** {row[0]}, **Patient ID:** {row[1]}, **Name:** {row[2]}, **Age:** {row[3]}, **Address:** {row[4]}, **DOB:** {row[5]}, **Email:** {row[6]}, **Phone:** {row[7]}")

# Function to update a record
def update_record(record_id, patient_id, name, age, address, dob, email, phone):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE records SET patient_id=%s, name=%s, age=%s, address=%s, dob=%s, email=%s, phone=%s WHERE id=%s",
                       (patient_id, name, age, address, dob, email, phone, record_id))
        st.success('Record updated successfully!')

# Function to delete a record
def delete_record(record_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM records WHERE id=%s", (record_id,))
        st.success('Record deleted successfully!')

# Function to create a new user
def create_user(username, email, password):
    
    # Hash the password using PBKDF2 with SHA-256
    hashed_password = pbkdf2_sha256.hash(password)
    
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Users (username, email, password) VALUES (%s, %s, %s)", (username, email, hashed_password))
        st.success('User created successfully!')

# Function to delete a user
def delete_user(user_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Users WHERE id=%s", (user_id,))
        st.success('User deleted successfully!')

# User Management
def user_management():
    st.subheader("User Management")

    # Option to create a new user
    st.subheader("Create User")
    new_username = st.text_input('Enter Username')
    new_email = st.text_input('Enter Email')
    if st.button('Create User'):
        password = generate_random_password()
        create_user(new_username, new_email, password)


    # Option to delete a user
    st.subheader("Delete User")
    user_id_to_delete = st.number_input('Enter ID of User to Delete', min_value=1, step=1)
    if st.button('Delete User'):
        delete_user(user_id_to_delete)

    # Display existing users
    conn = create_connection()
    if conn:
        # Query database and display results
        query = "SELECT * FROM Users"
        df = pd.read_sql(query, conn)
        st.write(df)
# Patient Management
#def patient_management():
    #st.subheader("Patient Management")
    #conn = create_connection()
    #if conn:
        # Query database and display results
        #query = "SELECT * FROM records"
       # df = pd.read_sql(query, conn)
       # st.write(df)
# Patient Management
def patient_management():
    st.subheader("Patient Management")
    conn = create_connection()
    if conn:
        # Query database and display results
        query = "SELECT * FROM records"
        df = pd.read_sql(query, conn)
        st.write(df)

        st.subheader("Assign Doctor")
        patient_id = st.text_input('Enter Patient ID')
        doctor_id = st.selectbox('Select Doctor', options=get_doctor_options())
        if st.button('Assign Doctor'):
            assign_doctor(patient_id, doctor_id)

# Function to get doctor options for dropdown
def get_doctor_options():
    conn = create_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM Doctors")
        doctors = cursor.fetchall()
        doctor_options = {doctor[0]: doctor[1] for doctor in doctors}
        return doctor_options

# Function to assign a doctor to a patient
def assign_doctor(patient_id, doctor_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE records SET doctor_id=%s WHERE patient_id=%s", (doctor_id, patient_id))
        st.success('Doctor assigned successfully!')


# Doctor Management
def doctor_management():
    st.subheader("Doctor Management")
    conn = create_connection()
    query = '''
    CREATE TABLE IF NOT EXISTS Doctors (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        specialization TEXT
    )
    '''
    conn.cursor().execute(query)
    conn.commit()
    
    # Add Doctor
    st.subheader("Add Doctor")
    new_doctor_name = st.text_input('Enter Doctor Name')
    new_specialization = st.text_input('Enter Specialization')
    if st.button('Add Doctor'):
        add_doctor(new_doctor_name, new_specialization)

    # Option to delete a doctor
    st.subheader("Delete Doctor")
    doctor_id_to_delete = st.number_input('Enter ID of Doctor to Delete', min_value=1, step=1)
    if st.button('Delete Doctor'):
        delete_doctor(doctor_id_to_delete)

    # Display existing doctors
    if conn:
        # Query database and display results
        query = "SELECT * FROM Doctors"
        df = pd.read_sql(query, conn)
        st.write(df)

# Function to add a new doctor record
def add_doctor(name, specialization):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Doctors (name, specialization) VALUES (%s, %s)", (name, specialization))
        st.success('Doctor added successfully!')

# Function to delete a doctor record
def delete_doctor(doctor_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Doctors WHERE id=%s", (doctor_id,))
        st.success('Doctor deleted successfully!')


def generate_invoice(patient_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records WHERE patient_id=%s", (patient_id,))
        patient_data = cursor.fetchone()

        cursor.execute("SELECT name, specialization FROM Doctors WHERE id=%s", (patient_data[8],))  # Assuming doctor_id is at index 8
        doctor_data = cursor.fetchone()
    
    if patient_data and doctor_data:
        # Extract patient information
        patient_id = patient_data[1]
        name = patient_data[2]
        age = patient_data[3]
        address = patient_data[4]
        dob = patient_data[5]
        email = patient_data[6]
        phone = patient_data[7]

        # Extract doctor information
        doctor_name = doctor_data[0]
        doctor_specialization = doctor_data[1]

        # Calculate total amount (replace this with your calculation logic)
        total_amount = 100  # Example total amount
        
        # Generate invoice
        invoice = f"Patient ID: {patient_id}\nName: {name}\nAge: {age}\nAddress: {address}\nDOB: {dob}\nEmail: {email}\nPhone: {phone}\nDoctor: {doctor_name} ({doctor_specialization})\nTotal Amount: {total_amount}"
        
        # Check if the Invoices table exists, if not, create it
        cursor.execute("CREATE TABLE IF NOT EXISTS Invoices (id SERIAL PRIMARY KEY, invoice_id TEXT NOT NULL, patient_id TEXT NOT NULL, invoice_text TEXT NOT NULL)")

        # Generate invoice ID (you can replace this with your own method to generate unique IDs)
        invoice_id = f"INV-{patient_id}-{doctor_name}"

        # Save invoice to the Invoices table with invoice ID
        cursor.execute("INSERT INTO Invoices (invoice_id, patient_id, invoice_text) VALUES (%s, %s, %s)", (invoice_id, patient_id, invoice))
        conn.commit()
        return invoice
    else:
        return "Patient or doctor not found"


# Function to create the inventory table if it doesn't exist
def create_inventory_table(conn):
    query = '''
    CREATE TABLE IF NOT EXISTS inventory (
        id SERIAL PRIMARY KEY,
        item_name VARCHAR(255) NOT NULL,
        quantity INT NOT NULL
    )
    '''
    conn.cursor().execute(query)
    conn.commit()

# Function to add a new item to the inventory
def add_inventory_item(item_name, quantity):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (item_name, quantity) VALUES (%s, %s)",
                       (item_name, quantity))
        st.success('Inventory item added successfully!')

# Function to view all items in the inventory
def view_inventory():
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventory")
        rows = cursor.fetchall()
    if not rows:
        st.warning('No items in inventory!')
    else:
        st.write('## Inventory')
        for row in rows:
            st.write(f"**ID:** {row[0]}, **Item Name:** {row[1]}, **Quantity:** {row[2]}")

# Function to update quantity of an item in the inventory
def update_inventory_item(item_id, new_quantity):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET quantity=%s WHERE id=%s",
                       (new_quantity, item_id))
        st.success('Inventory item quantity updated successfully!')

# Function to delete an item from the inventory
def delete_inventory_item(item_id):
    conn = create_connection()
    with conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id=%s", (item_id,))
        st.success('Inventory item deleted successfully!')


# Main function to run the Streamlit app
def main():
    create_table(create_connection())
    create_inventory_table(create_connection())

    st.title('Admin Portal')

    logo_image = Image.open('D:\\Back up 2024 Jan\\ALPS PROJECT\\Admin Portal\\alps-logo.png')
    st.sidebar.image(logo_image, use_column_width=True)

    # Navigation
    menu = ['Create record', 'User Management', 'Patient Management', 'Doctor Management', 'Generate Invoice', 'Inventory']
    choice = st.sidebar.selectbox('Select Feature', menu)  
    
    if choice == 'Inventory':
        st.title('Inventory Management')
        menu = ['Add Item', 'View Inventory', 'Update Item Quantity', 'Delete Item']
        sub_choice = st.sidebar.selectbox('Menu', menu)

        if sub_choice == 'Add Item':
            st.header('Add New Inventory Item')
            item_name = st.text_input('Enter Item Name')
            quantity = st.number_input('Enter Quantity', min_value=0, step=1)
            if st.button('Add Item'):
                add_inventory_item(item_name, quantity)

        elif sub_choice == 'View Inventory':
            st.header('View Inventory')
            view_inventory()

        elif sub_choice == 'Update Item Quantity':
            st.header('Update Inventory Item Quantity')
            item_id = st.number_input('Enter ID of Item to Update', min_value=1, step=1)
            new_quantity = st.number_input('Enter New Quantity', min_value=0, step=1)
            if st.button('Update Quantity'):
                update_inventory_item(item_id, new_quantity)

        elif sub_choice == 'Delete Item':
            st.header('Delete Inventory Item')
            item_id = st.number_input('Enter ID of Item to Delete', min_value=1, step=1)
            if st.button('Delete Item'):
                delete_inventory_item(item_id)

    if choice == 'Create record':
        st.title('record management')
        menu = ['Add Record', 'View Records', 'Update Record', 'Delete Record']
        choice = st.sidebar.selectbox('Menu', menu)

        if choice == 'Add Record':
            st.header('Add New Record')
            patient_id = st.text_input('Enter Patient ID')
            name = st.text_input('Enter Name')
            age = st.number_input('Enter Age', min_value=0, max_value=150, step=1)
            address = st.text_input('Enter Address')
            dob = st.date_input('Enter Date of Birth')
            email = st.text_input('Enter Email')
            phone = st.text_input('Enter Phone Number')
            if st.button('Add Record'):
                add_record(patient_id, name, age, address, dob, email, phone)

        elif choice == 'View Records':
            st.header('View Records')
            view_records()

        elif choice == 'Update Record':
            st.header('Update Record')
            record_id = st.number_input('Enter ID of Record to Update', min_value=1, step=1)
            patient_id = st.text_input('Enter Patient ID')
            name = st.text_input('Enter Name')
            age = st.number_input('Enter Age', min_value=0, max_value=150, step=1)
            address = st.text_input('Enter Address')
            dob = st.date_input('Enter Date of Birth')
            email = st.text_input('Enter Email')
            phone = st.text_input('Enter Phone Number')
            if st.button('Update Record'):
                update_record(record_id, patient_id, name, age, address, dob, email, phone)

        elif choice == 'Delete Record':
            st.header('Delete Record')
            record_id = st.number_input('Enter ID of Record to Delete', min_value=1, step=1)
            if st.button('Delete Record'):
                delete_record(record_id)

    elif choice == 'User Management':
        user_management()

    elif choice == 'Patient Management':
        patient_management()

    elif choice == 'Doctor Management':
        doctor_management()

    elif choice == 'Generate Invoice':
        st.title('Generate Invoice')
        invoice = ""  # Initialize invoice variable
        patient_id = st.text_input('Enter Patient ID')
        if st.button('Generate Invoice'):
            invoice = generate_invoice(patient_id)
        st.text_area('Invoice', value=invoice, height=400)


if __name__ == '__main__':
    main()
