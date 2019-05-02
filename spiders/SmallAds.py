from scrapy.item import Item
import scrapy


class SmallAds(Item):
    Type = scrapy.Field()
    Time = scrapy.Field()
    AdsId = scrapy.Field()
    AdsWebId = scrapy.Field()
    AdsUrl = scrapy.Field()
    AdsType = scrapy.Field()
    AdsPrice = scrapy.Field()
    AdsCriterea = scrapy.Field()
    AdsCity = scrapy.Field()
    RequestUrl = scrapy.Field()
    Raison = scrapy.Field()

    def jsonDefault(object):
        return object.__dict__