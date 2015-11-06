#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from peewee import *
import code
import dateutil.parser
import dateutil.tz
import MeCab

db = SqliteDatabase('tweets.db')

class PrecureTLModel(Model):
    class Meta:
        database = db

class TweetModel(PrecureTLModel):
    created_at = DateTimeField()
    text = TextField(db_column = 'tweet_text')

    def get_created_at(self):
        return  dateutil.parser.parse(self.created_at) \
                .astimezone(dateutil.tz.tzlocal())

    class Meta:
        db_table = 'timeline_concat'

def get_tweets():
    global _tweets

    try:
        return _tweets
    except:
        _tweets = list(TweetModel.select().limit(10000))
        return _tweets

def group_by_date():
    tweets = defaultdict(list)

    for i in get_tweets():
        tweets[i.get_created_at().date()].append(i)

    return tweets

def parse_timelines(timelines):
    m = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
    for k, v in timelines.items():
        for i in v:
            print(i)
            break
        break

if __name__ == '__main__':
    timelines = group_by_date()
    parse_timelines(timelines)
    code.interact(local=locals())
