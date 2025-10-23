import psycopg2
from psycopg2 import sql

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="YOUR_PASSWORD",
        host="localhost",
        port="5432"
    )
    print("Подключение к БД успешно")

    # Создаем курсор
    cur = conn.cursor()

    # Создаем таблицу category
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    """)

    # Создаем таблицу dish
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dish (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            title TEXT NOT NULL,
            price NUMERIC(8,2) CHECK (price > 0),
            category_id INT,
            CONSTRAINT fk_category
                FOREIGN KEY(category_id) 
                REFERENCES category(id)
                ON DELETE SET NULL
        )
    """)

    # Вставляем категории (только если таблица пустая)
    cur.execute("SELECT COUNT(*) FROM category")
    if cur.fetchone()[0] == 0:
        categories = [
            ("Супы",),
            ("Салаты",),
            ("Горячее",),
            ("Десерты",),
            ("Напитки",)
        ]
        cur.executemany("INSERT INTO category (name) VALUES (%s)", categories)

    # Вставляем блюда русской кухни (только если таблица пустая)
    cur.execute("SELECT COUNT(*) FROM dish")
    if cur.fetchone()[0] == 0:
        dishes = [
            ("Борщ", 350.00, 1), ("Щи", 320.00, 1), ("Солянка", 380.00, 1),
            ("Уха", 400.00, 1), ("Рассольник", 340.00, 1),
            ("Оливье", 280.00, 2), ("Сельдь под шубой", 320.00, 2),
            ("Винегрет", 220.00, 2), ("Салат Столичный", 300.00, 2),
            ("Мимоза", 290.00, 2), ("Бефстроганов", 450.00, 3),
            ("Пельмени", 380.00, 3), ("Голубцы", 420.00, 3),
            ("Котлеты по-киевски", 480.00, 3), ("Жаркое в горшочке", 460.00, 3),
            ("Блины с мясом", 320.00, 3), ("Сырники", 280.00, 4),
            ("Медовик", 220.00, 4), ("Пряники", 180.00, 4),
            ("Пастила", 190.00, 4), ("Блины с вареньем", 250.00, 4),
            ("Квас", 120.00, 5), ("Морс", 130.00, 5), ("Сбитень", 150.00, 5),
            ("Компот", 110.00, 5), ("Чай из самовара", 200.00, 5)
        ]
        cur.executemany("INSERT INTO dish (title, price, category_id) VALUES (%s, %s, %s)", dishes)

    cur.close()

    # Основной цикл меню
    while True:
        print("-"*50)
        print("1 - Показать всё меню")
        print("2 - Показать блюда в ценовом диапазоне")
        print("3 - Поиск по началу названия")
        print("4 - Показать N самых дешёвых блюд")
        print("5 - Категории и количество блюд")
        print("6 - Выход")
        print("-" * 50)
        choice = input("Выберите пункт меню (1-6): ").strip()

        if choice == "1":
            cur = conn.cursor()
            cur.execute("""
                SELECT d.title, d.price, c.name 
                FROM dish d 
                LEFT JOIN category c ON d.category_id = c.id 
                ORDER BY c.name, d.title
            """)
            print("--- Всё меню ---")
            for row in cur.fetchall():
                print(f"{row[0]} — {row[1]} руб. — {row[2]}")
            cur.close()


        elif choice == "2":

            try:

                min_price = float(input("Введите минимальную цену: "))

                max_price = float(input("Введите максимальную цену: "))

                # Проверяем, что максимальная цена больше минимальной

                if max_price <= min_price:
                    print("Ошибка: максимальная цена должна быть больше минимальной")

                    continue

                cur = conn.cursor()

                cur.execute("""

                           SELECT d.title, d.price, c.name 

                           FROM dish d 

                           LEFT JOIN category c ON d.category_id = c.id 

                           WHERE d.price BETWEEN %s AND %s

                           ORDER BY d.price

                       """, (min_price, max_price))

                print(f"--- Блюда в диапазоне {min_price}-{max_price} руб. ---")

                dishes = cur.fetchall()

                if dishes:

                    for row in dishes:
                        print(f"{row[0]} — {row[1]} руб. — {row[2]}")

                else:

                    print("Блюда не найдены")

                cur.close()

            except ValueError:

                print("Ошибка: введите корректные числа")

        elif choice == "3":
            prefix = input("Введите начало названия блюда: ").strip()
            if not prefix:
                print("Ошибка: введите текст для поиска")
                continue
            cur = conn.cursor()
            cur.execute("""
                SELECT d.title, d.price, c.name 
                FROM dish d 
                LEFT JOIN category c ON d.category_id = c.id 
                WHERE LOWER(d.title) LIKE LOWER(%s)
                ORDER BY d.title
            """, (f"{prefix}%",))
            print(f"--- Блюда, начинающиеся с '{prefix}' ---")
            dishes = cur.fetchall()
            if dishes:
                for row in dishes:
                    print(f"{row[0]} — {row[1]} руб. — {row[2]}")
            else:
                print("Блюда не найдены")
            cur.close()

        elif choice == "4":
            try:
                n = int(input("Введите количество блюд (N): "))
                if n <= 0:
                    print("Ошибка: введите положительное число")
                    continue
                cur = conn.cursor()
                cur.execute("""
                    SELECT d.title, d.price, c.name 
                    FROM dish d 
                    LEFT JOIN category c ON d.category_id = c.id 
                    ORDER BY d.price 
                    LIMIT %s
                """, (n,))
                print(f"--- {n} самых дешёвых блюд ---")
                for row in cur.fetchall():
                    print(f"{row[0]} — {row[1]} руб. — {row[2]}")
                cur.close()
            except ValueError:
                print("Ошибка: введите целое число")

        elif choice == "5":
            cur = conn.cursor()
            cur.execute("""
                SELECT c.name, COUNT(d.id) 
                FROM category c 
                LEFT JOIN dish d ON c.id = d.category_id 
                GROUP BY c.id, c.name 
                ORDER BY c.name
            """)
            print("--- Категории и количество блюд ---")
            for row in cur.fetchall():
                print(f"{row[0]} — {row[1]} блюд")
            cur.close()

        elif choice == "6":
            print("До свидания!")
            break

        else:
            print("Ошибка: выберите пункт от 1 до 6")

except Exception as e:
    print(f"Ошибка: {e}")
finally:
    if conn is not None:
        conn.close()
        print("Соединение закрыто")