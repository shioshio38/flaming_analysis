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

def get_tw():
    query=u'"動物" OR "猫"'
    params={'lang':'ja','include':'retweets'}
    start=datetime(2020,1,20)
    end=datetime(2020,1,21)
    logging.info(u"start={} end={}".format(start,end))
    col='cat'
    mp=MongoOp('localhost',col,db='twitter_fetch')
    ft=FetchTweet(mp)
    logging.info(u"start={} end={}".format(start,eday))
    ft.term(start,eday)
    ft.query(query)
    ft.params(params)
    ft.invoke_fetch()

def main():
    get_tw()
if __name__=='__main__':main()
