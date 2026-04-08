import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(layout="wide", page_title="Chinook Analytics")

@st.cache_data
def load_data():
    conn = sqlite3.connect("chinook.db")

    invoices = pd.read_sql("SELECT * FROM invoices", conn)
    customers = pd.read_sql("SELECT * FROM customers", conn)
    invoice_items = pd.read_sql("SELECT * FROM invoice_items", conn)
    tracks = pd.read_sql("SELECT * FROM tracks", conn)
    genres = pd.read_sql("SELECT * FROM genres", conn)
    albums = pd.read_sql("SELECT * FROM albums", conn)
    artists = pd.read_sql("SELECT * FROM artists", conn)
    employees = pd.read_sql("SELECT * FROM employees", conn)

    conn.close()

    invoices["InvoiceDate"] = pd.to_datetime(invoices["InvoiceDate"])
    invoices["Year"] = invoices["InvoiceDate"].dt.year
    invoices["Month"] = invoices["InvoiceDate"].dt.month

    return invoices, customers, invoice_items, tracks, genres, albums, artists, employees

with st.spinner("데이터 로딩 중..."):
    invoices, customers, invoice_items, tracks, genres, albums, artists, employees = load_data()

# ---------------- Sidebar ----------------
st.sidebar.title("📊 메뉴")
page = st.sidebar.radio("페이지 선택", [
    "매출 Overview",
    "고객 & 지역 분석",
    "장르 & 상품 분석",
    "영업사원 성과"
])

years = sorted(invoices["Year"].unique())
year_range = st.sidebar.slider("연도 선택", min(years), max(years), (min(years), max(years)))

countries = st.sidebar.multiselect(
    "국가 선택",
    options=invoices["BillingCountry"].unique(),
    default=invoices["BillingCountry"].unique()
)

df = invoices[
    (invoices["Year"].between(year_range[0], year_range[1])) &
    (invoices["BillingCountry"].isin(countries))
]

# ---------------- Page 1 ----------------
if page == "매출 Overview":
    st.title("📈 매출 Overview")

    total_sales = df["Total"].sum()
    total_orders = df["InvoiceId"].nunique()
    total_customers = df["CustomerId"].nunique()
    avg_order = df["Total"].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총매출", f"${total_sales:,.0f}")
    col2.metric("총주문수", total_orders)
    col3.metric("고객수", total_customers)
    col4.metric("평균주문액", f"${avg_order:,.2f}")

    yearly = df.groupby("Year")["Total"].sum().reset_index()
    fig = px.line(yearly, x="Year", y="Total", title="연도별 매출")
    st.plotly_chart(fig, use_container_width=True)

    pivot = df.pivot_table(index="Year", columns="Month", values="Total", aggfunc="sum")
    fig2 = px.imshow(pivot, title="월별 매출 히트맵")
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- Page 2 ----------------
elif page == "고객 & 지역 분석":
    st.title("🌍 고객 & 지역 분석")

    country_sales = df.groupby("BillingCountry")["Total"].sum().nlargest(10).reset_index()
    fig = px.bar(country_sales, x="Total", y="BillingCountry", orientation="h", title="국가별 매출 Top10")
    st.plotly_chart(fig, use_container_width=True)

    cust = df.groupby("BillingCountry").agg({
        "CustomerId": "nunique",
        "Total": "mean"
    }).reset_index()

    fig2 = px.scatter(cust, x="CustomerId", y="Total", text="BillingCountry",
                      title="고객수 vs 평균 주문액")
    st.plotly_chart(fig2, use_container_width=True)

    customer_total = df.groupby("CustomerId")["Total"].sum().reset_index()
    customer_total = customer_total.merge(customers, on="CustomerId")

    st.dataframe(customer_total.sort_values("Total", ascending=False))

# ---------------- Page 3 ----------------
elif page == "장르 & 상품 분석":
    st.title("🎵 장르 & 상품 분석")

    merged = invoice_items.merge(tracks, on="TrackId").merge(genres, on="GenreId")

    genre_sales = merged.groupby("Name_y")["Quantity"].sum().reset_index()
    fig = px.pie(genre_sales, values="Quantity", names="Name_y", hole=0.4,
                 title="장르별 판매량")
    st.plotly_chart(fig, use_container_width=True)

    merged2 = merged.merge(invoices, on="InvoiceId")
    trend = merged2.groupby(["Year", "Name_y"])["UnitPrice"].sum().reset_index()

    fig2 = px.area(trend, x="Year", y="UnitPrice", color="Name_y",
                   title="장르별 매출 트렌드")
    st.plotly_chart(fig2, use_container_width=True)

    artist = merged.merge(albums, on="AlbumId").merge(artists, on="ArtistId")
    artist_sales = artist.groupby("Name")["UnitPrice"].sum().nlargest(15).reset_index()

    fig3 = px.bar(artist_sales, x="UnitPrice", y="Name", orientation="h",
                  title="인기 아티스트 Top15")
    st.plotly_chart(fig3, use_container_width=True)

# ---------------- Page 4 ----------------
elif page == "영업사원 성과":
    st.title("👩‍💼 영업사원 성과")

    df_emp = df.merge(customers, on="CustomerId").merge(
        employees, left_on="SupportRepId", right_on="EmployeeId"
    )

    perf = df_emp.groupby("EmployeeId").agg({
        "Total": "sum",
        "InvoiceId": "nunique",
        "CustomerId": "nunique"
    }).reset_index()

    fig = px.bar(perf, x="EmployeeId", y=["Total", "InvoiceId", "CustomerId"],
                 barmode="group", title="담당자 성과")
    st.plotly_chart(fig, use_container_width=True)

    trend = df_emp.groupby(["EmployeeId", "Year"])["Total"].sum().reset_index()
    fig2 = px.line(trend, x="Year", y="Total", color="EmployeeId",
                   title="담당자 매출 추이")
    st.plotly_chart(fig2, use_container_width=True)

    country = df_emp.groupby(["EmployeeId", "BillingCountry"])["Total"].sum().reset_index()
    fig3 = px.bar(country, x="EmployeeId", y="Total", color="BillingCountry",
                  title="담당자별 국가 분포")
    st.plotly_chart(fig3, use_container_width=True)
