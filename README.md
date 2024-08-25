# AccViz: Financial Data Visualization Tool

## Overview

AccViz is a Streamlit-based financial data visualization tool designed to provide clear, interactive insights into accounting data. It specializes in transforming complex financial data from Excel and other sources into comprehensive visual representations, facilitating better decision-making and data analysis in the field of finance and accounting.

## Business Requirements

- Data Import and Transformation: AccViz must efficiently import data from Excel files and perform necessary transformations such as joining tables, creating dimensions, measures, and calendar tables.
- Interactive Dashboards: The tool should offer a multi-tabbed interface with interactive dashboards for different financial aspects like income statements, cash flows, and balance sheets.
- Custom Visualizations: AccViz needs to provide custom visualization options to suit diverse business needs, including trends, summaries, and detailed analyses.
- User Accessibility: The visualizations should be accessible to users with varying levels of technical expertise, ensuring ease of use and understanding.
- Performance and Scalability: The tool must handle large datasets with optimal performance and be scalable to accommodate growing data sizes.

## Features

- Data import from Excel and other formats.
- Data transformations and additional table generation (e.g., calendar tables).
- Multi-tab Streamlit interface for categorized data visualization.
- Customizable charts and graphs for financial analysis.
- Interactive elements for user-driven data exploration.

## Installation and Setup

To set up AccViz, clone the repository and install the dependencies:

// bash code 
 ```
git clone https://github.com/azfarbkhr/AccViz.git
cd AccViz
py -m venv .rbEnv
source .rbEnv/Scripts/Activate
py -m pip install --upgrade pip
pip install -r requirements.txt
 ```
 
## Usage

To run the AccViz Streamlit app:

// bash code 
 ```
streamlit run app.py
 ```