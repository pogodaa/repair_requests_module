from pydantic import BaseModel

class RequestCreate(BaseModel):
    climateTechType: str
    climateTechModel: str
    problemDescryption: str

    class Config:
        orm_mode = True