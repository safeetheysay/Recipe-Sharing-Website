from flask import Flask, session, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from PIL import Image
from functools import wraps
from flask import jsonify
import mimetypes
from datetime import datetime, timedelta

# Force correct MIME types
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js') 

app = Flask(__name__)
app.secret_key = "secret123"

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="python assignment"
    )
    return conn

app.config['UPLOAD_FOLDER'] = 'static/uploads/recipes'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""SELECT r.*, u.username, 
                      (SELECT AVG(rating) FROM reviews WHERE recipe_id = r.id) as avg_rating
                      FROM recipes r 
                      JOIN users u ON r.user_id = u.id 
                      WHERE r.status = 'approved'
                      ORDER BY r.created_at DESC""")
    recipes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('index.html', recipes=recipes)



def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login to access this page.")
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return wrapper

def clean_old_notifications():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""DELETE FROM notifications WHERE created_at < Date_SUB(NOW(), INTERVAL 2 DAY)""")

    deleted_count = cursor.rowcount
    conn.commit()
    cursor.close()
    conn.close()

    print(f"🧹 Cleaned up {deleted_count} notifications older than 3 days")
    return deleted_count

def check_password_reminder():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT id, username, password_last_changed 
        FROM users 
        WHERE password_last_changed IS NOT NULL 
        AND DATE_ADD(password_last_changed, INTERVAL 15 DAY) <= NOW()
        AND role = 'user'
    """)
    users_needing_reminder = cursor.fetchall()
    
    for user in users_needing_reminder:
        # FIX: Check by notification type instead of message text
        cursor.execute("""
            SELECT id FROM notifications 
            WHERE user_id = %s 
            AND commenter_id = %s  # Using commenter_id as self to identify password reminders
            AND DATE(created_at) = CURDATE()
        """, (user['id'], user['id']))
        existing_reminder = cursor.fetchone()

        if not existing_reminder:
            # Create new reminder notification
            cursor.execute("""
                INSERT INTO notifications (user_id, commenter_id, message, is_read, created_at) 
                VALUES (%s, %s, %s, %s, %s)
            """, (
                user['id'], 
                user['id'],  # Using user's own ID as commenter_id to mark as password reminder
                "Password Reminder: It's been 15 days since your last password change. Consider updating your password for security.", 
                0, 
                datetime.now()
            ))
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/admin_login', methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        identifier = request.form.get('identifier') 
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE (username=%s OR email=%s) AND role='admin'", (identifier, identifier))
        user = cursor.fetchone()

        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user['role']
            session['phone'] = user.get('phone', '')
            session['cnic'] = user.get('cnic', '')
            session['picture'] = user.get('picture', '')

            cursor.execute("SELECT COUNT(*) as count FROM recipes WHERE status = 'pending'")
            pending_count = cursor.fetchone()['count']
            
            cursor.close()
            conn.close()

            return redirect(url_for('admin_profile'))  
        else:
            flash("❌ Invalid Admin Username or Password")
            cursor.close()
            conn.close()
            return redirect(url_for('admin_login'))
    
    return render_template('adminlogin.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    clean_old_notifications()
    check_password_reminder()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get quick stats for dashboard
    cursor.execute("SELECT COUNT(*) as total_users FROM users WHERE role = 'user'")
    total_users = cursor.fetchone()['total_users']
    
    cursor.execute("SELECT COUNT(*) as pending_count FROM recipes WHERE status = 'pending'")
    pending_count = cursor.fetchone()['pending_count']
    
    cursor.execute("SELECT COUNT(*) as total_recipes FROM recipes")
    total_recipes = cursor.fetchone()['total_recipes']
    
    cursor.execute("SELECT COUNT(*) as feedback_count FROM feedbacks")
    feedback_count = cursor.fetchone()['feedback_count']
    
    cursor.close()
    conn.close()
    
    return render_template('AdminHome.html', 
                         total_users=total_users,
                         pending_count=pending_count,
                         total_recipes=total_recipes,
                         feedback_count=feedback_count,
                         )

@app.route('/admin/Admin_Manage_Recipes')
def admin_manage_recipes():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get all recipes for management - ADD AVG_RATING TO ALL QUERIES
    cursor.execute("""SELECT r.*, u.username,
                      (SELECT AVG(rating) FROM reviews WHERE recipe_id = r.id) as avg_rating
                      FROM recipes r 
                      JOIN users u ON r.user_id = u.id 
                      WHERE r.status = 'pending'
                      ORDER BY r.created_at DESC""")
    pending_recipes = cursor.fetchall()

    cursor.execute("""SELECT r.*, u.username,
                      (SELECT AVG(rating) FROM reviews WHERE recipe_id = r.id) as avg_rating
                      FROM recipes r 
                      JOIN users u ON r.user_id = u.id 
                      WHERE r.status = 'rejected'
                      ORDER BY r.created_at DESC""")
    rejected_recipes = cursor.fetchall()

    cursor.execute("""SELECT r.*, u.username,
                      (SELECT AVG(rating) FROM reviews WHERE recipe_id = r.id) as avg_rating
                      FROM recipes r 
                      JOIN users u ON r.user_id = u.id 
                      WHERE r.status = 'approved'
                      ORDER BY r.created_at DESC""")
    approved_recipes = cursor.fetchall()

    cursor.execute("""
        SELECT f.id, f.message, f.email, f.created_at, u.username
        FROM feedbacks f
        JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
    """)
    feedbacks = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('Admin_Manage_Recipes.html', 
                         pending_recipes=pending_recipes, 
                         approved_recipes=approved_recipes,
                         rejected_recipes=rejected_recipes,
                         feedbacks=feedbacks,
                         dashboard=True)

@app.route('/admin/View_feedbacks')
@login_required
def view_feedbacks():

    conn= get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT f.id, f.message, f.email, f.created_at, u.username
        FROM feedbacks f
        JOIN users u ON f.user_id = u.id
        ORDER BY f.created_at DESC
    """)
    feedbacks = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('Feedbacks.html',feedbacks=feedbacks,dashboard=True)


