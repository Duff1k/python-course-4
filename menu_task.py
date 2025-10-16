import psycopg2
import sys

DB_PARAMS = {
    "host": "localhost",
    "database": "menu_db",
    "user": "postgres",
    "password": "7243"
}

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS category (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dish (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    title TEXT NOT NULL,
    price NUMERIC(8,2) NOT NULL CHECK (price > 0),
    category_id INT,
    CONSTRAINT fk_category
        FOREIGN KEY(category_id)
        REFERENCES category(id)
        ON DELETE RESTRICT
);
"""

INITIAL_CATEGORIES = [
    ('Супы',),
    ('Салаты',),
    ('Горячее',),
    ('Десерты',),
    ('Напитки',)
]

INITIAL_DISHES = [
    ('Борщ', 350.00, 1),
    ('Солянка', 400.50, 1),
    ('Салат "Цезарь"', 450.00, 2),
    ('Салат "Греческий"', 380.00, 2),
    ('Стейк из говядины', 1200.00, 3),
    ('Паста "Карбонара"', 550.75, 3),
    ('Плов с бараниной', 650.00, 3),
    ('Чизкейк "Нью-Йорк"', 300.00, 4),
    ('Тирамису', 320.50, 4),
    ('Морс клюквенный', 150.00, 5),
    ('Кофе "Американо"', 180.00, 5),
]


def setup_database(conn):
    try:
        with conn.cursor() as cur:
            print("Создание таблиц...")
            cur.execute(CREATE_TABLES_SQL)

            cur.execute("SELECT COUNT(*) FROM category;")
            if cur.fetchone()[0] == 0:
                print("Заполнение таблиц начальными данными...")
                cur.executemany("INSERT INTO category (name) VALUES (%s);", INITIAL_CATEGORIES)

                cur.executemany("INSERT INTO dish (title, price, category_id) VALUES (%s, %s, %s);", INITIAL_DISHES)
                print("Данные успешно загружены.")
            else:
                print("База данных уже заполнена.")

            conn.commit()
    except psycopg2.Error as e:
        print(f"Ошибка при настройке базы данных: {e}")
        conn.rollback()
        sys.exit(1)


def show_all_menu(conn):
    print("\n--- Полное меню ---")
    sql = """
        SELECT d.title, d.price, c.name
        FROM dish d
        JOIN category c ON d.category_id = c.id
        ORDER BY c.name, d.title;
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        results = cur.fetchall()
        if not results:
            print("Меню пусто.")
            return

        print(f"{'Блюдо':<30} | {'Цена':>10} | {'Категория':<20}")
        print("-" * 65)
        for row in results:
            title, price, category_name = row
            print(f"{title:<30} | {price:>10.2f} | {category_name:<20}")


def show_dishes_in_price_range(conn):
    print("\n--- Поиск блюд по цене ---")
    try:
        min_price = float(input("Введите минимальную цену: "))
        max_price = float(input("Введите максимальную цену: "))
        if min_price > max_price:
            print("Ошибка: минимальная цена не может быть больше максимальной.")
            return
    except ValueError:
        print("Ошибка: пожалуйста, введите корректные числа.")
        return

    sql = """
        SELECT title, price
        FROM dish
        WHERE price BETWEEN %s AND %s
        ORDER BY price;
    """
    with conn.cursor() as cur:
        cur.execute(sql, (min_price, max_price))
        results = cur.fetchall()
        if not results:
            print(f"Блюда в диапазоне от {min_price:.2f} до {max_price:.2f} не найдены.")
            return

        print(f"\nНайденные блюда (от {min_price:.2f} до {max_price:.2f}):")
        print(f"{'Блюдо':<30} | {'Цена':>10}")
        print("-" * 45)
        for row in results:
            title, price = row
            print(f"{title:<30} | {price:>10.2f}")


def search_by_prefix(conn):
    print("\n--- Поиск по названию ---")
    prefix = input("Введите начало названия блюда: ")
    if not prefix:
        print("Вы ничего не ввели.")
        return

    sql = """
        SELECT d.title, d.price, c.name
        FROM dish d
        JOIN category c ON d.category_id = c.id
        WHERE d.title ILIKE %s
        ORDER BY d.title;
    """
    with conn.cursor() as cur:
        cur.execute(sql, (f"{prefix}%",))
        results = cur.fetchall()
        if not results:
            print(f"Блюда, начинающиеся на '{prefix}', не найдены.")
            return

        print(f"\nНайденные блюда (начинаются на '{prefix}'):")
        print(f"{'Блюдо':<30} | {'Цена':>10} | {'Категория':<20}")
        print("-" * 65)
        for row in results:
            title, price, category_name = row
            print(f"{title:<30} | {price:>10.2f} | {category_name:<20}")


def show_n_cheapest(conn):
    print("\n--- N самых дешёвых блюд ---")
    try:
        n = int(input("Сколько самых дешёвых блюд показать? Введите число: "))
        if n <= 0:
            print("Число должно быть положительным.")
            return
    except ValueError:
        print("Ошибка: пожалуйста, введите целое число.")
        return

    sql = """
        SELECT title, price
        FROM dish
        ORDER BY price ASC
        LIMIT %s;
    """
    with conn.cursor() as cur:
        cur.execute(sql, (n,))
        results = cur.fetchall()
        if not results:
            print("В меню нет блюд.")
            return

        print(f"\n{n} самых дешёвых блюд:")
        print(f"{'Блюдо':<30} | {'Цена':>10}")
        print("-" * 45)
        for row in results:
            title, price = row
            print(f"{title:<30} | {price:>10.2f}")


def show_category_counts(conn):
    print("\n--- Категории и количество блюд ---")
    sql = """
        SELECT c.name, COUNT(d.id)
        FROM category c
        LEFT JOIN dish d ON c.id = d.category_id
        GROUP BY c.name
        ORDER BY c.name;
    """
    with conn.cursor() as cur:
        cur.execute(sql)
        results = cur.fetchall()

        print(f"{'Категория':<20} | {'Количество блюд'}")
        print("-" * 40)
        for row in results:
            category_name, count = row
            print(f"{category_name:<20} | {count}")


def main():
    conn = None
    try:
        conn = psycopg2.connect(**DB_PARAMS)

        setup_database(conn)

        while True:
            print("\n" + "=" * 30)
            print("    Консольное меню ресторана")
            print("=" * 30)
            print("1. Показать всё меню")
            print("2. Показать блюда в ценовом диапазоне")
            print("3. Поиск по началу названия")
            print("4. Показать N самых дешёвых блюд")
            print("5. Категории и количество блюд")
            print("6. Выход")
            print("-" * 30)

            choice = input("Выберите пункт меню: ")

            if choice == '1':
                show_all_menu(conn)
            elif choice == '2':
                show_dishes_in_price_range(conn)
            elif choice == '3':
                search_by_prefix(conn)
            elif choice == '4':
                show_n_cheapest(conn)
            elif choice == '5':
                show_category_counts(conn)
            elif choice == '6':
                break
            else:
                print("Неверный ввод. Пожалуйста, выберите пункт от 1 до 6.")

    except psycopg2.OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
    finally:
        if conn:
            conn.close()
            print("Соединение с базой данных закрыто.")


if __name__ == "__main__":
    main()