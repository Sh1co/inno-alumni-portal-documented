from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from app.db import db
from app.utils.oa2 import get_current_user
from ..schema import schemas

router = APIRouter(tags=["Obtain Pass"], prefix="/request_pass")

@router.get("/")
def get_all_pass_requests(cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Retrieves all pass requests made by the current user, ordered by the creation date in descending order.
    
    Args:
        cur_user: The current authenticated user making the request.
    
    Returns:
        A list of pass requests made by the current user.
    """
    pass_requests = db.passrequest.find_many(where={"user_id": cur_user.id}, order={"created_at": "desc"})
    return pass_requests

@router.get("/admin", response_model=List[schemas.PassRequestOutput], status_code=status.HTTP_200_OK)
def get_all_pass_requests_by_admin(cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Retrieves all pass requests from all users, intended for admin use. The requests include user information and are ordered by creation date in descending order.
    
    Args:
        cur_user: The current authenticated user presumed to be an admin.
    
    Returns:
        A list of all pass requests including user information.
    """
    passes = db.passrequest.find_many(include={"user": True}, order={"created_at": "desc"})
    return passes

@router.patch("/", status_code=status.HTTP_200_OK)
def update_pass_request(request_id: str, to_update: schemas.UpdateRequest, cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Updates a specific pass request based on the provided request ID and update details.
    
    Args:
        request_id: The unique identifier of the pass request to be updated.
        to_update: An object containing the update details for the pass request.
        cur_user: The current authenticated user making the update request.
    
    Returns:
        The updated pass request.
    """
    update = jsonable_encoder(to_update)
    updated_request = db.passrequest.update(data=update, where={'id': request_id})
    return updated_request

@router.post("/", status_code=status.HTTP_201_CREATED)
def order_pass(pass_request: schemas.OrderPassRequest, cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Submits a new pass order request with optional guest information.
    
    Args:
        pass_request: The pass request details, including description, requested date, and optional guests.
        cur_user: The current authenticated user placing the pass order.
    
    Returns:
        A success message along with the created pass order request details.
    """
    guest_info = ""
    if pass_request.guests:
        guest_info = "*_*".join(pass_request.guests)

    requested_pass = db.passrequest.create(data={
        "user_id": cur_user.id,
        "description": pass_request.description,
        "requested_date": pass_request.requested_date.isoformat(),
        "guest_info": guest_info
    })

    return {"status": status.HTTP_201_CREATED, "detail": "Successfully created pass order", "data": requested_pass}

@router.delete("/", status_code=status.HTTP_200_OK)
def disconnect_pass_request(pass_request_id: str, cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Deletes a pass request based on the provided pass request ID.
    
    Args:
        pass_request_id: The unique identifier of the pass request to be deleted.
        cur_user: The current authenticated user attempting to delete the pass request.
    
    Returns:
        The result of the delete operation.
    """
    pass_to_delete = db.passrequest.find_first(where={
        "id": pass_request_id,
        "user_id": cur_user.id
    })
    return db.passrequest.delete(where={"id": pass_to_delete.id})
