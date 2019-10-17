from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:jbh09jbh@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    post_body = db.Column(db.Text)

    def __init__(self, title, post_body):
        self.title = title
        self.post_body = post_body

# 
@app.route('/blog', methods=['GET'])
def index():

    req = dict(request.args)
    if req == {}:
        posts = Post.query.order_by(desc(Post.id))
        return render_template('allposts.html', description="Blog Posts", posts=posts)
    else:
        post_id = req['id']
        posts = Post.query.filter_by(id=post_id).all()

        return render_template('post.html', description="Blog Posts", posts=posts)


# 
@app.route('/newpost', methods=['GET','POST'])
def newpost():

    if request.method == 'POST':
        post_title = request.form['title']
        post_body = request.form['post_body']
        
        if not post_title:
            errtitle = 'Please enter a blog post title '
            post_body = post_body
            return render_template('newpost.html', description="Add Blog Posts", errtitle=errtitle, body=post_body)
        elif not post_body:
            errbody = 'Please enter a blog post title'
            post_title = post_title
            return render_template('newpost.html', description="Add Blog Posts", errbody=errbody, title=post_title)
        else:
            new_post = Post(post_title, post_body)
            db.session.add(new_post)
            db.session.commit()
            
            id = str(Post.query.count())
            posts = Post.query.filter_by(id=id).all()
            return render_template('post.html', description="Blog Posts", posts=posts)

    if request.method == 'GET':

        return render_template('newpost.html', description="Add Blog Posts")  

# 
if __name__ == '__main__':
    app.run()