# 📱 Stock Sentinel - Stock Visibility App

A comprehensive stock market tracking application built with Django REST API backend and SwiftUI iOS frontend, following MVVM architecture principles.

## 🚀 Features

### ✅ Core Features Implemented

- **Real-time Market Overview**: View major indices, top gainers/losers, and most active stocks
- **Stock Search & Details**: Search for stocks and view detailed quotes, price information, and news
- **Personalized Watchlists**: Create and manage custom stock watchlists with real-time updates
- **Global Exchange Map**: Interactive map showing locations of major stock exchanges worldwide
- **User Authentication**: Secure login/registration system with JWT tokens
- **Modern iOS UI**: Clean, intuitive SwiftUI interface with dark/light mode support

### 🏗️ Architecture

- **Frontend**: SwiftUI with MVVM pattern
- **Backend**: Django REST Framework
- **Database**: SQLite (easily configurable for MySQL/PostgreSQL)
- **Authentication**: JWT-based token authentication
- **API Design**: RESTful endpoints with proper error handling

## 📁 Project Structure

```
stocksentinel/
├── stockapi/                 # Django backend
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Main URL routing
│   └── wsgi.py              # WSGI configuration
├── stocks/                   # Django app
│   ├── models.py            # Database models
│   ├── views.py             # API endpoints
│   ├── serializers.py       # Data serialization
│   └── urls.py              # App URL routing
├── StockSentinel/           # iOS app
│   ├── Models/              # Data models
│   ├── ViewModels/          # MVVM view models
│   ├── Views/               # SwiftUI views
│   ├── Services/            # API service layer
│   └── Utils/               # Utility functions
└── requirements.txt         # Python dependencies
```

## 🛠️ Setup Instructions

### Backend Setup (Django)

1. **Install Dependencies**

   ```bash
   cd /Users/justinlee/Cursor/stocksentinel
   pip install -r requirements.txt
   ```

2. **Run Database Migrations**

   ```bash
   python manage.py migrate
   ```

3. **Create Superuser (Optional)**

   ```bash
   python manage.py createsuperuser
   ```

4. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/api/`

### Frontend Setup (iOS)

1. **Open Xcode Project**

   - Open `StockSentinel/StockSentinel.xcodeproj` in Xcode
   - Select your target device or simulator
   - Build and run the project

2. **Configure API Endpoint**
   - Update the `baseURL` in `APIService.swift` if needed
   - Default: `http://localhost:8000/api`

## 📡 API Endpoints

### Authentication

- `POST /api/auth/login/` - User login
- `POST /api/auth/register/` - User registration

### Market Data

- `GET /api/markets/overview/` - Market overview with indices and trending stocks
- `GET /api/quotes/{symbol}/` - Real-time stock quote
- `GET /api/news/{symbol}/` - Stock news headlines

### Watchlists

- `GET /api/watchlists/` - Get user's watchlists
- `POST /api/watchlists/` - Create new watchlist
- `GET /api/watchlists/{id}/items/` - Get watchlist items
- `POST /api/watchlists/{id}/items/` - Add stock to watchlist
- `DELETE /api/watchlists/{id}/items/{item_id}/` - Remove stock from watchlist

## 🎨 iOS App Features

### Views Implemented

1. **AuthenticationView**: Login/Register with form validation
2. **MarketOverviewView**: Market indices and trending stocks
3. **SearchView**: Stock search with real-time quotes
4. **StockDetailView**: Detailed stock information and news
5. **WatchlistView**: Personal stock watchlist management
6. **MapView**: Global stock exchange locations

### Key Components

- **MVVM Architecture**: Clean separation of concerns
- **Combine Framework**: Reactive programming for API calls
- **MapKit Integration**: Interactive maps for exchange locations
- **SwiftUI**: Modern, declarative UI framework
- **UserDefaults**: Local token storage for authentication

## 🔧 Configuration

### Django Settings

- **Database**: SQLite (default), easily configurable for production databases
- **CORS**: Enabled for development (configure for production)
- **Authentication**: JWT token-based
- **API Keys**: Placeholder for external stock data APIs

### iOS Configuration

- **Minimum iOS Version**: 17.0
- **Architecture**: MVVM with Combine
- **Networking**: URLSession with Combine publishers
- **UI Framework**: SwiftUI with iOS 17+ features

## 🚀 Deployment

### Backend Deployment

1. Configure production database (MySQL/PostgreSQL)
2. Set up environment variables for API keys
3. Deploy to cloud platform (Google Cloud, AWS, Heroku)
4. Configure CORS for production domain

### iOS Deployment

1. Configure app signing and provisioning
2. Update API endpoints for production
3. Test on physical devices
4. Submit to App Store

## 🔮 Future Enhancements

### Planned Features

- **Real-time Data**: WebSocket integration for live updates
- **Push Notifications**: Price alerts and market updates
- **Portfolio Tracking**: Investment portfolio management
- **Charts**: Interactive price charts with technical indicators
- **Offline Support**: Local data caching and offline functionality
- **Dark Mode**: Enhanced UI theming
- **Widgets**: iOS home screen widgets for quick market overview

### Technical Improvements

- **External API Integration**: Real stock data from Finnhub/IEX Cloud
- **Caching**: Redis for improved performance
- **Testing**: Comprehensive unit and integration tests
- **CI/CD**: Automated testing and deployment pipeline
- **Analytics**: User behavior tracking and app analytics

## 📱 Screenshots

The app features a modern, intuitive interface with:

- Clean market overview with indices and trending stocks
- Easy stock search and detailed quote information
- Personal watchlist management
- Interactive map of global stock exchanges
- Smooth authentication flow

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Django REST Framework for the robust API framework
- SwiftUI for the modern iOS development experience
- MapKit for interactive map functionality
- Combine framework for reactive programming

---

**Built with ❤️ using Django and SwiftUI**
# musedb
