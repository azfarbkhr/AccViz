import pandas as pd
import streamlit as st
import numpy as np
from utils import load_gl_transactions_data_from_excel, print_df_to_dashboard, generated_sorted_column, apply_global_filters

# Set Streamlit page configuration
st.set_page_config(page_title='Financial Dashboard', page_icon=':bar_chart:', layout='wide', initial_sidebar_state='auto')


# Main dashboard title
st.title('Financial Dashboard')
st.write('This dashboard shows the financial performance of ABC Company')

# Load general ledger transactions data
GL_Master = load_gl_transactions_data_from_excel()

# Sidebar setup for comparison selection
st.sidebar.subheader('Comparison')
comparison_by = st.sidebar.multiselect('Comparison by', ['Region', 'Country'])
comparison_by.append('Year')  # Ensure 'Year' is always included in the comparison

# Sidebar setup for level of detail selection
st.sidebar.subheader('Level of Detail')
level_of_detail = st.sidebar.multiselect('Level of Detail', ['Class', 'SubClass', 'SubClass2', 'Account'])
if not level_of_detail:
    level_of_detail = ['Class', 'SubClass', 'SubClass2']
level_of_detail_sorted = sorted(level_of_detail, key=lambda x: ['Class', 'SubClass', 'SubClass2', 'Account'].index(x))
level_of_detail_sorted = [x + 'Sorted' for x in level_of_detail_sorted]

# Sidebar setup for data filtering
st.sidebar.subheader('Filter')
year = st.sidebar.multiselect('Year', GL_Master['Year'].unique())
region = st.sidebar.multiselect('Region', GL_Master['Region'].unique())
country = st.sidebar.multiselect('Country', GL_Master['Country'].unique())

filtered_values = (year, region, country)

# Sidebar footer
st.sidebar.write("----\n`Prepared by S. Azfar, ACCA` 🎈🎈🎈")

profit_and_loss_tab, balance_sheet_tab, cash_flow_tab, transaction_details_tab = st.tabs(["P&L Report", "Balance Sheet", "Cash Flow Statement", "Transaction Details"])

with transaction_details_tab:
    # Filter data based on sidebar selections
    Filtered_GL_Master = apply_global_filters(GL_Master, *filtered_values)    
    st.dataframe(Filtered_GL_Master)

with profit_and_loss_tab:
    # Filter data based on sidebar selections
    Filtered_GL_Master = apply_global_filters(GL_Master, *filtered_values)

    # Load and merge P&L structure, then sort and display the P&L report
    pnl_structure = pd.read_excel('data/Data.xlsx', sheet_name='PnL Structure')
    PnL_GL_Master = pd.merge(Filtered_GL_Master, pnl_structure, left_on='Account_key', right_on='Account_key', how='inner', suffixes=('', ''))
    
    # Generating sorted columns based on the sort key in the structure 
    PnL_GL_Master = generated_sorted_column(PnL_GL_Master, ['Account', 'SubClass', 'SubClass2', 'Class'])
    
    income_statement_df = pd.pivot_table(PnL_GL_Master, index= level_of_detail_sorted, values='Amount', columns=comparison_by, 
                                aggfunc='sum', margins=True, margins_name='Total'
                            ).sort_values(by=level_of_detail_sorted, ascending=True)
    
    # removing the grand total row at the bottom
    income_statement_df = income_statement_df.iloc[:-1, :]

    print_df_to_dashboard(income_statement_df, st)

