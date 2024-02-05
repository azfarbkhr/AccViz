import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def load_gl_transactions_data_from_excel():
    # read the data from the excel file
    file_path = 'data/Data.xlsx'
    gl = pd.read_excel(file_path, sheet_name='GL')
    coa = pd.read_excel(file_path, sheet_name='COA')
    trt = pd.read_excel(file_path, sheet_name='Territory')
    cln = pd.read_excel(file_path, sheet_name='Calendar')

    # join the data from all the sheets based on relevant keys
    cleaned_data = pd.merge(gl, coa, left_on='Account_key', right_on='Account_key', how='inner', suffixes=('', ''))
    cleaned_data = pd.merge(cleaned_data, trt, left_on='Territory_key', right_on='Territory_key', how='left')
    cleaned_data = pd.merge(cleaned_data, cln, left_on='Date', right_on='Date', how='left')
     
    cleaned_data['Year'] = cleaned_data['Year'].astype('str')

    return cleaned_data

def print_df_to_dashboard(df, st):
    df.index.names = [x.replace('Sorted', '') for x in df.index.names]

    df_styled = df.style.format(
                                na_rep='-',
                                formatter= lambda num:'{0:,.0f}'.format(num) if num>=0 else '({0:,.0f})'.format(abs(num)) ,
                            ).set_properties(**{'text-align': 'right'})

    st.write(df_styled.to_html(), unsafe_allow_html=True)


def generated_sorted_column(df, columns=[]):
    """
    Adds sorted columns to the DataFrame based on specified columns and sort keys.
    
    For each column in the provided list, the function creates a new column with 'Sorted'
    appended to the original column name. This new column contains a combination of a hidden sort key
    and the original column's value or a calculated name, formatted with HTML for display purposes.
    
    Parameters:
    - df (pd.DataFrame): The DataFrame to which the sorted columns will be added.
    - columns (list): A list of column names for which sorted columns will be generated.
    
    Returns:
    - pd.DataFrame: The modified DataFrame with added sorted columns.
    """    
    for column in columns:
        df[column + 'Sorted'] = '<span style="display:none;">' + df[column + '_SortKey'].astype('str').str.pad(2, side='left', fillchar='0') + ' - </span>' + np.where(df['isCalculated'] == 1, '<i>'+df['Calculated_' + column + '_Name'].astype('str')+'</i>', df[column]) 
    return df 


def apply_global_filters(df, year, region, country):
    return df[(df['Year'].isin(year) | (len(year) == 0)) & (df['Country'].isin(country) | (len(country) == 0))& (df['Region'].isin(region) | (len(region) == 0))]