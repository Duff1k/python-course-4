import psycopg2


def get_connection():
    return psycopg2.connect(dbname="db_name", host="localhost", user="db_user", password="db_pass", port="1080")

def create_schema():
    commands = [
        """
        CREATE TABLE IF NOT EXISTS category (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS dish (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            price NUMERIC(8,2) CHECK (price > 0),
            category_id INT REFERENCES category(id) ON DELETE SET NULL
        );
        """
    ]
    with get_connection() as conn, conn.cursor() as cur:
        for cmd in commands:
            cur.execute(cmd)

INITIAL_CATEGORIES = ['Супы', 'Салаты', 'Горячее', 'Десерты', 'Напитки']

def load_initial_data():
    with get_connection() as conn, conn.cursor() as cur:
        for name in INITIAL_CATEGORIES:
            cur.execute(
                "INSERT INTO category(name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
                (name,)
            )

def execute_and_print(query, params=None):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(query, params or ())
        rows = cur.fetchall()
        if rows:
            for row in rows:
                print(" — ".join(str(x) for x in row))
        else:
            print("Нет данных.")
    input("\nНажмите Enter для продолжения...")

def show_all_menu():
    query = """
    SELECT d.title, d.price, c.name
    FROM dish d
    LEFT JOIN category c ON d.category_id = c.id
    ORDER BY d.id;
    """
    execute_and_print(query)

def show_by_price_range():
    min_p = input("Мин. цена: ").strip()
    max_p = input("Макс. цена: ").strip()
    query = """
    SELECT title, price FROM dish
    WHERE price BETWEEN %s AND %s
    ORDER BY price;
    """
    execute_and_print(query, (min_p, max_p))

def search_by_prefix():
    prefix = input("Начало названия: ").strip()
    like_pattern = prefix + '%'
    query = """
    SELECT title, price FROM dish
    WHERE LOWER(title) LIKE LOWER(%s)
    ORDER BY title;
    """
    execute_and_print(query, (like_pattern,))

def show_cheapest_n():
    n = int(input("Введите N: ").strip())
    query = """
    SELECT title, price FROM dish
    ORDER BY price
    LIMIT %s;
    """
    execute_and_print(query, (n,))

def show_category_counts():
    query = """
    SELECT c.name, COUNT(d.id) AS dish_count
    FROM category c
    LEFT JOIN dish d ON d.category_id = c.id
    GROUP BY c.name
    ORDER BY c.name;
    """
    execute_and_print(query)

def main_menu():
    menu = """
    Выберите действие:
    1. Показать всё меню
    2. Показать блюда в ценовом диапазоне
    3. Поиск по началу названия
    4. Показать N самых дешёвых блюд
    5. Категории и количество блюд
    0. Выход
    """
    actions = {
        '1': show_all_menu,
        '2': show_by_price_range,
        '3': search_by_prefix,
        '4': show_cheapest_n,
        '5': show_category_counts
    }
    while True:
        choice = input(menu).strip()
        if choice == '0':
            print("Выход...")
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Неверный выбор, попробуйте снова.")

if __name__ == '__main__':
    create_schema()
    load_initial_data()
    main_menu()