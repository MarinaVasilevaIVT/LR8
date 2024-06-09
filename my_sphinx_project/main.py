"""
Разработать фрагмент программы, позволяющий получать данные о текущих курсах валют с сайта Центробанка РФ с использованием сервиса, который они предоставляют.

https://cbr.ru/development/
http://www.cbr.ru/scripts/XML_daily.asp

https://digitology.tech/docs/python_3/tutorial/floatingpoint.html
"""

import requests
from xml.etree import ElementTree as ET
import time
import matplotlib.pyplot as plt

def get_currencies(currencies_ids_lst: list) -> list:
    
    """
    
    Получает данные о текущих курсах валют с сайта Центробанка РФ.

    Args:
    - currencies_ids_lst (list): Список идентификаторов валют.

    Returns:
    - list: Список словарей с данными о валютах.
    
    """
  
    cur_res_str = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')

    result = []

    if cur_res_str.status_code == 200:
        root = ET.fromstring(cur_res_str.content)
        valutes = root.findall("Valute")

        for _v in valutes:
            valute_id = _v.get('ID')
            valute = {}
            if str(valute_id) in currencies_ids_lst:
                valute_cur_name = _v.find('Name').text
                valute_cur_val = _v.find('Value').text
                valute_charcode = _v.find('CharCode').text
                valute_data = (valute_cur_name, valute_cur_val)
              
                nominal = int(_v.find('Nominal').text)
                if nominal != 1:
                  valute_data += (nominal,)

                valute[valute_charcode] = (valute_data)
                result.append(valute)
    else:
        print("Ошибка при получении данных о курсах валют")

    return result

class CurrenciesLst:

  """
  
  Класс для работы с информацией о курсах валют.
  
  """
  
  def __init__(self):
      """
      
      Инициализация класса CurrenciesLst.
      
      """
      self._valutes = {}  
      self._tracked_currencies = []  
      self._last_updated = None 

  def __del__(self):
      # Деструктор класса
      pass  

  def get_currencies(self, currencies_ids_lst: list):

    """
    
    Получает данные о текущих курсах валют и сохраняет их в объекте класса.

    Args:
    - currencies_ids_lst (list): Список идентификаторов валют.

    """
    
    cur_res_str = requests.get('http://www.cbr.ru/scripts/XML_daily.asp')

    if cur_res_str.status_code == 200:
        root = ET.fromstring(cur_res_str.content)
        valutes = root.findall("Valute")
      

        for _v in valutes:
            valute_id = _v.get('ID')
            valute = {}

            if valute_id in currencies_ids_lst:  # Проверяем, присутствует ли ID в списке, если нет - пропускаем
                valute_cur_name = _v.find('Name').text
                valute_cur_val = _v.find('Value').text
                valute_charcode = _v.find('CharCode').text

                nominal = int(_v.find('Nominal').text)
                valute_data = (valute_cur_name,)

                if valute_cur_val is not None:
                  valute_value_parts = valute_cur_val.replace(',', '.').split('.')
                  int_part = valute_value_parts[0]
                  fract_part = valute_value_parts[1] if len(valute_value_parts) > 1 else '0'
                  valute_data += (int_part, fract_part)
                else:
                  valute_value_parts = ['0']

                if nominal != 1:
                    valute_data += (nominal,)

                valute[valute_charcode] = valute_data
                self._valutes[valute_charcode] = valute
        self._last_updated = int(time.time())

  @property
  def valutes(self):
      return self._valutes

  @property
  def tracked_currencies(self):
      return self._tracked_currencies

  @tracked_currencies.setter
  def tracked_currencies(self, currencies):
      self._tracked_currencies = currencies

  def plot_currencies(self):
    """
    
    Строит график текущих курсов валют на основе данных, хранящихся в объекте класса.

    """
    if self._valutes:
        currencies = list(self._valutes.keys())  # Используем CharCode
        values = []
        for valute_data in self._valutes.values():
            for val in valute_data.values():
                value = float(val[1].replace(',', '.')) if val[1] else 0.0
                values.append(value)

        plt.figure(figsize=(10, 6))
        plt.bar(currencies, values, color='blue')
        plt.xlabel('Валюта')
        plt.ylabel('Значение')
        plt.title('График курсов валют')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('currencies.jpg')
        plt.show()
    else:
        print("Нет данных о курсах валют для построения графика.")


if __name__ == '__main__':
  currency_list = CurrenciesLst()

  currency_list.get_currencies(['R01035', 'R01335', 'R01700J'])

  if currency_list.valutes: 
      currency_list.plot_currencies()
  else:
      print("Данные о курсах валют отсутствуют или не удалось получить.")
