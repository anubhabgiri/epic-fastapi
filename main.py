from fastapi import APIRouter, FastAPI

from logger import logger
from functions import search_patient,get_patient,add_patient


app = FastAPI()


@app.post("/patient_search")
async def search_patient_x(payload: dict):
    logger.info(f"Payload received to search patient: {payload}")
    r = search_patient(payload)
    return {"status": 200, "data": r}


@app.get("/patient/{patient_id}")
async def return_patient(patient_id: str):
    """
    return patient 
    """
    # all negative cases are handled inside get_patient
    # TODO any formatting in the response body as required
    logger.info(f"Payload received to return single patient:{patient_id}")
    patient = get_patient(patient_id)
    return {"status": 200, "data": patient}


@app.post("/create_patient")
async def create_patient_x(payload: dict):
    logger.info(f"Payload received to create patient:{payload}")
    r = add_patient(payload)
    return {"status": 200, "data": r}
