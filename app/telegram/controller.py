from datetime import datetime
from app.telegram import data
from app.db import db

# USERS RELATED


def get_user(user_id):
    """
    Retrieve a user by their Telegram ID from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        dict: The user document.
    """
    user = db.user.find_unique(where={'telegram_id': user_id})
    return user


def get_full_user(user_id):
    """
    Retrieve a user with additional details by their Telegram ID from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        dict: The user document with pass request and course request details.
    """
    user = db.user.find_unique(
        where={'telegram_id': user_id},
        include={'pass_request': True, 'course_request': True}
    )
    return user


def register_user(user_id, email="", fullname="", handle=""):
    """
    Register a new user in the database.

    Args:
        user_id (int): The Telegram ID of the user.
        email (str): Email address of the user (optional).
        fullname (str): Full name of the user (optional).
        handle (str): Telegram handle of the user (optional).

    Returns:
        dict: The newly created user document.
    """
    return db.user.create(data={
        "telegram_id": user_id,
        "telegram_handle": handle,
        "email": email,
        "name": fullname,
    })


def update_user(user_id, email="", fullname="", handle=""):
    """
    Update user information in the database.

    Args:
        user_id (int): The Telegram ID of the user.
        email (str): Email address of the user (optional).
        fullname (str): Full name of the user (optional).
        handle (str): Telegram handle of the user (optional).

    Returns:
        dict: The updated user document.
    """
    return db.user.update(data={
        "telegram_handle": handle,
        "email": email,
        "name": fullname,
    }, where={
        "telegram_id": user_id
    })


def update_user_alias(user_id, handle):
    """
    Update user's Telegram handle in the database.

    Args:
        user_id (int): The Telegram ID of the user.
        handle (str): New Telegram handle of the user.

    Returns:
        dict: The updated user document.
    """
    return db.user.update(where={'telegram_id': user_id}, data={"telegram_handle": handle})


def get_user_with_settings(user_id):
    """
    Retrieve a user's settings from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        dict: The user document including settings.
    """
    user = db.user.find_unique(
        where={'telegram_id': user_id})
    return user


def get_user_with_course(user_id):
    """
    Retrieve a user with course details from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        dict: The user document including course request details.
    """
    user = db.user.find_unique(
        where={'telegram_id': user_id}, include={"course_request": True})
    return user


# GENERAL REQUESTS

# not done yet
def print_request(request):
    """
    Format a request for printing.

    Args:
        request: Request object.

    Returns:
        str: Formatted request information.
    """
    date = datetime.strptime(
        f"{request.created_at}", "%Y-%m-%d %H:%M:%S.%f%z")
    result = ""
    if request.type == 'ELECTIVE':
        result += f"ELECTIVE request is {request.status} for {request.course.description} - {date.strftime('%d/%m/%Y')}\n"
    else:
        result += f"{request.type} request is {request.status} - {date.strftime('%d/%m/%Y')}\n"
    return result

# not done yet
def print_request_result(request):
    """
    Format a request result for printing.

    Args:
        request: Request object.

    Returns:
        str: Formatted request result information.
    """
    date = datetime.strptime(
        f"{request.created_at}", "%Y-%m-%d %H:%M:%S.%f%z")
    result = ""
    if request.type == 'ELECTIVE':
        result += f"ELECTIVE request has been {request.status} for {request.course.description} - {date.strftime('%d/%m/%Y')}\n"
    else:
        result += f"PASS request has been {request.status} - {date.strftime('%d/%m/%Y')}\n"
    return result


def get_pass_request(user_id):
    """
    Retrieve pass requests for a user from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        list: List of pass requests.
    """
    requests = db.passrequest.find_many(
        where={'user_id': user_id},
        order={'created_at': 'desc'}
    )
    return requests


def get_course_request(user_id):
    """
    Retrieve course requests for a user from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        list: List of course requests.
    """
    requests = db.courserequest.find_many(
        where={'user_id': user_id},
        include={'elective_course': True},
        order={'created_at': 'desc'}
    )
    return requests


def get_pass_request_by_id(request_id):
    """
    Retrieve a pass request by its ID from the database.

    Args:
        request_id (int): The ID of the pass request.

    Returns:
        dict: The pass request document.
    """
    return db.passrequest.find_unique(where={"id": request_id})


def get_course_request_by_id(request_id):
    """
    Retrieve a course request by its ID from the database.

    Args:
        request_id (int): The ID of the course request.

    Returns:
        dict: The course request document.
    """
    return db.courserequest.find_unique(where={"id": request_id})

def clear_pass_request_history(user_id):
    """
    Clear the history of pass requests for a user from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        int: Number of pass requests deleted.
    """
    requests = db.passrequest.delete_many(
        where={'user_id': user_id,
               'status': {
                   "in": ["APPROVED", "REJECTED"]
               }
        })
    return requests

def clear_course_request_history(user_id):
    """
    Clear the history of course requests for a user from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        int: Number of course requests deleted.
    """
    requests = db.courserequest.delete_many(
        where={'user_id': user_id,
               'status': {
                   "in": ["APPROVED", "REJECTED"]
               }
        })
    return requests

# '2023-03-24 08:11:10.059000+00:00' does not match format '%d/%m'

# ELECTIVE RELATED

# not done yet
def update_user_courses(user_id, course_id):
    """
    Update the courses of a user in the database.

    Args:
        user_id (int): The Telegram ID of the user.
        course_id (int): The ID of the course to update.

    Returns:
        dict: The updated user document.
    """
    return db.user.update(
        data={
            "courses": {
                "connect": {
                    "telegram_id": course_id
                }
            }
        },
        where={"telegram_id": user_id}
    )

