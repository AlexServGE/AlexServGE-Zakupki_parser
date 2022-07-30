from bs4 import BeautifulSoup
import requests
from common_info import sku_price,sku_value,istender_novolume
import re


def all_participants_id(param):
    '''Только, чтобы проверить были ли участники'''
    text = param.find_all('td', 'tableBlock__col')
    text = {idx: el for idx, el in enumerate(text)}
    final_list = []
    for i in range(1, len(text), 3):
        if text[i].next_element.strip().isdigit():
            final_list.append(text[i].next_element.strip())
    return final_list


def all_participants_winner(param):
    '''Только, чтобы проверить были ли участники'''
    text = param.find_all('td', 'tableBlock__col')
    text = {idx: el for idx, el in enumerate(text)}
    final_list = []
    for i in range(2, len(text), 3):
        final_list.append(text[i].next_element.strip())
        if len(final_list) == len(all_participants_id(param)):
            break
    return final_list


def all_participants_endvalue(param, param2):
    '''Предложения участников'''
    text = param.find_all('td', 'tableBlock__col') # хорошо было бы заменить на gettext
    text = {idx: el for idx, el in enumerate(text)}
    final_list = []
    if istender_novolume(param2) is False:
        for i in range(3, len(text), 3):
            if ',' in text[i].next_element.strip():
                final_list.append(text[i].next_element.strip())
        return final_list
    else:
        start_price = sum([float(el.replace(",",".")) for el in sku_price(param2)])
        suppliers_prices_offered = []
        for i in range(3, len(text), 3):
            el_to_check_add = text[i].next_element.strip()
            if ',' in el_to_check_add:
                el_to_check_add = el_to_check_add.replace(',', '.').replace(" ","")
                if len(f'{start_price:.2f}')+1 >= len(el_to_check_add):   #+1 для случаев, когда участники предложили хх.ххх
                    suppliers_prices_offered.append(float(el_to_check_add))
        if suppliers_prices_offered == []:
            return []
        else:
            pattern = re.compile(r'\d+')  # не нужный?
            start_value = float(''.join(pattern.findall(sku_value(param2)[0])[:-1]) + '.' + ''.join(
                pattern.findall(sku_value(param2)[0])[-1]))
            suppliers_values_offered = []
            for el in suppliers_prices_offered:
                suppliers_values_offered.append(start_value * el / start_price)
            return suppliers_values_offered

def winner(param):
    other_text = param.get_text('\n', strip='True').split('\n')
    idx = other_text.index('Электронные документы об исполнении контракта')
    winner = other_text[idx-4]
    if '"' in winner:
        return winner
    else:
        return "No data about winner YET"


if __name__ == '__main__':
    user_agent = ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0')
    main_p = requests.get(
        f'https://zakupki.gov.ru/epz/order/notice/ea20/view/supplier-results.html?regNumber=0318300163422000319',
        headers={'User-Agent':user_agent})
    main_p_dec = main_p.content.decode(encoding='utf-8')
    soup = BeautifulSoup(main_p_dec, 'html.parser')

    # print(soup.prettify())
    # print(all_participants_id(soup))
    # print(all_participants_winner(soup))
    print(all_participants_endvalue(soup, soup))
