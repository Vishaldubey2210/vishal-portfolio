from flask import Blueprint, render_template

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/')
def list_posts():
    return render_template('blog.html')

@blog_bp.route('/<int:post_id>')
def show_post(post_id):
    # placeholder data
    post = {'title': f'Post {post_id}', 'content': 'This is a sample post.'}
    return render_template('blog_post.html', post=post)
