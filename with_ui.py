import streamlit as st
import instructor
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
from datetime import datetime, date, timedelta
import json

today = date.today()
now = datetime.now()
hour = int(now.strftime("%H")) + 1
time_details = f"{hour}:00:00"

print("Today's date:", today)
print("Current time:", time_details)

# Define your desired output structure
class TimeV(BaseModel):
    hours: str = Field(default=str(hour), description="Hour of the event")
    minutes: str = Field(default="00", description="Minutes of the event")
    seconds: str = Field(default="00", description="Seconds of the event")

class TimeDetails(BaseModel):
    date: str = Field(default=today, description="Date of the event")
    start_time: TimeV = Field(default=TimeV(), description="Start time of the event")
    end_time: TimeV = Field(default=TimeV(), description="End time of the event")

class TaskDetails(BaseModel):
    eventname: str = Field(default="Event", description="Title or summary of the event")
    timeline: TimeDetails = Field(default=None, description="Date and time details")

class MultipleTaskData(BaseModel):
    tasks: List[TaskDetails]

def process_data(summary):
    # Load your OpenAI API key from a .env file
    load_dotenv(find_dotenv())
    api_key = os.getenv("OPENAI_API_KEY")

    # Patch the OpenAI client
    client = instructor.from_openai(OpenAI(
        api_key=api_key,
        timeout=20000,
        max_retries=3
    ))

    if "morning" in summary.lower():
        summary = summary.replace("morning", "8:00:00")
    if "noon" in summary.lower():
        summary = summary.replace("noon", "12:00:00")
    if "evening" in summary.lower():
        summary = summary.replace("evening", "16:00:00")
    if "today" in summary:
        summary = summary.replace("today", str(today))
    if "tomorrow" in summary:
        tmmr = str(date.today() + timedelta(days=1))
        summary = summary.replace("tomorrow", tmmr)

    user_info = client.chat.completions.create(
        model="gpt-3.5-turbo",
        response_model=MultipleTaskData,
        messages=[{"role": "user", "content": f"Please convert the following information into valid JSON representing the event details: {summary} specifically for assigning each task to google calender api."}],
    )

    result = json.dumps(user_info.model_dump(), indent=2)
    return result

def display_event_buttons(data):
    if 'added_events' not in st.session_state:
        st.session_state['added_events'] = set()

    # Initialize all checkbox states in session_state before any checkbox widgets are created
    for i, task in enumerate(data["tasks"]):
        checkbox_id = f"add_{i}"
        if checkbox_id not in st.session_state:
            st.session_state[checkbox_id] = i in st.session_state['added_events']

    # Create checkboxes and update session_state based on interactions
    for i, task in enumerate(data["tasks"]):
        checkbox_id = f"add_{i}"
        current_value = st.session_state[checkbox_id]
        new_value = st.checkbox(f"Add '{task['eventname']}' to calendar", value=current_value, key=checkbox_id)
        
        if new_value != current_value:
            st.session_state[checkbox_id] = new_value
            if new_value:
                st.session_state['added_events'].add(i)
            else:
                st.session_state['added_events'].discard(i)

def main():
    st.title("Input and Submit Example")

    # Create an input field
    summary = st.text_area("Enter your summary:", """
    Current date 2024-04-13, current time 15:00:00
    I have a meeting with the team tomorrow at noon.
    I have a meeting with the team today at 5pm.
    Brainstorming session next Friday at 10am to 11am.
    I have to complete the project by next Tuesday.
    Exam starts on Monday morning.
    """)

    # Create a submit button
    if st.button("Submit", key="submit_button"):
        with st.spinner("Processing data..."):
            result = process_data(summary)

        # Parse the JSON data
        data = json.loads(result)

        # Display the buttons for each event
        display_event_buttons(data)

if __name__ == "__main__":
    main()