from flask import Flask, render_template, request, redirect, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sharemusic.db'
app.config['SECRET_KEY'] = os.urandom(16).hex()
db = SQLAlchemy(app)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    music = db.Column(db.String(1000))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc)+timedelta(hours=8)) 
    uid = db.Column(db.Integer, db.ForeignKey('user_register.id'), nullable=False)
    PostReplyRelationship = db.relationship("PostReply", backref="blog")
    
    def __repr__(self):
        return 'Blog post ' + str(self.id)

class UserRegister(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    BlogPostRelationship = db.relationship("BlogPost", backref="user")
    PostReplyRelationship = db.relationship("PostReply", backref="user")

    def __repr__(self):
        return 'username:%s, email:%s' % (self.username, self.email)

class PostReply(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc)+timedelta(hours=8))
    uid = db.Column(db.Integer, db.ForeignKey('user_register.id'), nullable=False)
    pid = db.Column(db.Integer, db.ForeignKey('blog_post.id'), nullable=False)
    
    def __repr__(self):
        return 'Blog post ' + str(self.id)

@app.before_first_request
def create_tables():
    db.create_all()

@app.context_processor
def user_session():
    if session:
        username = session.get("username")
        uid = session.get("id")
        return dict(session_username=username, session_uid=uid)
    else:
        return dict(session_username='', session_uid='')

@app.route('/')
def index():
    return render_template("index.html", post='')

@app.route('/posts', methods=['GET'])
@app.route('/posts/<int:pages>', methods=['GET'])
def posts(pages=1):
    all_posts = BlogPost.query.order_by(BlogPost.date_posted.desc()).paginate(pages, 5, False)
    all_replys = PostReply.query.order_by(PostReply.date_posted.desc()).all()
    # all_authors = UserRegister.query.filter_by(id=BlogPost.query.order_by(BlogPost.date_posted).uid).all()
    return render_template("posts.html", posts = all_posts, replys = all_replys)

@app.route('/posts/add/<int:uid>', methods=['GET', 'POST'])
def add(uid):
    if session:
        if request.method == 'POST':
            post_title = request.form['title']
            post_music = request.form['music']
            post_content = request.form['content']
            post_uid = uid
            new_post = BlogPost(title=post_title, content=post_content, music=post_music, uid=post_uid)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/posts')
        else:
            return render_template("new_post.html")
    else:
        return render_template("login.html", unlogin=True)

@app.route('/posts/reply/<int:uid>/<int:id>', methods=['POST'])
def reply(uid,id):
    if session:
        if request.method == 'POST':
            reply_content = request.form['content']
            reply_uid = uid
            reply_pid = id
            new_reply = PostReply(content=reply_content, uid=reply_uid, pid=reply_pid)
            db.session.add(new_reply)
            db.session.commit()
            return redirect('/posts')
        else:
            return render_template("posts.html")
    else:
        return render_template("login.html", unlogin=True)

@app.route('/posts/delete/<int:uid>/<int:id>')
def delete(uid,id):
    if session:
        post = BlogPost.query.get_or_404(id)
        if post.uid == uid:
            db.session.delete(post)
            db.session.commit()
            return redirect('/posts')
        else:
            return redirect('/posts')
    else:
        return render_template("login.html", unlogin=True)

@app.route('/posts/edit/<int:uid>/<int:id>', methods=['GET', 'POST'])
def edit(uid,id):
    if session:
        edit_post = BlogPost.query.get_or_404(id)
        if edit_post.uid == uid:
            if request.method == 'POST':
                edit_post.title = request.form['title']
                edit_post.music = request.form['music']
                edit_post.content = request.form['content']
                db.session.commit()
                return redirect('/posts')
            else:
                return render_template('edit.html', post = edit_post)
        else:
            return redirect('/posts')
    else:
        return render_template("login.html", unlogin=True) 

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        register_username = request.form['username']
        register_email = request.form['email']
        register_password = request.form['password']
        hash_password = generate_password_hash(register_password).decode('utf8')
        same_name = UserRegister.query.filter_by(username=register_username).first()
        same_email = UserRegister.query.filter_by(email=register_email).first()
        if same_name or same_email:
            return render_template("register.html", register_error=True)
        else:
            new_member = UserRegister(username=register_username, email=register_email, password=hash_password)
            db.session.add(new_member)
            db.session.commit()
            return render_template("login.html", register_success=True)
    else:
        return render_template("register.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login_email = request.form['email']
        login_password = request.form['password']
        userData = UserRegister.query.filter_by(email=login_email).first()
        if userData:
            if check_password_hash(userData.password, login_password):
                session['id'] = userData.id
                session['username'] = userData.username
                return redirect('/')
            else:
                return render_template("login.html", message="帳號或密碼錯誤！")
        else:
            return render_template("login.html", message="帳號或密碼錯誤！")
    else:
        return render_template("login.html")

@app.route('/login/unlogin=True')
def unlogin():
    return render_template("login.html", unlogin = True)
        
@app.route('/logout')
def logout():
    if session:
        session.clear()
        return redirect('/')
    else:
        return redirect('/')

port = int(os.getenv('PORT', 8080))   
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port) 