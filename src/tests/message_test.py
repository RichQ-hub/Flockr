"""
message feature test implementation to test functions in message.py

Feature implementation was written by Tam Do and Prathamesh Jagtap.

2020 T3 COMP1531 Major Project
"""

from datetime import timezone, datetime
import time
import pytest

import src.feature.auth as auth
import src.feature.channel as channel
import src.feature.channels as channels
import src.feature.message as message

from src.feature.other import clear
from src.feature.error import InputError, AccessError

#------------------------------------------------------------------------------#
#                                message_send                                  #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_send_more_than_1000_char(user_1, public_channel_1):
    """
    Testing when the message sent is over 1000 characters
    """
    message_str_1 = ("Hello" * 250)
    message_str_2 = ("HI " * 500)
    message_str_3 = ("My name is blah" * 100)
    with pytest.raises(InputError):
        message.message_send(user_1['token'], public_channel_1['channel_id'], message_str_1)
    with pytest.raises(InputError):
        message.message_send(user_1['token'], public_channel_1['channel_id'], message_str_2)
    with pytest.raises(InputError):
        message.message_send(user_1['token'], public_channel_1['channel_id'], message_str_3)
    clear()

def test_message_send_auth_user_not_in_channel(user_1, user_2, public_channel_1):
    """
    Testing when the authorised user has not joined the channel they
    are trying to post to
    """
    message_str = "Hello"
    with pytest.raises(AccessError):
        message.message_send(user_2['token'], public_channel_1['channel_id'], message_str)
    clear()

def test_message_send_expired_token(user_1, user_2, user_3, user_4, public_channel_1, default_message):
    """
    Testing invalid token for users which have logged out
    """
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])
    with pytest.raises(AccessError):
        message.message_send(user_1['token'], default_message['message_id'], "Hi")
    with pytest.raises(AccessError):
        message.message_send(user_1['token'], default_message['message_id'], "Hi")
    with pytest.raises(AccessError):
        message.message_send(user_1['token'], default_message['message_id'], "Hi")
    with pytest.raises(AccessError):
        message.message_send(user_1['token'], default_message['message_id'], "Hi")
    clear()

def test_message_send_incorrect_token_type(user_1, public_channel_1, default_message):
    """
    Testing invalid token data type handling
    """
    with pytest.raises(AccessError):
        message.message_send(12, default_message['message_id'], "Hi")
    with pytest.raises(AccessError):
        message.message_send(-12, default_message['message_id'], "Hi")
    with pytest.raises(AccessError):
        message.message_send(121.11, default_message['message_id'], "Hi")
    clear()

def test_message_send_channel_id(user_1, public_channel_1):
    """
    Testing when an invalid channel_id is used as a parameter
    """
    with pytest.raises(InputError):
        message.message_send(user_1['token'], public_channel_1['channel_id'] + 7, "Bye channel!")
    clear()

def test_message_send_valid_token(user_1, public_channel_1):
    """
    Testing if token is valid
    """
    with pytest.raises(AccessError):
        message.message_send(-1, public_channel_1['channel_id'], "Bye channel!")
    clear()

def test_message_send_output_empty_str(user_1, user_2, public_channel_1):
    """
    Testing an empty string message (Authorised user sends a message in a channel)
    """
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    message_str = ""
    with pytest.raises(InputError):
        message.message_send(user_2['token'], public_channel_1['channel_id'], message_str)
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_message_send_output_one(user_1, user_2, public_channel_1):
    """
    Testing a normal case (Authorised user sends a message in a channel)
    """
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    message_str_one = "Welcome guys!"
    message_str_two = "Hello, I'm Jane!"
    message.message_send(user_1['token'], public_channel_1['channel_id'], message_str_one)
    message.message_send(user_2['token'], public_channel_1['channel_id'], message_str_two)
    message_list = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    message_count = 0
    check_unique_msg_id = []
    for msg in message_list['messages']:
        message_count += 1
        check_unique_msg_id.append(msg['message_id'])
        assert msg['message'] in (message_str_one, message_str_two)
    assert message_count == 2
    assert check_unique_msg_id[0] != check_unique_msg_id[1]
    clear()

def test_message_send_output_two(user_1, user_2, user_3, user_4, public_channel_1):
    """
    Testing a longer case (multiple authorised users sending messages in a channel)
    """
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    channel.channel_join(user_3['token'], public_channel_1['channel_id'])
    channel.channel_join(user_4['token'], public_channel_1['channel_id'])
    msg_str_1 = "Welcome guys!"
    msg_str_2 = "Hello, I'm Jane!"
    msg_str_3 = "sup"
    msg_str_4 = "Ok, let's start the project"
    msg_str_5 = "Join the call when you're ready guys"
    msg_str_6 = "sure, lemme get something to eat first"
    msg_str_7 = "Yeah aight, I'm joining."
    message.message_send(user_1['token'], public_channel_1['channel_id'], msg_str_1)
    message.message_send(user_2['token'], public_channel_1['channel_id'], msg_str_2)
    message.message_send(user_3['token'], public_channel_1['channel_id'], msg_str_3)
    message.message_send(user_4['token'], public_channel_1['channel_id'], msg_str_4)
    message.message_send(user_1['token'], public_channel_1['channel_id'], msg_str_5)
    message.message_send(user_2['token'], public_channel_1['channel_id'], msg_str_6)
    message.message_send(user_3['token'], public_channel_1['channel_id'], msg_str_7)
    message_list = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    message_count = 0
    message_confirmed = False
    check_unique_msg_id = []
    for msg in message_list['messages']:
        if msg['message'] in {msg_str_1, msg_str_2, msg_str_3, 
                            msg_str_4, msg_str_5, msg_str_6, msg_str_7}:
            message_confirmed = True
        message_count += 1
        check_unique_msg_id.append(msg['message_id'])
    assert message_count == 7
    assert message_confirmed
    assert len(set(check_unique_msg_id)) == 7
    clear()

