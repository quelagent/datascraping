
import scrapy
import traceback
#use Request to keep url live in parse method
import scrapy.signals

from scrapy.xlib.pydispatch import dispatcher




class BellesdemeuresAdsSpider(scrapy.Spider):
    name = 'bellesdemeuresadsspider'
    allowed_domains = ['bellesdemeures.com']
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
        super(BellesdemeuresAdsSpider, self).__init__(*args, **kwargs)
        dispatcher.connect(self.spider_closed, scrapy.signals.spider_closed)
        dispatcher.connect(self.spider_idle, scrapy.signals.spider_idle)


    def __init__(self, inputUrl=None, correlationId=None,sharedContext=None):
        self.inputUrl = inputUrl  # source url name
        self.urlCorrelationId = correlationId
        self.context = sharedContext
        dispatcher.connect(self.spider_closed, scrapy.signals.spider_closed)
        dispatcher.connect(self.spider_idle, scrapy.signals.spider_idle)



    def start_requests(self):
       yield scrapy.Request(url=self.inputUrl, callback=self.parse)


    def get_RealotrDataFromAds(self, response):

        name = response.xpath('//span[@class="agencyColLinkName"]/text()').extract_first()
        print("realtorName: %s" % name)

        address = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "detailMoreSummary", " " ))]/text()').extract()
        print("realtorAddress: %s" % address)

        siren =  response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "detailMoreSummary", " " ))]/text()')[-1].extract()
        print("realtorSiren: %s" % siren)

        carte_pro = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "detailMoreSummary", " " ))]/text()')[-4].extract()
        print("realtorCartePro: %s" % carte_pro)


        XPATH_website = '//a[@class="detailContactSite tagClick"]//@href'
        site = response.xpath(XPATH_website).extract()
        print("realtorWebSite: %s" % site)

        XPATH_phone = '//p[@class="buttonBlack phoneBtn js_phoneBtn trackClickPopin"]//@data-phone'
        phone = response.xpath(XPATH_phone).extract()
        print("realtorPhone: %s" % phone)

        price = response.xpath('//a[@class="detailBanner js_favoritesParent"]//@data-short-price').extract()
        print("realestate_price: %s" % price)

        desc = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "detailDescSummary", " " ))]/text()').extract()
        print("realestate_description: %s" % desc)

        price_mention = response.xpath('//*[contains(concat( " ", @class, " " ), concat( " ", "detailMoreAlur", " " ))]/text()').extract()
        print("realestate_price_mention: %s" % price_mention)

        surface = response.xpath('//li[@class="annonceSpecsListItem js_livingArea"]/text()').extract()
        print("realestate_surface: %s" % surface)

        nb_rooms = response.xpath('//li[@class="annonceSpecsListItem js_nbRooms"]/text()').extract()
        print("realestate_nb_rooms: %s" % nb_rooms)



        realtor= WebRealtor()
        realtor["RealtorName"] = None
        realtor["RealtorName"] = name
        realtor["RealtorAddress"] = None
        realtor["RealtorAddress"] = address
        realtor["RealtorPhone"] = None
        realtor["RealtorPhone"] = phone
        realtor["RealtorWebSite"] = None
        realtor["RealtorWebSite"] = site
        realtor["RealtroSiren"] = None
        realtor["RealtroSiren"] = siren
        realtor["RealtroCartePro"] = None
        realtor["RealtroCartePro"] = carte_pro
        realtor["RealEstate_desc"] = None
        realtor["RealEstate_desc"] = desc
        realtor["RealEstate_price"] = None
        realtor["RealEstate_price"] = price
        realtor["RealEstate_price_mention"] = None
        realtor["RealEstate_price_mention"] = price_mention
        realtor["RealEstate_surface"] = None
        realtor["RealEstate_surface"] = surface
        realtor["RealEstate_nbrooms"] = None
        realtor["RealEstate_nbrooms"] = nb_rooms

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
    RealtorName = scrapy.Field()
    RealtorAddress = scrapy.Field()
    RealtorPhone = scrapy.Field()
    RealtorWebSite = scrapy.Field()
    RealtroSiren = scrapy.Field()
    RealtroCartePro = scrapy.Field()
    RealEstate_desc = scrapy.Field()
    RealEstate_price = scrapy.Field()
    RealEstate_price_mention = scrapy.Field()
    RealEstate_surface = scrapy.Field()
    RealEstate_nbrooms = scrapy.Field()
