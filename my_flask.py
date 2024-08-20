from flask import Flask, render_template
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

# Database connection parameters
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Make sure your MySQL root user password is correct
    'database': 'blogging_platform'
}

# Database connection function
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/')
def index():
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT posts.id, posts.title, users.username AS author_name
                FROM posts
                JOIN users ON posts.author_id = users.id
            """)
            posts = cursor.fetchall()
        except Error as e:
            print(f"Error fetching data: {e}")
            posts = []
        finally:
            cursor.close()
            connection.close()
    else:
        posts = []
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post_detail(post_id):
    connection = get_db_connection()
    if connection:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT posts.id, posts.title, posts.content, users.username AS author_name
                FROM posts
                JOIN users ON posts.author_id = users.id
                WHERE posts.id = %s
            """, (post_id,))
            post = cursor.fetchone()

            if post:
                post['comments'] = fetch_comments_for_post(post_id, connection)
            else:
                post = None
        except Error as e:
            print(f"Error fetching data: {e}")
            post = None
        finally:
            cursor.close()
            connection.close()
    else:
        post = None

    return render_template('post_detail.html', post=post)

def fetch_comments_for_post(post_id, connection):
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT comments.id, comments.content, users.username AS author_name
            FROM comments
            JOIN users ON comments.author_id = users.id
            WHERE comments.post_id = %s
            ORDER BY comments.created_at DESC
        """, (post_id,))
        comments = cursor.fetchall()
        return comments
    except Error as e:
        print(f"Error fetching comments for post {post_id}: {e}")
        return []

if __name__ == '__main__':
    app.run(debug=True, port=5001)
