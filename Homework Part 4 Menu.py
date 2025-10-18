import psycopg2

def get_connection():
    return psycopg2.connect(
        dbname="restaurant_menu",
        user="postgres",
        password="хххх",
        host="localhost",
        port="5432"
    )


def init_database():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS category (
                        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        name TEXT NOT NULL UNIQUE
                    )
                ''')

                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS dish (
                        id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                        title TEXT NOT NULL,
                        price NUMERIC(8,2) CHECK (price > 0),
                        category_id INT,
                        FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL
                    )
                ''')

                categories = [
                    ('Супы',),
                    ('Салаты',),
                    ('Горячее',),
                    ('Десерты',),
                    ('Напитки',)
                ]

                insert_category_query = '''
                    INSERT INTO category (name) 
                    VALUES (%s)
                    ON CONFLICT (name) DO NOTHING
                '''
                cursor.executemany(insert_category_query, categories)

                dishes = [
                    ('Борщ', 200.00, 1),
                    ('Уха', 150.00, 1),
                    ('Греческий', 300.00, 2),
                    ('Оливье', 350.00, 2),
                    ('Стейк', 600.00, 3),
                    ('Филе семги', 700.00, 3),
                    ('Чизкейк', 250.00, 4),
                    ('Блинчики', 280.00, 4),
                    ('Чай', 100.00, 5),
                    ('Кофе', 150.00, 5),
                ]

                insert_dish_query = '''
                    INSERT INTO dish (title, price, category_id) 
                    VALUES (%s, %s, %s)
                    ON CONFLICT DO NOTHING
                '''
                cursor.executemany(insert_dish_query, dishes)

        print("✅ База данных инициализирована")

    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")
        return False
    return True


def show_all_menu():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT d.title, d.price, c.name 
                    FROM dish d 
                    LEFT JOIN category c ON d.category_id = c.id 
                ''')

                dishes = cursor.fetchall()

                print("\n" + "=" * 50)
                print("ВСЁ МЕНЮ РЕСТОРАНА")
                print("=" * 50)
                print(f"{'Блюдо':<20} {'Цена':<10} {'Категория':<10}")
                print("-" * 45)

                if dishes:
                    for dish in dishes:
                        print(f"{dish[0]:<20} {dish[1]:<10.2f} {dish[2]:<10}")
                else:
                    print("Меню пустое")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def show_dishes_in_price_range():
    try:
        min_price = float(input("Введите минимальную цену: "))
        max_price = float(input("Введите максимальную цену: "))

        if min_price > max_price:
            print("❌ Минимальная цена не может быть больше максимальной!")
            return

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT d.title, d.price, c.name 
                    FROM dish d 
                    LEFT JOIN category c ON d.category_id = c.id 
                    WHERE d.price BETWEEN %s AND %s
                    ORDER BY d.price
                ''', (min_price, max_price))

                dishes = cursor.fetchall()

                print(f"\n" + "=" * 50)
                print(f"БЛЮДА В ДИАПАЗОНЕ {min_price}-{max_price} РУБ.")
                print("=" * 50)

                if dishes:
                    for dish in dishes:
                        print(f"{dish[0]} — {dish[1]} руб. — {dish[2]}")
                else:
                    print("Блюд в указанном диапазоне не найдено")

    except ValueError:
        print("❌ Ошибка: введите корректные числовые значения!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def search_by_prefix():
    prefix = input("Введите начало названия блюда: ").strip()

    if not prefix:
        print("❌ Ошибка: введите текст для поиска")
        return

    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT d.title, d.price, c.name 
                    FROM dish d 
                    LEFT JOIN category c ON d.category_id = c.id 
                    WHERE d.title ILIKE %s
                    ORDER BY d.title
                ''', (f'{prefix}%',))

                dishes = cursor.fetchall()

                print(f"\n" + "=" * 50)
                print(f"РЕЗУЛЬТАТЫ ПОИСКА ПО '{prefix.upper()}'")
                print("=" * 50)

                if dishes:
                    for dish in dishes:
                        print(f"{dish[0]} — {dish[1]} руб. — {dish[2]}")
                else:
                    print("Блюд с таким началом названия не найдено")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def show_cheapest_dishes():
    try:
        n = int(input("Введите количество блюд (N): "))

        if n <= 0:
            print("❌ Ошибка: введите положительное число!")
            return

        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT d.title, d.price, c.name 
                    FROM dish d 
                    LEFT JOIN category c ON d.category_id = c.id 
                    ORDER BY d.price 
                    LIMIT %s
                ''', (n,))

                dishes = cursor.fetchall()

                print(f"\n" + "=" * 50)
                print(f"{n} САМЫХ ДЕШЁВЫХ БЛЮД")
                print("=" * 50)

                if dishes:
                    for i, dish in enumerate(dishes, 1):
                        print(f"{i}. {dish[0]} — {dish[1]} руб. — {dish[2]}")
                else:
                    print("В меню нет блюд")

    except ValueError:
        print("❌ Ошибка: введите целое число!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def show_categories_with_count():
    try:
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute('''
                    SELECT c.name, COUNT(d.id) 
                    FROM category c 
                    LEFT JOIN dish d ON c.id = d.category_id 
                    GROUP BY c.id, c.name 
                    ORDER BY c.name
                ''')

                categories = cursor.fetchall()

                print("\n" + "=" * 40)
                print("КАТЕГОРИИ И КОЛИЧЕСТВО БЛЮД")
                print("=" * 40)
                print(f"{'Категория':<15} {'Количество':<12}")
                print("-" * 30)

                for category in categories:
                    print(f"{category[0]:<15} {category[1]:<12}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")


def main():
    if not init_database():
        return

    while True:
        print("\n" + "=" * 50)
        print("МЕНЮ РЕСТОРАНА")
        print("=" * 50)
        print("1. Показать всё меню")
        print("2. Показать блюда в ценовом диапазоне")
        print("3. Поиск по началу названия (префикс)")
        print("4. Показать N самых дешёвых блюд")
        print("5. Категории и количество блюд")
        print("6. Выход")
        print("-" * 50)

        choice = input("Выберите пункт меню (1-6): ").strip()

        if choice == '1':
            show_all_menu()
        elif choice == '2':
            show_dishes_in_price_range()
        elif choice == '3':
            search_by_prefix()
        elif choice == '4':
            show_cheapest_dishes()
        elif choice == '5':
            show_categories_with_count()
        elif choice == '6':
            print("Вы вышли из меню ресторана.")
            break
        else:
            print("❌ Ошибка! Введите цифру от 1 до 6.")


if __name__ == "__main__":
    main()