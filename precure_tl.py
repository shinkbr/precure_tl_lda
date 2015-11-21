#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from gensim import corpora, models, similarities
from itertools import chain
from peewee import *
import code
import dateutil.parser
import dateutil.tz
import logging
import MeCab
import os
import pickle
import re

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

db = SqliteDatabase('tweets.db')

class PrecureTLModel(Model):
    class Meta:
        database = db

class Tweet(PrecureTLModel):
    created_at = DateTimeField()
    text = TextField(db_column = 'tweet_text')

    def get_created_at(self):
        return  dateutil.parser.parse(self.created_at) \
                .astimezone(dateutil.tz.tzlocal())

    class Meta:
        db_table = 'timeline_concat'

def calculate_models():
    timelines = load_pickle('analyzed_timelines.pickle')

    dictionary = corpora.Dictionary(timelines)
    dictionary.save('models/precure_tl.dict')

    corpus = [dictionary.doc2bow(i) for i in timelines]
    corpora.MmCorpus.serialize('models/precure_tl.mm', corpus)

    lda = models.ldamulticore.LdaMulticore(corpus, id2word = dictionary, workers = 4, num_topics = 5)
    lda.save('models/precure_tl.lda')

    hdp = models.hdpmodel.HdpModel(corpus, id2word = dictionary)
    hdp.save('models/precure_tl.hdp')

    sim = similarities.MatrixSimilarity(lda.get_document_topics(corpus))
    sim.save("models/precure_tl_similarity.index")

def load_models():
    global _dictionary, _corpus, _lda, _hdp, _sim
    _dictionary = corpora.Dictionary.load('models/precure_tl.dict')
    _corpus = corpora.MmCorpus('models/precure_tl.mm')
    _lda = models.ldamodel.LdaModel.load('models/precure_tl.lda')
    _hdp = models.ldamodel.LdaModel.load('models/precure_tl.hdp')
    _sim = similarities.docsim.Similarity.load(('models/precure_tl_similarity.index'))

def dump_pickle(var, file_name):
    f = open('pickle/' + file_name, 'wb')
    pickle.dump(var, f)
    f.close()

def load_pickle(file_name):
    f = open('pickle/' + file_name, 'rb')
    v = pickle.load(f)
    f.close()
    return v

def get_tweets():
    global _tweets

    try:
        return _tweets
    except:
        if os.environ.get('LIMIT') == 'NONE':
            _tweets = list(Tweet.select())
        else:
            _tweets = list(Tweet.select().limit(80000))
        return _tweets

def group_by_date():
    tweets = defaultdict(list)

    for i in get_tweets():
        tweets[i.get_created_at().date()].append(i)

    return tweets

def get_analyzed_timelines():
    global _analyzed_timelines

    try:
        return _analyzed_timelines
    except:
        _analyzed_timelines =  analyze_timelines(group_by_date())
        return _analyzed_timelines

def analyze_timelines(timelines):
    analyzed_timelines = []
    m = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
    for k, v in timelines.items():
        doc = []
        for i in v:
            text = strip_stopwords(i.text)
            node = m.parseToNode(text.encode('utf-8'))
            while node:
                feature = node.feature.split(',')
                if feature[0] in ["助詞", "助動詞", "記号", "BOS/EOS"]:
                    node = node.next
                    continue
                doc.append(node.surface)
                node = node.next
        analyzed_timelines.append(doc)

    return analyzed_timelines

def strip_stopwords(text):
    text = re.sub(r'^(RT)', '', text)
    text = re.sub(r'@[A-z]+', '', text)
    text = re.sub(r'#[^\s]+', '', text)
    text = re.sub(r'(https?:\/\/)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)', '', text)

    return text

def count_words(documents):
    flattened = list(chain.from_iterable(documents))
    count = defaultdict(lambda: 0)

    for i in flattened:
        count[i] += 1

    for k, v in sorted(count.items(), key=lambda x:x[1]):
        print("%s %s" % (k, v))

    return count

# timelines = morphologically analyzed timelines
def topic_dist(timelines):
    for tl in timelines:
        corpus = _dictionary.doc2bow(tl)
        print(_lda[corpus])

if __name__ == '__main__':
    code.interact(local=locals())
