import psycopg2

def insert_categories(cur):
    cur.execute("""
                INSERT INTO category (name)
                VALUES ('Супы'),
                       ('Салаты'),
                       ('Горячее'),
                       ('Десерты'),
                       ('Напитки')
                """)
    print("Заполнили категории")

def insert_dishes(cur):
    cur.execute("""
                INSERT INTO dishes (title, price, category_id)
                VALUES ('Уха', 350, 1),
                       ('Суп-лапша', 250, 1),
                       ('Том-ям', 370, 1),
                       ('Гороховый суп', 300, 1),
                       ('Цезарь с курицей', 320, 2),
                       ('Греческий салат', 270, 2),
                       ('Селедка под шубой', 290, 2),
                       ('Мимоза', 290, 2),
                       ('Паста Карбонара', 400, 3),
                       ('Стейк из лосося', 600, 3),
                       ('Жульен', 420, 3),
                       ('Котлета по-домашнему с отварным картофелем', 500, 3),
                       ('Яблочный штрудель', 350, 4),
                       ('Медовик', 370, 4),
                       ('Эклер с заварным кремом', 300, 4),
                       ('Пироженое Картошка', 250, 4),
                       ('Клюквенный морс', 200, 5),
                       ('Чай травяной', 320, 5),
                       ('Раф на кокосовом', 400, 5),
                       ('Лимонад Малина-мята', 370, 5)
                 """)
    print("Заполнили блюда")

def create_category_table(cur, insert: bool = False ):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name VARCHAR(50) NOT NULL UNIQUE
        );            
    """)
    if insert:
       insert_categories(cur)

def create_dish_table(cur, insert: bool = False ):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dishes (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            title TEXT NOT NULL UNIQUE,
            price NUMERIC(8,2) NOT NULL,
            category_id INT REFERENCES category(id) ON DELETE SET NULL
        );            
    """)
    if insert:
       insert_dishes(cur)

def get_all_dishes(conn):
    print("Название блюда/Категория/Цена")
    with conn.cursor() as cur:
        cur.execute("""
                SELECT
                    d.title AS dish_title,
                    d.price AS dish_price,
                    c.name AS category_name
                FROM dishes d
                JOIN category c ON d.category_id = c.id;
            """)
        all_dishes = cur.fetchall()

        for dish_title, dish_price, category_name in all_dishes:
            print(f'{dish_title} / {category_name}/ {dish_price}')

        return cur.fetchall()

def get_dishes_min_max(conn, min_price, max_price):
    print("Название блюда/Категория/Цена")
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT
                        d.title AS dish_title,
                        d.price AS dish_price,
                        c.name AS category_name
                    FROM dishes d
                    JOIN category c ON d.category_id = c.id
                    WHERE d.price BETWEEN %s AND %s
                    """, (min_price, max_price))
        dishes_min_max = cur.fetchall()

        for dish_title, dish_price, category_name in dishes_min_max:
            print(f'{dish_title} / {category_name}/ {dish_price}')

        return cur.fetchall()

def get_dishes_by_prefix(conn, dish_name):
    print("Название блюда / Категория / Цена")
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT
                        d.title AS dish_title,
                        d.price AS dish_price,
                        c.name AS category_name
                    FROM dishes d
                    JOIN category c ON d.category_id = c.id
                    WHERE LOWER(d.title) LIKE LOWER(%s)  
                    """, (dish_name + '%',))
        dishes_by_prefix = cur.fetchall()

        for dish_title, dish_price, category_name in dishes_by_prefix:
            print(f'{dish_title} / {category_name} / {dish_price}')

        return cur.fetchall()

def get_cheap_dishes(conn, N):
    print("Название блюда / Категория / Цена")
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT
                        d.title AS dish_title,
                        d.price AS dish_price,
                        c.name AS category_name
                    FROM dishes d
                    JOIN category c ON d.category_id = c.id
                    ORDER BY d.price ASC
                    LIMIT %s  
                    """, (N, ))
        cheap_dishes = cur.fetchall()

        for dish_title, dish_price, category_name in cheap_dishes:
            print(f'{dish_title} / {category_name}/ {dish_price}')

        return cur.fetchall()

def get_all_categories(conn):
    print("Категория / Кол-во блюд в категории")
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT 
                        c.name AS category_name,
	                    COUNT(*) AS dish_count
                    FROM category c
                    INNER JOIN dishes d ON d.category_id = c.id
                    GROUP BY c.id
                    ORDER BY c.id
                    """)
        all_categories = cur.fetchall()

        for category_name, dish_count in all_categories:
            dish = f'{category_name}/{dish_count}'
            print(dish)

        return cur.fetchall()

def console_menu(conn, action = 0):
    try:
        if action == 0:
            print('Консольное меню:')
            print('1 - Показать меню блюд')
            print('2 - Показать блюда в ценовом диапазоне')
            print('3 - Поиск по началу названия (префикс)')
            print('4 - Показать N самых дешёвых блюд')
            print('5 - Категории и количество блюд')
            print('6 - Выход')

            console_menu(conn, int(input('Выберите соответствующий пункт: ')))

        elif action == 1:
            get_all_dishes(conn)
            console_menu(conn, int(input('Введите 0, чтобы вернутся в консольное меню: ')))

        elif action == 2:
            get_dishes_min_max(conn, int(input('Введите нижнюю границу: ')), int(input('Введите верхнюю границу: ')))
            console_menu(conn, int(input('Введите 0, чтобы вернутся в консольное меню: ')))

        elif action == 3:
            get_dishes_by_prefix(conn, str(input('Введите название блюда: ')))
            console_menu(conn, int(input('Введите 0, чтобы вернутся в консольное меню: ')))

        elif action == 4:
            get_cheap_dishes(conn, int(input('Введите кол-во блюд N в подборке: ')))
            console_menu(conn, int(input('Введите 0, чтобы вернутся в консольное меню: ')))

        elif action == 5:
            get_all_categories(conn)
            console_menu(conn, int(input('Введите 0, чтобы вернутся в консольное меню: ')))

        elif action == 6:
            conn.close()

    except Exception as e:
        print("Ошибка:", e)


try:
    with psycopg2.connect(
            dbname="python_course_db",
            user="postgres",
            password="psql -U $(whoami) -d postgres",
            host="localhost",
            port="5432"
    ) as conn:
        print("Успешное подключение к бд")
        with conn.cursor() as cur:
            create_category_table(cur, True)
            create_dish_table(cur, True)
            console_menu(conn)

except Exception as e:
    print("Ошибка:", e)
