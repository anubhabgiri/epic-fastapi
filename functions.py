import os
import time
import uuid
import json
import jwt
import requests
import xmltodict
from dotenv import load_dotenv
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError, Field, model_validator
from rest_framework import status
from typing_extensions import Self

from .mongo_functions import add_patient_identifier
from .patient import patient_builder

from logger import logger

load_dotenv()
# KEY
EPIC_PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# TOKEN CONSTANTS
TOKEN_URL = "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token"
TOKEN_HEADER = {"Content-Type": "application/x-www-form-urlencoded"}


# NOTE the final behaviour of these functions will be determined by the usage of the endpoints but it should still be decoupled as much as possible


class SearchPatient(BaseModel):
    address: str | None = None
    address_city: str | None = Field(None, alias='address_city')
    address_postalcode: str | None = Field(None, alias='address_postalcode')
    address_state: str | None = Field(None, alias='address-state')
    birthdate: str | None = None  # format needed
    family: str | None = None
    given: str | None = None
    gender: str | None = None
    identifier: str | None = None
    telecom: str | None = None
    name: str | None = None
    own_name: str | None = Field(None, alias='own_name')
    own_prefix: str | None = Field(None, alias='own-prefix')
    partner_name: str | None = Field(None, alias='partner_name')
    partner_prefix: str | None = Field(None, alias='partner_prefix')
    legal_sex: str | None = Field(None, alias="legal-sex")

    @model_validator(mode='after')
    def verify_square(self) -> Self:
        values = self.model_dump().values()
        filtered_values = filter(lambda x: x is not None, values)
        if len(list(filtered_values)) < 1:
            raise ValueError('At least one valid field must be provided')
        return self


def generate_token():
    """

    Return: a JWT token to raise request for EPIC bearer token
    """

    with open(EPIC_PRIVATE_KEY, "r") as key_file:
        private_key = key_file.read()

    jwt_payload = {
        "iss": os.getenv("CLIENT_ID", "dummy"),
        "sub": os.getenv("CLIENT_ID", "dummy"),
        "aud": "https://fhir.epic.com/interconnect-fhir-oauth/oauth2/token",
        "jti": str(uuid.uuid1()),
        "exp": int(time.time()) + 300,
    }

    token = jwt.encode(jwt_payload, private_key, algorithm="RS384")
    return token


def get_bearer_token(jwt_token):
    """
    fetch a bearer token to access open EPIC FHIR  application
    """
    TOKEN_PAYLOAD = f"grant_type=client_credentials&client_assertion_type=urn%3Aietf%3Aparams%3Aoauth%3Aclient-assertion-type%3Ajwt-bearer&client_assertion={jwt_token}"
    response = requests.request(
        "POST", TOKEN_URL, headers=TOKEN_HEADER, data=TOKEN_PAYLOAD
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None


def authorize_application():
    """
    authorize application

    """
    jwt_token = generate_token()
    bearer_token = get_bearer_token(jwt_token)
    return bearer_token


def check_authorization() -> bool:
    """
    validate if there is a bearer token available to access the application
    """
    # FUTURE SCOPE
    pass


def match_patient(query_set: dict):
    """
    return a single patient matching the query
    """


def search_patient(query_set: dict):
    """
    search patient
    """
    logger.info(f"Request Received to search patient: {query_set}")
    patient_query_object = None
    try:
        patient_query_object = SearchPatient(**query_set)
        patient_query_object = patient_query_object.model_dump()
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=e.json()
        )

    bearer_token = authorize_application()
    url = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient"
    headers = {
        "Authorization": "bearer {}".format(bearer_token),
    }
    response = requests.request("GET", url, headers=headers, params=patient_query_object)
    if response.status_code == 200:
        logger.info(f"Request Successful for search patient: {query_set}")
        resp_xml = response.text
        if resp_xml is not None and len(resp_xml) > 0:
            resp = xmltodict.parse(resp_xml)
            return resp
        else:
            logger.info(f"No content found for : {query_set}")
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT, detail="No content"
            )
    elif response.status_code == 404:
        logger.info(f"Patient not found : {query_set}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    else:
        logger.error(f"Internal server error : {query_set}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


def add_patient(payload: dict) -> None:
    """
    add patient
    """
    logger.info("Request Received for add_patient function with payload: %s", payload)
    bearer_token = authorize_application()
    url = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "bearer {}".format(bearer_token),
    }
    patient = None
    try:
        patient = patient_builder(**payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    if patient is not None:
        print("fhir patient", patient)
        response = requests.request("POST", url, headers=headers, data=json.dumps(patient))
        if response.status_code == 201:
            resp_headers = response.headers
            patient_location = resp_headers["Location"]
            # created_date = resp_headers["Date"]
            add_patient_identifier(patient_location, payload.get("email", ""))
            logger.info("Patient identifier added for email: %s", payload.get("email", ""))
        else:
            logger.error("Failed to create patient. Status code: %s, Response: %s", response.status_code, response.text)


def get_patient(patient_epic_id: str):
    """
    get patient
    """
    logger.info(f"Request Received to get patient: {patient_epic_id}")
    bearer_token = authorize_application()
    url = "https://fhir.epic.com/interconnect-fhir-oauth/api/FHIR/R4/Patient/{}".format(
        patient_epic_id
    )
    headers = {
        "Content-Type": "application/json",
        "Authorization": "bearer {}".format(bearer_token),
    }

    response = requests.request("GET", url, headers=headers)
    if response.status_code == 200:
        logger.info(f"Patient identifier added for email: {patient_epic_id}")
        resp_xml = response.text
        if resp_xml is not None and len(resp_xml) > 0:
            resp = xmltodict.parse(resp_xml)
            return resp
        else:
            logger.error(f"Failed to get patient: {patient_epic_id} ")
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT, detail="No content"
            )
    elif response.status_code == 404:
        logger.info(f"Patient not found: {patient_epic_id} ")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found"
        )
    else:
        logger.error(f"Internal server error: {patient_epic_id} ")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
