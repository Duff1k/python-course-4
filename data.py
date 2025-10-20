import psycopg2


def create_category_table(cur, insert=False):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        )
    """)
    if insert:
        insert_categories(cur)


def create_dish_table(cur, insert=False):
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
    if insert:
        insert_dishes(cur)


def insert_categories(cur):
    # Проверяем, есть ли уже категории в базе
    cur.execute("SELECT COUNT(*) FROM category")
    count = cur.fetchone()[0]

    if count > 0:
        print("Категории уже существуют в базе данных")
        return

    categories = [
        ('Супы',), ('Салаты',), ('Горячее',), ('Десерты',), ('Напитки',)
    ]
    cur.executemany("INSERT INTO category (name) VALUES (%s)", categories)
    print("Заполнили категории")


def insert_dishes(cur):
    # Проверяем, есть ли уже блюда в базе
    cur.execute("SELECT COUNT(*) FROM dish")
    count = cur.fetchone()[0]

    if count > 0:
        print("Блюда уже существуют в базе данных")
        return

    dishes = [
        ('Борщ', 350.00, 1), ('Куриный суп', 280.00, 1),
        ('Грибной крем-суп', 310.00, 1), ('Солянка', 420.00, 1),
        ('Том Ям', 480.00, 1), ('Луковый суп', 320.00, 1),
        ('Харчо', 380.00, 1), ('Уха', 350.00, 1),
        ('Цезарь', 420.00, 2), ('Греческий салат', 380.00, 2),
        ('Оливье', 290.00, 2), ('Сельдь под шубой', 320.00, 2),
        ('Капрезе', 450.00, 2), ('Винегрет', 240.00, 2),
        ('Салат с тунцом', 390.00, 2), ('Крабовый салат', 410.00, 2),
        ('Салат Нисуаз', 470.00, 2), ('Мимоза', 330.00, 2),
        ('Лосось на гриле', 890.00, 3), ('Курица терияки', 650.00, 3),
        ('Бефстроганов', 720.00, 3), ('Индейка', 750.00, 3),
        ('Лазанья', 680.00, 3), ('Рататуй', 540.00, 3),
        ('Шоколадный фондан', 270.00, 4), ('Панна котта', 290.00, 4),
        ('Медовик', 300.00, 4), ('Сырники со сметаной', 260.00, 4),
        ('Тирамису', 350.00, 4), ('Чизкейк', 320.00, 4),
        ('Латте', 350.00, 5), ('Свежевыжатый сок', 380.00, 5),
        ('Капучино', 320.00, 5), ('Эспрессо', 150.00, 5),
        ('Молочный коктейль', 280.00, 5), ('Смузи', 370.00, 5)
    ]
    cur.executemany("INSERT INTO dish (title, price, category_id) VALUES (%s, %s, %s)", dishes)
    print("Заполнили блюда")


def show_all_menu(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.title, d.price, c.name as category
            FROM dish d
            LEFT JOIN category c ON d.category_id = c.id
            ORDER BY c.name, d.title
        """)
        results = cur.fetchall()

        if results:
            print("\n..... Меню .....")
            for row in results:
                print(f"{row[0]} — {row[1]:.2f} руб. — {row[2]}")
        else:
            print("..... Меню пусто .....")


