#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2017 Ganggao Zhu- Grupo de Sistemas Inteligentes
# gzhu[at]dit.upm.es
# DIT, UPM
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.


from flask import Flask, json, request, render_template as template
from sematch.application import Matcher
from sematch.semantic.similarity import ConceptSimilarity, WordNetSimilarity
from sematch.semantic.similarity import YagoTypeSimilarity, EntitySimilarity
from sematch.semantic.graph import DBpediaDataTransform, Taxonomy

import os

DEBUG = True
SECRET_KEY = 'Secret_development_key'
DATA_FILE = 'data/data.txt'

app = Flask(__name__)
app.config.from_object(__name__)

wn_sim = WordNetSimilarity()
yago_sim = YagoTypeSimilarity()
matcher = Matcher()
dbpedia_sim = ConceptSimilarity(Taxonomy(DBpediaDataTransform()), 'models/dbpedia_type_ic.txt')
entity = EntitySimilarity()

from search import text_lsa, text_tfidf, data

@app.route('/api/text_search')
def text_search():
    query = request.args.get('query')
    result = text_tfidf.search(query)
    result_data = []

    for doc_id, sim in result:
        result_dic = {}
        result_dic['uri'] = data[doc_id]['uri']
        result_dic['label'] = data[doc_id]['label']
        result_dic['abstract'] = data[doc_id]['abstract']
        result_dic['sim'] = sim
        result_data.append(result_dic)
    return json.dumps(result_data)

@app.route('/api/semantic_search')
def semantic_search():
    query = request.args.get('query')
    result = text_lsa.search(query)
    result_data = []
    for doc_id, sim in result:
        result_dic = {}
        result_dic['uri'] = data[doc_id]['uri']
        result_dic['label'] = data[doc_id]['label']
        result_dic['abstract'] = data[doc_id]['abstract']
        result_dic['sim'] = sim
        result_data.append(result_dic)
    return json.dumps(result_data)

@app.route('/api/entity_sim')
def entity_sim():
    e1 = request.args.get('e1')
    e2 = request.args.get('e2')
    result = []
    sim1 = {}
    sim1['name'] = 'yago concept similarity'
    sim1['sim'] = entity.similarity(e1, e2)
    result.append(sim1)
    sim2 = {}
    sim2['name'] = 'dbpedia link association'
    sim2['sim'] = entity.relatedness(e1,e2)
    result.append(sim2)
    return  json.dumps(result)

@app.route('/api/concept_sim')
def concept_sim():
    c1 = request.args.get('c1')
    c2 = request.args.get('c2')
    c_type = request.args.get('type')
    result = []
    if c_type == 'yago':
        for sim_type in ['path','lch','wup','li','res','lin','jcn','wpath','res_graph','lin_graph','jcn_graph', 'wpath_graph']:
            tmp = {}
            tmp['name'] = sim_type
            tmp['sim'] = yago_sim.yago_similarity(c1, c2,sim_type)
            result.append(tmp)
    else:
        for sim_type in ['path', 'wup', 'li', 'res', 'lin', 'jcn', 'wpath']:
            tmp = {}
            tmp['name'] = sim_type
            tmp['sim'] = dbpedia_sim.similarity(c1, c2, sim_type)
            result.append(tmp)
    return  json.dumps(result)

@app.route('/api/word_sim')
def word_sim():
    w1 = request.args.get('w1').encode('utf-8')
    lang1 = request.args.get('lang1')
    w2 = request.args.get('w2').encode('utf-8')
    lang2 = request.args.get('lang2')
    result = []
    for sim_type in wn_sim._default_metrics:
        tmp = {}
        tmp['name'] = sim_type
        tmp['sim'] = wn_sim.crossl_word_similarity(w1, w2, lang1, lang2, sim_type)
        result.append(tmp)
    return  json.dumps(result)

@app.route('/api/type_search')
def type_search():
    type = request.args.get('type').encode('utf-8')
    lang = request.args.get('lang')
    result = matcher.type_links(type, lang)
    return json.dumps(result)

@app.route('/api/entity_search')
def entity_search():
    query = request.args.get('query')
    results = matcher.match_entity_type(query)
    return json.dumps(results)

@app.route('/')
def home():
    endpoint = os.environ.get('SEMATCH_ENDPOINT', 'http://localhost:5005/api/')
    return template('sematch.html', endpoint=endpoint)

def runserver():
    host = str(os.environ.get('SEMATCH_HOST', '0.0.0.0'))
    port = int(os.environ.get('SEMATCH_PORT', 5005))
    app.run(host=host, port=port)

if __name__ == '__main__':
    runserver()
