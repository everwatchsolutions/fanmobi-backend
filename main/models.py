"""
model definitions for fanmobi

"""
import logging
import os

import django.contrib.auth
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings

from PIL import Image

import main.constants as constants

# Get an instance of a logger
logger = logging.getLogger('fanmobi')

# TODO:
# - mark messages as read
# - permissions (can artists send users messages)
# - current user location?
# - login/logout
# - upload avatar (and thumb)

class Genre(models.Model):
    """
    Music genres
    """
    name = models.CharField(max_length=128, unique=True)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name


class ArtistProfile(models.Model):
    basic_profile = models.ForeignKey('BasicProfile', related_name='artists')
    name = models.CharField(max_length=256, unique=True)
    hometown = models.CharField(max_length=256, blank=True, null=True)
    bio = models.CharField(max_length=8192, blank=True, null=True)
    avatar_url_thumb = models.URLField(max_length=2048)
    avatar_url = models.URLField(max_length=2048)
    website = models.URLField(max_length=2048)
    facebook_id = models.Charfield(max_length=256)
    twitter_id = models.Charfield(max_length=256)
    youtube_id = models.Charfield(max_length=256)
    soundcloud_id = models.Charfield(max_length=256)
    itunes_url = models.URLField(max_length=2048)
    ticket_url = models.URLField(max_length=2048)
    merch_url = models.URLField(max_length=2048)
    paypal_email = models.EmailField()
    current_latitude = models.DecimalField(max_digits=8, decimal_places=3,
        blank=True, null=True)
    current_longitude = models.DecimalField(max_digits=8, decimal_places=3,
        blank=True, null=True)
    next_show = models.ForeignKey('Show', related_name='artists')
    genres = models.ManyToManyField(
        Genre,
        related_name='artists',
        db_table='artist_genre')
    # thank you message
    # thank you attachment


class BasicProfile(models.Model):
    """
    Basic info for a user (fan)

    An Artist also has a basic profile

    Note that some information (username, email, last_login, date_joined) is
    held in the associated Django User model. In addition, the user's role
    (USER, ARTIST, or ADMIN) is represented by the Group
    associated with the Django User model

    Notes on use of contrib.auth.models.User model:
        * first_name and last_name are not used
        * is_superuser is always set to False
        * is_staff is set to True for Admins
        * password: TBD
    """
    # instead of overriding the builtin Django User model used
    # for authentication, we extend it
    # https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#extending-the-existing-user-model
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True,
        blank=True)

    # artist->user connections
    connected_artists = models.ManyToManyField(
        'ArtistProfile',
        related_name='connected_users',
        db_table='artist_user'
    )

    def __repr__(self):
        return 'Profile: %s' % self.user.username

    def __str__(self):
        return self.user.username

    @staticmethod
    def create_groups():
        """
        Groups are used as Roles, and as such are relatively static, hence
        their declaration here (NOTE that this must be invoked manually
        after the server has started)
        """
        # create the different Groups (Roles) of users
        group = django.contrib.auth.models.Group.objects.create(
            name='FAN')
        group = django.contrib.auth.models.Group.objects.create(
            name='ARTIST')
        group = django.contrib.auth.models.Group.objects.create(
            name='ADMIN')

    def highest_role(self):
        """
        ADMIN > ARTIST > FAN
        """
        groups = self.user.groups.all()
        group_names = [i.name for i in groups]

        if 'ADMIN' in group_names:
            return 'ADMIN'
        elif 'ARTIST' in group_names:
            return 'ARTIST'
        elif 'FAN' in group_names:
            return 'FAN'
        else:
            # TODO: raise exception?
            logger.error('User %s has invalid Group' % self.user.username)
            return ''

    @staticmethod
    def create_user(username, **kwargs):
        """
        Create a new User and Fan object

        kwargs:
            password
            groups (['group1_name', 'group2_name'])

        """
        # TODO: what to make default password?
        password = kwargs.get('password', 'password')

        email = kwargs.get('email', '')

        # create User object
        # if this user is an ORG_STEWARD or APPS_MALL_STEWARD, give them
        # access to the admin site
        groups = kwargs.get('groups', ['USER'])
        if 'ADMIN' in groups:
            user = django.contrib.auth.models.User.objects.create_superuser(
                username=username, email=email, password=password)
            user.save()
            # logger.warn('creating superuser: %s, password: %s' % (username, password))
        else:
            user = django.contrib.auth.models.User.objects.create_user(
                username=username, email=email, password=password)
            user.save()
            # logger.info('creating user: %s' % username)

        # add user to group(s) (i.e. Roles - FAN, ARTIST, ADMIN). If no
        # specific Group is provided, we will default to USER
        for i in groups:
            g = django.contrib.auth.models.Group.objects.get(name=i)
            user.groups.add(g)

        # get additional profile information (so far none)

        # create the fan object and associate it with the User
        f = BasicProfile(user=user)
        f.save()

        return f

class Message(models.Model):
    """
    A message (created by an artist for their users)
    """
    text = models.CharField(max_length=8192)
    created_at = models.DateTimeField(auto_now=True)
    attachment = models.URLField(max_length=2048)
    artist = models.ForeignKey(ArtistProfile, related_name='messages')

    def __repr__(self):
        return '%s:%s' % (self.artist.name, self.created_at)

    def __str__(self):
        return '%s:%s' % (self.artist.name, self.created_at)

class Venue(models.Model):
    """
    A venue
    """
    name = models.CharField(max_length=1024, unique=True)
    description = models.CharField(max_length=8192, blank=True, null=True)
    latitude = models.DecimalField(max_digits=8, decimal_places=3)
    longitude = models.DecimalField(max_digits=8, decimal_places=3)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

class Show(models.Model):
    """
    A Show
    """
    start = models.DateTimeField()
    end = models.DateTimeField()
    artist = models.ForeignKey(ArtistProfile, related_name='shows')
    venue = models.ForeignKey(Venue, related_name='shows')

    def __repr__(self):
        return '%s:%s:%s' % (self.artist.name, self.venue.name, self.start)

    def __str__(self):
        return '%s:%s:%s' % (self.artist.name, self.venue.name, self.start)


