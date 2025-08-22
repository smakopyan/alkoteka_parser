import scrapy
import json
import time
import re
from urllib.parse import urlparse
from alkoteka_parser.items import ProductItem

class AlkotekaSpider(scrapy.Spider):
    name = 'alkoteka'
    allowed_domains = ['alkoteka.com']
    
    START_URLS = [
        "https://alkoteka.com/catalog/slaboalkogolnye-napitki-2",
        "https://alkoteka.com/catalog/vino",
        "https://alkoteka.com/catalog/krepkiy-alkogol"
    ]
    
    CITY_UUID = '396df2b5-7b2b-11eb-80cd-00155d039009'
    
    custom_settings = {
        'DOWNLOAD_DELAY': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'RETRY_TIMES': 3,
        'ROBOTSTXT_OBEY': False,
    }

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://alkoteka.com/',
            'X-Requested-With': 'XMLHttpRequest',
        }
        
        csrf_url = f'https://alkoteka.com/web-api/v1/csrf-cookie?city_uuid={self.CITY_UUID}'
        yield scrapy.Request(csrf_url, headers=headers, callback=self.parse_csrf)

    def parse_csrf(self, response):
        csrf_token = response.headers.get('Set-Cookie', b'').decode()
        token_match = re.search(r'XSRF-TOKEN=([^;]+)', csrf_token)
        if token_match:
            csrf_token = token_match.group(1)
        else:
            csrf_token = ''

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Referer': 'https://alkoteka.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'X-XSRF-TOKEN': csrf_token,
        }

        for url in self.START_URLS:
            parsed_url = urlparse(url)
            slug = parsed_url.path.split('/')[-1]
            
            api_url = f'https://alkoteka.com/web-api/v1/product?city_uuid={self.CITY_UUID}&page=1&per_page=100&root_category_slug={slug}'
            
            yield scrapy.Request(
                api_url, 
                headers=headers,
                callback=self.parse_api, 
                meta={
                    'category': slug, 
                    'page': 1,
                }
            )

    def parse_api(self, response):
        try:
            data = json.loads(response.text)
            if not data.get('success', False):
                self.logger.error('API request was not successful')
                return
        except json.JSONDecodeError:
            self.logger.error('Failed to parse API response')
            return

        products = self.extract_products_from_data(data)
        self.logger.info(f'Found {len(products)} products in category {response.meta["category"]}')
        
        if products and isinstance(products[0], dict):
            self.logger.info(f'First product keys: {list(products[0].keys())}')
        
        for product in products:
            item = self.parse_product(product)
            if item:
                yield item

        current_page = response.meta['page']
        if isinstance(data, dict):
            pagination = data.get('meta', {})
            total_pages = pagination.get('last_page', 1)
            
            if current_page < total_pages:
                next_page = current_page + 1
                category = response.meta['category']
                next_url = f'https://alkoteka.com/web-api/v1/product?city_uuid={self.CITY_UUID}&page={next_page}&per_page=100&root_category_slug={category}'
                yield scrapy.Request(
                    next_url, 
                    headers=response.request.headers,
                    callback=self.parse_api, 
                    meta={
                        'category': category, 
                        'page': next_page,
                    }
                )

    def extract_products_from_data(self, data):
        """Извлекает товары из данных API"""
        products = []
        
        if isinstance(data, dict):
            possible_keys = ['results', 'data', 'products', 'items', 'result', 'content']
            for key in possible_keys:
                if key in data and isinstance(data[key], list):
                    products = data[key]
                    break
            
            if not products and 'data' in data and isinstance(data['data'], dict):
                for key in possible_keys:
                    if key in data['data'] and isinstance(data['data'][key], list):
                        products = data['data'][key]
                        break
        
        elif isinstance(data, list):
            products = data
        
        return products

    def parse_product(self, product_data):
        if not isinstance(product_data, dict):
            return None
            
        item = ProductItem()
        
        item['timestamp'] = int(time.time())
        item['RPC'] = str(product_data.get('id', product_data.get('product_id', '')))
        item['url'] = f"https://alkoteka.com/product/{product_data.get('slug', '')}"
        item['title'] = product_data.get('name', product_data.get('title', ''))
        
        volume = product_data.get('volume')
        color = product_data.get('color')
        if volume:
            item['title'] = f"{item['title']}, {volume} л"
        if color:
            item['title'] = f"{item['title']}, {color}"
        
        item['marketing_tags'] = []
        if product_data.get('is_discount') or product_data.get('has_discount'):
            item['marketing_tags'].append('Скидка')
        if product_data.get('is_new') or product_data.get('new'):
            item['marketing_tags'].append('Новинка')
        if product_data.get('is_popular') or product_data.get('popular'):
            item['marketing_tags'].append('Популярный')
        
        brand = product_data.get('brand', {})
        if isinstance(brand, dict):
            item['brand'] = brand.get('name', brand.get('title', ''))
        else:
            item['brand'] = str(brand)
        
        item['section'] = []
        categories = product_data.get('categories', [])
        for category in categories:
            if isinstance(category, dict):
                category_name = category.get('name', category.get('title', ''))
                if category_name:
                    item['section'].append(category_name)
            elif isinstance(category, str):
                item['section'].append(category)
        
        price_keys = ['price', 'current_price', 'final_price']
        old_price_keys = ['old_price', 'original_price', 'base_price']
        
        price = old_price = 0
        for key in price_keys:
            if key in product_data:
                price = float(product_data[key])
                break
                
        for key in old_price_keys:
            if key in product_data:
                old_price = float(product_data[key])
                break
        
        if old_price == 0:
            old_price = price
            
        sale_tag = ""
        if old_price > price:
            discount = int((old_price - price) / old_price * 100)
            sale_tag = f"Скидка {discount}%"
        
        item['price_data'] = {
            'current': price,
            'original': old_price,
            'sale_tag': sale_tag
        }
        
        stock_keys = ['in_stock', 'available', 'is_available']
        count_keys = ['stock_count', 'quantity', 'count']
        
        in_stock = False
        for key in stock_keys:
            if key in product_data:
                in_stock = bool(product_data[key])
                break
                
        count = 0
        for key in count_keys:
            if key in product_data:
                count = int(product_data[key])
                break
        
        item['stock'] = {
            'in_stock': in_stock,
            'count': count if in_stock else 0
        }
        
        images = []
        image_data = product_data.get('images', [])
        
        for img in image_data:
            if isinstance(img, dict):
                path = img.get('path', img.get('url', img.get('src', '')))
                if path:
                    images.append(path)
            elif isinstance(img, str):
                images.append(img)
        
        if not images:
            for key in ['image', 'image_url', 'main_image']:
                if key in product_data and product_data[key]:
                    images = [product_data[key]]
                    break
        
        item['assets'] = {
            'main_image': images[0] if images else '',
            'set_images': images,
            'view360': [],
            'video': []
        }
        
        metadata = {}
        
        alcohol = product_data.get('alcohol', product_data.get('alcohol_percentage', 0))
        volume = product_data.get('volume', product_data.get('capacity', 0))
        
        metadata['Алкоголь'] = f"{alcohol}%"
        metadata['Объем'] = f"{volume} л"
        
        properties = product_data.get('properties', {})
        if isinstance(properties, dict):
            for key, value in properties.items():
                if value:
                    metadata[key] = str(value)
        
        description = product_data.get('description', product_data.get('desc', ''))
        metadata['__description'] = description
        
        item['metadata'] = metadata
        
        variants = product_data.get('variants', [])
        variant_count = 0
        
        for variant in variants:
            if isinstance(variant, dict):
                if variant.get('color') or variant.get('volume') or variant.get('capacity'):
                    variant_count += 1
        
        item['variants'] = variant_count if variant_count > 0 else 1
        
        return item