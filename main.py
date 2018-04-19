from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'i7y8gjh45'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=(True))
    title = db.Column(db.String(120))
    body = db.Column(db.String(10000))

    def __init__(self, title, body):
        self.title = title
        self.body = body


@app.route('/')
def index():
    return redirect ('/blog')

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    blogs = Blog.query.all()

    if 'id' in request.args:
        blog_id = request.args.get('id')
        blog_post = Blog.query.get(blog_id)
        return render_template('post.html', blog=blog_post)

    return render_template('blog.html', blogs=blogs)

@app.route('/newpost', methods=['GET', 'POST'])
def add_blog():
    if request.method == 'POST':
        blog_title = request.form['blog_title']
        blog_body = request.form['blog_body']

        title_error = ''
        body_error = ''

        if blog_title == "":
            title_error = "Please enter a title."
        if blog_body == "":
            body_error = "Please enter body."

        if not title_error and not body_error:

            new_blog = Blog(blog_title, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            id_parameter = new_blog.id

            return redirect('/blog?id={0}'.format(id_parameter))

        else:
            return render_template('newpost.html',
            title_error=title_error,
            body_error=body_error,
            blog_body=blog_body,
            blog_title=blog_title)

    else: 
        return render_template('newpost.html')


if __name__ == '__main__':
    app.run()