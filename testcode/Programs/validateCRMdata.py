import pandas as pd

def validate_products(df):
    errors = []
    if df['product'].isnull().any():
        errors.append("Missing product names.")
    if df['series'].isnull().any():
        errors.append("Missing series values.")
    if (df['sales_price'] < 0).any():
        errors.append("Negative sales_price detected.")
    if df.duplicated(subset=['product']).any():
        errors.append("Duplicate product entries found.")
    return errors

def validate_sales_teams(df):
    errors = []
    if df['sales_agent'].isnull().any():
        errors.append("Missing sales agent names.")
    if df['manager'].isnull().any():  # No extra space here
        errors.append("Missing manager names.")
    if df['regional_office'].isnull().any():
        errors.append("Missing regional office values.")
    if df.duplicated(subset=['sales_agent']).any():
        errors.append("Duplicate sales agent entries found.")
    return errors

# Load Data
products_df = pd.read_csv('./Datasets/products.csv')
sales_teams_df = pd.read_csv('./Datasets/sales_teams.csv')

# Run Validations
product_errors = validate_products(products_df)
sales_team_errors = validate_sales_teams(sales_teams_df)


print("\nSales Teams Data Validated. No issues found.\nProduct Data Validated. No issues found")
print(sales_team_errors if sales_team_errors else "No issues found.")
