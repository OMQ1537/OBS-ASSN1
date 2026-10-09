from fastapi import FastAPI, HTTPException
from models import Department, DepartmentCreate, Employee, EmployeeCreate
from typing import Optional
from database import Base, engine, get_db
import database_models
from fastapi import Depends, FastAPI, HTTPException, status
import schemas
from sqlalchemy.orm import Session
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/departments", response_model=schemas.DepartmentResponse, status_code=status.HTTP_201_CREATED)
def create_department(dept: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    db_dept = db.query(database_models.Department).filter(database_models.Department.name == dept.name).first()
    if db_dept:
        raise HTTPException(status_code=400, detail="Department already exists")

    new_dept = database_models.Department(name=dept.name)
    db.add(new_dept)
    db.commit()
    db.refresh(new_dept)
    return new_dept


@app.get("/departments", response_model=list[schemas.DepartmentResponse])
def get_all_departments(db: Session = Depends(get_db)):
    return db.query(database_models.Department).all()


@app.get("/departments/{dept_id}", response_model=schemas.DepartmentResponse)
def get_department_by_id(dept_id: int, db: Session = Depends(get_db)):
    dept = db.query(database_models.Department).filter(database_models.Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


@app.put("/departments/{dept_id}", response_model=schemas.DepartmentResponse)
def update_department(dept_id: int, updated_dept: schemas.DepartmentCreate, db: Session = Depends(get_db)):
    dept = db.query(database_models.Department).filter(database_models.Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    dept.name = updated_dept.name
    db.commit()
    db.refresh(dept)
    return dept


@app.delete("/departments/{dept_id}")
def delete_department(dept_id: int, db: Session = Depends(get_db)):
    dept = db.query(database_models.Department).filter(database_models.Department.id == dept_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    db.delete(dept)
    db.commit()
    return {"message": "Department deleted successfully"}


@app.post("/employees", response_model=schemas.EmployeeResponse, status_code=status.HTTP_201_CREATED)
def create_employee(emp: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    existing_email = db.query(database_models.Employee).filter(database_models.Employee.email == emp.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    dept = db.query(database_models.Department).filter(database_models.Department.id == emp.department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department ID does not exist")

    new_emp = database_models.Employee(**emp.model_dump())
    db.add(new_emp)
    db.commit()
    db.refresh(new_emp)
    return new_emp


@app.get("/employees", response_model=list[schemas.EmployeeResponse])
def get_employees(
    db: Session = Depends(get_db),
    department_id: Optional[int] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
):
    query = db.query(database_models.Employee)
    if department_id:
        query = query.filter(database_models.Employee.department_id == department_id)

    if status:
        query = query.filter(database_models.Employee.status.ilike(f"%{status}%"))

    if search:
        query = query.filter(
            (database_models.Employee.name.ilike(f"%{search}%")) |
            (database_models.Employee.email.ilike(f"%{search}%"))
        )

    employees = query.offset(skip).limit(limit).all()
    return employees


@app.get("/employees/{emp_id}", response_model=schemas.EmployeeResponse)
def get_employee_by_id(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(database_models.Employee).filter(database_models.Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp


@app.put("/employees/{emp_id}", response_model=schemas.EmployeeResponse)
def update_employee(emp_id: int, updated_emp: schemas.EmployeeUpdate, db: Session = Depends(get_db)):
    emp = db.query(database_models.Employee).filter(database_models.Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = updated_emp.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(emp, key, value)

    db.commit()
    db.refresh(emp)
    return emp


@app.delete("/employees/{emp_id}")
def delete_employee(emp_id: int, db: Session = Depends(get_db)):
    emp = db.query(database_models.Employee).filter(database_models.Employee.id == emp_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(emp)
    db.commit()
    return {"message": "Employee deleted successfully"}

@app.post("/leave-requests", response_model=schemas.LeaveRequestResponse, status_code=status.HTTP_201_CREATED)
def create_leave_request(leave: schemas.LeaveRequestCreate, db: Session = Depends(get_db)):
    emp = db.query(database_models.Employee).filter(database_models.Employee.id == leave.employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    try:
        start = datetime.strptime(leave.start_date, "%d-%m-%Y")
        end = datetime.strptime(leave.end_date, "%d-%m-%Y")
        if end < start:
            raise HTTPException(status_code=400, detail="end_date cannot be earlier than start_date")
    except ValueError:
        raise HTTPException(status_code=400, detail="Dates must be in DD-MM-YYYY format")

    new_leave = database_models.LeaveRequest(**leave.model_dump(), status="Pending")
    db.add(new_leave)
    db.commit()
    db.refresh(new_leave)
    return new_leave


@app.get("/leave-requests", response_model=list[schemas.LeaveRequestResponse])
def get_leave_requests(
    db: Session = Depends(get_db),
    employee_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
):
    query = db.query(database_models.LeaveRequest)

    if employee_id:
        query = query.filter(database_models.LeaveRequest.employee_id == employee_id)
    if status_filter:
        query = query.filter(database_models.LeaveRequest.status.ilike(f"%{status_filter}%"))

    return query.offset(skip).limit(limit).all()


@app.get("/leave-requests/{leave_id}", response_model=schemas.LeaveRequestResponse)
def get_leave_request_by_id(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(database_models.LeaveRequest).filter(database_models.LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")
    return leave


@app.patch("/leave-requests/{leave_id}/status", response_model=schemas.LeaveRequestResponse)
def update_leave_status(leave_id: int, status_update: schemas.LeaveStatusUpdate, db: Session = Depends(get_db)):
    leave = db.query(database_models.LeaveRequest).filter(database_models.LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    allowed_statuses = ["Approved", "Rejected", "Pending"]
    if status_update.status.capitalize() not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {allowed_statuses}")

    leave.status = status_update.status.capitalize()
    db.commit()
    db.refresh(leave)
    return leave


@app.delete("/leave-requests/{leave_id}")
def delete_leave_request(leave_id: int, db: Session = Depends(get_db)):
    leave = db.query(database_models.LeaveRequest).filter(database_models.LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(status_code=404, detail="Leave request not found")

    db.delete(leave)
    db.commit()
    return {"message": "Leave request deleted successfully"}