# import csv
# import MySQLdb

# # Open the CSV File
# with open('./Datasets/accounts.csv', 'r') as file:
#     # Create a CSV reader Object
#     reader = csv.reader(file)
    
#     # Connection to MySQL Database
#     connection = MySQLdb.connect(host='localhost', user='root', password='root', db='accounts')
    
#     # Create a cursor object
#     cursor = connection.cursor()
    
#     # Create Table (Fixed SQL Syntax for MySQL)
#     # cursor.execute('''
#     #     CREATE TABLE IF NOT EXISTS accounts_data (
#     #         account VARCHAR(1000),
#     #         sector VARCHAR(1000),
#     #         year_established INT,
#     #         revenue FLOAT,
#     #         employees INT,
#     #         office_location VARCHAR(1000),
#     #         subsidiary_of VARCHAR(1000)
#     #     );
#     # ''')
    
#     for row in reader:
#         cursor.execute('INSERT INTO accounts_data(account, sector, year_established, revenue, employees, office_location, subsidiary_of) VALUES(%s, %s,%s,%s,%s,%s,%s)')
        

#     # Commit and close connection
#     connection.commit()
#     cursor.close()
#     connection.close()




import csv
import MySQLdb

# Open the CSV File
with open('./Datasets/accounts.csv', 'r') as file:
    reader = csv.reader(file)
    
    # Skip header row
    next(reader)

    # Connection to MySQL Database
    connection = MySQLdb.connect(host='localhost', user='root', password='root', db='accounts')
    
    # Create a cursor object
    cursor = connection.cursor()
    
    # Insert data row by row
    for row in reader:
        cursor.execute(
            'INSERT INTO accounts_data (account, sector, year_established, revenue, employees, office_location, subsidiary_of) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
            row  # <-- Pass the actual values from CSV
        )

    # Commit and close connection
    connection.commit()
    cursor.close()
    connection.close()