def get_pending_elective_request(user_id):
    """
    Retrieve pending elective requests for a user from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        list: List of pending elective requests.
    """
    requests = db.courserequest.find_many(
        where={'user_id': user_id, "status": "PENDING"},
        include={'elective_course': True}
    )
    return requests

def get_pending_pass_requests(user_id):
    """
    Retrieve pending pass requests for a user from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        list: List of pending pass requests.
    """
    return db.passrequest.find_many(
        where={'user_id': user_id, "status": "PENDING"},
        include={'user': True}
    )

def clear_pending_elective_request(user_id):
    """
    Clear pending elective requests for a user from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        int: Number of deleted pending elective requests.
    """
    deleted = db.courserequest.delete_many(
        where={'user_id': user_id, "status": "PENDING"},
    )
    return deleted


def get_elective_courses():
    """
    Retrieve all elective courses from the database.

    Returns:
        list: List of elective courses.
    """
    elective_courses = db.electivecourse.find_many()
    return elective_courses

def get_elective_by_name(elective_name):
    """
    Retrieve an elective course by its name from the database.

    Args:
        elective_name (str): The name of the elective course.

    Returns:
        dict: The elective course document.
    """
    return db.electivecourse.find_first(where={"name": elective_name})

def request_elective(elective, user_id):
    """
    Request an elective course for a user in the database.

    Args:
        elective (str): The name of the elective course.
        user_id (int): The Telegram ID of the user.

    Returns:
        dict: The created course request document.
    """
    course = db.electivecourse.find_first(where={"name": elective})
    if not course:
        return []

    return db.courserequest.create(data={
        "user_id": user_id,
        "course_id": course.id
    })


def clear_elective_courses(user_id, ids_to_disconnect):
    """
    Clear elective courses for a user in the database.

    Args:
        user_id (int): The Telegram ID of the user.
        ids_to_disconnect (list): List of course IDs to disconnect.

    Returns:
        dict: The updated user document.
    """
    return db.user.update(
        data={
            "courses": {
                "disconnect": ids_to_disconnect
            }
        }, where={"telegram_id": user_id})


def get_electives(user_id):
    """
    Retrieve elective courses for a user from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        list: List of elective courses.
    """
    user = db.user.find_unique(
        where={"telegram_id": user_id},
        include={"course_request": True}
    )
    return user.elective_courses

# PASS RELATED

def request_pass(requested_date, description, user_id):
    """
    Create a pass request for a user in the database.

    Args:
        requested_date (str): The requested date for the pass.
        description (str): Description of the pass request.
        user_id (int): The Telegram ID of the user.

    Returns:
        dict: The created pass request document.
    """
    user = db.user.find_unique(where={"telegram_id": user_id})
    return db.passrequest.create(data={
        "user_id": user.id,
        "description": description,
        "requested_date": requested_date
    })


def approve_pass_request(request_id, feedback):
    """
    Approve a pass request in the database.

    Args:
        request_id (int): The ID of the pass request.
        feedback (str): Feedback for the approval.

    Returns:
        dict: The updated pass request document.
    """
    try:
        request = db.passrequest.update(
            data={"status": "APPROVED", "feedback": feedback},
            where={"id": request_id})
    except:
        print(
            f"Error: Probably request with id - {request_id} does not exist anymore")
    return request

def approve_course_request(request_id, feedback):
    """
    Approve a course request in the database.

    Args:
        request_id (int): The ID of the course request.
        feedback (str): Feedback for the approval.

    Returns:
        dict: The updated course request document.
    """
    try:
        request = db.courserequest.update(
            data={"status": "APPROVED", "feedback": feedback},
            where={"id": request_id}, include={"elective_course": True})
    except:
        print(
            f"Error: Probably request with id - {request_id} does not exist anymore")
    return request

def reject_pass_request(request_id, feedback):
    """
    Reject a pass request in the database.

    Args:
        request_id (int): The ID of the pass request.
        feedback (str): Feedback for the rejection.

    Returns:
        dict: The updated pass request document.
    """
    try:
        request = db.passrequest.update(
            data={"status": "REJECTED", "feedback": feedback},
            where={"id": request_id})
    except:
        print(
            f"Error: Probably request with id - {request_id} does not exist anymore")
    return request

def reject_course_request(request_id, feedback):
    """
    Reject a course request in the database.

    Args:
        request_id (int): The ID of the course request.
        feedback (str): Feedback for the rejection.

    Returns:
        dict: The updated course request document.
    """
    try:
        request = db.courserequest.update(
            data={"status": "REJECTED", "feedback": feedback},
            where={"id": request_id},
            include={'elective_course': True})
    except:
        print(
            f"Error: Probably request with id - {request_id} does not exist anymore")
    return request

def get_pending_pass_request(user_id):
    """
    Retrieve pending pass requests for a user from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        list: List of pending pass requests.
    """
    user = db.user.find_unique(where={"telegram_id": user_id})
    requests = db.passrequest.find_many(
        where={'user_id': user.id, "status": "PENDING"}
    )
    return requests


def delete_pending_pass_request(user_id):
    """
    Delete pending pass requests for a user from the database.

    Args:
        user_id (int): The Telegram ID of the user.

    Returns:
        int: Number of deleted pending pass requests.
    """
    user = db.user.find_unique(where={"telegram_id": user_id})
    deleted = db.passrequest.delete_many(
        where={'user_id': user.id, "status": "PENDING"},
    )
    return deleted



# \copy public."Slot" (telegram_id, instructor_name, room_number, start_time, end_time, course_id, type, group_id, specific_group, course_name) FROM '/Users/danielatonge/Downloads/week3_schedule/slot.csv' DELIMITER ',' CSV HEADER QUOTE '"' ESCAPE '''';


###############
# Helper methods
###############
