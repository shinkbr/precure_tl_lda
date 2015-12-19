#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from collections import OrderedDict
from gensim import corpora, models, similarities
from itertools import chain
from peewee import *
import code
import datetime
import dateutil.parser
import dateutil.tz
import igraph
import logging
import math
import matplotlib.pyplot as pyplot
import MeCab
import os
import pickle
import re

# logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

db = SqliteDatabase('tweets.db')
num_topics = 5

titles = {
        1: '私がプリンセス？キュアフローラ誕生！',
        2: '学園のプリンセス！登場キュアマーメイド！',
        3: 'もうさよなら？パフを飼ってはいけません！',
        4: 'キラキラきららはキュアトゥインクル？',
        5: '3人でGO！私たちプリンセスプリキュア！',
        6: 'レッスンスタート！めざせグランプリンセス！',
        7: 'テニスで再会！いじわるな男の子！？',
        8: 'ぜったいムリ！？はるかのドレスづくり！',
        9: '幕よあがれ！憧れのノーブルパーティ！',
        10: 'どこどこ？新たなドレスアップキー！',
        11: '大大大ピンチ！？プリキュアVSクローズ！',
        12: 'きららとアイドル！あつ〜いドーナッツバトル！',
        13: '冷たい音色・・・！黒きプリンセス現る！',
        14: '大好きのカタチ！春野ファミリーの夢！',
        15: '大変身ロマ！アロマの執事試験！',
        16: '海への誓い！みなみの大切な宝物！',
        17: 'まぶしすぎる！きらら、夢のランウェイ！',
        18: '絵本のヒミツ！プリンセスってなぁに？',
        19: 'はっけ～ん！寮でみつけたタカラモノ！',
        20: 'カナタと再会！？いざ、ホープキングダムへ！',
        21: '想いよ届け！プリンセスVSプリンセス！',
        22: '希望の炎！その名はキュアスカーレット！',
        23: 'ず～っと一緒！私たち4人でプリンセスプリキュア！',
        24: '笑顔がカタイ？ルームメイトはプリンセス！',
        25: 'はるかのおうちへ！はじめてのおとまり会！',
        26: 'トワ様を救え！戦うロイヤルフェアリー！',
        27: 'ガンバレゆうき！応援ひびく夏祭り！',
        28: '心は一緒！プリキュアを照らす太陽の光！',
        29: 'ふしぎな女の子？受けつがれし伝説のキー！',
        30: '未来へ！チカラの結晶、プリンセスパレス！',
        31: '新学期！新たな夢と新たなる脅威！',
        32: 'みなみの許嫁！？帰ってきたスーパーセレブ！',
        33: '教えてシャムール♪願い叶える幸せレッスン！',
        34: 'ピンチすぎる～！はるかのプリンセスコンテスト！',
        35: 'やっと会えた…！カナタと失われた記憶！',
        36: '波立つ心…！みなみの守りたいもの！',
        37: 'はるかが主役！？ハチャメチャロマンな演劇会！',
        38: '怪しいワナ…！ひとりぼっちのプリンセス！',
        39: '夢の花ひらく時！舞え、復活のプリンセス！',
        40: 'トワの決意！空にかがやく希望の虹！',
        41: 'ゆいの夢！想いはキャンバスの中に…！',
        42: '夢かプリキュアか！？輝くきららの選ぶ道！',
        43: '一番星のきらら！夢きらめくステージへ！',
        44: '湧き上がる想い！みなみの本当のキモチ！'
        }

