# Developed By : <PRIYANSHUL SHARMA>
# My blog https://priyanshul.is-a.dev/

import mysql.connector as pymysql
from datetime import datetime

passwrd = None
db = None  
C = None

def base_check():
    check = 0
    db = pymysql.connect(host="localhost", user="root", password=passwrd)
    cursor = db.cursor()
    cursor.execute('SHOW DATABASES')
    result = cursor.fetchall()
    for r in result:
        for i in r:
            if i == 'pharmacy':
                cursor.execute('USE pharmacy')
                check = 1
    if check != 1:
        create_database()

def table_check():
    db = pymysql.connect(host="localhost", user="root", password=passwrd)
    cursor = db.cursor()
    cursor.execute('SHOW DATABASES')
    result = cursor.fetchall()
    for r in result:
        for i in r:
            if i == 'pharmacy':
                cursor.execute('USE pharmacy')
                cursor.execute('SHOW TABLES')
                result = cursor.fetchall()
                if len(result) <= 2:
                    create_tables()
                else:
                    print('      Booting systems...')

def create_database():
    try:
        db = pymysql.connect(host="localhost", user="root", password=passwrd)
        cursor = db.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS pharmacy")
        db.commit()
        db.close()
        print("Database 'pharmacy' created successfully.")
    except pymysql.Error as e:
        print(f"Error creating database: {str(e)}")

def create_tables():
    try:
        db = pymysql.connect(host="localhost", user="root", password=passwrd, database="pharmacy")
        cursor = db.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS medicines (
                MED_ID INT PRIMARY KEY,
                NAME VARCHAR(255),
                PRICE FLOAT,
                STOCK INT
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                SALE_ID INT AUTO_INCREMENT PRIMARY KEY,
                MED_ID INT,
                QUANTITY INT,
                SALE_DATE DATE,
                FOREIGN KEY (MED_ID) REFERENCES medicines(MED_ID)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS billing (
                BILL_ID INT AUTO_INCREMENT PRIMARY KEY,
                NAME VARCHAR(255),
                PHONE_NO VARCHAR(15),
                TOTAL_AMOUNT FLOAT,
                BILL_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        db.commit()
        db.close()
        print("Tables 'medicines', 'sales', and 'billing' created successfully.")
    except pymysql.Error as e:
        print(f"Error creating tables: {str(e)}")

def QR():
    result = C.fetchall()
    for r in result:
        print(r)

def add_medicine():
    med_id = int(input("Enter Medicine ID: "))
    name = input("Enter Medicine Name: ")
    price = float(input("Enter Medicine Price: "))
    stock = int(input("Enter Medicine Stock: "))
    data = (med_id, name, price, stock)
    sql = "INSERT INTO medicines (MED_ID, NAME, PRICE, STOCK) VALUES (%s, %s, %s, %s)"
    try:
        C.execute(sql, data)
        db.commit()
        print('Medicine added successfully...')
    except pymysql.Error as e:
        print(f"Error adding medicine: {str(e)}")

def view_medicines():
    C.execute("SELECT * FROM medicines")
    QR()

def search_medicine():
    search_by = input("Search by [MED_ID, NAME]: ")
    if search_by == 'NAME':
        name = input("Enter Medicine Name: ")
        sql = "SELECT * FROM medicines WHERE NAME = %s"
        C.execute(sql, (name,))
    elif search_by == 'MED_ID':
        med_id = int(input("Enter Medicine ID: "))
        sql = "SELECT * FROM medicines WHERE MED_ID = %s"
        C.execute(sql, (med_id,))
    else:
        print("Invalid search parameter.")
        return
    QR()

def update_medicine():
    med_id = int(input("Enter Medicine ID to update: "))
    field = input("Enter field to update [NAME, PRICE, STOCK]: ")
    new_value = input(f"Enter new value for {field}: ")
    if field in ['PRICE', 'STOCK']:
        new_value = float(new_value) if field == 'PRICE' else int(new_value)
    sql = f"UPDATE medicines SET {field} = %s WHERE MED_ID = %s"
    try:
        C.execute(sql, (new_value, med_id))
        db.commit()
        print('Medicine updated successfully...')
    except pymysql.Error as e:
        print(f"Error updating medicine: {str(e)}")

def delete_medicine():
    med_id = int(input("Enter Medicine ID to delete: "))
    sql = "DELETE FROM medicines WHERE MED_ID = %s"
    try:
        C.execute(sql, (med_id,))
        db.commit()
        print('Medicine deleted successfully...')
    except pymysql.Error as e:
        print(f"Error deleting medicine: {str(e)}")

def record_and_generate_bill():
    name = input("Enter Customer Name: ")
    phone_no = input("Enter Customer Phone Number: ")

    total_amount = 0.0
    while True:
        med_id = int(input("Enter Medicine ID for sale (or 0 to finish): "))
        if med_id == 0:
            break
        quantity = int(input("Enter Quantity: "))
        
        # Record Sale
        sale_date = datetime.now().date()
        sale_data = (med_id, quantity, sale_date)
        sql_sale = "INSERT INTO sales (MED_ID, QUANTITY, SALE_DATE) VALUES (%s, %s, %s)"
        try:
            C.execute(sql_sale, sale_data)
        except pymysql.Error as e:
            print(f"Error recording sale: {str(e)}")
            db.rollback()
            continue

        # Calculate Total Amount
        sql_price = "SELECT PRICE FROM medicines WHERE MED_ID = %s"
        C.execute(sql_price, (med_id,))
        result = C.fetchone()
        if result:
            price = result[0]
            total_amount += price * quantity

    # Generate Bill
    bill_data = (name, phone_no, total_amount)
    sql_bill = "INSERT INTO billing (NAME, PHONE_NO, TOTAL_AMOUNT) VALUES (%s, %s, %s)"
    try:
        C.execute(sql_bill, bill_data)
        db.commit()
        print(f'Bill generated successfully. Total amount: {total_amount}')
    except pymysql.Error as e:
        print(f"Error generating bill: {str(e)}")

def main():
    global passwrd
    passwrd = input("Enter password for MySQL: ")

    base_check()

    table_check()
    
    global db, C
    db = pymysql.connect(host="localhost", user="root", password=passwrd, database="pharmacy")
    C = db.cursor()
    while True:
        log = input("For Admin: A, For Salesperson: S ::: ")
        if log.upper() == "A":
            p = input("ENTER ADMIN PASSWORD: ")
            if p == 'admin123':
                print("LOGIN SUCCESSFUL")
                while True:
                    menu = input('''Add Medicine: AM, View Medicines: VM, Search Medicine: SM, Update Medicine: UM, Delete Medicine: DM, Record and Generate Bill: R&B, Exit: X :::''')
                    if menu.upper() == 'AM':
                        add_medicine()
                    elif menu.upper() == 'VM':
                        view_medicines()
                    elif menu.upper() == 'SM':
                        search_medicine()
                    elif menu.upper() == 'UM':
                        update_medicine()
                    elif menu.upper() == 'DM':
                        delete_medicine()
                    elif menu.upper() == 'R&B':
                        record_and_generate_bill()
                    elif menu.upper() == 'X':
                        break
                    else:
                        print("Wrong Input")
                        
        elif log.upper() == "S":
            print("Salesperson Interface")
            while True:
                menu = input('''Record and Generate Bill: R&B, Exit: X :::''')
                if menu.upper() == 'R'or  menu.upper()=="B" :
                    record_and_generate_bill()
                elif menu.upper() == 'X':
                    break
                else:
                    print("Wrong Input")
        
    


if __name__ == "__main__":
    main()
