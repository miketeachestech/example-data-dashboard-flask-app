import os
import sqlite3
import pandas as pd
import plotly.express as px
from flask import Flask, render_template

app = Flask(__name__)

# Database file
DB_FILE = "database.db"
UPLOAD_FOLDER = "uploads"

# Ensure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def create_soccer_table():
    """Creates the soccer_stats table with proper data types."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS soccer_stats (
            Player_Name TEXT,
            Team TEXT,
            Matches_Played INTEGER,
            Goals INTEGER,
            Assists INTEGER,
            Yellow_Cards INTEGER,
            Red_Cards INTEGER,
            Pass_Accuracy REAL,
            Shots_on_Target INTEGER,
            Minutes_Played INTEGER
        )
    """)
    
    conn.commit()
    conn.close()

def insert_soccer_data_from_excel_file(filename):
    """Reads soccer stats from an Excel file and inserts them into SQLite with proper types."""
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    # Read Excel file
    df = pd.read_excel(file_path, engine="openpyxl")

    # Normalize column names
    df.columns = [col.strip().replace(" ", "_") for col in df.columns]

    # Convert numeric columns to appropriate types
    numeric_columns = ["Matches_Played", "Goals", "Assists", "Yellow_Cards", "Red_Cards", "Pass_Accuracy", "Shots_on_Target", "Minutes_Played"]
    for col in numeric_columns:
        if col in df.columns:
            if col == "Pass_Accuracy":
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(float)  # Pass Accuracy as float
            else:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)  # Everything else as int

    # Connect to SQLite database
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Insert data into the table
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO soccer_stats (Player_Name, Team, Matches_Played, Goals, Assists, Yellow_Cards, Red_Cards, Pass_Accuracy, Shots_on_Target, Minutes_Played)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tuple(row))

    conn.commit()
    conn.close()

def get_soccer_dataframe():
    """Retrieve soccer data from SQLite database and return as a Pandas DataFrame."""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM soccer_stats", conn)
    conn.close()
    return df

@app.route('/')
def hello_world():
    return render_template("index.html")

@app.route('/process_soccer_data')
def process_soccer_file():
    try:
        filename = "dummy_soccer_stats.xlsx"  # Ensure this matches your actual filename
        create_soccer_table()  # Ensure the table is created before inserting
        insert_soccer_data_from_excel_file(filename)
        return "Soccer data inserted successfully!"
    except Exception as e:
        return f"Error: {e}"
    
@app.route('/soccer_data_dashboard')
def soccer_data_dashboard():
    # Fetch data
    df = get_soccer_dataframe()

    # Ensure relevant columns exist before plotting
    graphs = {}

    
    if "Team" in df.columns and "Goals" in df.columns and "Player_Name" in df.columns:
        # Sort by Goals (ascending order)
        df_sorted = df.sort_values(by="Goals", ascending=True)
        fig1 = px.bar(df_sorted, x="Team", y="Goals", color="Team", hover_data=["Player_Name"],
                      title="Goals Scored by Each Team")
        graphs["fig1_html"] = fig1.to_html(full_html=False)
    else:
        graphs["fig1_html"] = "<p>Not enough data for Team and Goals.</p>"

    if "Player_Name" in df.columns and "Assists" in df.columns:
        # Sort by Assists (ascending order)
        df_sorted = df.sort_values(by="Assists", ascending=True)
        fig2 = px.bar(df_sorted, x="Player_Name", y="Assists", color="Team", hover_data=["Team"], 
                      title="Assists by Player")
        graphs["fig2_html"] = fig2.to_html(full_html=False)
    else:
        graphs["fig2_html"] = "<p>Not enough data for Player Assists.</p>"

    if "Player_Name" in df.columns and "Shots_on_Target" in df.columns:
        # Sort by Shots on Target (ascending order)
        df_sorted = df.sort_values(by="Shots_on_Target", ascending=True)
        fig3 = px.bar(df_sorted, x="Player_Name", y="Shots_on_Target", color="Team", hover_data=["Team"], 
                      title="Shots on Target by Player")
        graphs["fig3_html"] = fig3.to_html(full_html=False)
    else:
        graphs["fig3_html"] = "<p>Not enough data for Shots on Target.</p>"

    if "Player_Name" in df.columns and "Minutes_Played" in df.columns:
        # Sort by Minutes Played (ascending order)
        df_sorted = df.sort_values(by="Minutes_Played", ascending=True)
        fig4 = px.bar(df_sorted, x="Player_Name", y="Minutes_Played", color="Team", hover_data=["Team"],
                       title="Minutes Played by Player")
        graphs["fig4_html"] = fig4.to_html(full_html=False)
    else:
        graphs["fig4_html"] = "<p>Not enough data for Minutes Played.</p>"

    if "Player_Name" in df.columns and "Goals" in df.columns:
        # Pie chart for goal contribution
        df_filtered = df[df["Goals"] > 0]  # Exclude players with 0 goals
        fig5 = px.pie(df_filtered, names="Player_Name", values="Goals", color="Team", hover_data=["Team"],
                      title="Goal Contribution Percentage by Player")
        graphs["fig5_html"] = fig5.to_html(full_html=False)
    else:
        graphs["fig5_html"] = "<p>Not enough data for Goal Contribution.</p>"

    if "Player_Name" in df.columns and "Matches_Played" in df.columns and "Goals" in df.columns:
        # Line graph for Goals Over Matches Played
        fig6 = px.line(df.sort_values(by="Matches_Played"),
                    x="Matches_Played", y="Goals", color="Player_Name",
                    markers=True, title="Goals Progression Over Matches")
        graphs["fig6_html"] = fig6.to_html(full_html=False)
    else:
        graphs["fig6_html"] = "<p>Not enough data for Goals Progression.</p>"


    # Render a simple HTML page with the graphs
    return render_template(
        "soccer_data_dashboard.html",
        fig1_html=graphs["fig1_html"],
        fig2_html=graphs["fig2_html"],
        fig3_html=graphs["fig3_html"],
        fig4_html=graphs["fig4_html"],
        fig5_html=graphs["fig5_html"],
        fig6_html=graphs["fig6_html"]
    )

if __name__ == '__main__':
    app.run(debug=True)
