from flask import Flask, render_template, request, Response, stream_with_context
import json
from groq import Groq
import os
from datetime import datetime
app = Flask(__name__, template_folder='.')

# Use environment variable for API key for Render security, fallback to hardcoded for local
client = Groq(api_key=os.environ.get("GROQ_API_KEY", "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"))

DB_FILE = "local_db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}, "chats": []}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {"users": {}, "chats": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route("/")
def index():
    return render_template("home.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/get_history")
def get_history():
    user_id = request.args.get("user_id")
    if not user_id:
        return {"error": "No user_id provided"}, 400
    
    data = load_db()
    user_chats = [c for c in data["chats"] if c["user_id"] == user_id]
    return {"chats": [{"role": c["role"], "content": c["content"]} for c in user_chats]}

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.form["msg"]
    user_id = request.form.get("user_id")

    if not user_id:
        return Response("Error: User not authenticated.", mimetype='text/plain')

    data = load_db()
    if user_id not in data["users"]:
        data["users"][user_id] = {"tokens": 10000, "is_paid": 0}
        save_db(data)
    
    user = data["users"][user_id]
    
    if user["tokens"] <= 0:
        return Response("Error: Token limit reached. Please upgrade to Pro for more tokens.", mimetype='text/plain')
    
    def generate():
        # Estimate input tokens (approx 4 chars per token)
        input_tokens = len(user_input) // 4
        output_text = ""

        # Save user message
        data = load_db()
        data["chats"].append({
            "user_id": user_id, 
            "role": "user", 
            "content": user_input,
            "timestamp": str(datetime.utcnow())
        })
        save_db(data)

        try:
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant. The user is a student, so please explain concepts clearly, use examples, and be encouraging."
                    },
                    {
                        "role": "user",
                        "content": user_input
                    }
                ],
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=True,
                stop=None
            )
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                output_text += content
                yield content
            
            # Calculate and deduct tokens
            output_tokens = len(output_text) // 4
            total_cost = input_tokens + output_tokens
            
            # Save assistant message and update tokens
            data = load_db()
            data["chats"].append({
                "user_id": user_id, 
                "role": "assistant", 
                "content": output_text,
                "timestamp": str(datetime.utcnow())
            })
            if user_id in data["users"]:
                data["users"][user_id]["tokens"] -= total_cost
            save_db(data)

        except Exception as e:
            yield f"Error generating response: {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/plain')

@app.route("/upgrade_user", methods=["POST"])
def upgrade_user():
    # Internal endpoint to simulate upgrading a user (in production, call this via webhook)
    user_id = request.form.get("user_id")
    if user_id:
        data = load_db()
        if user_id in data["users"]:
            data["users"][user_id]["tokens"] += 90000
            data["users"][user_id]["is_paid"] = 1
            save_db(data)
        return "User upgraded"
    return "No user_id provided", 400

if __name__ == "__main__":
    app.run(debug=True)
