import pandas as pd
import streamlit as st
from datetime import datetime

# Load data
file_path = r"./data/SISTEMA DE GESTÃO DE AVARIAS PREVENÇÃO - FRAGA MAIA.xlsm"
xls = pd.ExcelFile(file_path)

# Available sheets
sheets = ["Avarias Padaria", "Avarias Salgados", "Avarias Rotisseria"]

# Read data for the selected sheet
def load_data(sheet_name):
    df = pd.read_excel(xls, sheet_name=sheet_name, skiprows=1)
    
    # Clean and preprocess the data
    df['QTD'] = pd.to_numeric(df['QTD'], errors='coerce')
    df['VLR. UNIT. VENDA'] = df['VLR. UNIT. VENDA'].replace({'R\$ ': '', ',': '.'}, regex=True).astype(float)
    df['VLR. UNIT. CUSTO'] = df['VLR. UNIT. CUSTO'].replace({'R\$ ': '', ',': '.'}, regex=True).astype(float)
    df['VLR. TOT. VENDA'] = df['VLR. TOT. VENDA'].replace({'R\$ ': '', ',': '.'}, regex=True).astype(float)
    df['VLR. TOT. CUSTO'] = df['VLR. TOT. CUSTO'].replace({'R\$ ': '', ',': '.'}, regex=True).astype(float)
    
    # Drop rows with invalid or zero quantities
    df = df[(df['QTD'] > 0)]
    
    return df

# Process dates and weeks
def process_dates(df):
    df['DATA'] = pd.to_datetime(df['DATA'], format='%d/%m/%Y')
    df['week'] = df['DATA'].dt.isocalendar().week
    df['month'] = df['DATA'].dt.month
    return df

# Period filtering (Month, Week)
def filter_by_period(df, period_type, period_value):
    if period_type == 'Month':
        df = df[df['month'] == period_value]
    elif period_type == 'Week':
        df = df[df['week'] == period_value]
    return df

# Top 10 products by QTD
def top_10_by_qty(df):
    top_10_qty = df.groupby('DESCRIÇÃO').agg({'QTD': 'sum'}).sort_values(by='QTD', ascending=False).head(10)
    return top_10_qty

# Top 10 products by total sales value
def top_10_by_sales_value(df):
    df['VLR. TOT. VENDA'] = df['QTD'] * df['VLR. UNIT. VENDA']
    top_10_sales = df.groupby('DESCRIÇÃO').agg({'VLR. TOT. VENDA': 'sum'}).sort_values(by='VLR. TOT. VENDA', ascending=False).head(10)
    return top_10_sales

# Top 10 products by total cost value
def top_10_by_cost_value(df):
    df['VLR. TOT. CUSTO'] = df['QTD'] * df['VLR. UNIT. CUSTO']
    top_10_cost = df.groupby('DESCRIÇÃO').agg({'VLR. TOT. CUSTO': 'sum'}).sort_values(by='VLR. TOT. CUSTO', ascending=False).head(10)
    return top_10_cost

# Streamlit UI
def app():
    st.title("Dashboard de Avarias")
    
    # Sidebar filters
    sector = st.sidebar.selectbox('Escolha o setor', sheets)
    period_type = st.sidebar.selectbox('Escolha o período', ['Month', 'Week'])
    period_value = st.sidebar.number_input(f'Escolha o {period_type}', min_value=1, max_value=12, value=1)

    # Load and process data
    df = load_data(sector)
    df = process_dates(df)
    df_filtered = filter_by_period(df, period_type, period_value)
    
    # Display total sales and cost
    total_sales = df_filtered['VLR. TOT. VENDA'].sum()
    total_cost = df_filtered['VLR. TOT. CUSTO'].sum()
    
    st.markdown("### Total de Vendas e Custos")
    st.metric("Total de Vendas", f"R$ {total_sales:,.2f}")
    st.metric("Total de Custo", f"R$ {total_cost:,.2f}")
    
    # Top 10 products by QTD (lost quantity)
    top_10_qty = top_10_by_qty(df_filtered)
    
    if not top_10_qty.empty:
        st.markdown("### Top 10 Produtos Mais Perdidos (por QTD)")
        st.bar_chart(top_10_qty['QTD'])
    else:
        st.markdown("### No data available for QTD")
    
    # Top 10 products by total sales value
    top_10_sales = top_10_by_sales_value(df_filtered)
    
    if not top_10_sales.empty:
        st.markdown("### Top 10 Produtos Mais Perdidos (por VLR. TOT. VENDA)")
        st.bar_chart(top_10_sales['VLR. TOT. VENDA'])
    else:
        st.markdown("### No data available for Total Sales")
    
    # Top 10 products by total cost value
    top_10_cost = top_10_by_cost_value(df_filtered)
    
    if not top_10_cost.empty:
        st.markdown("### Top 10 Produtos Mais Perdidos (por VLR. TOT. CUSTO)")
        st.bar_chart(top_10_cost['VLR. TOT. CUSTO'])
    else:
        st.markdown("### No data available for Total Cost")
    
    # Display data table
    st.markdown("### Tabela de Avarias")
    df_filtered_display = df_filtered[['DATA', 'DESCRIÇÃO', 'QTD', 'VLR. UNIT. VENDA', 'VLR. UNIT. CUSTO', 'VLR. TOT. VENDA', 'VLR. TOT. CUSTO']]
# Apply the formatting for monetary values using .loc to avoid the warning
    df_filtered_display.loc[:, 'VLR. UNIT. VENDA'] = df_filtered_display['VLR. UNIT. VENDA'].apply(lambda x: f"R$ {x:,.2f}")
    df_filtered_display.loc[:, 'VLR. UNIT. CUSTO'] = df_filtered_display['VLR. UNIT. CUSTO'].apply(lambda x: f"R$ {x:,.2f}")
    df_filtered_display.loc[:, 'VLR. TOT. VENDA'] = df_filtered_display['VLR. TOT. VENDA'].apply(lambda x: f"R$ {x:,.2f}")
    df_filtered_display.loc[:, 'VLR. TOT. CUSTO'] = df_filtered_display['VLR. TOT. CUSTO'].apply(lambda x: f"R$ {x:,.2f}")
    
    st.dataframe(df_filtered_display)

if __name__ == "__main__":
    app()
