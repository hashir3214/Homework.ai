# Homework.AI

An AI-powered student assistant with a productivity dashboard, chat interface, and token-based usage system.

## Features
- **AI Chat**: Powered by Llama 3 (via Groq API).
- **Productivity Dashboard**: Pomodoro timer, To-Do list, Notes, and Lo-Fi music.
- **Authentication**: Secure login via Clerk.
- **Token System**: Usage tracking with free/paid tiers.
- **Persistent History**: Chat history saved to database.

## Local Setup

1.  **Clone the repository.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set Environment Variables:**
    Create a `.env` file or set them in your terminal:
    ```bash
    export GROQ_API_KEY="your_groq_api_key"
    # Optional: DATABASE_URL="sqlite:///users.db" (default)
    ```
4.  **Run the app:**
    ```bash
    python llama.py
    ```
5.  **Visit:** `http://localhost:5000`

## Deployment on Render.com

1.  **Push to GitHub**: Ensure your code is in a GitHub repository.
2.  **Create Web Service**:
    *   Go to Render Dashboard.
    *   Click **New +** -> **Web Service**.
    *   Connect your repository.
3.  **Configure Settings**:
    *   **Runtime**: Python 3
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `gunicorn llama:app`
4.  **Environment Variables**:
    Add the following in the "Environment" tab:
    *   `GROQ_API_KEY`: Your Groq API Key.
    *   `PYTHON_VERSION`: `3.9.0` (or similar).
5.  **Add Database (PostgreSQL)**:
    *   Go to Render Dashboard -> **New +** -> **PostgreSQL**.
    *   Create the database.
    *   Copy the **Internal Database URL**.
    *   Go back to your Web Service -> **Environment**.
    *   Add `DATABASE_URL` and paste the internal database URL.
6.  **Deploy**: Render will automatically build and deploy.

## Notes
- The app automatically handles the database creation (`db.create_all()`) on startup.
- Ensure your Clerk Publishable Key is correct in the HTML files.