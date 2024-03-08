from app.db import db
from app.telegram import data


def get_all_users():
    """
    Retrieve all users from the database.

    Returns:
        list: List of all users.
    """
    return db.user.find_many()


def get_user_by_alias(user_handle):
    """
    Retrieve a user by their handle from the database.

    Args:
        user_handle (str): The handle of the user to retrieve.

    Returns:
        dict: The user document.
    """
    return db.user.find_first(where={"handle": user_handle})


def get_elective_courses():
    """
    Retrieve all elective courses from the database.

    Returns:
        list: List of elective courses.
    """
    return db.course.find_many(where={"is_elective": True})


def get_groups():
    """
    Retrieve all groups from the database.

    Returns:
        list: List of groups.
    """
    return db.group.find_many()


def get_group_users(group_name):
    """
    Retrieve users belonging to a specific group from the database.

    Args:
        group_name (str): The name of the group.

    Returns:
        list: List of users belonging to the group.
    """
    group = db.group.find_first(where={"specific_group": group_name}, include={"users": True})
    if not group:
        return []
    return group.users


def get_elective_course_users(course_short_name):
    """
    Retrieve users enrolled in a specific elective course from the database.

    Args:
        course_short_name (str): The short name of the elective course.

    Returns:
        list: List of users enrolled in the elective course.
    """
    course = db.course.find_first(
        where={"short_name": course_short_name},
        include={"optional_course_users": True, "elective_users": True})
    if not course:
        return []
    if course.valid_group == 'ALL':
        users = course.optional_course_users
    else:
        users = course.elective_users
    return users
