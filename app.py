# app.py

from crypt import methods
from flask import Flask, render_template, request, redirect
import os
import psycopg2

dbname = 'd142ske1bsnjoq'
user = 'tnroyjmzmacvis'
password = 'fbbbe2b0fda76768890291f68dd049901a91058d124a0bd685d59a256ae66409'
host = 'ec2-54-208-104-27.compute-1.amazonaws.com'
port = '5432'

conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
            )

def initialize_lessons_table():
    conn = None
    try:
        # connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
            )
        # create a cursor object for execution
        cur = conn.cursor()
        cur.execute('DROP TABLE IF EXISTS lessons;')
        cur.execute('CREATE TABLE lessons (id serial PRIMARY KEY,'
                                 'name varchar (150) NOT NULL,'
                                 'content text NOT NULL,'
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

def insert_lesson_into_lesson_tables(name, content, preview_path, img1_path, img2_path, img3_path):
    conn = None
    try:
        # connect to the PostgreSQL database
        # conn = psycopg2.connect(
        # host="localhost",
        # database="flask_db",
        # user="postgres",
        # password="Dangely")
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
            )
        # create a cursor object for execution
        cur = conn.cursor()
        cur.execute('INSERT INTO lessons (name, content, preview_path, img1_path, img2_path, img3_path)'
            'VALUES (%s, %s, %s, %s, %s, %s)',
            (name, content, str(preview_path), str(img1_path), str(img2_path), str(img3_path))
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
        conn = psycopg2.connect(
        host="localhost",
        database="flask_db",
        user="postgres",
        password="Dangely")
        # create a cursor object for execution
        cur = conn.cursor()
        cur.execute('SELECT id, name, content, preview_path, img1_path, img2_path, img3_path '
                    'FROM lessons')
        # process the result set
        row = cur.fetchone()
        all_lessons = []
        while row is not None:
            lesson = dict(id=row[0], name=row[1], content=row[2], preview_path=row[3], img1_path=row[4], img2_path=row[5], img3_path=row[6])
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
        conn = psycopg2.connect(
        host="localhost",
        database="flask_db",
        user="postgres",
        password="Dangely")
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
            lesson_dict = dict(id=row[0], name=row[1], content=row[2], preview_path=row[3], img1_path=row[4], img2_path=row[5], img3_path=row[6])
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
    # content = """play_measure_1
    #             for repeat_number in range(repeats-1):
    #             if repeat_number == 1:
    #                 play_measures_2_and_3
    #             elif repeat_number == 2:
    #                 play_measures_2_and_3
    #             else:
    #                 play_measure_2
    #             play_measures_4_and_5

    #             play_measure_1
    #             repeat_number = 1
    #             while repeat_number <= repeats:
    #                 play_measure_2
    #             if repeat_number == 1 or repeat_number == 2:
    #                 play_measure_3
    #             repeat_number = repeat_number + 1
    #             play_measures_4_and_5"""
    preview_path = request.form.get("preview_path")
    img1_path = request.form.get("lesson_image_1")
    img2_path = request.form.get("lesson_image_2")
    img3_path = request.form.get("lesson_image_3")
    # img_path = "loops.jpg"
    print(name, content, preview_path, img1_path, img2_path, img3_path)
    # if img_path:
    #     insert_lesson_into_lesson_tables(name, img_path, content)
    # else:
    #     insert_lesson_into_lesson_tables(name, None, content)
    insert_lesson_into_lesson_tables(name, content, preview_path, img1_path, img2_path, img3_path)
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