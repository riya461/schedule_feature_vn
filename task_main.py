import instructor
import openai
from pydantic import BaseModel, Field, ValidationError
from typing import List, Literal
import json
import os
from dotenv import load_dotenv, find_dotenv
from cal import run
from datetime import date,datetime

today = date.today()
now = datetime.now()
current_time = now.strftime("%H:%M:%S")
load_dotenv(find_dotenv())
api_key = os.getenv("OPENAI_API_KEY")

instructor_openai_client = instructor.patch(openai.Client(
    api_key=api_key,
    timeout=20000,
    max_retries=3
))

class TimeExtract(BaseModel):
    # weeks: str = Field(default="NULL", description="The number of weeks for the event.")
    # month: Literal['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sept','Oct','Nov','Dec','NULL'] =Field(default="NULL", description="The month of the event.")
    # year: str = Field(default="2024", description="The year of the event if present in text.")
    # time: str = Field(default="NULL", description="The time of the event.")
    date : str = Field(default=f"{today}", description= f"The date of the event if present in the text.  It should be derived from phrases like 'next Monday', 'this Friday', etc. Current date is {today}. Return in DD-MM-YY format.")
    start_time: str = Field(default=f"{current_time}", description= f"The start time of the event if present. Current time is {current_time}")
    end_time: str = Field(default="NULL", description="The end time of the event.")


class TaskDetails(BaseModel):
    day: Literal['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday','NULL'] = Field(default="NULL", description="The day of the event if present in the summary.")
    event: str = Field(default="NULL", description="Title or summary of the event.")
    current_day: Literal['Yes','No'] = Field(default="No", description="The current day mentioned in the conversation.")
    successive_day: Literal['Yes','No'] = Field(default="No", description="The successive day mentioned in the conversation.")
    timeline: TimeExtract = Field(description="The time-related details of the event.")

class MultipleTaskData(BaseModel):
    tasks: List[TaskDetails]

def extract_event_details(conversation_summary: str) -> MultipleTaskData:
    completion = instructor_openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Please convert the following information into valid JSON representing the event details: {conversation_summary}."}
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

"""

multiple_task_data = extract_event_details(conversation_summary)

if multiple_task_data:
    print(json.dumps(multiple_task_data.dict(), indent=2))
    dicti = multiple_task_data.dict()["tasks"]
    print(dicti)
    print(len(dicti))
    for i in range(0, len(dicti)):
        run(summary=dicti[i]["events"], start_time= start_time, end_time= end_time)
else:
    print("Failed to extract event details.") 