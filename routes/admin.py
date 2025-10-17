from flask import Blueprint, render_template, request, redirect, url_for

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # dummy auth
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')
