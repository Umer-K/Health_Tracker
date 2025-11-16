import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import numpy as np

# ============================================================================
# DATABASE SETUP
# ============================================================================


def migrate_database():
    """Add missing columns to existing tables."""
    conn = sqlite3.connect("health_tracker.db")
    cursor = conn.cursor()

    # Get existing columns for food_library
    cursor.execute("PRAGMA table_info(food_library)")
    existing_food_cols = {row[1] for row in cursor.fetchall()}

    # Get existing columns for meals
    cursor.execute("PRAGMA table_info(meals)")
    existing_meal_cols = {row[1] for row in cursor.fetchall()}

    # All required columns with their types
    required_columns = {
        'fiber': 'REAL', 'sodium': 'REAL', 'cholesterol': 'REAL', 'sugar': 'REAL',
        'saturated_fat': 'REAL', 'vitamin_a': 'REAL', 'vitamin_b1': 'REAL',
        'vitamin_b2': 'REAL', 'vitamin_b3': 'REAL', 'vitamin_b5': 'REAL',
        'vitamin_b6': 'REAL', 'vitamin_b12': 'REAL', 'vitamin_c': 'REAL',
        'vitamin_d': 'REAL', 'vitamin_e': 'REAL', 'vitamin_k': 'REAL',
        'folate': 'REAL', 'calcium': 'REAL', 'iron': 'REAL', 'magnesium': 'REAL',
        'phosphorus': 'REAL', 'potassium': 'REAL', 'zinc': 'REAL', 'copper': 'REAL',
        'manganese': 'REAL', 'selenium': 'REAL', 'iodine': 'REAL', 'chromium': 'REAL',
        'molybdenum': 'REAL', 'omega_3': 'REAL', 'omega_6': 'REAL', 'water': 'REAL',
        'ash': 'REAL', 'created_date': 'TEXT'
    }

    # Add missing columns to food_library
    for col_name, col_type in required_columns.items():
        if col_name not in existing_food_cols:
            try:
                cursor.execute(
                    f"ALTER TABLE food_library ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass

    # Add missing columns to meals
    meal_columns = {**required_columns, 'notes': 'TEXT', 'time': 'TEXT'}
    for col_name, col_type in meal_columns.items():
        if col_name not in existing_meal_cols:
            try:
                cursor.execute(
                    f"ALTER TABLE meals ADD COLUMN {col_name} {col_type}")
            except sqlite3.OperationalError:
                pass

    conn.commit()
    conn.close()


def init_db():
    """Initialize SQLite database with meals and food library tables."""
    conn = sqlite3.connect("health_tracker.db")
    cursor = conn.cursor()

    # Foods Library Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS food_library (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name TEXT UNIQUE NOT NULL,
            calories TEXT, protein REAL, fat REAL, carbs REAL, fiber REAL,
            sodium REAL, cholesterol REAL, sugar REAL, saturated_fat REAL,
            vitamin_a REAL, vitamin_b1 REAL, vitamin_b2 REAL, vitamin_b3 REAL, vitamin_b5 REAL,
            vitamin_b6 REAL, vitamin_b12 REAL, vitamin_c REAL, vitamin_d REAL, vitamin_e REAL,
            vitamin_k REAL, folate REAL, calcium REAL, iron REAL, magnesium REAL,
            phosphorus REAL, potassium REAL, zinc REAL, copper REAL, manganese REAL,
            selenium REAL, iodine REAL, chromium REAL, molybdenum REAL,
            omega_3 REAL, omega_6 REAL, water REAL, ash REAL,
            created_date TEXT
        )
    """)

    # Meals Log Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            time TEXT,
            food_name TEXT NOT NULL,
            portion TEXT,
            calories TEXT, protein REAL, fat REAL, carbs REAL, fiber REAL,
            sodium REAL, cholesterol REAL, sugar REAL, saturated_fat REAL,
            vitamin_a REAL, vitamin_b1 REAL, vitamin_b2 REAL, vitamin_b3 REAL, vitamin_b5 REAL,
            vitamin_b6 REAL, vitamin_b12 REAL, vitamin_c REAL, vitamin_d REAL, vitamin_e REAL,
            vitamin_k REAL, folate REAL, calcium REAL, iron REAL, magnesium REAL,
            phosphorus REAL, potassium REAL, zinc REAL, copper REAL, manganese REAL,
            selenium REAL, iodine REAL, chromium REAL, molybdenum REAL,
            omega_3 REAL, omega_6 REAL, water REAL, ash REAL,
            notes TEXT
        )
    """)
    conn.commit()
    conn.close()

    migrate_database()


def get_db_connection():
    """Create database connection."""
    conn = sqlite3.connect("health_tracker.db")
    conn.row_factory = sqlite3.Row
    return conn

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def safe_float(value, default=0.0):
    """Safely convert value to float, handling NaN, None, and strings."""
    if value is None or value == '' or (isinstance(value, float) and np.isnan(value)):
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def parse_calorie_value(cal_str):
    """Parse calorie string which can be a number or range like '450-500'."""
    if isinstance(cal_str, (int, float)):
        if np.isnan(cal_str):
            return 0.0
        return float(cal_str)

    cal_str = str(cal_str).strip()
    if '-' in cal_str:
        try:
            parts = cal_str.split('-')
            low = float(parts[0].strip())
            high = float(parts[1].strip())
            return (low + high) / 2
        except:
            return 0.0
    else:
        try:
            return float(cal_str)
        except:
            return 0.0

# ============================================================================
# FOOD LIBRARY OPERATIONS
# ============================================================================


def add_food_to_library(food_name, calories, protein, fat, carbs, fiber, sodium, cholesterol, sugar,
                        saturated_fat, vitamin_a, vitamin_b1, vitamin_b2, vitamin_b3, vitamin_b5,
                        vitamin_b6, vitamin_b12, vitamin_c, vitamin_d, vitamin_e, vitamin_k, folate,
                        calcium, iron, magnesium, phosphorus, potassium, zinc, copper, manganese,
                        selenium, iodine, chromium, molybdenum, omega_3, omega_6, water, ash):
    """Add a food to the library with complete nutrition."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO food_library 
            (food_name, calories, protein, fat, carbs, fiber, sodium, cholesterol, sugar, saturated_fat,
             vitamin_a, vitamin_b1, vitamin_b2, vitamin_b3, vitamin_b5, vitamin_b6, vitamin_b12,
             vitamin_c, vitamin_d, vitamin_e, vitamin_k, folate, calcium, iron, magnesium,
             phosphorus, potassium, zinc, copper, manganese, selenium, iodine, chromium, molybdenum,
             omega_3, omega_6, water, ash, created_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (food_name, calories, protein, fat, carbs, fiber, sodium, cholesterol, sugar, saturated_fat,
              vitamin_a, vitamin_b1, vitamin_b2, vitamin_b3, vitamin_b5, vitamin_b6, vitamin_b12,
              vitamin_c, vitamin_d, vitamin_e, vitamin_k, folate, calcium, iron, magnesium,
              phosphorus, potassium, zinc, copper, manganese, selenium, iodine, chromium, molybdenum,
              omega_3, omega_6, water, ash, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True, f"✅ '{food_name}' added to library!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, f"⚠️ '{food_name}' already exists in library!"
    except Exception as e:
        conn.close()
        return False, f"❌ Error: {str(e)}"


def get_all_foods():
    """Fetch all foods from library."""
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM food_library ORDER BY food_name", conn)
    conn.close()
    return df


def get_food_by_id(food_id):
    """Fetch a single food by ID."""
    conn = get_db_connection()
    df = pd.read_sql_query(
        "SELECT * FROM food_library WHERE id = ?", conn, params=(food_id,))
    conn.close()
    if not df.empty:
        return df.iloc[0]
    return None


def delete_food_from_library(food_id):
    """Delete a food from library."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM food_library WHERE id = ?", (food_id,))
    conn.commit()
    conn.close()


