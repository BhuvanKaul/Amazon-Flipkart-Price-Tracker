import requests
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

apiKey = os.getenv("API_KEY")


custom_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
    'Accept-Language': 'en-US,en;q=0.9,en-IN;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Referer': 'https://www.amazon.in/'
}


def get_html(url):
    payload = { 'api_key': apiKey, 'device_type': 'desktop' , 'url':url}
    html = requests.get('https://api.scraperapi.com/', params=payload)
    return html


def getPriceAmazon(url):
    html = get_html(url).text
    soup = BeautifulSoup(html, 'lxml')
    price = soup.find('span', class_='a-price-whole').text.replace(',','')
    return float(price)


def writeHTML(text):
    with open('html.txt', 'w', encoding='utf-8') as file:
        file.write(text)

def getPriceFlipkart(url):
    html = get_html(url).text
    with open('html.txt', 'w', encoding='utf-8') as f:
        f.write(html)
    soup = BeautifulSoup(html, 'lxml')
    price_tag = soup.select_one('div.Nx9bqj.CxhGGd')
    price = price_tag.text.replace(',', '')
    return float(price[1:])   # index 0 is rupee symbol.


def getDetailsAmazon(url):
    html = get_html(url).text
    soup = BeautifulSoup(html, 'lxml')

    name = soup.find('span', id='productTitle').text.strip()
    img = soup.find('img', id='landingImage')['src']

    specKeys = [keys.text for keys in soup.findAll('span', class_='a-size-base a-text-bold')] #first 2 are useless can be more than values. Use from index 2 till we have values
    specValues = [values.text for values in soup.findAll('span', class_='a-size-base po-break-word')]

    specs = []
    if len(specKeys) > 2 and len(specValues) > 0:
        for i in range(2, min(len(specKeys), len(specValues) + 2)):
            specs.append([specKeys[i], specValues[i-2]])
    
    return [name, img, specs]


def getDetailsFlipkart(url):
    html = get_html(url).text
    soup = BeautifulSoup(html, 'lxml')

    name = soup.find('span', class_='VU-ZEz').text
    img = soup.find('img', class_='DByuf4 IZexXJ jLEJ7H')['src']

    specs = []
    parentClass = soup.find('div', class_='_3Fm-hO')
    generalSpec = parentClass.find('div', class_='GNDEQ-')

    specKeys = [keys.text for keys in generalSpec.findAll('td', class_='+fFi1w col col-3-12')]
    specValues = [values.text for values in generalSpec.findAll('li', class_='HPETK2')]
    
    for i in range(min(len(specKeys), len(specValues))):
        specs.append([specKeys[i], specValues[i]])
    
    return [name, img, specs]


def isGoodUrl(url):
    '''if len(url) > 24 and url[:22] == "https://www.amazon.in/" and '/dp/' in url:
        html = get_html(url).text
        soup = BeautifulSoup(html, 'lxml')
        title = soup.find('title')
        if title.text != '404 - Document Not Found':
            return True
    return False'''

    if len(url) > 26 and url[:22] == "https://www.amazon.in/" and "/dp/" in url:
        code = get_html(url).status_code
        if code == 200:
            return True

    elif len(url) > 29 and url[:24] == "https://www.flipkart.com" and "?pid=" in url:
        html = get_html(url)
        code = html.status_code
        page = html.text
        soup = BeautifulSoup(page, 'lxml')
        title = soup.find('title')
        # need title beacause bad sites like "https://www.flipkart.com/?pid=MONG8D5AEYJ6NE7E" and "https://www.flipkart.com/?pid=MONG8D5AEYJ6NE7E&lid=LSTMONG8D5AEYJ6NE7ELRX8BM&marketplace=FLIPKART&store=6bo%2Fg0i%2F9no&srno=b_1_1&otracker=browse&otracker1=hp_rich_navigation_PINNED_neo%2Fmerchandising_NA_NAV_EXPANDABLE_navigationCard_cc_3_L2_view-all&fm=organic&iid=en_EeyQthT8s4rga1nMEfsYHFJUK0cBgo9Q4DTTudWRozQD76DB9IWw30Gdpb6fUfDIO5qUgL8Wh0LKpV5sbJIemg%3D%3D&ppt=hp&ppn=homepage&ssid=tu5cyghar40000001745942065736" can redirect to "flipkart.com"
        mainPageTitle1 = "Buy Products Online at Best Price in India - All Categories | Flipkart.com"
        mainPageTitle2 = "Online Shopping Site for Mobiles, Electronics, Furniture, Grocery, Lifestyle, Books & More. Best Offers!"
        if code == 200 and title.text != mainPageTitle2 and title.text != mainPageTitle1:
            return True

    return False
