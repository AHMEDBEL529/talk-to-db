import mysql.connector
from mysql.connector import Error

# Get the database host from user input
db_host = input("Enter the database host: ")
db_port = 3306
db_user = 'admin'
db_password = 'your-custom-password'  # Replace with your actual password

connection = None

try:
    print("Attempting to connect to the database...")
    connection = mysql.connector.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password
    )

    if connection.is_connected():
        print("Successfully connected to the database")

        cursor = connection.cursor()

        # Create a new database
        cursor.execute("CREATE DATABASE IF NOT EXISTS testdb")
        print("Database 'testdb' created or already exists")

        # Connect to the new database
        connection.database = 'testdb'

        # Create users table
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), age INT)")
        print("Table 'users' created or already exists")

        # Insert data into the users table
        cursor.execute("INSERT INTO users (name, age) VALUES "
                       "('Alice', 30), ('Bob', 25), ('Charlie', 35), ('David', 20), ('Eva', 40)")
        connection.commit()
        print("Inserted data into 'users' table")

        # Create orders table
        cursor.execute("CREATE TABLE IF NOT EXISTS orders (order_id INT AUTO_INCREMENT PRIMARY KEY, user_id INT, amount DECIMAL(10, 2), order_date DATE, "
                       "FOREIGN KEY (user_id) REFERENCES users(id))")
        print("Table 'orders' created or already exists")

        # Insert data into the orders table
        cursor.execute("INSERT INTO orders (user_id, amount, order_date) VALUES "
                       "(1, 100.50, '2023-01-15'), "
                       "(2, 200.75, '2023-02-20'), "
                       "(3, 150.00, '2023-03-25'), "
                       "(1, 250.00, '2023-04-10'), "
                       "(4, 300.40, '2023-05-05')")
        connection.commit()
        print("Inserted data into 'orders' table")

        # Retrieve data from the tables using a join query
        cursor.execute("SELECT users.name, orders.amount, orders.order_date FROM users JOIN orders ON users.id = orders.user_id")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Name: {row[0]}, Amount: {row[1]}, Order Date: {row[2]}")

except Error as e:
    print("Error while connecting to MySQL:", e)

finally:
    if connection and connection.is_connected():
        connection.close()
        print("MySQL connection is closed")