def update_food_in_library(food_id, food_name, calories, protein, fat, carbs, fiber, sodium, cholesterol, sugar,
                           saturated_fat, vitamin_a, vitamin_b1, vitamin_b2, vitamin_b3, vitamin_b5,
                           vitamin_b6, vitamin_b12, vitamin_c, vitamin_d, vitamin_e, vitamin_k, folate,
                           calcium, iron, magnesium, phosphorus, potassium, zinc, copper, manganese,
                           selenium, iodine, chromium, molybdenum, omega_3, omega_6, water, ash):
    """Update an existing food in the library with complete nutrition."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE food_library 
            SET food_name=?, calories=?, protein=?, fat=?, carbs=?, fiber=?, sodium=?, cholesterol=?, sugar=?, saturated_fat=?,
                vitamin_a=?, vitamin_b1=?, vitamin_b2=?, vitamin_b3=?, vitamin_b5=?, vitamin_b6=?, vitamin_b12=?,
                vitamin_c=?, vitamin_d=?, vitamin_e=?, vitamin_k=?, folate=?, calcium=?, iron=?, magnesium=?,
                phosphorus=?, potassium=?, zinc=?, copper=?, manganese=?, selenium=?, iodine=?, chromium=?, molybdenum=?,
                omega_3=?, omega_6=?, water=?, ash=?
            WHERE id=?
        """, (food_name, calories, protein, fat, carbs, fiber, sodium, cholesterol, sugar, saturated_fat,
              vitamin_a, vitamin_b1, vitamin_b2, vitamin_b3, vitamin_b5, vitamin_b6, vitamin_b12,
              vitamin_c, vitamin_d, vitamin_e, vitamin_k, folate, calcium, iron, magnesium,
              phosphorus, potassium, zinc, copper, manganese, selenium, iodine, chromium, molybdenum,
              omega_3, omega_6, water, ash, food_id))
        conn.commit()
        conn.close()
        return True, f"✅ '{food_name}' updated successfully!"
    except Exception as e:
        conn.close()
        return False, f"❌ Error: {str(e)}"

# ============================================================================
# MEAL LOGGING OPERATIONS
# ============================================================================


def add_meal_to_log(date, time, food_name, portion, calories, protein, fat, carbs, fiber, sodium, cholesterol,
                    sugar, saturated_fat, vitamin_a, vitamin_b1, vitamin_b2, vitamin_b3, vitamin_b5,
                    vitamin_b6, vitamin_b12, vitamin_c, vitamin_d, vitamin_e, vitamin_k, folate,
                    calcium, iron, magnesium, phosphorus, potassium, zinc, copper, manganese,
                    selenium, iodine, chromium, molybdenum, omega_3, omega_6, water, ash, notes):
    """Log a meal to the daily log with complete nutrition."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meals 
        (date, time, food_name, portion, calories, protein, fat, carbs, fiber, sodium, cholesterol, sugar, saturated_fat,
         vitamin_a, vitamin_b1, vitamin_b2, vitamin_b3, vitamin_b5, vitamin_b6, vitamin_b12,
         vitamin_c, vitamin_d, vitamin_e, vitamin_k, folate, calcium, iron, magnesium,
         phosphorus, potassium, zinc, copper, manganese, selenium, iodine, chromium, molybdenum,
         omega_3, omega_6, water, ash, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, time, food_name, portion, calories, protein, fat, carbs, fiber, sodium, cholesterol, sugar, saturated_fat,
          vitamin_a, vitamin_b1, vitamin_b2, vitamin_b3, vitamin_b5, vitamin_b6, vitamin_b12,
          vitamin_c, vitamin_d, vitamin_e, vitamin_k, folate, calcium, iron, magnesium,
          phosphorus, potassium, zinc, copper, manganese, selenium, iodine, chromium, molybdenum,
          omega_3, omega_6, water, ash, notes))
    conn.commit()
    conn.close()


def get_meals_by_date_range(start_date, end_date):
    """Fetch meals within a date range."""
    conn = get_db_connection()
    query = """
        SELECT * FROM meals 
        WHERE date BETWEEN ? AND ? 
        ORDER BY date DESC, time DESC
    """
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()
    return df


def delete_meal_from_log(meal_id):
    """Delete a meal from log."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM meals WHERE id = ?", (meal_id,))
    conn.commit()
    conn.close()

# ============================================================================
# CALCULATIONS
# ============================================================================


def calculate_macros(df):
    """Calculate total and average macros from dataframe."""
    if df.empty:
        return {
            'total_calories': 0, 'avg_calories': 0,
            'total_protein': 0, 'avg_protein': 0,
            'total_fat': 0, 'avg_fat': 0,
            'total_carbs': 0, 'avg_carbs': 0,
            'meal_count': 0, 'days_count': 0
        }

    meal_count = len(df)
    days_count = df['date'].nunique()

    df_copy = df.copy()
    df_copy['calories_numeric'] = df_copy['calories'].apply(
        parse_calorie_value)

    return {
        'total_calories': df_copy['calories_numeric'].sum(),
        'avg_calories': df_copy['calories_numeric'].sum() / days_count if days_count > 0 else 0,
        'total_protein': safe_sum(df_copy['protein']),
        'avg_protein': safe_sum(df_copy['protein']) / days_count if days_count > 0 else 0,
        'total_fat': safe_sum(df_copy['fat']),
        'avg_fat': safe_sum(df_copy['fat']) / days_count if days_count > 0 else 0,
        'total_carbs': safe_sum(df_copy['carbs']),
        'avg_carbs': safe_sum(df_copy['carbs']) / days_count if days_count > 0 else 0,
        'meal_count': meal_count,
        'days_count': days_count
    }


def safe_sum(series):
    """Safely sum a pandas series, handling NaN and non-numeric values."""
    return pd.to_numeric(series, errors='coerce').fillna(0).sum()

# ============================================================================
# SIMPLE TABLE DISPLAY
# ============================================================================


def display_table(df, columns):
    """Display dataframe as simple HTML table."""
    if df.empty:
        st.info("No data to display.")
        return

    available_columns = [col for col in columns if col in df.columns]

    if not available_columns:
        st.info("No data to display.")
        return

    html = df[available_columns].to_html(index=False, border=0)
    st.write(html, unsafe_allow_html=True)

# ============================================================================
# CHARTS & VISUALIZATIONS
# ============================================================================


