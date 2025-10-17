from flask import Blueprint, render_template

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/')
def analytics_home():
    return render_template('admin/analytics.html')
