# to use a twisted reactor
from scrapy.crawler import CrawlerProcess
# to use the local projet setting
from scrapy.utils.project import get_project_settings
from multiprocessing import Process, Manager
from concurrent.futures import ThreadPoolExecutor

from multiprocessing import Pool
import threading
# to use activeMq bridge
import scrapy.signals
import stomp
from elasticsearch import Elasticsearch
import json

#mongo database
#import pymongo
#from pymongo import MongoClient

crawlerResults = None


class ScrapyError(Exception):
    pass


class QueueListener(stomp.ConnectionListener):

    def __init__(self, connection=None, queuename=None, crawlerprocess=None, crawlername=None, listenerId=None,):
        self.QueueName = queuename
        self.Connection = connection
        self.Connection.set_listener('', self)
        self.QueueSubscription = None
        self.CrawlerProcess = crawlerprocess
        self.CrawlerName = crawlername
        print("QueueListner creeated ")
        self.executorPool = ThreadPoolExecutor(max_workers=3)
        self.pool = Pool(processes=4)
        self.sharedData = Manager().dict()
        self.ListenerId = listenerId

    def start_consuming(self):
        self.subscription = self.Connection.subscribe(destination=self.QueueName, id=self.ListenerId, ack='client', headers={'activemq.prefetchSize': 1})
        print("subscribe to queue has been done, consuming start")

    # override activeMq method
    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_disconnected(self):
        print("stom est deconnected ")

    def on_receiver_loop_completed(self, headers, body):
        print("la loop est fini")

    # override activeMq method
    def on_message(self, headers, message):
        print('received an activeMq message "%s"' % message)
        # tx = self.Connection.begin()
        try:
            print('activeMq message "%s" :' % message)

            # raise Exception("test exec")
            self.process_message(headers, message)

            self.Connection.ack(headers["message-id"], self.ListenerId)
            # self.Connection.commit("tx");
            print("End processing message, transaction commited")
        except stomp.exception.ConnectFailedException:
            print('Stomp connection fail')
        except Exception as e:
            print("Exception catched during processing activeMq message")
            # send message on ads.error.queue
            self.Connection.nack(headers['message-id'], self.ListenerId);
            self.Connection.send(body=message, destination='/queue/scrapy.seloger.agency.queue.error.')
            # self.Connection.abort("tx");

            # traceback.print_exc()
            # reset the heartbeat for any received message

        # self.CrawlerProcess.engine.schedule(message, self.CrawlerName)
        # self.Connection.commit(tx);

    # local method
    def process_message(self, headers, message):
        # check if the message is ok
        urlToScrap = message
        correlationId = headers["message-id"]
        if urlToScrap:
            # yield threads.deferToThread(process_thread , message)
            # d.callback(process_thread_callback)
            # self.executorPool.submit(process_thread            , (urlToScrap))
            # reactor.run()
            print("task submited")
            # create new thread for each message, in fact crawlerProcess.start() is blocking and we have to run asynchronously

            sub_process = Process(target=process_thread, args=(urlToScrap, correlationId, self.sharedData))
            sub_process.start()
            sub_process.join()
            if self.sharedData[correlationId]:
                raise Exception("exception durant le process 2")

    def process_inner_task(self, s):
        print(s)


# used by scrapy when triggering signal
def on_item_passed(item):
    print("on_item_passed")
    print("process_passed_item")
    print(item["RealtorName"])
    print(item["RealtorAddress"])
    print(item["RealtorPhone"])
    print(item["RealtorWebSite"])
    print(item["Realtor_desc"])
    print(item["Realtor_logo"])
    print(item["Realtor_imgs"])
    print(item["Realtor_Ads_selling_infos"])

    print(item["Time"])

    """

    jsonencoder = ScrapyJSONEncoder()
    realtorjson = jsonencoder.encode(item)
    """
    r1 = Real1()
    r1.Realtor_Name = item["RealtorName"]
    r1.Realtor_ID = item["Realtor_ID"]
    r1.Realtor_Description = item["Realtor_desc"]
    r1.Realtor_Address = item["RealtorAddress"]
    r1.Realtor_Phone = item["RealtorPhone"]
    r1.Realtor_Logo = item["Realtor_logo"]
    r1.Realtor_website = item["RealtorWebSite"]
    r1.Realtor_images = item["Realtor_imgs"]
    r1.Realtor_Team = item["Realtor_Team_infos"]
    r1.Realtor_Selling_Ads = item["Realtor_Ads_selling_infos"]
    r1.Realtor_Sold_Ads = item["Realtor_sold_Ads_infos"]
    r1.Creation_Date = item["Time"]
    json_to_save = json.dumps(r1.__dict__, default=str)





    """
    client = pymongo.MongoClient("mongodb+srv://Quelagent:quelagent@cluster0-eiqrx.mongodb.net/realtors_database?retryWrites=true")

    db = client.realtors_database

    db.realtor.insert(realtor)
    """
    es = Elasticsearch('localhost:9200', use_ssl=False, verify_certs=True)
    if es.ping():
        print('Connection successfully')
    else:
        print('sorry it couldnt connect!')

    try:
        if es.indices.exists("testtest3"):
            print("Index already exists")
        if not es.indices.exists("testtest3"):
            # Ignore 400 means to ignore "Index Already Exist" error.
            es.indices.create(index="testtest3", ignore=400, body=json_to_save)
            print('Created Index')
    except Exception as ex:
        print(str(ex))
    try:
        es.index(index="testtest3", doc_type="infos", body=json_to_save, request_timeout=30)

    except Exception as ex:
        print('Error in indexing data')
        print(str(ex))


