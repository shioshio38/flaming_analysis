#!/usr/bin/env python3
# -*- coding:utf-8 -*-

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os
from datetime import datetime,timezone,timedelta
JST=timezone(timedelta(hours=+9), 'JST')
import logging
from pymongo import MongoClient,ASCENDING
MONGO_HOST=os.environ.get("MONGO_HOST")
MONGO_USER=os.environ.get("MONGO_USER")
PASSWORD=os.environ.get("PASSWORD")
AUTHSOURCE=os.environ.get("AUTHSOURCE")

class MongoOp(object):
    def __init__(self,host,col,db='twitter'):
        self.mp = MongoClient(MONGO_HOST,
                                      27017,
                                      username=MONGO_USER,
                                      password=PASSWORD,
                                      authSource=AUTHSOURCE,
                                      authMechanism='SCRAM-SHA-1')
        self.db=self.mp[db]
        self.col=self.db[col]
        self.col.create_index('created_at')
        self.col.create_index([('id',ASCENDING),('text',ASCENDING)])

    def __del__(self):
        if self.mp:
            self.mp.close()
    def conv_date(self):
        for i,a in enumerate(self.col.find({"created_at":{"$type":"string"}},{"created_at":1})):
            dt=a['created_at']
            dt=datetime.strptime(dt,"%a %b %d %H:%M:%S %z %Y")
            logging.info("i={} dt={}".format(i,dt))
            aid=a['_id']
            self.col.update({'_id':aid},{"$set":{"created_at":dt}})
    
    def insert_data(self,d):
        tids=[]
        crdate=None
        if 'modules' in d:
            for i,a in enumerate(d['modules']):
                if not 'status' in a:continue
                a=a['status']['data']
                tid=int(a['id'])
                tids.append(tid)
                if 'full_text' in a: #for tweet_mode=extended
                    a['text']=a['full_text']
                    del(a['full_text'])
                text=a['text']
                dt=a['created_at']
                dt=datetime.strptime(dt,"%a %b %d %H:%M:%S %z %Y")
                a['created_at']=dt
                crdate=dt
                if i==0:
                    dt0=dt.replace(tzinfo=JST)
                    logging.info("tid={} created_at(JST)={} text={}".format(tid,dt0,text))
                c=self.col.find_one({"$and":[{'id':tid},{'text':text}]})
                if len(text)>500:
                    logging.info("tid={} created_at={} text_size={} text={}".format(tid,dt,len(text),text))
                    a['text']=a['text'][:500] #avoid Index too learge
                if (not c):
                    self.col.insert_one(a)
        mint=-1
        if len(tids)>0:
            mint=min(tids)
        return mint,crdate
        
