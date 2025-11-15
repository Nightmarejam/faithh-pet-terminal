
@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests with optional RAG"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        model = data.get('model', 'llama3.1-8b')
        use_rag = data.get('use_rag', False)  # READ RAG PARAMETER
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Build context
        context = ""
        
        # USE RAG IF ENABLED
        if use_rag:
            try:
                print(f"🔍 RAG enabled for query: {message[:50]}...")
                
                # Call our smart RAG query function
                rag_results = smart_rag_query(message, n_results=10)
                
                if rag_results and rag_results.get('documents'):
                    docs = rag_results['documents'][0]
                    metadatas = rag_results['metadatas'][0]
                    
                    print(f"📚 Retrieved {len(docs)} documents from RAG")
                    
                    # Build context from documents
                    context = "\n\n".join([
                        f"--- Document {i+1}: {meta.get('source', 'Unknown')} ---\n{doc}"
                        for i, (doc, meta) in enumerate(zip(docs, metadatas))
                    ])
                    
                    context = f"Relevant context from your documents:\n\n{context}\n\n---\n\n"
                else:
                    print("⚠️  RAG query returned no results")
            except Exception as e:
                print(f"❌ RAG error: {e}")
                # Continue without RAG if it fails
        
        # Build full prompt
        system_prompt = """You are FAITHH, a helpful AI assistant. Use the provided context to answer questions accurately.
If context is provided, reference it in your answer. If no context is available, say so."""
        
        full_prompt = f"{system_prompt}\n\n{context}User: {message}\n\nAssistant:"
        
        # Call Ollama
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': full_prompt,
                    'stream': False
                },
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                reply = result.get('response', 'No response generated')
                
                return jsonify({
                    'response': reply,
                    'model': model,
                    'rag_used': use_rag and bool(context)
                })
            else:
                return jsonify({'error': f'Ollama error: {response.status_code}'}), 500
                
        except Exception as e:
            return jsonify({'error': f'Error calling model: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
