# AI-Powered Portfolio Analyzer

This project combines web scraping with AI analysis to extract meaningful insights from portfolio websites. Users can submit URLs to be analyzed, then ask questions about the content in a conversational interface.

## 🌟 Features

### 1. Website Content Extraction
- Scrapes any portfolio URL provided by users
- Extracts paragraphs, links, and images
- Processes HTML content for AI analysis

### 2. Dual AI Agent System
- **Agent**: Analyzes website content and extracts structured information
- **Agent1**: Answers user questions based on analyzed website data

### 3. Interactive Chat Interface
- Ask questions about the analyzed portfolio
- Get AI-powered responses with structured insights
- Reference specific content from the analyzed website

## 🔧 Tech Stack

### Backend
- **Flask**: REST API server
- **Pydantic AI**: Structured AI interactions with multiple models
- **Gemini 2.0 Flash**: Google's LLM for content analysis
- **BeautifulSoup4**: HTML parsing and content extraction
- **Asyncio**: Asynchronous processing

### Frontend (React)
- React component-based architecture
- URL submission interface
- Chat interface for questions and answers

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js and npm
- Google AI Platform API key

### Installation

1. Clone the repository
```bash
git clone <repository-url>
cd pydantic-ai-project
```

2. Install backend dependencies
```bash
pip install flask flask-cors pydantic pydantic-ai requests beautifulsoup4 asyncio
```

3. Install frontend dependencies
```bash
cd frontend
npm install
```

4. Configure your environment
```bash
# Create a .env file in the root directory
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

### Running the application

1. Start the backend server
```bash
python app.py
```

2. Start the frontend development server
```bash
cd frontend
npm start
```

3. Visit `http://localhost:3000` in your browser

## 📝 API Endpoints

### POST /api/process-url
Analyzes a portfolio website and returns structured information.

**Request:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "analysis": {
    "url": "https://example.com",
    "title": "Portfolio Title",
    "main_topic": "Web Development",
    "paragraph": "Content summary...",
    "key_points": ["Point 1", "Point 2", "..."]
  },
  "scraped_data": {
    "paragraphs": ["..."],
    "links": ["..."],
    "images": ["..."]
  }
}
```

### POST /api/chat
Answers questions about the analyzed portfolio using AI.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "What skills does this person have?"}
  ],
  "url_data": {
    // Data from the /api/process-url response
  }
}
```

**Response:**
```json
{
  "message": "Based on the portfolio analysis, this person has skills in..."
}
```

## 🧠 AI Agents

### Agent - Content Analyzer
- Extracts structured information from website content
- Maps raw HTML to a structured `WebsiteInfo` model
- Provides key points and main topics

### Agent1 - Question Answerer
- Answers user questions using the structured content
- Provides detailed answers with summaries and key points
- References specific parts of the website content

## 🔄 Data Flow
1. User submits a URL
2. Backend scrapes and processes the website
3. Agent analyzes and structures the content
4. User asks questions about the portfolio
5. Agent1 provides answers based on the structured content

## 📋 Future Enhancements
- Support for PDF portfolio analysis
- Multiple portfolio comparison
- Resume parsing and matching with job descriptions
- Integration with LinkedIn profiles
- Enhanced visualization of skills and experiences

## 📄 License
 MIT License
