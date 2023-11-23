import pandas as pd

def load_data():
    file_path = 'data/Data.xlsx'

    # Read data from sheets
    gl = pd.read_excel(file_path, sheet_name='GL')
    chart_of_accounts = pd.read_excel(file_path, sheet_name='Chart of Accounts')
    territory = pd.read_excel(file_path, sheet_name='Territory')

    # Join GL with Chart of Accounts and Territory
    gl = gl.merge(chart_of_accounts, on='Account_Key', how='left')
    gl = gl.merge(territory, on='Territory_Key', how='left')
    gl['Year'] = gl['Date'].dt.year 

    # Create Calendar Table
    min_date = gl['Date'].min()
    max_date = gl['Date'].max()
    calendar = pd.date_range(start=min_date, end=max_date).to_frame(index=False, name='Date')
    # (Include the data loading code here)
    return gl, chart_of_accounts, territory, calendar

def Total_FTP(GL):
    return GL['Amount'].sum()

def generate_pnl(gl):
    pnl = gl[gl['Report'] == 'Profit and Loss']
    
    pnl = pnl.pivot_table(
        values = 'Amount',
        index = ['Class', 'Sub_Class', 'Account', 'Sub_Account', 'Account_Key'],
        columns = 'Year',
        aggfunc = 'sum'
    ) 
    
    pnl = pnl.sort_values("Account_Key")

    pnl = pnl.style.format(thousands=",", precision=0)

    return pnl