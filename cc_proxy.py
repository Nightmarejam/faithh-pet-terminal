import os, re, requests
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
TARGET_MODEL = "openai/gpt-oss-120b"

@app.route("/", methods=["GET", "HEAD"])
def health():
    return jsonify({"status": "ok", "engine": "groq", "model": TARGET_MODEL})

@app.route("/v1/models", methods=["GET"])
def models():
    return jsonify({"data": [{"id": "claude-sonnet-4-6"}, {"id": "claude-opus-4-7"}]})

@app.route("/v1/messages", methods=["POST"])
@app.route("/v1/messages/<path:p>", methods=["POST", "GET"])
def messages(p=""):
    if not GROQ_API_KEY:
        return jsonify({"error": "GROQ_API_KEY not set"}), 500
    data = request.get_json(force=True) or {}
    system_prompt = data.get("system", "")
    msgs = []
    if system_prompt:
        if isinstance(system_prompt, str):
            msgs.append({"role": "system", "content": system_prompt})
        else:
            msgs.append({"role": "system", "content": " ".join(b.get("text","") for b in system_prompt if isinstance(b, dict))})
    for m in data.get("messages", []):
        c = m.get("content", "")
        if isinstance(c, list):
            parts = []
            for i in c:
                if i.get("type") == "text":
                    parts.append(i.get("text",""))
                elif i.get("type") == "tool_result":
                    parts.append(str(i.get("content","")))
                elif i.get("type") == "tool_use":
                    parts.append(f"[Tool: {i.get('name','')} Input: {i.get('input','')}]")
            c = " ".join(parts)
        msgs.append({"role": m.get("role", "user"), "content": c})
    requested = int(data.get("max_tokens", 8192))
    payload = {
        "model": TARGET_MODEL,
        "messages": msgs,
        "max_tokens": min(requested, 32768),
        "temperature": float(data.get("temperature", 0.2))
    }
    try:
        r = requests.post(
            "http://localhost:8000/v1/chat/completions",
            json=payload,
            headers={"Authorization": "Bearer dummy", "Content-Type": "application/json"},
            timeout=180
        )
        groq_data = r.json()
        import sys, time
        print(f"GROQ RAW: {str(groq_data)[:200]}", file=sys.stderr, flush=True)
        if not groq_data.get("choices"):
            print(f"GROQ ERROR: {groq_data}", file=sys.stderr, flush=True)
            error_msg = groq_data.get("error", {})
            if isinstance(error_msg, dict):
                error_msg = error_msg.get("message", str(groq_data))
            return jsonify({
                "id": "msg_err",
                "type": "message",
                "role": "assistant",
                "content": [{"type": "text", "text": f"[Proxy error: {error_msg}]"}],
                "model": data.get("model", "claude-sonnet-4-6"),
                "stop_reason": "end_turn",
                "stop_sequence": None,
                "usage": {"input_tokens": 0, "output_tokens": 0}
            }), 200
        import sys
        print(f"REQUEST max_tokens={data.get('max_tokens')} msgs={len(msgs)}", file=sys.stderr, flush=True)
        print(f"RESPONSE finish={groq_data.get('choices',[{}])[0].get('finish_reason')} content_len={len(groq_data.get('choices',[{}])[0].get('message',{}).get('content',''))}", file=sys.stderr, flush=True)
        choice = groq_data.get("choices", [{}])[0]
        content_text = choice.get("message", {}).get("content", "")
        content_text = re.sub(r"<think>.*?</think>", "", content_text, flags=re.DOTALL).strip()
        finish_reason = choice.get("finish_reason", "end_turn")
        stop_reason = "max_tokens" if finish_reason == "length" else "end_turn"
        usage = groq_data.get("usage", {})
        return jsonify({
            "id": groq_data.get("id", "msg_000"),
            "type": "message",
            "role": "assistant",
            "content": [{"type": "text", "text": content_text}],
            "model": data.get("model", "claude-sonnet-4-6"),
            "stop_reason": stop_reason,
            "stop_sequence": None,
            "usage": {
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0)
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5558, debug=False)
