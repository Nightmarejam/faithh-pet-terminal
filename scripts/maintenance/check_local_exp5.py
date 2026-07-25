#!/usr/bin/env python3
import chromadb
client = chromadb.HttpClient(host='localhost', port=8000)
coll = client.get_collection('faithh_knowledge_base')
docs = coll.get(ids=['exp5_parasitic_design'])
print('Local Exp 5 design:', len(docs['ids']), 'documents')
print('Total docs in local:', coll.count())
