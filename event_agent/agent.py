import os
from pathlib import Path
from datetime import datetime
from typing import List

from google.adk.agents import Agent

from .models import Event

# Load events data from the stored JSON and keep in memory as typed Event objects
DATA_DIR = Path(os.getenv("DATA_DIR", Path(__file__).resolve().parents[1] / "data"))
EVENTS_FILE = DATA_DIR / "all-events.json"

events_data: List[Event] = []


def load_events() -> None:
    global events_data
    try:
        if not EVENTS_FILE.exists():
            raise FileNotFoundError(f"Events file not found at {EVENTS_FILE}. Run scripts/fetch_events.py first.")
        raw = EVENTS_FILE.read_text(encoding="utf-8")
        import json

        parsed = json.loads(raw)
        if isinstance(parsed, list):
            events_data = [Event.from_raw(item) for item in parsed]
        else:
            events_data = []
    except Exception as e:
        print(f"Failed to load events data: {e}")
        events_data = []


def filter_events_by_name(query: str, events: List[Event]) -> List[Event]:
    q = query.strip().lower()
    return [event for event in events if q in (event.name or "").lower()]


def filter_events_by_date_range(start_date: str, end_date: str, events: List[Event]) -> List[Event]:
    # Expecting YYYY-MM-DD inputs. We treat them as inclusive dates and check for range overlap.
    start = datetime.strptime(start_date, "%Y-%m-%d").date()
    end = datetime.strptime(end_date, "%Y-%m-%d").date()
    filtered: List[Event] = []
    for event in events:
        if event.start_time is None and event.end_time is None:
            continue
        ev_start = (event.start_time or event.end_time).date()
        ev_end = (event.end_time or event.start_time).date()
        # overlap if event starts before end and ends after start
        if ev_start <= end and ev_end >= start:
            filtered.append(event)
    return filtered


def filter_events_by_city(city: str, events: List[Event]) -> List[Event]:
    c = city.strip().lower()
    return [event for event in events if (event.city or "").lower().find(c) != -1]


def filter_events_by_country(country: str, events: List[Event]) -> List[Event]:
    c = country.strip().lower()
    return [event for event in events if (event.country or "").lower().find(c) != -1]


def get_events(query: str = "", start_date: str = "", end_date: str = "", city: str = "", country: str = "") -> dict:
    """Fetch events from in-memory cache based on various filters and return a list of matches.

    Args:
        query: Text to search for in event names.
        start_date: Inclusive start date (YYYY-MM-DD) to filter events.
        end_date: Inclusive end date (YYYY-MM-DD) to filter events.
        city: City name fragment to filter events.
        country: Country name fragment to filter events.

    Returns:
        dict: status and result or error message.
    """
    filtered_events: List[Event] = events_data

    if query:
        filtered_events = filter_events_by_name(query, filtered_events)
    if start_date and end_date:
        filtered_events = filter_events_by_date_range(start_date, end_date, filtered_events)
    if city:
        filtered_events = filter_events_by_city(city, filtered_events)
    if country:
        filtered_events = filter_events_by_country(country, filtered_events)

    if not filtered_events:
        return {
            "status": "error",
            "error_message": "No events found for the given criteria."
        }

    # Limit the response to a maximum of 10 events
    limited_events = [e.to_public_dict() for e in filtered_events[:10]]
    return {
        "status": "success",
        "events": limited_events
    }


root_agent = Agent(
    name="event_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about events, including when and where they occur, and other details."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about events, providing details such as name, date, location, and more."
    ),
    tools=[get_events],
)

# Load events data when the module is imported
load_events()