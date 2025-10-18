import psycopg2

def create_tables(cur):
    """Создание таблиц в базе данных"""
    # Создание таблицы категорий
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
    """)

    # Создание таблицы блюд с проверкой цены > 0
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dish (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            title TEXT NOT NULL,
            price NUMERIC(8,2) CHECK (price > 0),
            category_id INT REFERENCES category(id) ON DELETE SET NULL
        );
    """)


def insert_categories(cur):
    """Заполнение таблицы с категориями"""
    cur.execute("""
        INSERT INTO category (name) 
        VALUES ('Супы'),
               ('Салаты'),
               ('Горячее'),
               ('Десерты'),
               ('Напитки')
        ON CONFLICT (name) DO NOTHING;
    """)
    print("Категории заполнены")


def insert_dishes(cur):
    """Заполнение таблицы блюд"""
    cur.execute("""
        INSERT INTO dish (title, price, category_id)
        VALUES  ('Борщ', 250.00, 1),
                ('Солянка', 280.00, 1),
                ('Цезарь', 320.00, 2),
                ('Греческий', 290.00, 2),
                ('Стейк', 650.00, 3),
                ('Курица гриль', 450.00, 3),
                ('Тирамису', 350.00, 4),
                ('Чизкейк', 320.00, 4),
                ('Кофе', 150.00, 5),
                ('Сок', 120.00, 5),
                ('Куриный суп', 220.00, 1),
                ('Оливье', 270.00, 2),
                ('Плов', 480.00, 3),
                ('Мороженое', 180.00, 4),
                ('Чай', 100.00, 5)
        ON CONFLICT DO NOTHING;
    """)
    print("Блюда заполнены")


def get_all_dishes(conn):
    """Запрос всех блюд"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                d.title AS "Блюдо",
                d.price AS "Цена",
                c.name AS "Категория"
            FROM dish d
            JOIN category c ON d.category_id = c.id
            ORDER BY c.name, d.title;
        """)
        dishes_all = cur.fetchall()

        print("\n" + "=" * 40)
        print("ВСЕ БЛЮДА В МЕНЮ")
        print("=" * 40)
        for dish_title, dish_price, dish_category in dishes_all:
            print(f"{dish_title} — {dish_price} руб. — {dish_category}")
        print(f"Всего блюд: {len(dishes_all)}")

        return dishes_all


def get_dishes_by_price(conn):
    """Запрос блюд по диапазону цен"""
    try:
        min_price = float(input("Введите минимальную цену: "))
        max_price = float(input("Введите максимальную цену: "))

        if min_price > max_price:
            print("Ошибка: минимальная цена не может быть больше максимальной")
            return

        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    d.title AS "Блюдо",
                    d.price AS "Цена",
                    c.name AS "Категория"
                FROM dish d
                JOIN category c ON d.category_id = c.id
                WHERE d.price BETWEEN %s AND %s
                ORDER BY d.price
            """, (min_price, max_price))
            dishes_by_price = cur.fetchall()

            print(f"\n" + "=" * 40)
            print(f"БЛЮДА В ДИАПАЗОНЕ {min_price}-{max_price} руб.")
            print("=" * 40)

            if dishes_by_price:
                for dish_title, dish_price, dish_category in dishes_by_price:
                    print(f"{dish_title} — {dish_price} руб. — {dish_category}")
                print(f"Найдено блюд: {len(dishes_by_price)}")
            else:
                print("Блюд в указанном диапазоне не найдено")

            return dishes_by_price

    except ValueError:
        print("Ошибка: введите корректные числовые значения для цены")


def get_dishes_by_name(conn):
    """Запрос блюд по названию"""
    dish_name = input("Введите начало названия блюда: ").strip()

    if not dish_name:
        print("Ошибка: введите название для поиска")
        return

    with conn.cursor() as cur:
        cur.execute("""
            SELECT
                d.title AS "Блюдо",
                d.price AS "Цена",
                c.name AS "Категория"
            FROM dish d
            JOIN category c ON d.category_id = c.id
            WHERE LOWER(d.title) LIKE LOWER(%s)  
            ORDER BY d.title
        """, (dish_name + '%',))
        dishes_by_name = cur.fetchall()

        print(f"\n" + "=" * 40)
        print(f"РЕЗУЛЬТАТЫ ПОИСКА ПО '{dish_name}'")
        print("=" * 40)

        if dishes_by_name:
            for dish_title, dish_price, dish_category in dishes_by_name:
                print(f"{dish_title} — {dish_price} руб. — {dish_category}")
            print(f"Найдено блюд: {len(dishes_by_name)}")
        else:
            print("Блюд с таким названием не найдено")

        return dishes_by_name


def get_cheapest_dishes(conn):
    """Запрос N самых дешевых блюд"""
    try:
        N = int(input("Введите количество блюд (N): "))

        if N <= 0:
            print("Ошибка: количество должно быть положительным числом")
            return

        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    d.title AS "Блюдо",
                    d.price AS "Цена",
                    c.name AS "Категория"
                FROM dish d
                JOIN category c ON d.category_id = c.id
                ORDER BY d.price ASC
                LIMIT %s  
            """, (N,))
            cheapest_dishes = cur.fetchall()

            print(f"\n" + "=" * 40)
            print(f"{N} САМЫХ ДЕШЕВЫХ БЛЮД")
            print("=" * 40)

            for i, (dish_title, dish_price, dish_category) in enumerate(cheapest_dishes, 1):
                print(f"{i}. {dish_title} — {dish_price} руб. — {dish_category}")

            return cheapest_dishes

    except ValueError:
        print("Ошибка: введите целое число")


