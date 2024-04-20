import instructor
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv
import os
from datetime import datetime, date, timedelta
import json
from gcalender.cal import run

today = date.today()
now = datetime.now()
hour = int(now.strftime("%H"))+1
time_details = f"{hour}:00:00"

print("Today's date:", today)   
print("Current time:", time_details)



# Load your OpenAI API key from a .env file
load_dotenv(find_dotenv())
api_key = os.getenv("OPENAI_API_KEY")

# Patch the OpenAI client
client = instructor.from_openai(OpenAI(
    api_key=api_key,
    timeout=20000,
    max_retries=3
))


summary = f"""
Current date {today}, current time {time_details}

I have a meeting with the team tomorrow at noon.
I have a meeting with the team today at 5pm.
Brainstorming session next Friday at 10am.
I have to complete the project by next Tuesday.
Exam starts on Monday morning.
"""

if "morning" in summary.lower():
    summary = summary.replace("morning", "08:00:00")
if "noon" in summary.lower():
    summary = summary.replace("noon", "12:00:00")
if "evening" in summary.lower():
    summary = summary.replace("evening", "16:00:00")
if "today" in summary:
    summary = summary.replace("today", str(today))
if "tomorrow" in summary:
    tmmr =  str(date.today() + timedelta(days=1))
    summary = summary.replace("tomorrow", tmmr )


class TimeV(BaseModel):
    hours: str = Field(fault= str(hour), description="Hour of the event (24-hour format)")
    minutes: str = Field(default= "00", description="Minutes of the event")
    seconds: str = Field(default= "00", description="Seconds of the event")


default_time = TimeV(hours= str(hour), minutes="00", seconds="00")

class TimeDetails(BaseModel):
    date: str = Field(default= today, description="Date of the event") 
    start_time: TimeV = Field(default= default_time, description="Start time of the event")
    end_time: TimeV = Field(default= default_time, description="End time of the event")

class TaskDetails(BaseModel):
    eventname: str = Field(default="Event", description="Title or summary of the event")
    timeline: TimeDetails = Field(default= None, description="Date and time details")

class MultipleTaskData(BaseModel):
    tasks: List[TaskDetails]

# Extract structured data from natural language
user_info = client.chat.completions.create(
    model="gpt-3.5-turbo",
    response_model=MultipleTaskData,
    messages=[{"role": "user", "content": f"Please convert the following information into valid JSON representing the event details: {summary} specifically for assigning each task to google calender api."}],
)
# print(json.dumps(user_info.model_dump(), indent=1))

tasks = user_info.dict()["tasks"]

for task in tasks:
    print("Event name:", task["eventname"])
    event_name = task["eventname"]
    print("Date:", task["timeline"]["date"])
    date = task["timeline"]["date"]
    print("Start time: ",task["timeline"]["start_time"]["hours"]+":"+task["timeline"]["start_time"]["minutes"]+":"+task["timeline"]["start_time"]["seconds"])
    start_time = task["timeline"]["start_time"]["hours"]+":"+task["timeline"]["start_time"]["minutes"]+":"+task["timeline"]["start_time"]["seconds"]
    print("End time: ",task["timeline"]["end_time"]["hours"]+":"+task["timeline"]["end_time"]["minutes"]+":"+task["timeline"]["end_time"]["seconds"])
    end_time = task["timeline"]["end_time"]["hours"]+":"+task["timeline"]["end_time"]["minutes"]+":"+task["timeline"]["end_time"]["seconds"]
    print("\n")
    
    run(summary=event_name, start_time=f"{date}T{start_time}", end_time=f"{date}T{end_time}", description="Automated by ...")
