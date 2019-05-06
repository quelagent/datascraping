# to use a twisted reactor
from scrapy.crawler import CrawlerProcess
# to use the local projet setting
from scrapy.utils.project import get_project_settings
from multiprocessing import Process , Manager
from concurrent.futures import ThreadPoolExecutor

from multiprocessing import Pool
import threading
# to use activeMq bridge
import scrapy.signals
import stomp
from elasticsearch import Elasticsearch
from marshmallow import Schema, fields, pprint
import argparse
import json
import jsonpickle


crawlerResults = None

class WebRealto(object):
    def __init__(self,id=None ,nom=None, siren=None,Adresse=None ,phone=None, logo=None, site=None, profile=None):
        self.externId = id
        self.Realtor_Name = nom
        self.Realtor_Siren = siren
        self.Realtor_Address = Adresse
        self.Realtor_Phone_Number = phone
        self.Realtor_Logo = logo
        self.Realtor_Seloger_Profile = profile
        self.Realtor_Website = site

class Feature(object):
    def __init__(self,surf=None, surf_unite=None, feat=None):
        self.Realestate_Surface = surf
        self.Realestate_Surface_Unite = surf_unite
        self.RealEstate_Features = feat
class Price(object):
    def __init__(self,prix=None, price_unite=None):
        self.Realestate_Price = prix
        self.Realestate_Price_Unite = price_unite
class Address(object):
    def __init__(self,RealEstate_Adress=None, RealEstate_Zip_Code=None):
        self.RealEstate_Adress = RealEstate_Adress
        self.RealEstate_Zip_Code = RealEstate_Zip_Code

class Webads( object):
    def __init__(self, type=None, transtype=None,addresse=None,prix = None,realtor = None,fea=None , desc=None ,Room=None, titre=None,date= None, Bed=None, img=None):
        self.TransactionType = transtype
        self.Type = type
        self.Title = titre
        self.Images = img
        self.Description = desc
        self.Rooms = Room
        self.Beds = Bed
        self.Creation_Date = date
        self.Adress = addresse
        self.Price = prix
        self.WebRealtor = realtor
        self.Features = fea









class ScrapyError(Exception):
    pass

class QueueListener(stomp.ConnectionListener):



    def __init__(self, connection=None,queuename=None,crawlerprocess=None,crawlername=None,listenerId=None,cp=None):
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
        self.Cp = cp






    def start_consuming(self):
        self.subscription=self.Connection.subscribe(destination=self.QueueName, id=self.ListenerId, ack='client',headers={'activemq.prefetchSize': 1})
        print("subscribe to queue has been done, consuming start")

    #override activeMq method
    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_disconnected(self):
        print("stom est deconnected ")

    def on_receiver_loop_completed(self, headers, body):
       print("la loop est fini")


    # override activeMq method
    def on_message(self, headers, message):
        print('received an activeMq message "%s"' % message)
        #tx = self.Connection.begin()
        try:
            print('activeMq message "%s" :' % message)

            #raise Exception("test exec")
            self.process_message(headers, message)

            self.Connection.ack(headers["message-id"],self.ListenerId)
            #self.Connection.commit("tx");
            print("End processing message, transaction commited")
        except stomp.exception.ConnectFailedException:
            print('Stomp connection fail')
        except Exception as e:
            print("Exception catched during processing activeMq message")
            #send message on ads.error.queue
            self.Connection.nack(headers['message-id'], self.ListenerId);
            self.Connection.send(body=message, destination='/queue/scrapy.seloger.ads.queue.error.'+str(self.Cp))
            #self.Connection.abort("tx");

            #traceback.print_exc()
            # reset the heartbeat for any received message


        #self.CrawlerProcess.engine.schedule(message, self.CrawlerName)
        #self.Connection.commit(tx);

    # local method
    def process_message(self,headers, message):
        #check if the message is ok
        urlToScrap=message
        correlationId =headers["message-id"]
        if urlToScrap :
            #yield threads.deferToThread(process_thread , message)
           # d.callback(process_thread_callback)
            #self.executorPool.submit(process_thread            , (urlToScrap))
            #reactor.run()
            print("task submited")
            #create new thread for each message, in fact crawlerProcess.start() is blocking and we have to run asynchronously

            sub_process = Process(target=process_thread, args=(urlToScrap,correlationId,self.sharedData))
            sub_process.start()
            sub_process.join()
            if self.sharedData[correlationId]:
                raise Exception("exception durant le process 2")


    def process_inner_task(self,s):
        print(s)











