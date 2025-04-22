import csv
import MySQLdb

# Database Connection
connection = MySQLdb.connect(host='localhost', user='root', password='root', db='accounts')
cursor = connection.cursor()

# ✅ Create Table If Not Exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales_teams_data (
        sales_agent VARCHAR(255),
        manager VARCHAR(255),
        regional_office VARCHAR(255)
    );
''')

# Open CSV File
with open('./Datasets/sales_teams.csv', 'r') as file:
    reader = csv.reader(file)
    
    # Skip the header row
    next(reader)

    # Insert data row by row
    for row in reader:
        # Handle empty fields by replacing '' with None (NULL in MySQL)
        sales_agent = row[0] if row[0] else None
        manager = row[1] if row[1] else None
        regional_office = row[2] if row[2] else None

        cursor.execute(
            'INSERT INTO sales_teams_data (sales_agent, manager, regional_office) VALUES (%s, %s, %s)', 
            (sales_agent, manager, regional_office)
        )

# Commit changes and close connection
connection.commit()
cursor.close()
connection.close()

print("Data inserted successfully into sales_teams_data table.")
