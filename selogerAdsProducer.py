
from scrapy.crawler import CrawlerProcess

# to get item processed by the scraper
import scrapy.signals

# to use the local projet setting
from scrapy.utils.project import get_project_settings
# to use activeMq bridge
import stomp
import argparse
from multiprocessing import Manager


results = []
conn = None

class QueueProducer:
    def __init__(self, connection=None,crawlerprocess=None,crawlername=None,producerId=None, cp=None):
        self.Connection = connection
        self.QueueSubscription = None
        self.CrawlerProcess = crawlerprocess
        self.CrawlerName = crawlername
        self.Context = Manager().dict()
        self.ProducerId = producerId
        self.Cp = cp
        self.CrawlerProcess.crawl(crawlername, cp=self.Cp)

        for p in self.CrawlerProcess.crawlers:
            print("set item scraped signal ")
            p.signals.connect(self.on_item_scraped, signal=scrapy.signals.item_scraped)
    def on_item_scraped(self,item, response, spider):
        #results.append(item)
        # set activeMs connection

        #print("send", item["AdsUrl"])

       # if(isinstance(item,DeferedRequest)):
        #    self.Connection.send(body=item["RequestUrl"], destination='/queue/scrapy.seloger.ads.queue.pageretry')

        #if (isinstance(item, SmallAds)):
        if (item["Type"]=="DeferedRequest"):
            self.Connection.send(body=item["RequestUrl"], destination='/queue/scrapy.seloger.ads.queue.pageretry.'+str(self.Cp))

        if (item["Type"] == "SmallAds"):
            ads_url_to_scrap = item["AdsUrl"]
            if "bellesdemeures" in ads_url_to_scrap:
                self.Connection.send(body=item["AdsUrl"], destination='/queue/scrapy.bellesdemeures.ads.queue.'+str(self.Cp))
            elif "selogerneuf" in ads_url_to_scrap:
                self.Connection.send(body=item["AdsUrl"], destination='/queue/scrapy.selogerneuf.ads.queue.'+str(self.Cp))

            else:

                self.Connection.send(body=item["AdsUrl"], destination='/queue/scrapy.seloger.ads.queue.'+str(self.Cp))




    def start(self):
        self.CrawlerProcess.start()



def main():
    #logging.basicConfig(filename='selogerAdsProducer.log', level=logging.DEBUG)
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

    parser = argparse.ArgumentParser()
    parser.add_argument('-cp', '-cp=', type=str)
    arg = parser.parse_args()

    producer = QueueProducer(conn, crawlingprocess, 'selogerdiscoveryadsspider', 1, arg.cp)
    producer.start()
    input("Enter to exit")


if __name__ == "__main__":
    # execute only if run as a script
    main()


