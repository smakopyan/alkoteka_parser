class AlkotekaParserPipeline:
    def process_item(self, item, spider):
        for field in ['marketing_tags', 'section']:
            if field not in item:
                item[field] = []
                
        for field in ['brand', 'title']:
            if field not in item:
                item[field] = ''
                
        if 'price_data' not in item:
            item['price_data'] = {
                'current': 0.0,
                'original': 0.0,
                'sale_tag': ''
            }
            
        if 'stock' not in item:
            item['stock'] = {
                'in_stock': False,
                'count': 0
            }
            
        if 'assets' not in item:
            item['assets'] = {
                'main_image': '',
                'set_images': [],
                'view360': [],
                'video': []
            }
            
        if 'metadata' not in item:
            item['metadata'] = {
                '__description': ''
            }
            
        return item