
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, Response, status

from app.utils.oa2 import get_current_user
from ..schema import schemas

# from ..database.configuration import get_db
from ..utils import hash, token, email_handler
from app.db import db


router = APIRouter(tags=["User Authentication"], prefix="/user")


@router.post("/login")
def login_alumni(
    user_cred: OAuth2PasswordRequestForm = Depends()
):
    """
    Authenticates an alumni user and returns an access token.

    Args:
        user_cred: An instance of OAuth2PasswordRequestForm containing the user's email (username) and password.

    Raises:
        HTTPException: 404 error if the user cannot be found or the password is incorrect.

    Returns:
        A JSON object containing the bearer token and its type.
    """
    user = db.user.find_first(where={"email": user_cred.username})
    print(user, user_cred)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials"
        )
    if not hash.verify_password(user_cred.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Incorrect password"
        )

    access_token = token.create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register",status_code=status.HTTP_201_CREATED)
def create_alumni_account(user_to_create: schemas.SignUpUser):
    """
    Registers a new alumni account with the provided user details.

    Args:
        user_to_create: An instance of SignUpUser schema containing the user's signup information.

    Raises:
        HTTPException: 400 error if the password confirmation fails or the user already exists.

    Returns:
        A success message indicating the user has been successfully registered.
    """
    password = user_to_create.password
    confirm_password = user_to_create.confirm_password
    if password != confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password doesn't match Confirm password")

    new_user_email = user_to_create.email
    found_user = db.user.find_first(where={"email": new_user_email})

    # If user is found return with error
    if found_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='User with email already exists')

    encrypted_password = hash.hash_password(password)
    db.user.create(data={
        "name": user_to_create.name,
        "email": new_user_email, 
        "password": encrypted_password
    })
    return {
            "status": status.HTTP_201_CREATED,
            "message": 'Successfully registered user'
        }

@router.post("/register-admin",response_model=schemas.UserOutput, status_code=status.HTTP_201_CREATED)
def create_admin_account(admin: schemas.CreateAdminUser):
    """
    Registers a new admin account with the provided admin details.

    Args:
        admin: An instance of CreateAdminUser schema containing the admin's registration information.

    Raises:
        HTTPException: 400 error if an admin with the provided email already exists.

    Returns:
        The newly created admin user details.
    """
    found_user = db.user.find_first(where={"email": admin.email, "role": "ADMIN"})

    # If user is found return with error
    if found_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Admin User with email already exists')

    encrypted_password = hash.hash_password(admin.password)
    return db.user.create(data={
        "name": admin.name,
        "email": admin.email, 
        "password": encrypted_password,
        "role": "ADMIN"
    })


@router.post("/update", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOutput)
def update_alumni_account(up_user: schemas.UpdateUser, 
                        cur_user:schemas.InternalUser = Depends(get_current_user)):
    """
    Updates an existing alumni account with the provided new details.

    Args:
        up_user: An instance of UpdateUser schema containing the updated user information.
        cur_user: The current user session, determined through JWT token authentication.

    Returns:
        The updated user details.
    """
    updated_user = db.user.update(where={"id": cur_user.id}, 
    data={
        "name": up_user.name if up_user.name else cur_user.name,
        "phone_number": up_user.phone_number if up_user.phone_number else cur_user.phone_number,
        "contact_email": up_user.contact_email if up_user.contact_email else cur_user.contact_email,
        "graduation_year": up_user.graduation_year if up_user.graduation_year else cur_user.graduation_year,
        "graduated_track": up_user.graduated_track if up_user.graduated_track else cur_user.graduated_track,
        "about_you": up_user.about_you if up_user.about_you else cur_user.about_you,
        "city": up_user.city if up_user.city else cur_user.city,
        "company": up_user.company if up_user.company else cur_user.company,
        "position": up_user.position if up_user.position else cur_user.position,
        "telegram_handle": up_user.telegram_handle if up_user.telegram_handle else cur_user.telegram_handle,
        "telegram_id": up_user.telegram_id if up_user.telegram_id else cur_user.telegram_id,
        "is_volunteer": up_user.is_volunteer if up_user.is_volunteer else cur_user.is_volunteer
        })
    return updated_user

