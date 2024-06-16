import pandas as pd
import streamlit as st
import numpy as np
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.bottom_container import bottom
from streamlit_extras.dataframe_explorer import dataframe_explorer

from utils import load_gl_transactions_data_from_excel 
from utils import print_df_to_dashboard
from utils import generated_sorted_column 
from utils import apply_global_filters, sum_filtered_values, filter_df_by_index_values 
from utils import stylize
from utils import plot_st_chart, plot_comparison_chart_with_traces
from utils import percent_formatter_v2

# Set Streamlit page configuration
st.set_page_config(page_title='Financial Dashboard', page_icon=':bar_chart:', layout='wide', initial_sidebar_state='auto')
st.markdown(
    """
        <style>
            .appview-container .main .block-container {{
                padding-top: {padding_top}rem;
                padding-bottom: {padding_bottom}rem;
                }}

        </style>""".format(
        padding_top=1, padding_bottom=1
    ),
    unsafe_allow_html=True,
)
with bottom():
    st.write("----\n`Prepared by S. Azfar, ACCA` 🎈🎈🎈")    

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

profit_and_loss_tab, balance_sheet_tab, cash_flow_tab, transaction_details_tab, soce_tab = st.tabs(["P&L Report", "Balance Sheet", "Cash Flow Statement", "Transaction Details", "Changes in Equity Statement"])

with transaction_details_tab:
    # Filter data based on sidebar selections
    Filtered_GL_Master = apply_global_filters(GL_Master, *filtered_values)    
    st.dataframe(dataframe_explorer(Filtered_GL_Master, case=False))


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

    # calculating the KPIs
    sales_ttd = apply_global_filters(GL_Master, region=region, country=country, year=[])
    sales_ttd = sum_filtered_values(sales_ttd, filter_maps={"SubClass": ['Sales']})

    current_year = max(year or ["2020"])
    prv_year = str(int(current_year) - 1)  

    sales_ftp = apply_global_filters(GL_Master, region=region, country=country, year=[current_year])
    sales_ftp = sum_filtered_values(sales_ftp, filter_maps={"SubClass": ['Sales']})
    
    prv_sales_ftp = apply_global_filters(GL_Master, region=region, country=country, year=[prv_year])
    prv_sales_ftp = sum_filtered_values(prv_sales_ftp, filter_maps={"SubClass": ['Sales']})
    diff_sales_ftp = sales_ftp - prv_sales_ftp

    
    col1, col2 = profit_and_loss_tab.columns([1, 5])
    col1.write("### Ratio Analysis")
    with col1.container(height=700):
        st.metric("Total Sales TTD", stylize(sales_ttd))
        st.metric("Total Sales FTP", stylize(sales_ftp), delta=stylize(diff_sales_ftp))
        
    style_metric_cards(background_color = "#fff", border_left_color="#f75")

    col2.write("### Report")
    with col2.container():
        print_df_to_dashboard(income_statement_df)
        income_statement_df = income_statement_df.iloc[:, :-1] # this is done to remove the total at column level as it is not useful in this report. 
    
    with st.expander("### More Reports",  expanded=True):
        income_statement_df_for_analysis = pd.pivot_table(PnL_GL_Master, index= ['ClassSorted', 'SubClassSorted', 'SubClass2Sorted'], values='Amount', columns=['Year'], 
                                aggfunc='sum'
                            ).sort_values(by=['ClassSorted', 'SubClassSorted', 'SubClass2Sorted'], ascending=True)

        if len(income_statement_df_for_analysis.index.names) > 0:
            income_statement_df_for_analysis.index.names = [x.replace('Sorted', '') if x else None for x in income_statement_df_for_analysis.index.names]    
    

        gross_profit_df = filter_df_by_index_values(income_statement_df_for_analysis, 'Class', ['Gross Profit'])
        sales_df = filter_df_by_index_values(income_statement_df_for_analysis, 'SubClass', ['Sales'])
        net_profit_df = filter_df_by_index_values(income_statement_df_for_analysis, 'Class', ['Net Profit'])
        ebitda_df = filter_df_by_index_values(income_statement_df_for_analysis, 'SubClass', ['Sales', 'Cost of Sales', 'Operating Expenses'])

        st.write("#### Gross Profit Margin Over the Period")
        gp_margin = gross_profit_df / sales_df * 100 
        gp_margin.index = ['Gross Profit %']
        print_df_to_dashboard(gp_margin, formatter=percent_formatter_v2)

        st.write("#### Net Profit Margin Over the Period")
        np_margin = net_profit_df / sales_df * 100 
        np_margin.index = ['Net Profit %']
        print_df_to_dashboard(np_margin, formatter=percent_formatter_v2)

        st.write(("#### EBITDA Over the Period"))
        ebitda_df.index = ['EBITDA']
        print_df_to_dashboard(ebitda_df)

        # plot_st_chart(comparison_by, gp_margin, 'bar', 'Gross Profit %')

        # # np margin
        # np_margin = net_profit_df / sales_df * 100 
        # gp_margin.index = ['Net Profit %']    
        # plot_comparison_chart_with_traces(comparison_by, gp_margin, 'Net Profit %')



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


