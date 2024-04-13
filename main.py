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


class Symptoms(BaseModel):
    """
        Represents the symptoms of a patient.
    """
    description: str = Field(description="A general scientific and objective description of the symptoms.")
    pain_type: str
    locations: List[str]
    intensity: int
    location_precision: int
    pace: int

class MedicalHistory(BaseModel):
    pathology: str
    symptoms: Symptoms
    increase_with_exertion: bool
    alleviate_with_rest: bool

class RiskFactors(BaseModel):
    spontaneous_history: bool
    smoking_history: bool
    copd_history: bool
    family_history: str

class DifferentialDiagnosis(BaseModel):
    disease_name: str
    probability: float

class PatientInfo(BaseModel):
    sex: Literal['M', 'F']
    age: int
    geographical_region: str
            
class PatientData(BaseModel):
    patient_info: PatientInfo
    medical_history: MedicalHistory
    risk_factors: RiskFactors
    differential_diagnosis: List[DifferentialDiagnosis]

medical_info = """Sex: Female, Age: 79
Geographical region: North America
Pathology: Spontaneous pneumothorax
Symptoms:
---------
 - I have chest pain even at rest.
 - I feel pain.
 - The pain is:
     » a knife stroke
 - The pain locations are:
     » upper chest
     » breast(R)
     » breast(L)
 - On a scale of 0-10, the pain intensity is 7
 - On a scale of 0-10, the pain's location precision is 4
 - On a scale of 0-10, the pace at which the pain appear is 9
 - I have symptoms that increase with physical exertion but alleviate with rest.
Antecedents:
-----------
 - I have had a spontaneous pneumothorax.
 - I smoke cigarettes.
 - I have a chronic obstructive pulmonary disease.
 - Some family members have had a pneumothorax.
Differential diagnosis:
----------------------
Unstable angina: 0.262, Stable angina: 0.201, Possible NSTEMI / STEMI: 0.160, GERD: 0.145, Pericarditis: 0.091, Atrial fibrillation: 0.082, Spontaneous pneumothorax: 0.060
"""


completion = instructor_openai_client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {
        "role": "user", 
        "content": f"Please convert the following information into valid JSON representing the medical diagnosis {medical_info}."
      }
    ],
    response_model=PatientData # Replace with the appropriate response model
)
print(type(completion))
print(json.dumps(completion.model_dump(), indent=1))