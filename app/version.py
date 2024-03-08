from fastapi import APIRouter
from app.api import user_api
from app.api import elective_course_api
from app.api import pass_request_api
from app.api import donation_api


router = APIRouter()

def version_one():
    """
    Version one of the API routers.

    Includes routers for user, elective course, pass request, and donation endpoints.
    """
    router.include_router(user_api.router)
    router.include_router(pass_request_api.router)
    router.include_router(elective_course_api.router)
    router.include_router(donation_api.router)


version_one()
