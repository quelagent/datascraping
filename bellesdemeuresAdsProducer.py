# to use a twisted reactor
from scrapy.crawler import CrawlerProcess

# to get item processed by the scraper
import scrapy.signals

# to use the local project setting
from scrapy.utils.project import get_project_settings
# to use activeMq bridge
import stomp

from multiprocessing import Manager

#from spiders.DiscoveryAdsSpider import DeferedRequest
#from spiders.DiscoveryAdsSpider import SmallAds

results = []
conn = None

class QueueProducer:
    def __init__(self, connection=None,crawlerprocess=None,crawlername=None,producerId=None):
        self.Connection = connection
        self.QueueSubscription = None
        self.CrawlerProcess = crawlerprocess
        self.CrawlerName = crawlername
        self.Context = Manager().dict()
        self.ProducerId = producerId
        self.CrawlerProcess.crawl(crawlername)
        for p in self.CrawlerProcess.crawlers:
            print("set item scraped signal ")
            p.signals.connect(self.on_item_scraped, signal=scrapy.signals.item_scraped)

    def on_item_scraped(self,item, response, spider):
        #results.append(item)
        # set activeMs connection

        #print("send", item["AdsUrl"])

        """hosts = [('localhost', 61613)]
        conn = stomp.Connection(hosts)
        conn.start()
        conn.connect('admin', 'admin', wait=True)"""
       # if(isinstance(item,DeferedRequest)):
        #    self.Connection.send(body=item["RequestUrl"], destination='/queue/scrapy.seloger.ads.queue.pageretry')

        #if (isinstance(item, SmallAds)):
        if (item["Type"]=="DeferedRequest"):
            self.Connection.send(body=item["RequestUrl"], destination='/queue/scrapy.bellesdemeures.ads.queue.pageretry')

        if (item["Type"] == "SmallAds" and "15ème" in item["AdsCity"]):
            ads_url_to_scrap = item["AdsUrl"]
            if "bellesdemeures" in ads_url_to_scrap:
                self.Connection.send(body=item["AdsUrl"], destination='/queue/scrapy.bellesdemeures.ads.queue')
            else:
                self.Connection.send(body=item["AdsUrl"], destination='/queue/scrapy.bellesdemeures.ads.queue.unknown_adsurl')

    def start(self):
        self.CrawlerProcess.start()



def main():
    print("producing start")

    #check connection if fail or not

    crawlingprocess = CrawlerProcess(get_project_settings())

    """crawlingprocess.crawl('discoveryadsspider')
    for p in crawlingprocess.crawlers:
        print("set item scraped signal ")
        p.signals.connect(on_item_scraped, signal=scrapy.signals.item_scraped)

    crawlingprocess.start()"""

    hosts = [('localhost', 61613)]
    conn = stomp.Connection(hosts)
    conn.start()
    conn.connect('admin', 'admin', wait=True)

    producer = QueueProducer(conn, crawlingprocess, 'bellesdemeuresDiscoveryAdsSpider', 1)
    producer.start()
    input("Enter to exit")
    conn.stop()

if __name__ == "__main__":
    # execute only if run as a script
    main()