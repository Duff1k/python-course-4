import psycopg2

def insert_students(cur):
    cur.execute("""
                INSERT INTO students (full_name, age, group_name)
                VALUES ('Иван Петров', 21, 'ВИШ-10'),
                       ('Мария Сидорова', 19, 'ВИШ-11'),
                       ('Анна Кузнецова', 20, 'ВИШ-10');
                """)
    print("Заполнили студентов")

def insert_courses(cur):
    cur.execute(
        "INSERT INTO courses(title, hours, teacher) VALUES (%s, %s, %s);",
        ("Основы Python", 36, "Юрий Анатольевич Андриенко")
    )

    cur.execute(
        "INSERT INTO courses(title, hours, teacher) VALUES (%s, %s, %s);",
        ("Базы данных", 48, "Михаил Георгиевич Жабицкий")
    )

    print("Заполнили курсы")


def insert_enrollments(cur):
    enrollments = [
        (1, 1),
        (1, 2),
        (2, 1),
        (3, 2)
    ]

    cur.executemany(
        "INSERT INTO enrollments (student_id, course_id) VALUES (%s, %s);",
        enrollments
    )

    print("Заполнили зачисления на курсы")


def create_students_table(cur, insert: bool = False ):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            full_name VARCHAR(50) NOT NULL,
            age INT CHECK (age>0),
            group_name TEXT,
            admission_date DATE DEFAULT CURRENT_DATE 
        );            
    """)
    if insert:
       insert_students(cur)

def create_courses_table(cur, insert: bool = False):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            title TEXT NOT NULL,
            hours INT CHECK (hours>0),
            teacher TEXT NOT NULL
        );
    """)
    if insert:
        insert_courses(cur)

def create_enrollments_table(cur, insert: bool = False):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS enrollments (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            student_id INT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
            course_id INT NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
            erollment_date DATE DEFAULT CURRENT_DATE,
            UNIQUE (student_id, course_id)
        );
    """)
    if insert:
        insert_enrollments(cur)

def get_all_students(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT id, full_name, age, group_name FROM students ORDER BY id DESC")
        return cur.fetchall()

def get_first_student_older_than(conn, min_age):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, full_name, age
            FROM students
            WHERE age > %s
            ORDER BY id DESC, id
            LIMIT 1;
        """, (min_age,))
        return cur.fetchone()

def search_students_by_prefix(conn, start):
    prefix = str(start)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, full_name
            FROM students
            WHERE full_name ILIKE %s
            ORDER BY id;
        """, (prefix + "%",))
        return cur.fetchall()

def get_student_courses(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT s.full_name, c.title
            FROM enrollments e
            INNER JOIN students s ON s.id = e.student_id
            INNER JOIN courses c ON c.id = e.course_id
            ORDER BY s.full_name, c.title;
        """)
        return cur.fetchall()

def get_students_of_course(conn, course_title):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT s.full_name, c.title
            FROM enrollments e
            INNER JOIN students s ON s.id = e.student_id
            INNER JOIN courses c ON c.id = e.course_id
            WHERE c.title = %s
        """, (course_title,))
        return cur.fetchall()

def get_students_between_ages(conn, min_age, max_age):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, full_name, age
            FROM students
            WHERE age BETWEEN %s AND %s
            ORDER BY id DESC
        """,(min_age, max_age))
        return cur.fetchall()

def get_course_student_counts(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.title, COUNT(*) AS total_students
            FROM enrollments e
            INNER JOIN courses c ON c.id = e.course_id
            GROUP BY title
        """)
        return cur.fetchall()

def get_students_on_course_by_min_hours(conn, min_hours):
    with conn.cursor() as cur:
        cur.execute("""
        SELECT DISTINCT s.full_name, c.title, c.hours
        FROM enrollments e
        INNER JOIN students s ON s.id = e.student_id
        INNER JOIN courses c ON c.id = e.course_id
        WHERE c.hours > %s;
        """, (min_hours,))
        return cur.fetchall()

try:
    with psycopg2.connect(
        dbname="python_course_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    ) as conn:
        print("Подключение к БД прошло успешно")

        with conn.cursor() as cur:
            create_students_table(cur)
            create_courses_table(cur)
            create_enrollments_table(cur)
            print(get_all_students(conn))
            print(get_first_student_older_than(conn, 19))
            print(search_students_by_prefix(conn, "аНн"))
            print(get_student_courses(conn))
            print(get_students_of_course(conn, "Базы данных"))
            print(get_students_between_ages(conn, 20, 21))
            print(get_course_student_counts(conn))
            print(get_students_on_course_by_min_hours(conn, 30))

except:
    print("Ошибка при подключении к БД")
