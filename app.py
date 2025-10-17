from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
import secrets
import os
import sqlite3
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['DATABASE'] = 'portfolio.db'

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

active_visitors = 0

# ==================== DATABASE ====================

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_admin BOOLEAN DEFAULT 1
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            tags TEXT NOT NULL,
            github TEXT,
            demo TEXT,
            image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blogs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            excerpt TEXT NOT NULL,
            content TEXT NOT NULL,
            author TEXT DEFAULT 'Vishal Kumar',
            tags TEXT NOT NULL,
            published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS certifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            issuer TEXT NOT NULL,
            date TEXT NOT NULL,
            url TEXT,
            image TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contact_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            subject TEXT,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password, full_name, is_admin)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@vishal.com', generate_password_hash('admin123'), 'Admin User', 1))
    except sqlite3.IntegrityError:
        pass
    
    sample_projects = [
        ('Bihar Domestic Violence Analysis', 
         'Data analysis project using Python, Pandas, and Matplotlib to analyze domestic violence patterns in Bihar (2016-2025).',
         'data-science',
         'Python,Pandas,Matplotlib,NumPy,Data Science',
         'https://github.com/Vishaldubey2210',
         'https://example.com/demo1',
         '/static/images/project1.jpg'),
        
        ('Spider-Man OpenCV Game',
         'Interactive hand gesture recognition game using MediaPipe and OpenCV with Marvel-themed UI.',
         'computer-vision',
         'Python,OpenCV,MediaPipe,Computer Vision',
         'https://github.com/Vishaldubey2210',
         'https://example.com/demo2',
         '/static/images/project2.jpg'),
        
        ('Seven Sister Gateway',
         'Tourist safety system for Northeast India with Flask, MongoDB, and ML clustering models.',
         'full-stack',
         'Flask,MongoDB,Python,Bootstrap,SQL,SQLite',
         'https://github.com/Vishaldubey2210',
         'https://example.com/demo3',
         '/static/images/project3.jpg'),
        
        ('LangChain Chat Model',
         'Advanced chat application using LangGraph, LangChain and Hugging Face APIs with Streamlit frontend.',
         'machine-learning',
         'Python,LangChain,LangGraph,Hugging Face,GenAI',
         'https://github.com/Vishaldubey2210',
         'https://example.com/demo4',
         '/static/images/project4.jpg')
    ]
    
    for project in sample_projects:
        try:
            cursor.execute('''
                INSERT INTO projects (title, description, category, tags, github, demo, image)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', project)
        except sqlite3.IntegrityError:
            pass
    
    conn.commit()
    conn.close()
    print("✅ Database initialized!")

with app.app_context():
    init_db()

# ==================== DECORATORS ====================

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('admin_login_page'))
        
        conn = get_db()
        user = conn.execute('SELECT is_admin FROM users WHERE id = ?', (session['user_id'],)).fetchone()
        conn.close()
        
        if not user or not user['is_admin']:
            return redirect(url_for('admin_login_page'))
        
        return f(*args, **kwargs)
    return decorated_function

# ==================== PUBLIC ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/projects')
def projects():
    return render_template('projects.html')

@app.route('/blog')
def blog():
    return render_template('blog.html')

@app.route('/blog/<slug>')
def blog_post(slug):
    return render_template('blog_post.html', slug=slug)

@app.route('/certifications')
def certifications():
    return render_template('certifications.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ==================== ADMIN ROUTES ====================

@app.route('/admin')
def admin_login_page():
    if 'user_id' in session and session.get('is_admin'):
        return redirect(url_for('admin_dashboard'))
    return render_template('admin_login.html')

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        conn = get_db()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND is_admin = 1', (username,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = 1
            
            print(f"✅ Admin login: {username}")
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'redirect': url_for('admin_dashboard')
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid admin credentials'}), 401
            
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return jsonify({'success': False, 'message': 'Login failed'}), 500

@app.route('/api/admin/signup', methods=['POST'])
def admin_signup():
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        if not all([username, email, password, full_name]):
            return jsonify({'success': False, 'message': 'All fields are required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password, full_name, is_admin)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, generate_password_hash(password), full_name, 1))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            
            session['user_id'] = user_id
            session['username'] = username
            session['is_admin'] = 1
            
            print(f"✅ New admin registered: {username}")
            
            return jsonify({
                'success': True,
                'message': 'Admin account created successfully!',
                'redirect': url_for('admin_dashboard')
            })
            
        except sqlite3.IntegrityError as e:
            conn.close()
            if 'username' in str(e):
                return jsonify({'success': False, 'message': 'Username already exists'}), 400
            elif 'email' in str(e):
                return jsonify({'success': False, 'message': 'Email already exists'}), 400
            else:
                return jsonify({'success': False, 'message': 'Registration failed'}), 400
        
    except Exception as e:
        print(f"❌ Signup error: {str(e)}")
        return jsonify({'success': False, 'message': f'Signup failed: {str(e)}'}), 500

@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login_page'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/projects')
@admin_required
def admin_projects():
    return render_template('admin/projects_manager.html')

@app.route('/admin/blogs')
@admin_required
def admin_blogs():
    return render_template('admin/blogs_manager.html')

@app.route('/admin/certifications')
@admin_required
def admin_certifications():
    return render_template('admin/certifications_manager.html')

@app.route('/admin/analytics')
@admin_required
def admin_analytics():
    return render_template('admin/analytics.html')

# ==================== PUBLIC API ====================

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'OK',
        'timestamp': datetime.now().isoformat(),
        'activeVisitors': active_visitors
    })

@app.route('/api/projects')
def get_projects():
    conn = get_db()
    projects = conn.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
    conn.close()
    
    projects_list = [{
        'id': p['id'],
        'title': p['title'],
        'description': p['description'],
        'category': p['category'],
        'tags': p['tags'].split(','),
        'github': p['github'],
        'demo': p['demo'],
        'image': p['image']
    } for p in projects]
    
    return jsonify({'success': True, 'projects': projects_list})

@app.route('/api/blogs')
def get_blogs():
    conn = get_db()
    blogs = conn.execute('SELECT * FROM blogs ORDER BY published_at DESC').fetchall()
    conn.close()
    
    blogs_list = [{
        'id': b['id'],
        'title': b['title'],
        'slug': b['slug'],
        'excerpt': b['excerpt'],
        'content': b['content'],
        'author': b['author'],
        'tags': b['tags'].split(','),
        'publishedAt': b['published_at']
    } for b in blogs]
    
    return jsonify({'success': True, 'blogs': blogs_list})

@app.route('/api/certifications')
def get_certifications():
    conn = get_db()
    certs = conn.execute('SELECT * FROM certifications ORDER BY created_at DESC').fetchall()
    conn.close()
    
    certs_list = [{
        'id': c['id'],
        'title': c['title'],
        'issuer': c['issuer'],
        'date': c['date'],
        'url': c['url'],
        'image': c['image']
    } for c in certs]
    
    return jsonify({'success': True, 'certifications': certs_list})

@app.route('/api/contact', methods=['POST'])
def contact_form():
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', 'No Subject')
        message = data.get('message', '').strip()
        
        if not all([name, email, message]):
            return jsonify({'success': False, 'message': 'All fields required'}), 400
        
        conn = get_db()
        conn.execute('''
            INSERT INTO contact_messages (name, email, subject, message)
            VALUES (?, ?, ?, ?)
        ''', (name, email, subject, message))
        conn.commit()
        conn.close()
        
        print(f"📧 Contact from: {name} ({email})")
        
        return jsonify({
            'success': True,
            'message': 'Thank you for reaching out! I will get back to you soon.'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to send message'}), 500

# ==================== ADMIN API ====================

@app.route('/api/admin/projects', methods=['GET', 'POST', 'DELETE'])
@admin_required
def admin_projects_api():
    conn = get_db()
    
    if request.method == 'GET':
        projects = conn.execute('SELECT * FROM projects ORDER BY created_at DESC').fetchall()
        projects_list = [{
            'id': p['id'],
            'title': p['title'],
            'description': p['description'],
            'category': p['category'],
            'tags': p['tags'].split(','),
            'github': p['github'],
            'demo': p['demo'],
            'image': p['image']
        } for p in projects]
        conn.close()
        return jsonify({'success': True, 'projects': projects_list})
    
    if request.method == 'POST':
        data = request.json
        tags_str = ','.join(data.get('tags', []))
        
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (title, description, category, tags, github, demo, image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('title'),
            data.get('description'),
            data.get('category'),
            tags_str,
            data.get('github'),
            data.get('demo'),
            data.get('image', '/static/images/default-project.jpg')
        ))
        conn.commit()
        conn.close()
        
        print(f"📁 New Project Added: {data.get('title')}")
        
        return jsonify({'success': True, 'message': 'Project added successfully!'})
    
    if request.method == 'DELETE':
        project_id = request.args.get('id', type=int)
        conn.execute('DELETE FROM projects WHERE id = ?', (project_id,))
        conn.commit()
        conn.close()
        
        print(f"🗑️ Project deleted: ID {project_id}")
        
        return jsonify({'success': True, 'message': 'Project deleted successfully!'})

@app.route('/api/admin/blogs', methods=['GET', 'POST', 'DELETE'])
@admin_required
def admin_blogs_api():
    conn = get_db()
    
    if request.method == 'GET':
        blogs = conn.execute('SELECT * FROM blogs ORDER BY published_at DESC').fetchall()
        blogs_list = [{
            'id': b['id'],
            'title': b['title'],
            'slug': b['slug'],
            'excerpt': b['excerpt'],
            'content': b['content'],
            'author': b['author'],
            'tags': b['tags'].split(','),
            'publishedAt': b['published_at']
        } for b in blogs]
        conn.close()
        return jsonify({'success': True, 'blogs': blogs_list})
    
    if request.method == 'POST':
        data = request.json
        slug = data.get('slug') or data.get('title', '').lower().replace(' ', '-')
        tags_str = ','.join(data.get('tags', []))
        
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO blogs (title, slug, excerpt, content, tags)
            VALUES (?, ?, ?, ?, ?)
        ''', (data.get('title'), slug, data.get('excerpt'), data.get('content'), tags_str))
        conn.commit()
        conn.close()
        
        print(f"📝 New Blog Posted: {data.get('title')}")
        
        return jsonify({'success': True, 'message': 'Blog post published successfully!'})
    
    if request.method == 'DELETE':
        blog_id = request.args.get('id', type=int)
        conn.execute('DELETE FROM blogs WHERE id = ?', (blog_id,))
        conn.commit()
        conn.close()
        
        print(f"🗑️ Blog deleted: ID {blog_id}")
        
        return jsonify({'success': True, 'message': 'Blog post deleted successfully!'})

