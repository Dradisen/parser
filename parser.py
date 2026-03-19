import asyncio
import httpx
import sqlite3
import time
import json
import fake_useragent
import pandas as pd

from typing import List

"""
Сайт: wildberries.ru
Нужен каталог товаров по поисковому запросу "пальто из натуральной шерсти" в XLSX формате 

Список нужных данных:
• Ссылка на товар [List|dynamic_url+id] - ref_link
• Артикул [List|id] - articul
• Название [List|name] - name
• Цена [List|sizes.0.price.product] - price
• Описание [Detail|description] - description
• Ссылки на изображения через запятую - photos - [не сделал]
• Все характеристики с сохранением их структуры [Detail|group_options] - attributes
• Название селлера [List|brand] - seller
• Ссылка на селлера [List|dynamic_url+brandId] - seller_ref_link
• Размеры товара через запятую [List|sizes.[].name] - sizes
• Остатки по товару (число) [List|totalQuantity??] - stock
• Рейтинг [List|reviewRating] - rating
• Количество отзывов [List|feedbacks] - feedbacks

Отдельным XLSX-файлом сделать из полного каталога выборку товаров с рейтингом не менее 4.5, стоимостью до 10000 и страной производства Россия 
На электронную почту ahapka1@gmail.com пришлите ссылку на Гит с вашим парсером и итоговые XLSX-файлы в письме напишите свои ФИО и контактный номер телефона!
ТЗ выполненные нейронкой автоматически отклоняются от рассмотрения. 

"""

