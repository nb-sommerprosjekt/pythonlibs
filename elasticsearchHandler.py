import argparse
import io
import os
import sys
from datetime import datetime
from elasticsearch import Elasticsearch




class elasticSearchHandler:
    ElasticSearchConnection=''
    Host='null'
    Port=0
    connectionEstablished=False

    def __init__(self, Host='localhost', Port=9200):
        self.Host=Host
        self.Port=Port
        self.ElasticSearchConnection = Elasticsearch([{'host':Host,'port':Port}])
        if not self.ElasticSearchConnection.ping():
            self.connectionEstablished = False
        else:
            self.connectionEstablished = True


    def isConnected(self):
        return self.connectionEstablished


    def createIndex(self,idx,mapping=None):
        if self.connectionEstablished == False:
            return False
        if self.ElasticSearchConnection.indices.exists(idx):
            return False
        res=""
        if (mapping == None):
            res = self.ElasticSearchConnection.indices.create(index=idx, ignore=400)
        else:
            res=self.ElasticSearchConnection.indices.create(index=idx, ignore=400, body=mapping)

        if "error" in res and res['error'] and res['error']['type'] != 'resource_already_exists_exception':
            print(res)
            return False
        return True
    
    def dropIndex(self,idx):
        if self.connectionEstablished == False:
            return False
        res = self.ElasticSearchConnection.indices.delete(index=idx, ignore=[400, 404])
        if "error" in res:
            if res['error']['type'] == 'index_not_found_exception':
                return True
            return False
        return True

    def insert(self,idx,doctype,dataInJSON,id=None):
        if self.connectionEstablished == False:
            return False
        res=""
        if (id == None):
            res = self.ElasticSearchConnection.index(index=idx, doc_type=doctype, body=dataInJSON)
        else:
            res = self.ElasticSearchConnection.index(index=idx, doc_type=doctype, id=id, body=dataInJSON)

        if "error" in res:
            return False
        #self.ElasticSearchConnection.indices.refresh(idx)

        return True

    def commit(self,idx):
        if self.connectionEstablished == False:
            return False
        self.ElasticSearchConnection.indices.refresh(idx)


    def get(self,idx,doctype,id):
        if self.connectionEstablished == False:
            return False
        res = self.ElasticSearchConnection.get(index=idx, doc_type=doctype, id=id, ignore=404)
        if "error" in res:
            return None
        return res

    def search(self,idx,query):
        if self.connectionEstablished == False:
            return False
        res=self.ElasticSearchConnection.search(index=idx,body=query,size=10000)
        return res


    def listAllIndexes(self):
        if self.connectionEstablished == False:
            return False
        for index in self.ElasticSearchConnection.indices.get('*'):
            print(index)

    def snapshot(self):
        if self.connectionEstablished == False:
            return False
        self.ElasticSearchConnection.snapshot()
        for index in self.ElasticSearchConnection.indices.get('*'):
            print(index)