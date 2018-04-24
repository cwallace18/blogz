from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:launchcode@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'i7y8gjh45'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=(True))
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
   

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template("index.html", users=users, title="All Blogs")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        error = 0
        username = request.form['username']
        password = request.form['password']
        user_error = ''
        pass_error = ''
        user = User.query.filter_by(username=username).first()

        if not user:
            error = error + 1
            user_error = 'User does not exist'

        elif user.password != password:
            error = error + 1
            pass_error = 'Invalid Password'

        if error == 0:
            if user and user.password == password:
                session['username'] = username
                flash("Logged in")
                return redirect('/newpost')
        else:
            return render_template('login.html', user_error=user_error, pass_error=pass_error)

    return render_template('login.html')

@app.route('/logout')
def logout():
    if session['username']:
        del session['username']
    return redirect('/blog')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        existing_user = User.query.filter_by(username=username).first()
        
        if password and not existing_user and password == verify and len(password)>2 and len(username)>3:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
        
        elif existing_user:
            return render_template("signup.html", error = "Userame already in use. Please choose a different username.")

        elif len(username) < 3:
            return render_template("signup.html", error = "Username must be at least 3 characters.")
        
        elif not password:
            return render_template("signup.html",user_name = username, error = "Please enter a password.")

        elif len(password) < 3:
            return render_template("signup.html", error = "Password must be at least 3 characters.")

        else:
            return render_template("signup.html", user_name = username, error = "Passwords don't match.")
    else:
        return render_template("signup.html")

    return render_template('signup.html')


@app.route('/blog', methods=['GET', 'POST'])
def blog():
    is_blog_id = request.args.get('id')
    is_blog_user = request.args.get('user')
    
    if is_blog_id:
        single_blog = Blog.query.filter_by(id = is_blog_id).first()
        return render_template("single_entry.html", blog=single_blog)
    
    elif is_blog_user:
        the_user = User.query.filter_by(username=is_blog_user).first()
        user_blogs = Blog.query.filter_by(owner=the_user).all()
        return render_template("user_post.html", blogs=user_blogs, username=is_blog_user, title = "YourBlogs")    

    else:
        blogs = Blog.query.all()
        return render_template("blog.html", blogs=blogs, title="YourBlogs")

@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        title_error = ""
        body_error = ""

        if blog_title == "":
            title_error = "Please add a blog title."

        if blog_body =="":
            body_error = "Please add some content to the new blog post."
        
        if title_error or body_error:
            return render_template("newpost.html", blog_title=blog_title, blog_body=blog_body, 
            title_error = title_error, body_error=body_error)
        
        else:
            owner = User.query.filter_by(username= session['username']).first()
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()

            return render_template("single_entry.html", blog=new_blog)

    return render_template("newpost.html", title = "CreatePost")

if __name__ == '__main__':
    app.run()