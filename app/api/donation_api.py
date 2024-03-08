from typing import List
from fastapi import APIRouter, Depends, status
from app.db import db
from app.utils.oa2 import get_current_user
from ..schema import schemas

router = APIRouter(tags=["Manage Donations"], prefix="/donation")

@router.get("/", response_model=List[schemas.DonationOutput])
def get_all_donations(cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Retrieve all donations made by alumni.
    
    This endpoint retrieves all donations that have been made by alumni, sorted by the creation date in descending order.
    
    Args:
        cur_user: The current user obtained via dependency injection, which ensures that the user is logged in.
    
    Returns:
        A list of donation objects that matches the criteria of being made by alumni.
    """
    donations = db.donation.find_many(where={"type": "ALUMNI"}, order={"created_at": "desc"}, include={"user": True})
    return donations

@router.post("/", status_code=status.HTTP_201_CREATED)
def make_donation(donation: schemas.MakeDonation, cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Create a new donation.
    
    This endpoint allows a user to make a new donation, capturing the donation message and associating it with the user.
    
    Args:
        donation: The donation details received from the request body.
        cur_user: The current user making the donation, obtained via dependency injection.
    
    Returns:
        A success message along with the created donation object.
    """
    created_donation = db.donation.create(data={
        "user_id": cur_user.id,
        "message": donation.message
    })

    return {"status": status.HTTP_201_CREATED, "detail": "Donation Successfully created", "data": created_donation}

@router.get("/admin")
def get_admin_donation_message(cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Retrieve the latest admin donation message.
    
    This endpoint fetches the most recent donation message set by an admin.
    
    Args:
        cur_user: The current user (admin) obtained via dependency injection, used to validate access.
    
    Returns:
        The most recent admin donation message.
    """
    donation_message = db.donation.find_first(where={"type": "ADMIN"}, order={"created_at": "desc"})
    return donation_message

@router.post("/admin", status_code=status.HTTP_202_ACCEPTED)
def update_admin_donation_message(donation: schemas.MakeDonation, cur_user: schemas.UserOutput = Depends(get_current_user)):
    """
    Update or create an admin donation message.
    
    This endpoint allows updating an existing admin donation message or creating a new one if it doesn't exist.
    
    Args:
        donation: The new donation message to be set or updated.
        cur_user: The current admin user making the update, obtained via dependency injection.
    
    Returns:
        A success message along with the updated or created admin donation message object.
    """
    donationInfo = db.donation.find_first(where={"user_id": cur_user.id, "type": "ADMIN"})
    upsert_donation = db.donation.upsert(
        where={
            "id": donationInfo.id if donationInfo else "",
        },
        data={
            "create": {
                "user_id": cur_user.id,
                "message": donation.message,
                "type": "ADMIN"
            },
            "update": {
                "message": donation.message,
            }
        }, 
    )

    return {"status": status.HTTP_202_ACCEPTED, "detail": "Donation message successfully updated", "data": upsert_donation}
