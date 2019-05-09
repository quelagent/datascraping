import requests
from elasticsearch import Elasticsearch



def main():

    res = requests.get('http://localhost:9200')
    print (res.content)
    es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])

    res = es.search(index='testtest2')
    print ('le contenu du res ', res)
    print ('============')
    print('Got %d ads:' % res['hits']['hits']['_source']['Realtor_Selling_Ads'])

if __name__ == "__main__":
    # execute only if run as a script
    main()
