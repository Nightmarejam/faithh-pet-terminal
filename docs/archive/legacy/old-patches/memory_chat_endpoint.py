
@app.route('/api/chat', methods=['POST'])
def chat():
    """Enhanced chat with persistent memory and RAG"""
    global CURRENT_MODEL
    start_time = datetime.now()

    try:
        data = request.json
        message = data.get('message', '')
        model = data.get('model', 'llama3.1-8b')
        use_rag = data.get('use_rag', True)

        # LOAD MEMORY
        memory = load_memory()
        memory_context = format_memory_context(memory)
        personality = get_faithh_personality()

        context = ""
        rag_results = []

        # RAG search with proper embedding dimensions
        if use_rag and CHROMA_CONNECTED:
            try:
                print(f"🔍 RAG query: {message[:60]}...")
                
                # Use smart_rag_query with all categories including chunks
                faithh_results = smart_rag_query(message, n_results=10)

                # If results found, use them
                if faithh_results['documents'] and faithh_results['documents'][0]:
                    results = faithh_results
                    docs = results['documents'][0]
                    metadatas = results['metadatas'][0]
                    distances = results['distances'][0]
                    
                    print(f"📚 Found {len(docs)} relevant documents")
                    
                    # Build context from top results
                    context_docs = []
                    for i, (doc, meta, dist) in enumerate(zip(docs, metadatas, distances)):
                        if dist < 0.9:  # Only include relevant results
                            source = meta.get('source', 'Unknown')
                            context_docs.append(f"[{i+1}] From: {source}\n{doc}\n")
                    
                    if context_docs:
                        context = "\n---\n".join(context_docs[:8])
                        print(f"✅ Using {len(context_docs[:8])} documents for context")
                else:
                    print("⚠️  No relevant documents found")
                    
            except Exception as e:
                print(f"❌ RAG error: {e}")
                import traceback
                traceback.print_exc()

        # BUILD FULL PROMPT WITH MEMORY + PERSONALITY + RAG
        system_prompt = f"""{personality}

{memory_context}

{"=" * 60}
RELEVANT CONTEXT FROM YOUR KNOWLEDGE BASE:
{context if context else "No specific context found for this query."}
{"=" * 60}

Now respond to the user's message below, using the context naturally."""

        full_prompt = f"{system_prompt}\n\nUser: {message}\n\nFAITHH:"

        # CALL OLLAMA
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': full_prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'top_p': 0.9
                    }
                },
                timeout=120
            )

            if response.status_code == 200:
                result = response.json()
                reply = result.get('response', '').strip()
                
                # UPDATE MEMORY with this conversation
                memory = update_recent_topics(memory, message, reply)
                
                # Increment session stats
                if "session_stats" not in memory:
                    memory["session_stats"] = {"total_queries": 0}
                memory["session_stats"]["total_queries"] = memory["session_stats"].get("total_queries", 0) + 1
                memory["session_stats"]["last_query_date"] = datetime.now().isoformat()
                
                # Save updated memory
                save_memory(memory)
                
                # AUTO-INDEX THIS CONVERSATION INTO RAG
                try:
                    conversation_text = f"USER: {message}\n\nFAITHH: {reply}"
                    doc_id = f"live_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    
                    collection.add(
                        ids=[doc_id],
                        documents=[conversation_text],
                        metadatas=[{
                            "source": f"FAITHH Live Session - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                            "category": "faithh_live_session",
                            "timestamp": datetime.now().isoformat(),
                            "type": "conversation"
                        }]
                    )
                    print(f"💾 Auto-indexed conversation: {doc_id}")
                except Exception as e:
                    print(f"⚠️  Could not auto-index conversation: {e}")

                return jsonify({
                    'success': True,
                    'response': reply,
                    'model': model,
                    'rag_used': bool(context),
                    'memory_loaded': True,
                    'processing_time': (datetime.now() - start_time).total_seconds()
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f'Model error: {response.status_code}'
                }), 500

        except requests.exceptions.Timeout:
            return jsonify({
                'success': False,
                'error': 'Request timeout - model took too long to respond'
            }), 504
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Error calling model: {str(e)}'
            }), 500

    except Exception as e:
        print(f"❌ Chat error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
