from pydantic import BaseModel,Field,field_validator
from typing import Annotated,Literal

class Validator(BaseModel):
    age:Annotated[int,Field(...,description='Please Enter The Age',examples=[8,12,18],ge=8,le=18)]
    gender:Annotated[Literal['male','Male','female','Female'],Field(...,description='Please Enter The Gender')]
    device:Annotated[str,Field(...,description="Please Enter The Primary Device Used")]
    edu_time:Annotated[float,Field(...,description='Please Enter The Time Spent Studying')]
    rec_time:Annotated[float,Field(...,description='Please Enter The Time Spent Recreating')]

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, value: str) -> str:
        value = value.strip().capitalize()  # normalize
        valid_genders = ["Male", "Female"]
        if value not in valid_genders:
            raise ValueError(f"Invalid gender. Must be one of: {valid_genders}")
        return value

    @field_validator("device")
    @classmethod
    def validate_device(cls, value: str) -> str:
        value_clean = value.strip().title()   # "smartphone" → "Smartphone"
        # Fix special case: TV
        if value_clean.lower() in ["tv", "t.v", "television"]:
            return "TV"
        valid_devices = ["Smartphone", "Laptop", "TV", "Tablet"]
        if value_clean not in valid_devices:
            raise ValueError(f"Invalid device. Must be one of: {valid_devices}")
        return value_clean