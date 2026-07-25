#!/usr/bin/env python3
import chromadb
client = chromadb.HttpClient(host='100.79.85.32', port=8000)
coll = client.get_collection('faithh_knowledge_base')
docs = coll.get(ids=['exp5_parasitic_design'])
print('Found documents:', len(docs['ids']))
print('Content preview:', docs['documents'][0][:200] if docs['documents'] else 'None')