#------------------------------------------------------------------------------#
#                                message_remove                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_remove_expired_token(user_1, user_2, user_3, user_4, public_channel_1, default_message):
    """Testing invalid token for users which have logged out
    """
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        message.message_remove(user_1['token'], default_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_2['token'], default_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_3['token'], default_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_4['token'], default_message['message_id'])
    clear()

def test_message_remove_incorrect_token_type(user_1, public_channel_1, default_message):
    """Testing invalid token data type handling
    """
    with pytest.raises(AccessError):
        message.message_remove(12, default_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(-12, default_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(121.11, default_message['message_id'])
    clear()

def test_message_remove_wrong_data_type():
    """Testing when wrong data types are used as input
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    public_channel_1 = channels.channels_create(user['token'], 'Group 1', True)
    default_message = message.message_send(user['token'], public_channel_1['channel_id'], "Bye channel!")

    with pytest.raises(InputError):
        message.message_remove(user['token'], '@#$!')
    with pytest.raises(InputError):
        message.message_remove(user['token'], 67.666)
    with pytest.raises(InputError):
        message.message_remove(user['token'], default_message['message_id'] - 1)
    with pytest.raises(InputError):
        message.message_remove(user['token'], default_message['message_id'] + 1)
    clear()

def test_message_remove_message_not_existent():
    """Testing when message based on message_id does not exist
       and is subjected for deletion
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    public_channel_1 = channels.channels_create(user['token'], 'Group 1', True)
    default_message = message.message_send(user['token'], public_channel_1['channel_id'], "Bye channel!")

    with pytest.raises(InputError):
        message.message_remove(user['token'], default_message['message_id'] + 1)
    with pytest.raises(InputError):
        message.message_remove(user['token'], default_message['message_id'] - 1)
    with pytest.raises(InputError):
        message.message_remove(user['token'], default_message['message_id'] + 100)
    with pytest.raises(InputError):
        message.message_remove(user['token'], default_message['message_id'] - 100)
    clear()

def test_message_remove_message_deleted_already():
    """Testing when message based on message_id has been deleted already
       and is subjected for deletion again
    """
    clear()
    user = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    public_channel_1 = channels.channels_create(user['token'], 'Group 1', True)
    default_message = message.message_send(user['token'], public_channel_1['channel_id'], "Hey channel!")
    assert message.message_remove(user['token'], default_message['message_id']) == {}

    with pytest.raises(InputError):
        message.message_remove(user['token'], default_message['message_id'])
    clear()

def test_message_remove_not_authorized_channel_owner():
    """Testing when message based on message_id is called for deletion
       but the requester is not a channel_owner
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')

    public_channel_1 = channels.channels_create(user_1['token'], 'Group 1', True)
    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id'])
    default_message = message.message_send(user_1['token'], public_channel_1['channel_id'], "Hey channel!")

    with pytest.raises(AccessError):
        message.message_remove(user_2['token'], default_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_3['token'], default_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_4['token'], default_message['message_id'])
    clear()

def test_message_remove_not_authorized_flockr_owner():
    """Testing when message based on message_id is called for deletion
       but the requester is not a flockr owner
    """
    clear()
    user_1 = auth.auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user_2 = auth.auth_register('jennielin@gmail.com', 'password', 'Jennie', 'Lin')
    user_3 = auth.auth_register('johnperry@gmail.com', 'password', 'John', 'Perry')
    user_4 = auth.auth_register('prathsjag@gmail.com', 'password', 'Praths', 'Jag')

    public_channel_1 = channels.channels_create(user_1['token'], 'Group 1', True)
    default_message = message.message_send(user_1['token'], public_channel_1['channel_id'], "Hey channel!")

    with pytest.raises(AccessError):
        message.message_remove(user_2['token'], default_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_3['token'], default_message['message_id'])
    with pytest.raises(AccessError):
        message.message_remove(user_4['token'], default_message['message_id'])
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_message_remove_authorized_owner_channel(user_1, public_channel_1):
    """Testing when message based on message_id is deleted by channel owner / flockr owner
    """
    message_1 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'I')
    message_2 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'am')
    message_3 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'really')
    message_4 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'hungry :(')
    on_list = False
    assert message.message_remove(user_1['token'], message_1['message_id']) == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list

    assert message.message_remove(user_1['token'], message_3['message_id']) == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_3['message_id']:
            on_list = True
    assert not on_list

    assert message.message_remove(user_1['token'], message_2['message_id']) == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_2['message_id']:
            on_list = True
    assert not on_list

    assert message.message_remove(user_1['token'], message_4['message_id']) == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_4['message_id']:
            on_list = True
    assert not on_list
    clear()

def test_message_remove_authorized_flockr_owner(user_1, user_2, public_channel_2):
    """(Assumption Testing) Testing when message based on message_id is deleted by
       flockr owner who is not part of any channel
       (Assumption) First user to register is flockr owner
    """
    message_1 = message.message_send(user_2['token'], public_channel_2['channel_id'], 'I')
    message_2 = message.message_send(user_2['token'], public_channel_2['channel_id'], 'am')
    message_3 = message.message_send(user_2['token'], public_channel_2['channel_id'], 'really')
    message_4 = message.message_send(user_2['token'], public_channel_2['channel_id'], 'hungry :(')

    on_list = False
    assert message.message_remove(user_1['token'], message_1['message_id']) == {}
    message_data = channel.channel_messages(user_2['token'], public_channel_2['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list

    assert message.message_remove(user_1['token'], message_3['message_id']) == {}
    message_data = channel.channel_messages(user_2['token'], public_channel_2['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_3['message_id']:
            on_list = True
    assert not on_list

    assert message.message_remove(user_1['token'], message_2['message_id']) == {}
    message_data = channel.channel_messages(user_2['token'], public_channel_2['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_2['message_id']:
            on_list = True
    assert not on_list

    assert message.message_remove(user_1['token'], message_4['message_id']) == {}
    message_data = channel.channel_messages(user_2['token'], public_channel_2['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_4['message_id']:
            on_list = True
    assert not on_list
    clear()

def test_message_remove_authorized_user(user_1, user_2, public_channel_1):
    """Testing when user is not flockr owner or channel owner, and wants to delete
       his/her message which he/she sent earlier

       Also testing if this user is unable to delete any another messages
    """
    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    message_1 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'Im user 1!')
    message_2 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'Im user 2!')
    message_3 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'Okay bye!!')

    on_list = False
    assert message.message_remove(user_2['token'], message_2['message_id']) == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_2['message_id']:
            on_list = True
    assert not on_list

    assert message.message_remove(user_1['token'], message_3['message_id']) == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_3['message_id']:
            on_list = True
    assert not on_list

    with pytest.raises(AccessError):
        message.message_remove(user_2['token'], message_1['message_id'])
    clear()

#------------------------------------------------------------------------------#
#                                message_edit                                  #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_edit_expired_token(user_1, user_2, user_3, user_4, public_channel_1, default_message):
    """Testing invalid token for users which have logged out
    """
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])

    with pytest.raises(AccessError):
        message.message_edit(user_1['token'], default_message['message_id'], 'hello')
    with pytest.raises(AccessError):
        message.message_edit(user_2['token'], default_message['message_id'], 'hello')
    with pytest.raises(AccessError):
        message.message_edit(user_3['token'], default_message['message_id'], 'hello')
    with pytest.raises(AccessError):
        message.message_edit(user_4['token'], default_message['message_id'], 'hello')
    clear()

def test_message_edit_incorrect_token_type(user_1, public_channel_1, default_message):
    """Testing invalid token data type handling
    """
    with pytest.raises(AccessError):
        message.message_edit(12, default_message['message_id'], 'hello')
    with pytest.raises(AccessError):
        message.message_edit(-12, default_message['message_id'], 'hello')
    with pytest.raises(AccessError):
        message.message_edit(121.11, default_message['message_id'], 'hello')
    clear()

def test_message_edit_wrong_data_type(user_1, public_channel_1, default_message):
    """Testing when wrong data types are used as input
    """
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], '@#$!', 'hello')
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], 67.666, 'hello')
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], default_message['message_id'] - 1, 'hello')
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], default_message['message_id'] + 1, 'hello')
    clear()

def test_message_edit_integer_message(user_1, public_channel_1, default_message):
    """Testing when message data type is an integer
    """
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], default_message['message_id'], 0)
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], default_message['message_id'], -1)
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], default_message['message_id'], 100)
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], default_message['message_id'], 127.66)
    clear()

def test_message_edit_more_than_1000_char(user_1, public_channel_1, default_message):
    """
    Testing when the message to edit is over 1000 characters
    """
    message_str_1 = ("Hello" * 250)
    message_str_2 = ("HI " * 500)
    message_str_3 = ("My name is blah" * 100)
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], default_message['message_id'], message_str_1)
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], default_message['message_id'], message_str_2)
    with pytest.raises(InputError):
        message.message_edit(user_1['token'], default_message['message_id'], message_str_3)
    clear()

def test_message_edit_deleted_message(user_1, public_channel_1, default_message):
    """Testing when message based on message_id does not exist
       and is subjected for editing
    """
    assert message.message_remove(user_1['token'], default_message['message_id']) == {}

    with pytest.raises(InputError):
        message.message_edit(user_1['token'], default_message['message_id'], 'hey')
    clear()

def test_message_edit_not_authorized_channel_owner(user_1, user_2, user_3, user_4, public_channel_1):
    """Testing when message based on message_id is called for editing
       but the requester is not a channel_owner
    """
    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    channel.channel_invite(user_2['token'], public_channel_1['channel_id'], user_3['u_id'])
    default_message = message.message_send(user_1['token'], public_channel_1['channel_id'], "Hey channel!")

    with pytest.raises(AccessError):
        message.message_edit(user_2['token'], default_message['message_id'], 'lets edit!')
    with pytest.raises(AccessError):
        message.message_edit(user_3['token'], default_message['message_id'], 'lets edit!')
    with pytest.raises(AccessError):
        message.message_edit(user_4['token'], default_message['message_id'], 'lets edit!')
    clear()

def test_message_edit_not_authorized_flockr_owner(user_1, user_2, user_3, user_4, public_channel_1, default_message):
    """Testing when message based on message_id is called for editing
       but the requester is not a flockr owner
    """
    with pytest.raises(AccessError):
        message.message_edit(user_2['token'], default_message['message_id'], 'lets edit!')
    with pytest.raises(AccessError):
        message.message_edit(user_3['token'], default_message['message_id'], 'lets edit!')
    with pytest.raises(AccessError):
        message.message_edit(user_4['token'], default_message['message_id'], 'lets edit!')
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_message_edit_authorized_owner_channel(user_1, public_channel_1, default_message):
    """Testing when message based on message_id is edited by channel owner / flockr owner
    """
    on_list = False
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == default_message['message_id']:
            if messages['message'] == 'Hey channel!':
                on_list = True
    assert on_list

    edited = False
    assert message.message_edit(user_1['token'], default_message['message_id'], 'not hungry :)') == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == default_message['message_id']:
            if messages['message'] == 'not hungry :)':
                edited = True
    assert edited
    clear()

def test_message_edit_authorized_flockr_owner(user_1, user_2, public_channel_2, default_message):
    """(Assumption Testing) Testing when message based on message_id is edited by
       flockr owner who is not part of any channel
       (Assumption) First user to register is flockr owner
    """
    on_list = False
    default_message = message.message_send(user_2['token'], public_channel_2['channel_id'], "Hey channel!")
    message_data = channel.channel_messages(user_2['token'], public_channel_2['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == default_message['message_id']:
            if messages['message'] == 'Hey channel!':
                on_list = True
    assert on_list

    edited = False
    assert message.message_edit(user_1['token'], default_message['message_id'], 'not hungry :)') == {}
    message_data = channel.channel_messages(user_2['token'], public_channel_2['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == default_message['message_id']:
            if messages['message'] == 'not hungry :)':
                edited = True
    assert edited
    clear()

def test_message_edit_empty_string(user_1, user_2, public_channel_1):
    """Testing when message based on message_id is edited by
       an empty string; in which case the message is deleted

       Testing also when unauthorized user tries to edit message
       via an empty string
    """
    message_1 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'I')
    message_2 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'am')
    message_3 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'really')
    message_4 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'hungry :(')
    message_5 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'maybe :/')

    on_list = False
    assert message.message_edit(user_1['token'], message_1['message_id'], '') == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_1['message_id']:
            on_list = True
    assert not on_list

    assert message.message_edit(user_1['token'], message_3['message_id'], '') == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_3['message_id']:
            on_list = True
    assert not on_list

    assert message.message_edit(user_1['token'], message_2['message_id'], "") == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_2['message_id']:
            on_list = True
    assert not on_list

    assert message.message_edit(user_1['token'], message_4['message_id'], "") == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_4['message_id']:
            on_list = True
    assert not on_list

    with pytest.raises(AccessError):
        message.message_edit(user_2['token'], message_5['message_id'], "")
    clear()

def test_message_edit_authorized_user(user_1, user_2, public_channel_1):
    """Testing when user is not flockr owner or channel owner, and wants to edit
       his/her message which he/she sent earlier

       Also testing if this user is unable to edit any another messages
    """
    channel.channel_invite(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    message_1 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'Im user 1!')
    message_2 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'Im user 2!')
    message_3 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'Okay bye!!')

    on_list = False
    assert message.message_edit(user_2['token'], message_2['message_id'], "Nice to meet you!") == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_2['message_id']:
            if messages['message'] == 'Nice to meet you!':
                on_list = True
    assert on_list

    on_list = False
    assert message.message_edit(user_1['token'], message_3['message_id'], "I can edit!!!") == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_3['message_id']:
            if messages['message'] == 'I can edit!!!':
                on_list = True
    assert on_list

    on_list = False
    assert message.message_edit(user_2['token'], message_3['message_id'], "") == {}
    message_data = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    for messages in message_data['messages']:
        if messages['message_id'] == message_3['message_id']:
            on_list = True
    assert not on_list

    with pytest.raises(AccessError):
        message.message_edit(user_2['token'], message_1['message_id'], "I can edit admin!")
    clear()


#------------------------------------------------------------------------------#
#                               message_sendlater                              #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_message_send_later_more_than_1000_char(user_1, public_channel_1):
    """
    Testing when the message sent is over 1000 characters
    """
    message_str_1 = ("Hello" * 250)
    message_str_2 = ("HI " * 500)
    message_str_3 = ("My name is blah" * 100)
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    with pytest.raises(InputError):
        message.message_sendlater(user_1['token'], public_channel_1['channel_id'], message_str_1, curr_time + 7)
    with pytest.raises(InputError):
        message.message_sendlater(user_1['token'], public_channel_1['channel_id'], message_str_2, curr_time + 7)
    with pytest.raises(InputError):
        message.message_sendlater(user_1['token'], public_channel_1['channel_id'], message_str_3, curr_time + 7)
    clear()

def test_message_send_later_auth_user_not_in_channel(user_1, user_2, public_channel_1):
    """
    Testing when the authorised user has not joined the channel they
    are trying to post to
    """
    message_str = "Hello"
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    with pytest.raises(AccessError):
        message.message_sendlater(user_2['token'], public_channel_1['channel_id'], message_str, curr_time + 7)
    clear()

def test_message_send_later_expired_token(user_1, user_2, user_3, user_4, public_channel_1, default_message):
    """
    Testing invalid token for users which have logged out
    """
    auth.auth_logout(user_1['token'])
    auth.auth_logout(user_2['token'])
    auth.auth_logout(user_3['token'])
    auth.auth_logout(user_4['token'])
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    with pytest.raises(AccessError):
        message.message_sendlater(user_1['token'], default_message['message_id'], "Hi", curr_time + 7)
    with pytest.raises(AccessError):
        message.message_sendlater(user_1['token'], default_message['message_id'], "Hi", curr_time + 7)
    with pytest.raises(AccessError):
        message.message_sendlater(user_1['token'], default_message['message_id'], "Hi", curr_time + 7)
    with pytest.raises(AccessError):
        message.message_sendlater(user_1['token'], default_message['message_id'], "Hi", curr_time + 7)
    clear()

def test_message_send_later_incorrect_token_type(user_1, public_channel_1, default_message):
    """
    Testing invalid token data type handling
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    with pytest.raises(AccessError):
        message.message_sendlater(12, default_message['message_id'], "Hi", curr_time + 7)
    with pytest.raises(AccessError):
        message.message_sendlater(-12, default_message['message_id'], "Hi", curr_time + 7)
    with pytest.raises(AccessError):
        message.message_sendlater(121.11, default_message['message_id'], "Hi", curr_time + 7)
    clear()

def test_message_send_later_channel_id(user_1, public_channel_1):
    """
    Testing when an invalid channel_id is used as a parameter
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    with pytest.raises(InputError):
        message.message_sendlater(user_1['token'], public_channel_1['channel_id'] + 7, "Bye channel!", curr_time + 7)
    clear()

def test_message_send_later_valid_token(user_1, public_channel_1):
    """
    Testing if token is valid
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    with pytest.raises(AccessError):
        message.message_sendlater(-1, public_channel_1['channel_id'], "Bye channel!", curr_time + 7)
    clear()

def test_message_send_later_output_empty_str(user_1, user_2, public_channel_1):
    """
    Testing an empty string message (Authorised user sends a message in a channel)
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    message_str = ""
    with pytest.raises(InputError):
        message.message_sendlater(user_2['token'], public_channel_1['channel_id'], message_str, curr_time + 7)
    clear()

def test_message_send_later_time_is_in_past(user_1, public_channel_1):
    """
    Testing when time sent is a time in the past
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    with pytest.raises(InputError):
        message.message_sendlater(user_1['token'], public_channel_1['channel_id'], "Bye channel!", curr_time - 7)
    clear()

#?------------------------------ Output Testing ------------------------------?#

def test_message_send_later_time_sent_is_curr_time(user_1, user_2, public_channel_1):
    """
    Testing a case where time sent is the current time
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    message.message_sendlater(user_1['token'], public_channel_1['channel_id'], "Hi", curr_time)
    message_list = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    message_count = 0
    for msg in message_list['messages']:
        message_count += 1
        assert msg['time_created'] == curr_time
    assert message_count == 1
    clear()

def test_message_send_later_output_one(user_1, user_2, public_channel_1):
    """
    Testing a normal case (Authorised user sends a delayed message in a channel)
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    message_str_one = "Welcome guys!"
    message_str_two = "Hello, I'm Jane!"
    message.message_sendlater(user_1['token'], public_channel_1['channel_id'], message_str_one, curr_time + 7)
    message.message_sendlater(user_2['token'], public_channel_1['channel_id'], message_str_two, curr_time + 17)
    time.sleep(19)
    message_list = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    message_count = 0
    check_unique_msg_id = []

    for msg in message_list['messages']:
        message_count += 1
        check_unique_msg_id.append(msg['message_id'])
        assert msg['time_created'] in (curr_time + 7, curr_time + 17)
        assert msg['message'] in (message_str_one, message_str_two)
    assert message_count == 2
    assert check_unique_msg_id[0] != check_unique_msg_id[1]
    clear()

def test_message_send_later_output_two(user_1, user_2, user_3, user_4, public_channel_1):
    """
    Testing a longer case (multiple authorised users sending messages in a channel)
    """
    curr_time = int(datetime.now(tz=timezone.utc).timestamp())
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    channel.channel_join(user_3['token'], public_channel_1['channel_id'])
    channel.channel_join(user_4['token'], public_channel_1['channel_id'])
    msg_str_1 = "Welcome guys!"
    msg_str_2 = "Hello, I'm Jane!"
    msg_str_3 = "sup"
    msg_str_4 = "Ok, let's start the project"
    msg_str_5 = "Join the call when you're ready guys"
    msg_str_6 = "sure, lemme get something to eat first"
    msg_str_7 = "Yeah aight, I'm joining."
    message.message_sendlater(user_1['token'], public_channel_1['channel_id'], msg_str_1, curr_time + 1)
    message.message_sendlater(user_2['token'], public_channel_1['channel_id'], msg_str_2, curr_time + 2)
    message.message_sendlater(user_3['token'], public_channel_1['channel_id'], msg_str_3, curr_time + 3)
    message.message_sendlater(user_4['token'], public_channel_1['channel_id'], msg_str_4, curr_time + 4)
    message.message_sendlater(user_1['token'], public_channel_1['channel_id'], msg_str_5, curr_time + 5)
    message.message_sendlater(user_2['token'], public_channel_1['channel_id'], msg_str_6, curr_time + 6)
    message.message_sendlater(user_3['token'], public_channel_1['channel_id'], msg_str_7, curr_time + 7)
    time.sleep(9)
    message_list = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)
    message_count = 0
    message_confirmed = False
    check_unique_msg_id = []

    for msg in message_list['messages']:
        if msg['message'] in {msg_str_1, msg_str_2, msg_str_3, 
                            msg_str_4, msg_str_5, msg_str_6, msg_str_7}:
            message_confirmed = True
        message_count += 1
        check_unique_msg_id.append(msg['message_id'])
        assert msg['time_created'] in (curr_time + 1, curr_time + 2, curr_time + 3,
                                       curr_time + 4, curr_time + 5, curr_time + 6,
                                       curr_time + 7)
    assert message_count == 7
    assert message_confirmed
    assert len(set(check_unique_msg_id)) == 7
    clear()

#------------------------------------------------------------------------------#
#                                 message_react                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#



#------------------------------------------------------------------------------#
#                                message_unreact                               #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#


#?------------------------------ Output Testing ------------------------------?#



#------------------------------------------------------------------------------#
#                                  message_pin                                 #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_valid_message_id(user_1, default_message):
    """
    Test whether the message_id is a valid id.
    """
    with pytest.raises(InputError):
        message.message_pin(user_1['token'], default_message['message_id'] + 1)
    clear()

def test_already_pinned(user_1, user_2, public_channel_1):
    """
    Test for pinning an already pinned message.
    """
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])

    message_1 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'Hello')
    message.message_pin(user_1['token'], message_1['message_id'])

    with pytest.raises(InputError):
        message.message_pin(user_1['token'], message_1['message_id'])
    clear()

