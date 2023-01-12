# app.py

from crypt import methods
import ssl
from flask import Flask, render_template, request, redirect
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']

def initialize_lessons_table():
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        # create a cursor object for execution
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS lessons;')
        cur.execute('CREATE TABLE lessons (id serial PRIMARY KEY,'
                                 'name varchar (150) NOT NULL,'
                                 'content text NOT NULL,'
                                 'content2 text NOT NULL,'
                                 'preview_path varchar (250) NOT NULL,'
                                 'img1_path varchar (250),'
                                 'img2_path varchar (250),'
                                 'img3_path varchar (250));'
                                 )
        # close the communication with the PostgreSQL database server
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()

def insert_lesson_into_lesson_tables(name, content, content2, preview_path, img1_path, img2_path, img3_path):
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        # create a cursor object for execution
        cur = conn.cursor()
        cur.execute('INSERT INTO lessons (name, content, content2, preview_path, img1_path, img2_path, img3_path)'
            'VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (name, content, content2, str(preview_path), str(img1_path), str(img2_path), str(img3_path))
            )
        # close the communication with the PostgreSQL database server
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()

def get_all_lessons():
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        # create a cursor object for execution
        cur = conn.cursor()
        cur.execute('SELECT id, name, content, preview_path, img1_path, img2_path, img3_path '
                    'FROM lessons')
        # process the result set
        row = cur.fetchone()
        all_lessons = []
        while row is not None:
            lesson = dict(id=row[0], name=row[1], content=row[2], content2=row[3], preview_path=row[4], img1_path=row[5], img2_path=row[6], img3_path=row[7])
            all_lessons.append(lesson)
            row = cur.fetchone()
        # close the communication with the PostgreSQL database server
        cur.close()
        if all_lessons:
            return all_lessons
        return []
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()

def get_lesson_by_id(lesson_id):
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        # create a cursor object for execution
        cur = conn.cursor()
        cur.execute('SELECT * '
                        'FROM lessons '
                        'WHERE id::varchar(255) = %s;', str(lesson_id))
        # process the result set
        lesson = cur.fetchone()
        # close the communication with the PostgreSQL database server
        cur.close()
        if lesson:
            return lesson
        return {}
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.commit()
            conn.close()

app = Flask(__name__, static_url_path='/static')

@app.route("/", methods=['GET', 'POST'])
def home():
    all_lessons = get_all_lessons()
    print(all_lessons)
    return render_template("index.html", title="CodeReMi", lessons=all_lessons)

@app.route("/lessons", methods=['GET', 'POST'])
def lessons():
    all_lessons = get_all_lessons()
    if all_lessons:
        print("ALL", all_lessons)
        search = request.form.get("lesson_search")
        print(search)
        if search:
            print("THIS", search)
            req_lessons = []
            for lesson in all_lessons:
                if str(search).lower() in lesson['name'].lower():
                    req_lessons.append(lesson)
            return render_template("lessons.html", title="CodeReMi Lessons", lessons=req_lessons)
        return render_template("lessons.html", title="CodeReMi Lessons", lessons=all_lessons)
    return render_template("lessons.html", title="CodeReMi Lessons", lessons=[])
@app.route("/lesson", methods=['GET', 'POST'])
def lesson():
    lesson_id = request.args.get("id")
    if lesson_id:
        row = get_lesson_by_id(int(lesson_id))
        if row:
            all_lessons = get_all_lessons()
            lesson_dict = dict(id=row[0], name=row[1], content=row[2], content2=row[3], preview_path=row[4], img1_path=row[5], img2_path=row[6], img3_path=row[7])
            if all_lessons:
                return render_template("lesson.html", id=lesson_id, lesson=lesson_dict, all_lessons=all_lessons)
            return render_template("lesson.html", id=lesson_id, lesson=lesson_dict, all_lessons=[])
        else:
            return render_template("error.html")
    else:
        return render_template("error.html")

@app.route("/resetlessontable", methods=['GET'])
def reset_lesson_table():
    initialize_lessons_table()
    print("THE LESSONS", get_all_lessons())
    return redirect("/")

@app.route("/createlesson", methods=['GET'])
def create_lesson_form():
    return render_template("create.html")

@app.route("/pushlessontodatabase", methods=['GET', 'POST'])
def push_lesson_to_database():
    name = request.form.get("lesson_name")
    content = request.form.get("lesson_content")
    content2 = request.form.get("lesson_content_2")
    preview_path = request.form.get("preview_path")
    img1_path = request.form.get("lesson_image_1")
    img2_path = request.form.get("lesson_image_2")
    img3_path = request.form.get("lesson_image_3")
    print(name, content, content2, preview_path, img1_path, img2_path, img3_path)
    insert_lesson_into_lesson_tables(name, content, content2, preview_path, img1_path, img2_path, img3_path)
    return redirect("/")
    

@app.route("/about")
def about():
    return render_template("about.html", title="About CodeReMi")

@app.errorhandler(404)
def handle_404(e):
    # handle all other routes here
    return render_template("error.html")

if __name__ == "__main__":
    app.run(debug=True)