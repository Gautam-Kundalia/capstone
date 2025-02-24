import csv
import MySQLdb

# Database Connection
connection = MySQLdb.connect(host='localhost', user='root', password='root', db='accounts')
cursor = connection.cursor()

# Open CSV File
with open('./Datasets/sales_pipeline.csv', 'r') as file:
    reader = csv.reader(file)
    
    # Skip the header row
    next(reader)

    # Insert data row by row
    for row in reader:
        # Handle empty date values by replacing '' with None (NULL in MySQL)
        engage_date = row[5] if row[5] else None
        close_date = row[6] if row[6] else None

        # Handle empty float values by replacing '' with None (NULL in MySQL)
        close_value = float(row[7]) if row[7] else None

        cursor.execute(
            'INSERT INTO sales_pipeline_data (opportunity_id, sales_agent, product, account, deal_stage, engage_date, close_date, close_value) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', 
            (row[0], row[1], row[2], row[3], row[4], engage_date, close_date, close_value)
        )

# Commit changes and close connection
connection.commit()
cursor.close()
connection.close()

print("Data inserted successfully into sales_pipeline_data table.")