def test_user_is_member_of_channel_with_message(user_1, user_2, user_3, public_channel_2):
    """
    Test for user pinning a message in a channel that they are not a member of.
    """
    message_1 = message.message_send(user_2['token'], public_channel_2['channel_id'], 'Hello')

    with pytest.raises(AccessError):
        message.message_pin(user_3['token'], message_1['message_id'])
    clear()

def test_authorised_to_pin(user_1, default_message, logout_user_1):
    """
    Test for a logged out user trying to pin a message.
    """
    with pytest.raises(AccessError):
        message.message_pin(user_1['token'], default_message['message_id'])
    clear()

def test_non_owner_pin(user_1, user_2, public_channel_1):
    """
    Test for a user who is not an owner of the channel, pinning a message.
    """
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    message_1 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'Hello')

    with pytest.raises(AccessError):
        message.message_pin(user_2['token'], message_1['message_id'])
    clear()


#?------------------------------ Output Testing ------------------------------?#

def test_pin_correct_message(user_1, user_2, public_channel_1):
    """
    Test for pinning the correct message.
    """
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])

    message.message_send(user_1['token'], public_channel_1['channel_id'], 'Hello')
    message_2 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'Hi')
    message_3 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'Mate')
    message.message_send(user_2['token'], public_channel_1['channel_id'], 'What?')

    message.message_pin(user_1['token'], message_2['message_id'])
    message.message_pin(user_1['token'], message_3['message_id'])
    
    message_list = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned'] and (curr_message['message'] in ['Hi', 'Mate']):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 2
    clear()


