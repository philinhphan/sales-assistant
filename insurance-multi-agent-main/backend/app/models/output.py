from __future__ import annotations
from pydantic import BaseModel, HttpUrl
from datetime import date
from typing import List, Literal, Dict

class NewsItem(BaseModel):
    title:       str
    description: str
    type:        Literal["M&A", "Stock", "Success", "Partnership", "Product"]
    date:        date

class Contact(BaseModel):
    name:       str
    position:   str
    department: str
    reasoning:  str

class ProductFit(BaseModel):
    product:    str
    confidence: Literal["High", "Medium", "Low"]
    reasoning:  str

class Company(BaseModel):
    name:          str
    headquarters:  str
    employees:     str
    coreProducts:  List[str]
    news:          List[NewsItem]
    productFit:    ProductFit
    keyContacts:   List[Contact]
    salesApproach: str

class LeadIn(BaseModel):
    company_name: str
    country:      str

class LeadOut(BaseModel):
    # now just a single Company record
    company: Company

    class Config:
        # forbid extra fields so schema has additionalProperties=false
        extra = "forbid"