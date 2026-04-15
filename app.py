import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(layout="wide", page_title="Chinook Analytics")

# ---------------- DB LOAD ----------------
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

# ---------------- SIDEBAR ----------------
st.sidebar.title("📊 메뉴")
page = st.sidebar.radio("페이지 선택", [
    "매출 Overview",
    "고객 & 지역 분석",
    "장르 & 상품 분석",
    "영업사원 성과",
    "고객 관리"
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

# ---------------- PAGE 1 ----------------
if page == "매출 Overview":
    st.title("📈 매출 Overview")

    total_sales = df["Total"].sum()
    total_orders = df["InvoiceId"].nunique()
    total_customers = df["CustomerId"].nunique()
    avg_order = df["Total"].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총매출", f"${total_sales:,.0f}")
    c2.metric("총주문수", total_orders)
    c3.metric("고객수", total_customers)
    c4.metric("평균주문액", f"${avg_order:,.2f}")

    yearly = df.groupby("Year")["Total"].sum().reset_index()
    st.plotly_chart(px.line(yearly, x="Year", y="Total", title="연도별 매출"), use_container_width=True)

    pivot = df.pivot_table(index="Year", columns="Month", values="Total", aggfunc="sum")
    st.plotly_chart(px.imshow(pivot, title="월별 매출"), use_container_width=True)

# ---------------- PAGE 2 ----------------
elif page == "고객 & 지역 분석":
    st.title("🌍 고객 & 지역 분석")

    top_country = df.groupby("BillingCountry")["Total"].sum().nlargest(10).reset_index()
    st.plotly_chart(px.bar(top_country, x="Total", y="BillingCountry",
                           orientation="h", title="국가별 매출 Top10"),
                    use_container_width=True)

    cust = df.groupby("BillingCountry").agg({
        "CustomerId": "nunique",
        "Total": "mean"
    }).reset_index()

    st.plotly_chart(px.scatter(cust, x="CustomerId", y="Total",
                               text="BillingCountry", title="고객수 vs 평균주문액"),
                    use_container_width=True)

    customer_total = df.groupby("CustomerId")["Total"].sum().reset_index()
    customer_total = customer_total.merge(customers, on="CustomerId")

    st.dataframe(customer_total.sort_values("Total", ascending=False))

# ---------------- PAGE 3 ----------------
elif page == "장르 & 상품 분석":
    st.title("🎵 장르 & 상품 분석")

    merged = invoice_items.merge(tracks, on="TrackId").merge(genres, on="GenreId")

    genre = merged.groupby("Name_y")["Quantity"].sum().reset_index()
    st.plotly_chart(px.pie(genre, values="Quantity", names="Name_y",
                           hole=0.4, title="장르별 판매량"),
                    use_container_width=True)

    merged2 = merged.merge(invoices, on="InvoiceId")
    trend = merged2.groupby(["Year", "Name_y"])["UnitPrice"].sum().reset_index()

    st.plotly_chart(px.area(trend, x="Year", y="UnitPrice",
                            color="Name_y", title="장르별 매출 트렌드"),
                    use_container_width=True)

    artist = merged.merge(albums, on="AlbumId").merge(artists, on="ArtistId")
    artist_sales = artist.groupby("Name")["UnitPrice"].sum().nlargest(15).reset_index()

    st.plotly_chart(px.bar(artist_sales, x="UnitPrice", y="Name",
                           orientation="h", title="Top 아티스트"),
                    use_container_width=True)

# ---------------- PAGE 4 ----------------
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

    st.plotly_chart(px.bar(perf, x="EmployeeId",
                           y=["Total","InvoiceId","CustomerId"],
                           barmode="group", title="성과 비교"),
                    use_container_width=True)

    trend = df_emp.groupby(["EmployeeId","Year"])["Total"].sum().reset_index()
    st.plotly_chart(px.line(trend, x="Year", y="Total",
                            color="EmployeeId", title="매출 추이"),
                    use_container_width=True)

# ---------------- ✅ PAGE 5 (CRUD) ----------------
elif page == "고객 관리":
    st.title("👤 고객 관리")

    conn = sqlite3.connect("chinook.db")

    # 조회
    st.subheader("📋 고객 목록")
    cust_df = pd.read_sql("SELECT * FROM customers", conn)
    st.dataframe(cust_df)

    st.divider()

    # 추가
    st.subheader("➕ 고객 추가")
    with st.form("add_customer"):
        fname = st.text_input("First Name")
        lname = st.text_input("Last Name")
        country = st.text_input("Country")
        email = st.text_input("Email")

        submit = st.form_submit_button("추가")

        if submit:
            try:
                conn.execute("""
                INSERT INTO customers (FirstName, LastName, Country, Email)
                VALUES (?, ?, ?, ?)
                """, (fname, lname, country, email))
                conn.commit()
                st.success("✅ 추가 완료")
            except Exception as e:
                st.error(e)

    st.divider()

    # 수정
    st.subheader("✏ 고객 수정")

    ids = cust_df["CustomerId"].tolist()
    cid = st.selectbox("고객 선택", ids)

    new_country = st.text_input("새 Country")
    new_email = st.text_input("새 Email")

    if st.button("수정"):
        try:
            conn.execute("""
            UPDATE customers
            SET Country=?, Email=?
            WHERE CustomerId=?
            """, (new_country, new_email, cid))
            conn.commit()
            st.success("✅ 수정 완료")
        except Exception as e:
            st.error(e)

    conn.close()
    


