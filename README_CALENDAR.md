# Google Calendar Integration for ADK Voice Assistant

This document explains how to set up and use the Google Calendar integration with your ADK Voice Assistant.

## Setup Instructions

### 1. Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API for your project:
   - In the sidebar, navigate to "APIs & Services" > "Library"
   - Search for "Google Calendar API" and enable it

### 2. Create OAuth 2.0 Credentials

1. In the Google Cloud Console, navigate to "APIs & Services" > "Credentials"
2. Click "Create Credentials" and select "OAuth client ID"
3. For application type, select "Desktop application"
4. Name your OAuth client (e.g., "ADK Voice Calendar Integration")
5. Click "Create"
6. Download the credentials JSON file
7. Save the file as `credentials.json` in the root directory of this project

### 3. Run the Setup Script

Run the setup script to authenticate with Google Calendar:

```bash
python setup_calendar_auth.py
```

This will:
1. Start the OAuth 2.0 authorization flow
2. Open your browser to authorize the application
3. Save the access token securely for future use
4. Test the connection to your Google Calendar

## Working with Multiple Calendars

The Google Calendar integration supports working with multiple calendars. The OAuth flow will grant access to all calendars associated with your Google account. You can:

1. List all available calendars using the voice command "What calendars do I have access to?"
2. Specify which calendar to use for operations by name or ID
3. Use your primary calendar by default if no calendar is specified

Examples:
- "Show me all my calendars"
- "Create a meeting in my Work calendar" 
- "What's on my Family calendar this weekend?"

## Using the Calendar Integration

Once set up, you can interact with your Google Calendar through the voice assistant:

### Examples:

- "What's on my calendar today?"
- "Show me my schedule for next week"
- "Create a meeting with John tomorrow at 2 PM"
- "Schedule a doctor's appointment for next Friday at 10 AM"
- "Find a free time slot for a 30-minute meeting tomorrow"
- "Delete my 3 PM meeting today"

## Troubleshooting

### Token Errors

If you encounter authentication errors:

1. Delete the token file at `~/.credentials/calendar_token.json`
2. Run the setup script again

### Permission Issues

If you need additional calendar permissions:

1. Delete the token file at `~/.credentials/calendar_token.json`
2. Edit the `SCOPES` variable in `app/jarvis/sub_agents/google_calendar_agent/utils.py`
3. Run the setup script again

### API Quota

Google Calendar API has usage quotas. If you hit quota limits:

1. Check your [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to "APIs & Services" > "Dashboard"
3. Select "Google Calendar API"
4. View your quota usage and consider upgrading if necessary

## Security Considerations

- The OAuth token is stored securely in your user directory
- Never share your `credentials.json` file or the generated token
- The application only requests the minimum permissions needed for calendar operations 


uvicorn main:app --reload
