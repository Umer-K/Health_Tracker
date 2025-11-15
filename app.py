import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import urllib.parse
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
    meal_columns = {**required_columns, 'notes': 'TEXT'}
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


def delete_food_from_library(food_id):
    """Delete a food from library."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM food_library WHERE id = ?", (food_id,))
    conn.commit()
    conn.close()

# ============================================================================
# MEAL LOGGING OPERATIONS
# ============================================================================


def add_meal_to_log(date, food_name, portion, calories, protein, fat, carbs, fiber, sodium, cholesterol,
                    sugar, saturated_fat, vitamin_a, vitamin_b1, vitamin_b2, vitamin_b3, vitamin_b5,
                    vitamin_b6, vitamin_b12, vitamin_c, vitamin_d, vitamin_e, vitamin_k, folate,
                    calcium, iron, magnesium, phosphorus, potassium, zinc, copper, manganese,
                    selenium, iodine, chromium, molybdenum, omega_3, omega_6, water, ash, notes):
    """Log a meal to the daily log with complete nutrition."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO meals 
        (date, food_name, portion, calories, protein, fat, carbs, fiber, sodium, cholesterol, sugar, saturated_fat,
         vitamin_a, vitamin_b1, vitamin_b2, vitamin_b3, vitamin_b5, vitamin_b6, vitamin_b12,
         vitamin_c, vitamin_d, vitamin_e, vitamin_k, folate, calcium, iron, magnesium,
         phosphorus, potassium, zinc, copper, manganese, selenium, iodine, chromium, molybdenum,
         omega_3, omega_6, water, ash, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, food_name, portion, calories, protein, fat, carbs, fiber, sodium, cholesterol, sugar, saturated_fat,
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
        ORDER BY date DESC
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
        'total_protein': df_copy['protein'].sum(),
        'avg_protein': df_copy['protein'].sum() / days_count if days_count > 0 else 0,
        'total_fat': df_copy['fat'].sum(),
        'avg_fat': df_copy['fat'].sum() / days_count if days_count > 0 else 0,
        'total_carbs': df_copy['carbs'].sum(),
        'avg_carbs': df_copy['carbs'].sum() / days_count if days_count > 0 else 0,
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

    df_sorted = df.sort_values('date')
    daily_macros = df_sorted.groupby(
        'date')[['protein', 'fat', 'carbs']].sum().reset_index()

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
# STREAMLIT UI
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

        tab1, tab2 = st.tabs(["Add New Food", "View & Manage Foods"])

        with tab1:
            st.subheader("➕ Add Food to Library - Complete Nutrition")

            food_name = st.text_input(
                "🍛 Food Name (e.g., 'Chicken Biryani - 1 plate')")

            # MACRONUTRIENTS
            st.write("### 🔥 Macronutrients")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                calories = st.text_input(
                    "Calories (kcal)", value="0", help="Enter a number (e.g., 450) or range (e.g., 450-500)")
            with col2:
                protein = st.number_input(
                    "Protein (g)", min_value=0.0, step=0.1, value=0.0)
            with col3:
                fat = st.number_input(
                    "Fat (g)", min_value=0.0, step=0.1, value=0.0)
            with col4:
                saturated_fat = st.number_input(
                    "Saturated Fat (g)", min_value=0.0, step=0.1, value=0.0)

            col5, col6, col7, col8 = st.columns(4)
            with col5:
                carbs = st.number_input(
                    "Carbs (g)", min_value=0.0, step=0.1, value=0.0)
            with col6:
                fiber = st.number_input(
                    "Fiber (g)", min_value=0.0, step=0.1, value=0.0)
            with col7:
                sugar = st.number_input(
                    "Sugar (g)", min_value=0.0, step=0.1, value=0.0)
            with col8:
                omega_3 = st.number_input(
                    "Omega-3 (g)", min_value=0.0, step=0.1, value=0.0)

            # MINERALS
            st.write("### 🧂 Minerals & Electrolytes")
            col9, col10, col11, col12 = st.columns(4)
            with col9:
                sodium = st.number_input(
                    "Sodium (mg)", min_value=0.0, step=1.0, value=0.0)
            with col10:
                potassium = st.number_input(
                    "Potassium (mg)", min_value=0.0, step=1.0, value=0.0)
            with col11:
                calcium = st.number_input(
                    "Calcium (mg)", min_value=0.0, step=1.0, value=0.0)
            with col12:
                magnesium = st.number_input(
                    "Magnesium (mg)", min_value=0.0, step=1.0, value=0.0)

            col13, col14, col15, col16 = st.columns(4)
            with col13:
                phosphorus = st.number_input(
                    "Phosphorus (mg)", min_value=0.0, step=1.0, value=0.0)
            with col14:
                iron = st.number_input(
                    "Iron (mg)", min_value=0.0, step=0.1, value=0.0)
            with col15:
                zinc = st.number_input(
                    "Zinc (mg)", min_value=0.0, step=0.1, value=0.0)
            with col16:
                copper = st.number_input(
                    "Copper (mg)", min_value=0.0, step=0.1, value=0.0)

            col17, col18, col19, col20 = st.columns(4)
            with col17:
                manganese = st.number_input(
                    "Manganese (mg)", min_value=0.0, step=0.1, value=0.0)
            with col18:
                selenium = st.number_input(
                    "Selenium (mcg)", min_value=0.0, step=0.1, value=0.0)
            with col19:
                iodine = st.number_input(
                    "Iodine (mcg)", min_value=0.0, step=0.1, value=0.0)
            with col20:
                chromium = st.number_input(
                    "Chromium (mcg)", min_value=0.0, step=0.1, value=0.0)

            # VITAMINS
            st.write("### 💊 Vitamins")
            col21, col22, col23, col24 = st.columns(4)
            with col21:
                vitamin_a = st.number_input(
                    "Vitamin A (IU)", min_value=0.0, step=1.0, value=0.0)
            with col22:
                vitamin_b1 = st.number_input(
                    "Vitamin B1 - Thiamine (mg)", min_value=0.0, step=0.01, value=0.0)
            with col23:
                vitamin_b2 = st.number_input(
                    "Vitamin B2 - Riboflavin (mg)", min_value=0.0, step=0.01, value=0.0)
            with col24:
                vitamin_b3 = st.number_input(
                    "Vitamin B3 - Niacin (mg)", min_value=0.0, step=0.01, value=0.0)

            col25, col26, col27, col28 = st.columns(4)
            with col25:
                vitamin_b5 = st.number_input(
                    "Vitamin B5 - Pantothenic (mg)", min_value=0.0, step=0.01, value=0.0)
            with col26:
                vitamin_b6 = st.number_input(
                    "Vitamin B6 (mg)", min_value=0.0, step=0.01, value=0.0)
            with col27:
                vitamin_b12 = st.number_input(
                    "Vitamin B12 (mcg)", min_value=0.0, step=0.01, value=0.0)
            with col28:
                folate = st.number_input(
                    "Folate (mcg)", min_value=0.0, step=1.0, value=0.0)

            col29, col30, col31, col32 = st.columns(4)
            with col29:
                vitamin_c = st.number_input(
                    "Vitamin C (mg)", min_value=0.0, step=0.1, value=0.0)
            with col30:
                vitamin_d = st.number_input(
                    "Vitamin D (IU)", min_value=0.0, step=1.0, value=0.0)
            with col31:
                vitamin_e = st.number_input(
                    "Vitamin E (mg)", min_value=0.0, step=0.1, value=0.0)
            with col32:
                vitamin_k = st.number_input(
                    "Vitamin K (mcg)", min_value=0.0, step=0.1, value=0.0)

            # OTHER NUTRIENTS
            st.write("### 💧 Other")
            col33, col34, col35, col36 = st.columns(4)
            with col33:
                cholesterol = st.number_input(
                    "Cholesterol (mg)", min_value=0.0, step=1.0, value=0.0)
            with col34:
                omega_6 = st.number_input(
                    "Omega-6 (g)", min_value=0.0, step=0.1, value=0.0)
            with col35:
                water = st.number_input(
                    "Water (g)", min_value=0.0, step=1.0, value=0.0)
            with col36:
                molybdenum = st.number_input(
                    "Molybdenum (mcg)", min_value=0.0, step=0.1, value=0.0)

            ash = st.number_input(
                "Ash (g)", min_value=0.0, step=0.1, value=0.0)

            if st.button("💾 Save to Library", use_container_width=True, type="primary"):
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
            st.subheader("📋 Your Food Library")
            foods_df = get_all_foods()

            if not foods_df.empty:
                display_table(foods_df, [
                              'food_name', 'calories', 'protein', 'fat', 'carbs', 'fiber', 'sodium', 'cholesterol'])

                st.write("---")
                col1, col2 = st.columns(2)
                with col1:
                    food_to_delete = st.selectbox(
                        "Delete a food:",
                        foods_df['id'].tolist(),
                        format_func=lambda x: foods_df[foods_df['id']
                                                       == x]['food_name'].values[0]
                    )
                    if st.button("🗑️ Delete Food"):
                        delete_food_from_library(food_to_delete)
                        st.success("Food deleted!")
                        st.rerun()

                with col2:
                    st.info(f"📦 Total foods saved: {len(foods_df)}")
            else:
                st.info("No foods in library yet. Add some foods first!")

    # ========== LOG MEAL PAGE ==========
    elif page in ["Today's Log", "Last 7 Days", "Last 15 Days", "Last 30 Days"]:
        st.header(title)

        meals_df = get_meals_by_date_range(start_date, end_date)
        macros = calculate_macros(meals_df)

        # Quick Add Meal Section
        st.subheader("➕ Quick Add Meal")
        foods_df = get_all_foods()

        if not foods_df.empty:
            col1, col2, col3 = st.columns(3)

            with col1:
                selected_food_id = st.selectbox(
                    "Select Food from Library",
                    foods_df['id'].tolist(),
                    format_func=lambda x: foods_df[foods_df['id']
                                                   == x]['food_name'].values[0],
                    key='selected_food_id'
                )

            with col2:
                meal_date = st.date_input("Date", value=today, key='meal_date')

            with col3:
                portion = st.text_input(
                    "Portion (e.g., 1 plate, 1 bowl)", key='portion_input')

            col_log_1, col_log_2 = st.columns(2)

            with col_log_1:
                log_button = st.button(
                    "✅ Add to Log", use_container_width=True, type="primary")

            with col_log_2:
                analyze_button = st.button(
                    "🧠 Analyze Meal with ChatGPT", use_container_width=True)

            # Logic for Logging
            if log_button:
                if portion:
                    food_row = foods_df[foods_df['id']
                                        == selected_food_id].iloc[0]
                    add_meal_to_log(
                        meal_date.isoformat(),
                        food_row['food_name'],
                        portion,
                        food_row['calories'],
                        safe_float(food_row.get('protein', 0)),
                        safe_float(food_row.get('fat', 0)),
                        safe_float(food_row.get('carbs', 0)),
                        safe_float(food_row.get('fiber', 0)),
                        safe_float(food_row.get('sodium', 0)),
                        safe_float(food_row.get('cholesterol', 0)),
                        safe_float(food_row.get('sugar', 0)),
                        safe_float(food_row.get('saturated_fat', 0)),
                        safe_float(food_row.get('vitamin_a', 0)),
                        safe_float(food_row.get('vitamin_b1', 0)),
                        safe_float(food_row.get('vitamin_b2', 0)),
                        safe_float(food_row.get('vitamin_b3', 0)),
                        safe_float(food_row.get('vitamin_b5', 0)),
                        safe_float(food_row.get('vitamin_b6', 0)),
                        safe_float(food_row.get('vitamin_b12', 0)),
                        safe_float(food_row.get('vitamin_c', 0)),
                        safe_float(food_row.get('vitamin_d', 0)),
                        safe_float(food_row.get('vitamin_e', 0)),
                        safe_float(food_row.get('vitamin_k', 0)),
                        safe_float(food_row.get('folate', 0)),
                        safe_float(food_row.get('calcium', 0)),
                        safe_float(food_row.get('iron', 0)),
                        safe_float(food_row.get('magnesium', 0)),
                        safe_float(food_row.get('phosphorus', 0)),
                        safe_float(food_row.get('potassium', 0)),
                        safe_float(food_row.get('zinc', 0)),
                        safe_float(food_row.get('copper', 0)),
                        safe_float(food_row.get('manganese', 0)),
                        safe_float(food_row.get('selenium', 0)),
                        safe_float(food_row.get('iodine', 0)),
                        safe_float(food_row.get('chromium', 0)),
                        safe_float(food_row.get('molybdenum', 0)),
                        safe_float(food_row.get('omega_3', 0)),
                        safe_float(food_row.get('omega_6', 0)),
                        safe_float(food_row.get('water', 0)),
                        safe_float(food_row.get('ash', 0)),
                        ""
                    )
                    st.success("Meal added successfully!")
                    st.rerun()
                else:
                    st.error("Please enter a portion size!")

            # Logic for Individual Meal Analysis
            if analyze_button:
                if portion and selected_food_id:
                    # Get the food data
                    food_row_series = foods_df[foods_df['id']
                                               == selected_food_id].iloc[0].copy()
                    food_name = food_row_series.get(
                        "food_name", "Unknown Food")
                    calories = parse_calorie_value(
                        food_row_series.get("calories", 0))

                    # Get today's totals and meal history
                    try:
                        today_str = datetime.now().date().isoformat()
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

                            # Calculate nutrient totals using safe_sum
                            total_protein = safe_sum(today_meals['protein'])
                            total_fat = safe_sum(today_meals['fat'])
                            total_carbs = safe_sum(today_meals['carbs'])
                            total_fiber = safe_sum(today_meals['fiber'])
                            total_sodium = safe_sum(today_meals['sodium'])
                            total_sugar = safe_sum(today_meals['sugar'])
                            total_saturated_fat = safe_sum(
                                today_meals['saturated_fat'])
                        else:
                            total_cals_today = 0
                            meal_count = 0
                            total_protein = total_fat = total_carbs = total_fiber = 0
                            total_sodium = total_sugar = total_saturated_fat = 0
                    except:
                        total_cals_today = 0
                        meal_count = 0
                        total_protein = total_fat = total_carbs = total_fiber = 0
                        total_sodium = total_sugar = total_saturated_fat = 0

                    # Calculate new totals after this meal
                    new_total_cals = total_cals_today + calories
                    new_total_protein = total_protein + \
                        safe_float(food_row_series.get('protein', 0))
                    new_total_fat = total_fat + \
                        safe_float(food_row_series.get('fat', 0))
                    new_total_carbs = total_carbs + \
                        safe_float(food_row_series.get('carbs', 0))
                    new_total_fiber = total_fiber + \
                        safe_float(food_row_series.get('fiber', 0))
                    new_total_sodium = total_sodium + \
                        safe_float(food_row_series.get('sodium', 0))
                    new_total_sugar = total_sugar + \
                        safe_float(food_row_series.get('sugar', 0))

                    # Build COMPACT prompt for URL
                    if meal_count > 0:
                        prompt = f"""Umer's Meal Analysis (21y, 78kg, 1600 kcal goal):

MEAL: {food_name} ({portion})
Cals: {calories:.0f} | P: {safe_float(food_row_series.get('protein', 0)):.1f}g | F: {safe_float(food_row_series.get('fat', 0)):.1f}g | C: {safe_float(food_row_series.get('carbs', 0)):.1f}g
Fiber: {safe_float(food_row_series.get('fiber', 0)):.1f}g | Sugar: {safe_float(food_row_series.get('sugar', 0)):.1f}g | Sodium: {safe_float(food_row_series.get('sodium', 0)):.0f}mg

TODAY SO FAR ({meal_count} meals): {total_cals_today:.0f} kcal

AFTER THIS MEAL:
Total: {new_total_cals:.0f}/1600 kcal {"🚨 OVER!" if new_total_cals > 1800 else "✅" if new_total_cals <= 1600 else "⚠️"}
Protein: {new_total_protein:.1f}/78-120g | Fat: {new_total_fat:.1f}/44-62g | Carbs: {new_total_carbs:.1f}/175-245g
Fiber: {new_total_fiber:.1f}/25g {"⚠️" if new_total_fiber < 25 else "✅"} | Sugar: {new_total_sugar:.1f}/25g {"⚠️" if new_total_sugar > 25 else "✅"}
Sodium: {new_total_sodium:.0f}/2000mg {"🚨" if new_total_sodium > 2000 else "✅"}

Should I eat this? Health risks? Recommendations for rest of day?"""
                    else:
                        prompt = f"""Umer's First Meal (21y, 78kg, 1600 kcal goal):

MEAL: {food_name} ({portion})
Cals: {calories:.0f} | P: {safe_float(food_row_series.get('protein', 0)):.1f}g | F: {safe_float(food_row_series.get('fat', 0)):.1f}g | C: {safe_float(food_row_series.get('carbs', 0)):.1f}g
Fiber: {safe_float(food_row_series.get('fiber', 0)):.1f}g | Sugar: {safe_float(food_row_series.get('sugar', 0)):.1f}g | Sodium: {safe_float(food_row_series.get('sodium', 0)):.0f}mg

This is my FIRST meal today. Is it good? Does it leave room for 2 more meals? What should I focus on for lunch/dinner?"""

                    # Display prompt in copyable text area
                    st.success(
                        "✅ Analysis ready! Copy the prompt below and paste it into your ChatGPT conversation.")

                    st.text_area("📋 Copy this prompt:", prompt,
                                 height=300, key="meal_analysis_prompt")

                    st.markdown("""
                    <a href="https://chatgpt.com/c/691863ca-6930-8322-b1cf-447ba8f4d793" target="_blank">
                        <button style="
                            background-color: #10a37f;
                            color: white;
                            padding: 12px 24px;
                            font-size: 16px;
                            border: none;
                            border-radius: 6px;
                            cursor: pointer;
                            width: 100%;
                        ">
                            🚀 Open Your ChatGPT Conversation
                        </button>
                    </a>
                    """, unsafe_allow_html=True)

                    st.info(
                        "💡 **How to use:** Click the button above to open your ChatGPT conversation, then paste the prompt from the text box.")
                else:
                    st.warning(
                        "Please select a food and enter a portion to analyze.")

        else:
            st.warning("Please add some foods to the **Food Library** first.")

        # Display Log and Calculations
        st.subheader("📚 Logged Meals")

        if not meals_df.empty:
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("Total Calories",
                          f"{int(macros['total_calories']):,}")
            col_m2.metric("Total Protein (g)",
                          f"{macros['total_protein']:.1f}")
            col_m3.metric("Total Fat (g)", f"{macros['total_fat']:.1f}")
            col_m4.metric("Total Carbs (g)", f"{macros['total_carbs']:.1f}")

            # DETAILED NUTRITION BREAKDOWN
            st.write("---")
            st.subheader("📊 Detailed Nutrition Breakdown")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("### 🔥 Macronutrients")
                st.metric("Calories", f"{int(macros['total_calories'])} kcal")

                # Safe metric display with error handling
                def safe_metric(label, column, format_str=".1f", unit="g"):
                    try:
                        value = safe_sum(meals_df[column])
                        st.metric(label, f"{value:{format_str}} {unit}")
                    except:
                        st.metric(label, f"0.0 {unit}")

                safe_metric("Protein", "protein")
                safe_metric("Fat", "fat")
                safe_metric("Saturated Fat", "saturated_fat")
                safe_metric("Carbs", "carbs")
                safe_metric("Fiber", "fiber")
                safe_metric("Sugar", "sugar")
                safe_metric("Omega-3", "omega_3")
                safe_metric("Omega-6", "omega_6")

            with col2:
                st.write("### 🧂 Minerals")
                safe_metric("Sodium", "sodium", ".0f", "mg")
                safe_metric("Potassium", "potassium", ".0f", "mg")
                safe_metric("Calcium", "calcium", ".0f", "mg")
                safe_metric("Magnesium", "magnesium", ".0f", "mg")
                safe_metric("Phosphorus", "phosphorus", ".0f", "mg")
                safe_metric("Iron", "iron", ".1f", "mg")
                safe_metric("Zinc", "zinc", ".1f", "mg")
                safe_metric("Copper", "copper", ".1f", "mg")
                safe_metric("Manganese", "manganese", ".1f", "mg")
                safe_metric("Selenium", "selenium", ".1f", "mcg")
                safe_metric("Iodine", "iodine", ".1f", "mcg")
                safe_metric("Chromium", "chromium", ".1f", "mcg")
                safe_metric("Molybdenum", "molybdenum", ".1f", "mcg")

            with col3:
                st.write("### 💊 Vitamins")
                safe_metric("Vitamin A", "vitamin_a", ".0f", "IU")
                safe_metric("Vitamin B1", "vitamin_b1", ".2f", "mg")
                safe_metric("Vitamin B2", "vitamin_b2", ".2f", "mg")
                safe_metric("Vitamin B3", "vitamin_b3", ".2f", "mg")
                safe_metric("Vitamin B5", "vitamin_b5", ".2f", "mg")
                safe_metric("Vitamin B6", "vitamin_b6", ".2f", "mg")
                safe_metric("Vitamin B12", "vitamin_b12", ".2f", "mcg")
                safe_metric("Folate", "folate", ".0f", "mcg")
                safe_metric("Vitamin C", "vitamin_c", ".1f", "mg")
                safe_metric("Vitamin D", "vitamin_d", ".0f", "IU")
                safe_metric("Vitamin E", "vitamin_e", ".1f", "mg")
                safe_metric("Vitamin K", "vitamin_k", ".1f", "mcg")

                st.write("### 💧 Other")
                safe_metric("Cholesterol", "cholesterol", ".0f", "mg")
                safe_metric("Water", "water", ".0f", "g")
                safe_metric("Ash", "ash", ".1f", "g")

            # DAILY SUMMARY BUTTON
            if page == "Today's Log":
                st.write("---")
                if st.button("🌟 Daily Health Summary & Coach Review", use_container_width=True, type="secondary"):
                    # Calculate totals using safe methods
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

                    # Build COMPACT daily summary prompt
                    prompt = f"""Daily Review for Umer (21y, 78kg, 1600 kcal goal):

DATE: {today.isoformat()} | {len(df_copy)} meals

MEALS:
"""
                    for idx, meal in df_copy.iterrows():
                        meal_cals = parse_calorie_value(meal['calories'])
                        prompt += f"{idx+1}. {meal['food_name']} ({meal['portion']}) - {meal_cals:.0f} kcal\n"

                    prompt += f"""
TOTALS:
Cals: {total_cals:.0f}/1600 {"🚨 OVER" if total_cals >= 1800 else "✅" if 1400 <= total_cals <= 1600 else "⚠️"}
Protein: {total_protein:.1f}/78-120g | Fat: {total_fat:.1f}/44-62g | Carbs: {total_carbs:.1f}/175-245g
Fiber: {total_fiber:.1f}/25g {"⚠️" if total_fiber < 25 else "✅"} | Sugar: {total_sugar:.1f}/25g {"⚠️" if total_sugar > 25 else "✅"}
Sodium: {total_sodium:.0f}/2000mg {"🚨" if total_sodium > 2000 else "✅"}

Assess: Did I meet goals? Health risks? Tomorrow's plan? Pakistani food suggestions?"""

                    # Display in text area
                    st.success(
                        "📋 Copy this prompt and paste it into your ChatGPT conversation:")
                    st.text_area("Daily Review Prompt", prompt,
                                 height=400, key="daily_prompt")

                    st.markdown("""
                    <a href="https://chatgpt.com/c/691863ca-6930-8322-b1cf-447ba8f4d793" target="_blank">
                        <button style="
                            background-color: #10a37f;
                            color: white;
                            padding: 12px 24px;
                            font-size: 16px;
                            border: none;
                            border-radius: 6px;
                            cursor: pointer;
                            width: 100%;
                        ">
                            🚀 Open Your ChatGPT Conversation
                        </button>
                    </a>
                    """, unsafe_allow_html=True)

                    st.info(
                        "💡 **How to use:** Click the button above to open your ChatGPT conversation, then paste the prompt from the text box above.")

            st.write("---")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                plot_calories_trend(meals_df)
            with col_c2:
                plot_macros_breakdown(meals_df)

            plot_daily_macros(meals_df)

            st.subheader("Detailed Log")
            log_cols = [
                'id', 'date', 'food_name', 'portion', 'calories',
                'protein', 'fat', 'saturated_fat', 'carbs', 'fiber', 'sugar',
                'cholesterol', 'omega_3', 'omega_6',
                'sodium', 'potassium', 'calcium', 'magnesium', 'phosphorus',
                'iron', 'zinc', 'copper', 'manganese', 'selenium', 'iodine',
                'chromium', 'molybdenum',
                'vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_b3',
                'vitamin_b5', 'vitamin_b6', 'vitamin_b12', 'folate',
                'vitamin_c', 'vitamin_d', 'vitamin_e', 'vitamin_k',
                'water', 'ash', 'notes'
            ]
            display_table(meals_df, log_cols)

            st.write("---")
            meal_ids = meals_df['id'].tolist()
            if meal_ids:
                col_d1, col_d2 = st.columns([0.5, 1])
                with col_d1:
                    meal_to_delete = st.selectbox(
                        "Delete an entry (Select ID):",
                        meal_ids,
                        format_func=lambda x: f"ID {x}: {meals_df[meals_df['id'] == x]['food_name'].values[0]}"
                    )
                with col_d2:
                    st.write("")
                    st.write("")
                    if st.button("❌ Permanently Delete Meal Entry", type="secondary"):
                        delete_meal_from_log(meal_to_delete)
                        st.success(f"Meal ID {meal_to_delete} deleted!")
                        st.rerun()
        else:
            st.info("No meals logged for this period. Add a meal above!")

    # ========== SETTINGS PAGE ==========
    elif page == "Settings":
        st.header("⚙️ Settings / Data Management")

        st.subheader("Database Management")
        st.info(
            "The database is automatically saved as `health_tracker.db` in your project folder.")

        if st.button("Run Database Migration (Check for missing columns)"):
            try:
                migrate_database()
                st.success("Database migration completed!")
            except Exception as e:
                st.error(f"Error during migration: {e}")

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
                type="primary"
            )
        else:
            st.warning("No data to export yet.")


if __name__ == "__main__":
    main()