# used by process for chaining task
def process_thread_callback(response):
    print("process_thread_callback start")
    # reactor.stop()
    print("process_thread_callback end")


def on_spider_closed(spider):
    # check errors when spider close and notify the caller process
    print("spider_closed")
    print("ERREUR: ", spider.crawler.stats.get_value('log_count/ERROR'))
    print("crawled_url: ", spider.crawler.stats.get_value('crawled_url'))
    print("crawled_correlationId: ", spider.crawler.stats.get_value('crawled_correlationId'))
    # excepition is catched by scrapy so can not be raised outer
    # raise Exception("scrapy error")


# task used for parrallel processing
def process_thread(url, messageCorrelationId, sharedContext):
    # create new crawler process each time we need to process an url
    print("process_thread start")
    print(threading.current_thread().name)
    crawlerProcess = CrawlerProcess(get_project_settings())
    crawlerProcess.crawl('selogeragencyspider', inputUrl=url, correlationId=messageCorrelationId,sharedContext=sharedContext)
    for p in crawlerProcess.crawlers:
        print("set item scraped signal ")
        p.signals.connect(on_item_passed, scrapy.signals.item_scraped)
        p.signals.connect(on_spider_closed, scrapy.signals.spider_closed)
    # dispatcher.connect(on_item_passed, scrapy.signals.item_passed)
    try:
        crawlerProcess.start()  # method bloaquante car scrapy et mono threading- se debloquer quand le status spided closed sera declancher, apres l'affichage des stats
        print("crawler process finished")
        for key, val in sharedContext.items():
            print(key, "=>", val)

        # si la valuer est different de none alors il y'a erreur
        if sharedContext[messageCorrelationId]:
            raise Exception("exception durant le process")

    except Exception as e:
        print('runspider spider:%s exception:%s' % ('selogeragencyspider', e))
        # raise e

    print("process_thread end")


def main():
    # logging.basicConfig(filename='selogerAdsConsumer.log', level=logging.INFO)

    print("listing start")
    hosts = [('localhost', 61613)]
    # check connection if fail or not
    conn = stomp.Connection(hosts)
    conn.start()
    conn.connect('admin', 'admin', wait=True)
    crawlingprocess = CrawlerProcess(get_project_settings())
    try:
        listner = QueueListener(conn, '/queue/scrapy.seloger.agency.profile.queue', crawlingprocess,'selogeragencyspider', 1)
        raise Exception("exception durant le listener")
    except Exception as e:
        print('Error in listening', e)
    listner.start_consuming()

    input("Enter to exit")


if __name__ == "__main__":
    # execute only if run as a script
    main()





class Real1(object):
    def __init__(self, nom=None, id=None, desc=None ,Adresse=None ,tel=None, img=None, en_vente=None, vendu=None, logo=None,date= None, site=None, team=None):
        self.Realtor_ID = id
        self.Realtor_Name = nom
        self.Realtor_Description = desc
        self.Realtor_Address = Adresse
        self.Realtor_Phone = tel
        self.Realtor_website = site
        self.Realtor_images = img
        self.Realtor_Team = team
        self.Realtor_Selling_Ads = en_vente
        self.Realtor_Sold_Ads = vendu
        self.Realtor_Logo = logo
        self.Creation_Date = date