date_to_epnum = {
        datetime.date(2015, 2, 1): 1,
        datetime.date(2015, 2, 8): 2,
        datetime.date(2015, 2, 15): 3,
        datetime.date(2015, 2, 22): 4,
        datetime.date(2015, 3, 1): 5,
        datetime.date(2015, 3, 8): 6,
        datetime.date(2015, 3, 15): 7,
        datetime.date(2015, 3, 22): 8,
        datetime.date(2015, 3, 29): 9,
        datetime.date(2015, 4, 5): 10,
        datetime.date(2015, 4, 12): 11,
        datetime.date(2015, 4, 19): 12,
        datetime.date(2015, 4, 26): 13,
        datetime.date(2015, 5, 3): 14,
        datetime.date(2015, 5, 10): 15,
        datetime.date(2015, 5, 17): 16,
        datetime.date(2015, 5, 24): 17,
        datetime.date(2015, 5, 31): 18,
        datetime.date(2015, 6, 7): 19,
        datetime.date(2015, 6, 14): 20,
        datetime.date(2015, 6, 28): 21,
        datetime.date(2015, 7, 5): 22,
        datetime.date(2015, 7, 12): 23,
        datetime.date(2015, 7, 19): 24,
        datetime.date(2015, 7, 26): 25,
        datetime.date(2015, 8, 2): 26,
        datetime.date(2015, 8, 9): 27,
        datetime.date(2015, 8, 16): 28,
        datetime.date(2015, 8, 23): 29,
        datetime.date(2015, 8, 30): 30,
        datetime.date(2015, 9, 6): 31,
        datetime.date(2015, 9, 13): 32,
        datetime.date(2015, 9, 20): 33,
        datetime.date(2015, 9, 27): 34,
        datetime.date(2015, 10, 4): 35,
        datetime.date(2015, 10, 11): 36,
        datetime.date(2015, 10, 18): 37,
        datetime.date(2015, 10, 25): 38,
        datetime.date(2015, 11, 8): 39,
        datetime.date(2015, 11, 15): 40,
        datetime.date(2015, 11, 22): 41,
        datetime.date(2015, 11, 29): 42,
        datetime.date(2015, 12, 6): 43,
        datetime.date(2015, 12, 13): 44
        }

epnum_to_member = {
        1: 0,
        2: 1,
        3: 4,
        4: 2,
        5: 2,
        6: 0,
        7: 0,
        8: 0,
        9: 1,
        10: 4,
        11: 4,
        12: 2,
        13: 3,
        14: 0,
        15: 4,
        16: 1,
        17: 2,
        18: 0,
        19: 4,
        20: 4,
        21: 4,
        22: 3,
        23: 3,
        24: 3,
        25: 3,
        26: 4,
        27: 4,
        28: 3,
        29: 4,
        30: 4,
        31: 4,
        32: 1,
        33: 4,
        34: 0,
        35: 4,
        36: 1,
        37: 0,
        38: 0,
        39: 0,
        40: 3,
        41: 4,
        42: 2,
        43: 2,
        44: 1
        }

member_to_color = {0: 'pink', 1: 'blue', 2: 'yellow', 3: 'red', 4: 'white'}

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
    timelines = load_pickle('analyzed_timelines.pickle').values()

    dictionary = corpora.Dictionary(timelines)
    # dictionary.filter_extremes(no_below = 0, no_above = 0.5)
    dictionary.save('models/precure_tl.dict')

    corpus = [dictionary.doc2bow(i) for i in timelines]
    corpora.MmCorpus.serialize('models/precure_tl.mm', corpus)

    lda = models.ldamulticore.LdaMulticore(corpus,
            id2word = dictionary,
            workers = 4,
            num_topics = num_topics,
            passes = 5)
    lda.save('models/precure_tl_%s_topics.lda' % num_topics)

    # hdp = models.hdpmodel.HdpModel(corpus, id2word = dictionary)
    # hdp.save('models/precure_tl.hdp')

    # sim = similarities.MatrixSimilarity(lda.get_document_topics(corpus))
    # sim.save("models/precure_tl_similarity.index")

def load_models():
    global _dictionary, _corpus, _lda, _hdp, _sim
    _dictionary = corpora.Dictionary.load('models/precure_tl.dict')
    _corpus = corpora.MmCorpus('models/precure_tl.mm')
    _lda = models.ldamodel.LdaModel.load('models/precure_tl_%s_topics.lda' % num_topics)
    # _hdp = models.ldamodel.LdaModel.load('models/precure_tl.hdp')
    # _sim = similarities.docsim.Similarity.load(('models/precure_tl_similarity.index'))

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
        _tweets = list(Tweet.select())
        return _tweets

def group_by_date():
    tmp = defaultdict(list)
    for i in get_tweets():
        if i.text[:3] == 'RT ':
            continue
        tmp[i.get_created_at().date()].append(i)

    tweets = OrderedDict()
    for i in sorted(tmp.keys()):
        tweets[i] = tmp[i]

    return tweets

