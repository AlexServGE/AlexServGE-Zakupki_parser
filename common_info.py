import requests
from bs4 import BeautifulSoup
import re


def istender_novolume(param):
    if 'ч. 24 ст. 22 Закона № 44-ФЗ' in str(param.find_all()):
        return True
    else:
        return False


def center_name(param):
    '''ГОСУДАРСТВЕННОЕ БЮДЖЕТНОЕ УЧРЕЖДЕНИЕ ЗДРАВООХРАНЕНИЯ КЛИНИЧЕСКИЙ ОНКОЛОГИЧЕСКИЙ ДИСПАНСЕР 1 МИНИСТЕРСТВА ЗДРАВООХРАНЕНИЯ КРАСНОДАРСКОГО КРАЯ'''
    if param.count('Организация, осуществляющая размещение') == 2:
        text = param.split('Организация, осуществляющая размещение')[2]
        text = text.split('Почтовый адрес')[0]
        el_result = text
        pattern = re.compile(r'[А-ЯЁ]+')
        result = pattern.findall(el_result)
        result = ' '.join(result)
        return result
    else:
        text = param.split('Организация, осуществляющая размещение')[1]
        text = text.split('Почтовый адрес')[0]
        el_result = text
        pattern = re.compile(r'[А-ЯЁ]+')
        result = pattern.findall(el_result)
        result = ' '.join(result)
        return result


def dates(param):
    '''Все даты'''
    try:
        text = param.split('Дата и время начала срока подачи заявок')[1]
        pattern = re.compile(r'\d\d.\d\d.\d\d\d\d')
        result = pattern.findall(text)[:4]
    except IndexError:
        text = param.split('Дата и время окончания срока подачи заявок')[1]
        date_start = param.split('Размещено')[1]
        pattern = re.compile(r'\d\d.\d\d.\d\d\d\d')
        result = [pattern.findall(date_start)[0]] + pattern.findall(text)[:3]
        if '.' not in result[3]:
            result[3] = result[2]
            result[2] = 'No data'
        return result
    else:
        if '.' not in result[3]:
            result[3] = result[2]
            result[2] = 'No data'
        return result


def product_name(param):
    '''ЙОГЕКСОЛ, эти же теги ищут кол-во, цену, стоимость'''
    other_text = param.get_text('\n', strip='True').split('\n')
    final_list = []
    idx = 0
    every_second = 2
    distance_to_list = len(form_concentration(param)) * 2
    for el in range(0, distance_to_list):
        idx = other_text.index('Основной вариант поставки', idx + 1)
        if every_second % 2 == 0:
            final_list.append(other_text[idx + 1])
            every_second = every_second + 1
        else:
            every_second = every_second + 1
    return final_list


def sku_volume(param):
    '''Количество в мл'''
    if istender_novolume(param) is False:
        other_text = param.get_text('\n', strip='True').split('\n')
        final_list = []
        idx = 0
        for el in range(len(form_concentration(param))):
            idx = other_text.index('Сведения из ГРЛС', idx + 1)
            final_list.append(other_text[idx + 1])
        return final_list
    else:
        return ['Тендер без объема' for el in product_name(param)]


def sku_price(param):
    '''Цена за ед., 6,69 ; 9,60'''
    final_list = []
    if istender_novolume(param) is False:
        other_text = param.get_text('\n', strip='True').split('\n')
        idx = 0
        for el in range(len(form_concentration(param))):
            idx = other_text.index('Цена за единицу товара, ₽', idx + 1)
            final_list.append(other_text[idx + 1])
    else:
        text = param.get_text('\n', strip='True').split('\n')
        idx = 0
        for el in range(len(form_concentration(param))):
            idx = text.index('Начальная цена за единицу товара, ₽', idx+1)
            final_list.append(text[idx + 1])
    final_list = [el.replace('\xa0', '') for el in final_list]
    return final_list


def sku_value(param):
    '''СТОИМОСТЬ, ₽ 10 033 000,00 ; 7 900 000,00; 168 665,00; 146 025,00'''
    if istender_novolume(param) is False:
        other_text = param.get_text('\n', strip='True').split('\n')
        final_list = []
        idx = 0
        for el in range(len(form_concentration(param))):
            idx = other_text.index('Стоимость позиции', idx + 1)
            final_list.append(other_text[idx + 1])
        return final_list
    else:
        text = param.get_text("\n").split("\n")
        text = [el.strip() for el in text if el]
        final_list = []
        for el in range(len(form_concentration(param))):
            idx = text.index('Всего, ₽')
            final_list.append(text[idx + 1])
        return final_list


def form_concentration(param):
    '''['РАСТВОР ДЛЯ ИНЪЕКЦИЙ, 240 мг/мл, см[3*];^мл (мл)', 'РАСТВОР ДЛЯ ИНЪЕКЦИЙ, 350 мг/мл, см[3*];^мл (мл)']'''
    text = param.find_all("div", "tableBlock__scroll60px")  # блок готов для поиска Наименования ЛПУ
    text = {idx: el for idx, el in enumerate(text)}
    final_list = []
    for idx, el in text.items():
        el_result = el.next_element
        sub_result = el_result.split('\n')
        result = []
        for sub_el in sub_result:
            result.append(sub_el.strip())
        final_list.append(' '.join(result).strip())
    return final_list


if __name__ == '__main__':
    user_agent = ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0')
    main_p = requests.get(
        f'https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber=0318300163422000319',
        headers={'User-Agent': user_agent})
    main_p_dec = main_p.content.decode(encoding='utf-8')
    soup = BeautifulSoup(main_p_dec, 'html.parser')

    # print(soup.prettify())
    # print(dates(main_p_dec))
    # print(sku_price(soup))
    # print(sku_value(soup))
    print(istender_novolume(soup))
