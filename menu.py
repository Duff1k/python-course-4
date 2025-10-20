import psycopg2


def insert_categories(cur):
    categories = ['Супы', 'Салаты', 'Горячее', 'Десерты', 'Напитки']

    for i in categories:
        cur.execute(
            """INSERT INTO category (name) VALUES (%s);""", (i,)
        )


def insert_dishes(cur):
    cur.execute("""
            INSERT INTO dish (title, price, category_id) VALUES
                ('Куриный суп', 250, 1),
                ('Солянка', 450, 1),
                ('Борщ', 330, 1),
                ('Оливье', 300, 2),
                ('Цезарь с курицей', 550, 2),
                ('Цезарь с креветками', 650, 2),
                ('Стейк', 1200, 3),
                ('Плов', 450, 3),
                ('Семга', 740, 3),
                ('Индейка на пару', 560.5, 3),
                ('Капучино', 250, 5),
                ('Чай черный', 85, 5),
                ('Сок', 120, 5),
                ('Морс', 100, 5),
                ('Кола без сахара', 150, 5);
    """)


def create_category_table(cur, insert: bool = False):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );            
    """)
    if insert:
        insert_categories(cur)


def create_dish_table(cur, insert: bool = False):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dish (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            title TEXT NOT NULL,
            price NUMERIC(8,2) CHECK (price > 0),
            category_id INT REFERENCES category(id) ON DELETE RESTRICT
        );
    """)
    if insert:
        insert_dishes(cur)


def show_console_menu():
    print("\nМЕНЮ РЕСТОРАНА")
    print("1. Показать всё меню")
    print("2. Показать блюда в ценовом диапазоне")
    print("3. Поиск по началу названия")
    print("4. Показать N самых дешёвых блюд")
    print("5. Категории и количество блюд")
    print("6. Выход")


def print_dishes(dishes):
    if dishes:
        print("Блюдо --- Цена --- Категория")
        for dish in dishes:
            print(f"{dish[0]} - {dish[1]} руб - {dish[2]}")
    else:
        print("Блюд не найдено.")


def show_menu(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.title, d.price, c.name 
            FROM dish d 
            INNER JOIN category c ON d.category_id = c.id 
            ORDER BY c.id, d.title;
        """)
        dishes = cur.fetchall()

        print("\n          МЕНЮ")
        return dishes


def show_dishes_in_price_range(conn):
    try:
        min_price = float(input("Введите минимальную цену: "))
        max_price = float(input("Введите максимальную цену: "))

        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.title, d.price, c.name 
                FROM dish d 
                INNER JOIN category c ON d.category_id = c.id 
                WHERE d.price BETWEEN %s AND %s 
                ORDER BY d.price ASC, d.title;
            """, (min_price, max_price))
            dishes = cur.fetchall()

            print(f"\nБЛЮДА В ДИАПАЗОНЕ ЦЕН {min_price} - {max_price} руб")
            return dishes

    except:
        print("Введите корректное значение цены.")
        return []


def search_dishes_by_prefix(conn):
    prefix = input("Введите начало названия блюда: ").strip()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.title, d.price, c.name 
            FROM dish d 
            INNER JOIN category c ON d.category_id = c.id 
            WHERE d.title ILIKE %s
            ORDER BY d.title;
        """, (prefix + "%",))
        dishes = cur.fetchall()

        print(f"\nБЛЮДА НА '{prefix}'")
        return dishes


def show_cheapest_dishes(conn):
    try:
        n = int(input("Введите количество блюд: "))

        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.title, d.price, c.name 
                FROM dish d 
                INNER JOIN category c ON d.category_id = c.id 
                ORDER BY d.price, d.title
                LIMIT %s;
            """, (n,))
            dishes = cur.fetchall()

            print(f"\n{n} ДЕШЁВЫХ БЛЮД")
            return dishes

    except:
        print("Введите целое число.")
        return []


def show_categories_with_dishes_count(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.name, COUNT(d.id) 
            FROM category c 
            LEFT JOIN dish d ON c.id = d.category_id 
            GROUP BY c.id
            ORDER BY c.id;
        """)
        categories = cur.fetchall()

        print("\nКОЛИЧЕСТВО БЛЮД В КАТЕГОРИЯХ")
        print("Категория - Количество блюд")
        for category in categories:
            print(f"{category[0]} - {category[1]}")
        return categories


try:
    with psycopg2.connect(
            dbname="restaurant_menu",
            user="postgres",
            password="12345678",
            host="localhost",
            port="5432"
    ) as conn:
        # print("Подключение к БД прошло успешно")

        with conn.cursor() as cur:
            create_category_table(cur, insert=True)
            create_dish_table(cur, insert=True)

        while True:
            show_console_menu()
            point = input("\nВыберите пункт меню (1-6): ").strip()

            if point == '1':
                print_dishes(show_menu(conn))
            elif point == '2':
                print_dishes(show_dishes_in_price_range(conn))
            elif point == '3':
                print_dishes(search_dishes_by_prefix(conn))
            elif point == '4':
                print_dishes(show_cheapest_dishes(conn))
            elif point == '5':
                show_categories_with_dishes_count(conn)
            elif point == '6':
                print("Выходим из меню. До встречи!")
                break
            else:
                print("Выберите пункт от 1 до 6.")


except Exception as e:
    print(f"Ошибка: {e}")
