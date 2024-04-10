import instructor
import openai
from pydantic import BaseModel, Field, ValidationError
from typing import List, Literal
import json
import os
from dotenv import load_dotenv, find_dotenv
from cal import run
from datetime import datetime, date, timedelta

today = date.today()
now = datetime.now()
time_details = now.strftime("%H:%M:%S")

load_dotenv(find_dotenv())
api_key = os.getenv("OPENAI_API_KEY")

instructor_openai_client = instructor.patch(openai.Client(
    api_key=api_key,
    timeout=20000,
    max_retries=3
))

date_details = date.today().strftime("%B %d, %Y")
w = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
day = w[date.today().weekday()]

class TimeExtract(BaseModel):
    date: str = Field(default=f"{today}", description=f"The date of the event if present in the text. It should be derived from phrases like 'next Monday', 'this Friday', etc. Current date is {today}. Return in YYYY-MM-DD format.")
    start_time: str = Field(default=f"{time_details}", description=f"The start time of the event if present. Change to %H%H:%M%M:%S%S . Current time is {time_details}")
    end_time: str = Field(default="NULL", description="The end time of the event.Change to %H%H:%M%M:%S%S")

class TaskDetails(BaseModel):
    day: Literal['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday', 'NULL'] = Field(default="NULL", description="The day of the event if present in the summary.")
    event: str = Field(default="NULL", description="Title or summary of the event.")
    current_day: Literal['Yes', 'No'] = Field(default="No", description="The current day mentioned in the conversation.")
    successive_day: Literal['Yes', 'No'] = Field(default="No", description="The successive day mentioned in the conversation.")
    timeline: TimeExtract = Field(default=None, description="The time-related details of the event.")

class MultipleTaskData(BaseModel):
    tasks: List[TaskDetails]

def extract_event_details(conversation_summary: str) -> MultipleTaskData:
    completion = instructor_openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": f"Please convert the following information into valid JSON representing the event details: {conversation_summary} specifically for assigning each task to google calender api."}
        ],
        response_model=MultipleTaskData
    )

    try:
        multiple_task_data = MultipleTaskData(**completion.model_dump())
        return multiple_task_data
    except ValidationError as e:
        print(f"Error extracting event details: {e}")
        return None

# Example usage
conversation_summary = """
A meeting is to be held on Monday at 10:00 AM. The meeting will be about the new project.
There's a project deadline with a friend by this evening, requiring immediate attention to send out an email.
Furthermore, a dentist appointment needs scheduling for the upcoming Friday.
Amid this, there's also a pressing task to complete algorithm analysis assignments by next Tuesday, ahead of an exam scheduled for Monday.
"""

if "by this evening" or "by evening" or "today evening" in conversation_summary:
    conversation_summary = conversation_summary.replace("by this evening", "by 4:00 PM")
    conversation_summary = conversation_summary.replace("by evening", "by 4:00 PM")
    conversation_summary = conversation_summary.replace("today evening", "by 4:00 PM")
if "today" in conversation_summary:
    conversation_summary = conversation_summary.replace("today", today)
if "tomorrow" in conversation_summary:
    conversation_summary = conversation_summary.replace("tomorrow", today + timedelta(days=1))

if "by this morning" or "by morning" or "today morning" in conversation_summary:
    conversation_summary = conversation_summary.replace("by this morning", "by 8:00 AM")
    conversation_summary = conversation_summary.replace("by morning", "by 8:00 AM")
    conversation_summary = conversation_summary.replace("today morning", "by 8:00 AM")

if "by this noon" or "by noon" or "today noon" in conversation_summary:
    conversation_summary = conversation_summary.replace("by this noon", "by 12:00 PM")
    conversation_summary = conversation_summary.replace("by noon", "by 12:00 PM")
    conversation_summary = conversation_summary.replace("today noon", "by 12:00 PM")

conversation_summary = f"""
Current details:{time_details}, {date_details}, {day}
Had a very hectic day with continuous classes from morning till evening.
Need to brainstorm ideas on building access Laravel this year 2023.
Must focus on finishing a project with a friend by this evening to send the mail.
Need to schedule a meeting with the dentist for next Friday.
Have to complete assignments for algorithm analysis by next Tuesday.
Exam starts on Monday.
"""

multiple_task_data = extract_event_details(conversation_summary)

if multiple_task_data:
    print(json.dumps(multiple_task_data.dict(), indent=2))
    tasks = multiple_task_data.dict()["tasks"]
    print(tasks)
    print(len(tasks))

    for task in tasks:
        if task["timeline"]["date"] == "NULL":
            task["timeline"]["date"] = today
        if task["timeline"]["start_time"] == "NULL":
            task["timeline"]["start_time"] = time_details
        if task["timeline"]["end_time"] == "NULL":
            task["timeline"]["end_time"] = (
                datetime.strptime(task["timeline"]["start_time"], "%H:%M:%S")
                + timedelta(hours=1)
            ).strftime("%H:%M:%S")
        start_time = task["timeline"]["start_time"]
        end_time = task["timeline"]["end_time"]
        run(summary=task["event"], start_time=start_time, end_time=end_time)
else:
    print("Failed to extract event details.")