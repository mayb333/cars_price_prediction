import requests
import csv
import math
import time
import random
from bs4 import BeautifulSoup


params = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,\
                application/signed-exchange;v=b3;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) \
                    Chrome/104.0.0.0 Safari/537.36'
}


def get_models_links():
    url = 'https://auto.drom.ru/kia/?grouping=1'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')

    models = []
    models_html = soup.find_all('a', class_='css-nox51k e13zubtn5')
    for model in models_html:
        link = model['href']
        quantity = ''.join(model.find(class_='css-1hrfta1 e162wx9x0').text.strip().split()[:-1])
        if int(quantity) > 2000:
            pages = 101
        else:
            pages = math.ceil(int(quantity) / 20) + 1

        item = [link, pages]
        models.append(item)
    return models


def parse_to_csv(models):
    #I could've done 2 functions (get_data, dump_to_csv), but in order to not lose the parsed data in case of a error
    #I combined 2 functions in one
    with open('data.csv', 'w') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(('name', 'year', 'price', 'place', 'liters', 'engine_type', 'transmission_type',
                         'drivetrain_type', 'mileage', 'car_is_new', 'normal_price', 'high_price', 'no_eval_price'))

    all_pages = 0
    for model in models:
        pages = model[1]
        all_pages += pages

    amount = 0
    for model in models:
        raw_link, pages = model[0], model[1]

        for i in range(1, pages):
            url = raw_link + f'page{i}/'

            response = requests.get(url=url, params=params)
            soup = BeautifulSoup(response.text, 'lxml')

            cars_on_page = soup.find_all(class_='css-xb5nz8 e1huvdhj1')

            for car in cars_on_page:
                try:
                    name_and_year = car.find('div', class_='css-13ocj84 e1icyw250').\
                        find('div', class_='css-17lk78h e3f4v4l2').find('span').text
                except Exception:
                    continue
                try:
                    name, year = name_and_year.split(',')[0], name_and_year.split(',')[1]
                except Exception:
                    name = name_and_year
                    year = ''

                info_html = car.find('div', class_='css-1fe6w6s e162wx9x0').find_all('span', class_='css-1l9tp44 e162wx9x0')
                car_info = [item.text for item in info_html]

                try:
                    flag = car.find('div', class_='css-xbntwf eha7c1r0').find(class_='css-cxiuxk ejipaoe0').text
                    car_is_new = '1'
                except Exception:
                    car_is_new = '0'

                try:
                    liters = car_info[0]
                    engine_type = car_info[1]
                    transmission_type = car_info[2]
                    drivetrain_type = car_info[3]
                except Exception:
                    continue

                try:
                    mileage = car_info[4]
                except Exception:
                    mileage = '0'

                price_html = car.find('div', class_='css-1dkhqyq e1f2m3x80').find('span', class_='css-46itwz e162wx9x0').\
                    find('span').text
                price = ''.join(price_html.split())

                try:
                    price_eval_2 = car.find('div', class_='css-b9bhjf ejipaoe0').text
                    normal_price = '1'
                except Exception:
                    normal_price = '0'

                try:
                    price_eval_2 = car.find('div', class_='css-16vzcmq ejipaoe0').text
                    high_price = '1'
                except Exception:
                    high_price = '0'

                try:
                    price_eval_3 = car.find('div', class_='css-9rcimf ejipaoe0').text
                    no_eval_price = '1'
                except Exception:
                    no_eval_price = '0'

                try:
                    place = car.find('div', class_='css-1x4jcds eotelyr0').find(class_='css-1488ad e162wx9x0').text
                except Exception:
                    place = ''

                #Collect the data together
                item = [name, year, price, place, liters, engine_type, transmission_type, drivetrain_type, mileage,
                        car_is_new, normal_price, high_price, no_eval_price]

                with open('data.csv', 'a') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(item)

            print(f'[PROCESS] {url} IS DONE')
            amount += 1
            if amount % 10 == 0:
                print(f'[INFO] {"%.2f" % ((amount / all_pages) * 100)} % ')

            if i % 2 == 0:
                time.sleep(random.randint(2, 4))


def main():
    models = get_models_links()
    print(models)
    parse_to_csv(models=models)


if __name__ == '__main__':
    main()