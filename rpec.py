from bs4 import BeautifulSoup
import requests


def winner_info(param):
    other_text = param.get_text('\n', strip='True').split('\n')
    idx = other_text.index('Полное наименование поставщика')
    return other_text[idx+1]


if __name__ == '__main__':
    user_agent = ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0')
    secondary_p = requests.get(
        f'https://zakupki.gov.ru/epz/order/notice/rpec/common-info.html?regNumber=03212000220220002610001',
        headers={'User-Agent':user_agent})
    secondary_p_dec = secondary_p.content.decode(encoding='utf-8')
    soup = BeautifulSoup(secondary_p_dec, 'html.parser')
    print(winner_info(soup))
    # print(soup.prettify())
