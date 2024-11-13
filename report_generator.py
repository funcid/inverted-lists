from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from apartment import ApartmentDatabase
from typing import List, Dict
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

class ApartmentReportGenerator:
    """Генератор PDF-отчетов для базы данных квартир"""
    
    def __init__(self):
        """Инициализация генератора отчетов"""
        
        # Регистрация шрифта
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'RobotoMono[wght].ttf')
        pdfmetrics.registerFont(TTFont('Roboto', font_path))
        
        # Создание стилей
        self.styles = getSampleStyleSheet()
        self._create_custom_styles()
    
    def _create_custom_styles(self) -> None:
        """Создание пользовательских стилей для отчета"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            fontSize=16,
            spaceAfter=30,
            alignment=1,  # По центру
            fontName='Roboto'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            fontSize=11,
            spaceAfter=12,
            fontName='Roboto'
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeader',
            fontName='Roboto',
            fontSize=14,
            spaceAfter=20,
            spaceBefore=20
        ))
    
    def _create_database_summary(self, db: ApartmentDatabase) -> List:
        """Создание общей информации о базе данных"""
        elements = []
        
        # Заголовок секции
        elements.append(Paragraph(
            'Общая информация о базе данных',
            self.styles['CustomHeader']
        ))
        
        # Статистика
        total_apartments = len(db._apartments)
        unique_metros = len(db._indices['metro'])
        avg_area = sum(apt.total_area for apt in db._apartments) / total_apartments if total_apartments > 0 else 0
        
        summary_data = [
            ['Всего квартир:', str(total_apartments)],
            ['Количество станций метро:', str(unique_metros)],
            ['Средняя площадь:', f"{avg_area:.1f} м²"]
        ]
        
        # Создание таблицы со статистикой
        summary_table = Table(summary_data, colWidths=[200, 100])
        summary_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Roboto'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_apartment_table(self, apartments: List) -> Table:
        """Создание таблицы с информацией о квартирах"""
        # Заголовки таблицы
        headers = ['Комнат', 'Площадь', 'Кухня', 'Балконы', 'Метро']
        
        # Данные для таблицы
        data = [headers]
        for apt in apartments:
            data.append([
                str(apt.rooms),
                f"{apt.total_area} м²",
                f"{apt.kitchen_area} м²",
                str(apt.balconies),
                apt.metro
            ])
        
        # Создание таблицы
        table = Table(data, colWidths=[60, 80, 80, 60, 150])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Roboto'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        
        return table
    
    def _create_index_section(self, db: ApartmentDatabase) -> List:
        """Создание секции с информацией об индексах"""
        elements = []
        
        elements.append(Paragraph(
            'Индексация данных',
            self.styles['CustomHeader']
        ))
        
        # Информация об индексах
        for index_name, index_data in db._indices.items():
            elements.append(Paragraph(
                f'Индекс: {index_name}',
                self.styles['CustomBody']
            ))
            
            # Создаем таблицу для каждого индекса
            index_rows = []
            for key, value_set in index_data.items():
                index_rows.append([str(key), f"Записи: {sorted(value_set)}"])
            
            if index_rows:
                index_table = Table(index_rows, colWidths=[100, 300])
                index_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Roboto'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                    ('PADDING', (0, 0), (-1, -1), 4),
                ]))
                elements.append(index_table)
                elements.append(Spacer(1, 10))
        
        return elements
    
    def _create_search_results_section(self, db: ApartmentDatabase) -> List:
        """Создание секции с результатами поиска"""
        elements = []
        
        elements.append(Paragraph(
            'Результаты поиска',
            self.styles['CustomHeader']
        ))
        
        # Определяем тестовые поисковые запросы
        search_tests = [
            {
                'name': 'Поиск по метро "Академическая"',
                'criteria': {'metro': 'Академическая'},
                'operator': 'AND'
            },
            {
                'name': 'Поиск двухкомнатных квартир',
                'criteria': {'rooms': 2},
                'operator': 'AND'
            },
            {
                'name': 'Поиск квартир с 2 балконами у метро "Политехническая"',
                'criteria': {'balconies': 2, 'metro': 'Политехническая'},
                'operator': 'AND'
            },
            {
                'name': 'Поиск квартир с площадью 75м² ИЛИ с 2 балконами',
                'criteria': {'total_area': 75, 'balconies': 2},
                'operator': 'OR'
            }
        ]
        
        # Выполняем каждый поиск и добавляем результаты
        for test in search_tests:
            elements.append(Paragraph(
                test['name'],
                self.styles['CustomBody']
            ))
            
            results = db.search(test['criteria'], test['operator'])
            
            if results:
                # Создаем таблицу с результатами
                data = [['Комнат', 'Площадь', 'Кухня', 'Балконы', 'Метро']]
                for apt in results:
                    data.append([
                        str(apt.rooms),
                        f"{apt.total_area} м²",
                        f"{apt.kitchen_area} м²",
                        str(apt.balconies),
                        apt.metro
                    ])
                
                results_table = Table(data, colWidths=[60, 80, 80, 60, 150])
                results_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), 'Roboto'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('PADDING', (0, 0), (-1, -1), 4),
                ]))
                elements.append(results_table)
            else:
                elements.append(Paragraph(
                    "Ничего не найдено",
                    self.styles['CustomBody']
                ))
            
            elements.append(Spacer(1, 10))
        
        return elements
    
    def _create_logic_description(self) -> List:
        """Создание секции с описанием логики работы"""
        elements = []
        
        elements.append(Paragraph(
            'Описание логики работы',
            self.styles['CustomHeader']
        ))
        
        descriptions = [
            """Система использует инвертированные индексы для быстрого поиска квартир по различным критериям. 
            Основные компоненты системы:""",
            
            """1. Структура данных:
            - Основной список квартир хранится в памяти
            - Для каждого атрибута (площадь, комнаты, метро и т.д.) создается отдельный индекс
            - Каждый индекс представляет собой хеш-таблицу, где ключ - это значение атрибута, 
              а значение - множество индексов квартир с таким значением атрибута""",
            
            """2. Процесс индексации:
            - При добавлении новой квартиры она получает уникальный индекс
            - Значения всех атрибутов квартиры добавляются в соответствующие индексы
            - В каждом индексе создается связь между значением атрибута и индексом квартиры""",
            
            """3. Процесс поиска:
            - Для каждого критерия поиска система обращается к соответствующему индексу
            - Получает множество индексов квартир, удовлетворяющих критерию
            - При использовании оператора AND выполняется пересечение множеств
            - При использовании оператора OR выполняется объединение множеств
            - На основе полученных индексов формируется итоговый список квартир""",
            
            """4. Преимущества подхода:
            - Быстрый поиск по любой комбинации критериев
            - Эффективное использование памяти благодаря множествам
            - Возможность комбинировать условия через операторы AND и OR
            - Легкое добавление новых критериев поиска"""
        ]
        
        for desc in descriptions:
            elements.append(Paragraph(
                desc,
                self.styles['CustomBody']
            ))
            elements.append(Spacer(1, 10))
        
        return elements
    
    def generate_report(self, db: ApartmentDatabase, filename: str) -> None:
        """
        Генерация PDF-отчета по базе данных квартир.
        
        Args:
            db (ApartmentDatabase): База данных квартир
            filename (str): Путь к файлу для сохранения отчета
        """
        doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Список элементов отчета
        elements = []
        
        # Заголовок отчета
        elements.append(Paragraph(
            'Отчет по базе данных квартир',
            self.styles['CustomTitle']
        ))
        
        # Добавление описания логики работы
        elements.extend(self._create_logic_description())
        
        # Добавление общей информации
        elements.extend(self._create_database_summary(db))
        
        # Добавление информации об индексах
        elements.extend(self._create_index_section(db))
        
        # Добавление результатов поиска
        elements.extend(self._create_search_results_section(db))
        
        # Секция со списком всех квартир
        elements.append(Paragraph(
            'Полный список квартир',
            self.styles['CustomHeader']
        ))
        elements.append(self._create_apartment_table(db._apartments))
        
        # Генерация отчета
        doc.build(elements)

def generate_sample_report():
    """Создание примера отчета"""
    # Создание и заполнение базы данных
    db = ApartmentDatabase()
    db.load_from_file('apartments.json')
    
    # Создание генератора отчетов
    report_gen = ApartmentReportGenerator()
    
    # Генерация отчета
    report_gen.generate_report(db, 'apartment_report.pdf')

if __name__ == "__main__":
    generate_sample_report() 