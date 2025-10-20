try:
    import psycopg
    connect = psycopg.connect
except ImportError:
    import psycopg2 as psycopg
    connect = psycopg.connect #моя версия питона 3.13.3 не поддерживает psycopg2

DB_PARAMS = {
    "dbname": "menu",
    "user": "postgres",
    "password": "your_password",  
    "host": "localhost",
    "port": "5432"
}


def create_tables(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dish (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            price NUMERIC(8,2) CHECK(price > 0),
            category_id INT REFERENCES category(id) ON DELETE SET NULL
        );
    """)

def insert_initial_data(cur):
    cur.execute("""
        INSERT INTO category (name)
        VALUES
            ('Супы'),
            ('Салаты'),
            ('Горячие блюда'),
            ('Десерты'),
            ('Напитки')
        ON CONFLICT (name) DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO dish (title, price, category_id)
        VALUES
            ('Крем-суп из тыквы', 340, 1),
            ('Суп Том Ям', 420, 1),
            ('Борщ с говядиной', 360, 1),
            ('Салат с тунцом', 480, 2),
            ('Салат с креветками', 520, 2),
            ('Фетуччине с грибами', 690, 3),
            ('Стейк из лосося', 890, 3),
            ('Куриное филе в сливочном соусе', 740, 3),
            ('Шоколадный фондан', 390, 4),
            ('Медовик домашний', 370, 4),
            ('Чизкейк ягодный', 410, 4),
            ('Эспрессо', 190, 5),
            ('Лимонад мятный', 260, 5),
            ('Чай жасминовый', 220, 5),
            ('Молочный коктейль ванильный', 310, 5)
        ON CONFLICT DO NOTHING;
    """)

def get_all_menu(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.title, d.price, c.name
            FROM dish d
            JOIN category c ON d.category_id = c.id
            ORDER BY c.name, d.price;
        """)
        return cur.fetchall()

def get_dishes_in_price_range(conn, min_price, max_price):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.title, d.price, c.name
            FROM dish d
            JOIN category c ON d.category_id = c.id
            WHERE d.price BETWEEN %s AND %s
            ORDER BY d.price;
        """, (min_price, max_price))
        return cur.fetchall()

def search_by_prefix(conn, prefix):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.title, d.price, c.name
            FROM dish d
            JOIN category c ON d.category_id = c.id
            WHERE d.title ILIKE %s
            ORDER BY d.title;
        """, (prefix + "%",))
        return cur.fetchall()

def get_n_cheapest(conn, n):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.title, d.price, c.name
            FROM dish d
            JOIN category c ON d.category_id = c.id
            ORDER BY d.price
            LIMIT %s;
        """, (n,))
        return cur.fetchall()

def get_category_counts(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.name, COUNT(d.id)
            FROM category c
            LEFT JOIN dish d ON d.category_id = c.id
            GROUP BY c.id
            ORDER BY c.name;
        """)
        return cur.fetchall()


def run_menu(conn):
    while True:
        print("""
==============================
Меню ресторана
1. Показать всё меню
2. Показать блюда в ценовом диапазоне
3. Поиск по началу названия блюда
4. Показать N самых дешёвых блюд
5. Категории и количество блюд
0. Выход
==============================
""")
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            for title, price, category in get_all_menu(conn):
                print(f"{title:<35} {price:>7.2f} руб. — {category}")

        elif choice == "2":
            try:
                min_p = float(input("Минимальная цена: "))
                max_p = float(input("Максимальная цена: "))
            except ValueError:
                print("Ошибка: введите число.")
                continue
            for title, price, category in get_dishes_in_price_range(conn, min_p, max_p):
                print(f"{title:<35} {price:>7.2f} руб. — {category}")

        elif choice == "3":
            prefix = input("Введите начало названия: ").strip()
            for title, price, category in search_by_prefix(conn, prefix):
                print(f"{title:<35} {price:>7.2f} руб. — {category}")

        elif choice == "4":
            try:
                n = int(input("Сколько дешёвых блюд показать: "))
            except ValueError:
                print("Ошибка: нужно число.")
                continue
            for title, price, category in get_n_cheapest(conn, n):
                print(f"{title:<35} {price:>7.2f} руб. — {category}")

        elif choice == "5":
            for category, count in get_category_counts(conn):
                print(f"{category:<25} — {count} блюд")

        elif choice == "0":
            print("Выход из программы. До встречи!")
            break
        else:
            print("Неверный выбор, попробуйте снова.")


if __name__ == "__main__":
    try:
        with psycopg.connect(**DB_PARAMS) as conn:
            print("Подключение успешно!")
            with conn.cursor() as cur:
                create_tables(cur)
                insert_initial_data(cur)
            conn.commit()
            run_menu(conn)
    except Exception as e:
        print("Ошибка", e)

