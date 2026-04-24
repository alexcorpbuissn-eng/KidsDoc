from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)
DB_NAME = "clinic_bot.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    try:
        conn = get_db_connection()
        
        # Get total users
        users = conn.execute('SELECT * FROM users').fetchall()
        total_users = len(users)
        
        # Get unique services for dropdown
        services_query = conn.execute('SELECT DISTINCT service_name FROM reviews WHERE service_name IS NOT NULL').fetchall()
        services = ["All Services"] + sorted([row['service_name'] for row in services_query if row['service_name']])
        
        # Get selected service filter
        selected_service = request.args.get('service', 'All Services')
        
        # Build reviews query
        if selected_service == 'All Services':
            reviews = conn.execute('''
                SELECT r.id, r.user_id, u.username, u.first_name, 
                       r.service_name, r.rating, r.review_text, r.review_date 
                FROM reviews r 
                LEFT JOIN users u ON r.user_id = u.user_id
            ''').fetchall()
        else:
            reviews = conn.execute('''
                SELECT r.id, r.user_id, u.username, u.first_name, 
                       r.service_name, r.rating, r.review_text, r.review_date 
                FROM reviews r 
                LEFT JOIN users u ON r.user_id = u.user_id
                WHERE r.service_name = ?
            ''', (selected_service,)).fetchall()
            
        total_reviews_filtered = len(reviews)
        all_reviews_count = conn.execute('SELECT COUNT(*) FROM reviews').fetchone()[0]
        
        conn.close()
        
        return render_template(
            'dashboard.html', 
            users=users, 
            reviews=reviews, 
            total_users=total_users, 
            total_reviews=all_reviews_count,
            filtered_reviews_count=total_reviews_filtered,
            services=services,
            selected_service=selected_service,
            error=None
        )
    except Exception as e:
        return render_template('dashboard.html', error=str(e))

if __name__ == '__main__':
    app.run(debug=True, port=8501)
