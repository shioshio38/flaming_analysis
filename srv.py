#!/usr/bin/env python
# coding: utf-8
import sys
sys.path.append('lib')
from mog_op import MongoOp
from flask import Flask, render_template,g,request,url_for
app = Flask(__name__) 
import re
import json
import logging
logging.basicConfig(level=logging.INFO)
import pytz
from datetime import datetime
timezone = pytz.timezone('Asia/Tokyo')
from date_dict import date_dict
from scipy import stats
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
import os
DATABASE = os.environ.get('MONGO_DB')
MONGO_HOST = os.environ.get('MONGO_HOST')
COLLECTION = os.environ.get('COLLECTION')
@app.before_request
def connect():
    app.logger.info('MONGO_HOST={} DATABASE={}'.format(MONGO_HOST,DATABASE))
    g.client=MongoOp(MONGO_HOST,COLLECTION,DATABASE)

@app.route("/") #アリケーションルートにアクセスが合った場合
def index(): #hello関数が動作します。
    pipeline=[
        {"$group":{"_id":"$packet_id","count":{"$sum":1}}}
    ]
    rdkt={}
    for c,v in g.client.coldict.items():
        rdkt.setdefault(c,[])
        for a in v.aggregate(pipeline):
            rdkt[c].append(a)
        rdkt[c]=sorted(rdkt[c],key=lambda x:x['count'],reverse=True)
    return render_template('index.html',coldict=g.client.coldict,rdkt=rdkt)

class KInfo(object):
    def __init__(self,k):
        self.k=k
    def insert(self,cnt,cnt2,outs,eval_data,eval_user,other_user,interval_data):
        self.cnt=cnt
        self.cnt2=cnt2
        self.outs=outs
        self.eval_data=eval_data
        self.eval_user=eval_user
        tall=sum([a for a in eval_data.values()])
        self.tall=tall
        self.other=self.cnt-tall
        uall=sum([a for a in eval_user.values()])
        self.uall=uall
        self.other_user=other_user-uall
        self.interval_data = interval_data
@app.route('/set_info')
def set_info():
    app.logger.info(request)
    did=request.args.get('did')
    ev=request.args.get('event')
    col_name=request.args.get('col_name')
    col=g.client.coldict.get(col_name)
    app.logger.info("col_name={} col={}".format(col_name,col))
    did=int(did)
    if ev=='reset':
        r=col.update_one({'id':did},{'$unset':{
            'other':None,
            'adovocacy':None,
            'criticism':None,
            'intoline':None,
            'impression':None,
            'unknown':None,
            'irrelevant':None,
            'duplicate':None,
        }})
    else:
        r=col.update_one({'id':did},{"$set":{ev:True}})
    dkt=dict(did=did,ev=ev,r=str(r))
    return json.dumps(dkt)

class TweetInfo(object):
    def __init__(self,k,st,ed,col,packet_id):
        self.k=k
        self.st=st
        self.ed=ed
        self.col=col
        self.packet_id=packet_id
    def __str__(self):
        return 'k={} st={} ed={} col={} packet_id={}'.\
            format(self.k,self.st,self.ed,self.col.name,self.packet_id)
    def __gen_interval(self,eval_data):
        interval_data = {}        
        samplesize = sum([v for k,v in eval_data.items()])
        if samplesize == 0:
            for k in eval_data:
                interval_data[k]='0.0%'
            return interval_data
        alpha = 0.95
        for k,v in eval_data.items():
            p = 1.0 * v / samplesize
            (buttom,up) = stats.binom.interval(alpha = alpha,
                                              n = samplesize,
                                              p = p,
                                              loc = 0)
            if v == 0:
                buttom = 0
            interval_data[k]="{:.1f}% - {:.1f}%".format(100*buttom/samplesize,100*up/samplesize)
        return interval_data
    def gen(self):
        ki=KInfo(self.k)
        dkt={'created_at':{"$gt":self.st,"$lt":self.ed}}
        cnt=self.col.find(dkt).count()
        other_user = len(self.col.distinct('user.id',dkt))
        eval_data={}
        eval_user={}
        for attrk in ("criticism","intoline","adovocacy",'other','unknown','irrelevant','duplicate','impression'):
            dkt={'created_at':{"$gt":self.st,"$lt":self.ed},attrk:True}
            c=self.col.count(dkt)
            eval_data[attrk]=c
            eval_user[attrk]=len(self.col.distinct('user.id',dkt))
        interval_data = self.__gen_interval(eval_data)
        outs=[]
        dkt={'created_at':{"$gt":self.st,"$lt":self.ed}}
        if self.packet_id:
            dkt['packet_id']=self.packet_id
        for i,a in enumerate(self.col.find(dkt).limit(1000).sort([('created_at',1)])):
            a['href']='https://twitter.com/{}/status/{}'.format(a['user']['screen_name'],a['id'])
            a['user_name']=a['user']['name']
            a['number']=i+1
            if 'quoted_status' in a and 'text' in a['quoted_status']:
                a['text']=a["quoted_status"]['text']+" "+a['text']
            outs.append(a)
        cnt2=len(outs)
        logging.info(dkt)
        ki.insert(cnt,cnt2,outs,eval_data,eval_user,other_user,interval_data)
        return ki

@app.route('/get_data/<col_name>')
def get_data(col_name):
    outd={}
    col=g.client.coldict[col_name]
    packet_id=request.args.get('packet_id')
    first_one,last_one = g.client.get_date_range(col)
    tsrc = date_dict.get(col_name,[('all',first_one,last_one)])
    app.logger.info(tsrc)
    pipeline=[
        {"$group":{"_id":"$packet_id","count":{"$sum":1}}}
    ]
    packet_list=[]
    for a in col.aggregate(pipeline):
        packet_list.append(a)
    packet_list=sorted(packet_list,key=lambda x:x['count'],reverse=True)
    for k,st,ed in tsrc:
        tw=TweetInfo(k,st,ed,col,packet_id)
        outd[k]=tw.gen()
    return render_template('get_data.html',outd=outd,col_name=col_name,packet_id=packet_id,packet_list=packet_list) 

if __name__ == "__main__":
    # webサーバー立ち上げ
    app.run(host='0.0.0.0',debug=True,port=5000)
