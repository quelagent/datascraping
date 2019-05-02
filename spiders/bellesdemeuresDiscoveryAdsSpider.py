
import scrapy
from scrapy.item import Item
from concurrent.futures import ThreadPoolExecutor
import traceback
from .SmallAds import SmallAds

class BellesdemeuresDiscoveryAdsSpider(scrapy.Spider):
    name = 'bellesdemeuresDiscoveryAdsSpider'
    allowed_domains = ['bellesdemeures.com']
    handle_httpstatus_list = [502,404]
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_fake_useragent.middleware.RandomUserAgentMiddleware': 400,
            'immoscraping.middlewares.LuminatiProxyMiddleware': 450,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 500,
        }
    }
    #start_urls = ['https://www.seloger.com/list.htm?tri=initial&idtypebien=2,1&idtt=2,5&naturebien=1,2,4&cp=75']


    def start_requests(self):
        for i in range(1, 6):
            page = 'https://www.bellesdemeures.com/recherche?ci=750115&tri=Selection&idtt=2&page=' + str(i)
            yield scrapy.Request(page, callback=self.parse)


    def getAdsDataFromSearchPagebelles(self, response):
        self.logger.info(" ---- start getAdsDataFromSearchPagebelles for url" + response.request.url)
        self.logger.info(response.request.meta)

        try:
            all_adsids = response.xpath('//p[@class="contactButtonsItem agencyContactPhone js_contactPhone trackClick"]//@data-id').extract()
            #ll_adsids = response.xpath('//div[@class="c-pa-list c-pa-sl c-pa-gold cartouche "]//@id').extract()

            urls = response.xpath('//div[@class="annonceItemContact"]//a//@href').extract()
            all_adsprices = response.xpath('//p[@class="annonceItemPrice"]/text()').extract()
            all_adstypes = response.xpath('//span[@class="annonceItemType"]/text()').extract()
            all_adscriterea = response.xpath('//span[@class="annonceItemRoom"]').extract()
            all_adscity = response.xpath('//strong[@class="annonceItemCity"]/text()').extract()


            items = []
            self.logger.info("ads count: " + str(len(all_adsids)))
            for i in range(0, len(all_adsids)):
                ads = SmallAds()
                ads["Type"] = "SmallAds"
                ads['AdsWebId'] = all_adsids[i]
                a = 'www.bellesdemeures.com'
                completedurl = a + urls[i]
                ads['AdsUrl'] = completedurl
                ads['AdsType'] = all_adstypes[i]
                ads['AdsPrice'] = all_adsprices[i]
                ads['AdsCriterea'] = all_adscriterea[i]
                ads['AdsCity'] = all_adscity[i]

                #print("ads=",ads['AdsWebId'], ",", ads['AdsUrl'], ",", ads['AdsType'], ",", ads['AdsPrice'], ",", ads['AdsCity'])
                items.append(ads)
        except Exception as e :
            self.logger.info("Exception : getAdsDataFromSearchPagebelles")
            self.logger.info(traceback.print_exc())

        self.logger.info(" ---- end getAdsDataFromSearchPagebelles for url" + response.request.url)
        return items



    #override scrapy method
    def parse(self, response):

        # initialisation des varriables
        is_expired = False
        is_robot_error = False
        is_response_ok = True
        self.logger.info("")
        self.logger.info("######### Parsing ############")
        self.logger.info("response: %s", response)
        meta = response.request.meta
        self.logger.info("Response meta: %s", meta)
        self.logger.info(meta)





        # verifier s il y a des redirections, si meta['redirect_urls'] exit
        # verifier si l annonce a expiree
        if 'redirect_urls' in meta:
            redirectUrl = meta['redirect_urls'][0]
            self.logger.info("redirectUrl url : %s" % redirectUrl)
            self.logger.info("responseUrl url : %s" % response)
            self.logger.info('rederiction done')

            if "erreur" in str(redirectUrl):
                # gerer le cas ou on recoit  https://www.seloger.com/erreur-temporaire/ avec le code 200
                self.logger.info('robot sent error')
                is_robot_error = True
                #is_response_ok = False

            #if rederection check the sent url and the received utl
            if "expiree" in str(redirectUrl):
                self.logger.info('ads expired')
                is_expired = True
                #is_response_ok = False

        else:
            self.logger.info('no rederiction done')


        if "erreur" in str(response):
            # gerer le cas ou on recoit  https://www.seloger.com/erreur-temporaire/ avec le code 200
            self.logger.info('robot sent error')
            is_robot_error = True
            is_response_ok = False

        if "expiree" in str(response):
            self.logger.info('ads expired')
            is_expired = True
            is_response_ok = False

        if is_response_ok is True:
                ads_list = self.getAdsDataFromSearchPagebelles(response)
                if len(ads_list) > 0:
                    for adsItem in ads_list:
                        yield adsItem
                else:
                    retries = response.request.meta.get('retry_times', 0) + 1
                    if retries <= 5:
                        self.logger.info("retry requets: %s", str(retries))
                        retryreq = scrapy.Request(response.request.meta["origin"], callback=self.parse)
                        retryreq.meta['retry_times'] = retries
                        retryreq.dont_filter = True
                        retryreq.priority = response.request.priority + 1
                        yield retryreq
                    else:
                        deferedRequest = SmallAds()
                        deferedRequest['RequestUrl'] = str(response.request.meta['origin'])
                        deferedRequest['Raison'] = response.status
                        deferedRequest["Type"] = "DeferedRequest"
                        yield deferedRequest
                """print("look for the next page")
                nextpageurl = response.xpath('//a[@class="pagination-next"]/@href')
                if nextpageurl:
                    # If we've found a pattern which matches
                    path = nextpageurl.extract_first()
                    nextpage = response.urljoin(path)
                    print("Found url: {}".format(nextpage))  # Write a debug statement
                    yield scrapy.Request(nextpage, callback=self.parse)  # Return a call to the function "parse"
                else:
                    print("next pas not found")"""
        else:
            # fix tentative number to 3, the issue is that some time we could be blocked several times by the target server like when there are forward 307
            self.logger.info("not able to extract data from : %s" , response.request.meta["origin"])
            retries = response.request.meta.get('retry_times', 0) + 1
            if retries <= 5:
                self.logger.info("retry requets:  %s", str(retries))
                #retryreq=response.request.copy()
                retryreq = scrapy.Request( response.request.meta["origin"], callback=self.parse)
                retryreq.meta['retry_times'] = retries
                retryreq.dont_filter = True
                retryreq.priority = response.request.priority + 1
                self.logger.info("retry: %s" , retryreq)
                yield retryreq
            else:
                deferedRequest = SmallAds()
                deferedRequest['RequestUrl'] = str(response.request.meta['origin'])
                deferedRequest['Raison'] = response.status
                deferedRequest["Type"] = "DeferedRequest"
                yield deferedRequest





    def get_nbRooms(self):
        critereaList=self.AdsCriterea.replace("<em>","").replace(' ', '').replace('\n', '').split("</em>")
        #for item in critereaList :
           # print(item)


class DeferedRequest(Item):
    RequestUrl =  scrapy.Field()
    Raison =  scrapy.Field()



def main():
    print("Discovery")

if __name__ == '__main__':
    main()