# -*- coding: utf-8 -*-
import scrapy
import traceback

import scrapy.signals

from scrapy.xlib.pydispatch import dispatcher
from datetime import datetime

import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


chrome_options = Options()
chrome_options.add_argument("--headless")



#service = webdriver.Chrome(executable_path=os.path.abspath(r'C:\Users\Oussama\Desktop\webdriver/chromedriver.exe'),chrome_options=chrome_options)

service = webdriver.chrome.service.Service(os.path.abspath(r'C:\Users\Oussama\Desktop/chromedriver.exe'))
service.start()
driver = webdriver.Remote(service.service_url,   desired_capabilities=chrome_options.to_capabilities())




class SelogerAdsSpider(scrapy.Spider):
    name = 'selogeradsspider'
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
        self.context[self.urlCorrelationId]=  spider.crawler.stats.get_value('log_count/ERROR')


    def spider_idle(self, spider):
        print("spider just become idle ")
        #raise DontCloseSpider("..I prefer live spiders.")
        self.crawler.stats.set_value("crawled_url", self.inputUrl)
        self.crawler.stats.set_value("crawled_correlationId", self.urlCorrelationId)

    def __init__(self, *args, **kwargs):
        super(SelogerAdsSpider, self).__init__(*args, **kwargs)
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
       """ urls = [
            'https://www.seloger.com/annonces/achat/appartement/paris-14eme-75/montsouris-dareau/143580615.htm?ci=750114&idtt=2,5&idtypebien=2,1&LISTING-LISTpg=8&naturebien=1,2,4&tri=initial&bd=ListToDetail',
            'https://www.seloger.com/annonces/achat/appartement/montpellier-34/gambetta/137987697.htm?ci=340172&idtt=2,5&idtypebien=1,2&naturebien=1,2,4&tri=initial&bd=ListToDetail',
            'https://www.seloger.com/annonces/achat/appartement/montpellier-34/celleneuve/142626025.htm?ci=340172&idtt=2,5&idtypebien=1,2&naturebien=1,2,4&tri=initial&bd=ListToDetail',
            'https://www.seloger.com/annonces/achat/appartement/versailles-78/domaine-national-du-chateau/138291887.htm'

        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)"""
       yield scrapy.Request(url=self.inputUrl, callback=self.parse)

       driver.get(self.inputUrl)
       """
       scrapy_selector = Selector(text=driver.page_source)
       scrapy_selector.xpath('//div[@class="grid-flexible-height g-row g-row-30-sm g-row-50-xs"]')  # returns the list of selectors
        """
    def get_RealotrDataFromAds(self, response):
        #element = driver.find_elements_by_css_selector("div[class='u-left']")
        #testt = element.text
        #test = ''.join(str(v) for v in testt)
        feat = []
        print("realestate_features: ")
        for elem in driver.find_elements_by_css_selector("div[class='u-left']"):
            feat.append(elem.text)
            #featur = ','.join(feat)

        tr = response.xpath('//h1[@class="detail-title title1"]/text()').extract()
        tran = [p.split()[0] for p in tr]
        trans = ''.join(tran)
        print("realestate_transaction_type: %s" % trans)

        tit = response.xpath('//h2[@class="title2 fi fi-house description-bien-title"]/text()').extract()
        titl = [p.split()[4] for p in tit] + [p.split()[5] for p in tit] + [p.split()[6] for p in tit]
        title = ' '.join(titl)
        print("realestate_title: %s" % title)

        name = response.css(".agence-link::text").extract_first()
        print("realtorName: %s" % name)

        address = response.css(".agence-adresse::text").extract_first()
        print("realtorAddress: %s" % address)
        try:
            sire = response.xpath(".//div[@class='legalNoticeAgency']//p/text()")[-1].extract()
            siren = sire.split()[1]
        except:
            siren = None
        print("realtorSiren: %s" % siren)


        site = response.xpath(".//div[@class='agence-links']//a/@href")[-2].extract()
        print("realtorWebSite: %s" % site)



        profile = response.xpath('//input[@name="urlagence"]/@value').extract()[0].strip()
        print("realtorProfile: %s" % profile)


        idd = response.xpath('//div[@class="g-col g-50 sticky_button_bottom_col sticky_button_bottom_col_tel"]/a/@data-idannonce').extract()
        id = ''.join(idd)
        print("realestate_id: %s" % id)

        real_type = response.xpath('//h2[@class="c-h2"]/text()').extract_first()
        print("realestate_type: %s" % real_type)

        real_address = response.xpath('//p[@class="localite"]/text()').extract_first()
        print("realestate_adress: %s" % real_address)

        id_rea = response.xpath('//div[@class="c-main listing  p-detail c-detail-bar"]/@data-publication-id').extract()
        id_real = ''.join(id_rea)
        print("realtor_id: %s" % id_real)

        XPATH_phone = ".//div[@class='contact g-row-50']//div[@class='g-col g-50 u-pad-0']//button[@class='btn-phone b-btn b-second fi fi-phone tagClick']/@data-phone"
        phone = response.xpath(XPATH_phone).extract_first()
        print("realtorPhone: %s" % phone)

        price = response.xpath('//input[@name="prix"]/@value').extract()[0].strip()
        print("realestate_price: %s" % price)

        desc = response.xpath('//input[@name="description"]/@value').extract()[0].strip()
        print("realestate_description: %s" % desc)

        zip = response.xpath('//input[@name="codepostal"]/@value').extract()[0].strip()
        print("realestate_description: %s" % zip)

        piece = response.xpath('//li/text()').extract_first()
        print("realestate_pieces: %s" % piece)

        nb_rooms = response.xpath('//li/text()')[-2].extract()
        print("realestate_nb_rooms: %s" % nb_rooms)

        surface = response.xpath('//input[@name="surface"]/@value').extract()[0].strip()
        print("realestate_surface: %s" % surface)

        logo = response.xpath('//div[@class="agence-top"]//img/@src').extract()
        print("realtor_logo: %s" % logo)

        img = response.css('.carrousel_image_small::attr("src")').extract()
        print("realestate_image: %s" % img)

        realtor = WebRealtor()
        realtor["RealEstateFeatures"] = None
        realtor["RealEstateFeatures"] = feat

        realtor["RealtorWebId"] = None
        realtor["RealtorWebId"] = id
        realtor["RealtorId"] = None
        realtor["RealtorId"] = id_real
        realtor["RealtorName"] = None
        realtor["RealtorName"] = name
        realtor["RealtorAddress"] = None
        realtor["RealtorAddress"] = address
        realtor["RealtorPhone"] = None
        realtor["RealtorPhone"] = phone
        realtor["Realtor_Profile"] = None
        realtor["Realtor_Profile"] = profile
        realtor["RealtorWebSite"] = None
        if not site :
            site = None
        realtor["RealtorWebSite"] = site

        realtor["RealtroSiren"] = None
        if not siren :
            siren = None
        realtor["RealtroSiren"] = siren

        realtor["RealEstate_trans"] = None
        realtor["RealEstate_trans"] = trans

        realtor["RealEstate_title"] = None
        realtor["RealEstate_title"] = title

        realtor["RealEstate_zip"] = None
        realtor["RealEstate_zip"] = zip
        realtor["RealEstate_Adress"] = None
        realtor["RealEstate_Adress"] = real_address
        realtor["RealEstate_type"] = None
        realtor["RealEstate_type"] = real_type
        realtor["RealEstate_desc"] = None
        realtor["RealEstate_desc"] = desc
        realtor["RealEstate_price"] = None
        realtor["RealEstate_price"] = price
        realtor["RealEstate_pieces"] = None
        realtor["RealEstate_pieces"] = piece
        realtor["RealEstate_nbrooms"] = None
        realtor["RealEstate_nbrooms"] = nb_rooms
        realtor["RealEstate_surface"] = None
        realtor["RealEstate_surface"] = surface
        realtor["Realtor_logo"] = None
        realtor["Realtor_logo"] = logo
        realtor["RealEstate_img"] = None
        realtor["RealEstate_img"] = img


        t = datetime.now()
        realtor["Time"] = t



        return realtor
        driver.close()

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
                realtor =self.get_RealotrDataFromAds(response)
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
    RealtorInternId = scrapy.Field()
    RealtorWebId = scrapy.Field()
    RealtorId = scrapy.Field()
    RealtorName = scrapy.Field()
    RealtorAddress = scrapy.Field()
    RealtorPhone = scrapy.Field()
    RealtorWebSite = scrapy.Field()
    RealtroSiren = scrapy.Field()
    RealEstate_type = scrapy.Field()
    RealEstate_Adress = scrapy.Field()
    RealEstate_desc = scrapy.Field()
    RealEstate_price = scrapy.Field()
    RealEstate_pieces = scrapy.Field()
    RealEstate_nbrooms = scrapy.Field()
    RealEstate_surface = scrapy.Field()
    RealEstate_zip = scrapy.Field()
    Realtor_logo = scrapy.Field()
    RealEstate_img = scrapy.Field()
    Realtor_Profile = scrapy.Field()
    RealEstate_trans = scrapy.Field()
    RealEstate_title = scrapy.Field()

    Time = scrapy.Field()

    RealEstateFeatures = scrapy.Field()



