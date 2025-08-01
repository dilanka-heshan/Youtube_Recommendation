# Ethical Recommendation System API

A secure, ethical, and well-structured recommendation system with YouTube integration, built with FastAPI and following best practices.

## 🏗️ Project Structure

```
app/
├── api/                    # API route handlers
│   ├── core_routes.py     # Core recommendation endpoints
│   └── youtube_routes.py  # YouTube integration endpoints
├── core/                   # Core configuration and utilities
│   ├── config.py          # Application settings
│   └── security.py        # Security utilities and validation
├── models/                 # Data models and schemas
│   └── schemas.py         # Pydantic models for requests/responses
├── services/              # Business logic services
│   ├── recommendation_service.py  # Recommendation algorithms
│   └── youtube_service.py         # YouTube API integration
└── main.py                # FastAPI application entry point

tests/                     # Test suite
└── test_api.py           # Comprehensive API tests

requirements.txt          # Python dependencies
.env                     # Environment configuration
run_server.py           # Server startup script
```

## 🔒 Security Features

- **Input Validation**: All user inputs are sanitized and validated
- **Rate Limiting**: API calls are rate-limited to prevent abuse
- **Data Privacy**: User data is anonymized and has retention limits
- **CORS Protection**: Controlled cross-origin access
- **Error Handling**: Secure error responses without information leakage
- **Logging**: Comprehensive request/response logging

## 🎯 Ethical Considerations

- **Bias Mitigation**: Diversity promotion in recommendations
- **Transparency**: Clear recommendation explanations
- **Privacy Protection**: Data anonymization and retention policies
- **Content Filtering**: Safe search for YouTube content
- **User Control**: Preference management and feedback collection

## 🚀 Getting Started

### 1. Environment Setup

```bash
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Edit `.env` file:

```env
# YouTube API (optional)
YOUTUBE_API_KEY=your_youtube_api_key_here

# Security
SECRET_KEY=your-secure-secret-key

# Server
DEBUG=True
HOST=127.0.0.1
PORT=8000
```

### 3. Run the Server

```bash
# Method 1: Using run script
python run_server.py

# Method 2: Direct uvicorn
uvicorn app.main:app --reload
```

### 4. Test the API

```bash
# Run comprehensive tests
python tests/test_api.py

# Or visit interactive docs
http://localhost:8000/docs
```

## 📋 API Endpoints

### Core Endpoints

- `GET /` - API welcome message
- `GET /health` - Health check with system status
- `GET /api-info` - API capabilities and features

### Recommendations

- `GET /items` - Get all available items
- `GET /categories` - Get all categories
- `POST /recommendations` - Get personalized recommendations
- `POST /recommendations/feedback` - Provide recommendation feedback

### User Management

- `POST /user/preferences` - Set user preferences
- `GET /user/{user_id}/preferences` - Get user preferences

### YouTube Integration (Optional)

- `POST /youtube/video-details` - Get video information
- `POST /youtube/search` - Search videos
- `GET /youtube/video/{video_id}` - Get video by ID
- `POST /youtube/recommend-similar` - Get similar videos
- `GET /youtube/quota-status` - Check API quota usage

## 🔧 Configuration Options

### Security Settings

```env
# Rate limiting
YOUTUBE_RATE_LIMIT=100
MAX_RECOMMENDATIONS=20

# Data privacy
DATA_RETENTION_DAYS=30
ANONYMIZE_LOGS=True

# API security
SECRET_KEY=change-this-in-production
```

### Performance Settings

```env
# YouTube API quotas
YOUTUBE_QUOTA_LIMIT=10000

# Server configuration
DEBUG=False  # Set to False in production
HOST=127.0.0.1  # More secure than 0.0.0.0
```

## 🧪 Testing

The project includes comprehensive tests covering:

- ✅ Health checks and API information
- ✅ Core recommendation functionality
- ✅ User preference management
- ✅ Input validation and security
- ✅ YouTube integration (if configured)
- ✅ Error handling

Run tests with:

```bash
python tests/test_api.py
```

## 📊 Monitoring and Logging

- Request/response logging with timing
- Error tracking with stack traces
- YouTube API quota monitoring
- User interaction analytics (anonymized)

## 🛡️ Privacy and Ethics

### Data Protection

- User IDs are hashed for privacy
- Personal data has automatic expiration
- Minimal data collection principle
- GDPR compliance considerations

### Recommendation Ethics

- Diversity promotion to avoid filter bubbles
- Bias detection and mitigation
- Transparent recommendation explanations
- User feedback incorporation

### Content Safety

- YouTube safe search enabled
- Content filtering mechanisms
- Inappropriate content blocking

## 🔄 Development Guidelines

### Code Quality

- Type hints throughout the codebase
- Comprehensive error handling
- Input validation and sanitization
- Secure coding practices

### Architecture

- Clean separation of concerns
- Dependency injection patterns
- Service-oriented architecture
- Modular and testable design

## 📈 Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication and authorization
- [ ] Machine learning model deployment
- [ ] Real-time recommendation updates
- [ ] Advanced analytics dashboard
- [ ] A/B testing framework
- [ ] Content moderation system

## 🐛 Troubleshooting

### Common Issues

1. **YouTube API not working**

   - Check API key in `.env` file
   - Verify YouTube Data API v3 is enabled
   - Check quota limits

2. **Server won't start**

   - Ensure virtual environment is activated
   - Check all dependencies are installed
   - Verify port 8000 is available

3. **Tests failing**
   - Make sure server is running
   - Check network connectivity
   - Review error messages in test output

### Debug Mode

Enable debug logging:

```env
DEBUG=True
```

Check logs in `app.log` file for detailed information.

## 📄 License

This project follows ethical AI development principles and includes appropriate safeguards for responsible use.

## 🤝 Contributing

When contributing, please:

1. Follow the existing code structure
2. Add appropriate tests
3. Ensure security best practices
4. Document ethical considerations
5. Validate privacy protection measures
