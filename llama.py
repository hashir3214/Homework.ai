from flask import Flask, render_template, request, Response, stream_with_context
from flask_sqlalchflaemy import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from groq import Groq
import os
from datetime import datetime
# flask_sqlalchflaemy
app = Flask(__name__)
app = Flask(__name__, template_folder='.')

# Use environment variable for API key for Render security, fallback to hardcoded for local
client = Groq(api_key=os.environ.get("GROQ_API_KEY", "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"))

# Database setup
# Use SQLite for local, PostgreSQL for Render
database_url = os.environ.get("DATABASE_URL", "sqlite:///users.db")
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    user_id = db.Column(db.String(255), primary_key=True)
    tokens = db.Column(db.Integer, default=10000)
    is_paid = db.Column(db.Integer, default=0)

class ChatHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

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
    
    chats = ChatHistory.query.filter_by(user_id=user_id).order_by(ChatHistory.timestamp).all()
    return {"chats": [{"role": c.role, "content": c.content} for c in chats]}

@app.route("/get_response", methods=["POST"])
def get_response():
    user_input = request.form["msg"]
    user_id = request.form.get("user_id")

    if not user_id:
        return Response("Error: User not authenticated.", mimetype='text/plain')

    user = User.query.get(user_id)
    if not user:
        user = User(user_id=user_id, tokens=10000, is_paid=0)
        db.session.add(user)
        db.session.commit()
    
    if user.tokens <= 0:
        return Response("Error: Token limit reached. Please upgrade to Pro for more tokens.", mimetype='text/plain')
    
    def generate():
        # Estimate input tokens (approx 4 chars per token)
        input_tokens = len(user_input) // 4
        output_text = ""

        # Save user message
        with app.app_context():
            user_msg = ChatHistory(user_id=user_id, role="user", content=user_input)
            db.session.add(user_msg)
            db.session.commit()

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
            
            with app.app_context():
                # Save assistant message and update tokens
                bot_msg = ChatHistory(user_id=user_id, role="assistant", content=output_text)
                db.session.add(bot_msg)
                current_user = User.query.get(user_id)
                current_user.tokens -= total_cost
                db.session.commit()

        except Exception as e:
            yield f"Error generating response: {str(e)}"

    return Response(stream_with_context(generate()), mimetype='text/plain')

@app.route("/upgrade_user", methods=["POST"])
def upgrade_user():
    # Internal endpoint to simulate upgrading a user (in production, call this via webhook)
    user_id = request.form.get("user_id")
    if user_id:
        user = User.query.get(user_id)
        if user:
            user.tokens += 90000
            user.is_paid = 1
            db.session.commit()
        return "User upgraded"
    return "No user_id provided", 400

if __name__ == "__main__":
    app.run(debug=True)