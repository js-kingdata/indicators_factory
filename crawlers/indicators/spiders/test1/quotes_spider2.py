import scrapy
from jinja2 import Template


class QuotesSpider(scrapy.Spider):
    name = "quotes3"

    def start_requests(self):
        urls = [
            'https://quotes.toscrape.com/page/1/',
            'https://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        params = {
            'exchange_name': 'OKX',
        }
        print(Template(self.alert_en_template()).render(exchange_name='OKX'))
        print(Template(self.alert_cn_template()).render(params))

    # must be declare
    def alert_en_template(self):
        return """
             According to KingData monitoring, {{ exchange_name }}
          """

        # must be declare

    def alert_cn_template(self):
        return """
          据 KingData 监控，{{exchange_name}} 
      """