def get_all_categories(conn):
    """Запрос всех категорий с количеством блюд"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 
                c.name AS "Категория",
                COUNT(d.id) AS "Количество_блюд" 
            FROM category c
            LEFT JOIN dish d ON d.category_id = c.id
            GROUP BY c.id, c.name
            ORDER BY c.id
        """)
        categories_all = cur.fetchall()

        print("\n" + "=" * 40)
        print("КАТЕГОРИИ И КОЛИЧЕСТВО БЛЮД")
        print("=" * 40)

        for category_name, dish_count in categories_all:
            print(f"{category_name} — {dish_count} блюд")

        total_dishes = sum(count for _, count in categories_all)
        print(f"\nВсего категорий: {len(categories_all)}")
        print(f"Всего блюд: {total_dishes}")

        return categories_all


def show_main_menu():
    """Отображение главного меню"""
    print("\n" + "=" * 40)
    print("РЕСТОРАННОЕ МЕНЮ - ГЛАВНОЕ МЕНЮ")
    print("=" * 40)
    print("1. Показать всё меню")
    print("2. Показать блюда в ценовом диапазоне")
    print("3. Поиск по началу названия (префикс)")
    print("4. Показать N самых дешёвых блюд")
    print("5. Категории и количество блюд")
    print("6. Выход")
    print("-" * 40)


def main_menu(conn):
    """Основное меню приложения"""
    while True:
        show_main_menu()

        try:
            choice = input("Выберите пункт меню (1-6): ").strip()

            if choice == "1":
                get_all_dishes(conn)
            elif choice == "2":
                get_dishes_by_price(conn)
            elif choice == "3":
                get_dishes_by_name(conn)
            elif choice == "4":
                get_cheapest_dishes(conn)
            elif choice == "5":
                get_all_categories(conn)
            elif choice == "6":
                print("До свидания!")
                break
            else:
                print("Неверный выбор. Пожалуйста, выберите пункт от 1 до 6.")
                continue

            # Пауза перед следующим действием
            if choice != "6":
                input("\nНажмите Enter для продолжения...")

        except ValueError:
            print("Ошибка: введите число от 1 до 6")
        except KeyboardInterrupt:
            print("\n\nПрограмма прервана пользователем")
            break
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")


def main():
    """Основная функция приложения"""
    try:
        # Подключение к базе данных
        conn = psycopg2.connect(
            dbname="python_course_db",
            user="postgres",
            password="vi888",
            host="localhost",
            port="5432"
        )

        # Автоматическое подтверждение транзакций
        conn.autocommit = True

        print("Успешное подключение к базе данных!")

        # Инициализация базы данных
        with conn.cursor() as cur:
            create_tables(cur)
            insert_categories(cur)
            insert_dishes(cur)

        # Запуск основного меню
        main_menu(conn)

    except psycopg2.OperationalError as e:
        print(f"Ошибка подключения к базе данных: {e}")
        print("Проверьте параметры подключения и убедитесь, что PostgreSQL запущен")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        # Закрытие соединения
        if 'conn' in locals():
            conn.close()
            print("Соединение с базой данных закрыто")


if __name__ == "__main__":
    main()