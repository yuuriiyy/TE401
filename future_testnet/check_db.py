import sqlite3

# Connect to the SQLite database (replace 'your_database.db' with your actual database file)
conn = sqlite3.connect('funding_rate_database.db')
cursor = conn.cursor()
coin = 'BTC'
table_name = f'{coin}_funding_rate'

# Check if the table exists
cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
result = cursor.fetchone()

if result:
    # Table exists, fetch and display data
    cursor.execute(f'SELECT * FROM {table_name}')
    rows = cursor.fetchall()

    # Display the data
    for row in rows:
        print(row)
else:
    print(f'Table "{table_name}" does not exist in the database.')

# Close the cursor and connection
cursor.close()
conn.close()