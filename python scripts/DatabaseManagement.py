import mysql.connector
import os
from datetime import date
import random
from webScraping import getPriceAmazon, getPriceFlipkart, getDetailsAmazon, getDetailsFlipkart, isGoodUrl
from sendAlerts import sendEmail
from dotenv import load_dotenv

load_dotenv()

db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

db = mysql.connector.connect(host=db_host,
                             user=db_user,
                             password=db_password,
                             database=db_name,
                             buffered=True)


def writeLog(text):
    with open('logs.txt', 'a') as file:
        file.write(f"\n{text}")


def writeRequestLog(text):
    with open('request_log.txt', 'a') as file:
        file.write(f'{text}\n')


def updatePrice():
    totalSuccess = True
    todayDate = date.today()
    cursor = db.cursor()
    query = 'select product_id, product_link from products;'
    cursor.execute(query)
    details = [list(data) for data in cursor]

    writeLog('') # adds a empty line
    writeLog(f'DATE: {todayDate}')

    for product in details:
        url = product[1]
        print(f'TRYING TO GET PRICE OF: {url}')
        try:
            if 'www.amazon.in' in url:
                todaysPrice = getPriceAmazon(url)
            elif 'www.flipkart.com' in url:
                todaysPrice = getPriceFlipkart(url)
            product.append(todaysPrice)
            print("SUCCESS")

        except Exception as error:
            print(f"ERROR IN GETTING PRICE FOR URL: {url}")
            print(error)
        
    for product in details:
        pId = product[0]
        url = product[1]
        if len(product) != 3:
            totalSuccess = False
            print(f"No price for product ID: {pId}, date = {date}")
            writeLog(f"No price for product ID: {pId}, date = {date}")
            continue
        price = product[2]
        query = 'insert into product_prices values(%s, %s, %s)'
        cursor.execute(query, (pId, price, todayDate))
        print(f'Updated price for Product ID: {pId}, price = {price}, date={date}')
        writeLog(f'Updated price for Product ID: {pId}, price = {price}, date={date}')

    if totalSuccess:
        print(f"FULLY UPDATED PRICES FOR ALL PRODUCTS ON {todayDate}")
        writeLog(f"FULLY UPDATED PRICES FOR ALL PRODUCTS ON {todayDate}")
    else:
        print(f"PARTIALLY UPDATED PRICES FOR ALL PRODUCTS ON {todayDate}")
        writeLog(f"PARTIALLY UPDATED PRICES FOR ALL PRODUCTS ON {todayDate}")
    return 1


def getId(url):
    cursor = db.cursor()
    query = 'select product_id from products where product_link=%s;'
    cursor.execute(query, (url,))
    for data in cursor:
        return data[0]


'''def isNewUrl(url):
    cursor = db.cursor()
    query = 'select product_link from products;'
    cursor.execute(query)
    for data in cursor:
        if url == data[0]:
            return False
    return True'''


'''def clipUrl(url):
    dp_index = url.find("/dp/")
    if dp_index != -1:
        end_index = url.find("/", dp_index + 4)
        clipped_url = url[:end_index] if end_index != -1 else url[:]
        return clipped_url
    return url'''


def addNewProductData(url, productDetails):
    cursor = db.cursor()
    pName = productDetails[0]
    pImg = productDetails[1]
    pSpecs = productDetails[2]

    query = 'insert into products(product_link, product_name, img) values(%s, %s, %s);'
    cursor.execute(query, (url, pName, pImg))

    pId = getId(url)
    for spec in pSpecs:
        specKey = spec[0]
        specValue = spec[1]
        query = 'insert into product_specifications values(%s, %s, %s);'
        cursor.execute(query, (pId, specKey, specValue))

    print(f'ADDED PRODUCT: {url}')


def deleteRequestedProduct(link):
    cursor = db.cursor()
    query = 'delete from new_requests where link=%s'
    cursor.execute(query, (link,))


def addRequestedProducts():
    cursor = db.cursor()
    todayDate = date.today()
    query = 'select link from new_requests;'
    cursor.execute(query)

    requests = [data[0] for data in cursor]
    print('ADDING VALID REQUEST FROM NEW REQUESTS')
    
    writeRequestLog('')
    writeRequestLog(f'DATE: {todayDate}')
    for url in requests:
        if isGoodUrl(url):
            if 'www.amazon.in' in url:
                try:
                    details = getDetailsAmazon(url)
                    addNewProductData(url, details)
                    deleteRequestedProduct(url)
                    writeRequestLog(f"ADDED REQUEST OF URL: {url} TO DB SUCCESSFULLY")
                except Exception as error: 
                    print(f"ERROR OCCURED: {url}") 
                    print(error)
                    writeRequestLog(f'ERROR OCCURED IN ADDING PRODUCT WITH URL: {url}')
                               
            elif 'www.flipkart.com' in url:
                try:
                    details = getDetailsFlipkart(url)
                    addNewProductData(url, details)
                    deleteRequestedProduct(url)
                    writeRequestLog(f"ADDED REQUEST OF URL: {url} TO DB SUCCESSFULLY")
                except Exception as error: 
                    print(f"ERROR OCCURED: {url}") 
                    print(error)
                    writeRequestLog(f'ERROR OCCURED IN ADDING PRODUCT WITH URL: {url}')

        else:
            print(f'BAD URL, NOT WITHIN CONSTRAINTS OF GOOD URL: {url}')
            deleteRequestedProduct(url)
            writeRequestLog(f'BAD REQUEST, REMOVED FROM REQUESTED PRODUCTS URL: {url}')

    print('ADDED VALID REQUESTS TO DB')
    return 1


def getLatestPrice(id):
    cursor = db.cursor()
    query = 'SELECT price FROM product_prices WHERE product_id = %s ORDER BY date DESC LIMIT 1;'
    cursor.execute(query, (id,))
    for price in cursor:
        return price[0]


def getNameLink(pId):
    cursor = db.cursor()
    query = 'select product_name, product_link from products where product_id = %s;'
    cursor.execute(query, (pId,))
    for data in cursor:
        return data


def sendAlert():
    cursor = db.cursor()
    query = 'select * from notifications;'
    cursor.execute(query)
    for alert in cursor:
        pId = alert[0]
        email = alert[1]
        alertPrice = alert[2]

        latestPrice = getLatestPrice(pId)
        if latestPrice <= alertPrice:
            name, link = getNameLink(pId)
            sendEmail(email, name, link, alertPrice, latestPrice)
            cursor2 = db.cursor()
            query = 'delete from notifications where product_id = %s and email=%s;'
            cursor2.execute(query, (pId, email))

    db.commit()


if addRequestedProducts() == 1:
    db.commit()
    print("ADDED ALL NEW REQUESTS AND COMMITED")

    if updatePrice() == 1:  
        db.commit()
        print("COMMITED ALL THE CHANGES TO THE DATABASE")
        sendAlert()
        print('SENT EMAILS TO ALL THE VALID ALERTS')

db.close()
