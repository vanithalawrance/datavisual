# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Retail Dashboard", layout="wide")

# Loading Data
@st.cache_data
def load_data(path="sales.csv"):
    df = pd.read_csv(path, parse_dates=["Order Date"])
    # derived columns for convenience
    df["Order Month"] = df["Order Date"].dt.to_period("M").dt.to_timestamp()
    return df

df = load_data()
st.write("Data loaded:", df.shape)
st.write(df.head())

# Sidebar Filters

st.sidebar.header("Filters")
min_date = df["Order Date"].min().date()
max_date = df["Order Date"].max().date()
date_range = st.sidebar.date_input("Order Date range", value=[min_date, max_date], min_value=min_date, max_value=max_date)
regions = st.sidebar.multiselect("Region", options=df["Region"].unique(), default=df["Region"].unique())
categories = st.sidebar.multiselect("Category", options=df["Category"].unique(), default=df["Category"].unique())

# apply filters
mask = (
    (df["Order Date"].dt.date >= date_range[0]) &
    (df["Order Date"].dt.date <= date_range[1]) &
    (df["Region"].isin(regions)) &
    (df["Category"].isin(categories))
)
filtered = df[mask]

# KPI

st.title("Retail Sales Dashboard — Demo")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Sales", f"${filtered['Sales'].sum():,.2f}")
c2.metric("Total Profit", f"${filtered['Profit'].sum():,.2f}")
c3.metric("Avg Order Value", f"${filtered['Sales'].mean():,.2f}")
c4.metric("Orders", f"{filtered.shape[0]}")


# Time Series

monthly = filtered.groupby("Order Month").agg({"Sales":"sum","Profit":"sum"}).reset_index()
fig = go.Figure()
fig.add_trace(go.Bar(x=monthly["Order Month"], y=monthly["Sales"], name="Sales"))
fig.add_trace(go.Line(x=monthly["Order Month"], y=monthly["Profit"], name="Profit", yaxis="y2"))
fig.update_layout(
    title="Monthly Sales and Profit",
    xaxis_title="Month",
    yaxis_title="Sales",
    yaxis2=dict(title="Profit", overlaying="y", side="right")
)
st.plotly_chart(fig, use_container_width=True)

# Categorical charts

# Bar chart (Region)
region_sales = filtered.groupby("Region")["Sales"].sum().reset_index()
st.subheader("Sales by Region")
st.plotly_chart(px.bar(region_sales, x="Region", y="Sales", title="Sales by Region"), use_container_width=True)

# Pie (Category)
cat_sales = filtered.groupby("Category")["Sales"].sum().reset_index()
st.subheader("Sales Share by Category")
st.plotly_chart(px.pie(cat_sales, names="Category", values="Sales", title="Category Share"), use_container_width=True)

# Treemap (Region > Category)
treemap = filtered.groupby(["Region","Category"])["Sales"].sum().reset_index()
st.subheader("Treemap — Region and Category")
st.plotly_chart(px.treemap(treemap, path=["Region","Category"], values="Sales", title="Sales Treemap"), use_container_width=True)

#Distribution and Relationships

# Histogram of Sales
st.subheader("Sales Distribution")
st.plotly_chart(px.histogram(filtered, x="Sales", nbins=30, title="Sales Distribution"), use_container_width=True)

# Scatter: Sales vs Profit
st.subheader("Sales vs Profit")
st.plotly_chart(px.scatter(filtered, x="Sales", y="Profit", color="Category", size="Quantity", hover_data=["Order ID","Region"], title="Sales vs Profit"), use_container_width=True)

# Box plot: Sales by Category
st.subheader("Sales dispersion by Category")
st.plotly_chart(px.box(filtered, x="Category", y="Sales", points="all", title="Box plot - Sales by Category"), use_container_width=True)

# Violin: Profit by Category
st.subheader("Profit distribution by Category")
st.plotly_chart(px.violin(filtered, x="Category", y="Profit", box=True, points="all", title="Violin - Profit by Category"), use_container_width=True)

# Correlation heatmap
num_cols = ["Sales","Profit","Quantity"]
if not filtered[num_cols].empty:
    corr = filtered[num_cols].corr()
    st.subheader("Correlation Matrix")
    st.plotly_chart(px.imshow(corr, text_auto=True, title="Correlation"), use_container_width=True)
    
# Area and Line charts

st.subheader("Cumulative Sales by Category over Months")
area = filtered.groupby(["Order Month","Category"])["Sales"].sum().reset_index()
st.plotly_chart(px.area(area, x="Order Month", y="Sales", color="Category", title="Area: Sales by Category Over Time"), use_container_width=True)

st.subheader("Monthly Average Order Value (AOV)")
aov = filtered.groupby("Order Month")["Sales"].mean().reset_index()
st.plotly_chart(px.line(aov, x="Order Month", y="Sales", markers=True, title="Monthly AOV"), use_container_width=True)

# Download

st.subheader("Download filtered data")
csv = filtered.to_csv(index=False)
st.download_button("Download CSV", data=csv, file_name="filtered_sales.csv", mime="text/csv")
