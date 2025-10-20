import psycopg2

def insert_categories(cur):
    categories = [
        ('Супы',),
        ('Салаты',),
        ('Горячее',),
        ('Десерты',),
        ('Напитки',)
    ]

    cur.executemany(
        "INSERT INTO category (name) VALUES (%s);",
        categories
    )
    print("Таблица 'category' заполнена.")


def insert_dishes(cur):
    dishes = [
        ('Борщ', 350.00, 1),
        ('Солянка', 400.50, 1),
        ('Цезарь с курицей', 450.00, 2),
        ('Греческий салат', 380.00, 2),
        ('Стейк Рибай', 1500.00, 3),
        ('Паста Карбонара', 600.00, 3),
        ('Бефстроганов', 750.00, 3),
        ('Тирамису', 300.00, 4),
        ('Чизкейк', 320.00, 4),
        ('Морс клюквенный', 150.00, 5),
        ('Эспрессо', 200.00, 5)
    ]
    cur.executemany(
        "INSERT INTO dish (title, price, category_id) VALUES (%s, %s, %s);",
        dishes
    )
    print("Таблица 'dish' заполнена.")

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
        price NUMERIC(8,2) CHECK (price>0),
        category_id INT,
        FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL
    );
    """)

    if insert:
        insert_dishes(cur)

def get_all_dishes(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT title, price, name
            FROM dish
            JOIN category ON dish.category_id = category.id
            ORDER BY name DESC
        """)
        return cur.fetchall()

def get_dishes_between_min_and_max(conn, min_price, max_price):
    with conn.cursor() as cur:
        query = """
            SELECT title, price
            FROM dish
            WHERE price BETWEEN %s AND %s
            ORDER BY price
        """
        cur.execute(query, (min_price, max_price))
        return cur.fetchall()

def search_dishes_by_prefix(conn, prefix):
    with conn.cursor() as curp:
        query = """
            SELECT id, title
            FROM dish
            WHERE title ILIKE %s
            ORDER BY id;
        """
        curp.execute(query, (prefix + "%",))
        return curp.fetchall()

def get_top_lowest_dishes(conn, n):
    with conn.cursor() as cur:
        query = """
            SELECT title, price
            FROM dish
            ORDER BY price
            LIMIT %s 
        """
        cur.execute(query, (n,))
        return cur.fetchall()

def get_category_total_dish(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.name, COUNT(d.id) AS total_dishes
            FROM category c -- Начинаем с категорий
            LEFT JOIN dish d ON c.id = d.category_id -- Делаем LEFT JOIN к блюдам
            GROUP BY c.id, c.name -- Группируем по категории
            ORDER BY c.name;
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
        dbname="HW4_dishes",
        user="postgres",
        password="admin",
        host="localhost",
        port="5432"
    ) as conn:
        print("Подключение к БД прошло успешно\n")

        with conn.cursor() as cur:
            create_category_table(cur) 
            create_dish_table(cur)

            while True:
                print("--- Меню ресторана ---")
                print("1. Показать все блюда с категориями")
                print("2. Показать блюда в диапазоне цен")
                print("3. Поиск блюд по названию")
                print("4. Показать топ N самых дешевых блюд")
                print("5. Показать категории и количество блюд")
                print("0. Выход")
                
                choice = input("Выберите действие: ")
                print() 

                try:
                    if choice == '1':
                        print("--- Все блюда ---")
                        all_dishes = get_all_dishes(conn)
                        table_look_like(
                            "Блюдо               \tЦена                \tКатегория",
                            all_dishes
                        )
                    
                    elif choice == '2':
                        print("--- Блюда в диапазоне цен ---")
                        min_p = float(input("Введите минимальную цену: "))
                        max_p = float(input("Введите максимальную цену: "))
                        if min_p > max_p:
                            print("Ошибка: Минимальная цена больше максимальной.\n")
                            continue
                        
                        dishes = get_dishes_between_min_and_max(conn, min_p, max_p)
                        table_look_like("Блюдо               \tЦена", dishes)

                    elif choice == '3':
                        print("--- Поиск блюд по названию ---")
                        prefix = input("Введите начало названия блюда: ")
                        if not prefix:
                            print("Ошибка: Ввод не может быть пустым.\n")
                            continue
                            
                        dishes = search_dishes_by_prefix(conn, prefix)
                        table_look_like("ID                  \tБлюдо", dishes)

                    elif choice == '4':
                        print("--- Топ N самых дешевых блюд ---")
                        n = int(input("Сколько блюд показать (N): "))
                        if n <= 0:
                            print("Ошибка: Число должно быть положительным.\n")
                            continue
                            
                        dishes = get_top_lowest_dishes(conn, n)
                        table_look_like("Блюдо               \tЦена", dishes)

                    elif choice == '5':
                        print("--- Категории и количество блюд ---")
                        category_counts = get_category_total_dish(conn) 
                        table_look_like(
                            "Категория           \tКол-во блюд", 
                            category_counts
                        )
                    
                    elif choice == '0':
                        break

                    else:
                        print("Неверный выбор. Пожалуйста, введите число от 0 до 5.\n")

                except:
                    print("Произошла ошибка при выполнении запроса")

except Exception as e:
    print("Ошибка при подключении или работе с БД:", e)
