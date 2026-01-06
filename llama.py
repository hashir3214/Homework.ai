


from flask import Flask, render_template, request, Response, stream_with_context, jsonify
from groq import Groq
import os

app = Flask(__name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# In-memory storage for chat history
# Structure: { "user_id": [ {"role": "user", "content": "message"}, ... ] }
chat_history_db = {}

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/auth/callback")
def auth_callback():
    # Supabase will redirect here after authentication
    return render_template("dashboard.html")

@app.route("/get_history")
def get_history():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"chats": []})
    
    history = chat_history_db.get(user_id, [])
    return jsonify({"chats": history})

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.form["msg"]
    user_id = request.form.get("user_id")

    if not user_input:
        return Response("Error: No message provided.", mimetype='text/plain', status=400)
    
    def generate():
        if user_id:
            if user_id not in chat_history_db:
                chat_history_db[user_id] = []
            chat_history_db[user_id].append({"role": "user", "content": user_input})

        conversation_history = chat_history_db.get(user_id, [])
        
        messages_for_api = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. The user is a student, so please explain concepts clearly, use examples, and be encouraging."
            }
        ]
        messages_for_api.extend(conversation_history)

        output_text = ""
        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages_for_api,
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None
            )
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                output_text += content
                yield content
            
            if user_id:
                chat_history_db[user_id].append({"role": "assistant", "content": output_text})

        except Exception as e:
            yield f"Error generating response: {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/plain')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)