with balance_sheet_tab:
    # Load balance sheet structure from an Excel file
    bs_structure = pd.read_excel('data/Data.xlsx', sheet_name='BS Structure')
    
    # Merge the loaded balance sheet structure with the GL_Master data
    BS_GL_Master = pd.merge(GL_Master, bs_structure, left_on='Account_key', right_on='Account_key', how='inner', suffixes=('', ''))

    # generated sorted columns to ensure rows appear in correct order 
    BS_GL_Master = generated_sorted_column(BS_GL_Master, ['Account', 'SubClass', 'SubClass2', 'Class'])

    # generate a simple FTP balance
    BS_GL_Group2 = BS_GL_Master.groupby(['ClassSorted', 'SubClassSorted', 'SubClass2Sorted', 'AccountSorted', 'Region', 'Country', 'Year']).agg({'Amount': 'sum'}).reset_index()
    
    # move the year to columns 
    crosstab_result = pd.crosstab(
        index=[BS_GL_Group2['ClassSorted'], BS_GL_Group2['SubClassSorted'], BS_GL_Group2['SubClass2Sorted'], BS_GL_Group2['AccountSorted'], BS_GL_Group2['Region'], BS_GL_Group2['Country'],],
        columns=BS_GL_Group2['Year'], values=BS_GL_Group2['Amount'], aggfunc='sum')

    # generate a cumsum to attain a balance for year 
    balance_summary = crosstab_result.cumsum(axis=1)
    balance_summary = balance_summary.stack().reset_index(name='CumulativeSum')

    # apply global filters 
    Filtered_Balance_Summary = apply_global_filters(balance_summary, *filtered_values)

    # prepare the balance sheet report 
    BS_GL_Group3 = pd.pivot_table(Filtered_Balance_Summary, index=level_of_detail_sorted, values='CumulativeSum', columns=comparison_by, aggfunc='sum')

    print_df_to_dashboard(BS_GL_Group3, st)
    # a
with cash_flow_tab:
    cf_structure = pd.read_excel('data/Data.xlsx', sheet_name='CF Structure')
    CF_GL_Master = pd.merge(GL_Master, cf_structure, left_on='Account_key', right_on='Account_key', how='inner', suffixes=('', '')) 
    CF_GL_Master = generated_sorted_column(CF_GL_Master, ['SubType'])
    CF_GL_Master['Sign'] = np.where(CF_GL_Master['Amount'] > 0, 'Positive', 'Negative') 

    cash_flow_df = pd.pivot_table(CF_GL_Master, index= ['Type','SubTypeSorted','ValueType', 'Region', 'Country', 'Sign', 'Account'], values='Amount', columns='Year', aggfunc='sum'
                                  ).sort_values(by=['SubTypeSorted'], ascending=True)
    
    cash_flow_df = cash_flow_df.reset_index()      

    years_in_data = GL_Master['Year'].unique()

    transformed_cf_df = pd.DataFrame()
    for _, row in cash_flow_df.iterrows():
        prv_year_value = 0
        for yr in years_in_data:
            current_year_value = 0

            if row['ValueType'] == 'All_FTP':
                current_year_value += row[yr]
            elif row['ValueType'] == 'All_FTP_CS':
                current_year_value -= row[yr]
            elif row['ValueType'] == 'All_FTP_Negative' and row['Sign'] == 'Negative':
                current_year_value += row[yr]
            elif row['ValueType'] == 'All_FTP_Positive_CS' and row['Sign'] == 'Positive':
                current_year_value -= row[yr]
            elif row['ValueType'] == 'All_FTP_Negative_CS' and row['Sign'] == 'Negative':
                current_year_value -= row[yr]
            elif row['ValueType'] == 'All_FTP_Positive' and row['Sign'] == 'Positive':
                current_year_value += row[yr]
            elif row['ValueType'] == 'Closing_balance':
                current_year_value += row[yr] + prv_year_value
                prv_year_value = current_year_value
            elif row['ValueType'] == 'Opening_balance':
                current_year_value = prv_year_value
                prv_year_value = row[yr] + prv_year_value
            
            row[yr] = current_year_value
        transformed_cf_df = pd.concat([transformed_cf_df, row], axis=1)
    
    transformed_cf_df = transformed_cf_df.transpose() 
    transformed_cf_df = pd.melt(transformed_cf_df, id_vars=['Type','SubTypeSorted','ValueType', 'Region', 'Country', 'Sign', 'Account'], var_name='Year', value_name='Amount')
    
    Filtered_CF = apply_global_filters(transformed_cf_df, *filtered_values)
    
    Filtered_CF = pd.pivot_table(Filtered_CF, index= ['Type','SubTypeSorted'], values= ['Amount'], columns=comparison_by, aggfunc='sum'
                                 ).sort_values(by=['SubTypeSorted'], ascending=True)

    print_df_to_dashboard(Filtered_CF, st)