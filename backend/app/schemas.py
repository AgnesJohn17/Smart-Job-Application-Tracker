"""API input validation and response contracts."""
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator

Status = Literal["Wishlist", "Applied", "Interview", "Offer", "Rejected"]


class Register(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class Login(Register):
    pass


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ApplicationInput(BaseModel):
    company: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1, max_length=160)
    location: str | None = Field(default=None, max_length=160)
    url: HttpUrl | None = None
    status: Status = "Wishlist"
    applied_date: date | None = None
    deadline: date | None = None
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("company", "role")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("Cannot be empty")
        return value.strip()


class ApplicationPatch(BaseModel):
    company: str | None = Field(default=None, min_length=1, max_length=120)
    role: str | None = Field(default=None, min_length=1, max_length=160)
    location: str | None = Field(default=None, max_length=160)
    url: HttpUrl | None = None
    status: Status | None = None
    applied_date: date | None = None
    deadline: date | None = None
    notes: str | None = Field(default=None, max_length=2000)

    @field_validator("company", "role")
    @classmethod
    def nonblank(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Cannot be empty")
        return value.strip() if value else value


class ApplicationOut(ApplicationInput):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    url: str | None = None


class Dashboard(BaseModel):
    total: int
    Wishlist: int
    Applied: int
    Interview: int
    Offer: int
    Rejected: int
