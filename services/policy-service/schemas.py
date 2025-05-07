from pydantic import BaseModel, PositiveInt, Field
from datetime import datetime


class PolicyCreate(BaseModel):
    customerId: PositiveInt = Field(..., alias="customerId")
    coverage: PositiveInt
    annualPremium: float    = Field(..., alias="annualPremium")

class PolicyOut(BaseModel):
    id: int
    customerId: int = Field(alias="customer_id")
    coverage: int
    annualPremium: float = Field(alias="annual_premium")
    status: str
    issuedAt: datetime = Field(alias="issued_at")

    # tell Pydantic v2 that we’re feeding it ORM objects
    model_config = {"from_attributes": True}