@app.route('/api/admin/certifications', methods=['GET', 'POST', 'DELETE'])
@admin_required
def admin_certifications_api():
    conn = get_db()
    
    if request.method == 'GET':
        certs = conn.execute('SELECT * FROM certifications ORDER BY created_at DESC').fetchall()
        certs_list = [{
            'id': c['id'],
            'title': c['title'],
            'issuer': c['issuer'],
            'date': c['date'],
            'url': c['url'],
            'image': c['image']
        } for c in certs]
        conn.close()
        return jsonify({'success': True, 'certifications': certs_list})
    
    if request.method == 'POST':
        data = request.json
        
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO certifications (title, issuer, date, url, image)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('title'),
            data.get('issuer'),
            data.get('date'),
            data.get('url'),
            data.get('image', '/static/images/default-cert.jpg')
        ))
        conn.commit()
        conn.close()
        
        print(f"🎓 New Certification Added: {data.get('title')}")
        
        return jsonify({'success': True, 'message': 'Certification added successfully!'})
    
    if request.method == 'DELETE':
        cert_id = request.args.get('id', type=int)
        conn.execute('DELETE FROM certifications WHERE id = ?', (cert_id,))
        conn.commit()
        conn.close()
        
        print(f"🗑️ Certification deleted: ID {cert_id}")
        
        return jsonify({'success': True, 'message': 'Certification deleted successfully!'})

