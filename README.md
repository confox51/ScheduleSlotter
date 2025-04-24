# Free Time Slot Finder

A Streamlit web application that helps users find available time slots in their calendar within a specified date range.

## Features

- View free time slots between working hours for a specified date range
- Customize working hours (default: 9 AM to 5 PM)
- Set timezone display (ET, CT, MT, PT, GMT, CET, JST, AEST)
- Add buffer times before and after meetings (0-60 minutes)
- Display results in an easy-to-read format with dates and time slots

## Technical Details

Built with:
- Python 3.11
- Streamlit
- icalendar
- ics
- recurring-ical-events
- requests

## Usage

1. The application uses a pre-configured ICS calendar URL
2. Select your desired date range
3. Customize working hours (0-23)
4. Choose your timezone
5. Set buffer times before and after meetings if needed
6. Click "Find Free Time Slots" to view available time slots

## Running the Application

Before first run, install dependencies:
```bash
pip install -r requirements.txt
```
The application runs on port 8501 by default. To start the application:
```bash
streamlit run app.py
```

## Output Format

Results are displayed in the following format:
- M/D (Weekday): Time slots in timezone
- Example: 3/15 (Mon): 9a-10:30a, 2p-5p ET

## Notes

- Time slots are displayed in a compact format (e.g., 9a, 10:30a, 2p)
- Buffer times can be set in 15-minute increments (0, 15, 30, 45, or 60 minutes)
- The application validates input dates and working hours
