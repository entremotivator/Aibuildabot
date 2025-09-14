# 🤖 Enhanced AI Agent Toolkit

A comprehensive Streamlit application featuring specialized AI business assistants with OpenAI API integration, custom bot creation, and personalization features.

## 🚀 Features

### Core Features
- **Multiple AI Business Assistants**: Pre-built specialized agents for different business domains
- **OpenAI API Integration**: Powered by OpenAI's language models for intelligent conversations
- **Custom Bot Creation**: Users can create and configure their own personalized AI assistants
- **User Personalization**: Individual user profiles with custom settings and chat history
- **Multi-Page Interface**: Clean navigation between Chat, Bot Management, and User Profile pages
- **Beautiful UI**: Modern gradient design with responsive layout and smooth interactions

### Pre-built AI Agents
1. **🚀 Startup Strategist**: Specializes in business planning, MVP development, and scaling strategies
2. **📱 Marketing Strategy Expert**: Focuses on digital marketing, brand positioning, and customer acquisition
3. **🤖 AI Strategy Consultant**: Helps with AI implementation and automation strategies

### Custom Bot Features
- **Personalized Configuration**: Set custom names, emojis, categories, and descriptions
- **Adjustable Creativity**: Control response creativity with temperature settings
- **Custom Specialties**: Define specific areas of expertise
- **Quick Actions**: Pre-configured action buttons for common tasks
- **System Prompts**: Full control over bot personality and behavior

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.11+
- OpenAI API Key

### Required Dependencies
```bash
pip install streamlit openai supabase plotly tiktoken
```

### Environment Setup
Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 🚀 Running the Application

### Basic Usage
```bash
streamlit run ai_agent_toolkit_simple.py --server.port 8502 --server.address 0.0.0.0
```

### Demo Login
- **Email**: demo@example.com
- **Password**: demo123

## 📱 Application Pages

### 1. Chat Interface
- **Real-time Conversations**: Chat with AI agents using OpenAI API
- **Agent Selection**: Choose from pre-built or custom agents
- **Category Filtering**: Organize agents by business categories
- **Conversation History**: View and track chat history with timestamps
- **Agent Information Cards**: Detailed information about each agent's specialties

### 2. Custom Bot Management
- **Create New Bots**: Comprehensive form for bot configuration
- **Bot Library**: View and manage all custom bots
- **Advanced Configuration**: 
  - Custom system prompts
  - Specialty areas
  - Quick action buttons
  - Creativity level control
  - Category organization

### 3. User Profile
- **Account Information**: View user details and statistics
- **Usage Statistics**: Track messages sent and custom bots created
- **Chat Management**: Clear conversation history
- **Profile Settings**: Manage account preferences

## 🎨 Design Features

### Visual Design
- **Modern Gradient Headers**: Beautiful purple-blue gradient backgrounds
- **Color-Coded Elements**: Red backgrounds with black text for consistency
- **Responsive Layout**: Works on desktop and mobile devices
- **Interactive Elements**: Hover effects and smooth transitions
- **Card-Based Design**: Clean organization of information

### User Experience
- **Intuitive Navigation**: Easy switching between pages
- **Real-time Updates**: Immediate feedback for all actions
- **Error Handling**: Graceful handling of API errors and edge cases
- **Loading States**: Visual feedback during API calls

## 🔧 Technical Architecture

### File Structure
```
AIAgentToolkit/
├── ai_agent_toolkit_simple.py    # Main application (working version)
├── ai_agent_toolkit_final.py     # Enhanced version with Supabase
├── ai_agent_toolkit_enhanced.py  # Intermediate version
├── supabase_integration.py       # Database integration
├── auth.py                       # Original authentication
├── analysis.md                   # Code analysis
├── architecture_design.md        # Design documentation
└── README.md                     # This file
```

### Key Components
- **Session State Management**: Persistent user data across page reloads
- **OpenAI Integration**: Direct API calls with error handling
- **Custom Bot Storage**: In-memory storage with session persistence
- **Multi-page Navigation**: Streamlit-based page routing
- **Form Handling**: Comprehensive form validation and processing

## 🔑 API Integration

### OpenAI Configuration
- **Model Support**: Compatible with OpenAI's chat completion models
- **Error Handling**: Graceful handling of unsupported models and API errors
- **Temperature Control**: Adjustable creativity levels for different use cases
- **Context Management**: Maintains conversation context for better responses

### Supported Models
- gpt-4.1-mini
- gpt-4.1-nano
- gemini-2.5-flash (if configured)

## 🎯 Usage Examples

### Creating a Custom Bot
1. Navigate to "Manage Custom Bots"
2. Click "Create New Bot" tab
3. Fill in bot details:
   - Name: "Content Marketing Expert"
   - Emoji: "📝"
   - Category: "Marketing"
   - Description: "Specializes in content strategy and creation"
   - Specialties: "SEO, Content Strategy, Social Media"
   - System Prompt: "You are an expert content marketer..."
4. Click "Create Custom Bot"

### Chatting with Agents
1. Select an agent from the sidebar
2. Type your message in the chat area
3. Click "Send Message"
4. View the response in the conversation history

## 🚀 Deployment

### Local Development
The application runs locally on port 8502 and can be accessed at:
```
http://localhost:8502
```

### Production Deployment
For production deployment, consider:
- Setting up proper authentication
- Configuring Supabase for persistent storage
- Setting up environment variables securely
- Using a production WSGI server

## 🔒 Security Considerations

- **API Key Management**: Store OpenAI API keys securely
- **User Authentication**: Implement proper authentication for production
- **Data Privacy**: User conversations are stored in session state only
- **Input Validation**: All user inputs are validated and sanitized

## 🎨 Customization

### Styling
The application uses custom CSS for styling. Key design elements:
- Gradient backgrounds for headers
- Red backgrounds for content areas
- Black text for readability
- Rounded corners and shadows for modern look

### Adding New Agents
To add new pre-built agents, modify the `BOT_PERSONALITIES` dictionary in the main file:

```python
"New Agent Name": {
    "description": "Agent description",
    "emoji": "🎯",
    "category": "Business Category",
    "temperature": 0.7,
    "specialties": ["Specialty 1", "Specialty 2"],
    "quick_actions": ["Action 1", "Action 2"],
    "is_custom": False
}
```

## 📊 Statistics & Analytics

The application tracks:
- Total messages sent
- Custom bots created
- Conversation history
- User activity timestamps

## 🔄 Future Enhancements

Potential improvements:
- **Database Integration**: Persistent storage with Supabase
- **Advanced Analytics**: Detailed usage statistics
- **Bot Sharing**: Share custom bots between users
- **Export Features**: Export conversations and bot configurations
- **Advanced Personalization**: More customization options
- **API Integrations**: Connect with external business tools

## 🐛 Troubleshooting

### Common Issues
1. **OpenAI API Errors**: Ensure API key is set correctly
2. **Model Not Supported**: Use supported models (gpt-4.1-mini, etc.)
3. **Port Conflicts**: Change port number if 8502 is in use
4. **Dependencies**: Install all required packages

### Error Messages
- "OpenAI API key not configured": Set the OPENAI_API_KEY environment variable
- "Unsupported model": Update the model name to a supported version
- "Module not found": Install missing dependencies with pip

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the error messages in the application
3. Ensure all dependencies are installed correctly
4. Verify OpenAI API key configuration

## 📄 License

This project is provided as-is for educational and development purposes.

---

**Built with ❤️ using Streamlit and OpenAI**

