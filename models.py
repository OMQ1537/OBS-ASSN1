from pydantic import BaseModel
from typing import Optional

class DepartmentBase(BaseModel):
    name: str

class DepartmentCreate(DepartmentBase):
    pass

class Department(DepartmentBase):
    id: int

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

class Employee(EmployeeBase):
    id: int