# used by scrapy when triggering signal
def on_item_passed(item):
        print("on_item_passed")
        print("process_passed_item")
        print(item["RealtorWebId"])
        print(item["RealtorId"])
        print(item["RealtorName"])
        print(item["RealtorAddress"])
        print(item["RealtorPhone"])
        print(item["RealtorWebSite"])
        print(item["RealtroSiren"])
        print(item["RealEstate_type"])
        print(item["RealEstate_Adress"])
        print(item["RealEstate_desc"])
        print(item["RealEstate_price"])
        print(item["RealEstate_pieces"])
        print(item["RealEstate_nbrooms"])
        print(item["RealEstate_surface"])
        print(item["Realtor_logo"])
        print(item["RealEstate_img"])
        print(item["RealEstate_zip"])
        print(item["RealEstate_trans"])
        print(item["RealEstate_title"])
        print(item["Time"])
        print(item["RealtorFeatures"])

        """
        
        jsonencoder = ScrapyJSONEncoder()
        realtorjson = jsonencoder.encode(item)
        """
        Real = WebRealto()

        Real.externId = item["RealtorWebId"]
        Real.Realtor_Siren = item["RealtroSiren"]
        Real.Realtor_Name = item["RealtorName"]
        Real.Realtor_Address = item["RealtorAddress"]
        Real.Realtor_Phone_Number = item["RealtorPhone"]
        Real.Realtor_Logo = item["Realtor_logo"]
        Real.Realtor_Website = item["RealtorWebSite"]

        #Real.Realtor_Seloger_Profile = item["Realtor_Profile"]
        rea = json.dumps(Real.__dict__)

        add = Address()
        add.RealEstate_Adress = item["RealEstate_Adress"]
        add.RealEstate_Zip_Code = item["RealEstate_zip"]
        ad = json.dumps(add.__dict__)

        pr = Price()
        pr.Realestate_Price = item["RealEstate_price"]
        pr.Realestate_Price_Unite = "€ FAI*"
        pri = json.dumps(pr.__dict__)

        featu = Feature()
        featu.Realestate_Surface = item["RealEstate_surface"]
        featu.Realestate_Surface_Unite = "m²"
        featu.RealEstate_Features = item["RealtorFeatures"]
        fea = json.dumps(featu.__dict__)

        web = Webads()
        web.Title = item["RealEstate_title"]
        web.Type = item["RealEstate_type"]
        web.TransactionType = item["RealEstate_trans"]
        web.Adress = ad
        web.Description = item["RealEstate_desc"]
        web.Price = pri
        web.Rooms = item["RealEstate_pieces"]
        web.Beds = item["RealEstate_nbrooms"]
        web.Images = item["RealEstate_img"]
        web.Features = fea
        web.WebRealtor = rea
        web.Creation_Date = item["Time"]

        json_to_save = json.dumps(web.__dict__, default=str)




        es = Elasticsearch('localhost:9200', use_ssl=False, verify_certs=True)
        if es.ping():
            print('Connection successfully')
        else:
            print('sorry it couldnt connect!')

        try:
            if es.indices.exists("testttestttestt1"):
                print("Index already exists")
            if not es.indices.exists("testttestttestt1"):
                # Ignore 400 means to ignore "Index Already Exist" error.
                es.indices.create(index="testttestttestt1", ignore=400, body=json_to_save)
                print('Created Index')
        except Exception as ex:
            print(str(ex))
        try:
                 es.index(index="testttestttestt1", doc_type="info", body=json_to_save, request_timeout=340)

        except Exception as ex:
            print('Error in indexing data')
            print(str(ex))







# used by process for chaining task
def process_thread_callback(response):
        print("process_thread_callback start")
        #reactor.stop()
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
def process_thread(url, messageCorrelationId,sharedContext):
    #create new crawler process each time we need to process an url
    print("process_thread start")
    print(threading.current_thread().name)
    crawlerProcess = CrawlerProcess(get_project_settings())
    crawlerProcess.crawl('selogeradsspider', inputUrl=url,correlationId=messageCorrelationId, sharedContext=sharedContext)
    for p in crawlerProcess.crawlers:
        print("set item scraped signal ")
        p.signals.connect(on_item_passed, scrapy.signals.item_scraped)
        p.signals.connect(on_spider_closed, scrapy.signals.spider_closed)
   #dispatcher.connect(on_item_passed, scrapy.signals.item_passed)
    try:
        crawlerProcess.start() # method bloaquante car scrapy et mono threading- se debloquer quand le status spided closed sera declancher, apres l'affichage des stats
        print("crawler process finished")
        for key, val in sharedContext.items():
            print(key, "=>", val)

        #si la valuer est different de none alors il y'a erreur
        if sharedContext[messageCorrelationId]:
            raise Exception("exception durant le process")

    except Exception as e:
        print('runspider spider:%s exception:%s' % ('selogeradsspider', e))
        #raise e

    print("process_thread end")



def main():
        #logging.basicConfig(filename='selogerAdsConsumer.log', level=logging.INFO)

        parser = argparse.ArgumentParser()
        parser.add_argument('-nb','-nb=',type=int)
        parser.add_argument('-cp','-cp=')

        arg = parser.parse_args()
        print(format(arg.nb))

        print("listing start")
        hosts = [('localhost', 61613)]
        # check connection if fail or not
        conn = stomp.Connection(hosts)
        conn.start()
        conn.connect('admin', 'admin', wait=True)
        crawlingprocess = CrawlerProcess(get_project_settings())
        try:
            listner = QueueListener(conn, '/queue/scrapy.seloger.ads.queue.' + str(arg.cp), crawlingprocess,'selogeradsspider', 1)
            raise Exception("exception durant le listener")
        except Exception as e:
                print('Error in listening',e)

        for i in range(arg.nb):
            listner.start_consuming()

        input("Enter to exit")




if __name__ == "__main__":
         # execute only if run as a script
        main()
