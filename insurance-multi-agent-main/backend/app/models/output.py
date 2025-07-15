from pydantic import BaseModel


class LeadIn(BaseModel):
    company_name: str
    country:      str


class LeadOut(BaseModel):
    companyInfo:       dict
    newsInfo:          dict
    productFit:        dict
    peopleOfInterest:  list
    salesApproach:     dict
    salesPitch:        dict