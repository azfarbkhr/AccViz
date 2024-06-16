import streamlit as st
import pandas as pd
import numpy as np

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


amount_formatter = lambda num:'{0:,.2f}'.format(num) if num>=0 else '({0:,.2f})'.format(abs(num))
percent_formatter = lambda num: '{0:,.2f}%'.format(num * 100) if num >= 0 else '({0:,.2f}%)'.format(abs(num) * 100)

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

def print_df_to_dashboard(df, st=st, formatter=amount_formatter):
    if len(df.index.names) > 0:
        df.index.names = [x.replace('Sorted', '') if x else None for x in df.index.names]

    df_styled = df.style.format(
                                na_rep='-',
                                formatter= formatter,
                            ).set_properties(**{'text-align': 'right'})

    st.write(df_styled.to_html(), unsafe_allow_html=True)
    return df_styled


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


def slice_df_by_name(df, index_level, slice_value):
    """
    Filters a DataFrame by cleaning a specified level of its multi-index and then slicing by a given value.
    
    Parameters:
    - df: The pandas DataFrame with a multi-index.
    - index_level: The name (or integer position) of the index level to clean.
    - slice_value: The value to slice by after cleaning the index level.
    
    Returns:
    - A DataFrame filtered based on the specified slice_value, after cleaning the specified index level.
    """
    # Extract the specified level of the index and clean it
    df_index = df.index.get_level_values(index_level)
    cleaned_index = df_index.str.replace('<span style="display:none;">\d+ - </span>', '', regex=True)
    cleaned_index = cleaned_index.str.replace('<i>', '')
    cleaned_index = cleaned_index.str.replace('</i>', '')
    
    # Identify keys after cleaning that match the specified slice_value
    matches = cleaned_index == slice_value
    
    # Convert the boolean array to the original index keys
    keys_to_search = df.index[matches]
    
    # Use the filtered keys to access rows in the original DataFrame
    result =  df.loc[keys_to_search]

    result = result.sum().to_frame().T

    result = result.reset_index(drop=True)

    return result

def filter_values(df, filter_maps={}):
    for column, filter in filter_maps.items():
        df = df[(df[column].isin(filter))]
    
    return df 

def sum_filtered_values(df, filter_maps={}, amount_column_name="Amount"):
    df = filter_values(df, filter_maps)
    return df['Amount'].sum()

def stylize(value, style='shortened_currency'):
    if style == 'currency':
        formatted_value = "${:,}".format(value)
    elif style == 'shortened_currency':
        if value < 1000:
            formatted_value = "${:,}".format(value)
        elif value < 1000000:
            value = value / 1000
            formatted_value = "${:,.2f}k".format(value)
        elif value < 1000000000:
            value = value / 1000000
            formatted_value = "${:,.2f}M".format(value)
        else:
            value = value / 1000000000
            formatted_value = "${:,.2f}B".format(value)
        return formatted_value        
    return formatted_value




def plot_st_chart(comparison_by, dataframe, chart_type, y_column_name):
    """
    Plots a comparison chart using Plotly based on the specified parameters.

    Parameters:
    - comparison_by: List of column names to combine for the x-axis.
    - dataframe: The pandas DataFrame containing the data to plot.
    - chart_type: Type of chart to plot (e.g., 'bar', 'line').
    - y_column_name: The name of the column to use for the y-axis.
    """
    # Combine the specified columns for the x-axis
    
    dataframe = dataframe.T.reset_index()
    

    x_axis_label = ' - '.join(comparison_by)
    dataframe[x_axis_label] = dataframe[comparison_by].astype(str).agg(' - '.join, axis=1)
    
    # Ensure the y-axis column is in the correct format (e.g., float)
    dataframe[y_column_name] = dataframe[y_column_name].astype(float)
    
    # Select the plotting function based on the chart_type
    if chart_type == 'bar':
        fig = px.bar(dataframe, x=x_axis_label, y=y_column_name, category_orders={x_axis_label: sorted(dataframe[x_axis_label].unique())})
    elif chart_type == 'line':
        fig = px.line(dataframe, x=x_axis_label, y=y_column_name, category_orders={x_axis_label: sorted(dataframe[x_axis_label].unique())})
    else:
        raise ValueError("Unsupported chart type provided.")
    
    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)


def plot_comparison_chart_with_traces(comparison_by, dataframe, y_column_name):
    """
    Creates a Plotly figure with a new trace for each unique combination of comparison categories,
    excluding 'Year' which is used for the x-axis.
    
    Parameters:
    - comparison_by: List of column names for comparison, 'Year' should be at the end.
    - dataframe: The pandas DataFrame containing the data to plot.
    - y_column_name: The name of the column to use for the y-axis values.
    """
    dataframe = dataframe.T.reset_index()
    # Ensure 'Year' is at the end and remove it for trace grouping
    assert comparison_by[-1] == 'Year', "'Year' must be the last item in comparison_by"
    group_by_columns = comparison_by[:-1]  # Exclude 'Year'
    
    # Create a Plotly figure
    fig = go.Figure()
    
    if group_by_columns:
        # Group by the specified columns (excluding 'Year')
        for group, df_group in dataframe.groupby(group_by_columns):
            group_label = ' - '.join(map(str, group)) if isinstance(group, tuple) else str(group)
            # For each group, add a trace
            fig.add_trace(go.Bar(
                x=df_group['Year'],  
                y=df_group[y_column_name],
                name=group_label, 
                text=df_group[y_column_name]
            ))
    else:
        fig.add_trace(go.Bar(
            x=dataframe['Year'],
            y=dataframe[y_column_name],
            name=y_column_name,
            text=dataframe[y_column_name]
        ))
    
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
    # Update layout if needed (e.g., for barmode, tickangle)
    fig.update_layout(barmode='group', xaxis_tickangle=-45, yaxis={'title': y_column_name})
    
    # Display the plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)