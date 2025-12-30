# Mongez AI

A simple FastAPI backend to interact with the Gemini API.

## Setup and Installation

1.  **Clone the repository (or create the files as provided).**

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set your Gemini API Key:**
    The `GEMINI_API_KEY` must be available as an environment variable in the shell session where you run the application.

    You can set it for your current session:
    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY"
    ```
    Alternatively, for convenience during development, you can pass it directly when starting the `uvicorn` server:
    ```bash
    GEMINI_API_KEY="YOUR_API_KEY" uvicorn main:app --reload
    ```
    Replace `"YOUR_API_KEY"` with your actual key.

## Running the Application

Once the setup is complete, you can run the FastAPI server using `uvicorn`. Ensure your `GEMINI_API_KEY` is set as described above.

```bash
uvicorn main:app --reload
```

The server will start, and you can access it at `http://127.0.0.1:8000`.

## API Endpoints

### `GET /`

A simple welcome message to confirm the server is running.

-   **Response:**
    ```json
    {
        "message": "Welcome to Mongez AI"
    }
    ```

### `POST /chat`

Sends a prompt to the Gemini API and returns the response.

-   **Request Body:**
    ```json
    {
        "prompt": "Your question or instruction here"
    }
    ```

-   **Example Usage (using `curl`):**
    ```bash
    curl -X POST "http://127.0.0.1:8000/chat" \
    -H "Content-Type: application/json" \
    -d '{"prompt": "What is the speed of light?"}'
    ```

-   **Success Response:**
    ```json
    {
        "response": "The speed of light in a vacuum is a universal physical constant, exactly 299,792,458 metres per second."
    }
    ```

-   **Error Response (if `GEMINI_API_KEY` is not set):**
    ```json
    {
        "detail": "The Gemini API is not configured on the server. Please set the GEMINI_API_KEY environment variable."
    }
    ```
