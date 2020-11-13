# # -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from scrapy import Selector
import time
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from scrapy.crawler import CrawlerProcess
from fake_useragent import UserAgent
import smtplib
from email.message import EmailMessage
import os 
import datetime
import schedule
from scrapy.utils.project import get_project_settings
from apscheduler.schedulers.twisted import TwistedScheduler


class ScrapperSpider(scrapy.Spider):
    name = 'Scrapper'
    allowed_domains = ['www.google.com']
    start_urls = ['http://www.google.com/']
    ua = UserAgent()
    
    custom_settings = {      
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'domains.csv',
        'FEED_EXPORT_ENCODED': 'utf-8'
    }

    def __init__(self):
        self.ua = UserAgent()
        self.options = Options()
        self.options.add_argument("start-maximized")
        self.options.add_argument('--headless')
        # self.options.add_argument("--disable-blink-features")
        # self.options.add_argument("--disable-blink-features=AutomationControlled")
        # self.options.add_argument("--use-fake-ui-for-media-stream")
        self.options.add_argument(
            f'--user-agent={self.ua.chrome}')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(),options=self.options)

    def start_request(self):
        for link in self.start_urls:
            yield scrapy.Request(url=link,callback=self.parse,headers={
                "User-Agent": self.ua.chrome
            })


    def parse(self,response):
        url = 'http://analytics.censis.net/app/test'
        self.driver.get('http://analytics.censis.net/app')
        
        time.sleep(20)
        self.driver.find_element_by_xpath('//input[@name="username"]').send_keys('censisscraper@censis.com')
        self.driver.find_element_by_xpath('//input[@name="password"]').send_keys('Scrap3r!')
        self.driver.find_element_by_xpath('//button[@type="submit"]').click()
        time.sleep(2)
        self.driver.get(url)
        time.sleep(3)
        while True:
            resp = Selector(text=self.driver.page_source)
            if resp.xpath('//table/tbody/tr').get() != None:
                for data in resp.xpath('//table/tbody/tr'):
                    yield{
                        'Service Name': data.xpath('./th[1]/text()').get(),
                        'Url': data.xpath('./th[2]/text()').get(),
                        'Active': data.xpath('./th[3]/text()').get(),
                    }
                self.driver.quit()
                break
                

        date = str(datetime.datetime.now())[:19]
        mail = 'censisscraper@gmail.com'
        password = 'Censis_1000'

        msg = EmailMessage()
        msg['Subject'] = f'data scraped on {date}'
        msg['From'] =  mail
        # add emails to recipient list. 'sample@censis.com, sample2@censis.com'
        msg['To'] = 'matt.henley@censis.com. jim.suruda@censis.com'
        msg.set_content = 'see attachment'

        with open('domains.csv','rb') as file:
            file_data = file.read()
        file.close()
        msg.add_attachment(file_data,maintype='application',subtype='csv',filename='analytics_status.csv')
        print('setting up email')
        s = smtplib.SMTP('smtp.gmail.com', 587)
        print('setting')
        s.ehlo()
        print('ehlo')
        s.starttls()
        print('starttls')
        s.login(mail, password)
        print('login')
        s.send_message(msg)
        print('message sent')
        s.close()
        
        file2 = open('domains.csv', 'w')
        file2.write('')
        file2.close()

    
process = CrawlerProcess(get_project_settings())
scheduler = TwistedScheduler()
# set time interval of email message
scheduler.add_job(process.crawl, 'interval', args=[ScrapperSpider], seconds=3600)
scheduler.start()
process.start(False)        
        