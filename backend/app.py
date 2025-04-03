from flask import Flask, request, jsonify, Response, stream_with_context
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Literal
import asyncio
import logging
from pydantic import BaseModel, Field

# Import Pydantic AI with Gemini
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, TextPart, UserPromptPart
from pydantic_ai.providers.google_gla import GoogleGLAProvider

from flask_cors import CORS
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define structured output model
class WebsiteInfo(BaseModel):
    url: str
    title: Optional[str] = None
    main_topic: Optional[str] = None
    summary: str = Field(..., description="A brief summary of the website content")
    key_points: List[str] = Field(..., description="Main points extracted from the website")

# Initialize the Gemini model and agent - keeping the original structure
model = GeminiModel(
    'gemini-1.5-flash', provider=GoogleGLAProvider(api_key='AIzaSyDo88VXyuDtTIP95TPF8J3WINj957dGvOM')
)
agent = Agent(
    model,
    system_prompt="You are an assistant that analyzes URLs and their content. Provide structured analysis of websites.",
    result_type=WebsiteInfo
)

app = Flask(__name__)
CORS(app)

# Pydantic models for request/response validation
class Message(BaseModel):
    role: Literal['user', 'model', 'system']
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())

class ChatRequest(BaseModel):
    messages: List[Message]
    url_data: Optional[Dict[str, Any]] = None

class URLRequest(BaseModel):
    url: str

# Helper function to convert ModelMessage to chat message format
def to_chat_message(m: ModelMessage) -> Dict[str, Any]:
    first_part = m.parts[0]
    if isinstance(m, ModelRequest):
        if isinstance(first_part, UserPromptPart):
            return {
                'role': 'user',
                'timestamp': first_part.timestamp.isoformat(),
                'content': first_part.content,
            }
    elif isinstance(m, ModelResponse):
        if isinstance(first_part, TextPart):
            return {
                'role': 'model',
                'timestamp': m.timestamp.isoformat(),
                'content': first_part.content,
            }
    return {
        'role': 'system',
        'timestamp': datetime.now(tz=timezone.utc).isoformat(),
        'content': 'Unexpected message format',
    }

@app.route('/api/process-url', methods=['POST'])
def process_url():
    try:
        # Get the URL from the request body
        data = request.get_json()
        
        # Validate with Pydantic
        url_request = URLRequest.model_validate(data)
        url = url_request.url
        logger.info(f"Processing URL: {url}")
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            logger.info(f"Updated URL with https prefix: {url}")
        
        # Fetch the content from the URL
        try:
            import requests
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Log successful response
            logger.info(f"Successfully fetched URL: {url}")
            logger.info(f"Response status code: {response.status_code}")
            
            # Process the content
            content_preview = response.text[:1000] + '...' if len(response.text) > 1000 else response.text
            
            # Return the processed data
            return jsonify({
                'url': url,
                'status': 'success',
                'content_length': len(response.text),
                'content_preview': content_preview,
                'content_type': response.headers.get('Content-Type', 'unknown')
            })
            
        except Exception as e:
            logger.error(f"Error fetching URL {url}: {str(e)}")
            return jsonify({
                'error': f"Failed to fetch URL: {str(e)}",
                'url': url
            }), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in process_url: {str(e)}")
        return jsonify({'error': f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Get request data
        data = request.get_json()
        
        # Extract messages and url_data
        messages = data.get('messages', [])
        url_data = data.get('url_data')
        
        logger.info(f"Received chat request with {len(messages)} messages")
        
        # Create a prompt that includes URL context if available
        prompt = messages[-1]['content'] if messages else "Analyze this website"
        
        # Prepare context from URL data
        context = ""
        if url_data:
            context = f"""
            URL: {url_data.get('url', 'Unknown')}
            Content Type: {url_data.get('content_type', 'Unknown')}
            Content Preview: {url_data.get('content_preview', 'No preview available')}
            """
            prompt = f"Context: {context}\n\nUser question: {prompt}"
        
        # Convert previous messages to format expected by pydantic_ai
        history = []
        for msg in messages[:-1]:  # Exclude the last message as it's in the prompt
            if msg['role'] == 'user':
                history.append(ModelRequest(parts=[UserPromptPart(msg['content'])]))
            elif msg['role'] == 'model':
                history.append(ModelResponse(parts=[TextPart(msg['content'])]))
        
        # Run in synchronous mode for simplicity
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Use the agent with structured output
        result = loop.run_until_complete(agent.run(prompt, message_history=history))
        
        # Get the structured data and format it
        website_info = result.data
        formatted_response = f"""**Website Analysis**

**URL**: {website_info.url}

**Title**: {website_info.title or 'Not available'}

**Summary**: {website_info.summary}

**Key Points**:
{chr(10).join([f"- {point}" for point in website_info.key_points])}

**Main Topic**: {website_info.main_topic or 'Not specified'}
"""
        
        return jsonify({'message': formatted_response})
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': f"Failed to get AI response: {str(e)}"}), 500

if __name__ == '__main__':
    logger.info("Starting Flask API server...")
    app.run(debug=True, host='0.0.0.0', port=3000)