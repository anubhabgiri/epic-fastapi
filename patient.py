from datetime import datetime
# PATIENT BUILDER

# This builder method has been created based on the HL7 FHIR standard with R4 format

"""
expected input flat file example

"is_active": True, not mandatory
"name" : "Sourav Banerjee", full name, required
"dob": "YYYY-MM-DD",
"image": "https://example.com/image.jpg",
"gender": "male" 
"email: : "sb@unitedwecare.com"


"""
DATE_FORMAT_STRING = '%Y-%m-%d'
def patient_builder(**kwargs):
    patient = dict()

    # This is a constant value, need not be dynamic 
    patient["resourceType"] = "Patient"

    # TODO patient identifier
    patient["identifier"] = [
        {
            "use": "usual",
            "system": "urn:oid:2.16.840.1.113883.4.1",
            "value": "000-00-0000"
        }
    ]
    
    # ACTIVE
    patient["active"] = True
    
    if "is_active" in kwargs:
        patient["active"] = kwargs["is_active"]

    # NAME
    if 'name' not in kwargs:
        raise ValueError("Patient name is required")
     
    patient['name'] = [name_builder(kwargs['name'])]

    # GENDER
    patient['gender'] = 'unknown'
    if 'gender' in kwargs:
        if kwargs['gender'].lower() not in ['male', 'female', 'other', 'unknown']:
            raise ValueError("Invalid gender value. should in one of [male, female, other, unknown]")
        
        patient['gender'] = kwargs['gender'].lower()

    # BIRTH DATE
    if 'dob' not in kwargs:
        raise ValueError("Patient date of birth is required")
    
    if not is_valid_date(kwargs['dob']):
        raise ValueError("Invalid date format for date of birth it should be in YYYY-MM-DD format")
    
    patient["birthDate"] = kwargs['dob']

    # DECEASED 

    # patient["deceasedBoolean"] = False # assumed value

    # ADDRESS TODO

    # MARITAL STATUS TODO

    # patient["multipleBirthBoolean"] = False # assumed value

    # PHOTO TODO
    # CONTACT TODO
    # GENERAL PRACTITIONER
    return patient

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, DATE_FORMAT_STRING)
        return True
    except ValueError:
        return False
    
def name_builder(name: str):
    name_dict = dict()
    name_dict["use"] = "official" # assumed value
    name_list = name.split(' ')
    name_dict["given"] = [name_list[0]]
    
    if len(name_list) > 1:
        name_dict["family"] = name_list[-1]
    return name_dict