@router.post("/update-password", status_code=status.HTTP_202_ACCEPTED)
def update_password(
    pass_info: schemas.UpdateUserPassword,
    cur_user:schemas.UserWithPassword = Depends(get_current_user)
):
    """
    Updates the password of the current logged-in user.
    
    Args:
        pass_info: Schema containing the current and new password of the user.
        cur_user: The current logged-in user whose password is to be updated.
        
    Raises:
        HTTPException: If the current password provided is incorrect.
        
    Returns:
        A response indicating the successful password update.
    """
    if not hash.verify_password(pass_info.current_password, cur_user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Currently entered password is wrong")
    
    encrypted_new_password = hash.hash_password(pass_info.new_password)
    db.user.update(data={
        "password": encrypted_new_password
    }, where={
        "id": cur_user.id
    })
    return {
            "status": status.HTTP_202_ACCEPTED,
            "message": 'Successfully updated password'
        }

@router.get("/", response_model=schemas.UserOutput, status_code=status.HTTP_200_OK)
def get_current_alumni(cur_user:schemas.UserOutput = Depends(get_current_user)):
    """
    Retrieves the details of the current logged-in alumni user.
    
    Args:
        cur_user: The current logged-in user obtained from JWT token.
        
    Returns:
        The current user's details.
    """
    return cur_user


@router.get("/all", status_code=status.HTTP_200_OK)
def get_all_registered_alumni(cur_user:schemas.UserOutput = Depends(get_current_user)):
    users = db.user.find_many(include={"course_request": True, "pass_request": True, "donation": True}, order={
        "created_at": "desc"
    })
    """
    Retrieves a list of all registered alumni users along with their statistics.
    
    Args:
        cur_user: The current logged-in user, used to authenticate the request.
        
    Returns:
        A list of all users with their details and statistics.
    """
    users_with_stats = list(map(lambda u: {
        "id": u.id, "name": u.name, "email": u.email, "contact_email": u.contact_email,
        "phone_number": u.phone_number, "role": u.role, "graduation_year": u.graduation_year, "graduated_track": u.graduated_track,
        "about_you": u.about_you, "city": u.city, "company": u.company, "position": u.position, 
        "is_volunteer": u.is_volunteer, "created_at": u.created_at, "telegram_handle": u.telegram_handle,
        "course_request": len(u.course_request), "pass_request": len(u.pass_request), "donation": len(u.donation)
    }, users))
    return users_with_stats


@router.post("/forgot-password")
def forgot_password(
    university_email: str,
    background_tasks: BackgroundTasks,
):
    """
    Initiates the password recovery process by sending a reset password email.
    
    Args:
        university_email: The email of the user who has forgotten their password.
        background_tasks: BackgroundTasks object to handle email sending asynchronously.
        
    Raises:
        HTTPException: If no user is found with the provided email.
        
    Returns:
        A successful response indicating the email has been sent.
    """
    # user.forgot_password(user_email.email, background_tasks,  db)
    user = db.user.find_first(where={"email": university_email})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    
    email_handler.send_email(
        background_tasks, 
        'Forgotten Password: Reset your password', 
        university_email, {'title': 'Welcome'}, 
        "forgot_password.html")
    # background_tasks.add_task(reset_can_update_password, user, PASSWORD_RESET_INTERVAL, db)
    
    return Response(status_code=status.HTTP_200_OK)


@router.post("/forgot-update-password")
def update_password(
    user_info,
):
    """
    Endpoint to update the password as part of the forgot password process.
    
    Args:
        user_info: Information required to update the password.
        
    Returns:
        A successful response indicating the password has been updated.
    """
    # user.hash_update_password(user_info, db)
    return Response(status_code=status.HTTP_200_OK)





@router.post("/verify-account")
def verify_account(
    university_email: str,
    background_tasks: BackgroundTasks
):
    """
    Sends an account verification email to the user.
    
    Args:
        university_email: The email address of the user to verify.
        background_tasks: BackgroundTasks object for asynchronous email sending.
        
    Raises:
        HTTPException: If no user is found with the provided email or the user is already verified.
        
    Returns:
        A successful response indicating the verification email has been sent.
    """
    # user.verify_user_account(user_email.email, background_tasks,  db)
    user = db.user.find_first(where={"email": university_email})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="User already verified")

    verification_code = token.generate_user_verification_code()
    db.user.update(where={"id": user.id}, data={"verification_code": verification_code})
    print(verification_code)

    email_handler.send_email(background_tasks, "Account Verification: Let's make sure it is you", university_email, {'verification_code': verification_code}, "account_verification.html")
    # background_tasks.add_task(verification_expired, user, VERIFICATION_EXPIRATION_INTERVAL, db)
    
    return Response(status_code=status.HTTP_200_OK)


