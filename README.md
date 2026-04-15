# 🎵 Chinook Data Analytics Dashboard ## 📌 Project Overview This project is a Streamlit-based data analytics dashboard using the Chinook SQLite database. It analyzes sales, customers, genres, and employee performance, and also includes customer management (CRUD functionality). --- ## 🚀 Features - Sales Overview Dashboard - Customer & Country Analysis - Genre & Product Analysis - Employee Performance Analysis - Customer Management (View, Add, Update) --- ## 📊 Business Insights ### 1. Revenue by Country The United States generates the highest revenue among all countries. This indicates that the U.S. is the primary market and should be a key focus for business strategy. ### 2. Genre Performance Certain genres outperform others in sales. In particular, popular genres consistently generate higher revenue, reflecting strong customer preferences. ### 3. Customer Segmentation A small number of customers contribute a large portion of total revenue. This shows the existence of high-value (VIP) customers. ### 4. Sales Trend Sales remain relatively stable over time with some fluctuations. This indicates consistent demand and stable business performance. --- ## 🗄️ SQL Query Explanation ### 1) SELECT ```sql SELECT * FROM customers;
Retrieve customer data from the database.

2) INSERT
sql


INSERT INTO customers (FirstName, LastName, Country, Email)
VALUES ('John', 'Doe', 'USA', 'john@example.com');
Add a new customer to the database.

3) UPDATE
sql


UPDATE customers
SET Country = 'Canada', Email = 'new@email.com'
WHERE CustomerId = 1;
Update existing customer information.

4) GROUP BY + SUM
sql


SELECT BillingCountry, SUM(Total) AS TotalSales
FROM invoices
GROUP BY BillingCountry;
Aggregate total sales by country.

🔧 Tech Stack
Python
Streamlit
SQLite
Pandas
Plotly
🌐 Deployment
🔗 Streamlit App: https://my-website-bmx3w3zmtvdyhfwa2kc2mh.streamlit.app/
🔗 GitHub Repo: https://github.com/boma4607-creator/my-website
✅ Conclusion
This dashboard provides a clear view of business performance and supports customer management.
It helps identify key markets, popular genres, and high-value customers.
