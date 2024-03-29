"""
Access the ORM primarily through this
"""
import logging
import os.path

from django.conf import settings

import django.contrib.auth

import main.models as models

# Get an instance of a logger
logger = logging.getLogger('fanmobi')

def get_profile(username):
    """
    get a user's Profile
    """
    try:
        profile = models.BasicProfile.objects.get(user__username=username)
        return profile
    except models.BasicProfile.DoesNotExist:
        return None

def get_profile_by_id(id):
    """
    Get a user's Profile by id
    """
    try:
        profile = models.BasicProfile.objects.get(id=id)
        return profile
    except models.BasicProfile.DoesNotExist:
        return None

def is_admin(username):
    try:
        profile = get_profile(username)
        groups = profile.user.groups.values_list('name', flat=True)
        if 'ADMIN' in groups:
            return True
        return False
    except Exception:
        return False

def can_access(current_username, requested_profile_id):
    """
    Determine if a user should have access to another user's profile

    Args:
        current_username: username currently logged in
        requested_profile_id: id of models.Profile to access
    """
    try:
        requested_profile_id = int(requested_profile_id)
    except ValueError:
        return False
    if is_admin(current_username):
        return True
    profile = get_profile_by_id(requested_profile_id)
    if not profile:
        return False
    if profile.user.username != current_username:
        return False
    return True

def get_all_genres():
    return models.Genre.objects.all()

def get_all_users():
    return django.contrib.auth.models.User.objects.all()

def get_artist_by_id(id):
    try:
        return models.ArtistProfile.objects.get(id=id)
    except models.ArtistProfile.DoesNotExist:
        return None

def get_all_groups():
    return django.contrib.auth.models.Group.objects.all()

def get_all_profiles():
    return models.BasicProfile.objects.all()

def get_profiles_by_role(role):
    return models.BasicProfile.objects.filter(
        user__groups__name__exact=role)

def get_all_artists():
    return models.ArtistProfile.objects.all()

# def get_all_venues():
#     return models.Venue.objects.all()

def get_all_shows():
    return models.Show.objects.all()

def get_all_messages():
    return models.Message.objects.all()

def get_all_unread_messages(username):
    profile = get_profile(username)
    # get all artists connected to this user
    artists = models.ArtistProfile.objects.filter(connected_users__in=[profile.id])
    # get all messages from these artists
    artist_ids = [a.id for a in artists]
    messages = models.Message.objects.filter(artist__id__in=artist_ids)
    # and remvove the messages that have been dismissed
    dismissed_messages = messages.filter(dismissed_by__in=[profile.id])
    unread_messages = messages.exclude(id__in=[msg.id for msg in dismissed_messages])
    return unread_messages

def mark_message_as_read(username, message):
    profile = get_profile(username)
    message.dismissed_by.add(profile)
    return


def delete_show(username, show):
    profile = get_profile(username)
    if username != show.artist.basic_profile.user.username and profile.highest_role() not in ['ADMIN']:
        raise errors.PermissionDenied('Cannot delete a show for another artist')
    show.delete()

def delete_message(username, message):
    profile = get_profile(username)
    if username != message.artist.basic_profile.user.username and profile.highest_role() not in ['ADMIN']:
        raise errors.PermissionDenied('Cannot delete a message for another artist')
    message.delete()

def get_all_images():
    images = models.Image.objects.all()
    return images

def get_image_path(pk, image_type):
    """
    Return absolute file path to an image given its id (pk)
    """
    image = models.Image.objects.get(id=pk)
    image_path = settings.MEDIA_ROOT + '/' + str(image.id) + '_' + image_type + '.' + image.file_extension
    if os.path.isfile(image_path):
        return image_path
    else:
        logger.error('image for pk %d does not exist' % pk)
        # TODO: raise exception
        return '/does/not/exist'

def get_image_by_id(id):
    # Since this is effectively only metadata about the image and not the image
    # itself, access control is not enforced here. That is done when the image
    # itself is served
    try:
        return models.Image.objects.get(id=id)
    except models.Image.DoesNotExist:
        return None

def user_is_artist(username):
    """
    Returns True if user is an artist
    """
    if models.ArtistProfile.objects.filter(basic_profile__user__username=username).count() > 0:
        return True
    return False

def get_artist_id_by_username(username):
    """
    Returns the artist id for a given username, or null
    """
    artist = models.ArtistProfile.objects.filter(basic_profile__user__username=username).first()
    if artist:
        return artist.id
    else:
        return None

