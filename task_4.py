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

def insert_dish(cur):
    cur.execute("""
                INSERT INTO dish (title, price, category_id) 
                VALUES  ('Борщ', '300', '1'),
                        ('Солянка', '350', '1'),
                        ('Грибной суп', '250', '1'),
                        ('Гороховый суп', '400', '1'),
                        ('Цезарь', '550', '2'),
                        ('Оливье','530','2'),
                        ('Винегрет','520','2'),
                        ('Мимоза', '480', '2'),
                        ('Овощной', '450', '2'),
                        ('Котлеты с пюре', '690', '3'),
                        ('Карбонара', '690', '3'),
                        ('Плов', '750', '3'),
                        ('Шашлык свиной', '750', '3'),
                        ('Ризотто', '690', '3'),
                        ('Жаркое', '700', '3'),
                        ('Штрудель', '270', '4'),
                        ('Мороженое', '150', '4'),
                        ('Чизкейк', '350', '4'),
                        ('Тирамису', '290', '4'),
                        ('Профитроли', '400', '4'),
                        ('Морс', '200', '5'),
                        ('Лимонад', '250', '5'),
                        ('Мохито', '300', '5'),
                        ('Сок апельсиновый', '180', '5');
                """)

def create_category_table(cur, insert: bool = False): #при первичном внесеннии данных insert=True
    cur.execute("""
        CREATE TABLE IF NOT EXISTS category (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
        );            
    """)
    if insert:
       insert_category(cur)

def create_dish_table(cur, insert: bool = False): #при первичном внесеннии данных insert=True
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dish (
            id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            title TEXT NOT NULL,
            price NUMERIC(8,2) CHECK(price>0),
            category_id INT REFERENCES category(id) ON DELETE SET NULL
        );
    """)
    if insert:
        insert_dish(cur)

def get_all_menu(conn):
    with conn.cursor() as cur:
        cur.execute("""
                    SELECT d.title, d.price, c.name
                    FROM dish d JOIN category c ON d.category_id=c.id;
                    """ )
        return cur.fetchall()

def get_dish_between_min_max_price(conn, min_price, max_price):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.title, d.price, c.name
            FROM dish d JOIN category c ON d.category_id=c.id
            WHERE d.price>= %s AND d.price <= %s;
        """, (min_price, max_price))
        return cur.fetchall()

def search_dish_by_prefix(conn, start):
    prefix = str(start)
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.title, d.price, c.name
            FROM dish d JOIN category c ON d.category_id=c.id
            WHERE d.title ILIKE %s
            ORDER BY d.title;
        """, (prefix + "%",))
        return cur.fetchall()

def search_n_dish_by_min_price(conn, n):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT d.title, d.price, c.name
            FROM dish d JOIN category c ON d.category_id=c.id
            ORDER BY d.price
            LIMIT %s;
        """, (n,))
        return cur.fetchall()
def search_category_dish (conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.name, COUNT(d.title)
            FROM category c LEFT JOIN dish d ON d.category_id = c.id
            GROUP BY c.name;
        """)
        return cur.fetchall()
def run_menu(conn):
    while True:
        print("\n МЕНЮ")
        print("1. Показать всё меню")
        print("2. Показать блюда в ценовом диапазоне")
        print("3. Поиск по началу названия блюда")
        print("4. Показать N самых дешёвых блюд")
        print("5. Категории и количество блюд в них")
        print("0. Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            print(get_all_menu(conn))

        elif choice == "2":
            min_price = float(input("Минимальная цена: ").replace(",", "."))
            max_price = float(input("Максимальная цена: ").replace(",", "."))
            print(get_dish_between_min_max_price(conn, min_price, max_price))

        elif choice == "3":
            prefix = input("Введите начало названия: ").strip()
            print(search_dish_by_prefix(conn, prefix))

        elif choice == "4":
            n = int(input("Укажите, сколько недорогих блюд показать: "))
            print(search_n_dish_by_min_price(conn, n))

        elif choice == "5":
            print(search_category_dish(conn))

        elif choice == "0":
            print("Выход.")
            break

        else:
            print("Неизвестный пункт меню.")
try:
    with psycopg2.connect(
        dbname="menu",
        user="postgres",
        password="mary2002",
        host="localhost",
        port="5432"
    ) as conn:
        print("Подключение к БД прошло успешно")

        with conn.cursor() as cur:
            create_category_table(cur)
            create_dish_table(cur)
        conn.commit()
        
        run_menu(conn)

except Exception as e:
    print("Ошибка при подключении к БД: ", repr(e))
