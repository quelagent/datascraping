import requests, json, os
from elasticsearch import Elasticsearch



def main():

    res = requests.get('http://localhost:9200')
    print (res.content)
    es = Elasticsearch([{'host': 'localhost', 'port': '9200'}])


if __name__ == "__main__":
    # execute only if run as a script
    main()