def test_added_owner_can_pin(user_1, user_2, public_channel_1):
    """
    Test for pinning messages from a recently added owner.
    """
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    message_1 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'Hello')

    channel.channel_addowner(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    message.message_pin(user_2['token'], message_1['message_id'])

    message_list = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)

    for curr_message in message_list['messages']:
        if curr_message['message_id'] == message_1['message_id']:
            assert curr_message['is_pinned']
    clear()

def test_pin_owned_message(user_1, public_channel_1):
    """
    Test for pinning the user's own messages.
    """
    message_1 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'Hello')
    message.message_pin(user_1['token'], message_1['message_id'])

    message_list = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)

    for curr_message in message_list['messages']:
        if curr_message['message_id'] == message_1['message_id']:
            assert curr_message['is_pinned'] == True
    clear()

def test_pin_other_messages(user_1, user_2, user_3, public_channel_2):
    """
    Test for pinning other user's messages.
    """
    channel.channel_join(user_1['token'], public_channel_2['channel_id'])
    channel.channel_join(user_3['token'], public_channel_2['channel_id'])

    message_1 = message.message_send(user_1['token'], public_channel_2['channel_id'], 'Hello')
    message_2 = message.message_send(user_3['token'], public_channel_2['channel_id'], 'Hi')

    message.message_pin(user_2['token'], message_1['message_id'])
    message.message_pin(user_2['token'], message_2['message_id'])

    message_list = channel.channel_messages(user_1['token'], public_channel_2['channel_id'], 0)

    for curr_message in message_list['messages']:
        if curr_message['message_id'] == message_1['message_id']:
            assert curr_message['is_pinned']

    for curr_message in message_list['messages']:
        if curr_message['message_id'] == message_2['message_id']:
            assert curr_message['is_pinned']
    clear()

