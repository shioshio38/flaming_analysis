#!/usr/bin/env python3
# -*- coding:utf-8 

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os
import requests
from requests_oauthlib import OAuth1
import json
from dateutil.relativedelta import relativedelta
from datetime import datetime,timezone,timedelta
import logging
import time
import pprint
from mog_op import MongoOp
import copy
import pymongo
JST=timezone(timedelta(hours=+9), 'JST')

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',level=logging.INFO)

AT=os.environ.get('access_token')
ATS=os.environ.get("access_token_secret")
CK=os.environ.get('consumer_key')
CKS=os.environ.get('consumer_key_secret')

auth = OAuth1(CK,CKS,AT,ATS)

TWITTER_SEARCH_URL='https://api.twitter.com/1.1/search/tweets.json'

class FetchTweet(object):
    def __init__(self,mp):
        self.mp=mp
        self.old_mid=-1
        self.mid=-1
        self.crlist=[]
        self.thdate=None
        self.rate_limit_limit=180
        self.rate_limit_remaining=180
        self.rate_limit_lower_limit = int(180*0.2)
    def query(self,query):
        self.query=query
    def term(self,end):
        start = end - timedelta(days=7)
        self.thdate = start.replace(tzinfo=None)
        self.until = end.strftime('%Y-%m-%d')
    def invoke_fetch(self):
        cnt=0
        while True:
            logging.info("-"*200)
            d=self.__get_tweet(self.query,self.mid)
            logging.debug(u"d={}".format(d.keys()))
            if not d:
                logging.error(u"d {} is None".format(d))
                break
            self.mid,crdate=self.mp.insert_data(d)
            if cnt%60==0 and crdate:
                dt=crdate+timedelta(hours=9)
                dt=dt.replace(tzinfo=JST)
                msg=u"query={} cnt={} created_at={} UST {} JST".format(self.query,cnt,crdate,dt)
                logging.info(msg)
            if self.mid==self.old_mid:
                logging.error("finish mid={} old_mid={}".format(self.mid,self.old_mid))
                break
            if self.old_mid:
                differ=self.mid-self.old_mid
                msg="time sleep c={} mid={} old_mid={} differ={}".format(cnt,self.mid,self.old_mid,differ)
                logging.info(msg)
            if crdate and self.thdate >= crdate.replace(tzinfo=None):
                logging.error("finish thdate={} crdate={}".format(self.thdate,crdate))
                break
            if self.mid and self.mid==-1:
                logging.error("finish mid={}".format(self.mid))
                break
            if crdate:
                c2=sorted(self.crlist)
                if len(c2) > 10:
                    ccd=c2[9]
                    if crdate>ccd:
                        logging.error("finish cdate={} ccd={}".format(crdate,ccd))
                        break
                self.crlist.append(copy.copy(crdate))
            self.old_mid=self.mid
            self.mid=self.mid-1
            cnt+=1
            time.sleep(10)
            if self.rate_limit_lower_limit  > self.rate_limit_remaining:
                time.sleep(100)
    def __get_rate_limit(self,headers):
        self.rate_limit_limit_remaing = int(headers['x-rate-limit-remaining'])
        self.rate_limit_limit=int(headers['x-rate-limit-limit'])
        self.rate_limit_lower_limit = int(self.rate_limit_limit*0.2)
        
    def __get_tweet(self,search_word,max_id=None):
        logging.info("max_id={}".format(max_id))
        cnt=100
        url=TWITTER_SEARCH_URL
        params = {
            "q": search_word,
            "result_type": "recent",
            "count": cnt,
            'until':self.until
        }
        if max_id > 0:
            params['max_id'] = max_id
        logging.info(params)
        r = requests.get(url, auth=auth, params=params)
        self.__get_rate_limit(r.headers)
        if r.status_code != 200:
            logging.error("Error code: {} {}".format(r.status_code,r))
            return None
        return r.json()

