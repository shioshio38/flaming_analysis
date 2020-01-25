#!/usr/bin/env python3
# -*- coding:utf-8 -*-
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import sys
sys.path.append('lib')
from fetch_tweet import FetchTweet
from mog_op import MongoOp
import os
from dateutil.relativedelta import relativedelta
from datetime import datetime,timezone,timedelta
import logging
import time

JST=timezone(timedelta(hours=+9), 'JST')

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',level=logging.INFO)

DATABASE = os.environ.get('MONGO_DB')
MONGO_HOST = os.environ.get('MONGO_HOST')
COLLECTION = os.environ.get('COLLECTION')

def get_tw():
    query=u'"猿" OR "雉"'
    until=datetime(2020,1,21)
    mp=MongoOp(MONGO_HOST,COLLECTION,db=DATABASE)
    ft=FetchTweet(mp)
    logging.info(u"until={}".format(until))
    ft.term(until)
    ft.query(query)
    ft.invoke_fetch()

def main():
    get_tw()
if __name__=='__main__':main()
