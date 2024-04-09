import instructor
import openai
from pydantic import BaseModel, Field, ValidationError
from typing import List, Literal
import json
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
api_key = os.getenv("OPENAI_API_KEY")

instructor_openai_client = instructor.patch(openai.Client(
    api_key=api_key,
    timeout=20000,
    max_retries=3
))

class TimeExtract(BaseModel):
    weeks: str = Field(default="NULL", description="The number of weeks for the event.")
    month: str = Field(default="NULL", description="The month of the event.")
    year: str = Field(default="NULL", description="The year of the event.")
    time: str = Field(default="NULL", description="The time of the event.")

class TaskDetails(BaseModel):
    day: str = Field(default="NULL", description="The day of the event.")
    event: str = Field(default="NULL", description="The title or name of the event.")
    current_day: str = Field(default="NULL", description="The current day mentioned in the conversation.")
    successive_day: str = Field(default="NULL", description="The successive day mentioned in the conversation.")
    timeline: TimeExtract = Field(default=None, description="The time-related details of the event.")

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
The hacknight will be conducted in two weeks on April 15th, 2023 at 7:00 PM.
The company's quarterly meeting is scheduled for May 1st, 2023 at 10:00 AM.
"""

multiple_task_data = extract_event_details(conversation_summary)

if multiple_task_data:
    print(json.dumps(multiple_task_data.dict(), indent=2))
else:
    print("Failed to extract event details.") 