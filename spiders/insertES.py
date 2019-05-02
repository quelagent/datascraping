"""
from elasticsearch import Elasticsearch
from pprint import pprint
import json

class InsertEs :

    with open('seloger.json', 'r', encoding='utf-8') as data_file:
        data = json.load(data_file)
        #pprint(data)


        es = Elasticsearch('localhost:9200',use_ssl=False,verify_certs=True)

        if es.ping():
            print('Connection successfully')
        else:
            print('sorry it couldnt connect!')



        try:
            if es.indices.exists("d"):
                print("Index already exists")
            if not es.indices.exists("d"):
                # Ignore 400 means to ignore "Index Already Exist" error.
                es.indices.create(index="d", ignore=400, body=data)
                print('Created Index')
            created = True
        except Exception as ex:
            print(str(ex))
        try:
            es.index(index="d", doc_type="Adsursd", body=data, request_timeout=30)

        except Exception as ex:
            print('Error in indexing data')
            print(str(ex))

"""
"""
        res = es.get(index="adurls", doc_type="Adurls",id="44VhSGkBm5rx4ldDTISy")
        print(res)
"""