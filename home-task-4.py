import psycopg2


#Заполнение таблицы с категориями
def insert_categories(cur):
    cur.execute("""
                INSERT INTO category (name) 
                VALUES ('Супы'),
                       ('Салаты'),
                       ('Горячее'),
                       ('Десерты'),
                       ('Напитки'),
                       ('Алкоголь');
                """)
    print("Заполнили категории")
    print(" ")


#Заполнение таблицы блюд
def insert_dishes(cur):
    cur.execute("""
                INSERT INTO dish (title, price, category_id)
                VALUES  ('Борщ', 300, 1),
                        ('Рассольник', 250, 1),
                        ('Щи', 270.30, 1),
                        ('Оливье', 150, 2),
                        ('Крабовый салат', 100.99, 2),
                        ('Цезарь', 230, 2),
                        ('Винегрет', 75, 2),
                        ('Тушеная картошка', 120, 3),
                        ('Запеченая курица', 190, 3),
                        ('Наполеон', 100, 4),
                        ('Медовик', 70, 4), 
                        ('Мороженое', 50, 4),
                        ('Тирамису', 105, 4),
                        ('Круасан', 340, 4),
                        ('Чай', 30, 5),
                        ('Морс', 50, 5),
                        ('Кофе', 70, 5),
                        ('Лимонад', 90, 5),
                        ('Цикорий', 60, 5);
                """)
    print("Заполнили блюда")
    print(" ")


#Создание таблицы с категориями
def create_category_table(cur, insert: bool = False):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
    """)
    if insert:
        insert_categories(cur)


#Создание таблицы блюд
def create_dish_table(cur, insert: bool = False):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dish (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            title TEXT NOT NULL,
            price NUMERIC(8,2),
            category_id INT REFERENCES category(id) ON DELETE SET NULL
        );
    """)
    if insert:
        insert_dishes(cur)


#Запрос всех блюд
def get_all_dishes(conn):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT 
                        d.title "Блюдо",
                        d.price "Цена",
                        c.name "Категория"
                    FROM dish d
                    JOIN category c ON d.category_id = c.id;
                    """)
        dishes_all = cur.fetchall()

        for dish_title, dish_price, dich_categoty in dishes_all:
            dish = f'{dish_title}—{dish_price}—{dich_categoty}'
            print(dish)

        print('')
        return cur.fetchall()


#Запрос блюд по диапазону цен
def get_dishes_by_price(conn, min_price, max_price):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT
                        d.title "Блюдо",
                        d.price "Цена",
                        c.name "Категория"
                    FROM dish d
                    JOIN category c ON d.category_id = c.id
                    WHERE d.price BETWEEN %s AND %s
                    """, (min_price, max_price))
        dishes_by_price = cur.fetchall()

        for dish_title, dish_price, dich_categoty in dishes_by_price:
            dish = f'{dish_title}—{dish_price}—{dich_categoty}'
            print(dish)

        print('')
        return cur.fetchall()


#Запрос блюд по названию
def get_dishes_by_name(conn, dish_name):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT
                        d.title "Блюдо",
                        d.price "Цена",
                        c.name "Категория"
                    FROM dish d
                    JOIN category c ON d.category_id = c.id
                    WHERE LOWER(d.title) LIKE LOWER(%s)  
                    """, (dish_name + '%', ))
        dishes_by_price = cur.fetchall()

        for dish_title, dish_price, dich_categoty in dishes_by_price:
            dish = f'{dish_title}—{dish_price}—{dich_categoty}'
            print(dish)

        print('')
        return cur.fetchall()


#Запрос N самых дешевых блюд
def get_cheapest_dishes(conn, N):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT
                        d.title "Блюдо",
                        d.price "Цена",
                        c.name "Категория"
                    FROM dish d
                    JOIN category c ON d.category_id = c.id
                    ORDER BY d.price ASC
                    LIMIT %s  
                    """, (N, ))
        dishes_by_price = cur.fetchall()

        for dish_title, dish_price, dich_categoty in dishes_by_price:
            dish = f'{dish_title}—{dish_price}—{dich_categoty}'
            print(dish)

        print('')
        return cur.fetchall()


#Запрос всех категорий
def get_all_categories(conn):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT 
	                    c.name "Категория",
	                    COUNT(*) "Количество блюд" 
                    FROM category c
                    INNER JOIN dish d ON d.category_id = c.id
                    GROUP BY c.id
                    ORDER BY c.id
                    """)
        categories_all = cur.fetchall()

        for category_name, dish_count in categories_all:
            dish = f'{category_name}—{dish_count}'
            print(dish)

        print('')
        return cur.fetchall()


#Консольное меню
def menu(conn, action = 0):
    try:
        if action == 0:
            print('1. Показать меню')
            print('2. Показать блюда в ценовом диапазоне')
            print('3. Поиск по началу названия (префикс)')
            print('4. Показать N самых дешёвых блюд')
            print('5. Категории и количество блюд')
            print('6. Выход')
            print('')
            menu(conn, int(input('Выберите пункт: ')))
        elif action == 1:
            get_all_dishes(conn)
            print('')
            menu(conn, int(input('Введите 0, чтобы показать меню: ')))
        elif action == 2:
            get_dishes_by_price(conn, int(input('Введите минимальную сумму: ')), int(input('Введите максимальную сумму: ')))
            print('')
            menu(conn, int(input('Введите 0, чтобы показать меню: ')))
        elif action == 3:
            get_dishes_by_name(conn, str(input('Введите название блюда: ')))
            print('')
            print('Введите 0, чтобы показать меню и 3, чтобы продолжить поиск')
            menu(conn, int(input('Введите 0 или 3: ')))
        elif action == 4:
            get_cheapest_dishes(conn, int(input('Введите N: ')))
            print('')
            menu(conn, int(input('Введите 0, чтобы показать меню: ')))
        elif action == 5:
            get_all_categories(conn)
            print('')
            menu(conn, int(input('Введите 0, чтобы показать меню: ')))
        elif action == 6:
            print('До свидания!')
            conn.close()
    except:
        print('Данного пункта нет в меню.')
        menu(conn, int(input('Выберите пункт: ')))


#Запуск подключения
try:
    with psycopg2.connect(
        dbname="******",         #введите название своей базы данных
        user="********",         #введите имя пользователя, под которым вы создали свою БД
        password="********",     #введите пароль, под которым вы создали свою БД
        host="localhost",        #введите host
        port="5432"              #введите порт
    ) as conn:
        with conn.cursor() as cur:
            create_category_table(cur, True)
            create_dish_table(cur, True)
            menu(conn)
except:
    print("Ошибка при подключении к БД")