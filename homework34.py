import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('restaurant.db')
cursor = conn.cursor()

# Создание таблиц и вставка данных (если ещё не созданы)
cursor.executescript("""
CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS dish (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    price NUMERIC(8,2) CHECK (price > 0),
    category_id INTEGER,
    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL
);

INSERT OR IGNORE INTO category (name) VALUES
('Супы'), ('Салаты'), ('Горячее'), ('Десерты'), ('Напитки');

INSERT OR IGNORE INTO dish (title, price, category_id) VALUES
('Борщ', 150.00, 1),
('Щи', 130.00, 1),
('Оливье', 200.00, 2),
('Цезарь', 250.00, 2),
('Стейк', 600.00, 3),
('Паста', 350.00, 3),
('Тирамису', 180.00, 4),
('Мороженое', 120.00, 4),
('Кофе', 100.00, 5),
('Чай', 80.00, 5),
('Лимонад', 90.00, 5);
""")

conn.commit()

def show_all_menu():
    cursor.execute("""
        SELECT d.title, d.price, c.name
        FROM dish d
        LEFT JOIN category c ON d.category_id = c.id
        ORDER BY d.title
    """)
    rows = cursor.fetchall()
    print("\nВсё меню:")
    for title, price, cat in rows:
        cat_name = cat if cat else "Без категории"
        print(f"  {title} — {price:.2f} — {cat_name}")

def show_by_price_range():
    try:
        min_price = float(input("Введите минимальную цену: "))
        max_price = float(input("Введите максимальную цену: "))
        if min_price > max_price:
            print("Минимальная цена не может быть больше максимальной.")
            return
        cursor.execute("""
            SELECT d.title, d.price, c.name
            FROM dish d
            LEFT JOIN category c ON d.category_id = c.id
            WHERE d.price BETWEEN ? AND ?
            ORDER BY d.price
        """, (min_price, max_price))
        rows = cursor.fetchall()
        if rows:
            print(f"\nБлюда в диапазоне от {min_price} до {max_price}:")
            for title, price, cat in rows:
                cat_name = cat if cat else "Без категории"
                print(f"  {title} — {price:.2f} — {cat_name}")
        else:
            print("Ничего не найдено.")
    except ValueError:
        print("Ошибка: введите корректное число.")

def search_by_prefix():
    prefix = input("Введите начало названия: ").strip()
    if not prefix:
        print("Пустой ввод.")
        return
    cursor.execute("""
        SELECT d.title, d.price, c.name
        FROM dish d
        LEFT JOIN category c ON d.category_id = c.id
        WHERE LOWER(d.title) LIKE ?
        ORDER BY d.title
    """, (prefix.lower() + '%',))
    rows = cursor.fetchall()
    if rows:
        print(f"\nРезультаты поиска по '{prefix}':")
        for title, price, cat in rows:
            cat_name = cat if cat else "Без категории"
            print(f"  {title} — {price:.2f} — {cat_name}")
    else:
        print("Ничего не найдено.")

def show_cheapest_n():
    try:
        n = int(input("Введите количество самых дешёвых блюд: "))
        if n <= 0:
            print("Введите положительное число.")
            return
        cursor.execute("""
            SELECT d.title, d.price, c.name
            FROM dish d
            LEFT JOIN category c ON d.category_id = c.id
            ORDER BY d.price ASC
            LIMIT ?
        """, (n,))
        rows = cursor.fetchall()
        if rows:
            print(f"\nТоп-{n} самых дешёвых блюд:")
            for title, price, cat in rows:
                cat_name = cat if cat else "Без категории"
                print(f"  {title} — {price:.2f} — {cat_name}")
        else:
            print("Блюд нет.")
    except ValueError:
        print("Ошибка: введите целое число.")

def show_categories_with_counts():
    cursor.execute("""
        SELECT c.name, COUNT(d.id) AS dish_count
        FROM category c
        LEFT JOIN dish d ON c.id = d.category_id
        GROUP BY c.id, c.name
        ORDER BY c.name
    """)
    rows = cursor.fetchall()
    print("\nКатегории и количество блюд:")
    for name, count in rows:
        print(f"  {name}: {count} блюд(а)")

def main():
    while True:
        print("\n--- Меню ресторана ---")
        print("1. Показать всё меню")
        print("2. Показать блюда в ценовом диапазоне")
        print("3. Поиск по началу названия")
        print("4. Показать N самых дешёвых блюд")
        print("5. Категории и количество блюд")
        print("0. Выход")
        choice = input("Выберите пункт: ").strip()

        if choice == '1':
            show_all_menu()
        elif choice == '2':
            show_by_price_range()
        elif choice == '3':
            search_by_prefix()
        elif choice == '4':
            show_cheapest_n()
        elif choice == '5':
            show_categories_with_counts()
        elif choice == '0':
            print("До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")

if __name__ == "__main__":
    main()

conn.close()
