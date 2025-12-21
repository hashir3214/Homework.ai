# Homework.AI - Your AI Study Partner

## 📝 Overview

Homework.AI is a web application designed to be an intelligent study companion for students. It leverages a powerful large language model (via the Groq API) to provide instant help, clear explanations for complex topics, and a conversational learning experience. The application also includes a feature-rich dashboard with tools to help students stay organized and focused.

## ✨ Features

-   **AI Chat**: A real-time, streaming chat interface to ask questions and get detailed answers from an AI tutor.
-   **Conversation History**: The AI remembers the context of your conversation for a more natural dialogue.
-   **User Authentication**: Secure sign-up and login powered by Clerk.
-   **Student Dashboard**: A central hub with helpful widgets:
    -   **Focus Timer**: A Pomodoro timer to manage study sessions.
    -   **Task Manager**: A to-do list to keep track of assignments.
    -   **Study Music**: Embedded Spotify playlist for focus.
    -   **Quick Notes**: A section to jot down important information.

## 🛠️ Setup and Installation

Follow these steps to get the application running on your local machine.

### Prerequisites

-   Python 3.7+
-   A [Groq](https://console.groq.com/keys) account and API Key.
-   A [Clerk](https://clerk.com/) account for user authentication (the provided code has a test key, but you may want your own for a real project).

### 1. Set up the Project Folder

Ensure all the project files are in the same directory:
```
your-project-folder/
├── llama.py
├── home.html
├── chat.html
├── dashboard.html
└── requirements.txt
```

### 2. Create a Virtual Environment

It's highly recommended to use a virtual environment to manage project dependencies.

```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

With your virtual environment activated, install the required Python packages.

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

The application needs a Groq API key to communicate with the AI. You should set this as an environment variable.

```bash
# For Windows (in Command Prompt)
set GROQ_API_KEY="your_groq_api_key_here"

# For macOS/Linux
export GROQ_API_KEY="your_groq_api_key_here"
```
> **Note:** The code has a fallback key for local testing, but using an environment variable is the correct practice.

## 🚀 Running the Application

1.  Start the Flask server from your terminal:
    ```bash
    python llama.py
    ```

2.  Open your web browser and navigate to:
    ```
    http://localhost:5000
    ```

You will be greeted by the home page. From there, you can sign up or log in to access the AI chat and dashboard features.