def test_pin_multiple_messages(user_1, user_2, user_3, user_4, public_channel_3):
    """
    Test for pinning multiple different messages.
    """
    channel.channel_join(user_1['token'], public_channel_3['channel_id'])
    channel.channel_join(user_2['token'], public_channel_3['channel_id'])
    channel.channel_join(user_4['token'], public_channel_3['channel_id'])

    message_1 = message.message_send(user_1['token'], public_channel_3['channel_id'], 'Hello')
    message_2 = message.message_send(user_2['token'], public_channel_3['channel_id'], 'Hi')
    message_3 = message.message_send(user_3['token'], public_channel_3['channel_id'], 'Mate')
    message_4 = message.message_send(user_4['token'], public_channel_3['channel_id'], 'What?')
    message.message_send(user_4['token'], public_channel_3['channel_id'], 'No')
    message_6 = message.message_send(user_2['token'], public_channel_3['channel_id'], 'Ok')

    message.message_pin(user_3['token'], message_1['message_id'])
    message.message_pin(user_3['token'], message_2['message_id'])
    message.message_pin(user_3['token'], message_3['message_id'])
    message.message_pin(user_3['token'], message_4['message_id'])
    message.message_pin(user_3['token'], message_6['message_id'])
    
    message_list = channel.channel_messages(user_1['token'], public_channel_3['channel_id'], 0)

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned']:
            count_msg_pinned += 1
        
    assert count_msg_pinned == 5
    clear()

