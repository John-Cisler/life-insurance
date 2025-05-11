from pydantic import BaseModel, PositiveInt, Field, condecimal
from datetime import datetime
from enum import Enum

class PolicyType(str, Enum):
    TERM  = "TERM"
    WHOLE = "WHOLE"

class PolicyCreate(BaseModel):
    customerId: PositiveInt = Field(..., alias="customerId")
    coverage: PositiveInt
    annualPremium: float    = Field(..., alias="annualPremium")
    policyType: PolicyType = PolicyType.TERM # default policy type

class PolicyOut(BaseModel):
    id: int
    customerId: int = Field(alias="customer_id")
    coverage: int
    annualPremium: float = Field(alias="annual_premium")
    policyType: PolicyType = Field(alias="policy_type")
    status: str
    issuedAt: datetime = Field(alias="issued_at")

    # tell Pydantic v2 that we’re feeding it ORM objects
    model_config = {"from_attributes": True}


Percent = condecimal(gt=0, le=100, max_digits=5, decimal_places=2)

class BeneficiaryIn(BaseModel):
    name: str
    pctShare: Percent = Field(alias="pctShare")   # maps JSON key

    model_config = {"extra": "forbid"}            # catches typos

