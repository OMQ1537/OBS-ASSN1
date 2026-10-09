from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)

    employees = relationship("Employee", back_populates="department", cascade="all, delete-orphan")


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=False)
    designation = Column(String, nullable=False)
    joiningdate = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Active")

    department_id = Column(Integer, ForeignKey("departments.id"), nullable=False)
    department = relationship("Department", back_populates="employees")

    leave_requests = relationship("LeaveRequest", back_populates="employee", cascade="all, delete-orphan")

class LeaveRequest(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    leave_type = Column(String, nullable=False)  
    start_date = Column(String, nullable=False)   
    end_date = Column(String, nullable=False)    
    reason = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Pending") 
    employee = relationship("Employee", back_populates="leave_requests")