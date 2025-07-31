# Template Integration for Receipt Processor

This document explains how the template integration works alongside the existing API endpoints with JWT authentication.

## Overview

The Receipt Processor now supports both:
- **Web Interface**: User-friendly HTML templates with Bootstrap styling and JWT authentication
- **API Endpoints**: RESTful API for programmatic access with JWT tokens

## Authentication

The system uses JWT (JSON Web Tokens) for authentication:
- **Login/Register**: User registration and login with JWT token generation
- **Token Storage**: Tokens stored in browser localStorage
- **Protected Routes**: All API endpoints require authentication
- **Auto-logout**: Tokens expire after 1 hour (configurable)

## URL Structure

### Web Interface URLs
- `/` - Home page with overview and navigation
- `/login/` - User login page
- `/register/` - User registration page
- `/upload/` - Upload receipt page with drag-and-drop functionality (requires auth)
- `/receipts/` - List all receipts with search and filter options (requires auth)
- `/receipts/<id>/` - Detailed view of a specific receipt with text extraction tab (requires auth)

### API Endpoints
- `/api/register/` - User registration API
- `/api/login/` - User login API
- `/api/logout/` - User logout API
- `/api/upload/` - Upload receipt API (requires auth)
- `/api/validate/` - Validate receipt API (requires auth)
- `/api/process/` - Process receipt with OCR API (requires auth)
- `/api/extract-text/` - Extract text only API (requires auth)
- `/api/receipts/` - List all receipts API (requires auth)
- `/api/receipts/<id>/` - Get/Delete specific receipt API (requires auth)

## Features

### Web Interface Features
1. **JWT Authentication**: Secure login/register with token-based auth
2. **Responsive Design**: Bootstrap 5 with mobile-friendly layout
3. **Drag & Drop Upload**: Modern file upload with visual feedback
4. **Search & Filter**: Real-time search and status filtering
5. **Pagination**: Efficient handling of large datasets
6. **Interactive Actions**: Process, validate, and delete receipts
7. **Text Extraction**: Dedicated tab for extracting raw text from receipts
8. **Summary Statistics**: Dashboard with key metrics

### Template Structure
```
templates/
├── base.html                 # Base template with navigation and auth
├── 404.html                  # 404 error page
├── 500.html                  # 500 error page
└── receipts/
    ├── home.html             # Home page
    ├── login.html            # Login page
    ├── register.html         # Registration page
    ├── upload.html           # Upload page (protected)
    ├── receipts_list.html    # Receipts list page (protected)
    └── receipt_detail.html   # Receipt detail page with tabs (protected)
```

## Usage

### For End Users
1. Visit the home page at `/`
2. Register or login to access protected features
3. Upload receipts using the drag-and-drop interface
4. View and manage receipts through the web interface
5. Use the "Extracted Text" tab to get raw OCR text

### For Developers
1. Use API endpoints for programmatic access
2. Include JWT token in Authorization header: `Bearer <token>`
3. Templates use the same underlying views as the API
4. Both interfaces share the same data models
5. API responses are JSON, templates render HTML

## Authentication Flow

1. **Registration**: User creates account → receives JWT tokens
2. **Login**: User authenticates → receives JWT tokens
3. **API Calls**: Include `Authorization: Bearer <token>` header
4. **Logout**: Token blacklisted and cleared from localStorage

## Text Extraction Feature

- **Dedicated Tab**: Separate tab in receipt detail view
- **Raw OCR Text**: Extracts text without processing
- **Copy to Clipboard**: Easy text copying functionality
- **File Information**: Shows source file name
- **Authentication Required**: Protected endpoint

## Styling

The templates use:
- **Bootstrap 5**: For responsive layout and components
- **Font Awesome**: For icons
- **Custom CSS**: For enhanced styling and animations

## JavaScript Features

- **JWT Management**: Token storage and automatic inclusion in requests
- **Authentication Checks**: Redirect unauthenticated users
- **Drag & Drop**: File upload with visual feedback
- **Real-time Search**: Client-side filtering of receipts
- **AJAX Requests**: Asynchronous processing and validation
- **Modal Dialogs**: For processing feedback
- **Text Extraction**: OCR text extraction and display

## Error Handling

- **404 Page**: Custom error page for missing resources
- **500 Page**: Server error page
- **Authentication Errors**: Redirect to login page
- **Form Validation**: Client and server-side validation
- **User Feedback**: Success and error messages

## Browser Compatibility

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile responsive design
- Progressive enhancement for older browsers

## Development

To modify templates:
1. Edit files in the `templates/` directory
2. Templates extend `base.html` for consistent styling
3. Use Django template tags for dynamic content
4. JavaScript is included in template blocks
5. Include JWT authentication headers in API calls

## API vs Templates

| Feature | API | Templates |
|---------|-----|-----------|
| Response Format | JSON | HTML |
| Use Case | Programmatic | User Interface |
| Authentication | JWT Token | JWT Token + Session |
| Styling | None | Bootstrap + Custom CSS |
| Interactivity | Manual | Built-in JavaScript |
| Text Extraction | Dedicated endpoint | Tab interface |

## Security Considerations

- **JWT Tokens**: Stored in localStorage (consider httpOnly cookies for production)
- **Token Expiration**: 1 hour access tokens, 1 day refresh tokens
- **Protected Routes**: All sensitive operations require authentication
- **CSRF Protection**: CSRF tokens included in forms
- **Input Validation**: Both client and server-side validation 