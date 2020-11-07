"""
user feature implementation as specified by the specification

Feature implementation was written by Christian Ilagan, Richard Quisumbing and
Tam Do.

2020 T3 COMP1531 Major Project
"""

import pickle
from src.feature.validate import (
    validate_token,
    validate_names,
    validate_names_characters,
    validate_handle_str,
    validate_handle_unique,
    validate_create_email,
    validate_u_id,
)
from src.feature.action import convert_token_to_u_id
from src.feature.error import AccessError, InputError

def user_profile(token, u_id):
    """For a valid user, returns information about their user_id, email, first
    name, last name, and handle

    Args:
        token (string)
        u_id (int)

    Returns:
        (dict): { user }
    """
    data = pickle.load(open("data.p", "rb"))
    # Authorised user check.
    authorised_to_display_profile = validate_token(data, token)
    if not authorised_to_display_profile:
        raise AccessError("User cannot display another user's profile, must log in first.")

    if not validate_u_id(data, u_id):
        raise InputError("User with u_id is not a valid user.")

    # Search data.py for the valid user with matching u_id.
    user = data.get_user_details(u_id)
    with open('data.p', 'wb') as FILE:
        pickle.dump(data, FILE)
    return {
        'user': {
            'u_id': u_id,
            'email': user['email'],
            'name_first': user['name_first'],
            'name_last': user['name_last'],
            'handle_str': user['handle_str'],
            'profile_img_url': user['profile_img_url']
        }
    }

def user_profile_setname(token, name_first, name_last):
    """Update the authorised user's first and last name

    Args:
        token (string)
        name_first (string)
        name_last (string)

    Returns:
        (dict): {}
    """
    data = pickle.load(open("data.p", "rb"))
    if not validate_token(data, token):
        raise InputError("Invalid token")
    if not validate_names(name_first) or not validate_names(name_last):
        raise InputError("Name should be between 1-50 chars")
    if not validate_names_characters(name_first) or not validate_names_characters(name_last):
        raise InputError("Invalid chars inputted")

    # changing name in the users field
    u_id = convert_token_to_u_id(data, token)
    data.set_user_name(u_id, name_first, name_last)
    data.set_user_name_in_channels(u_id, name_first, name_last)
    with open('data.p', 'wb') as FILE:
        pickle.dump(data, FILE)
    return {}

def user_profile_setemail(token, email):
    """Update the authorised user's email.

    Args:
        token (string): unique identifier of user.
        email (string): what the email will be set to.

    Returns:
        (dict): Contains no key types.
    """
    data = pickle.load(open("data.p", "rb"))
    # Error checks
    if not validate_token(data, token):
        raise AccessError("User cannot display another user's profile, must log in first.")
    if not validate_create_email(email):
        raise InputError("Email contains invalid syntax. Try again.")
    # Check for whether email is already in use.
    for curr_user in data.get_users():
        if curr_user['email'] == email:
            raise InputError("Email is already taken. Try again.")

    u_id = convert_token_to_u_id(data, token)
    data.set_user_email(u_id, email)
    with open('data.p', 'wb') as FILE:
        pickle.dump(data, FILE)

    return {}

def user_profile_sethandle(token, handle_str):
    '''Update authorised users handle

    Args:
        token (string)
        handle_str (string)

    Returns:
        (dict): {}
    '''
    data = pickle.load(open("data.p", "rb"))
    if not validate_token(data, token):
        raise InputError("Invalid Token.")
    if not validate_handle_unique(data, handle_str):
        raise InputError("This handle already exists")
    if not validate_handle_str(handle_str):
        raise InputError("Invalid characters, must be between 3-20 chars")

    # updating in users list.
    u_id = convert_token_to_u_id(data, token)
    data.set_user_handle(u_id, handle_str)
    with open('data.p', 'wb') as FILE:
        pickle.dump(data, FILE)
    return {}


def user_profile_uploadphoto(token, img_url, x_start, y_start, x_end, y_end):
    """Given a URL of an image on the internet, crops the image within bounds (x_start, y_start) and (x_end, y_end). Position (0,0) is the top left.

    Args:
        token (string)
        img_url (string)
        x_start (int)
        y_start (int)
        x_end (int)
        y_end (int)

    Returns:
        (dict): {}
    """
    return {}
