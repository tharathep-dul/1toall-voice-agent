"""
Tool for listing available calendars the user has access to.
"""

from ..utils import get_calendar_service


def list_calendars() -> dict:
    """
    List all calendars the user has access to.

    Returns:
        dict: List of available calendars or error details
    """
    try:
        # Get calendar service
        service = get_calendar_service()
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Google Calendar. Please check credentials.",
                "calendars": [],
            }

        # Get calendar list
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get("items", [])

        if not calendars:
            return {
                "status": "success",
                "message": "No calendars found. Make sure you've granted access to your calendars.",
                "calendars": [],
            }

        # Format calendars for display
        formatted_calendars = []
        for calendar in calendars:
            formatted_calendar = {
                "id": calendar.get("id"),
                "summary": calendar.get("summary", "Unnamed Calendar"),
                "description": calendar.get("description", ""),
                "primary": calendar.get("primary", False),
                "access_role": calendar.get("accessRole", "Unknown"),
                "color": calendar.get("backgroundColor", "#FFFFFF"),
            }
            formatted_calendars.append(formatted_calendar)

        return {
            "status": "success",
            "message": f"Found {len(formatted_calendars)} calendar(s).",
            "calendars": formatted_calendars,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching calendars: {str(e)}",
            "calendars": [],
        }
