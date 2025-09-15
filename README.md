# Zine Social Network

A minimalist zine-making and distribution platform built with Flask and Firebase Firestore, designed for deployment on Vercel.

**Status:** Firebase Firestore integration complete - Dec 2024

## Features

### Core Functionality
- **User Authentication**: Email-based registration and login
- **Zine Editor**: Drag-and-drop page designer with templates
- **Publishing**: Create and publish multi-page digital zines
- **Viewer**: Flip and scroll modes for reading zines
- **Social Features**: Follow creators, personalized feed
- **Discovery**: Search and explore zines by category
- **Analytics**: View stats for your published zines
- **Sharing**: QR codes and share links for each zine

### Technical Features
- Lightweight SQLite database
- Responsive design
- Auto-save and version history (last 10 saves)
- Image upload with auto-compression
- PDF export capability (optional)

## Setup Instructions

### Local Development

1. Clone the repository:
```bash
cd zine-app
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

5. Edit `.env` with your configuration:
   - Set a secure `SECRET_KEY`
   - Configure email settings if needed
   - Add OAuth credentials (optional)

6. Initialize the database:
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

7. Run the application:
```bash
python app.py
```

The app will be available at `http://localhost:5000`

### Vercel Deployment

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Configure environment variables in Vercel:
   - Go to your Vercel dashboard
   - Add all variables from `.env.example`
   - Set `FLASK_ENV` to `production`

3. Deploy:
```bash
vercel
```

4. For production deployment:
```bash
vercel --prod
```

## Project Structure

```
zine-app/
├── app/
│   ├── __init__.py        # App initialization
│   ├── models.py          # Database models
│   └── routes/            # Route blueprints
│       ├── auth.py        # Authentication routes
│       ├── main.py        # Main app routes
│       ├── editor.py      # Zine editor routes
│       ├── viewer.py      # Zine viewer routes
│       └── api.py         # API endpoints
├── static/
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   └── uploads/          # User uploads
├── templates/            # HTML templates
│   ├── auth/            # Auth templates
│   ├── editor/          # Editor templates
│   └── viewer/          # Viewer templates
├── instance/            # Instance folder (database)
├── requirements.txt     # Python dependencies
├── vercel.json         # Vercel configuration
└── app.py             # Main application file
```

## Database Schema

- **User**: User accounts with profiles
- **Zine**: Published zines with metadata
- **Page**: Individual pages within zines
- **Followers**: Many-to-many relationship for following
- **Notification**: User notifications
- **Analytics**: View and engagement tracking
- **Tag**: Categories for zines
- **ZineVersion**: Version history for autosave

## API Endpoints

### Public
- `GET /` - Home page/feed
- `GET /explore` - Discover zines
- `GET /<username>` - Creator profile
- `GET /<username>/<slug>` - View zine

### Authenticated
- `POST /editor/create` - Create new zine
- `POST /editor/<id>/save` - Save zine content
- `POST /editor/<id>/publish` - Publish zine
- `POST /follow/<user_id>` - Follow creator
- `GET /notifications` - View notifications

### API
- `POST /api/upload` - Upload images
- `GET /api/analytics/<zine_id>` - Get zine analytics
- `GET /api/templates` - Get page templates
- `POST /api/track-read-time` - Track reading time

## Environment Variables

Required environment variables:

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///instance/zines.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

Optional OAuth configuration:
```
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## Notes

- SQLite database is stored in `instance/zines.db`
- Uploaded images are stored in `static/uploads/`
- For production, consider using PostgreSQL instead of SQLite
- Email notifications require SMTP configuration
- PDF generation requires WeasyPrint (may need additional system dependencies)

## License

MIT