class Sqlite:
    
    def __init__(self) -> None:
        self.conn = sqlite3.connect('parsing.sqlite')

    def recreate_table(self):
        self.conn.execute("DROP TABLE IF EXISTS cards").connection.commit()
        self.create_tables()
        
    def create_tables(self):        
        # поле артикул не уникально
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cards (
                id INTEGER PRIMARY KEY,
                articul INTEGER UNIQUE NOT NULL , 
                name TEXT,
                price FLOAT,
                description TEXT,
                photos TEXT,
                attributes TEXT,
                parsed_attributes TEXT,
                seller TEXT,
                seller_ref_link TEXT,
                sizes TEXT,
                stock INTEGER,
                rating FLOAT,
                feedbacks INTEGER
            )
        """).connection.commit()
    

    def select(self):
        return self.conn.execute("SELECT * FROM cards").fetchall()
    
    def select_unready_parse_rows(self):
        return self.conn.cursor().execute("SELECT * FROM cards WHERE description = 'None'").fetchall()
        
    
class WildBerriesParser:
    # https://habr.com/ru/companies/wildberries/articles/967988/
    LIST_PARSE_URL = 'https://search.wb.ru/exactmatch/ru/common/v4/search'
    
    def __init__(self, db: Sqlite) -> None:
        self.db = db
        self.q = ""    
    
    def params(self, query: str, page: int = 1):
        return {
            "appType": 1, # судя по всему формат отображения приложения
            "curr": "rub",
            "dest": "-1257786", # Критичный параметр. Этот параметр указывает какой-то склад или нав.позицию. От этого зависит выдача
            "land": "ru",
            "query": query,
            "resultset": "catalog",
            "sort": "popular",
            "spp": 30,
            "page": page,
        }
    
    @property
    def headers(self):
        agent = fake_useragent.UserAgent()
        return {
            "User-Agent": agent.random,
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Headers":"Authorization,Accept,Origin,DNT,User-Agent,Content-Type,Wb-AppType,Wb-AppVersion,Xwbuid,Site-Locale,X-Clientinfo,Storage-Type,Data-Version,Model-Version,__wbl, x-captcha-id",
            "Access-Control-Allow-Methods":"GET,OPTIONS",
            "Access-control-Allow-Origin":"https://www.wildberries.ru",
            "Content-Encoding":"gzip",
            "Content-Type":"application/json charset=utf-8"
        }
    
    def search(self, q: str):
        self.q = q
        return self
    
    def find_shard(self, articul: str) -> str:
        """Определение шарда"""
        # Долго не вдуплял по какому принципу выбирается шард, чтобы получить картинки и детальную карточку.
        # Нашел статью https://habr.com/ru/companies/wildberries/articles/967988/
        # Этот код я разрыл из скрипта JS на сайте
        vol = int(articul) // 100000
        if vol <= 143:
            s = "01"
        elif vol <= 287:
            s = "02"
        elif vol <= 431:
            s = "03"
        elif vol <= 719:
            s = "04"
        elif vol <= 1007:
            s = "05"
        elif vol <= 1061:
            s = "06"
        elif vol <= 1115:
            s = "07"
        elif vol <= 1169:
            s = "08"
        elif vol <= 1313:
            s = "09"
        elif vol <= 1601:
            s = "10"
        elif vol <= 1655:
            s = "11"
        elif vol <= 1919:
            s = "12"
        elif vol <= 2045:
            s = "13"
        elif vol <= 2189:
            s = "14"
        elif vol <= 2405:
            s = "15"
        elif vol <= 2621:
            s = "16"
        elif vol <= 2837:
            s = "17"
        elif vol <= 3053:
            s = "18"
        elif vol <= 3269:
            s = "19"
        elif vol <= 3485:
            s = "20"
        elif vol <= 3701:
            s = "21"
        elif vol <= 3917:
            s = "22"
        elif vol <= 4133:
            s = "23"
        elif vol <= 4349:
            s = "24"
        elif vol <= 4565:
            s = "25"
        elif vol <= 4877:
            s = "26"
        elif vol <= 5189:
            s = "27"
        elif vol <= 5501:
            s = "28"
        elif vol <= 5813:
            s = "29"
        elif vol <= 6125:
            s = "30"
        elif vol <= 6437:
            s = "31"
        elif vol <= 6749:
            s = "32"
        elif vol <= 7061:
            s = "33"
        elif vol <= 7373:
            s = "34"
        elif vol <= 7685:
            s = "35"
        elif vol <= 7997:
            s = "36"
        elif vol <= 8309:
            s = "37"
        elif vol <= 8741:
            s = "38"
        elif vol <= 9173:
            s = "39"
        elif vol <= 9605:
            s = "40"
        else:
            s = "41"
        return s
    
    def insert_cards(self, data_list: list[dict]):
        """Делает вставку в поля"""
        stmt = "INSERT or IGNORE INTO cards (articul, name, price, description, photos, attributes, \
            seller, seller_ref_link, sizes, stock, rating, feedbacks) VALUES "
        for i in data_list:
            stmt += f'\
                ({i.get("articul")}, "{i.get("name")}", {i.get("price")}, "{i.get("description")}",\
                "{i.get("photos")}", "{i.get("attributes")}", "{i.get("seller")}", "{i.get("seller_ref_link")}", \
                "{i.get("sizes")}", {i.get("stock")}, {i.get("rating")}, {i.get("feedbacks")}),'
        stmt = stmt[:-1] + ";"
        self.db.conn.execute(stmt).connection.commit()
        
    def update_card(self, articul: str, description: str, attributes: List[dict]):
        """Обновляет описание и атрибуты карточки по артикулу"""
        parsed_attributes = ' -/- '.join([f"{attr['name']}={attr['value']}" for attr in attributes])
        stmt = f"UPDATE cards SET description = '{description}', \
            parsed_attributes = '{parsed_attributes}', \
            attributes = '{json.dumps(attributes, ensure_ascii=False)}'\
            WHERE articul = '{articul}';"
        self.db.conn.execute(stmt).connection.commit()
    
    def update_photo(self, articul: str, photos: List[str]):
        """Обновляет фотографии карточки по артикулу"""
        join_photos = ";".join(photos)
        stmt = f"UPDATE cards SET photos = '{join_photos}' WHERE articul = '{articul}';"
        self.db.conn.execute(stmt).connection.commit()
    
    # def extract_detail(self, result: dict):
    #     """Извлечение основных данных из списка"""
    #     return {
    #         "description": result.get("feedbacks"),
    #         "attributes": result.get("group_options"),
    #         "parsed_attributes": ';'.join([result.get("group_options")])
    #     }
    
    def extract_rows(self, result: list[dict]):
        """Извлечение основных данных из списка"""
        for row in result:
            yield {
                "ref_link": f"https://www.wildberries.ru/catalog/{row.get('id')}/detail.aspx",
                "articul": row.get("id"),
                "name": row.get("name"),
                "price": int(row.get("sizes", [{}])[0].get("price", {}).get("product", 0))/100,
                "description": row.get("description"),
                "seller": row.get("brand"),
                "sizes": ",".join([size.get("origName", '') for size in row.get("sizes", [])]),
                "seller_ref_link": f"https://www.wildberries.ru/brands/{row.get('brandId')}",
                "stock": row.get("totalQuantity"),
                "rating": row.get("reviewRating"),
                "feedbacks": row.get("feedbacks")
            }
    
    async def fetch_detail(self, url: str, articul: str):
        """Детальный запрос карточки по артикулу"""
        # https://card.wb.ru/cards/v4/detail?appType=1&curr=rub&dest=-1257786&lang=ru&nm={id}
        async with httpx.AsyncClient() as client:
            return await client.get(
                url,
                params=dict(
                    appType=1,
                    curr='rub',
                    dest='-1257786',
                    lang='ru',
                    nm=articul
                ),
                headers=self.headers,
            )
    
    async def fetch_photos(self, url: str, articul: str):
        """Загрузка фото по артикулу"""
        print(f"|-- Fetch Photo [{url}]: articul=[{articul}]")
        async with httpx.AsyncClient() as client:
            return await client.get(
                url,
                params=dict(
                    appType=1,
                    curr='rub',
                    dest='-1257786',
                    lang='ru',
                    nm=articul
                ),
                headers=self.headers,
            )
            
            
    def fetch_list(self, page: int=1):
        return httpx.get(
            self.LIST_PARSE_URL,
            params=self.params(self.q, page),
            headers=self.headers,
        )
  
    def get_list(self, page: int = 1, retry: int = 10) -> bool:
        """Загрузка списка товаров. Возвращает False, если товаров больше нет или при неуспешных попытках"""
        while retry > 0:
            try:
                print(f"|- List [{self.LIST_PARSE_URL}]: page=[{page}] Запрос...")
                response = self.fetch_list(page)
                print(f"|- List [{self.LIST_PARSE_URL}]: page=[{page}] Успешно")
            except httpx.ReadTimeout:
                print(f"|- List [{self.LIST_PARSE_URL}]: Таймаут...")
                time.sleep(1)
                retry -= 1
                continue

            if response.status_code != 200:
                print(f"|- List [{self.LIST_PARSE_URL}]: Ошибка статуса: {response.status_code}. Повтор...")
                time.sleep(1)
                retry -= 1
                continue

            data = response.json()
            products = data.get('products', [])
            data_len_list = len(products)

            if not data_len_list:
                print("Продуктов не найдено")
                return False

            self.insert_cards(list(self.extract_rows(products)))
            return True

        return False
    
    async def binary_load_detail_photo(self, articul: str, size: int=60) -> List[str]:
        """
        Загрузка фото по бинарному поиску. Возвращает список ссылок на фото.
        """
        # Поскольку фото по циклу проверять много, как и кол-во запросов, оптимизируем его по бинарному поиску. 
        # Предполагается, что от успешного запроса - все предыдущие фото по индексу существуют, 
        # а при неуспешном - все последующие не существуют.
        
        base_url = self.extract_base_url_from_articul(articul)
        
        index = size // 2
        step = index // 2
        
        while step > 0:
            await asyncio.sleep(1)
            url = f"{base_url}/images/c246x328/{index}.webp"
            try:
                response = await self.fetch_photos(url, articul)
            except (httpx.ReadTimeout, httpx.ConnectTimeout):
                print(f"|-- Photo [{url}]: articul=[{articul}] Таймаут...")
                await asyncio.sleep(1)
                continue
            
            if response.status_code != 200:
                index -= step
                step //= 2
            elif response.status_code == 200:
                index += step
                step //= 2
        return [f"{base_url}/images/big/{i}.webp" for i in range(1, index)]

    def extract_base_url_from_articul(self, articul: str) -> str:
        """Возвращает шард-URL ссылку по артикулу"""
        shard_id = self.find_shard(articul)
        vol = int(articul) // 100000
        part = int(articul) // 1000
        return f"https://basket-{shard_id}.wbbasket.ru/vol{vol}/part{part}/{articul}"
        
        
    async def get_detail(self, articul: str, retry: int = 30) -> bool:
        """Получает детальную информацию по артикулу из запроса"""
        await asyncio.sleep(1)
        url =  self.extract_base_url_from_articul(articul) + '/info/ru/card.json'

        while retry > 0:
            try:
                print(f"|- Detail [{url}]: articul=[{articul}]")
                response = await self.fetch_detail(url, articul)
            except (httpx.ReadTimeout, httpx.ConnectTimeout):
                print(f"|-- Detail [{url}]: articul=[{articul}] Таймаут...")
                await asyncio.sleep(1)
                retry -= 1
                continue
            
            if response.status_code != 200:
                print(f"Ошибка кода: {response.status_code}")
                await asyncio.sleep(1)
                retry -= 1
                continue

            product = response.json()

            if not product:
                print("Продукт не найден, стоп")
                return False
            
            result = await self.binary_load_detail_photo(articul=articul)
            self.update_photo(articul, result)
            self.update_card(
                articul=articul, 
                description=product.get('description', ''), 
                attributes=product.get('options', [])
            )
            return True        
        return False
    
    async def load_details_from_list(self):
        """Загрузка детальной информации для всех товаров из списка"""
        # Ограничение на 10 запросов, чтобы не наглеть и не забанили :)
        sem = asyncio.Semaphore(10)
        async def run_detail(articul: str):
            async with sem:
                return await self.get_detail(articul=articul)
        # row[1] - артикул товара
        await asyncio.gather(*[run_detail(articul=row[1]) for row in self.db.select_unready_parse_rows()])
    
    def load_list(self):
        """Синхронная загрузка списка товаров"""
        page = 1
        while True:
            has_more = self.get_list(page=page)
            if not has_more:
                break
            page += 1
    
    async def start(self):
        """Запуск задачи"""
        self.load_list()
        await self.load_details_from_list()
        

async def main():
    sqlite = Sqlite()
    sqlite.recreate_table()
    # db - предполагается, что можно выбрать любую реализацию БД, я выбрал sqlite для простоты. 
    # В целом можно было бы сделать абстрактный класс и реализовать его для разных БД.
    parser = WildBerriesParser(db=sqlite)
    await parser.search('пальто из натуральной шерсти').start()


def export_main_xlsx():
    """
    Нужен каталог товаров по поисковому запросу "пальто из натуральной шерсти" в XLSX формате 
    """
    conn = sqlite3.connect("parsing.sqlite")
    df = pd.read_sql_query("SELECT * FROM cards", conn)
    # По хорошему необходимо выровнять колонки
    df.to_excel("list.xlsx", index=False)
    

def export_filter_xlsx():
    """
    Отдельным XLSX-файлом сделать из полного каталога выборку 
    товаров с рейтингом не менее 4.5, стоимостью до 10000 и 
    страной производства Россия
    """
    conn = sqlite3.connect("parsing.sqlite")
    df = pd.read_sql_query("SELECT * from cards WHERE \
        rating >= 4.5 AND \
        price <= 10000 AND \
        parsed_attributes LIKE '%Страна производства=Россия%'", conn)
    # По хорошему необходимо выровнять колонки
    df.to_excel("list_filter.xlsx", index=False)
            
            
if __name__ == "__main__":
    # В целом написал как есть, сдаю MVP (парсинг данных). Поскольку времени у меня на тестовые ограничено, написал так.
    # Есть вещи, где можно улучшить код (
        # асинхронно загружать запрос на список, 
        # более детально разделить функции, 
        # улучшить класс с бд, 
        # создать сериализаторы из pydantic для точной валидации данных,
        # обработка ошибок
        # В запросе на список собирать только артикулы (id), а в детальной уже собирать всю информацию
        # и тд
    # )
        
    # Добавил семафоры, чтобы не забанили меня и ограничить кол-во запросов. как и время.
    
    # Основной затык оказался в том, что существовали shard-ссылки на детальную информацию и фото,
    # поэтому пришлось попотеть и потратил приличное кол-во времени.
    asyncio.run(main())
    export_main_xlsx()
    export_filter_xlsx()

            
# ===========================================Для анализа========================================================

# Результат списка
"""
[{
    "id": 332407348, - идентификатор продукта (необходим для парсинга детальной информации)
    "time1": 2,
    "time2": 25,
    "wh": 206348,
    "dtype": 6597069766664,
    "dist": 203,
    "root": 191397934,
    "kindId": 1,
    "brand": "Красный ананас",
    "brandId": 310841848,
    "siteBrandId": 0,
    "colors": [
        {
            "name": "черный",
            "id": 0
        }
    ],
    "subjectId": 170,
    "subjectParentId": 1,
    "name": "Пальто воротник стойка",
    "entity": "пальто",
    "matchId": 173888227,
    "supplier": "Красный ананас",
    "supplierId": 1316722,
    "supplierRating": 4.8,
    "supplierFlags": 12224,
    "pics": 14,
    "rating": 5,
    "reviewRating": 4.8,
    "nmReviewRating": 4.8,
    "feedbacks": 2390,
    "nmFeedbacks": 2390,
    "panelPromoId": 1025110,
    "volume": 160,
    "weight": 1.427,
    "viewFlags": 8590459024,
    "sizes": [
        {
            "name": "176-182/54 рф",
            "origName": "56",
            "rank": 1007691,
            "optionId": 497099339,
            "wh": 206348,
            "time1": 2,
            "time2": 25,
            "dtype": 6597069766664,
            "price": {
                "basic": 2744200,
                "product": 1335000,
                "logistics": 0,
                "return": 0
            },
            "saleConditions": 402653184,
            "payload": "A2gp60ehoaLOBI9Ec60HISWi7Nt2nV7bPoravac4aOAfLaFDFBbUhm8R6MkmQgj82263i3IgPSQaxuuOwX5JD5x85EZb+IO8HaSMmSvEO3caPi7VkZe8JZNhQKvARTr1nm5LTKCa48IrtLUbSUcDyNA6jJquhzc7qOR1DvEiVbfOp6ks/ZP/6qHrk26aY4gHAcWE4Sbyhp53MWym4QAfsZJwAvATuScqIE5stfaOXXaLz7jDDes0lw"
        }
    ],
    "totalQuantity": 2,
    "meta": {
        "tokens": [],
        "presetId": 200703090
    }
}]