@app.route('/api/admin/stats')
@admin_required
def admin_stats():
    conn = get_db()
    
    total_projects = conn.execute('SELECT COUNT(*) as count FROM projects').fetchone()['count']
    total_blogs = conn.execute('SELECT COUNT(*) as count FROM blogs').fetchone()['count']
    total_certs = conn.execute('SELECT COUNT(*) as count FROM certifications').fetchone()['count']
    total_users = conn.execute('SELECT COUNT(*) as count FROM users').fetchone()['count']
    total_messages = conn.execute('SELECT COUNT(*) as count FROM contact_messages').fetchone()['count']
    
    conn.close()
    
    return jsonify({
        'success': True,
        'stats': {
            'totalProjects': total_projects,
            'totalBlogs': total_blogs,
            'totalCertifications': total_certs,
            'totalUsers': total_users,
            'totalMessages': total_messages,
            'activeVisitors': active_visitors
        }
    })

# ==================== SOCKETIO ====================

@socketio.on('connect')
def handle_connect():
    global active_visitors
    active_visitors += 1
    print(f'✅ Visitor connected. Total: {active_visitors}')
    emit('visitor_count', {'count': active_visitors}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    global active_visitors
    active_visitors = max(0, active_visitors - 1)
    print(f'❌ Visitor disconnected. Total: {active_visitors}')
    emit('visitor_count', {'count': active_visitors}, broadcast=True)

@socketio.on('page_view')
def handle_page_view(data):
    print(f"📄 Page view: {data.get('page')}")

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html'), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== RUN ====================

if __name__ == '__main__':
    print('\n' + '='*60)
    print('🚀 Vishal Kumar Portfolio Server Started!')
    print('='*60)
    print('📡 Server URL: http://localhost:5000')
    print('🔐 Admin Panel: http://localhost:5000/admin')
    print('   Default: admin / admin123')
    print('🗄️  Database: portfolio.db (SQLite)')
    print('📅 Started at:', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('='*60 + '\n')
    
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, allow_unsafe_werkzeug=True)
