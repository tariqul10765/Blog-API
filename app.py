from flask import Flask, jsonify, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow

app = Flask(__name__)

# /// = relative path, //// = absolute path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)

migrate = Migrate(app, db)


# models
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    description = db.Column(db.String())
    view = db.Column(db.Integer, default=0)

    def __init__(self, title, description, view=0):
        self.title = title
        self.description = description
        self.view = view


class BlogSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ("id", "title", "description", "view")


blog_schema = BlogSchema()
blogs_schema = BlogSchema(many=True)


@app.route('/')
def Home():
    return '<h1 style="text-align:center">Welcome to our blog api</h1 >'


@app.route('/get-all-blogs')
def ReadBlogs():
    data = Blog.query.all()
    s_data = blogs_schema.dump(data)

    return jsonify({'data': s_data})


@app.route('/get-blog/<int:blogId>')
def ReadBlog(blogId):
    blog = Blog.query.filter_by(id=blogId).first()
    s_data = blog_schema.dump(blog)

    blog.view += 1
    db.session.commit()

    return jsonify({'data': s_data})


@app.route('/add-blog', methods=['POST'])
def CreateBlog():
    data = request.json
    new_blog = Blog(data['title'], data['description'])
    # s_data = blog_schema.dump(new_blog)

    db.session.add(new_blog)
    db.session.commit()
    # print(s_data)

    return redirect(url_for("ReadBlogs"))


@app.route('/update-blog/<int:blogId>', methods=['PUT'])
def UpdateBlog(blogId):
    blog = Blog.query.filter_by(id=blogId).first()

    if 'title' in request.json:
        blog.title = request.json['title']
    if 'description' in request.json:
        blog.description = request.json['description']
    # if 'view' in request.json:
    #     blog.view = request.json['view']

    db.session.commit()

    return redirect(url_for("ReadBlogs"))


@app.route('/delete-blog/<int:blogId>', methods=['DELETE'])
def DeleteBlog(blogId):
    blog = Blog.query.filter_by(id=blogId).delete()
    db.session.commit()

    return redirect(url_for("ReadBlogs"))


if __name__ == '__main__':
    app.run(debug=True)
