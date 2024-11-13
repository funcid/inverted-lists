from apartment import ApartmentDatabase
import json
from typing import List, Dict

def create_sample_data(filename: str) -> None:
    """
    Создание тестового файла данных с примерами квартир.
    
    Args:
        filename (str): Путь к файлу для сохранения данных
    """
    apartments: List[Dict] = [
        {
            "total_area": 75,
            "rooms": 3,
            "kitchen_area": 12,
            "balconies": 1,
            "metro": "Академическая"
        },
        {
            "total_area": 45,
            "rooms": 1,
            "kitchen_area": 9,
            "balconies": 1,
            "metro": "Политехническая"
        },
        {
            "total_area": 60,
            "rooms": 2,
            "kitchen_area": 10,
            "balconies": 2,
            "metro": "Академическая"
        },
        {
            "total_area": 100,
            "rooms": 4,
            "kitchen_area": 15,
            "balconies": 2,
            "metro": "Политехническая"
        }
    ]
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(apartments, f, ensure_ascii=False, indent=2)

def run_search_test(db: ApartmentDatabase, 
                   test_name: str,
                   criteria: Dict,
                   operator: str = 'AND') -> None:
    """
    Выполнение отдельного теста поиска.
    
    Args:
        db (ApartmentDatabase): База данных квартир
        test_name (str): Название теста
        criteria (Dict): Критерии поиска
        operator (str): Оператор для комбинации критериев
    """
    print(f"\n{test_name}:")
    results = db.search(criteria, operator)
    if results:
        for apt in results:
            print(apt)
    else:
        print("Ничего не найдено")

def test_apartment_database() -> None:
    """Выполнение всех тестов базы данных квартир"""
    # Создание и загрузка тестовых данных
    create_sample_data('apartments.json')
    db = ApartmentDatabase()
    db.load_from_file('apartments.json')
    
    # Тест 1: Поиск по метро
    run_search_test(
        db,
        "Тест 1: Поиск квартир рядом с метро 'Академическая'",
        {'metro': 'Академическая'}
    )
    
    # Тест 2: Поиск по количеству комнат
    run_search_test(
        db,
        "Тест 2: Поиск двухкомнатных квартир",
        {'rooms': 2}
    )
    
    # Тест 3: Поиск по нескольким критериям с AND
    run_search_test(
        db,
        "Тест 3: Поиск квартир с 2 балконами у метро 'Политехническая'",
        {
            'balconies': 2,
            'metro': 'Политехническая'
        },
        'AND'
    )
    
    # Тест 4: Поиск по нескольким критериям с OR
    run_search_test(
        db,
        "Тест 4: Поиск квартир с площадью 75м² ИЛИ с 2 балконами",
        {
            'total_area': 75,
            'balconies': 2
        },
        'OR'
    )

if __name__ == "__main__":
    test_apartment_database()
