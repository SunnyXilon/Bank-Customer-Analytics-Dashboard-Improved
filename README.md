# Bank Customer Analytics Dashboard 🏦

A modern, interactive web application built with Python, Dash, and Plotly to visualize and analyze synthetic bank customer data.

## ✨ Features

- **Interactive Filtering**: Filter data in real-time by State (Indian states), Account Type, Gender, and Age Range.
- **Dynamic KPI Cards**: Instantly view total customers, deposits, loan amounts, revenue, and churn rate based on your current filters.
- **Data Visualizations**: 
  - Customer Growth Trends (Line Chart)
  - Account Type Segmentation (Pie Chart)
  - Revenue breakdown (Bar Chart)
  - Age Distribution (Histogram)
- **Interactive Data Explorer**: A fully paginated data table containing specific customer details, complete with a dedicated `customer_id` search bar for quick lookups.
- **Modern UI**: Built with Dash Bootstrap Components using the sleek, dark `CYBORG` theme, featuring shadow depth and rounded cards.

## 🛠️ Technologies Used

- **Python**: Core programming language
- **Pandas & NumPy**: Data generation and manipulation
- **Dash**: Web framework for building the analytical app
- **Plotly Express**: Interactive chart generation
- **Dash Bootstrap Components**: Responsive grid layout and UI styling

## 🚀 How to Run Locally

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <your-repository-url>
   cd banking
   ```

2. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **View the Dashboard**:
   Open your web browser and navigate to `http://127.0.0.1:8050/`

## 📊 Data Source
The data used in this dashboard is purely synthetic, generated using `NumPy` and `Pandas` for demonstration and portfolio purposes. It includes features like customer age, geographic location (Indian States), account types, and revenue generated.
