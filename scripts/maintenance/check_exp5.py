#!/usr/bin/env python3
import chromadb
client = chromadb.HttpClient(host='192.158.1.10', port=8000)
coll = client.get_collection('faithh_knowledge_base')
docs = coll.get(ids=['exp5_parasitic_design'])
print('Found Exp 5 design:', len(docs['ids']), 'documents')
if docs['documents']:
    print('Content preview:', docs['documents'][0][:100])
