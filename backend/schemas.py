from typing import Literal

from pydantic import BaseModel, Field

EmergencyType = Literal['fire', 'medical', 'accident']
Severity = Literal['low', 'medium', 'high', 'critical']
ResourceType = Literal['ambulance', 'fire_truck']
Role = Literal['citizen', 'operator', 'admin']


class RegisterRequest(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=150)
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: str
    password: str


class EmergencyCreate(BaseModel):
    type: EmergencyType
    severity: Severity
    people_affected: int = Field(default=1, ge=1, le=10000)
    address: str = Field(min_length=3, max_length=300)


class ResourceCreate(BaseModel):
    type: ResourceType
    name: str = Field(min_length=2, max_length=100)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    role: Role
