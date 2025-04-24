import streamlit as st
import requests
from ics import Calendar
import recurring_ical_events
import datetime
import icalendar

# Set page title
st.set_page_config(page_title="Free Time Slot Finder", layout="wide")

# Function to get free times (from the provided code)
def get_free_times_for_date_range(ics_url, start_date_str, end_date_str):
    """
    Retrieves free time slots between 9 am and 5 pm for each date within a range.

    Args:
        ics_url: URL of the ICS calendar file.
        start_date_str: Start date string in YYYY-MM-DD format.
        end_date_str: End date string in YYYY-MM-DD format.

    Returns:
        A dictionary where keys are dates and values are lists of free time slots 
        for that date.
    """

    # Fetch calendar data only once
    response = requests.get(ics_url)
    ical_string = response.content
    calendar = icalendar.Calendar.from_ical(ical_string)

    start_date = datetime.datetime.strptime(start_date_str, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d").date()

    free_times_by_date = {}  # Store free times for each date

    for current_date in [start_date + datetime.timedelta(days=x) for x in range(0, (end_date-start_date).days + 1)]:
        # add one day to the datetime
        current_date_future = current_date + datetime.timedelta(days=1)

        # Get events for the target date
        events_for_day = [
            event for event in recurring_ical_events.of(calendar).between(current_date, current_date_future)
        ]

        # Define working hours (9 am to 5 pm)
        work_start = datetime.datetime.combine(current_date, datetime.time(9, 0))
        work_end = datetime.datetime.combine(current_date, datetime.time(17, 0))

        # Initialize free time slots with the entire working hours
        free_times = [(work_start, work_end)]

        # Adjust free time slots based on events
        for event in events_for_day:
            event_start = event["DTSTART"].dt.replace(tzinfo=None)  # Remove timezone for comparison
            event_end = event["DTEND"].dt.replace(tzinfo=None)  # Remove timezone for comparison

            updated_free_times = []
            for start, end in free_times:
                if event_start >= end or event_end <= start:
                    # Event outside current free slot, keep the slot
                    updated_free_times.append((start, end))
                else:
                    # Event overlaps current free slot, split the slot
                    if event_start > start:
                        updated_free_times.append((start, event_start))
                    if event_end < end:
                        updated_free_times.append((event_end, end))
            free_times = updated_free_times

        free_times_by_date[current_date] = free_times  # Store free times for current date

    return free_times_by_date

# Application title
st.title("Free Time Slot Finder")
st.write("Find available time slots in your calendar within a specified date range.")

# Default ICS URL (from the provided example)
default_ics_url = "https://outlook.office365.com/owa/calendar/4ad02a7e9e6f42c78ca2d4315deb9db2@mit.edu/c10ddb3f0fc44257a81eed8e7d7f1a545527055253664937927/calendar.ics"

# Input form
with st.form(key="free_time_form"):
    # ICS URL input (read-only/greyed out)
    ics_url = st.text_input("ICS Calendar URL", 
                           value=default_ics_url, 
                           disabled=True,
                           help="The URL of the ICS calendar file (read-only)")
    
    # Create a row with two columns for date pickers
    col1, col2 = st.columns(2)
    
    # Default to tomorrow as start date
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    
    # Date pickers
    with col1:
        start_date = st.date_input("Start Date", 
                                   value=tomorrow,
                                   help="Select the start date for checking free time slots")
    
    with col2:
        # Default end date is 3 days from start
        default_end = start_date + datetime.timedelta(days=3)
        end_date = st.date_input("End Date", 
                                 value=default_end,
                                 help="Select the end date for checking free time slots")
    
    # Submit button
    submit_button = st.form_submit_button(label="Find Free Time Slots")

# Process and display results when form is submitted
if submit_button:
    # Input validation
    if start_date > end_date:
        st.error("Error: Start date must be before end date.")
    else:
        # Show loading message
        with st.spinner("Fetching calendar data and finding free time slots..."):
            try:
                # Convert dates to string format
                start_date_str = start_date.strftime("%Y-%m-%d")
                end_date_str = end_date.strftime("%Y-%m-%d")
                
                # Call the function to get free times
                free_times_by_date = get_free_times_for_date_range(ics_url, start_date_str, end_date_str)
                
                # Display results
                st.subheader("Available Free Time Slots")
                
                # Create a container for the results
                results_container = st.container()
                
                with results_container:
                    if not free_times_by_date:
                        st.info("No free time slots found in the selected date range.")
                    else:
                        for date, free_times in free_times_by_date.items():
                            # Format the date in the requested format: M/D (Weekday)
                            weekday = date.strftime("%a")[:3]  # First 3 letters of weekday
                            formatted_date = f"{date.month}/{date.day} ({weekday})"
                            
                            if not free_times:
                                st.write(f"**{formatted_date}**: No free time slots available")
                            else:
                                # Create formatted list of time slots
                                time_slots = []
                                for start, end in free_times:
                                    # Format times in a more compact way (9a, 10:30a, 2p, etc.)
                                    start_hour = int(start.strftime("%I"))
                                    start_min = start.strftime("%M")
                                    start_ampm = start.strftime("%p").lower()[0]  # 'a' or 'p'
                                    
                                    end_hour = int(end.strftime("%I"))
                                    end_min = end.strftime("%M")
                                    end_ampm = end.strftime("%p").lower()[0]  # 'a' or 'p'
                                    
                                    # Format with or without minutes
                                    start_fmt = f"{start_hour}:{start_min}{start_ampm}" if start_min != "00" else f"{start_hour}{start_ampm}"
                                    end_fmt = f"{end_hour}:{end_min}{end_ampm}" if end_min != "00" else f"{end_hour}{end_ampm}"
                                    
                                    time_slots.append(f"{start_fmt}-{end_fmt}")
                                
                                # Join all time slots with commas
                                time_slots_str = ", ".join(time_slots)
                                
                                # Display in the requested format
                                st.write(f"**{formatted_date}**: {time_slots_str} ET")
                                
                                st.write("---")  # Add a separator between dates
                
            except Exception as e:
                st.error(f"Error occurred: {str(e)}")
                st.info("Please check if the ICS URL is valid and accessible.")

# Add some informational text at the bottom
st.info("""
**Note**: This application displays free time slots between 9 AM and 5 PM for the selected date range.
It uses the calendar data from the provided ICS URL to determine availability.
""")
