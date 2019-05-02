# -*- coding: utf-8 -*-
import scrapy
import traceback

import scrapy.signals

from scrapy.xlib.pydispatch import dispatcher
from datetime import datetime

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#pour trouver l'id de l'agence
import re

import stomp
import json

chrome_options = Options()
chrome_options.add_argument("--headless")

service = webdriver.chrome.service.Service(os.path.abspath(r'C:\Users\Oussama\Desktop\agencywebdriver/chromedriver.exe'))
service.start()
driver = webdriver.Remote(service.service_url,   desired_capabilities=chrome_options.to_capabilities())

class SelogerAgencySpider(scrapy.Spider):
    name = 'selogeragencyspider'
    allowed_domains = ['seloger.com']
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 500,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'immoscraping.middlewares.LuminatiProxyMiddleware': 450,


        }
     }

    def spider_closed(self, spider):
        print("spider just become closed")
        self.context[self.urlCorrelationId] = spider.crawler.stats.get_value('log_count/ERROR')


    def spider_idle(self, spider):
        print("spider just become idle ")
        #raise DontCloseSpider("..I prefer live spiders.")
        self.crawler.stats.set_value("crawled_url", self.inputUrl)
        self.crawler.stats.set_value("crawled_correlationId", self.urlCorrelationId)

    def __init__(self, *args, **kwargs):
        super(SelogerAgencySpider, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, scrapy.signals.spider_closed)
        dispatcher.connect(self.spider_idle, scrapy.signals.spider_idle)


    def __init__(self, inputUrl=None, correlationId=None,sharedContext=None):
        print("getting url")
        self.inputUrl = inputUrl  # source url name
        self.urlCorrelationId = correlationId
        self.context = sharedContext
        dispatcher.connect(self.spider_closed, scrapy.signals.spider_closed)
        dispatcher.connect(self.spider_idle, scrapy.signals.spider_idle)



    def start_requests(self):

        yield scrapy.Request(url=self.inputUrl, callback=self.parse)

        driver.get(self.inputUrl)

    def get_RealotrDataFromProfile(self, response):

        name = response.xpath(".//h1[@itemprop='name']/text()").extract()
        print("realtorName: %s" % name)

        address = response.xpath("//div[@class='subtitle']/text()").extract()[1].strip()
        #address = [el.strip() for el in addre]
        print("realtorAddress: %s" % address)

        site = response.xpath(".//a[@class='b-link url-agency fi fi-agencywebsite']/@href").extract_first()
        print("realtorWebSite: %s" % site)

        logo = response.xpath('//div[@class="img-container"]//img/@src').extract()
        print("realtor_logo: %s" % logo)

        XPATH_phone = ".//div[@class='hide']/text()"
        phone = response.xpath(XPATH_phone).extract_first()
        print("realtorPhone: %s" % phone)

        des = response.xpath('//div[@class="full"]/text()').extract()
        desc = [el.strip() for el in des]
        print("realtor_description: %s" % desc)

        img = response.xpath('//div[@class="g-col g-333 img-centered-panoramic"]//img/@src').extract()
        print("realtor_images: %s" % img)

        #récupération de l'id de l'agence

        last_part = self.inputUrl.split('/')[-1]
        agency_id = re.findall(r'\d+', last_part)
        print('Agency ID : ', agency_id)

        # récupération agency team:
        team_pic = []

        print("voilà le team pics")
        try:
                images = driver.find_elements_by_xpath("//div[@class='portrait']/img")
                for image in images:
                    pic = image.get_attribute('src')
                    if pic :
                        team_pic.append(pic)
                        image_urls = team_pic
                    elif not pic :
                        team_pic.append('None')
        except :
                print('lequipe nont pas tous une photo')
        try:

            team_inf = []
            team_inf_position = []

            for elem_team in driver.find_elements_by_xpath("//div[@class='ag-team-member']//div[@class='description high']"):
                    team_inf.append(elem_team.text)

            for elem_team_post in driver.find_elements_by_xpath("//div[@class='ag-team-member']//div[@class='description low']"):
                    team_inf_position.append(elem_team_post.text)

            Team_information = []
            for b in range(len(team_inf_position)-1):
                    Team_information.append(('Team_Photo :' + team_pic[b],'Team_Name :' + team_inf[b],'Team Position :' + team_inf_position[b]))

        except :
            print("no agency team")


        #récupération des biens en vente:




        """
            , 'Url Picture :', ads_pictures[a]

        """
        try:
            for j in range(10):
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@class='b-btn b-ghost']")))
                driver.execute_script("arguments[0].click();", element)
        except:
            print("no more ads to show")




        lien_bien = []
        bien_inf = []
        lien = ''
        bien = ''
        print("les biens en vente:")
        for elem_lien in driver.find_elements_by_xpath("//div[@class='c-pa-info']/a"):
            url = elem_lien.get_attribute("href")
            lien_bien.append(url)
            myset_urls = set(lien_bien)
            lien = list(myset_urls)
            bien_inf.append(elem_lien.text)
            myset_infos = set(bien_inf)
            bien = list(myset_infos)
        ads_picture = []
        ads_pictures = ''
        picture=''

        for img_ads in driver.find_elements_by_xpath("//div[@class='c-pa-pic ']//div[@class='c-pa-img']//img"):
            ads_pic = img_ads.get_attribute('src')
            ads_picture.append(ads_pic)
            myset_pic = set(ads_picture)
            picture = list(myset_pic)
            ads_pictures = ' \n '.join(str(picture))

            print("les photos des annonces :", ads_pic)


        bien_en_vente_info = []
        for a in range(len(lien) - 1):
            bien_en_vente_info.append(('Ads_Url :' + lien[a], 'Ads_Description :' + bien[a], 'Ads_Picture :' + ads_picture[a]))

        print("bien en vente infos :", bien_en_vente_info)

       
       
    # récupération des biens vendus:
        move_to_sold = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, "//span[@class='tab sold-tab']")))
        driver.execute_script("arguments[0].click();", move_to_sold)

        try:
            for j in range(20):
                element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='tab-container sold']//button[@class='b-btn b-ghost']")))
                driver.execute_script("arguments[0].click();", element)
        except:
            print("no more sold ads to show")


        type_biens = []
        for elem_biens_vendus in driver.find_elements_by_xpath('//div[@class="ag-bien-vendu"]/div[@class="title"]'):
            type_biens.append(elem_biens_vendus.text)


        desc_biens = []
        for elem_biens_vendus in driver.find_elements_by_xpath('//div[@class="ag-bien-vendu"]/div[@class="tags"]'):
            desc_biens.append(elem_biens_vendus.text)


        city_biens = []
        for elem_biens_vendus in driver.find_elements_by_xpath('//div[@class="ag-bien-vendu"]/div[@class="city"]'):
            city_biens.append(elem_biens_vendus.text)


        details_biens = []
        for elem_biens_vendus in driver.find_elements_by_xpath('//div[@class="ag-bien-vendu"]/div[@class="sold-details"]'):
            details_biens.append(elem_biens_vendus.text)


        bien_vendu_info = []
        for c in range(len(type_biens)):
            bien_vendu_info.append(('Ads_type :' + type_biens[c], 'Ads_Description :' + desc_biens[c],'Ads_City :' + city_biens[c],'Ads_Details :' + details_biens[c]))

        print("bien en vente infos :", bien_vendu_info)





        realtor = WebRealtor()

        print("producing start")

        hosts = [('localhost', 61613)]
        conn = stomp.Connection(hosts)
        conn.start()
        conn.connect('admin', 'admin', wait=True)
        for l in range(len(lien)):
                url = lien[l]
                conn.send(body=url, destination='/queue/scrapy.seloger.agency.profile.ads.queue')
        conn.stop()

        realtor["Realtor_ID"] = None
        realtor["Realtor_ID"] = agency_id
        realtor["RealtorName"] = None
        realtor["RealtorName"] = name
        realtor["RealtorAddress"] = None
        realtor["RealtorAddress"] = address
        realtor["RealtorPhone"] = None
        realtor["RealtorPhone"] = phone
        realtor["RealtorWebSite"] = None
        realtor["RealtorWebSite"] = site
        realtor["Realtor_desc"] = None
        realtor["Realtor_desc"] = desc
        realtor["Realtor_logo"] = None
        realtor["Realtor_logo"] = logo
        realtor["Realtor_imgs"] = None
        realtor["Realtor_imgs"] = img

        realtor["Realtor_Ads_selling_infos"] = None
        if not bien_en_vente_info :
            bien_en_vente_info = None
        realtor["Realtor_Ads_selling_infos"] = bien_en_vente_info

        realtor["Realtor_sold_Ads_infos"] = None
        if not bien_vendu_info :
            bien_vendu_info = None
        realtor["Realtor_sold_Ads_infos"] = bien_vendu_info

        realtor["Realtor_Team_infos"] = None
        if not Team_information :
            Team_information = None
        realtor["Realtor_Team_infos"] = Team_information


        t = datetime.now()
        realtor["Time"] = t


        return realtor



    def parse(self, response):
        try:
            #initialisation des varriables
            is_expired = False
            is_robot_error = False
            is_response_ok = False



            print("-------------- Start processing response")

            print("response: %s" % response)

            meta = response.request.meta
            print("meta contains :")
            #print(meta)


            # verifier s il y a des redirections, si meta['redirect_urls'] exit
            # verifier si l annonce a expiree
            if 'redirect_urls' in meta :
                redirectUrl = meta['redirect_urls']
                print("http request url : %s" % redirectUrl)
                print('rederiction done')
                if str(redirectUrl).find("expiree") :
                    print('ads expired')
                    is_expired = True
                elif str(redirectUrl).find("erreur") :
                    #gerer le cas ou on recoit  https://www.seloger.com/erreur-temporaire/ avec le code 200
                    print('robot sent error')
                    is_robot_error = True
            else:
                print('no rederiction done')
                is_response_ok = True

            print("http response url: %s" % response.request.url)

            realtor = WebRealtor()
            if is_response_ok is True :
                realtor =self.get_RealotrDataFromProfile(response)
                print("-------------- End processing response with sucess")
            else:
                print("-------------- End processing response with error")

            """if not realtor.RealtorWebId exist in database
                save into database as json"""

            print("")
            yield realtor



        except Exception as e:
            print("Exception catched in AdsspiderSpider:parse :")
            traceback.print_exc()






class MetaHttpUrl(object):
    url = ''

class WebRealtor(scrapy.Item):
    Realtor_ID = scrapy.Field()
    RealtorName = scrapy.Field()
    RealtorAddress = scrapy.Field()
    RealtorPhone = scrapy.Field()
    RealtorWebSite = scrapy.Field()

    Realtor_desc = scrapy.Field()
    Realtor_logo = scrapy.Field()
    Realtor_imgs = scrapy.Field()
    Realtor_Ads_selling_infos = scrapy.Field()
    Realtor_sold_Ads_infos = scrapy.Field()
    Realtor_Team_infos = scrapy.Field()



    Time = scrapy.Field()


