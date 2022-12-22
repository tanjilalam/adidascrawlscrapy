import scrapy
import pandas as pd


class AdidasSpider(scrapy.Spider):
    name = 'adidas'
    allowed_domains = ['shop.adidas.com']
    start_urls = ["https://shop.adidas.jp/item/?gender=mens&page=%d/" % i for i in range(1, 18)]
    PROD = []
    page_number = 1

    def parse(self, response, **kwargs):
        product_urls = response.xpath(
            "//div[@class='articleDisplayCard itemCardArea-cards test-card css-1lhtig4']//a").xpath("@href").extract()
        for url in product_urls:
            self.PROD.append("https://shop.adidas.jp/" + url)

        with open(f"product_url.txt", "w") as f:
            for link in self.PROD:
                f.write(link + "\n")

        # if len(self.PROD) >= 300:
        #     for prod_url in self.PROD:
        #         yield scrapy.Request(url=prod_url, callback=self.parse_details)
