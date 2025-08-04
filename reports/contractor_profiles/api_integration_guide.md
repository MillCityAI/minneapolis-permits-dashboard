# Contractor Profile API Integration Guide

This guide explains how to integrate your contractor detail pages with your Render backend for call logging and notes tracking.

## Setup Steps

### 1. Update the API Configuration

In the contractor detail HTML files, update the API configuration with your Render app URL:

```javascript
const API_CONFIG = {
    baseUrl: 'https://your-app-name.onrender.com/api', // Replace with your actual Render URL
    headers: {
        'Content-Type': 'application/json',
        // Add authentication if needed:
        // 'Authorization': 'Bearer YOUR_TOKEN'
    }
};
```

### 2. Required API Endpoints

Your Render backend should implement these endpoints:

#### Get Call History
```
GET /api/contractors/{contractorId}/calls
```
Response:
```json
[
  {
    "id": "call-123",
    "date": "2024-01-15T10:30:00Z",
    "time": "10:30 AM",
    "status": "success",
    "statusDisplay": "Success - Spoke with contact",
    "contactPerson": "John Smith",
    "notes": "Interested in our services",
    "followUpDate": "2024-01-20",
    "author": "Sales Rep Name"
  }
]
```

#### Save New Call
```
POST /api/contractors/{contractorId}/calls
```
Request body:
```json
{
  "contractorId": "contractor-123",
  "status": "success",
  "contactPerson": "John Smith",
  "notes": "Call summary...",
  "followUpDate": "2024-01-20",
  "date": "2024-01-15T10:30:00Z",
  "author": "Sales Rep Name"
}
```

#### Get Notes History
```
GET /api/contractors/{contractorId}/notes
```
Response:
```json
[
  {
    "id": "note-123",
    "date": "2024-01-15T09:00:00Z",
    "content": "This contractor prefers email communication...",
    "author": "Sales Rep Name"
  }
]
```

#### Save New Note
```
POST /api/contractors/{contractorId}/notes
```
Request body:
```json
{
  "contractorId": "contractor-123",
  "content": "Note content...",
  "date": "2024-01-15T09:00:00Z",
  "author": "Sales Rep Name"
}
```

### 3. CORS Configuration

Ensure your Render backend has CORS enabled to allow requests from your local HTML files:

```javascript
// Express.js example
app.use(cors({
    origin: ['file://', 'http://localhost:*', 'https://your-domain.com'],
    credentials: true
}));
```

### 4. Authentication (Optional)

If your API requires authentication:

1. Add authentication headers to API_CONFIG
2. Implement a login flow to get tokens
3. Store tokens securely (localStorage or sessionStorage)
4. Include tokens in all API requests

### 5. Contractor IDs

Each contractor needs a unique ID. You can:

1. Use the company name as a slug:
   ```javascript
   const contractorId = companyName.toLowerCase().replace(/[^a-z0-9]/g, '-');
   ```

2. Generate UUIDs for each contractor

3. Use an existing ID from your database

### 6. User Identification

The `getCurrentUser()` function needs to identify the current user. Options:

1. Simple localStorage:
   ```javascript
   function getCurrentUser() {
       return localStorage.getItem('userName') || 'Sales Team';
   }
   ```

2. Session-based:
   ```javascript
   function getCurrentUser() {
       return sessionStorage.getItem('currentUser') || 'Sales Team';
   }
   ```

3. API-based authentication with user profile

## Testing the Integration

1. Open a contractor detail page
2. Check browser console for any CORS or API errors
3. Try logging a call
4. Try saving a note
5. Refresh the page to verify data persistence

## Error Handling

The template includes error handling for:
- Failed API calls
- Network issues
- Invalid responses

Error messages are displayed to users with appropriate styling.

## Customization Options

### Add More Call Statuses
Edit the call status dropdown in the modal:
```html
<option value="interested">Interested - Send Quote</option>
<option value="not-interested">Not Interested</option>
<option value="callback-later">Call Back Later</option>
```

### Add Custom Fields
Add more fields to the call logging form:
```html
<div class="form-group">
    <label class="form-label" for="projectType">Project Type</label>
    <select id="projectType" class="form-control">
        <option value="residential">Residential</option>
        <option value="commercial">Commercial</option>
    </select>
</div>
```

### Integrate with CRM
Add a function to sync with your CRM:
```javascript
async function syncWithCRM(contractorData) {
    // Send contractor data to your CRM API
}
```

## Database Schema Suggestion

For your Render backend, consider this schema:

```sql
-- Contractors table
CREATE TABLE contractors (
    id VARCHAR(255) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(255),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Calls table
CREATE TABLE calls (
    id SERIAL PRIMARY KEY,
    contractor_id VARCHAR(255) REFERENCES contractors(id),
    status VARCHAR(50),
    contact_person VARCHAR(255),
    notes TEXT,
    follow_up_date DATE,
    author VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notes table
CREATE TABLE notes (
    id SERIAL PRIMARY KEY,
    contractor_id VARCHAR(255) REFERENCES contractors(id),
    content TEXT,
    author VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Next Steps

1. Update all contractor HTML files with your Render API URL
2. Implement the required endpoints in your Render backend
3. Test the integration with a few contractors
4. Add authentication if needed
5. Deploy and start tracking calls!