def get_analyzed_timelines():
    global _analyzed_timelines

    try:
        return _analyzed_timelines
    except:
        _analyzed_timelines =  analyze_timelines(group_by_date())
        return _analyzed_timelines

def analyze_timelines(timelines):
    analyzed_timelines = OrderedDict()
    m = MeCab.Tagger("-d /usr/local/lib/mecab/dic/mecab-ipadic-neologd")
    stop_words = ['し', 'さん', 'の', 'ん', 'てる', 'ちゃん',
            'この', 'れ', 'これ', 'あ', 'する', 'さ', 'そう', 'お', 
            'こと', 'て', 'なっ', 'い', 'き', 'ー', '0', 'すぎ', 'また', '何',
            'ここ', 'もう', 'w', '3', 'え', 'れる', 'すぎる', '2', 'ご',
            'み', 'なん', '1', 'それ', 'やっ', 'どう', 'せ', 'あっ', 'その',
            'www', 'っ', 'られ', 'ら', '4', '5', 'いる', 'ある', 'プリキュア', 'プリンセス']

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
                if node.surface in stop_words:
                    node = node.next
                    continue
                doc.append(node.surface)
                node = node.next
        analyzed_timelines[k] = doc

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

def get_similarity_index(timelines):
    global _sim

    try:
        return _sim
    except:
        corpus = [_dictionary.doc2bow(tl) for tl in timelines.values()]
        _sim = similarities.MatrixSimilarity(_lda[corpus])

def get_edges(threshold = 0.9):
    topics = _lda[_corpus]
    _sim = similarities.MatrixSimilarity(topics, num_features = num_topics)

    edges = []
    for i, t in enumerate(topics):
        sim = _sim[t]
        for j, s in enumerate(sim):
            if i >= j:
                continue
            print("%s %s %s" % (s, _index_to_title[i], _index_to_title[j]))
            if s >= threshold:
                edges.append((i, j))

    return edges

def sim_dist(timelines):
    sim = get_similarity_index(timelines.values)
    edges = []

    count = defaultdict(lambda: 0)

    for i, tl in enumerate(timelines):
        corpus = _dictionary.doc2bow(tl)
        topics = _lda[corpus]
        for j, s in enumerate(sim[topics]):
            if j <= i:
                continue
            count[math.floor(s * 10)] += 1

    return count

def draw_ig_graph(timelines, index_to_title, threshold = 0.9):
    g = igraph.Graph()
    g.add_vertices(len(timelines))
    edges = get_edges(threshold = threshold)
    g.add_edges(edges)

    for i, v in enumerate(g.vs):
        epnum = date_to_epnum[timelines.keys()[i]]
        v['label'] = epnum
        v['color'] = member_to_color[epnum_to_member[epnum]]
    igraph.plot(g, 'graph_kk.png', bbox = (4000, 4000), layout = g.layout('kk'))

def print_similar(index_to_title, threshold = 0.9):
    topics = _lda[_corpus]
    for i, t in enumerate(topics):
        sim = _sim[t]
        for j, s in enumerate(sim):
            if i >= j:
                continue
            if s < threshold:
                continue
            print("%s %s %s" % (s, index_to_title[i], index_to_title[j]))

def count_words(timelines, order=1):
    flattened = list(chain.from_iterable(timelines.values()))
    count = defaultdict(lambda: 0)

    for i in flattened:
        count[i] += 1

    for k, v in sorted(count.items(), key=lambda x:x[1]*order):
        print("%s %s" % (k, v))

if __name__ == '__main__':
    '''
    global _index_to_title
    load_models()
    timelines = load_pickle('analyzed_timelines.pickle')
    _index_to_title = [titles[date_to_epnum[i]] for i in timelines.keys()]

    threshold = 0.99
    draw_ig_graph(timelines, _index_to_title, threshold = threshold)
    '''

    '''
    timelines = load_pickle('analyzed_timelines.pickle')
    count_words(timelines, order = -1)
    '''

    '''
    gbd = load_pickle('group_by_date.pickle')
    at = analyze_timelines(gbd)
    count_words(at)
    '''

    gbd = group_by_date()
    # at = analyze_timelines(gbd)
    # calculate_models()
    code.interact(local=locals())
