# **Simple Soccer Data Dashboard**

This is a simple (work-in-progress) **Flask web application** example that:
- **Processes** an Excel file (`dummy_soccer_stats.xlsx`) and inserts data into an **SQLite database**.
- **Generates interactive graphs** using **Plotly** to visualize soccer data.

---

## **🛠 Setup & Installation**
### **1️⃣ Install Dependencies**
Ensure you have Python installed, then install the required libraries:
```bash
pip install flask pandas sqlite3 plotly
```

### **2️⃣ Run the Flask App**
Start the server:
```bash
python app.py
```

### **3️⃣ Open in Browser**
- **Home Page:** [`http://localhost:5000/`](http://localhost:5000/)
- **Process File:** Click "Process File" to read data from the excel file in the uploads folder and store the data in SQLite.
- **View Graphs:** Click "View Graphs" to visualize the data.