@app.route('/admin/approve_recipe/<int:recipe_id>')
def approve_recipe(recipe_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE recipes SET status = 'approved' WHERE id = %s", (recipe_id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    flash("✅ Recipe approved successfully!")
    return redirect(url_for('admin_manage_recipes'))


@app.route('/admin/reject_recipe/<int:recipe_id>')
def reject_recipe(recipe_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("UPDATE recipes SET status = 'rejected' WHERE id = %s", (recipe_id,))
    conn.commit()
    
    cursor.close()
    conn.close()
    
    flash("✅ Recipe rejected successfully!")
    return redirect(url_for('admin_manage_recipes'))

@app.route('/admin/recipe/<int:recipe_id>')
def admin_view_recipe(recipe_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT r.*, u.username, 
               (SELECT AVG(rating) FROM reviews WHERE recipe_id = r.id) as avg_rating
        FROM recipes r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.id = %s
    """, (recipe_id,))
    recipe = cursor.fetchone()
    
    if not recipe:
        flash("❌ Recipe not found")
        return redirect(url_for('admin_manage_recipes'))
    
    cursor.execute("""
        SELECT rr.*, u.username 
        FROM reviews rr 
        JOIN users u ON rr.user_id = u.id 
        WHERE rr.recipe_id = %s 
        ORDER BY rr.created_at DESC
    """, (recipe_id,))
    reviews = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('admin_view_recipe.html', recipe=recipe, reviews=reviews)


import os
@app.route('/admin/delete_user/<int:user_id>')
def admin_delete_user(user_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT role, picture FROM users WHERE id = %s", (user_id,))
    target_user = cursor.fetchone()

    if not target_user:
        flash("❌ User not found")
        cursor.close()
        conn.close()
        return redirect(url_for('manage_users'))

    if target_user['role'] == 'admin':
        flash("⚠️ You cannot delete another admin account")
        cursor.close()
        conn.close()
        return redirect(url_for('manage_users'))

    try:
        cursor.execute("DELETE FROM notifications WHERE comment_id IN (SELECT id FROM comments WHERE user_id = %s)", (user_id,))
        cursor.execute("DELETE FROM notifications WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM comments WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM reviews WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM favorites WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM feedbacks WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM recipes WHERE user_id = %s", (user_id,))
        
        if target_user['picture']:
            pic_path = os.path.join(app.root_path, 'static', target_user['picture'])
            if os.path.exists(pic_path):
                os.remove(pic_path)

        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))

        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ User Account & All Data Deleted Successfully!")
        return redirect(url_for('manage_users'))
        
    except Exception as e:
        conn.rollback()
        cursor.close()
        conn.close()
        flash(f"❌ Error deleting user: {str(e)}")
        return redirect(url_for('manage_users'))




@app.route('/admin/delete_recipe/<int:recipe_id>')
def admin_delete_recipe(recipe_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM recipes WHERE id = %s", (recipe_id,))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("✅ Recipe deleted successfully!")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/users')
def manage_users():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT id, username, email, phone, cnic, role, picture FROM users WHERE role = 'user' ORDER BY id")
    users = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('UserManager.html', users=users,dashboard=True)


@app.route('/admin/profile')
def admin_profile():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    if user:
        session['username'] = user['username']
        session['email'] = user['email']
        session['phone'] = user.get('phone', '')
        session['cnic'] = user.get('cnic', '')
        session['picture'] = user.get('picture', '')

    cursor.close()
    conn.close()

    return render_template('AdminHome.html', user=user)

@app.route('/admin/update_profile', methods=['POST'])
def admin_update_profile():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    if not user:
        flash("❌ User not found")
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        
        if 'remove_picture' in request.form:
            if user['picture']:
                old_image_path = os.path.join('static', user['picture'])
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            cursor.execute("UPDATE users SET picture='' WHERE id=%s", (session['user_id'],))
            session['picture'] = ''
            
            conn.commit()
            cursor.close()
            conn.close()
            flash("✅ Profile picture removed successfully!")
            return redirect(url_for('admin_profile'))

        user_id = session['user_id']
        
        username = request.form.get('username', user['username'])
        email = request.form.get('email', user['email'])
        phone = request.form.get('phone', user.get('phone', ''))
        cnic = request.form.get('cnic', user.get('cnic', ''))
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        picture_path = user['picture']

        if 'picture' in request.files:
            file = request.files['picture']
            if file and file.filename != '' and allowed_file(file.filename):
                if user['picture']:
                    old_image_path = os.path.join('static', user['picture'])
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                filename = secure_filename(file.filename)
                unique_filename = f"admin_{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                filepath = os.path.join('static/uploads/users', unique_filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)

                try:
                    img = Image.open(filepath)
                    img.thumbnail((500, 500))
                    img.save(filepath)
                except:
                    pass

                picture_path = f"uploads/users/{unique_filename}"
        
        if username != user['username'] or email != user['email']:
            cursor.execute("SELECT * FROM users WHERE (username = %s OR email = %s) AND id != %s", (username, email, session['user_id']))
            if cursor.fetchone():
                flash("❌ Username or Email already exists! Choose another username/email") 
                cursor.close()
                conn.close()
                return redirect(url_for('admin_profile'))

        update_query = "UPDATE users SET username=%s, email=%s, phone=%s, cnic=%s, picture=%s WHERE id=%s"
        cursor.execute(update_query, (username, email, phone, cnic, picture_path, session['user_id']))

        if current_password and new_password and confirm_password:
            if current_password != user['password']:
                flash("❌ Current password is incorrect")
                cursor.close()
                conn.close()
                return redirect(url_for('admin_profile'))
            
            if new_password != confirm_password:
                flash("❌ New password and confirm password do not match")
                cursor.close()
                conn.close()
                return redirect(url_for('admin_profile'))
            
            cursor.execute("UPDATE users SET password=%s, password_last_changed=%s WHERE id=%s", (new_password,datetime.now(), session['user_id']))
            
            flash("✅ Password updated successfully!")  
        else:
            flash("✅ Profile updated successfully!")

        session['email'] = email
        session['username'] = username
        session['picture'] = picture_path
        session['phone'] = phone
        session['cnic'] = cnic

        session.modified = True

        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('admin_profile'))



@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        identifier = request.form.get('identifier')
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE (username=%s OR email=%s) AND role='user'", (identifier, identifier))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['email'] = user['email']
            session['role'] = user['role']
            session['picture'] = user['picture']
            
            
            flash("✅ Login successful!")
            return redirect(url_for('profile'))
        else:
            flash("❌ Invalid Username/Email or Password")
            return redirect(url_for('user_login'))
    
    return render_template('user_login.html')


@app.route('/profile')
def profile():
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('user_login'))
    
    clean_old_notifications()
    check_password_reminder()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    session['phone'] = user['phone']
    session['cnic'] = user['cnic']

    cursor.close()
    conn.close()

    return render_template('Profile.html')
    
@app.route('/manage_recipes')
def manage_recipes():
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('user_login'))
    
    clean_old_notifications()
    check_password_reminder()
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()
    
    # FIX: Add avg_rating to the main recipes query
    cursor.execute("""
        SELECT r.*, 
               (SELECT AVG(rating) FROM reviews WHERE recipe_id = r.id) as avg_rating
        FROM recipes r 
        WHERE r.user_id = %s 
        ORDER BY r.created_at DESC
    """, (session['user_id'],))
    recipes = cursor.fetchall()

    # Load comments for user's own recipes
    for recipe in recipes:
        cursor.execute("""
            SELECT c.*, u.username
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.recipe_id = %s
            ORDER BY c.created_at DESC
        """, (recipe['id'],))
        recipe['comments'] = cursor.fetchall()
        recipe['comment_count'] = len(recipe['comments'])  
    
    cursor.close()
    conn.close()
    
    return render_template('ManageRecipes.html', user=user, recipes=recipes, show_bell_only=True, show_search=True)


@app.route('/All_recipes')
@login_required
def All_recipes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    clean_old_notifications()
    check_password_reminder()

    try:
        cursor.execute("""SELECT r.*, u.username,
                          (SELECT AVG(rating) FROM reviews WHERE recipe_id = r.id) as avg_rating,
                          EXISTS(SELECT 1 FROM favorites f WHERE f.user_id = %s AND f.recipe_id = r.id) as is_favorited,
                       (SELECT COUNT(*) FROM comments WHERE recipe_id = r.id) as comment_count
                          FROM recipes r 
                          JOIN users u ON r.user_id = u.id 
                          WHERE r.status = 'approved' AND r.user_id != %s
                          ORDER BY r.created_at DESC""", (session['user_id'], session['user_id']))
        community_recipes = cursor.fetchall() 

        # Load comments for each recipe
        for recipe in community_recipes:
            cursor.execute("""
                           SELECT c.*, u.username
                           FROM comments c
                           JOIN users u ON c.user_id = u.id
                           WHERE c.recipe_id = %s
                           ORDER BY c.created_at DESC
                           """, (recipe['id'],))
            recipe['comments'] = cursor.fetchall()

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        community_recipes = []
    finally:
        
        cursor.close()
        conn.close()
    
    return render_template('All_recipes.html', community_recipes=community_recipes, show_bell_only=True, show_search=True)

@app.route('/add_recipe', methods=['GET', 'POST'])
def add_recipe():
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('user_login'))
    
    if request.method == 'POST':
        title = request.form['title']
        ingredients = request.form['ingredients']
        steps = request.form['steps']
        category = request.form['category']
        user_id = session['user_id']

        image_path = None
        if 'recipe_image' in request.files:
            file = request.files['recipe_image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)

                try:
                    img = Image.open(filepath)
                    img.thumbnail((800,800))
                    img.save(filepath)
                except:
                    pass

                image_path = f"uploads/recipes/{unique_filename}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO recipes (title, ingredients, steps, category, user_id, image_path) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, ingredients, steps, category, user_id, image_path))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("✅ Recipe submitted for approval!")
        return redirect(url_for('manage_recipes'))
    
    return render_template('add_recipe.html', show_bell_only=True)


@app.route('/edit_recipe/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('user_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM recipes WHERE id = %s AND user_id = %s", (recipe_id, session['user_id']))
    recipe = cursor.fetchone()
    
    if not recipe:
        flash("❌ Recipe not found or you don't have permission to edit it")
        return redirect(url_for('profile'))
    
    if request.method == 'POST':
        title = request.form['title']
        ingredients = request.form['ingredients']
        steps = request.form['steps']
        category = request.form['category']

        image_path = recipe['image_path']

        if 'recipe_image' in request.files:
            file = request.files['recipe_image']
            if file and allowed_file(file.filename):
                if recipe['image_path']:
                    old_image_path = os.path.join('static', recipe['image_path'])
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                filename = secure_filename(file.filename)
                unique_filename = f"{session['user_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)

                try:
                    img = Image.open(filepath)
                    img.thumbnail((800,800))
                    img.save(filepath)
                except:
                    pass

                image_path = f"uploads/recipes/{unique_filename}"
        
        cursor.execute("""
            UPDATE recipes SET title=%s, ingredients=%s, steps=%s, category=%s, image_path=%s
            WHERE id=%s
        """, (title, ingredients, steps, category, image_path, recipe_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        flash("✅ Recipe updated successfully!")
        return redirect(url_for('manage_recipes'))
    
    cursor.close()
    conn.close()
    return render_template('edit_recipe.html', recipe=recipe)

@app.route('/delete_recipe/<int:recipe_id>')
def delete_recipe(recipe_id):
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('user_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM recipes WHERE id = %s AND user_id = %s", (recipe_id, session['user_id']))
    recipe = cursor.fetchone()
    
    if not recipe:
        flash("❌ Recipe not found or you don't have permission to delete it")
        return redirect(url_for('profile'))
    
    if recipe[5]:  # image_path index
        old_image_path = os.path.join('static', recipe[5])
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
    
    cursor.execute("DELETE FROM recipes WHERE id = %s", (recipe_id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash("✅ Recipe deleted successfully!")
    return redirect(url_for('profile'))


@app.route('/recipe/<int:recipe_id>')
def view_recipe(recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT r.*, u.username, 
               (SELECT AVG(rating) FROM reviews WHERE recipe_id = r.id) as avg_rating,
               (SELECT COUNT(*) FROM comments WHERE recipe_id = r.id) as comment_count
        FROM recipes r 
        JOIN users u ON r.user_id = u.id 
        WHERE r.id = %s
    """, (recipe_id,))
    recipe = cursor.fetchone()
    
    if not recipe:
        flash("❌ Recipe not found")
        return redirect(url_for('index'))
    
    # Get comments for this recipe
    cursor.execute("""
        SELECT c.*, u.username 
        FROM comments c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.recipe_id = %s 
        ORDER BY c.created_at DESC
    """, (recipe_id,))
    comments = cursor.fetchall()
    recipe['comments'] = comments
    
    is_favorited = False
    if 'user_id' in session:
        cursor.execute("SELECT id FROM favorites WHERE user_id=%s AND recipe_id=%s", (session['user_id'], recipe_id))
        if cursor.fetchone():
            is_favorited = True
    
    cursor.execute("""
        SELECT rr.*, u.username 
        FROM reviews rr 
        JOIN users u ON rr.user_id = u.id 
        WHERE rr.recipe_id = %s 
        ORDER BY rr.created_at DESC
    """, (recipe_id,))
    reviews = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('view_recipe.html', recipe=recipe, reviews=reviews, comments=comments, is_favorited=is_favorited)


@app.route('/add_review/<int:recipe_id>', methods=['GET', 'POST'])
def add_review(recipe_id):
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('user_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM recipes WHERE id = %s", (recipe_id,))
    recipe = cursor.fetchone()
    
    if not recipe:
        flash("❌ Recipe not found")
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        rating = request.form['rating']
        comment = request.form['comment']
        user_id = session['user_id']
        user_email = session['email']
        title = recipe['title']
        
        cursor.execute("SELECT * FROM reviews WHERE recipe_id = %s AND user_id = %s", (recipe_id, user_id))
        existing_review = cursor.fetchone()
        
        if existing_review:
            flash("❌ You have already reviewed this recipe")
            return redirect(url_for('view_recipe', recipe_id=recipe_id))
        
        cursor.execute("""
            INSERT INTO reviews (recipe_id, title, rating, comment, user_id, user_email)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (recipe_id, title, rating, comment, user_id, user_email))

        conn.commit()
        cursor.close()
        conn.close()
        
        flash("✅ Review submitted successfully!")
        return redirect(url_for('All_recipes', recipe_id=recipe_id))
    
    cursor.close()
    conn.close()
    return render_template('add_review.html', recipe=recipe)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        phone = request.form['phone']
        cnic = request.form['cnic']

        picture_path = None
        if 'picture' in request.files:
            file = request.files['picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                filepath = os.path.join('static/uploads/users', unique_filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)

                # resize to avoid oversized images
                try:
                    img = Image.open(filepath)
                    img.thumbnail((500, 500))
                    img.save(filepath)
                except:
                    pass

                picture_path = f"uploads/users/{unique_filename}"

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            flash("❌ Username already exists")
            cursor.close()
            conn.close()
            return redirect(url_for('register'))

        cursor.execute("""
            INSERT INTO users (username, email, password, picture, phone, cnic, role)
            VALUES (%s, %s, %s, %s, %s, %s, 'user')
        """, (username, email, password, picture_path, phone, cnic))
        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Registration successful! Please login.")
        return redirect(url_for('user_login'))

    return render_template('RegUser.html')


@app.route('/add_feedback', methods=['GET', 'POST'])
def feedbacks():
    if 'user_id' not in session:
        flash("❌ Please login first to give feedback")
        return redirect(url_for('user_login'))
    
    if request.method == 'POST':
        user_id = session['user_id']
        email = request.form['email']
        message = request.form['message']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO feedbacks (user_id, email, message) VALUES (%s, %s, %s)",
            (user_id, email, message)
        )

        conn.commit()
        cursor.close()
        conn.close()

        flash("✅ Feedback submitted successfully!")
        return redirect(url_for('profile'))

    # If GET, show feedback form page
    return render_template("add_feedback.html",show_bell_only=True)


@app.route('/search', methods=['GET', 'POST'])
def search_recipe():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()

    query = """
    SELECT r.id, r.title, r.ingredients, r.steps, r.image_path, r.category, u.username FROM recipes r
    join users u ON r.user_id = u.id
    WHERE r.status = 'approved' """

    params = []

    if keyword:
        query += "AND (r.title LIKE %s OR r.ingredients LIKE %s)"
        like_kw = f"%{keyword}%"
        params.extend([like_kw,like_kw])

    if category and category != "all":
       query += "AND r.category = %s"
       params.append(category)


    cursor.execute(query, tuple(params))
    recipes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("search_results.html", recipes=recipes, keyword=keyword, category=category, show_search=True, show_bell_only=True)

@app.route('/update_profile', methods=['GET', 'POST'])
def update_profile():
    if 'user_id' not in session or session['role'] != 'user':
        return redirect(url_for('user_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE id = %s", (session['user_id'],))
    user = cursor.fetchone()

    if not user:
        flash("❌ User not found")
        return redirect(url_for('user_login'))
    
    if request.method == 'POST':
        
        if 'remove_picture' in request.form:
            if user['picture']:
                old_image_path = os.path.join('static', user['picture'])
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            cursor.execute("UPDATE users SET picture='' WHERE id=%s", (session['user_id'],))
            session['picture'] = ''
            
            conn.commit()
            cursor.close()
            conn.close()
            flash("✅ Profile picture removed successfully!")
            return redirect(url_for('profile'))

        user_id = session['user_id']
        
        username = request.form.get('username', user['username'])
        email = request.form.get('email', user['email'])
        phone = request.form.get('phone', user.get('phone', ''))
        cnic = request.form.get('cnic', user.get('cnic', ''))
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        picture_path = user['picture']

        if 'picture' in request.files:
            file = request.files['picture']
            if file and file.filename != '' and allowed_file(file.filename):
                if user['picture']:
                    old_image_path = os.path.join('static', user['picture'])
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                filename = secure_filename(file.filename)
                unique_filename = f"{username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                filepath = os.path.join('static/uploads/users', unique_filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)

                try:
                    img = Image.open(filepath)
                    img.thumbnail((500, 500))
                    img.save(filepath)
                except:
                    pass

                picture_path = f"uploads/users/{unique_filename}"
        
        if username != user['username'] or email != user['email']:
            cursor.execute("SELECT * FROM users WHERE (username = %s OR email = %s) AND id != %s", (username, email, session['user_id']))
            if cursor.fetchone():
                flash("❌ Username or Email already exists! Choose another username/email") 
                cursor.close()
                conn.close()
                return redirect(url_for('update_profile'))

        update_query = "UPDATE users SET username=%s, email=%s, phone=%s, cnic=%s, picture=%s WHERE id=%s"
        cursor.execute(update_query, (username, email, phone, cnic, picture_path, session['user_id']))

        if current_password and new_password and confirm_password:
            if current_password != user['password']:
                flash("❌ Current password is incorrect")
                cursor.close()
                conn.close()
                return redirect(url_for('update_profile'))
            
            if new_password != confirm_password:
                flash("❌ New password and confirm password do not match")
                cursor.close()
                conn.close()
                return redirect(url_for('update_profile'))
            
            cursor.execute("UPDATE users SET password=%s, password_last_changed=%s WHERE id=%s", (new_password, datetime.now(), session['user_id']))
            flash("✅ Password updated successfully!")  

            
        else:
            flash("✅ Profile updated successfully!")

        # Update session
        session['email'] = email
        session['username'] = username
        session['picture'] = picture_path
        session['phone'] = phone
        session['cnic'] = cnic
        if new_password:
            session['password'] = new_password

        conn.commit()
        cursor.close()
        conn.close()
        
        return redirect(url_for('profile'))
    
    return render_template('Profile.html', user=user)

@app.route('/logout')
def logout():

    role = session.get('role') 
    session.clear()
    flash("✅ Logged out successfully!")

    if role == 'admin':
       return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('user_login'))

@app.route('/favorite/<int:recipe_id>', methods=['GET','POST'])
@login_required
def toggle_favorite(recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    user_id = session['user_id']

    cursor.execute("SELECT id FROM favorites WHERE user_id=%s AND recipe_id=%s", (user_id, recipe_id))
    existing = cursor.fetchone()

    if existing: 
        cursor.execute("DELETE FROM favorites WHERE id=%s", (existing['id'],))
        conn.commit()
        favorited = False
        flash("💔 Removed from favorites!")
    else:
        # First get the recipe title
        cursor.execute("SELECT title FROM recipes WHERE id=%s", (recipe_id,))
        recipe = cursor.fetchone()
        recipe_title = recipe['title'] if recipe else "Unknown Recipe"
        
        # Insert with recipe title
        cursor.execute("INSERT INTO favorites (user_id, recipe_id, recipe_title) VALUES (%s, %s, %s)", 
                      (user_id, recipe_id, recipe_title))
        conn.commit()
        favorited = True
        flash("❤️ Added to favorites!")

    cursor.close()
    conn.close()

    return jsonify({
        'favorited': favorited,
        'message': 'Favorite updated Successfully.'
    })

@app.route('/my_favorites')
@login_required
def my_favorites():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    user_id = session['user_id']
    username = session['username']
    
   
    cursor.execute("""
        SELECT r.*, u.username as username
        FROM recipes r 
        JOIN favorites f ON r.id = f.recipe_id 
        JOIN users u ON r.user_id = u.id
        WHERE f.user_id = %s
    """, (user_id,))
    
    recipes = cursor.fetchall()
    
    for recipe in recipes:
        cursor.execute("""
            SELECT c.*, u.username 
            FROM comments c 
            JOIN users u ON c.user_id = u.id 
            WHERE c.recipe_id = %s 
            ORDER BY c.created_at DESC
        """, (recipe['id'],))
        recipe['comments'] = cursor.fetchall()
        recipe['comment_count'] = len(recipe['comments'])
    
    cursor.close()
    conn.close()

    return render_template('my_favorites.html', recipes=recipes, username=username, show_bell_only=True)

@app.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    user_id = session['user_id']
    role = session['role']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if role == 'admin':
        flash("⚠️ Admin accounts cannot be deleted")
        return redirect(url_for('admin_profile'))
    cursor.execute("SELECT picture FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    if user and user['picture']:
        pic_path = os.path.join(app.root_path,'static', user['picture'])

        if os.path.exists(pic_path):
            os.remove(pic_path)

    cursor.execute("DELETE from users WHERE id=%s", (user_id,))

    conn.commit()
    conn.close()
    cursor.close()
            
    session.clear()
    flash("✅ Your account has been deleted Successfully")
    return redirect(url_for('user_login'))

@app.route('/recipe/<int:recipe_id>/comments', methods=['POST'])
@login_required
def comments(recipe_id):
    if request.method == 'POST':
        comment_text = request.form['comment_text']
        user_id = session['user_id']
        username = session['username'] 
    
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
                       INSERT INTO comments (recipe_id, user_id, comment_text)
                       VALUES(%s,%s,%s)
                       """, (recipe_id, user_id, comment_text))
        
        comment_id = cursor.lastrowid

        cursor.execute("SELECT user_id FROM recipes WHERE id=%s", (recipe_id,))
        recipe = cursor.fetchone()

        
        if recipe and recipe['user_id'] != session['user_id']:
            cursor.execute("""
                           INSERT INTO notifications (user_id, recipe_id, comment_id, commenter_id, message)
                           VALUES(%s,%s,%s,%s,%s)
                           """, (recipe['user_id'], recipe_id, comment_id, session['user_id'], f"{session['username']} commented on your recipe."))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'comment_id': comment_id,
            'username': username 
        })
    

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM comments WHERE id=%s", (comment_id,))
    comment = cursor.fetchone()

    if comment and (comment['user_id'] == session['user_id'] or session['role'] == 'admin'):

        cursor.execute("DELETE FROM notifications WHERE comment_id=%s", (comment_id,))
        cursor.execute("DELETE FROM comments WHERE id=%s", (comment_id,))


        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'recipe_id': comment['recipe_id']})
    
    cursor.close()
    conn.close()
    return jsonify({'success': False, 'error': 'Permission denied'}), 403


@app.route('/recipe/<int:recipe_id>/get_comments', methods=['GET'])
def get_comments(recipe_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT c.*, u.username 
        FROM comments c 
        JOIN users u ON c.user_id = u.id 
        WHERE c.recipe_id = %s 
        ORDER BY c.created_at DESC
    """, (recipe_id,))
    comments = cursor.fetchall()

    cursor.close()
    conn.close()
    return jsonify(comments)



@app.route('/get_notifications')
@login_required
def get_notifications():

    clean_old_notifications()
    check_password_reminder()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
                       SELECT n.*, r.title as recipe_title, u.username as commenter_username FROM notifications n LEFT JOIN
                       recipes r ON n.recipe_id = r.id
                       LEFT JOIN users u ON n.commenter_id = u.id
                       WHERE n.user_id = %s
                       ORDER BY n.created_at DESC
                       LIMIT 10
                       """, (session['user_id'],))
        
    notifications = cursor.fetchall()
    unread_count = sum(1 for n in notifications if not n['is_read'])

    return jsonify({
            'notifications': notifications,
            'unread_count': unread_count
    })    

if __name__ == '__main__':
    app.run(debug=True)
