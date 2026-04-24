from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# Use PythonAnywhere path if running there
if os.path.exists("/home/KidsDoc"):
    DB_NAME = "/home/KidsDoc/KidsDoc/clinic_bot.db"
else:
    DB_NAME = "clinic_bot.db"

# Language Translations
TRANSLATIONS = {
    'en': {
        'title': '🏥 Clinic Bot Dashboard',
        'quick_stats': 'Quick Stats',
        'total_users': 'Total Users',
        'total_reviews': 'Total Reviews',
        'avg_rating': 'Overall Rating',
        'reg_users': '👥 Registered Users',
        'feedback': '⭐ Feedback & Reviews',
        'filter_label': 'Select a Service Category to Filter:',
        'all_services': 'All Services',
        'detailed_reviews': 'Detailed Reviews',
        'no_reviews': 'No reviews yet for',
        'user': 'User',
        'rating': 'Rating'
    },
    'ru': {
        'title': '🏥 Панель управления ботом клиники',
        'quick_stats': 'Краткая статистика',
        'total_users': 'Всего пользователей',
        'total_reviews': 'Всего отзывов',
        'avg_rating': 'Средний рейтинг',
        'reg_users': '👥 Зарегистрированные пользователи',
        'feedback': '⭐ Отзывы и оценки',
        'filter_label': 'Выберите категорию услуг для фильтрации:',
        'all_services': 'Все услуги',
        'detailed_reviews': 'Подробные отзывы',
        'no_reviews': 'Пока нет отзывов для',
        'user': 'Пользователь',
        'rating': 'Оценка'
    },
    'uz': {
        'title': '🏥 Klinika boti paneli',
        'quick_stats': 'Qisqacha statistika',
        'total_users': 'Jami foydalanuvchilar',
        'total_reviews': 'Jami sharhlar',
        'avg_rating': 'O‘rtacha reyting',
        'reg_users': '👥 Ro‘yxatdan o‘tgan foydalanuvchilar',
        'feedback': '⭐ Sharhlar va baholar',
        'filter_label': 'Filtrlash uchun xizmat turini tanlang:',
        'all_services': 'Barcha xizmatlar',
        'detailed_reviews': 'Batafsil sharhlar',
        'no_reviews': 'Hozircha sharhlar yo‘q:',
        'user': 'Foydalanuvchi',
        'rating': 'Baho'
    }
}

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    try:
        conn = get_db_connection()
        
        # Get language
        lang = request.args.get('lang', 'en')
        if lang not in TRANSLATIONS:
            lang = 'en'
        t = TRANSLATIONS[lang]
        
        # Get total users
        users = conn.execute('SELECT * FROM users').fetchall()
        total_users = len(users)
        
        # Get unique services for dropdown
        services_query = conn.execute('SELECT DISTINCT service_name FROM reviews WHERE service_name IS NOT NULL').fetchall()
        services = [t['all_services']] + sorted([row['service_name'] for row in services_query if row['service_name']])
        
        # Get selected service filter
        selected_service = request.args.get('service', t['all_services'])
        
        # Build reviews query
        if selected_service == t['all_services'] or selected_service == 'All Services':
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
        
        # Calculate Average Rating
        avg_rating = 0
        if total_reviews_filtered > 0:
            total_score = sum([r['rating'] for r in reviews if r['rating']])
            avg_rating = round(total_score / total_reviews_filtered, 2)
        
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
            avg_rating=avg_rating,
            lang=lang,
            t=t,
            error=None
        )
    except Exception as e:
        return render_template('dashboard.html', error=str(e), t=TRANSLATIONS['en'], lang='en')

if __name__ == '__main__':
    app.run(debug=True, port=8501)
