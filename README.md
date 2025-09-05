🌍 Impact Insights – Tracking the Effect of Public Events on Companies
📖 Overview

Impact Insights is a data visualization web application that tracks how public events, movements, and reports potentially impact companies and markets.

This project aims to:

Collect publicly available information about companies from verified sources.

Analyze sales and financial trends around significant event dates.

Visualize the results in an interactive and accessible way to support researchers, students, and analysts.

The platform is designed for educational and research purposes only, promoting data transparency without taking a political or ideological stance.

✨ Features

📊 Dashboard Visualizations
Explore sales and market trends through interactive, dynamic graphs.

🔍 Company Search
Search for companies and view related event descriptions and source links.

📈 Real-Time Financial Data (via Yahoo Finance API)
Integrate actual sales/stock data to analyze the timeline of impact.

Smooth User Experience
Built with React on the frontend and Flask as the backend.

Neutral, Ethical Framework
All data sources are public and verified, ensuring that the app serves as a transparent research tool.

🖼️ How It Works
1. Event Data Collection

The backend holds a dataset of companies linked to public reports or events.

Each record contains:

Company Name

Event Date

Event Description

Source Link

2. Financial Data Integration

The app fetches historical stock/sales data using the Yahoo Finance API.

By comparing data before and after the event, it visualizes potential correlations.

3. Data Visualization

The dashboard presents three key visualization types:

Line Chart – Stock/sales trends over time.

Candlestick Chart – Market movement around specific dates.

Bar Chart – Sales comparisons across companies or timeframes.