def plot_calories_trend(df):
    """Plot daily calorie trend."""
    if df.empty:
        st.warning("No data available for chart.")
        return

    df_sorted = df.sort_values('date').copy()
    df_sorted['calories_numeric'] = df_sorted['calories'].apply(
        parse_calorie_value)
    daily_calories = df_sorted.groupby(
        'date')['calories_numeric'].sum().reset_index()

    fig = px.line(
        daily_calories,
        x='date',
        y='calories_numeric',
        title='Daily Calorie Intake',
        labels={'date': 'Date', 'calories_numeric': 'Calories'},
        markers=True
    )
    fig.update_layout(hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)


def plot_macros_breakdown(df):
    """Plot macros as pie chart."""
    if df.empty:
        st.warning("No data available for chart.")
        return

    macros = calculate_macros(df)

    fig = go.Figure(data=[
        go.Pie(
            labels=['Protein', 'Fat', 'Carbs'],
            values=[macros['total_protein'],
                    macros['total_fat'], macros['total_carbs']],
            title='Total Macronutrients (grams)'
        )
    ])
    st.plotly_chart(fig, use_container_width=True)


def plot_daily_macros(df):
    """Plot daily macros trend."""
    if df.empty:
        st.warning("No data available for chart.")
        return

    df_sorted = df.sort_values('date').copy()
    daily_macros = df_sorted.groupby('date').agg({
        'protein': lambda x: safe_sum(x),
        'fat': lambda x: safe_sum(x),
        'carbs': lambda x: safe_sum(x)
    }).reset_index()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_macros['date'], y=daily_macros['protein'], name='Protein (g)', mode='lines+markers'))
    fig.add_trace(go.Scatter(
        x=daily_macros['date'], y=daily_macros['fat'], name='Fat (g)', mode='lines+markers'))
    fig.add_trace(go.Scatter(
        x=daily_macros['date'], y=daily_macros['carbs'], name='Carbs (g)', mode='lines+markers'))

    fig.update_layout(
        title='Daily Macronutrients Trend',
        xaxis_title='Date',
        yaxis_title='Grams',
        hovermode='x unified'
    )
    st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# STREAMLIT UI - MAIN FUNCTION
# ============================================================================