def test_pin_in_private_channel(user_1, user_2, private_channel_1):
    """
    Test for pinning messages in private channels.
    """
    channel.channel_invite(user_1['token'], private_channel_1['channel_id'], user_2['u_id'])

    message_1 = message.message_send(user_1['token'], private_channel_1['channel_id'], 'Hello')
    message_2 = message.message_send(user_2['token'], private_channel_1['channel_id'], 'Hi')
    message_3 = message.message_send(user_2['token'], private_channel_1['channel_id'], 'Mate')

    message.message_pin(user_1['token'], message_1['message_id'])
    message.message_pin(user_1['token'], message_2['message_id'])
    message.message_pin(user_1['token'], message_3['message_id'])

    message_list = channel.channel_messages(user_2['token'], private_channel_1['channel_id'], 0)

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned']:
            count_msg_pinned += 1
        
    assert count_msg_pinned == 3
    clear()

def test_flockr_owner_pin_msg_in_nonmember_channels(user_1, user_2, private_channel_2):
    """
    (Assumption Testing) Test for the ability of flockr owner to pin messages in channels that
    they are not a part of.
    (Assumption) First user to register is flockr owner.
    """
    message_1 = message.message_send(user_2['token'], private_channel_2['channel_id'], 'I')
    message_2 = message.message_send(user_2['token'], private_channel_2['channel_id'], 'Am')
    message_3 = message.message_send(user_2['token'], private_channel_2['channel_id'], 'Insane')

    message.message_pin(user_1['token'], message_1['message_id'])
    message.message_pin(user_1['token'], message_2['message_id'])
    message.message_pin(user_1['token'], message_3['message_id'])

    message_list = channel.channel_messages(user_2['token'], private_channel_2['channel_id'], 0)

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if curr_message['is_pinned']:
            count_msg_pinned += 1
        
    assert count_msg_pinned == 3
    clear()


