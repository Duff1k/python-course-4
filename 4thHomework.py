import psycopg2

DB_CONFIG = {
    'dbname': 'your_db_name',
    'user': 'your_user',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
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
            price NUMERIC(8,2) CHECK (price > 0),
            category_id INT REFERENCES category(id) ON DELETE SET NULL
        );
    """)


def insert_initial_data(cur):
    cur.execute("""
        INSERT INTO category (name)
        VALUES ('Супы'), ('Салаты'), ('Горячее'), ('Десерты'), ('Напитки')
        ON CONFLICT (name) DO NOTHING;
    """)

    cur.execute("""
        INSERT INTO dish (title, price, category_id) VALUES
        ('Борщ', 260, 1), ('Солянка', 230, 1), ('Окрошка', 230, 1),
        ('Винегрет', 110, 2), ('Оливье', 130, 2), ('Цезарь', 180, 2),
        ('Греческий салат', 125, 2), ('Утиная грудка', 350, 3),
        ('Котлета по-киевски', 145, 3), ('Карбонара', 310, 3),
        ('Медовик', 85, 4), ('Штрудель', 115, 4), ('Крем-брюле', 105, 4),
        ('Канноли', 135, 4), ('Липтон', 85, 5), ('Добрый кола', 70, 5),
        ('Кофе', 70, 5), ('Чай черный', 25, 5), ('Чай зеленый', 25, 5)
        ON CONFLICT DO NOTHING;
    """)


def print_menu():
    print("1. Показать всё меню")
    print("2. Показать блюда в ценовом диапазоне")
    print("3. Поиск по началу названия")
    print("4. Показать N самых дешёвых блюд")
    print("5. Категории и количество блюд")
    print("6. Выход")


def show_all_menu(cur):
    cur.execute("""
        SELECT d.title, d.price, c.name
        FROM dish d
        JOIN category c ON d.category_id = c.id
        ORDER BY d.title;
    """)
    print("Блюдо — Цена — Категория")
    for title, price, category in cur.fetchall():
        print(f"{title} — {price} — {category}")


def show_dishes_by_price(cur):
    min_price = input("Минимальная цена: ")
    max_price = input("Максимальная цена: ")
    cur.execute("""
        SELECT d.title, d.price, c.name
        FROM dish d
        JOIN category c ON d.category_id = c.id
        WHERE d.price BETWEEN %s AND %s
        ORDER BY d.price;
    """, (min_price, max_price))
    for title, price, category in cur.fetchall():
        print(f"{title} — {price} — {category}")


def search_dishes_by_prefix(cur):
    prefix = input("Начало названия блюда: ")
    cur.execute("""
        SELECT d.title, d.price, c.name
        FROM dish d
        JOIN category c ON d.category_id = c.id
        WHERE LOWER(d.title) LIKE LOWER(%s)
        ORDER BY d.title;
    """, (prefix + '%',))
    for title, price, category in cur.fetchall():
        print(f"{title} — {price} — {category}")


def show_n_cheapest_dishes(cur):
    n = input("Введите количество блюд: ")
    cur.execute("""
        SELECT d.title, d.price, c.name
        FROM dish d
        JOIN category c ON d.category_id = c.id
        ORDER BY d.price ASC
        LIMIT %s;
    """, (n,))
    for title, price, category in cur.fetchall():
        print(f"{title} — {price} — {category}")


def show_categories_and_counts(cur):
    cur.execute("""
        SELECT c.name, COUNT(d.id)
        FROM category c
        LEFT JOIN dish d ON d.category_id = c.id
        GROUP BY c.id, c.name
        ORDER BY c.id;
    """)
    print("Категория — Количество блюд")
    for category, count in cur.fetchall():
        print(f"{category} — {count}")


def main():
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            create_tables(cur)
            insert_initial_data(cur)
            conn.commit()
            while True:
                print_menu()
                choice = input("Выберите пункт меню: ")
                if choice == '1':
                    show_all_menu(cur)
                elif choice == '2':
                    show_dishes_by_price(cur)
                elif choice == '3':
                    search_dishes_by_prefix(cur)
                elif choice == '4':
                    show_n_cheapest_dishes(cur)
                elif choice == '5':
                    show_categories_and_counts(cur)
                elif choice == '6':
                    print("До свидания!")
                    break
                else:
                    print("Некорректный пункт.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Ошибка при подключении или выполнении:", e)