def main():
    st.set_page_config(page_title="Health Tracker Pakistan", layout="wide")
    st.title("🍛 Personal Health Tracker - Pakistan Edition")
    st.caption(
        "Track your daily nutrition from Pakistani foods | AI powered by ChatGPT")

    init_db()

    # Sidebar
    st.sidebar.title("📱 Navigation")
    page = st.sidebar.radio(
        "Select",
        ["Today's Log", "Last 7 Days", "Last 15 Days",
            "Last 30 Days", "Food Library", "Settings"]
    )

    # Determine date range
    today = datetime.now().date()
    if page == "Today's Log":
        start_date = today.isoformat()
        end_date = today.isoformat()
        title = "📅 Today's Nutrition"
    elif page == "Last 7 Days":
        start_date = (today - timedelta(days=6)).isoformat()
        end_date = today.isoformat()
        title = "📊 Last 7 Days"
    elif page == "Last 15 Days":
        start_date = (today - timedelta(days=14)).isoformat()
        end_date = today.isoformat()
        title = "📊 Last 15 Days"
    elif page == "Last 30 Days":
        start_date = (today - timedelta(days=29)).isoformat()
        end_date = today.isoformat()
        title = "📊 Last 30 Days"
    else:
        title = None

    # ========== FOOD LIBRARY PAGE ==========
    if page == "Food Library":
        st.header("🍖 Food Library")
        st.write(
            "Create & save your favorite foods with their calories & macros. Then quickly add them to your daily log!")

        tab1, tab2, tab3 = st.tabs(
            ["Add New Food", "Edit Food", "View & Manage Foods"])

        with tab1:
            st.subheader("➕ Add Food to Library")
            st.info(
                "💡 **Tip:** Save each food as a **standard serving** (e.g., '1 egg', '1 slice bread')")

            food_name = st.text_input("🍛 Food Name", key="add_food_name")

            st.write("### 🔥 Macronutrients")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                calories = st.text_input(
                    "Calories (kcal)", value="0", key="add_calories")
            with col2:
                protein = st.number_input(
                    "Protein (g)", min_value=0.0, step=0.1, value=0.0, key="add_protein")
            with col3:
                fat = st.number_input(
                    "Fat (g)", min_value=0.0, step=0.1, value=0.0, key="add_fat")
            with col4:
                saturated_fat = st.number_input(
                    "Saturated Fat (g)", min_value=0.0, step=0.1, value=0.0, key="add_sat_fat")

            col5, col6, col7, col8 = st.columns(4)
            with col5:
                carbs = st.number_input(
                    "Carbs (g)", min_value=0.0, step=0.1, value=0.0, key="add_carbs")
            with col6:
                fiber = st.number_input(
                    "Fiber (g)", min_value=0.0, step=0.1, value=0.0, key="add_fiber")
            with col7:
                sugar = st.number_input(
                    "Sugar (g)", min_value=0.0, step=0.1, value=0.0, key="add_sugar")
            with col8:
                omega_3 = st.number_input(
                    "Omega-3 (g)", min_value=0.0, step=0.1, value=0.0, key="add_omega3")

            st.write("### 🧂 Minerals")
            col9, col10, col11, col12 = st.columns(4)
            with col9:
                sodium = st.number_input(
                    "Sodium (mg)", min_value=0.0, step=1.0, value=0.0, key="add_sodium")
            with col10:
                potassium = st.number_input(
                    "Potassium (mg)", min_value=0.0, step=1.0, value=0.0, key="add_potassium")
            with col11:
                calcium = st.number_input(
                    "Calcium (mg)", min_value=0.0, step=1.0, value=0.0, key="add_calcium")
            with col12:
                magnesium = st.number_input(
                    "Magnesium (mg)", min_value=0.0, step=1.0, value=0.0, key="add_magnesium")

            col13, col14, col15, col16 = st.columns(4)
            with col13:
                phosphorus = st.number_input(
                    "Phosphorus (mg)", min_value=0.0, step=1.0, value=0.0, key="add_phosphorus")
            with col14:
                iron = st.number_input(
                    "Iron (mg)", min_value=0.0, step=0.1, value=0.0, key="add_iron")
            with col15:
                zinc = st.number_input(
                    "Zinc (mg)", min_value=0.0, step=0.1, value=0.0, key="add_zinc")
            with col16:
                copper = st.number_input(
                    "Copper (mg)", min_value=0.0, step=0.1, value=0.0, key="add_copper")

            col17, col18, col19, col20 = st.columns(4)
            with col17:
                manganese = st.number_input(
                    "Manganese (mg)", min_value=0.0, step=0.1, value=0.0, key="add_manganese")
            with col18:
                selenium = st.number_input(
                    "Selenium (mcg)", min_value=0.0, step=0.1, value=0.0, key="add_selenium")
            with col19:
                iodine = st.number_input(
                    "Iodine (mcg)", min_value=0.0, step=0.1, value=0.0, key="add_iodine")
            with col20:
                chromium = st.number_input(
                    "Chromium (mcg)", min_value=0.0, step=0.1, value=0.0, key="add_chromium")

            st.write("### 💊 Vitamins")
            col21, col22, col23, col24 = st.columns(4)
            with col21:
                vitamin_a = st.number_input(
                    "Vitamin A (IU)", min_value=0.0, step=1.0, value=0.0, key="add_vita")
            with col22:
                vitamin_b1 = st.number_input(
                    "Vitamin B1 (mg)", min_value=0.0, step=0.01, value=0.0, key="add_vitb1")
            with col23:
                vitamin_b2 = st.number_input(
                    "Vitamin B2 (mg)", min_value=0.0, step=0.01, value=0.0, key="add_vitb2")
            with col24:
                vitamin_b3 = st.number_input(
                    "Vitamin B3 (mg)", min_value=0.0, step=0.01, value=0.0, key="add_vitb3")

            col25, col26, col27, col28 = st.columns(4)
            with col25:
                vitamin_b5 = st.number_input(
                    "Vitamin B5 (mg)", min_value=0.0, step=0.01, value=0.0, key="add_vitb5")
            with col26:
                vitamin_b6 = st.number_input(
                    "Vitamin B6 (mg)", min_value=0.0, step=0.01, value=0.0, key="add_vitb6")
            with col27:
                vitamin_b12 = st.number_input(
                    "Vitamin B12 (mcg)", min_value=0.0, step=0.01, value=0.0, key="add_vitb12")
            with col28:
                folate = st.number_input(
                    "Folate (mcg)", min_value=0.0, step=1.0, value=0.0, key="add_folate")

            col29, col30, col31, col32 = st.columns(4)
            with col29:
                vitamin_c = st.number_input(
                    "Vitamin C (mg)", min_value=0.0, step=0.1, value=0.0, key="add_vitc")
            with col30:
                vitamin_d = st.number_input(
                    "Vitamin D (IU)", min_value=0.0, step=1.0, value=0.0, key="add_vitd")
            with col31:
                vitamin_e = st.number_input(
                    "Vitamin E (mg)", min_value=0.0, step=0.1, value=0.0, key="add_vite")
            with col32:
                vitamin_k = st.number_input(
                    "Vitamin K (mcg)", min_value=0.0, step=0.1, value=0.0, key="add_vitk")

            st.write("### 💧 Other")
            col33, col34, col35, col36 = st.columns(4)
            with col33:
                cholesterol = st.number_input(
                    "Cholesterol (mg)", min_value=0.0, step=1.0, value=0.0, key="add_cholesterol")
            with col34:
                omega_6 = st.number_input(
                    "Omega-6 (g)", min_value=0.0, step=0.1, value=0.0, key="add_omega6")
            with col35:
                water = st.number_input(
                    "Water (g)", min_value=0.0, step=1.0, value=0.0, key="add_water")
            with col36:
                molybdenum = st.number_input(
                    "Molybdenum (mcg)", min_value=0.0, step=0.1, value=0.0, key="add_molybdenum")

            ash = st.number_input(
                "Ash (g)", min_value=0.0, step=0.1, value=0.0, key="add_ash")

            if st.button("💾 Save to Library", use_container_width=True, type="primary", key="save_food_btn"):
                if food_name and calories and parse_calorie_value(calories) > 0:
                    success, msg = add_food_to_library(
                        food_name, calories, protein, fat, carbs, fiber, sodium, cholesterol, sugar,
                        saturated_fat, vitamin_a, vitamin_b1, vitamin_b2, vitamin_b3, vitamin_b5,
                        vitamin_b6, vitamin_b12, vitamin_c, vitamin_d, vitamin_e, vitamin_k, folate,
                        calcium, iron, magnesium, phosphorus, potassium, zinc, copper, manganese,
                        selenium, iodine, chromium, molybdenum, omega_3, omega_6, water, ash
                    )
                    if success:
                        st.success(msg)
                        st.balloons()
                        st.rerun()
                    else:
                        st.warning(msg)
                else:
                    st.error("❌ Please enter Food Name and Calories!")

        with tab2:
            st.subheader("✏️ Edit Food")
            foods_df_edit = get_all_foods()

            if not foods_df_edit.empty:
                food_to_edit_id = st.selectbox(
                    "Select food to edit:",
                    foods_df_edit['id'].tolist(),
                    format_func=lambda x: foods_df_edit[foods_df_edit['id']
                                                        == x]['food_name'].values[0],
                    key="edit_food_selector"
                )

                if food_to_edit_id:
                    food_data = get_food_by_id(food_to_edit_id)

                    if food_data is not None:
                        st.write("---")

                        edit_food_name = st.text_input("🍛 Food Name", value=str(
                            food_data['food_name']), key="edit_food_name")

                        st.write("### 🔥 Macronutrients")
                        ecol1, ecol2, ecol3, ecol4 = st.columns(4)
                        with ecol1:
                            edit_calories = st.text_input("Calories (kcal)", value=str(
                                food_data['calories']), key="edit_calories")
                        with ecol2:
                            edit_protein = st.number_input(
                                "Protein (g)", min_value=0.0, step=0.1, value=safe_float(food_data['protein']), key="edit_protein")
                        with ecol3:
                            edit_fat = st.number_input(
                                "Fat (g)", min_value=0.0, step=0.1, value=safe_float(food_data['fat']), key="edit_fat")
                        with ecol4:
                            edit_saturated_fat = st.number_input(
                                "Saturated Fat (g)", min_value=0.0, step=0.1, value=safe_float(food_data['saturated_fat']), key="edit_sat_fat")

                        ecol5, ecol6, ecol7, ecol8 = st.columns(4)
                        with ecol5:
                            edit_carbs = st.number_input(
                                "Carbs (g)", min_value=0.0, step=0.1, value=safe_float(food_data['carbs']), key="edit_carbs")
                        with ecol6:
                            edit_fiber = st.number_input(
                                "Fiber (g)", min_value=0.0, step=0.1, value=safe_float(food_data['fiber']), key="edit_fiber")
                        with ecol7:
                            edit_sugar = st.number_input(
                                "Sugar (g)", min_value=0.0, step=0.1, value=safe_float(food_data['sugar']), key="edit_sugar")
                        with ecol8:
                            edit_omega_3 = st.number_input(
                                "Omega-3 (g)", min_value=0.0, step=0.1, value=safe_float(food_data['omega_3']), key="edit_omega3")

                        st.write("### 🧂 Minerals")
                        ecol9, ecol10, ecol11, ecol12 = st.columns(4)
                        with ecol9:
                            edit_sodium = st.number_input(
                                "Sodium (mg)", min_value=0.0, step=1.0, value=safe_float(food_data['sodium']), key="edit_sodium")
                        with ecol10:
                            edit_potassium = st.number_input(
                                "Potassium (mg)", min_value=0.0, step=1.0, value=safe_float(food_data['potassium']), key="edit_potassium")
                        with ecol11:
                            edit_calcium = st.number_input(
                                "Calcium (mg)", min_value=0.0, step=1.0, value=safe_float(food_data['calcium']), key="edit_calcium")
                        with ecol12:
                            edit_magnesium = st.number_input(
                                "Magnesium (mg)", min_value=0.0, step=1.0, value=safe_float(food_data['magnesium']), key="edit_magnesium")

                        ecol13, ecol14, ecol15, ecol16 = st.columns(4)
                        with ecol13:
                            edit_phosphorus = st.number_input(
                                "Phosphorus (mg)", min_value=0.0, step=1.0, value=safe_float(food_data['phosphorus']), key="edit_phosphorus")
                        with ecol14:
                            edit_iron = st.number_input(
                                "Iron (mg)", min_value=0.0, step=0.1, value=safe_float(food_data['iron']), key="edit_iron")
                        with ecol15:
                            edit_zinc = st.number_input(
                                "Zinc (mg)", min_value=0.0, step=0.1, value=safe_float(food_data['zinc']), key="edit_zinc")
                        with ecol16:
                            edit_copper = st.number_input(
                                "Copper (mg)", min_value=0.0, step=0.1, value=safe_float(food_data['copper']), key="edit_copper")

                        ecol17, ecol18, ecol19, ecol20 = st.columns(4)
                        with ecol17:
                            edit_manganese = st.number_input(
                                "Manganese (mg)", min_value=0.0, step=0.1, value=safe_float(food_data['manganese']), key="edit_manganese")
                        with ecol18:
                            edit_selenium = st.number_input(
                                "Selenium (mcg)", min_value=0.0, step=0.1, value=safe_float(food_data['selenium']), key="edit_selenium")
                        with ecol19:
                            edit_iodine = st.number_input(
                                "Iodine (mcg)", min_value=0.0, step=0.1, value=safe_float(food_data['iodine']), key="edit_iodine")
                        with ecol20:
                            edit_chromium = st.number_input(
                                "Chromium (mcg)", min_value=0.0, step=0.1, value=safe_float(food_data['chromium']), key="edit_chromium")

                        st.write("### 💊 Vitamins")
                        ecol21, ecol22, ecol23, ecol24 = st.columns(4)
                        with ecol21:
                            edit_vitamin_a = st.number_input(
                                "Vitamin A (IU)", min_value=0.0, step=1.0, value=safe_float(food_data['vitamin_a']), key="edit_vita")
                        with ecol22:
                            edit_vitamin_b1 = st.number_input(
                                "Vitamin B1 (mg)", min_value=0.0, step=0.01, value=safe_float(food_data['vitamin_b1']), key="edit_vitb1")
                        with ecol23:
                            edit_vitamin_b2 = st.number_input(
                                "Vitamin B2 (mg)", min_value=0.0, step=0.01, value=safe_float(food_data['vitamin_b2']), key="edit_vitb2")
                        with ecol24:
                            edit_vitamin_b3 = st.number_input(
                                "Vitamin B3 (mg)", min_value=0.0, step=0.01, value=safe_float(food_data['vitamin_b3']), key="edit_vitb3")

                        ecol25, ecol26, ecol27, ecol28 = st.columns(4)
                        with ecol25:
                            edit_vitamin_b5 = st.number_input(
                                "Vitamin B5 (mg)", min_value=0.0, step=0.01, value=safe_float(food_data['vitamin_b5']), key="edit_vitb5")
                        with ecol26:
                            edit_vitamin_b6 = st.number_input(
                                "Vitamin B6 (mg)", min_value=0.0, step=0.01, value=safe_float(food_data['vitamin_b6']), key="edit_vitb6")
                        with ecol27:
                            edit_vitamin_b12 = st.number_input(
                                "Vitamin B12 (mcg)", min_value=0.0, step=0.01, value=safe_float(food_data['vitamin_b12']), key="edit_vitb12")
                        with ecol28:
                            edit_folate = st.number_input(
                                "Folate (mcg)", min_value=0.0, step=1.0, value=safe_float(food_data['folate']), key="edit_folate")

                        ecol29, ecol30, ecol31, ecol32 = st.columns(4)
                        with ecol29:
                            edit_vitamin_c = st.number_input(
                                "Vitamin C (mg)", min_value=0.0, step=0.1, value=safe_float(food_data['vitamin_c']), key="edit_vitc")
                        with ecol30:
                            edit_vitamin_d = st.number_input(
                                "Vitamin D (IU)", min_value=0.0, step=1.0, value=safe_float(food_data['vitamin_d']), key="edit_vitd")
                        with ecol31:
                            edit_vitamin_e = st.number_input(
                                "Vitamin E (mg)", min_value=0.0, step=0.1, value=safe_float(food_data['vitamin_e']), key="edit_vite")
                        with ecol32:
                            edit_vitamin_k = st.number_input(
                                "Vitamin K (mcg)", min_value=0.0, step=0.1, value=safe_float(food_data['vitamin_k']), key="edit_vitk")

                        st.write("### 💧 Other")
                        ecol33, ecol34, ecol35, ecol36 = st.columns(4)
                        with ecol33:
                            edit_cholesterol = st.number_input(
                                "Cholesterol (mg)", min_value=0.0, step=1.0, value=safe_float(food_data['cholesterol']), key="edit_cholesterol")
                        with ecol34:
                            edit_omega_6 = st.number_input(
                                "Omega-6 (g)", min_value=0.0, step=0.1, value=safe_float(food_data['omega_6']), key="edit_omega6")
                        with ecol35:
                            edit_water = st.number_input(
                                "Water (g)", min_value=0.0, step=1.0, value=safe_float(food_data['water']), key="edit_water")
                        with ecol36:
                            edit_molybdenum = st.number_input(
                                "Molybdenum (mcg)", min_value=0.0, step=0.1, value=safe_float(food_data['molybdenum']), key="edit_molybdenum")

                        edit_ash = st.number_input(
                            "Ash (g)", min_value=0.0, step=0.1, value=safe_float(food_data['ash']), key="edit_ash")

                        if st.button("💾 Update Food", use_container_width=True, type="primary", key="update_food_btn"):
                            if edit_food_name and edit_calories and parse_calorie_value(edit_calories) > 0:
                                success, msg = update_food_in_library(
                                    food_to_edit_id, edit_food_name, edit_calories, edit_protein, edit_fat, edit_carbs,
                                    edit_fiber, edit_sodium, edit_cholesterol, edit_sugar, edit_saturated_fat,
                                    edit_vitamin_a, edit_vitamin_b1, edit_vitamin_b2, edit_vitamin_b3, edit_vitamin_b5,
                                    edit_vitamin_b6, edit_vitamin_b12, edit_vitamin_c, edit_vitamin_d, edit_vitamin_e,
                                    edit_vitamin_k, edit_folate, edit_calcium, edit_iron, edit_magnesium,
                                    edit_phosphorus, edit_potassium, edit_zinc, edit_copper, edit_manganese,
                                    edit_selenium, edit_iodine, edit_chromium, edit_molybdenum,
                                    edit_omega_3, edit_omega_6, edit_water, edit_ash
                                )
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                            else:
                                st.error(
                                    "❌ Please enter Food Name and Calories!")
            else:
                st.info("No foods in library yet!")

        with tab3:
            st.subheader("📋 Your Food Library")
            foods_df = get_all_foods()

            if not foods_df.empty:
                display_table(
                    foods_df, ['food_name', 'calories', 'protein', 'fat', 'carbs'])

                st.write("---")
                food_to_delete = st.selectbox(
                    "Delete a food:",
                    foods_df['id'].tolist(),
                    format_func=lambda x: foods_df[foods_df['id']
                                                   == x]['food_name'].values[0],
                    key="delete_food_selector"
                )
                if st.button("🗑️ Delete Food", key="delete_food_btn"):
                    delete_food_from_library(food_to_delete)
                    st.success("Food deleted!")
                    st.rerun()
            else:
                st.info("No foods in library yet!")

    # ========== LOG MEAL PAGE ==========
    elif page in ["Today's Log", "Last 7 Days", "Last 15 Days", "Last 30 Days"]:
        st.header(title)

        meals_df = get_meals_by_date_range(start_date, end_date)
        macros = calculate_macros(meals_df)

        st.subheader("➕ Quick Add Meal")

        st.info("💡 **Tip:** You can select ANY date below - including past dates you forgot to log! Click the date field to open the calendar.")

        foods_df = get_all_foods()

        if not foods_df.empty:
            col1, col2, col3 = st.columns(3)

            with col1:
                selected_food_id = st.selectbox(
                    "Select Food",
                    foods_df['id'].tolist(),
                    format_func=lambda x: foods_df[foods_df['id']
                                                   == x]['food_name'].values[0],
                    key="meal_food_selector"
                )

            with col2:
                meal_date = st.date_input(
                    "📅 Date (Click to change!)",
                    value=today,
                    help="Click here to select any past date - like Nov 11th or any other day you forgot to log!",
                    key='meal_date_picker'
                )

            with col3:
                meal_time = st.time_input(
                    "🕐 Time",
                    value=datetime.now().time(),
                    key='meal_time_picker'
                )

            portion_multiplier = st.number_input(
                "Quantity",
                min_value=0.1,
                max_value=50.0,
                value=1.0,
                step=0.5,
                key="portion_multiplier"
            )

            if selected_food_id:
                food_row = foods_df[foods_df['id'] == selected_food_id].iloc[0]
                base_cals = parse_calorie_value(food_row['calories'])
                calculated_cals = base_cals * portion_multiplier
                st.info(
                    f"📊 {portion_multiplier} × {food_row['food_name']} = **{calculated_cals:.0f} calories**")

            col_btn1, col_btn2 = st.columns(2)

            with col_btn1:
                add_log_btn = st.button(
                    "✅ Add to Log", use_container_width=True, type="primary", key="add_meal_btn")

            with col_btn2:
                analyze_meal_btn = st.button(
                    "🧠 Analyze with ChatGPT", use_container_width=True, key="analyze_meal_btn")

            if add_log_btn:
                if portion_multiplier > 0:
                    food_row = foods_df[foods_df['id']
                                        == selected_food_id].iloc[0]
                    multiplied_calories = str(parse_calorie_value(
                        food_row['calories']) * portion_multiplier)
                    portion_display = f"{portion_multiplier}x"

                    add_meal_to_log(
                        meal_date.isoformat(),
                        meal_time.strftime("%H:%M"),
                        food_row['food_name'],
                        portion_display,
                        multiplied_calories,
                        safe_float(food_row.get('protein', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('fat', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('carbs', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('fiber', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('sodium', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('cholesterol', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('sugar', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('saturated_fat', 0)
                                   ) * portion_multiplier,
                        safe_float(food_row.get('vitamin_a', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('vitamin_b1', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('vitamin_b2', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('vitamin_b3', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('vitamin_b5', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('vitamin_b6', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('vitamin_b12', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('vitamin_c', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('vitamin_d', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('vitamin_e', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('vitamin_k', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('folate', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('calcium', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('iron', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('magnesium', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('phosphorus', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('potassium', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('zinc', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('copper', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('manganese', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('selenium', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('iodine', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('chromium', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('molybdenum', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('omega_3', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('omega_6', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('water', 0)) *
                        portion_multiplier,
                        safe_float(food_row.get('ash', 0)) *
                        portion_multiplier,
                        ""
                    )
                    st.success(
                        f"✅ Logged {portion_multiplier}x {food_row['food_name']} on {meal_date.isoformat()} at {meal_time.strftime('%H:%M')}!")
                    st.rerun()
                else:
                    st.error("Please enter a valid quantity!")

            # ChatGPT Analysis Logic
            if analyze_meal_btn:
                if selected_food_id and portion_multiplier > 0:
                    food_row = foods_df[foods_df['id']
                                        == selected_food_id].iloc[0]
                    food_name = food_row['food_name']

                    # Calculate multiplied nutrition values
                    meal_cals = parse_calorie_value(
                        food_row['calories']) * portion_multiplier
                    meal_protein = safe_float(food_row.get(
                        'protein', 0)) * portion_multiplier
                    meal_fat = safe_float(food_row.get(
                        'fat', 0)) * portion_multiplier
                    meal_carbs = safe_float(food_row.get(
                        'carbs', 0)) * portion_multiplier
                    meal_fiber = safe_float(food_row.get(
                        'fiber', 0)) * portion_multiplier
                    meal_sugar = safe_float(food_row.get(
                        'sugar', 0)) * portion_multiplier
                    meal_sodium = safe_float(food_row.get(
                        'sodium', 0)) * portion_multiplier

                    # Get today's totals
                    try:
                        today_str = meal_date.isoformat()
                        conn = get_db_connection()
                        today_meals = pd.read_sql_query(
                            "SELECT * FROM meals WHERE date = ?", conn, params=(today_str,))
                        conn.close()

                        if not today_meals.empty:
                            today_meals['calories_numeric'] = today_meals['calories'].apply(
                                parse_calorie_value)
                            total_cals_today = today_meals['calories_numeric'].sum(
                            )
                            meal_count = len(today_meals)
                            total_protein = safe_sum(today_meals['protein'])
                            total_fat = safe_sum(today_meals['fat'])
                            total_carbs = safe_sum(today_meals['carbs'])
                            total_fiber = safe_sum(today_meals['fiber'])
                            total_sodium = safe_sum(today_meals['sodium'])
                            total_sugar = safe_sum(today_meals['sugar'])
                        else:
                            total_cals_today = 0
                            meal_count = 0
                            total_protein = total_fat = total_carbs = total_fiber = 0
                            total_sodium = total_sugar = 0
                    except:
                        total_cals_today = 0
                        meal_count = 0
                        total_protein = total_fat = total_carbs = total_fiber = 0
                        total_sodium = total_sugar = 0

                    # Calculate new totals after this meal
                    new_total_cals = total_cals_today + meal_cals
                    new_total_protein = total_protein + meal_protein
                    new_total_fat = total_fat + meal_fat
                    new_total_carbs = total_carbs + meal_carbs
                    new_total_fiber = total_fiber + meal_fiber
                    new_total_sodium = total_sodium + meal_sodium
                    new_total_sugar = total_sugar + meal_sugar

                    # Build compact prompt
                    if meal_count > 0:
                        prompt = f"""Analyze this meal for my health goals (1600 kcal/day target):

MEAL I'M ABOUT TO EAT:
{food_name} ({portion_multiplier}x serving)
Calories: {meal_cals:.0f} kcal
Protein: {meal_protein:.1f}g | Fat: {meal_fat:.1f}g | Carbs: {meal_carbs:.1f}g
Fiber: {meal_fiber:.1f}g | Sugar: {meal_sugar:.1f}g | Sodium: {meal_sodium:.0f}mg

TODAY SO FAR ({meal_count} meals logged): {total_cals_today:.0f} kcal

AFTER EATING THIS:
Total Calories: {new_total_cals:.0f}/1600 kcal {"🚨 OVER LIMIT!" if new_total_cals > 1800 else "✅ Good" if new_total_cals <= 1600 else "⚠️ Close to limit"}
Protein: {new_total_protein:.1f}g | Fat: {new_total_fat:.1f}g | Carbs: {new_total_carbs:.1f}g
Fiber: {new_total_fiber:.1f}g {"⚠️ Low" if new_total_fiber < 25 else "✅"} | Sugar: {new_total_sugar:.1f}g {"⚠️ High" if new_total_sugar > 25 else "✅"}
Sodium: {new_total_sodium:.0f}mg {"🚨 Too high!" if new_total_sodium > 2000 else "✅"}

Answer these:
1. Should I eat this {food_name} now? Give me a clear YES/NO with reasoning.
2. Is the {portion_multiplier}x portion size appropriate or should I reduce it?
3. What specific nutrients am I lacking today that I need in my next meal?
4. Recommend ONE Pakistani dish for dinner that would perfectly balance my macros.
5. Any immediate health risks from eating this based on my sodium/sugar levels?"""
                    else:
                        prompt = f"""This is my FIRST meal today. Analyze it:

MEAL: {food_name} ({portion_multiplier}x serving)
Calories: {meal_cals:.0f} kcal (Daily Target: 1600 kcal)
Protein: {meal_protein:.1f}g | Fat: {meal_fat:.1f}g | Carbs: {meal_carbs:.1f}g
Fiber: {meal_fiber:.1f}g | Sugar: {meal_sugar:.1f}g | Sodium: {meal_sodium:.0f}mg

Answer these:
1. Is this a healthy first meal? Should I eat the full {portion_multiplier}x portion or reduce it?
2. This meal is {(meal_cals/1600*100):.1f}% of my daily calories. Is that too much for breakfast?
3. I have {1600-meal_cals:.0f} calories left. Suggest a simple lunch and dinner combo (Pakistani foods).
4. What nutrients am I missing from this meal that I MUST get in lunch/dinner?
5. Red flags: any health concerns with this meal's sodium/sugar/fat content?"""

                    # Create ChatGPT URLs
                    import urllib.parse
                    encoded_prompt = urllib.parse.quote(prompt)
                    chatgpt_url_new = f"https://chat.openai.com/?q={encoded_prompt}"
                    chatgpt_url_existing = "https://chatgpt.com/c/691863ca-6930-8322-b1cf-447ba8f4d793"

                    st.success(
                        "🎯 Analysis ready! Choose how to get your answer:")

                    col_gpt1, col_gpt2 = st.columns(2)

                    with col_gpt1:
                        st.markdown(f"""
                        <a href="{chatgpt_url_new}" target="_blank">
                            <button style="
                                background-color: #10a37f;
                                color: white;
                                padding: 16px 20px;
                                font-size: 16px;
                                font-weight: bold;
                                border: none;
                                border-radius: 8px;
                                cursor: pointer;
                                width: 100%;
                                margin: 10px 0;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            ">
                                🆕 New Chat (Auto-filled)
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
                        st.caption("✨ Instant - prompt already entered!")

                    with col_gpt2:
                        st.markdown(f"""
                        <a href="{chatgpt_url_existing}" target="_blank">
                            <button style="
                                background-color: #7c3aed;
                                color: white;
                                padding: 16px 20px;
                                font-size: 16px;
                                font-weight: bold;
                                border: none;
                                border-radius: 8px;
                                cursor: pointer;
                                width: 100%;
                                margin: 10px 0;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            ">
                                💬 My Health Coach
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
                        st.caption("📋 Copy prompt below & paste")

                    with st.expander("📋 Copy Prompt (for My Health Coach conversation)"):
                        st.text_area("Prompt:", prompt,
                                     height=300, key="manual_prompt")
                        st.info(
                            "💡 Click 'My Health Coach' button above, then paste this prompt there.")
                else:
                    st.warning(
                        "Please select a food and enter quantity to analyze!")
        else:
            st.warning("Please add foods to the Food Library first!")

        st.write("---")
        st.subheader("📚 Logged Meals")

        if not meals_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Calories", f"{int(macros['total_calories']):,}")
            col2.metric("Total Protein", f"{macros['total_protein']:.1f}g")
            col3.metric("Total Fat", f"{macros['total_fat']:.1f}g")
            col4.metric("Total Carbs", f"{macros['total_carbs']:.1f}g")

            st.write("---")
            st.subheader("📊 Detailed Nutrition Breakdown")

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                st.write("### 🔥 Macronutrients")
                st.metric("Calories", f"{int(macros['total_calories'])} kcal")
                st.metric("Protein", f"{safe_sum(meals_df['protein']):.1f} g")
                st.metric("Fat", f"{safe_sum(meals_df['fat']):.1f} g")
                st.metric("Saturated Fat",
                          f"{safe_sum(meals_df['saturated_fat']):.1f} g")
                st.metric("Carbs", f"{safe_sum(meals_df['carbs']):.1f} g")
                st.metric("Fiber", f"{safe_sum(meals_df['fiber']):.1f} g")
                st.metric("Sugar", f"{safe_sum(meals_df['sugar']):.1f} g")
                st.metric("Omega-3", f"{safe_sum(meals_df['omega_3']):.1f} g")
                st.metric("Omega-6", f"{safe_sum(meals_df['omega_6']):.1f} g")

            with col_b:
                st.write("### 🧂 Minerals")
                st.metric("Sodium", f"{safe_sum(meals_df['sodium']):.0f} mg")
                st.metric(
                    "Potassium", f"{safe_sum(meals_df['potassium']):.0f} mg")
                st.metric("Calcium", f"{safe_sum(meals_df['calcium']):.0f} mg")
                st.metric(
                    "Magnesium", f"{safe_sum(meals_df['magnesium']):.0f} mg")
                st.metric("Phosphorus",
                          f"{safe_sum(meals_df['phosphorus']):.0f} mg")
                st.metric("Iron", f"{safe_sum(meals_df['iron']):.1f} mg")
                st.metric("Zinc", f"{safe_sum(meals_df['zinc']):.1f} mg")
                st.metric("Copper", f"{safe_sum(meals_df['copper']):.1f} mg")
                st.metric(
                    "Manganese", f"{safe_sum(meals_df['manganese']):.1f} mg")
                st.metric(
                    "Selenium", f"{safe_sum(meals_df['selenium']):.1f} mcg")
                st.metric("Iodine", f"{safe_sum(meals_df['iodine']):.1f} mcg")
                st.metric(
                    "Chromium", f"{safe_sum(meals_df['chromium']):.1f} mcg")
                st.metric("Molybdenum",
                          f"{safe_sum(meals_df['molybdenum']):.1f} mcg")

            with col_c:
                st.write("### 💊 Vitamins")
                st.metric(
                    "Vitamin A", f"{safe_sum(meals_df['vitamin_a']):.0f} IU")
                st.metric("Vitamin B1",
                          f"{safe_sum(meals_df['vitamin_b1']):.2f} mg")
                st.metric("Vitamin B2",
                          f"{safe_sum(meals_df['vitamin_b2']):.2f} mg")
                st.metric("Vitamin B3",
                          f"{safe_sum(meals_df['vitamin_b3']):.2f} mg")
                st.metric("Vitamin B5",
                          f"{safe_sum(meals_df['vitamin_b5']):.2f} mg")
                st.metric("Vitamin B6",
                          f"{safe_sum(meals_df['vitamin_b6']):.2f} mg")
                st.metric("Vitamin B12",
                          f"{safe_sum(meals_df['vitamin_b12']):.2f} mcg")
                st.metric("Folate", f"{safe_sum(meals_df['folate']):.0f} mcg")
                st.metric(
                    "Vitamin C", f"{safe_sum(meals_df['vitamin_c']):.1f} mg")
                st.metric(
                    "Vitamin D", f"{safe_sum(meals_df['vitamin_d']):.0f} IU")
                st.metric(
                    "Vitamin E", f"{safe_sum(meals_df['vitamin_e']):.1f} mg")
                st.metric(
                    "Vitamin K", f"{safe_sum(meals_df['vitamin_k']):.1f} mcg")

                st.write("### 💧 Other")
                st.metric("Cholesterol",
                          f"{safe_sum(meals_df['cholesterol']):.0f} mg")
                st.metric("Water", f"{safe_sum(meals_df['water']):.0f} g")
                st.metric("Ash", f"{safe_sum(meals_df['ash']):.1f} g")

            st.write("---")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                plot_calories_trend(meals_df)
            with col_c2:
                plot_macros_breakdown(meals_df)

            plot_daily_macros(meals_df)

            # DAILY SUMMARY CHATGPT BUTTON
            if page == "Today's Log":
                st.write("---")
                if st.button("🌟 Get Daily Health Summary from ChatGPT", use_container_width=True, type="secondary", key="daily_summary_btn"):
                    # Calculate totals
                    df_copy = meals_df.copy()
                    df_copy['calories_numeric'] = df_copy['calories'].apply(
                        parse_calorie_value)

                    total_cals = df_copy['calories_numeric'].sum()
                    total_protein = safe_sum(df_copy['protein'])
                    total_fat = safe_sum(df_copy['fat'])
                    total_carbs = safe_sum(df_copy['carbs'])
                    total_fiber = safe_sum(df_copy['fiber'])
                    total_sodium = safe_sum(df_copy['sodium'])
                    total_sugar = safe_sum(df_copy['sugar'])

                    # Build daily summary prompt
                    prompt = f"""Daily Health Report - {meal_date.isoformat()}

TOTAL MEALS TODAY: {len(df_copy)}

MEALS BREAKDOWN:
"""
                    for idx, meal in df_copy.iterrows():
                        meal_cals = parse_calorie_value(meal['calories'])
                        prompt += f"{idx+1}. {meal['food_name']} ({meal['portion']}) - {meal_cals:.0f} kcal\n"

                    prompt += f"""
DAILY TOTALS (Target: 1600 kcal/day):
Calories: {total_cals:.0f}/1600 kcal {"🚨 OVER!" if total_cals > 1800 else "✅ Perfect" if 1400 <= total_cals <= 1600 else "⚠️ Close"}
Protein: {total_protein:.1f}g (Target: 78-120g)
Fat: {total_fat:.1f}g (Target: 44-62g)
Carbs: {total_carbs:.1f}g (Target: 175-245g)
Fiber: {total_fiber:.1f}g (Target: 25g) {"⚠️ Need more" if total_fiber < 25 else "✅"}
Sugar: {total_sugar:.1f}g (Limit: <25g) {"⚠️ Too much!" if total_sugar > 25 else "✅"}
Sodium: {total_sodium:.0f}mg (Limit: <2000mg) {"🚨 Way too high!" if total_sodium > 2000 else "✅"}

Give me ACTIONABLE answers:
1. Rate my day: A-F grade with specific reasoning for the grade.
2. Biggest mistake today: What ONE thing hurt my health goals the most?
3. Biggest win today: What did I do right that I should repeat?
4. Tomorrow's plan: Give me 3 specific Pakistani meals (breakfast, lunch, dinner) with portion sizes.
5. Health risks: Based on my sodium/sugar/fiber, what should I watch out for?
6. One-week challenge: What ONE habit should I focus on this week to improve?"""

                    import urllib.parse
                    encoded_prompt = urllib.parse.quote(prompt)
                    chatgpt_url_new = f"https://chat.openai.com/?q={encoded_prompt}"
                    chatgpt_url_existing = "https://chatgpt.com/c/691863ca-6930-8322-b1cf-447ba8f4d793"

                    st.success(
                        "📊 Daily summary ready! Get your personalized health coach review:")

                    col_daily1, col_daily2 = st.columns(2)

                    with col_daily1:
                        st.markdown(f"""
                        <a href="{chatgpt_url_new}" target="_blank">
                            <button style="
                                background-color: #10a37f;
                                color: white;
                                padding: 16px 20px;
                                font-size: 16px;
                                font-weight: bold;
                                border: none;
                                border-radius: 8px;
                                cursor: pointer;
                                width: 100%;
                                margin: 10px 0;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            ">
                                🆕 New Chat (Auto-filled)
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
                        st.caption("✨ Instant analysis - ready to send!")

                    with col_daily2:
                        st.markdown(f"""
                        <a href="{chatgpt_url_existing}" target="_blank">
                            <button style="
                                background-color: #7c3aed;
                                color: white;
                                padding: 16px 20px;
                                font-size: 16px;
                                font-weight: bold;
                                border: none;
                                border-radius: 8px;
                                cursor: pointer;
                                width: 100%;
                                margin: 10px 0;
                                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                            ">
                                💬 My Health Coach
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
                        st.caption("📋 Copy & paste for continuity")

                    with st.expander("📋 Copy Prompt (for My Health Coach conversation)"):
                        st.text_area("Daily Summary Prompt:", prompt,
                                     height=400, key="daily_manual_prompt")
                        st.info(
                            "💡 Click 'My Health Coach' above, then paste this prompt.")

            st.write("---")
            st.subheader("Detailed Log")
            display_table(meals_df, [
                          'id', 'date', 'time', 'food_name', 'portion', 'calories', 'protein', 'fat', 'carbs'])

            st.write("---")
            meal_ids = meals_df['id'].tolist()
            if meal_ids:
                meal_to_delete = st.selectbox(
                    "Delete an entry:",
                    meal_ids,
                    format_func=lambda x: f"ID {x}: {meals_df[meals_df['id'] == x]['food_name'].values[0]}",
                    key="delete_meal_selector"
                )
                if st.button("❌ Delete Meal Entry", key="delete_meal_btn"):
                    delete_meal_from_log(meal_to_delete)
                    st.success(f"Meal ID {meal_to_delete} deleted!")
                    st.rerun()
        else:
            st.info("No meals logged for this period. Add a meal above!")

    # ========== SETTINGS PAGE ==========
    elif page == "Settings":
        st.header("⚙️ Settings")

        st.subheader("Database Management")
        st.info("Database saved as `health_tracker.db` in your project folder")

        if st.button("Run Database Migration", key="migrate_db_btn"):
            try:
                migrate_database()
                st.success("Database migration completed!")
            except Exception as e:
                st.error(f"Error: {e}")

        st.write("---")
        st.subheader("Data Export")

        all_meals_df = get_meals_by_date_range("2000-01-01", today.isoformat())

        if not all_meals_df.empty:
            csv = all_meals_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="⬇️ Download All Meal Log Data as CSV",
                data=csv,
                file_name='health_tracker_meal_log.csv',
                mime='text/csv',
                type="primary",
                key="download_csv_btn"
            )
        else:
            st.warning("No data to export yet.")


if __name__ == "__main__":
    main()
