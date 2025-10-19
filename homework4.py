import psycopg2
from psycopg2 import sql
import sys

def create_database():
    """Создание базы данных если она не существует"""
    try:
        # Подключаемся к базе данных postgres по умолчанию
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",  
            host="localhost",
            port="5432"
        )
        conn.autocommit = True  
        
        with conn.cursor() as cur:
            # Проверяем существование базы данных
            cur.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = 'python_course_db';")
            exists = cur.fetchone()
            
            if not exists:
                print("Создаем базу данных 'python_course_db'...")
                cur.execute(sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier('python_course_db')
                ))
                print("База данных успешно создана!")
            else:
                print("База данных 'python_course_db' уже существует.")
                
        conn.close()
        
    except psycopg2.Error as e:
        print(f"Ошибка при создании базы данных: {e}")
        sys.exit(1)


def create_tables(cur):
    """Создание таблиц категорий и блюд"""
    # Таблица категорий
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );
    """)
    
    # Таблица блюд
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dish (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            title TEXT NOT NULL,
            price NUMERIC(8,2) CHECK (price > 0),
            category_id INT REFERENCES category(id) ON DELETE SET NULL
        );
    """)

def insert_initial_data(cur):
    """Заполнение начальными данными"""
    # Вставка категорий
    categories = ['Супы', 'Салаты', 'Горячее', 'Десерты', 'Напитки']
    for category_name in categories:
        cur.execute(
            "INSERT INTO category (name) VALUES (%s) ON CONFLICT (name) DO NOTHING;",
            (category_name,)
        )
    
    # Вставка блюд
    dishes = [
        ('Борщ', 350.00, 1),
        ('Оливье', 280.00, 2),
        ('Стейк', 850.00, 3),
        ('Тирамису', 320.00, 4),
        ('Кофе', 150.00, 5),
        ('Щи', 300.00, 1),
        ('Цезарь', 320.00, 2),
        ('Плов', 450.00, 3),
        ('Чизкейк', 280.00, 4),
        ('Чай', 100.00, 5)
    ]
    
    for dish in dishes:
        cur.execute(
            "INSERT INTO dish (title, price, category_id) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
            dish
        )

def show_all_menu(conn):
    """Показать всё меню"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.title, d.price, c.name 
            FROM dish d 
            LEFT JOIN category c ON d.category_id = c.id 
            ORDER BY c.name, d.title;
        """)
        dishes = cur.fetchall()
        
        print("\n=== ВСЁ МЕНЮ ===")
        for dish in dishes:
            print(f"{dish[0]} - {dish[1]} руб. - {dish[2]}")
        print()

def show_dishes_in_price_range(conn):
    """Показать блюда в ценовом диапазоне"""
    try:
        min_price = float(input("Введите минимальную цену: "))
        max_price = float(input("Введите максимальную цену: "))
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.title, d.price, c.name 
                FROM dish d 
                LEFT JOIN category c ON d.category_id = c.id 
                WHERE d.price BETWEEN %s AND %s 
                ORDER BY d.price;
            """, (min_price, max_price))
            dishes = cur.fetchall()
            
            print(f"\n=== БЛЮДА В ДИАПАЗОНЕ {min_price}-{max_price} руб. ===")
            for dish in dishes:
                print(f"{dish[0]} - {dish[1]} руб. - {dish[2]}")
            print()
            
    except ValueError:
        print("Ошибка: введите корректные числовые значения!")

def search_dishes_by_prefix(conn):
    """Поиск по началу названия"""
    prefix = input("Введите начало названия блюда: ").strip()
    
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.title, d.price, c.name 
            FROM dish d 
            LEFT JOIN category c ON d.category_id = c.id 
            WHERE d.title ILIKE %s 
            ORDER BY d.title;
        """, (prefix + '%',))
        dishes = cur.fetchall()
        
        print(f"\n=== РЕЗУЛЬТАТЫ ПОИСКА '{prefix}' ===")
        for dish in dishes:
            print(f"{dish[0]} - {dish[1]} руб. - {dish[2]}")
        print()

def show_cheapest_dishes(conn):
    """Показать N самых дешёвых блюд"""
    try:
        n = int(input("Введите количество блюд (N): "))
        
        with conn.cursor() as cur:
            cur.execute("""
                SELECT d.title, d.price, c.name 
                FROM dish d 
                LEFT JOIN category c ON d.category_id = c.id 
                ORDER BY d.price 
                LIMIT %s;
            """, (n,))
            dishes = cur.fetchall()
            
            print(f"\n=== {n} САМЫХ ДЕШЁВЫХ БЛЮД ===")
            for dish in dishes:
                print(f"{dish[0]} - {dish[1]} руб. - {dish[2]}")
            print()
            
    except ValueError:
        print("Ошибка: введите целое число!")

def show_categories_with_dish_count(conn):
    """Показать категории и количество блюд"""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.name, COUNT(d.id) as dish_count 
            FROM category c 
            LEFT JOIN dish d ON c.id = d.category_id 
            GROUP BY c.id, c.name 
            ORDER BY c.name;
        """)
        categories = cur.fetchall()
        
        print("\n=== КАТЕГОРИИ И КОЛИЧЕСТВО БЛЮД ===")
        for category in categories:
            print(f"{category[0]} - {category[1]} блюд")
        print()

def main():
    """Главная функция с меню"""
    
    create_database()
    
    try:
        with psycopg2.connect(
            dbname="python_course_db",
            user="postgres",
            password="postgres",  
            host="localhost",
            port="5432"
        ) as conn:
            print("Успешное подключение к базе данных!")
            
            # Создание таблиц и заполнение начальными данными
            with conn.cursor() as cur:
                create_tables(cur)
                insert_initial_data(cur)
                conn.commit()
            
            # Главное меню
            while True:
                print("=" * 50)
                print("МЕНЮ РЕСТОРАНА")
                print("1. Показать всё меню")
                print("2. Показать блюда в ценовом диапазоне")
                print("3. Поиск по началу названия")
                print("4. Показать N самых дешёвых блюд")
                print("5. Категории и количество блюд")
                print("6. Выход")
                print("=" * 50)
                
                choice = input("Выберите пункт меню (1-6): ").strip()
                
                if choice == '1':
                    show_all_menu(conn)
                elif choice == '2':
                    show_dishes_in_price_range(conn)
                elif choice == '3':
                    search_dishes_by_prefix(conn)
                elif choice == '4':
                    show_cheapest_dishes(conn)
                elif choice == '5':
                    show_categories_with_dish_count(conn)
                elif choice == '6':
                    print("Выход из программы. До свидания!")
                    break
                else:
                    print("Неверный выбор! Попробуйте снова.\n")
                    
    except psycopg2.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
    except Exception as e:
        print(f"Произошла ошибка: {e}")

if __name__ == "__main__":
    main()