@router.post("/confirm_verification")
def confirm_verification(
    verify:schemas.VerificationCode,
):
    """
    Confirms the account verification of a user using a verification code.
    
    Args:
        verify: Schema containing the verification code and the user's email.
        
    Raises:
        HTTPException: If the user is not found, already verified, verification code expired, or incorrect code is provided.
        
    Returns:
        A successful response indicating the account has been verified.
    """
    # user.confirm_verification(verify.code, verify.email, db)
    user = db.user.find_first(where={"email": verify.email})

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="User not found")
    if user.is_verified:
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="User already verified")
    if user.verification_code == "":
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Verification code expired")
    if user.verification_code != verify.code:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Incorrect code")
    
    db.user.update(where={"id":user.id}, data={"is_verified": True})
    return Response(status_code=status.HTTP_200_OK)


from fastapi_sso.sso.generic import create_provider
from typing import Any, Callable, Dict, List, Optional, Type, Union
discovery = {
    "authorization_endpoint": 'https://sso.university.innopolis.ru/adfs/oauth2/authorize',
    "token_endpoint": "http://127.0.0.1:9001/api/v1/user/token_sso",
    "userinfo_endpoint": "http://127.0.0.1:9001/api/v1/user/user_sso",
}
# https://moodle.innopolis.university/auth/oauth2/login.php?id=1&wantsurl=%2F&sesskey=bxqcQ7BJwf
# https://sso.university.innopolis.ru/adfs/oauth2/authorize/?client_id=c393d763-6d21-4f25-9e64-857b6822336c&
# response_type=code&redirect_uri=https%3A%2F%2Fmoodle.innopolis.university%2Fadmin%2Foauth2callback.php&
# state=%2Fauth%2Foauth2%2Flogin.php%3Fwantsurl%3Dhttps%253A%252F%252F

# moodle.innopolis.university%252F%26sesskey%3DEfWRDuEBqD%26id%3D1&scope=openid%20profile%20email%20allatclaims&
# response_mode=form_post
SSOProvider = create_provider(name="oidc", discovery_document=discovery)
sso = SSOProvider(
    client_id="c393d763-6d21-4f25-9e64-857b6822336c",
    client_secret="secret",
    redirect_uri="http://127.0.0.1:9001/api/v1/user/callback",
    allow_insecure_http=True,
    scope=["openid"],
    )

@router.get("/login_sso")
async def login_with_sso():
    """
    Initiates the SSO login process by redirecting the user to the SSO provider's login page.

    Returns:
        A redirection to the SSO login page to start the authentication process.
    """
    print("login_sso")
    print(sso)
    return await sso.get_login_redirect()

@router.get("/token_sso")
def token_callback_with_sso():
    """
    SSO token callback endpoint to receive the authentication token.

    Note: This function is a placeholder and should be implemented to handle the token received from the SSO provider.
    """
    print("token_sso")
    pass

@router.get("/user_sso")
def user_callback_with_sso():
    """
    SSO user callback endpoint to receive user information after successful authentication.

    Note: This function is a placeholder and should be implemented to handle user information received from the SSO provider.
    """
    print("user_sso")
    pass

@router.get("/callback")
async def authentication_callback_with_sso(request: Request):
    """
    Processes the authentication callback from the SSO provider.

    Args:
        request: The incoming request object from the SSO provider containing user authentication details.

    Note: This function demonstrates processing the callback and should be customized to handle the authentication logic.
    """
    print("callback", request)
    user = await sso.verify_and_process(request)
    print(user)
    pass