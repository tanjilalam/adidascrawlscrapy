import time
import scrapy
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


with open("product_url.txt") as f:
    content_list = f.readlines()
CONTENTS = [x.strip() for x in content_list]
url_list = []
name_list = []
breadcrumb_lists = []
pricing_list = []
category_list = []
image_url_lists = []
available_sizes_lists = []
sense_of_sizes_lists = []
coordinates_item_urls_lists = []
title_description_lists = []
general_description_lists = []
general_description_item_lists = []
all_size_table_lists = []


def get_driver():
    options = Options()
    # options.add_argument('--headless')
    options.add_argument("--start-maximized")
    options.add_argument('--blink-settings=imagesEnabled=false')
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    return driver


class AdidasSpider(scrapy.Spider):
    name = 'details'
    allowed_domains = ['shop.adidas.com']
    start_urls = [i for i in CONTENTS]

    def parse(self, response, **kwargs):
        # breadcrumb data
        breadcrumb_list = []
        breadcrumb_links = response.xpath("//div[@class='breadcrumb_wrap']//ul//li//a/text()").extract()
        for link in breadcrumb_links:
            breadcrumb_list.append(link)

        # category data
        category = response.xpath('//a[@class="groupName"]//span/text()').extract()

        # product name data
        product_name = response.xpath('//h1[@class="itemTitle test-itemTitle"]/text()').extract()


        # pricing data
        pricing = response.xpath('//span[@class="price-value test-price-value"]/text()').extract()

        # image url
        image_url_list = []
        image_urls = response.xpath('//ul[@class="slider-list test-slider-list"]//img').xpath("@src").extract()
        for image_url in image_urls:
            image_url_list.append("https://shop.adidas.jp"+image_url)

        # available sizes
        available_sizes = []
        available_prod_sizes = response.xpath('//div[@class="test-sizeSelector css-958jrr"]//ul//li//button/text()').extract()
        for available_size in available_prod_sizes:
            available_sizes.append(available_size.strip())

        # sense of sizes
        sense_of_sizes = []
        sense_of_prod_size = response.xpath('//div[@class="sizeFitBar css-zrdet1"]//span/text()').extract()
        for sense_size in sense_of_prod_size:
            sense_of_sizes.append(sense_size.strip())

        # coordinate
        # try:
        #     coordinates_item_urls = []
        #     coordinate_items = response.xpath('//*[@class="coordinateItems css-jhef4r"]//ul//li').extract()
        #     for coordinates_item in coordinate_items:
        #         coordinates_item.click()
        #         coordinates_url = response.xpath('//*[@class="coordinate_item_container test-coordinate_item_container add-open"]//a').xpath("@href").extract()
        #         coordinates_item_urls.append(coordinates_url)
        # except:
        #     coordinates_item_urls.append("none")

        # description title
        title_description = response.xpath('//h4[@class="itemFeature heading test-commentItem-subheading"]/text()').extract()

        # general description
        general_description = response.xpath('//div[@class="details description_part test-itemComment-descriptionPart"]//div/text()').extract()

        general_description_item_list = []
        general_item_description = response.xpath('//ul[@class="articleFeatures description_part css-woei2r"]//li/text()').extract()
        for general_item_des in general_item_description:
            general_description_item_list.append(general_item_des)
        # get size table data

        # -----------------------------------

        driver = get_driver()
        driver.get(response.url)
        driver.execute_script("window.scrollBy(0, arguments[0]);", 950)
        driver.implicitly_wait(10)

        # all the sizes
        all_size_list = []
        all_the_sizes = driver.find_elements(By.XPATH, '//table[@class="sizeChartTable"]//tbody//tr[1]//td//span')
        for size in all_the_sizes:
            all_size_list.append(size.text.strip())
        all_prod_size_data = driver.find_elements(By.XPATH, '//table[@class="sizeChartTable"]//tbody//tr')

        all_value_zip_list = []
        count = 2
        for i in range(1, len(all_size_list) - 1):
            value_list = []
            for all_size_value in all_prod_size_data:
                value_data_list = all_size_value.find_elements(
                    By.XPATH,
                    f'//table[@class="sizeChartTable"]//tbody//tr[{count}]/td/span'
                )

                for value_data in value_data_list:
                    value_list.append(value_data.text.strip())
            data_zip = dict(zip(all_size_list, value_list))
            all_value_zip_list.append(data_zip)
            value_list.clear()
            count += 1

        size_chart_headers_list = []
        size_chart_headers = driver.find_elements(
            By.XPATH,
            '//div[@class="sizeChart test-sizeChart css-l7ym9o"]//table[@class="sizeChartTable"]//thead//tr//th')

        for size_chart_header in size_chart_headers[1:]:
            size_chart_headers_list.append(size_chart_header.text.strip())

        table_data = dict(zip(size_chart_headers_list, all_value_zip_list))

        url_list.append(response.url)
        breadcrumb_lists.append(breadcrumb_list)
        name_list.append(product_name)
        pricing_list.append(pricing)
        category_list.append(category)
        image_url_lists.append(image_url_list)
        available_sizes_lists.append(available_sizes)
        sense_of_sizes_lists.append(sense_of_sizes)
       # coordinates_item_urls_lists.append(coordinates_item_urls)
        title_description_lists.append(title_description)
        general_description_lists.append(general_description)
        general_description_item_lists.append(general_description_item_list)
        all_size_table_lists.append(table_data)

        df = pd.DataFrame({
            'url_list': url_list,
            'product_name': name_list,
            'breadcrumb_list': breadcrumb_lists,
            'category': category_list,
            'pricing': pricing_list,
            'image_urls': image_url_lists,
            'available_sizes_lists': available_sizes_lists,
            'sense_of_sizes_lists': sense_of_sizes_lists,
          # 'coordinates_item_urls_lists': coordinates_item_urls_lists
            'title_description_lists': title_description_lists,
            'general_description_lists': general_description_lists,
            'general_description_item_lists': general_description_item_lists,
            'all_size_table_lists': all_size_table_lists
        })

        # save in excel
        df.to_excel('scraped_data.xlsx', index=False)

