import instructor
import openai
from pydantic import BaseModel, Field, ValidationInfo
from typing import List, Literal
import json
import os
from dotenv import load_dotenv,find_dotenv

load_dotenv(find_dotenv())
api_key=os.getenv("OPENAI_API_KEY")


instructor_openai_client = instructor.patch(openai.Client(
    api_key=api_key, timeout=20000, max_retries=3
))


class TimeExtract(BaseModel):
    weeks: int = Field(default="NULL", description="The number of weeks for the event if exists.")
    date: int = Field(default="NULL", description="The date for the event if exists.")
    month: str = Field(default="NULL", description="The month of the event if exists.")
    year: str = Field(default="NULL", description="The year of the event if exists.")
    time: str = Field(default="NULL", description="The time of the event if exists.")

class TaskDetails(BaseModel):
    day: str = Field(default="NULL", description="The day of the event if present.")
    event: str = Field(default="NULL", description="The title or name of the event if exists.")
    current_day: str = Field(default="NULL", description="The current day mentioned in the conversation is exists.")
    successive_day: str = Field(default="NULL", description="The successive day mentioned in the conversation if exists.")
    timeline: TimeExtract = Field(default=None, description="The time-related details of the event.")

class PatientData(BaseModel):
    task_details: TaskDetails


medical_info = """
The hacknight will be conducted in two weeks
"""

def extract_event_details(conversation_summary: str) -> PatientData:
    completion = instructor_openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Please convert the following information into valid JSON representing the event details: {conversation_summary}."}
        ],
        response_model=PatientData
    )

    try:
        patient_data = PatientData(**completion.model_dump())
        return patient_data
    except ValidationError as e:
        print(f"Error extracting event details: {e}")
        return None

conversation_summary = "The hacknight will be conducted in two weeks on April 15th, 2023 at 7:00 PM."
completion=extract_event_details(conversation_summary)

# print(type(completion))
print(json.dumps(completion.model_dump(), indent=1))