import os
import csv
from collections import defaultdict

class PriceMachine:
    def __init__(self):
        self.data = []
        self.name_length = 0

    def load_prices(self, folder_path='.'):
        """
        Сканирует указанный каталог. Ищет файлы со словом price в названии.
        В файле ищет столбцы с названием товара, ценой и весом.
        """
        self.data = []
        for filename in os.listdir(folder_path):
            if 'price' in filename:
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    headers = next(reader)
                    product_col, price_col, weight_col = self._search_product_price_weight(headers)
                    if product_col is not None and price_col is not None and weight_col is not None:
                        for row in reader:
                            if len(row) > max(product_col, price_col, weight_col):
                                product = row[product_col].strip()
                                price = float(row[price_col].replace(',', '.'))
                                weight = float(row[weight_col].replace(',', '.'))
                                price_per_kg = price / weight
                                self.data.append({
                                    'product': product,
                                    'price': price,
                                    'weight': weight,
                                    'file': filename,
                                    'price_per_kg': price_per_kg
                                })

    def _search_product_price_weight(self, headers):
        """
        Возвращает номера столбцов с названием товара, ценой и весом.
        """
        product_col = price_col = weight_col = None
        for idx, header in enumerate(headers):
            if header.lower() in ['название', 'продукт', 'товар', 'наименование']:
                product_col = idx
            elif header.lower() in ['цена', 'розница']:
                price_col = idx
            elif header.lower() in ['фасовка', 'масса', 'вес']:
                weight_col = idx
        return product_col, price_col, weight_col

    def export_to_html(self, fname='output.html'):
        """
        Выгружает все данные в html файл.
        """
        with open(fname, 'w', encoding='utf-8') as html_file:
            html_file.write('''
            <!DOCTYPE html>
            <html>
            <head>
                <title>Позиции продуктов</title>
            </head>
            <body>
                <table border="1">
                    <tr>
                        <th>№</th>
                        <th>Название</th>
                        <th>Цена</th>
                        <th>Фасовка</th>
                        <th>Файл</th>
                        <th>Цена за кг.</th>
                    </tr>
            ''')
            for idx, item in enumerate(sorted(self.data, key=lambda x: x['price_per_kg']), start=1):
                html_file.write(f'''
                    <tr>
                        <td>{idx}</td>
                        <td>{item['product']}</td>
                        <td>{item['price']}</td>
                        <td>{item['weight']}</td>
                        <td>{item['file']}</td>
                        <td>{item['price_per_kg']:.2f}</td>
                    </tr>
                ''')
            html_file.write('''
                </table>
            </body>
            </html>
            ''')

    def find_text(self, text):
        """
        Возвращает список позиций, содержащих указанный текст в названии продукта.
        """
        results = [item for item in self.data if text.lower() in item['product'].lower()]
        return sorted(results, key=lambda x: x['price_per_kg'])

    def run_console_interface(self):
        """
        Запускает консольный интерфейс для поиска товаров.
        """
        while True:
            query = input("Введите текст для поиска (или 'exit' для выхода): ").strip()
            if query.lower() == 'exit':
                print("Работа завершена.")
                break
            results = self.find_text(query)
            if results:
                print(f"{'№':<3} {'Наименование':<30} {'цена':<10} {'вес':<5} {'файл':<15} {'цена за кг.':<10}")
                for idx, item in enumerate(results, start=1):
                    print(f"{idx:<3} {item['product']:<30} {item['price']:<10.2f} {item['weight']:<5.2f} {item['file']:<15} {item['price_per_kg']:<10.2f}")
            else:
                print("Ничего не найдено.")

# Пример использования
if __name__ == "__main__":
    pm = PriceMachine()
    pm.load_prices()
    pm.export_to_html()
    pm.run_console_interface()