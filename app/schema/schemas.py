from enum import Enum
import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr

####### USER SCHEMAS
#######################################

class InternalUser(BaseModel):
    """
    Schema for internal user details, including optional personal and professional information.
    """
    id: str
    email: EmailStr
    role: str
    name: Optional[str]
    contact_email: EmailStr
    phone_number: Optional[str]
    graduated_track: Optional[str]
    graduation_year: Optional[str]
    about_you: Optional[str]
    city: Optional[str]
    company: Optional[str]
    position: Optional[str]
    telegram_handle: Optional[str]
    telegram_id: Optional[int]
    is_volunteer: Optional[bool]

class LogInUser(BaseModel):
    """
    Schema for user login credentials.
    """
    email: EmailStr
    password: str

class UserWithPassword(BaseModel):
    """
    Schema for user details including the hashed password.
    """
    id: str
    email: EmailStr
    password: str

class CreateAdminUser(BaseModel):
    """
    Schema for creating a new admin user with essential credentials.
    """
    name: str
    email: EmailStr
    password: str

class SignUpUser(BaseModel):
    """
    Schema for user sign-up, requiring confirmation of password.
    """
    name: str
    email: EmailStr
    password: str
    confirm_password: str

class UpdateUser(BaseModel):
    """
    Schema for updating user information with all fields optional.
    """
    name: Optional[str]
    phone_number: Optional[str]
    contact_email: EmailStr
    graduation_year: Optional[str]
    graduated_track: Optional[str]
    about_you: Optional[str]
    city: Optional[str]
    company: Optional[str]
    position: Optional[str]
    telegram_handle: Optional[str]
    telegram_id: Optional[int]
    is_volunteer: Optional[bool]

    class Config():
        orm_mode = True

class UserOutput(BaseModel):
    """
    Output schema for displaying user information with optional fields for personal and professional details.
    """
    name: Optional[str]
    email: EmailStr
    contact_email: Optional[EmailStr]
    phone_number: Optional[str]
    graduation_year: Optional[str]
    telegram_id: Optional[int]
    telegram_handle: Optional[str]
    position: Optional[str]
    company: Optional[str]
    city: Optional[str]
    about_you: Optional[str]
    graduated_track: Optional[str]
    is_volunteer: Optional[bool]

    class Config():
        orm_mode = True

class ConfirmationCode(BaseModel):
    """
    Schema for confirmation code verification process.
    """
    code: int

class UpdateUserPassword(BaseModel):
    """
    Schema for updating a user's password, requiring current and new passwords.
    """
    current_password: str
    new_password: str

####### ORDER PASS SCHEMAS
#######################################

class OrderPassRequest(BaseModel):
    """
    Schema for requesting a pass, including optional fields for guests and description.
    """
    requested_date: Optional[datetime.date]
    guests: Optional[List[str]] = None
    description: Optional[str] = None

class PassRequestOutput(BaseModel):
    """
    Represents the output schema for a pass request, including information about the request, user details, and administrative feedback.
    """
    id: str
    guest_info: str
    description: Optional[str]
    feedback: Optional[str]
    type: str
    requested_date: str
    status: str
    user_id: str
    user: Optional[UserOutput] = None
    created_at: datetime.datetime

####### ELECTIVE COURSE SCHEMAS
#######################################

class ElectiveCourse(BaseModel):
    """
    Schema for creating or representing an elective course, including its name, instructor, and mode of delivery.
    """
    course_name: str
    instructor_name: Optional[str] 
    description: Optional[str]
    mode: Optional[str]

class ElectiveCourseOutput(BaseModel):
    """
    Output schema for elective courses, extending ElectiveCourse with the addition of an ID field.
    """
    id: str
    course_name: str
    instructor_name: Optional[str]
    description: Optional[str]
    mode: Optional[str]

class UpdateRequest(BaseModel):
    """
    Schema for updating a request, typically used for providing feedback and updating the status of a request.
    """
    feedback: str
    status: str

####### DONATION SCHEMAS
#######################################

class MakeDonation(BaseModel):
    """
    Schema for making a donation, encapsulating the message attached to the donation.
    """
    message: str

class DonationOutput(BaseModel):
    """
    Output schema for a donation, including details about the user making the donation, the message, and the timestamp.
    """
    id: str
    user: UserOutput
    message: str
    created_at: datetime.datetime

class ShowUser(BaseModel):
    """
    Simplified user display schema, primarily for showing user information in various contexts.
    """
    full_name: str
    email: str

    class Config:
        orm_mode = True

class User(BaseModel):
    """
    Basic user schema for authentication purposes, including email and password.
    """
    email: EmailStr
    password: str

class UserForgotPassword(BaseModel):
    """
    Schema for users requesting a password reset, identifying them by email.
    """
    email: EmailStr

class UserVerifyAccount(BaseModel):
    """
    Schema for account verification requests, identifying users by email.
    """
    email: EmailStr

class UserUpdatePassword(BaseModel):
    """
    Schema for updating a user's password, requiring email and new password.
    """
    email: EmailStr
    password: str

class VerificationCode(BaseModel):
    """
    Schema for verification processes, including the verification code and the associated email.
    """
    code: str
    email: EmailStr

class UserOut(BaseModel):
    """
    Comprehensive user output schema, including personal information and contact details.
    """
    full_name: str
    email: EmailStr
    phone_number: Optional[str]
    address: Optional[str]
    avatar: Optional[str]
    birth_date: Optional[datetime.date]
    country: Optional[str]

    class Config():
        orm_mode = True


class UserEdit(BaseModel):
    """
    Schema for editing user information, specifically for updating address and avatar.
    """
    address: Optional[str]
    avatar: Optional[str]

class SlotTypeEnum(str, Enum):
    """
    Enumeration of possible types for a class slot, including LAB for laboratories, TUT for tutorials, and LEC for lectures.
    """
    LAB = "LAB"
    TUT = "TUT"
    LEC = "LEC"

class Slot(BaseModel):
    """
    Represents a class slot, including optional and required information about the class such as the instructor, room number, timing, course name, type of class, course ID, and group ID.
    """
    instructor_name: Optional[str]
    room_number: Optional[str]
    start_time: datetime.datetime
    end_time: datetime.datetime
    course_name: Optional[str]
    type: Optional[SlotTypeEnum]
    course_id: str
    group_id: str

    class Config:
        orm_mode = True

class SlotUpdate(BaseModel):
    """
    Schema for updating existing slot information. All fields are optional to allow partial updates.
    """
    instructor_name: Optional[str]
    room_number: Optional[str]
    start_time: Optional[datetime.datetime]
    end_time: Optional[datetime.datetime]
    course_name: Optional[str]
    type: Optional[SlotTypeEnum]
    course_id: Optional[str]
    group_id: Optional[str]

    class Config:
        orm_mode = True

class SlotRange(BaseModel):
    """
    Defines a date range with a start and end date, used for querying slots within a specific timeframe.
    """
    start_date: datetime.date
    end_date: datetime.date

    class Config:
        orm_mode = True