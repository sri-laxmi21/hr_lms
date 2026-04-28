from pydantic import BaseModel
from typing import List


class LeaveBalanceResponse(BaseModel):
    leave_type_id: int
    leave_type: str

    allocated: float
    used: float
    pending: float
    balance: float


class LeaveBalanceListResponse(BaseModel):
    user_id: int          # ✅ identifies WHICH user's balance this is
    year: int
    balances: List[LeaveBalanceResponse]
