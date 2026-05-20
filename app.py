import os
import mysql.connector 
import uuid # For generating unique GCash reference numbers
from datetime import datetime # For the receipt timestamp
from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_key'
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db_config = {
    'host': 'localhost',
    'user': 'root',      
    'password': '',      
    'database': 'platform_db' 
}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db():
    conn = mysql.connector.connect(**db_config)
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (id INT NOT NULL AUTO_INCREMENT, username VARCHAR(255) UNIQUE, 
                       password TEXT, role TEXT, PRIMARY KEY (id))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS platforms 
                      (id INT NOT NULL AUTO_INCREMENT, seller_id INT, category TEXT, 
                       title TEXT, details TEXT, price DOUBLE, acc_email TEXT, 
                       acc_password TEXT, image_url TEXT, status TEXT, PRIMARY KEY (id))''')
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
def index():
    if 'user_id' not in session: 
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True) 
    cursor.execute("SELECT * FROM platforms WHERE status = 'approved' ORDER BY id DESC")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', items=items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        
        if role == 'admin':
            if username == 'admin_master' and password == '123':
                session.update({'user_id': 0, 'username': 'Admin Master', 'role': 'admin'})
                return redirect(url_for('admin_dashboard'))
            return "Invalid Admin Credentials", 401
        
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session.update({'user_id': user['id'], 'username': user['username'], 'role': 'user'})
            return redirect(url_for('index'))
        return "Login failed. Please check your credentials.", 401
            
    return render_template('login.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, 'user')", (username, password))
        conn.commit()
        return redirect(url_for('login'))
    except mysql.connector.Error as err:
        return f"Error: {err}"
    finally:
        cursor.close()
        conn.close()

@app.route('/sell', methods=['POST'])
def sell_request():
    if 'user_id' not in session: 
        return redirect(url_for('login'))
    
    title = request.form.get('title')
    category = request.form.get('category')
    price = request.form.get('price', 0)
    email = request.form.get('email')
    password = request.form.get('password')
    details = request.form.get('details')
    
    file = request.files.get('image')
    filename = ""
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("""INSERT INTO platforms (seller_id, category, title, details, price, acc_email, acc_password, image_url, status) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'pending')""", 
                       (session['user_id'], category, title, details, price, email, password, filename))
        conn.commit()
    except Exception as e:
        print(f"Database Error: {e}")
        return "There was an error saving your post.", 500
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('index'))

@app.route('/admin')
def admin_dashboard():
    if session.get('role') != 'admin': return "Access Denied", 403
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM platforms WHERE status = 'pending'")
    pending = cursor.fetchall()
    cursor.execute("SELECT * FROM platforms WHERE status = 'sold'")
    sold = cursor.fetchall()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin.html', pending=pending, sold=sold, users=users)

@app.route('/approve/<int:item_id>')
def approve(item_id):
    if session.get('role') != 'admin': 
        return "Access Denied", 403
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE platforms SET status = 'approved' WHERE id = %s", (item_id,))
        conn.commit()
    except Exception as e:
        print(f"Approval Error: {e}")
        return "Failed to approve item.", 500
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin_dashboard'))

# --- RE-MAPPED TO USE CHECKOUT.HTML ---

@app.route('/buy/<int:item_id>', methods=['GET', 'POST'])
def buy(item_id):
    if 'user_id' not in session: 
        return redirect(url_for('login'))
    
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Fetch item details
    cursor.execute("SELECT * FROM platforms WHERE id = %s AND status = 'approved'", (item_id,))
    item = cursor.fetchone()
    
    if not item:
        cursor.close()
        conn.close()
        return "Not available.", 404

    # 2. Show the GCash Checkout Form
    if request.method == 'GET':
        cursor.close()
        conn.close()
        # Matches your filename "checkout.html" in VS Code
        return render_template('checkout.html', item=item)

    # 3. Process the Payment and Display Receipt
    if request.method == 'POST':
        # Mark as sold
        cursor.execute("UPDATE platforms SET status = 'sold' WHERE id = %s", (item_id,))
        conn.commit()

        # Capture form data from checkout.html
        gcash_number = request.form.get('gcash_number')
        gcash_amount = request.form.get('gcash_amount')
        # Generate ref if user left it blank
        gcash_ref = request.form.get('gcash_ref') or str(uuid.uuid4().hex[:12]).upper()

        # Data for receipt.html
        receipt_data = {
            'ref': gcash_ref,
            'gcash_amount': float(gcash_amount),
            'paid_at': datetime.now().strftime("%b %d, %Y %I:%M %p"),
            'gcash_number': gcash_number,
            'buyer': session.get('username'),
            'item': item
        }

        cursor.close()
        conn.close()
        
        return render_template('receipt.html', receipt=receipt_data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5001, debug=True)