def show_dishes_by_price_range(conn):
    try:
        min_price = float(input("Введите минимальную цену: "))
        max_price = float(input("Введите максимальную цену: "))

        if min_price < 0 or max_price < 0:
            print("Ошибка: цена не может быть отрицательной")
            return

        if min_price > max_price:
            print("Ошибка: минимальная цена не может быть больше максимальной")
            return

        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.title, d.price, c.name as category
                FROM dish d
                LEFT JOIN category c ON d.category_id = c.id
                WHERE d.price BETWEEN %s AND %s
                ORDER BY d.price
            """, (min_price, max_price))
            results = cur.fetchall()

            if results:
                print(f"\n..... Блюда в диапазоне {min_price}-{max_price} руб. .....")
                for row in results:
                    print(f"{row[0]} - {row[1]:.2f} руб. - {row[2]}")
            else:
                print("Блюд в указанном диапазоне не найдено")

    except ValueError:
        print("Ошибка: введите корректные числовые значения")


def search_by_prefix(conn):
    prefix = input("Введите начало названия блюда: ").strip()

    if not prefix:
        print("Ошибка: введите текст для поиска")
        return

    prefix = str(prefix)

    # Создаем варианты поиска для разных регистров
    search_variants = [
        prefix,  # как ввел пользователь
        prefix.capitalize()  # с заглавной буквы
    ]

    # Добавляем % к каждому варианту для поиска по префиксу
    search_patterns = [variant + "%" for variant in search_variants]

    with conn.cursor() as cur:
        placeholders = ','.join(['%s'] * len(search_patterns))

        cur.execute(f"""
            SELECT d.title, d.price, c.name as category
            FROM dish d
            LEFT JOIN category c ON d.category_id = c.id
            WHERE d.title ILIKE ANY(ARRAY[{placeholders}])
            ORDER BY d.title
        """, search_patterns)
        results = cur.fetchall()

        if results:
            print(f"\n..... Результаты поиска по '{prefix}' .....")
            for row in results:
                print(f"{row[0]} - {row[1]:.2f} руб. - {row[2]}")
        else:
            print(f"..... Блюд с началом '{prefix}' не найдено .....")


def show_cheapest_dishes(conn):
    try:
        n = int(input("Введите количество блюд (N): "))

        if n <= 0:
            print("Ошибка: введите положительное число")
            return

        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.title, d.price, c.name as category
                FROM dish d
                LEFT JOIN category c ON d.category_id = c.id
                ORDER BY d.price
                LIMIT %s
            """, (n,))
            results = cur.fetchall()

            if results:
                print(f"\n..... {n} самых дешевых блюд .....")
                for i, row in enumerate(results, 1):
                    print(f"{i}. {row[0]} — {row[1]:.2f} руб. — {row[2]}")
            else:
                print("..... Блюда не найдены .....")

    except:
        print("Ошибка при вводе числа")


def show_categories_with_count(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.name, COUNT(d.id) as dish_count
            FROM category c
            LEFT JOIN dish d ON c.id = d.category_id
            GROUP BY c.id, c.name
            ORDER BY c.name
        """)
        results = cur.fetchall()

        if results:
            print("\n..... Категории и количества блюд .....")
            for row in results:
                print(f"{row[0]} — {row[1]} блюд")
        else:
            print("..... Категории не найдены .....")


def display_menu():
    print("\n")
    print(" МЕНЮ")
    print("1. Показать всё меню")
    print("2. Показать блюда в ценовом диапазоне")
    print("3. Поиск по началу названия (префикс)")
    print("4. Показать N самых дешёвых блюд")
    print("5. Категории и количество блюд")
    print("6. Выход")


def main():
    try:
        with psycopg2.connect(
                dbname="python_course_db",
                user="postgres",
                password="25082003",
                host="localhost",
                port="5432"
        ) as conn:
            print("Подключение к БД прошло успешно")

            # Создание таблиц и заполнение начальными данными
            with conn.cursor() as cur:
                create_category_table(cur, insert=True)
                create_dish_table(cur, insert=True)
                conn.commit()
                print("База данных инициализирована успешно")

            # Главный цикл меню
            while True:
                display_menu()
                try:
                    choice = input("\nВыберите пункт меню (1-6): ").strip()

                    if choice == '1':
                        show_all_menu(conn)
                    elif choice == '2':
                        show_dishes_by_price_range(conn)
                    elif choice == '3':
                        search_by_prefix(conn)
                    elif choice == '4':
                        show_cheapest_dishes(conn)
                    elif choice == '5':
                        show_categories_with_count(conn)
                    elif choice == '6':
                        print("Выход!")
                        break
                    else:
                        print("Ошибка: выберите пункт от 1 до 6")
                        continue

                    input("\nНажмите Enter для продолжения...")

                except KeyboardInterrupt:
                    print("\n\nПрограмма прервана пользователем")
                    break
                except EOFError:
                    print("\n\nВвод завершен")
                    break

    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    main()