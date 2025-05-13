"""
Tool for creating new events in Google Calendar.
"""

from ..utils import get_calendar_service, parse_datetime


def create_event(
    summary: str,
    start_time: str,
    end_time: str,
    description: str,
    location: str,
    attendees: str,
    all_day: bool,
    calendar_id: str,
) -> dict:
    """
    Create a new event in Google Calendar.

    Args:
        summary (str): Event title/summary
        start_time (str): Start time (e.g., "2023-12-31 14:00" or "2023-12-31" for all-day)
        end_time (str): End time (e.g., "2023-12-31 15:00" or "2024-01-01" for all-day)
        description (str): Event description
        location (str): Event location
        attendees (str): Comma-separated list of email addresses
        all_day (bool): Whether this is an all-day event
        calendar_id (str): ID of the calendar to use (use 'primary' for default calendar)

    Returns:
        dict: Information about the created event or error details
    """
    try:
        # Get calendar service
        service = get_calendar_service()
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Google Calendar. Please check credentials.",
            }

        # Process date/time inputs
        start_dt = parse_datetime(start_time)
        end_dt = parse_datetime(end_time)

        if not start_dt or not end_dt:
            return {
                "status": "error",
                "message": "Invalid date/time format. Please use formats like 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD'.",
            }

        # Create event object as dictionary
        event = {}
        event["summary"] = summary
        event["description"] = description
        event["location"] = location

        # Set start and end times based on whether it's an all-day event
        if all_day:
            start_dict = {
                "date": start_dt.strftime("%Y-%m-%d"),
                "timeZone": "UTC",
            }
            end_dict = {
                "date": end_dt.strftime("%Y-%m-%d"),
                "timeZone": "UTC",
            }
            event["start"] = start_dict
            event["end"] = end_dict
        else:
            start_dict = {
                "dateTime": start_dt.isoformat(),
                "timeZone": "UTC",
            }
            end_dict = {
                "dateTime": end_dt.isoformat(),
                "timeZone": "UTC",
            }
            event["start"] = start_dict
            event["end"] = end_dict

        # Add attendees if provided
        if attendees:
            attendee_list = []
            for email in attendees.split(","):
                attendee_list.append({"email": email.strip()})
            event["attendees"] = attendee_list

        # Call the Calendar API to create the event
        created_event = (
            service.events().insert(calendarId=calendar_id, body=event).execute()
        )

        return {
            "status": "success",
            "message": "Event created successfully",
            "event_id": created_event.get("id"),
            "event_link": created_event.get("htmlLink"),
        }

    except Exception as e:
        return {"status": "error", "message": f"Error creating event: {str(e)}"}
