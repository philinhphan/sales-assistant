from datetime import datetime
from typing import Any, Dict, List
from pydantic import BaseModel, ConfigDict, HttpUrl

class CompanyInfo(BaseModel):
    model_config = ConfigDict(extra='forbid')
    overview: str
    industry: str
    size: str
    headquarters: str

class NewsArticle(BaseModel):
    model_config = ConfigDict(extra='forbid')
    headline: str
    date:      datetime

class NewsInfo(BaseModel):
    model_config = ConfigDict(extra='forbid')
    articles:        List[NewsArticle]
    keyDevelopments: str

class ProductFit(BaseModel):
    model_config = ConfigDict(extra='forbid')
    rationale:   str
    strengths:   List[str]
    limitations: List[str]

class PersonOfInterest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name:     str
    role:     str
    interest: str

class SalesApproach(BaseModel):
    model_config = ConfigDict(extra='forbid')
    talkingPoints:      List[str]
    objectionHandling:  List[str]

class SalesPitch(BaseModel):
    model_config = ConfigDict(extra='forbid')
    subject: str
    body:    str

class LeadOut(BaseModel):
    model_config = ConfigDict(extra='forbid')
    companyInfo:      CompanyInfo
    newsInfo:         NewsInfo
    productFit:       ProductFit
    peopleOfInterest: List[PersonOfInterest]
    salesApproach:    SalesApproach
    salesPitch:       SalesPitch


class LeadIn(BaseModel):
    company_name: str
    country:      str