from typing import Dict, List, Set, Optional, Tuple
import json

class Apartment:
    """
    Класс для представления квартиры.
    Использует tuple для хранения данных для оптимизации памяти.
    """
    __slots__ = ('_data',)  # Оптимизация использования памяти

    def __init__(self, total_area: int, rooms: int, kitchen_area: int, 
                 balconies: int, metro: str):
        """
        Инициализация квартиры.
        Args:
            total_area (int): Общая площадь в кв. метрах
            rooms (int): Количество комнат
            kitchen_area (int): Площадь кухни в кв. метрах
            balconies (int): Количество балконов
            metro (str): Ближайшая станция метро
        """
        # Храним все данные в tuple для экономии памяти
        self._data: Tuple[int, int, int, int, str] = (
            total_area, rooms, kitchen_area, balconies, metro
        )
    
    # Свойства для доступа к данным
    @property
    def total_area(self) -> int:
        return self._data[0]
    
    @property
    def rooms(self) -> int:
        return self._data[1]
    
    @property
    def kitchen_area(self) -> int:
        return self._data[2]
    
    @property
    def balconies(self) -> int:
        return self._data[3]
    
    @property
    def metro(self) -> str:
        return self._data[4]
    
    def __str__(self) -> str:
        """Строковое представление квартиры"""
        return (f"{self.rooms}-комн. кв., {self.total_area}м², "
                f"кухня {self.kitchen_area}м², "
                f"балконов: {self.balconies}, метро: {self.metro}")


class ApartmentDatabase:
    """
    База данных квартир с инвертированными индексами для быстрого поиска.
    Использует массивы и хеш-таблицы для эффективного хранения и поиска.
    """
    
    def __init__(self):
        """Инициализация пустой базы данных"""
        # Основной массив для хранения квартир
        self._apartments: List[Apartment] = []
        
        # Инвертированные индексы для быстрого поиска
        # Каждый индекс отображает значение атрибута на множество индексов квартир
        self._indices: Dict[str, Dict] = {
            'total_area': {},    # int -> Set[int]
            'rooms': {},         # int -> Set[int]
            'kitchen_area': {},  # int -> Set[int]
            'balconies': {},     # int -> Set[int]
            'metro': {}          # str -> Set[int]
        }
    
    def _clear_indices(self) -> None:
        """Очистка всех индексов"""
        for index in self._indices.values():
            index.clear()
    
    def _add_to_index(self, index_name: str, key: int | str, 
                      apartment_index: int) -> None:
        """
        Добавление значения в индекс.
        
        Args:
            index_name (str): Имя индекса ('total_area', 'rooms', etc.)
            key: Значение атрибута (ключ для индекса)
            apartment_index (int): Индекс квартиры в основном массиве
        """
        if key not in self._indices[index_name]:
            self._indices[index_name][key] = set()
        self._indices[index_name][key].add(apartment_index)
    
    def _add_apartment(self, apartment: Apartment) -> None:
        """
        Добавление квартиры в базу данных и обновление всех индексов.
        
        Args:
            apartment (Apartment): Объект квартиры для добавления
        """
        apartment_index = len(self._apartments)
        self._apartments.append(apartment)
        
        # Обновление всех индексов
        self._add_to_index('total_area', apartment.total_area, apartment_index)
        self._add_to_index('rooms', apartment.rooms, apartment_index)
        self._add_to_index('kitchen_area', apartment.kitchen_area, apartment_index)
        self._add_to_index('balconies', apartment.balconies, apartment_index)
        self._add_to_index('metro', apartment.metro, apartment_index)
    
    def load_from_file(self, filename: str) -> None:
        """
        Загрузка данных из JSON файла.
        
        Args:
            filename (str): Путь к JSON файлу с данными
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Очистка существующих данных
        self._apartments.clear()
        self._clear_indices()
        
        # Загрузка новых данных
        for apt_data in data:
            apartment = Apartment(
                total_area=int(apt_data['total_area']),
                rooms=int(apt_data['rooms']),
                kitchen_area=int(apt_data['kitchen_area']),
                balconies=int(apt_data['balconies']),
                metro=apt_data['metro']
            )
            self._add_apartment(apartment)
    
    def _get_index_for_field(self, field: str) -> Optional[Dict]:
        """
        Получение соответствующего индекса для поля.
        
        Args:
            field (str): Имя поля для поиска
        
        Returns:
            Optional[Dict]: Индекс для поля или None, если поле неизвестно
        """
        return self._indices.get(field)
    
    def search(self, criteria: Dict[str, int | str], operator: str = 'AND') -> List[Apartment]:
        """
        Поиск квартир по заданным критериям.
        
        Args:
            criteria (Dict[str, int | str]): Словарь критериев поиска
            operator (str): Оператор для комбинации критериев ('AND' или 'OR')
        
        Returns:
            List[Apartment]: Список квартир, удовлетворяющих критериям
        """
        if not criteria:
            return []
        
        result_indices: Optional[Set[int]] = None
        
        for field, value in criteria.items():
            index = self._get_index_for_field(field)
            if index is None:
                continue
                
            current_indices = index.get(value, set())
            
            if result_indices is None:
                result_indices = current_indices.copy()
            else:
                if operator == 'AND':
                    result_indices &= current_indices
                else:  # OR
                    result_indices |= current_indices
        
        if not result_indices:
            return []
            
        return [self._apartments[i] for i in sorted(result_indices)] 