#------------------------------------------------------------------------------#
#                                 message_unpin                                #
#------------------------------------------------------------------------------#

#?-------------------------- Input/Access Error Testing ----------------------?#

def test_valid_message_id_unpin(user_1, default_message):
    """
    Test whether the message_id is a valid id.
    """
    with pytest.raises(InputError):
        message.message_unpin(user_1['token'], default_message['message_id'] + 1)
    clear()

def test_already_unpinned(user_1, user_2, public_channel_1):
    """
    Test for unpinning an already pinned message.
    """
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])

    message_1 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'No')

    with pytest.raises(InputError):
        message.message_unpin(user_1['token'], message_1['message_id'])
    clear()

def test_user_is_member_of_channel_with_message_unpin(user_1, user_2, user_3, public_channel_2):
    """
    Test for user unpinning a message in a channel that they are not a member of.
    """
    message_1 = message.message_send(user_2['token'], public_channel_2['channel_id'], 'No way!')
    message.message_pin(user_2['token'], message_1['message_id'])

    with pytest.raises(AccessError):
        message.message_unpin(user_3['token'], message_1['message_id'])
    clear()

def test_authorised_to_unpin(user_1, public_channel_1):
    """
    Test for a logged out user trying to unpin a message.
    """
    message_1 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'No way!')
    message.message_pin(user_1['token'], message_1['message_id'])
    auth.auth_logout(user_1['token'])

    with pytest.raises(AccessError):
        message.message_unpin(user_1['token'], message_1['message_id'])
    clear()

def test_non_owner_unpin(user_1, user_2, public_channel_1):
    """
    Test for a user who is not an owner of the channel, unpinning a message.
    """
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    message_1 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'Ok mate')
    message.message_pin(user_1['token'], message_1['message_id'])

    with pytest.raises(AccessError):
        message.message_unpin(user_2['token'], message_1['message_id'])
    clear()


#?------------------------------ Output Testing ------------------------------?#

def test_unpin_correct_message(user_1, user_2, public_channel_1):
    """
    Test for unpinning the correct message.
    """
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])

    message_1 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'Hello')
    message_2 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'Hi')
    message_3 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'Mate')
    message_4 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'What?')

    message.message_pin(user_1['token'], message_1['message_id'])
    message.message_pin(user_1['token'], message_2['message_id'])
    message.message_pin(user_1['token'], message_3['message_id'])
    message.message_pin(user_1['token'], message_4['message_id'])

    message.message_unpin(user_1['token'], message_1['message_id'])
    message.message_unpin(user_1['token'], message_3['message_id'])
    message.message_unpin(user_1['token'], message_4['message_id'])
    
    message_list = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)

    count_msg_pinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned'] and (curr_message['message'] in ['Hello', 'Mate', 'What?']):
            count_msg_pinned += 1
        
    assert count_msg_pinned == 3
    clear()

def test_added_owner_can_unpin(user_1, user_2, public_channel_1):
    """
    Test for unpinning messages from a recently added owner.
    """
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    message_1 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'Hello')

    channel.channel_addowner(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])
    message.message_pin(user_1['token'], message_1['message_id'])
    message.message_unpin(user_1['token'], message_1['message_id'])

    message_list = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)

    for curr_message in message_list['messages']:
        if curr_message['message_id'] == message_1['message_id']:
            assert not curr_message['is_pinned']
    clear()

def test_unpin_owned_message(user_1, user_2, public_channel_1):
    """
    Test for unpinning the user's own messages.
    """
    channel.channel_join(user_2['token'], public_channel_1['channel_id'])
    channel.channel_addowner(user_1['token'], public_channel_1['channel_id'], user_2['u_id'])

    message_1 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'Hello')
    message_2 = message.message_send(user_1['token'], public_channel_1['channel_id'], 'What')
    message_3 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'Are')
    message_4 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'You')
    message_5 = message.message_send(user_2['token'], public_channel_1['channel_id'], 'Doing?')

    message.message_pin(user_1['token'], message_1['message_id'])
    message.message_pin(user_1['token'], message_2['message_id'])
    message.message_pin(user_1['token'], message_3['message_id'])
    message.message_pin(user_2['token'], message_4['message_id'])
    message.message_pin(user_2['token'], message_5['message_id'])

    message.message_unpin(user_2['token'], message_4['message_id'])
    message.message_unpin(user_2['token'], message_5['message_id'])

    message_list = channel.channel_messages(user_1['token'], public_channel_1['channel_id'], 0)

    count_msg_unpinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned']:
            count_msg_unpinned += 1
        
    assert count_msg_unpinned == 2
    clear()

