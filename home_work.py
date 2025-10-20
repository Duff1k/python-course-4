import psycopg2

def insert_category(cur):
    cur.execute("""
                INSERT INTO category (name)
                 VALUES ('Супы'),
                ('Салаты'),
                ('Горячее'),
                ('Десерты'),
                ('Напитки');
                """)
    print("Заполнили категории")


def insert_dish(cur):
    cur.execute("""
                INSERT INTO dish (title, price, category_id)
                VALUES ('Борщ', 120.00, 1),
                ('Солянка', 130.00, 1),
                ('Оливье', 90.00, 2),
                ('Цезарь', 150.00, 2),
                ('Котлета с пюре', 180.00, 3),
                ('Плов', 160.00, 3),
                ('Тирамису', 110.00, 4),
                ('Чизкейк', 120.00, 4),
                ('Чай', 30.00, 5),
                ('Щи', 110.00, 1),
                ('Куриный суп', 100.00, 1),
                ('Грибной суп', 140.00, 1),
                ('Греческий салат', 130.00, 2),
                ('Салат с креветками', 200.00, 2),
                ('Винегрет', 80.00, 2),
                ('Бефстроганов', 220.00, 3),
                ('Курица гриль', 190.00, 3),
                ('Лазанья', 210.00, 3),
                ('Мороженое с шоколадом', 80.00, 4),
                ('Медик с орехами', 100.00, 4),
                ('Фруктовый салат', 90.00, 4),
                ('Сок апельсиновый', 60.00, 5),
                ('Минеральная вода', 40.00, 5),
                ('Лимонад домашний', 70.00, 5),
                ('Кофе', 50.00, 5);

                """)
    print("Заполнили блюда")

def create_category_table(cur, insert: bool = False):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );            
    """)
    if insert:
       insert_category(cur)

def create_dish_table(cur, insert: bool = False):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dish (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            title TEXT NOT NULL,
            price NUMERIC(8, 2) CHECK (price>0),
            category_id INT REFERENCES category(id) ON DELETE SET NULL 
        );
    """)
    if insert:
        insert_dish(cur)

def show_menu(cur):
    cur.execute("""
        SELECT d.title, d.price, c.name
        FROM dish d
        JOIN category c ON d.category_id = c.id
        ORDER BY d.title;
    """)
    rows = cur.fetchall()
    print("\nМеню:")
    for row in rows:
        print(f"{row[0]} — {row[1]} — {row[2]}")

def show_price_range(cur):
    min_price = float(input("Введите минимальную цену: "))
    max_price = float(input("Введите максимальную цену: "))
    cur.execute("""
        SELECT d.title, d.price, c.name
        FROM dish d
        JOIN category c ON d.category_id = c.id
        WHERE d.price BETWEEN %s AND %s
        ORDER BY d.price;
    """, (min_price, max_price))
    rows = cur.fetchall()
    print(f"\nБлюда в ценовом диапазоне от {min_price} до {max_price}:")
    for row in rows:
        print(f"{row[0]} — {row[1]} — {row[2]}")

def search_by_prefix(cur):
    prefix = input("Введите начало названия блюда: ").lower()
    cur.execute("""
        SELECT d.title, d.price, c.name
        FROM dish d
        JOIN category c ON d.category_id = c.id
        WHERE LOWER(d.title) LIKE %s
        ORDER BY d.title;
    """, (f"{prefix}%",))
    rows = cur.fetchall()
    print(f"\nБлюда, начинающиеся на '{prefix}':")
    for row in rows:
        print(f"{row[0]} — {row[1]} — {row[2]}")

def show_cheapest_dishes(cur):
    n = int(input("Введите количество самых дешёвых блюд: "))
    cur.execute("""
        SELECT d.title, d.price, c.name
        FROM dish d
        JOIN category c ON d.category_id = c.id
        ORDER BY d.price ASC
        LIMIT %s;
    """, (n,))
    rows = cur.fetchall()
    print(f"\n{n} самых дешёвых блюд:")
    for row in rows:
        print(f"{row[0]} — {row[1]} — {row[2]}")

def show_category_counts(cur):
    cur.execute("""
        SELECT c.name, COUNT(d.id) as dish_count
        FROM category c
        LEFT JOIN dish d ON c.id = d.category_id
        GROUP BY c.name
        ORDER BY c.name;
    """)
    rows = cur.fetchall()
    print("\nКатегории и количество блюд:")
    for row in rows:
        print(f"{row[0]} — {row[1]}")


try:
    with psycopg2.connect(
        dbname="python_course_db",
        user="postgres",
        password="qwRw3go!wtR",
        host="localhost",
        port="5432"
    ) as conn:
        print("Подключение к БД прошло успешно")

        with conn.cursor() as cur:
            create_category_table(cur)
            create_dish_table(cur)

            while True:
                print("\nМеню:")
                print("1. Показать всё съестное меню")
                print("2. Показать блюда в ценовом диапазоне")
                print("3. Поиск по началу названия")
                print("4. Показать N самых дешёвых блюд")
                print("5. Категории и количество блюд")
                print("6. Выход")

                choice = input("Выберите пункт меню: ")

                if choice == "1":
                    show_menu(cur)
                    input("\nНажмите Enter, чтобы вернуться в меню...")
                elif choice == "2":
                    show_price_range(cur)
                    input("\nНажмите Enter, чтобы вернуться в меню...")
                elif choice == "3":
                    search_by_prefix(cur)
                    input("\nНажмите Enter, чтобы вернуться в меню...")
                elif choice == "4":
                    show_cheapest_dishes(cur)
                    input("\nНажмите Enter, чтобы вернуться в меню...")
                elif choice == "5":
                    show_category_counts(cur)
                    input("\nНажмите Enter, чтобы вернуться в меню...")
                elif choice == "6":
                    print("Выход из программы. До встречи в нашей столовке!")
                    break
                else:
                    print("Неверный выбор. Попробуйте снова.")
except:
    print("Ошибка при подключении к БД")
