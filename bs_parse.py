from bs4 import BeautifulSoup

def get_stock_value(html_text: str):
    soup = BeautifulSoup(html_text, 'lxml')
    return soup.find('div', class_='stock').text.strip()
