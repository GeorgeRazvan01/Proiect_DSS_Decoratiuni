from flask import Flask, jsonify, render_template, request
import psycopg2
from psycopg2 import OperationalError
from config import DATABASE_CONFIG

app = Flask(__name__)

# Funcție pentru conectarea la baza de date
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DATABASE_CONFIG['host'],
            port=DATABASE_CONFIG['port'],
            database=DATABASE_CONFIG['database'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password']
        )
        return conn
    except OperationalError as e:
        print(f"Eroare la conectarea la baza de date: {e}")
        return None

# Endpoint pentru a reda pagina principală
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint pentru vânzări pe tip de decor și perioade de timp
@app.route('/api/sales_by_type_and_time', methods=['GET'])
def sales_by_type_and_time():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        return jsonify({"error": "Lipsesc parametrii 'start_date' și 'end_date'."}), 400
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Conexiunea la baza de date a eșuat."}), 500

    cursor = conn.cursor()
    
    query = """
    SELECT d.name, COUNT(s.sale_id) AS sales_count
    FROM decorations d
    JOIN sales s ON d.decoration_id = s.decoration_id
    WHERE s.sale_date BETWEEN %s AND %s
    GROUP BY d.name
    """
    cursor.execute(query, (start_date, end_date))
    
    results = [{"type": row[0], "sales_count": row[1]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(results)

# Endpoint pentru relația dintre profilul clientului și tipurile de decor preferate
@app.route('/api/customer_preferences', methods=['GET'])
def customer_preferences():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Conexiunea la baza de date a eșuat."}), 500

    cursor = conn.cursor()
    
    query = """
    SELECT c.occupation, d.name, COUNT(s.sale_id) AS sales_count
    FROM customers c
    JOIN sales s ON c.customer_id = s.customer_id
    JOIN decorations d ON d.decoration_id = s.decoration_id
    GROUP BY c.occupation, d.name
    ORDER BY c.occupation, sales_count DESC
    """
    cursor.execute(query)
    
    results = [{"occupation": row[0], "decoration_type": row[1], "sales_count": row[2]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(results)

# Endpoint pentru estimarea impactului modificării prețului asupra vânzărilor
@app.route('/api/price_impact', methods=['GET'])
def price_impact():
    decoration_type = request.args.get('type')
    price_change_percentage = request.args.get('percentage')
    
    if not decoration_type or not price_change_percentage:
        return jsonify({"error": "Lipsesc parametrii 'type' și 'percentage'."}), 400
    
    try:
        price_change_percentage = float(price_change_percentage)
    except ValueError:
        return jsonify({"error": "Parametrul 'percentage' trebuie să fie un număr."}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Conexiunea la baza de date a eșuat."}), 500

    cursor = conn.cursor()
    
    query = """
    SELECT AVG(sales_count) * (1 + %s / 100) AS estimated_sales
    FROM (
        SELECT COUNT(s.sale_id) AS sales_count
        FROM decorations d
        JOIN sales s ON d.decoration_id = s.decoration_id
        WHERE d.name = %s
        GROUP BY s.sale_date
    ) AS daily_sales
    """
    cursor.execute(query, (price_change_percentage, decoration_type))
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return jsonify({"type": decoration_type, "estimated_sales": result[0]})

# Endpoint pentru intervalele cu cele mai bune și cele mai slabe vânzări
@app.route('/api/best_worst_sales_intervals', methods=['GET'])
def best_worst_sales_intervals():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Conexiunea la baza de date a eșuat."}), 500

    cursor = conn.cursor()
    
    query = """
    SELECT d.name, s.sale_date, COUNT(s.sale_id) AS sales_count
    FROM decorations d
    JOIN sales s ON d.decoration_id = s.decoration_id
    GROUP BY d.name, s.sale_date
    ORDER BY sales_count DESC
    LIMIT 5
    """
    cursor.execute(query)
    
    results = [{"type": row[0], "date": row[1], "sales_count": row[2]} for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
