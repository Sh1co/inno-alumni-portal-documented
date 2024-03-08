from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.encoders import jsonable_encoder
from app.db import db
from app.utils.oa2 import get_current_user
from app.utils.role_checker import admin_role
from app.schema import schemas

router = APIRouter(tags=["Elective Courses"], prefix="/elective_course")

@router.get("/", response_model=List[schemas.ElectiveCourseOutput])
def get_all_elective_courses(cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Retrieves all elective courses that the current user has not yet booked.
    
    Args:
        cur_user: The current user attempting to view the courses.
        
    Returns:
        A list of elective courses excluding those that the current user has already booked.
    """
    booked_courses = db.courserequest.find_many(where={"user_id": cur_user.id, "status": "PENDING"}, order={"created_at": "desc"})
    booked_courses_id = [c.course_id for c in booked_courses]
    courses = db.electivecourse.find_many(where={"id": {"not_in": booked_courses_id}})
    return courses

@router.get("/admin", response_model=List[schemas.ElectiveCourseOutput])
def get_all_elective_courses_by_admin(cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Retrieves all elective courses, intended for admin use.
    
    Args:
        cur_user: The current admin user.
        
    Returns:
        A list of all elective courses.
    """
    courses = db.electivecourse.find_many()
    return courses

@router.get("/booked")
def get_booked_elective_courses(cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Retrieves all elective courses that the current user has booked.
    
    Args:
        cur_user: The current user.
        
    Returns:
        A list of booked elective courses for the current user.
    """
    courses = db.courserequest.find_many(where={"user_id": cur_user.id}, include={"elective_course": True}, order={"created_at": "desc"})
    return courses

@router.get("/request")
def get_all_elective_requests(cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Retrieves all elective course requests.
    
    Args:
        cur_user: The current user, used for authentication.
        
    Returns:
        A list of all elective course requests, including course and user details.
    """
    courses = db.courserequest.find_many(include={"elective_course": True, "user": True}, order={"created_at": "desc"})
    return courses

@router.post("/", response_model=schemas.ElectiveCourseOutput, status_code=status.HTTP_201_CREATED)
def create_elective_course(course: schemas.ElectiveCourse, cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Creates a new elective course.
    
    Args:
        course: The elective course data.
        cur_user: The current user, used for authentication.
        
    Returns:
        The created elective course.
    """
    created_course = db.electivecourse.create(data={
        "course_name": course.course_name,
        "instructor_name": course.instructor_name,
        "description": course.description,
        "mode": course.mode
        })
    return created_course

@router.post("/bulk", status_code=status.HTTP_201_CREATED)
def create_bulk_elective_courses(courses: List[schemas.ElectiveCourse], cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Bulk creates elective courses.
    
    Args:
        courses: A list of elective courses to be created.
        cur_user: The current user, used for authentication.
        
    Returns:
        The number of elective courses added.
    """
    courses_to_upload = jsonable_encoder(courses)
    number_added = db.electivecourse.create_many(data=courses_to_upload, skip_duplicates=True)
    return number_added

@router.put("/", response_model=schemas.ElectiveCourseOutput, status_code=status.HTTP_200_OK)
def update_elective_course(course_id: str, course: schemas.ElectiveCourse, cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Updates an existing elective course.
    
    Args:
        course_id: The ID of the course to update.
        course: The updated course data.
        cur_user: The current user, used for authentication.
        
    Returns:
        The updated elective course.
    """
    course_to_update = jsonable_encoder(course)
    updated_course = db.electivecourse.update(data=course_to_update, where={'id': course_id})
    return updated_course

@router.delete("/remove", response_model=schemas.ElectiveCourseOutput, status_code=status.HTTP_200_OK)
def delete_elective_course(course_id: str, cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Deletes an elective course.
    
    Args:
        course_id: The ID of the course to delete.
        cur_user: The current user, used for authentication.
        
    Returns:
        The deleted elective course.
    """
    return db.electivecourse.delete(where={'id': course_id})

@router.delete("/", status_code=status.HTTP_200_OK)
def disconnect_elective_course_request(course_request_id: str, cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Deletes an elective course request.
    
    Args:
        course_request_id: The ID of the course request to delete.
        cur_user: The current user, used for authentication.
        
    Returns:
        The deletion result of the elective course request.
    """
    course_to_delete = db.courserequest.find_first(where={"id": course_request_id, "user_id": cur_user.id})
    return db.courserequest.delete(where={"id": course_to_delete.id}, include={"elective_course": True})

@router.post("/request", status_code=status.HTTP_201_CREATED)
def request_elective_course(course_id: str, cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Submits a request for an elective course.
    
    Args:
        course_id: The ID of the elective course to request.
        cur_user: The current user making the request.
        
    Raises:
        HTTPException: If the course does not exist or a request is already being processed.
        
    Returns:
        The created elective course request.
    """
    found_elective = db.electivecourse.find_unique(where={"id": course_id})
    if not found_elective:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Course with this Id doesn't exist")
    
    already_being_processed = db.courserequest.find_first(where={"user_id": cur_user.id, "course_id": course_id, "status": "PENDING"})
    if already_being_processed:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Your request is already being processed. Be patient")
    
    created_elective_request = db.courserequest.create(data={
        "user_id": cur_user.id,
        "course_id": course_id
    }, include={"elective_course": True})
    return created_elective_request

@router.patch("/", status_code=status.HTTP_200_OK)
def update_elective_request(request_id: str, to_update: schemas.UpdateRequest, cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Updates an elective course request.
    
    Args:
        request_id: The ID of the request to update.
        to_update: The update details.
        cur_user: The current user, used for authentication.
        
    Returns:
        The updated elective course request.
    """
    update = jsonable_encoder(to_update)
    updated_request = db.courserequest.update(data=update, where={'id': request_id})
    return updated_request
