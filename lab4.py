#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Мини-система меню без базы данных.
Данные хранятся в памяти (списки и словари).
Поддерживает те же 5 функций, что и SQL-версия.
"""

# ----- Исходные данные -----

categories = {
    1: "Супы",
    2: "Салаты",
    3: "Горячее",
    4: "Десерты",
    5: "Напитки"
}

dishes = [
    {"title": "Борщ", "price": 120.00, "category_id": 1},
    {"title": "Солянка", "price": 130.00, "category_id": 1},
    {"title": "Оливье", "price": 90.00, "category_id": 2},
    {"title": "Цезарь", "price": 150.00, "category_id": 2},
    {"title": "Котлета с пюре", "price": 180.00, "category_id": 3},
    {"title": "Плов", "price": 160.00, "category_id": 3},
    {"title": "Тирамису", "price": 110.00, "category_id": 4},
    {"title": "Чизкейк", "price": 120.00, "category_id": 4},
    {"title": "Чай", "price": 30.00, "category_id": 5},
    {"title": "Щи", "price": 110.00, "category_id": 1},
    {"title": "Куриный суп", "price": 100.00, "category_id": 1},
    {"title": "Грибной суп", "price": 140.00, "category_id": 1},
    {"title": "Греческий салат", "price": 130.00, "category_id": 2},
    {"title": "Салат с креветками", "price": 200.00, "category_id": 2},
    {"title": "Винегрет", "price": 80.00, "category_id": 2},
    {"title": "Бефстроганов", "price": 220.00, "category_id": 3},
    {"title": "Курица гриль", "price": 190.00, "category_id": 3},
    {"title": "Лазанья", "price": 210.00, "category_id": 3},
    {"title": "Мороженое с шоколадом", "price": 80.00, "category_id": 4},
    {"title": "Медик с орехами", "price": 100.00, "category_id": 4},
    {"title": "Фруктовый салат", "price": 90.00, "category_id": 4},
    {"title": "Сок апельсиновый", "price": 60.00, "category_id": 5},
    {"title": "Минеральная вода", "price": 40.00, "category_id": 5},
    {"title": "Лимонад домашний", "price": 70.00, "category_id": 5},
    {"title": "Кофе", "price": 50.00, "category_id": 5},
]

# ----- Функции меню -----


def show_all_menu():
    print("\nПолное меню:")
    for dish in sorted(dishes, key=lambda x: x["title"].lower()):
        cat_name = categories.get(dish["category_id"], "Без категории")
        print(f"{dish['title']} — {dish['price']} — {cat_name}")


def show_by_price_range():
    try:
        min_price = float(input("Введите минимальную цену: "))
        max_price = float(input("Введите максимальную цену: "))
    except ValueError:
        print("Ошибка: нужно ввести числа.")
        return

    if min_price > max_price:
        print("Минимальная цена не может быть больше максимальной.")
        return

    filtered = [d for d in dishes if min_price <= d["price"] <= max_price]
    filtered.sort(key=lambda x: x["price"])

    print(f"\nБлюда в диапазоне {min_price} — {max_price}:")
    if not filtered:
        print("Нет подходящих блюд.")
    for d in filtered:
        print(f"{d['title']} — {d['price']} — {categories.get(d['category_id'])}")


def search_by_prefix():
    prefix = input("Введите начало названия блюда: ").strip().lower()
    if not prefix:
        print("Пустая строка — возвращаемся в меню.")
        return

    result = [
        d for d in dishes if d["title"].lower().startswith(prefix)
    ]
    result.sort(key=lambda x: x["title"])

    print(f"\nБлюда, начинающиеся на '{prefix}':")
    if not result:
        print("Не найдено.")
    for d in result:
        print(f"{d['title']} — {d['price']} — {categories.get(d['category_id'])}")


def show_cheapest_dishes():
    try:
        n = int(input("Введите количество самых дешёвых блюд: "))
    except ValueError:
        print("Ошибка: нужно ввести целое число.")
        return

    if n <= 0:
        print("Число должно быть положительным.")
        return

    sorted_dishes = sorted(dishes, key=lambda x: x["price"])
    result = sorted_dishes[:n]

    print(f"\n{n} самых дешёвых блюд:")
    for d in result:
        print(f"{d['title']} — {d['price']} — {categories.get(d['category_id'])}")


def show_category_counts():
    counts = {cid: 0 for cid in categories.keys()}
    for d in dishes:
        cid = d["category_id"]
        counts[cid] = counts.get(cid, 0) + 1

    print("\nКатегории и количество блюд:")
    for cid, name in sorted(categories.items(), key=lambda x: x[1]):
        print(f"{name} — {counts.get(cid, 0)}")


# ----- Главное меню -----

def main():
    while True:
        print("\nМеню:")
        print("1. Показать всё меню")
        print("2. Показать блюда в ценовом диапазоне")
        print("3. Поиск по началу названия")
        print("4. Показать N самых дешёвых блюд")
        print("5. Категории и количество блюд")
        print("6. Выход")

        choice = input("Выберите пункт меню: ").strip()

        if choice == "1":
            show_all_menu()
            input("\nНажмите Enter, чтобы вернуться в меню...")
        elif choice == "2":
            show_by_price_range()
            input("\nНажмите Enter, чтобы вернуться в меню...")
        elif choice == "3":
            search_by_prefix()
            input("\nНажмите Enter, чтобы вернуться в меню...")
        elif choice == "4":
            show_cheapest_dishes()
            input("\nНажмите Enter, чтобы вернуться в меню...")
        elif choice == "5":
            show_category_counts()
            input("\nНажмите Enter, чтобы вернуться в меню...")
        elif choice == "6":
            print("Выход из программы. До свидания!")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")


if __name__ == "__main__":
    main()
