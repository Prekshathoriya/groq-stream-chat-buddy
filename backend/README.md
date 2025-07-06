# FastAPI Chatbot Backend

This is the backend service for the AI chatbot that integrates with Groq API and provides streaming responses.

## Features

- **FastAPI Backend**: Fast, modern Python web framework
- **Groq API Integration**: Powered by Groq's lightning-fast inference
- **Streaming Support**: Real-time response streaming to the frontend
- **Context Awareness**: Maintains chat history for meaningful conversations
- **CORS Enabled**: Ready to work with React frontend
- **Error Handling**: Robust error handling and validation

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Get Your Groq API Key

1. Sign up at [Groq Console](https://console.groq.com/)
2. Create a new API key
3. Copy the API key

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Groq API key
GROQ_API_KEY=your_actual_groq_api_key_here
```

### 4. Run the Server

```bash
# Development server with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Or simply run the Python file
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### POST /chat
Main streaming chat endpoint used by the React frontend.

**Request Body:**
```json
{
  "user_query": "What is artificial intelligence?",
  "system_prompt": "You are a helpful AI assistant.",
  "chat_history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi there!"}
  ]
}
```

**Response:** Server-Sent Events stream with JSON chunks

### POST /chat-simple
Non-streaming endpoint for testing.

**Request Body:** Same as /chat

**Response:**
```json
{
  "response": "AI response here...",
  "model": "mixtral-8x7b-32768",
  "usage": {...}
}
```

### GET /health
Health check endpoint to verify server and Groq API configuration.

## Available Groq Models

You can change the model in `main.py`. Popular options:

- `mixtral-8x7b-32768` - Great for general conversations
- `llama2-70b-4096` - Good performance
- `gemma-7b-it` - Fast and efficient

## Context Management

The backend automatically manages conversation context:

- **History Limit**: Keeps last 10 messages to prevent token overflow
- **System Prompt**: Configurable personality/behavior
- **Context Awareness**: Maintains conversation flow

## Testing the Backend

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Simple Chat Test
```bash
curl -X POST "http://localhost:8000/chat-simple" \
     -H "Content-Type: application/json" \
     -d '{
       "user_query": "Hello, how are you?",
       "system_prompt": "You are a friendly assistant."
     }'
```

### 3. Streaming Test
```bash
curl -X POST "http://localhost:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "user_query": "Tell me a short story",
       "system_prompt": "You are a creative storyteller."
     }'
```

## Integration with React Frontend

The React app is configured to call `http://localhost:8000/chat`. Make sure:

1. The FastAPI server is running on port 8000
2. Your Groq API key is configured
3. CORS is properly set up (already configured)

## Troubleshooting

### Common Issues:

1. **"GROQ_API_KEY not configured"**
   - Make sure you created `.env` file with your API key

2. **CORS errors**
   - Check that your React dev server port is in the CORS origins list

3. **Connection refused**
   - Ensure FastAPI server is running on port 8000

4. **Import errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`

## Security Notes

- Never commit your `.env` file with real API keys
- The `.env` file is already in `.gitignore`
- For production, use proper environment variable management
- Consider rate limiting for production deployments

## Extending the Backend

### Adding New Models
Modify the model name in the Groq API calls in `main.py`.

### Custom System Prompts
The system prompt can be customized per request or set globally.

### Additional Context
You can extend the `ContextManager` class to add more sophisticated context handling.

### Database Integration
Add database models to store conversation history permanently.

## Production Deployment

For production deployment:

1. Use a production WSGI server like Gunicorn
2. Set up proper environment variable management
3. Add rate limiting and authentication
4. Use a reverse proxy like Nginx
5. Enable logging and monitoring

```bash
# Example production command
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```