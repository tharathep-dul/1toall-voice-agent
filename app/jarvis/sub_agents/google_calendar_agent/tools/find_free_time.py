"""
Tool for finding free time slots in Google Calendar.
"""

import datetime

from ..utils import get_calendar_service, parse_datetime


def find_free_time(
    start_date: str,
    end_date: str,
    duration_minutes: int,
    working_hours_start: int,
    working_hours_end: int,
    calendar_id: str,
) -> dict:
    """
    Find available time slots in the calendar.

    Args:
        start_date (str): Start date to search from (YYYY-MM-DD)
        end_date (str): End date to search to (YYYY-MM-DD)
        duration_minutes (int): Desired meeting length in minutes
        working_hours_start (int): Start of working hours, 24h format (e.g., 9 = 9 AM)
        working_hours_end (int): End of working hours, 24h format (e.g., 17 = 5 PM)
        calendar_id (str): ID of the calendar to use (use 'primary' for default calendar)

    Returns:
        dict: List of available time slots or error details
    """
    try:
        # Get calendar service
        service = get_calendar_service()
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Google Calendar. Please check credentials.",
                "free_slots": [],
            }

        # Parse dates
        start_dt = parse_datetime(start_date)
        end_dt = parse_datetime(end_date)

        if not start_dt or not end_dt:
            return {
                "status": "error",
                "message": "Invalid date format. Please use YYYY-MM-DD format.",
                "free_slots": [],
            }

        # Set start/end time to beginning/end of day
        start_dt = start_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Convert to RFC3339 timestamp for API
        time_min = start_dt.isoformat() + "Z"
        time_max = end_dt.isoformat() + "Z"

        # Get existing events in the time range
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])

        # Calculate free time slots
        free_slots = []
        current_date = start_dt.date()
        end_date_dt = end_dt.date()

        # Loop through each day in the range
        while current_date <= end_date_dt:
            # Get today's events
            today_events = [
                event
                for event in events
                if "dateTime" in event["start"]
                and datetime.datetime.fromisoformat(
                    event["start"]["dateTime"].replace("Z", "+00:00")
                ).date()
                == current_date
            ]

            # Set working hours for today
            day_start = datetime.datetime.combine(
                current_date, datetime.time(working_hours_start, 0)
            )
            day_end = datetime.datetime.combine(
                current_date, datetime.time(working_hours_end, 0)
            )

            # Sort today's events by start time
            today_events.sort(
                key=lambda e: datetime.datetime.fromisoformat(
                    e["start"]["dateTime"].replace("Z", "+00:00")
                )
            )

            # Find free slots between events
            current_time = day_start

            for event in today_events:
                event_start = datetime.datetime.fromisoformat(
                    event["start"]["dateTime"].replace("Z", "+00:00")
                )
                event_end = datetime.datetime.fromisoformat(
                    event["end"]["dateTime"].replace("Z", "+00:00")
                )

                # If there's time before this event, add as free slot
                if current_time < event_start:
                    time_diff = (event_start - current_time).total_seconds() / 60
                    if time_diff >= duration_minutes:
                        free_slots.append(
                            {
                                "start": current_time.strftime("%Y-%m-%d %H:%M"),
                                "end": event_start.strftime("%Y-%m-%d %H:%M"),
                                "duration_minutes": int(time_diff),
                            }
                        )

                # Update current time to end of this event
                if event_end > current_time:
                    current_time = event_end

            # Check for free time after last event until end of day
            if current_time < day_end:
                time_diff = (day_end - current_time).total_seconds() / 60
                if time_diff >= duration_minutes:
                    free_slots.append(
                        {
                            "start": current_time.strftime("%Y-%m-%d %H:%M"),
                            "end": day_end.strftime("%Y-%m-%d %H:%M"),
                            "duration_minutes": int(time_diff),
                        }
                    )

            # Move to next day
            current_date += datetime.timedelta(days=1)

        # Filter slots by minimum duration
        free_slots = [
            slot for slot in free_slots if slot["duration_minutes"] >= duration_minutes
        ]

        return {
            "status": "success",
            "message": f"Found {len(free_slots)} available time slots",
            "free_slots": free_slots,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error finding free time slots: {str(e)}",
            "free_slots": [],
        }