def test_unpin_other_messages(user_1, user_2, user_3, public_channel_2):
    """
    Test for unpinning other user's messages.
    """
    channel.channel_join(user_1['token'], public_channel_2['channel_id'])
    channel.channel_join(user_3['token'], public_channel_2['channel_id'])

    message_1 = message.message_send(user_1['token'], public_channel_2['channel_id'], 'Hello')
    message_2 = message.message_send(user_2['token'], public_channel_2['channel_id'], 'What')
    message.message_send(user_2['token'], public_channel_2['channel_id'], 'Are')
    message_4 = message.message_send(user_2['token'], public_channel_2['channel_id'], 'You')
    message_5 = message.message_send(user_3['token'], public_channel_2['channel_id'], 'Doing?')

    message.message_pin(user_1['token'], message_1['message_id'])
    message.message_pin(user_1['token'], message_2['message_id'])
    message.message_pin(user_1['token'], message_4['message_id'])
    message.message_pin(user_1['token'], message_5['message_id'])

    message.message_unpin(user_1['token'], message_2['message_id'])
    message.message_unpin(user_1['token'], message_4['message_id'])
    message.message_unpin(user_1['token'], message_5['message_id'])

    message_list = channel.channel_messages(user_2['token'], public_channel_2['channel_id'], 0)

    count_msg_unpinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned']:
            count_msg_unpinned += 1
        
    assert count_msg_unpinned == 4
    clear()

def test_unpin_multiple_messages(user_1, user_2, user_3, user_4, public_channel_3):
    """
    Test for unpinning multiple different messages.
    """
    channel.channel_join(user_1['token'], public_channel_3['channel_id'])
    channel.channel_join(user_2['token'], public_channel_3['channel_id'])
    channel.channel_join(user_4['token'], public_channel_3['channel_id'])

    message_1 = message.message_send(user_1['token'], public_channel_3['channel_id'], 'Hello')
    message_2 = message.message_send(user_2['token'], public_channel_3['channel_id'], 'Hi')
    message_3 = message.message_send(user_3['token'], public_channel_3['channel_id'], 'Mate')
    message_4 = message.message_send(user_4['token'], public_channel_3['channel_id'], 'What?')
    message_5 = message.message_send(user_4['token'], public_channel_3['channel_id'], 'No')
    message_6 = message.message_send(user_2['token'], public_channel_3['channel_id'], 'Ok')
    message_7 = message.message_send(user_2['token'], public_channel_3['channel_id'], 'Ok')

    message.message_pin(user_3['token'], message_1['message_id'])
    message.message_pin(user_3['token'], message_2['message_id'])
    message.message_pin(user_3['token'], message_3['message_id'])
    message.message_pin(user_3['token'], message_4['message_id'])
    message.message_pin(user_3['token'], message_5['message_id'])
    message.message_pin(user_3['token'], message_6['message_id'])
    message.message_pin(user_3['token'], message_7['message_id'])

    channel.channel_addowner(user_3['token'], public_channel_3['channel_id'], user_2['u_id'])

    message.message_unpin(user_2['token'], message_1['message_id'])
    message.message_unpin(user_2['token'], message_3['message_id'])
    message.message_unpin(user_2['token'], message_4['message_id'])
    message.message_unpin(user_2['token'], message_5['message_id'])
    message.message_unpin(user_2['token'], message_6['message_id'])
    
    message_list = channel.channel_messages(user_1['token'], public_channel_3['channel_id'], 0)

    count_msg_unpinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned']:
            count_msg_unpinned += 1
        
    assert count_msg_unpinned == 5
    clear()

def test_unpin_in_private_channel(user_1, user_2, private_channel_1):
    """
    Test for unpinning messages in private channels.
    """
    channel.channel_invite(user_1['token'], private_channel_1['channel_id'], user_2['u_id'])

    message_1 = message.message_send(user_1['token'], private_channel_1['channel_id'], 'Hello')
    message_2 = message.message_send(user_2['token'], private_channel_1['channel_id'], 'Hi')
    message_3 = message.message_send(user_2['token'], private_channel_1['channel_id'], 'Mate')

    message.message_pin(user_1['token'], message_1['message_id'])
    message.message_pin(user_1['token'], message_2['message_id'])
    message.message_pin(user_1['token'], message_3['message_id'])

    message.message_unpin(user_1['token'], message_1['message_id'])
    message.message_unpin(user_1['token'], message_3['message_id'])

    message_list = channel.channel_messages(user_2['token'], private_channel_1['channel_id'], 0)

    count_msg_unpinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned']:
            count_msg_unpinned += 1
        
    assert count_msg_unpinned == 2
    clear()

def test_flockr_owner_unpin_msg_in_nonmember_channels(user_1, user_2, private_channel_2):
    """
    (Assumption Testing) Test for the ability of flockr owner to unpin messages in channels that
    they are not a part of.
    (Assumption) First user to register is flockr owner.
    """
    message_1 = message.message_send(user_2['token'], private_channel_2['channel_id'], 'I')
    message_2 = message.message_send(user_2['token'], private_channel_2['channel_id'], 'Am')
    message_3 = message.message_send(user_2['token'], private_channel_2['channel_id'], 'Insane')

    message.message_pin(user_1['token'], message_1['message_id'])
    message.message_pin(user_1['token'], message_2['message_id'])
    message.message_pin(user_1['token'], message_3['message_id'])

    message.message_unpin(user_1['token'], message_2['message_id'])
    message.message_unpin(user_1['token'], message_3['message_id'])

    message_list = channel.channel_messages(user_2['token'], private_channel_2['channel_id'], 0)

    count_msg_unpinned = 0
    for curr_message in message_list['messages']:
        if not curr_message['is_pinned']:
            count_msg_unpinned += 1
        
    assert count_msg_unpinned == 2
    clear()
