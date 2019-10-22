from flask import Flask, request, redirect, render_template, session, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from hash_utils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:jbh09jbh@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = "imleavingeverythingtomyghost"
Bootstrap(app)
db = SQLAlchemy(app)
# ////////////////////////////////////////////
class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    post_body = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, post_body, owner):
        self.title = title
        self.post_body = post_body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(255))
    blogs = db.relationship('Post', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = make_pw_hash(password)

# ////////////////////////////////////////////
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'post_list', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')   
# ////////////////////////////////////////////
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if not user:
            flash("Username incorrect")
            # TODO - populate flash message on base.html, include categories
            return redirect('/login')

        if user and check_pw_hash(password, user.password):
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            # if user and user.password != make_pw_hash(password):            
            flash("Password incorrect")
            # TODO - populate flash message on base.html, include categories
            return redirect('/login')

    return render_template('login.html')
# ////////////////////////////////////////////
@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        user = User.query.filter_by(username=username).first()

        if not username:
            flash('All fields are required')
            # TODO - populate flash message on base.html, include categories
            return redirect('/signup')
        elif not password:
            flash('All fields are required')
            # TODO - populate flash message on base.html, include categories
            return redirect('/signup')
        elif not verify:
            flash('All fields are required')
            # TODO - populate flash message on base.html, include categories
            return redirect('/signup')
    
        if password != verify:
            flash("Passwords do not match")
            # TODO - populate flash message on base.html, include categories
            return redirect('/signup')

        if user and user.username == username:
            flash('Username already exists')
            # TODO - populate flash message on base.html, include categories
            return redirect('/signup')

        if len(username) < 3:
            flash('Username must be 3 or more characters')
            # TODO - populate flash message on base.html, include categories
            return redirect('/signup')

        if len(password) < 3:
            flash('Password must be 3 or more characters')
            # TODO - populate flash message on base.html, include categories
            return redirect('/signup')

        session['username'] = username
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/newpost')
        
    
    return render_template('signup.html')
# ////////////////////////////////////////////
@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')
# ////////////////////////////////////////////
@app.route('/blog')
def post_list():

    req = dict(request.args)
    if req == {}:
        posts = Post.query.order_by(desc(Post.id))
        users = User.query.all()
        return render_template('all-posts.html', description="Blog Posts", posts=posts, users=users) 
    elif 'post_id' in req:
        post_id = req['post_id']
        posts = Post.query.filter_by(id=post_id).all()
        users = User.query.all()
        return render_template('post.html', description="Blog Posts", posts=posts, users=users)
    elif 'user_id' in req:
        user_id = req['user_id']
        titles = Post.query.filter_by(user_id=user_id).first()
        posts = Post.query.filter_by(user_id=user_id).order_by(desc(Post.id))
        users = User.query.all()
        return render_template('user.html', description="Author's Posts", posts=posts, users=users, titles=titles)
# ///////////////////////////////////////////
@app.route('/')
def index():

    req = dict(request.args)
    if req == {}:
        users = User.query.order_by(desc(User.id))
        return render_template('index.html', description="Authors", users=users)
# ///////////////////////////////////////////
@app.route('/newpost', methods=['GET','POST'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        post_title = request.form['title']
        post_body = request.form['post_body']
        
        if not post_title:
            errtitle = 'Please enter a title for the post'
            post_body = post_body
            return render_template('newpost.html', description="Add Blog Posts", errtitle=errtitle, body=post_body)
        elif not post_body:
            errbody = 'Please enter a title for the post'
            post_title = post_title
            return render_template('newpost.html', description="Add Blog Posts", errbody=errbody, title=post_title)
        else:
            new_post = Post(post_title, post_body, owner)
            db.session.add(new_post)
            db.session.commit()
            
            id = str(Post.query.count())
            posts = Post.query.filter_by(id=id).all()
            return render_template('post.html', description="Blog Posts", posts=posts)

    if request.method == 'GET':

        return render_template('newpost.html', description="Add Blog Posts")  
# ////////////////////////////////////////////
if __name__ == '__main__':
    app.run()