"""
user feature implementation as specified by the specification

Feature implementation was written by Christian Ilagan, Richard Quisumbing and
Tam Do.

2020 T3 COMP1531 Major Project
"""

import pickle

from src.feature.confirm import confirm_token, confirm_u_id
from src.globals import DATA_FILE, NON_EXIST
from src.feature.validate import (
    validate_names,
    validate_names_characters,
    validate_handle_str,
    validate_handle_unique,
    validate_create_email,
)
from src.feature.action import convert_email_to_u_id, convert_token_to_u_id
from src.classes.error import InputError

def user_profile(token, u_id):
    """For a valid user, returns information about their user_id, email, first
    name, last name, and handle

    Args:
        token (string)
        u_id (int)

    Returns:
        (dict): { user }
    """
    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)
    confirm_u_id(data, u_id)

    # Search data.py for the valid user with matching u_id.
    user = data.get_user_details(u_id)
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
    
    data = pickle.load(open(DATA_FILE, "rb"))
    # Error checks: Basic validation
    confirm_token(data, token)
    
    # Error check: Name validation
    if not validate_names(name_first):
        raise InputError(description="First name must be between 1 to 50 characters long (inclusive)")
    if not validate_names(name_last):
        raise InputError(description="Last name must be between 1 to 50 characters long (inclusive)")
    if not validate_names_characters(name_first):
        raise InputError(description="First name can only include uppercase and lowercase alphabetical characters, hyphens or whitespaces")
    if not validate_names_characters(name_last):
        raise InputError(description="Last name can only include uppercase and lowercase alphabetical characters, hyphens or whitespaces")

    # changing name in the users field
    u_id = convert_token_to_u_id(data, token)
    data.set_user_name(u_id, name_first, name_last)
    data.set_user_name_in_channels(u_id, name_first, name_last)

    with open(DATA_FILE, 'wb') as FILE:
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

    data = pickle.load(open(DATA_FILE, "rb"))
    
    # Error checks: Basic validation
    confirm_token(data, token)

    # Error check: Email validation
    if not validate_create_email(email):
        raise InputError(description="InputError: Invalid email address")
    # Check for whether email is already in use.
    for curr_user in data.get_users():
        if curr_user['email'] == email:
            raise InputError(description=f"InputError: Email address is already being used by another user")

    u_id = convert_token_to_u_id(data, token)
    data.set_user_email(u_id, email)

    with open(DATA_FILE, 'wb') as FILE:
        pickle.dump(data, FILE)

    return {}

def user_profile_sethandle(token, handle_str):
    """Update authorised users handle

    Args:
        token (string)
        handle_str (string)

    Returns:
        (dict): {}
    """
    data = pickle.load(open(DATA_FILE, "rb"))

    # Error checks: Basic validation
    confirm_token(data, token)

    # Error check: handle_str must be between 3 and 20 characters
    if not validate_handle_str(handle_str):
        raise InputError(description="InputError: Handle string must be between 3 and 20 characters (inclusive)")

    # Error check: handle is already used by another user
    if not validate_handle_unique(data, handle_str):
        raise InputError(description="InputError: Handle is already used by another user")

    # updating in users list.
    u_id = convert_token_to_u_id(data, token)
    data.set_user_handle(u_id, handle_str)

    with open(DATA_FILE, 'wb') as FILE:
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
