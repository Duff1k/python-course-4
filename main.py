from pickletools import string1

import psycopg2

def insert_categories(curp):
    curp.execute("""
        INSERT INTO category (name)
        VALUES ('Супы'),
               ('Салаты'),
               ('Горячее'),
               ('Десерты'),
               ('Напитки');
        """)


def insert_dishes(curp):
    curp.execute("""
        INSERT INTO dish (title, price, category_id)
        VALUES ('Margherita Pizza', 1250.50, 3),
               ('Caesar Salad', 375.75, 2),
               ('Grilled Chicken', 500.00, 3),
               ('Chocolate Cake', 359.99, 4),
               ('Iced Tea', 150.00, 5),
               ('French Fries', 140.25, 3),
               ('Spaghetti Bolognese', 740.99, 3),
               ('Greek Salad', 509.50, 2),
               ('Fish and Chips', 916.75, 3),
               ('Tiramisu', 407.25, 4),
               ('Coffee', 82.99, 5),
               ('Onion Rings', 205.00, 3),
               ('Borsh', 410.50, 1),
               ('Caprese Salad', 710.00, 2),
               ('Solyanka', 609.99, 1),
               ('Cheesecake', 310.50, 4),
               ('Orange Juice', 110.00, 5),
               ('Mashed Potatoes', 405.75, 3),
               ('Xarcho', 610.25, 1),
               ('Fruit Salad', 405.00, 4);
        """)


def create_category_table(curp, insert: bool = False):
    curp.execute("""
    CREATE TABLE IF NOT EXISTS category (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    );            
    """)
    print(curp.name)
    if insert:
       insert_categories(curp)

def create_dish_table(curp, insert: bool = False):
    curp.execute("""
    CREATE TABLE IF NOT EXISTS dish (
        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
        title TEXT NOT NULL,
        price NUMERIC(8,2) CHECK (price>0),
        category_id INT,
        FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL
    );
    """)
    if insert:
        insert_dishes(curp)


def get_all_dishes(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT title, price, name
            FROM dish
            JOIN category ON dish.category_id = category.id
            ORDER BY name DESC
        """)
        return cur.fetchall()

def get_dishes_between_prices(conn, min_price, max_price):
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT title, price
            FROM dish
            WHERE price BETWEEN {min_price} AND {max_price}
            ORDER BY price
        """)
        return cur.fetchall()

def search_dishes_by_prefix(conn, start):
    with conn.cursor() as curp:
        pref = str(start)
        curp.execute(f"""
            SELECT id, title
            FROM dish
            WHERE title ILIKE '{pref + "%"}'
            ORDER BY id;
        """)
        return curp.fetchall()

def get_top_lowest_dishes(conn, n):
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT title, price
            FROM dish
            ORDER BY price
            LIMIT {n} 
        """)
        return cur.fetchall()

def get_category_total_dish(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT category_id, name, COUNT(category_id) AS total_dishes
            FROM dish
            join category on category.id = dish.category_id
            GROUP BY category_id, name
            ORDER BY category_id;
        """)
        return cur.fetchall()

def table_look_like(headers, rows):
    print(headers)
    for row in rows:
        print(tab_control(row))
    print()

def tab_control(strarr):
    stt = ""
    for st in strarr:
        stt = stt + str(st) + "\t"
    return stt

try:
    with psycopg2.connect(
        dbname="python_course_db",
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    ) as conn:
        with conn.cursor() as cur:
            create_category_table(cur, True)
            create_dish_table(cur, True)
            while (True):
                menu = ("Показать всё меню",
                        "Показать блюда в ценовом диапазоне",
                        "Поиск по началу префикса",
                        "Показать N самых дешёвых блюд",
                        "Категории и количество блюд",
                        "Выход"
                        )
                for i in range (len(menu)):
                    print(f"{i+1}. {menu[i]}")
                num = int(input("Введите номер пункта: "))
                if num == 1:
                    table_look_like("Блюдо\tЦена\tКатегория", get_all_dishes(conn))
                elif num == 2:
                    min_price = int(input("Введите минимальную стоимость:"))
                    max_price = int(input("Введите максимальную стоимость:"))
                    table_look_like("Блюдо\tЦена",get_dishes_between_prices(conn, min_price, max_price))
                elif num == 3:
                    prefix = input("Введите начало названия блюда (префикс):")
                    table_look_like("№\tБлюдо",search_dishes_by_prefix(conn, prefix))
                elif num == 4:
                    n = int(input("Введите число N:"))
                    table_look_like("Блюдо\tЦена", get_top_lowest_dishes(conn, n))
                elif num == 5:
                    table_look_like("№\tКатегоря\tКол-во блюд", get_category_total_dish(conn))
                elif num ==6:
                    break
                else:
                    continue
except:
    print("Ошибка при подключении к БД.")