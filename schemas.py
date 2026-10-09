from typing import Optional
from pydantic import BaseModel, EmailStr

class DepartmentBase(BaseModel):
    name: str


class DepartmentCreate(DepartmentBase):
    pass


class DepartmentResponse(DepartmentBase):
    id: int

    class Config:
        from_attributes = True


class EmployeeBase(BaseModel):
    name: str
    email: str
    phone: str
    designation: str
    joiningdate: str
    status: str = "Active"
    department_id: int


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    joiningdate: Optional[str] = None
    status: Optional[str] = None
    department_id: Optional[int] = None


class EmployeeResponse(EmployeeBase):
    id: int

    class Config:
        from_attributes = True

class LeaveRequestBase(BaseModel):
    employee_id: int
    leave_type: str
    start_date: str
    end_date: str
    reason: str

class LeaveRequestCreate(LeaveRequestBase):
    pass

class LeaveStatusUpdate(BaseModel):
    status: str  

class LeaveRequestResponse(LeaveRequestBase):
    id: int
    status: str

    class Config:
        from_attributes = True