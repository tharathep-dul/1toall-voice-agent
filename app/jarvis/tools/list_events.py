"""
List events tool for Google Calendar integration.
"""

import datetime

from .calendar_utils import format_event_time, get_calendar_service


def list_events(
    start_date: str,
    days: int,
    max_results: int,
    calendar_id: str,
) -> dict:
    """
    List upcoming calendar events within a specified date range.

    Args:
        start_date (str): Start date in YYYY-MM-DD format. If empty, defaults to today.
        days (int): Number of days to look ahead.
        max_results (int): Maximum number of events to return (hardcoded to 100 internally).
        calendar_id (str): ID of the calendar to use (use 'primary' for default calendar).

    Returns:
        dict: Information about upcoming events or error details
    """
    try:
        # Get calendar service
        service = get_calendar_service()
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Google Calendar. Please check credentials.",
                "events": [],
            }

        # Always use a large max_results value to return all events
        max_results = 100

        # Check if we need to lookup calendar_id (if only one calendar exists)
        if (
            calendar_id != "primary"
            and "," not in calendar_id
            and not calendar_id.endswith(".com")
        ):
            # This might be a calendar name instead of ID, try to find matching calendar
            try:
                from .list_calendars import list_calendars

                calendars_result = list_calendars()
                if (
                    calendars_result["status"] == "success"
                    and calendars_result["calendars"]
                ):
                    # If only one calendar exists, use that one
                    if len(calendars_result["calendars"]) == 1:
                        calendar_id = calendars_result["calendars"][0]["id"]
                    else:
                        # Look for a calendar with a matching name
                        for cal in calendars_result["calendars"]:
                            if calendar_id.lower() in cal["summary"].lower():
                                calendar_id = cal["id"]
                                break
            except Exception as e:
                print(f"Error looking up calendar: {str(e)}")
                # Continue with the original calendar_id

        # Set time range
        if not start_date or start_date.strip() == "":
            start_time = datetime.datetime.utcnow()
        else:
            try:
                start_time = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                return {
                    "status": "error",
                    "message": f"Invalid date format: {start_date}. Use YYYY-MM-DD format.",
                    "events": [],
                }

        # If days is not provided or is invalid, default to 1 day
        if not days or days < 1:
            days = 1

        end_time = start_time + datetime.timedelta(days=days)

        # Format times for API call
        time_min = start_time.isoformat() + "Z"
        time_max = end_time.isoformat() + "Z"

        # Call the Calendar API
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])

        if not events:
            return {
                "status": "success",
                "message": "No upcoming events found.",
                "events": [],
            }

        # Format events for display
        formatted_events = []
        for event in events:
            formatted_event = {
                "id": event.get("id"),
                "summary": event.get("summary", "Untitled Event"),
                "start": format_event_time(event.get("start", {})),
                "end": format_event_time(event.get("end", {})),
                "location": event.get("location", ""),
                "description": event.get("description", ""),
                "attendees": [
                    attendee.get("email")
                    for attendee in event.get("attendees", [])
                    if "email" in attendee
                ],
                "link": event.get("htmlLink", ""),
            }
            formatted_events.append(formatted_event)

        return {
            "status": "success",
            "message": f"Found {len(formatted_events)} event(s).",
            "events": formatted_events,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching events: {str(e)}",
            "events": [],
        }