"""

# Результат детальной информации
"""
{
    "imt_id": 361904004,
    "nm_id": 287700029,
    "imt_name": "Пальто шерстяное натуральное",
    "slug": "palto-sherstyanoe-naturalnoe",
    "subj_name": "Пальто",
    "subj_root_name": "Одежда",
    "vendor_code": "4412726",
    "season": "демисезон",
    "kinds": [
        "Женский"
    ],
    "description": "Черное пальто женское французского бренда Maison David. Состав: 100% шерсть натуральная. Шерсть отлично согревает, при этом позволяет телу дышать, не создавая парникового эффекта. В шерстяных вещах тепло, но не жарко. Одежда из шерсти — идеальный выбор для зимы и холодного демисезона. Состав подкладки: полиэстер, вискоза.\n\nВерхняя одежда имеет прямой силуэт. Модель отличает отложной воротник и наличие прорезных карманов. Температурный режим от плюс 5 до минус 10.\n\nУхаживайте за вещью правильно, чтобы она дольше служила и радовала вас. Правила по уходу указаны на вшивном ярлычке изделия. Разрешено: химчистка. Запрещено: стирка, отбеливание, глажка, барабанная сушка.\n\nПальто в стиле кэжуал — удачное дополнение повседневного гардероба. Одежда в стиле кэжуал станет частью ваших комфортных образов на каждый день для работы и отдыха. Maison David — дом современной элегантности. Бренд отражает идею французского bon chic, bon genre: искусство быть безупречным без усилий, сочетая гармонию интеллекта и формы, а качество становится главным языком красоты. Бренд соединяет современные тенденции с классическими формами, сохраняя баланс между актуальностью и вечностью. Каждая вещь Maison David создается, чтобы жить долго — сопровождать своего владельца в реальной, настоящей жизни: в работе, в путешествиях, в личных историях. Это не просто гардероб, а состояние уравновешенности и эстетического покоя.",
    "options": [
        {
            "name": "Состав",
            "value": "шерсть натуральная 100%",
            "charc_type": 1
        },
        {
            "name": "Цвет",
            "value": "черный",
            "is_variable": true,
            "charc_type": 1,
            "variable_value_IDs": [
                13600062
            ],
            "variable_values": [
                "черный"
            ]
        },
        {
            "name": "Пол",
            "value": "Женский",
            "charc_type": 1
        },
        {
            "name": "Сезон",
            "value": "демисезон",
            "charc_type": 1
        },
        {
            "name": "Рост модели на фото",
            "value": "175 см",
            "charc_type": 4
        },
        {
            "name": "Температурный режим",
            "value": "от +5 °C до -10 °C",
            "charc_type": 1
        },
        {
            "name": "Покрой",
            "value": "прямой",
            "charc_type": 1
        },
        {
            "name": "Тип карманов",
            "value": "прорезные",
            "charc_type": 1
        },
        {
            "name": "Тип рукава",
            "value": "длинные",
            "charc_type": 1
        },
        {
            "name": "Особенности модели",
            "value": "Без капюшона, теплый",
            "charc_type": 1
        },
        {
            "name": "Уход за вещами",
            "value": "Химическая стирка; стирка запрещена; отбеливание запрещено",
            "charc_type": 1
        },
        {
            "name": "Комплектация",
            "value": "1 шт",
            "charc_type": 1
        },
        {
            "name": "Страна производства",
            "value": "Россия",
            "charc_type": 1
        }
    ],
    "compositions": [
        {
            "name": "шерсть натуральная 100%"
        }
    ],
    "sizes_table": {
        "details_props": [
            "RU",
            "Обхват бедер, в см",
            "Обхват талии, в см",
            "Обхват груди, в см"
        ],
        "values": [
            {
                "tech_size": "XS",
                "chrt_id": 439778161,
                "details": [
                    "42",
                    "90-94",
                    "62-66",
                    "82-86"
                ]
            },
            {
                "tech_size": "S",
                "chrt_id": 439778162,
                "details": [
                    "44",
                    "94-98",
                    "66-70",
                    "86-90"
                ]
            },
            {
                "tech_size": "M",
                "chrt_id": 439778163,
                "details": [
                    "46",
                    "98-102",
                    "70-74",
                    "90-94"
                ]
            },
            {
                "tech_size": "L",
                "chrt_id": 439778164,
                "details": [
                    "48",
                    "102-106",
                    "74-78",
                    "94-98"
                ]
            },
            {
                "tech_size": "XL",
                "chrt_id": 1018533512,
                "details": [
                    "50",
                    "106-110",
                    "78-82",
                    "98-102"
                ]
            },
            {
                "tech_size": "XXL",
                "chrt_id": 1018533513,
                "details": [
                    "52",
                    "110-114",
                    "82-86",
                    "102-106"
                ]
            }
        ]
    },
    "certificate": {},
    "nm_colors_names": "черный",
    "colors": [
        348433484,
        370477912,
        346967629,
        287700029,
        309779961,
        312616259,
        320728097,
        320728091,
        320728084,
        333388543,
        346320940
    ],
    "contents": "1 шт",
    "full_colors": [
        {
            "nm_id": 348433484
        },
        {
            "nm_id": 370477912
        },
        {
            "nm_id": 346967629
        },
        {
            "nm_id": 287700029
        },
        {
            "nm_id": 309779961
        },
        {
            "nm_id": 312616259
        },
        {
            "nm_id": 320728097
        },
        {
            "nm_id": 320728091
        },
        {
            "nm_id": 320728084
        },
        {
            "nm_id": 333388543
        },
        {
            "nm_id": 346320940
        }
    ],
    "selling": {
        "brand_name": "MAISON DAVID",
        "brand_hash": "74D276D603DADCF9",
        "supplier_id": 528630
    },
    "media": {
        "has_video": true,
        "photo_count": 5
    },
    "data": {
        "subject_id": 170,
        "subject_root_id": 1,
        "chrt_ids": [
            439778161,
            439778162,
            439778163,
            439778164,
            1018533512,
            1018533513
        ]
    },
    "grouped_options": [
        {
            "group_name": "Основная информация",
            "options": [
                {
                    "name": "Состав",
                    "value": "шерсть натуральная 100%",
                    "charc_type": 1
                },
                {
                    "name": "Цвет",
                    "value": "черный",
                    "is_variable": true,
                    "charc_type": 1,
                    "variable_value_IDs": [
                        13600062
                    ],
                    "variable_values": [
                        "черный"
                    ]
                },
                {
                    "name": "Пол",
                    "value": "Женский",
                    "charc_type": 1
                }
            ]
        },
        {
            "group_name": "Дополнительная информация",
            "options": [
                {
                    "name": "Сезон",
                    "value": "демисезон",
                    "charc_type": 1
                },
                {
                    "name": "Рост модели на фото",
                    "value": "175 см",
                    "charc_type": 4
                },
                {
                    "name": "Температурный режим",
                    "value": "от +5 °C до -10 °C",
                    "charc_type": 1
                },
                {
                    "name": "Покрой",
                    "value": "прямой",
                    "charc_type": 1
                },
                {
                    "name": "Тип карманов",
                    "value": "прорезные",
                    "charc_type": 1
                },
                {
                    "name": "Тип рукава",
                    "value": "длинные",
                    "charc_type": 1
                },
                {
                    "name": "Особенности модели",
                    "value": "Без капюшона, теплый",
                    "charc_type": 1
                },
                {
                    "name": "Уход за вещами",
                    "value": "Химическая стирка; стирка запрещена; отбеливание запрещено",
                    "charc_type": 1
                },
                {
                    "name": "Комплектация",
                    "value": "1 шт",
                    "charc_type": 1
                },
                {
                    "name": "Страна производства",
                    "value": "Россия",
                    "charc_type": 1
                }
            ]
        }
    ],
    "update_date": "2026-03-05T14:41:40.836797Z",
    "create_date": "2024-11-20T07:37:58.269761Z",
    "need_kiz": true,
    "user_flags": 0
}
"""