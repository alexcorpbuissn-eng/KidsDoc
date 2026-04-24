import streamlit as st
import sqlite3
import pandas as pd

# Connect to database
DB_NAME = "clinic_bot.db"

def load_data(query):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

st.set_page_config(page_title="Clinic Bot Dashboard", layout="wide")

st.title("🏥 Clinic Bot Dashboard")

try:
    # Load data
    users_df = load_data("SELECT * FROM users")
    reviews_df = load_data("""
        SELECT r.id, r.user_id, u.username, u.first_name, 
               r.service_name, r.rating, r.review_text, r.review_date 
        FROM reviews r 
        LEFT JOIN users u ON r.user_id = u.user_id
    """)

    # Top metrics
    st.markdown("### Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Users", len(users_df))
    with col2:
        st.metric("Total Reviews", len(reviews_df))

    st.markdown("---")

    # Users Table
    st.subheader("👥 Registered Users")
    st.dataframe(users_df, use_container_width=True)

    st.markdown("---")

    # Reviews Table
    st.subheader("⭐ Feedback & Reviews")

    # Filter by Category
    services = ["All Services"] + sorted(reviews_df['service_name'].dropna().unique().tolist())
    selected_service = st.selectbox("Select a Service Category to Filter:", services)

    if selected_service == "All Services":
        filtered_reviews = reviews_df
    else:
        filtered_reviews = reviews_df[reviews_df['service_name'] == selected_service]

    st.markdown(f"**Total Reviews for {selected_service}:** {len(filtered_reviews)}")

    st.dataframe(
        filtered_reviews, 
        use_container_width=True,
        column_config={
            "review_text": st.column_config.TextColumn("Review Text", width="large")
        }
    )
    
    st.markdown("### Detailed Reviews")
    if filtered_reviews.empty:
        st.info(f"No reviews yet for {selected_service}.")
    else:
        for index, row in filtered_reviews.iterrows():
            with st.chat_message("user"):
                username = f"@{row['username']}" if pd.notna(row['username']) and row['username'] else ""
                first_name = row['first_name'] if pd.notna(row['first_name']) and row['first_name'] else "Unknown User"
                user_display = f"{first_name} {username}".strip()
                
                st.markdown(f"**{row['service_name'].upper()}** (User: {user_display})")
                st.write(f"*{row['review_date']}* | Rating: {row['rating']} ⭐")
                st.info(row['review_text'])

except sqlite3.OperationalError as e:
    st.error(f"Error connecting to database. Please make sure the bot has run at least once to create the 'clinic_bot.db' file. Error details: {e}")
except Exception as e:
    st.error(f"An error occurred: {e}")
