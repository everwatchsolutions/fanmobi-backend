"""
Views
"""
import logging

from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import status
from rest_framework import viewsets
from rest_framework.response import Response

import main.permissions as permissions
import main.serializers as serializers
import main.models as models
import main.services as services
import main.errors as errors

# Get an instance of a logger
logger = logging.getLogger('fanmobi')

class GenreViewSet(viewsets.ModelViewSet):
    queryset = services.get_all_genres()
    serializer_class = serializers.GenreSerializer
    # permission_classes = (permissions.IsFan,)


class GroupViewSet(viewsets.ModelViewSet):
    queryset = services.get_all_groups()
    serializer_class = serializers.GroupSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = services.get_all_users()
    serializer_class = serializers.UserSerializer
    # permission_classes = (permissions.IsFan,)


class BasicProfileViewSet(viewsets.ModelViewSet):
    # permission_classes = (permissions.IsFan,)
    serializer_class = serializers.BasicProfileSerializer

    def get_queryset(self):
        queryset = services.get_all_profiles()
        role = self.request.query_params.get('role', None)
        if role:
            queryset = services.get_profiles_by_role(role)
        return queryset


class ArtistViewSet(viewsets.ModelViewSet):
    queryset = services.get_all_artists()
    permission_classes = (permissions.IsArtistOrReadOnly,)
    serializer_class = serializers.ArtistProfileSerializer

    def create(self, request):
        """
        Create a new artist
        """
        try:
            logger.debug('inside ArtistViewSet.create, data: %s' % request.data)
            serializer = serializers.ArtistProfileSerializer(data=request.data,
                context={'request': request}, partial=True)
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            raise e

    def update(self, request, pk=None):
        """
        Create a new artist
        """
        try:
            logger.debug('inside ArtistViewSet.update, data: %s' % request.data)
            instance = self.get_queryset().get(pk=pk)
            serializer = serializers.ArtistProfileSerializer(instance,
                data=request.data, context={'request': request}, partial=True)
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except models.ArtistProfile.DoesNotExist:
            return Response('Artist does not exist', status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            raise e


# class VenueViewSet(viewsets.ModelViewSet):
#     queryset = services.get_all_venues()
#     permission_classes = (permissions.IsFan,)
#     serializer_class = serializers.VenueSerializer


class ShowViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsArtistOrReadOnly,)
    serializer_class = serializers.ShowSerializer

    def get_queryset(self):
        return services.get_all_shows()

    def list(self, request, artist_pk=None):
        queryset = self.get_queryset().filter(artist__id=artist_pk)
        # because we override the queryset here, we must
        # manually invoke the pagination methods
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.ShowSerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.ShowSerializer(queryset, many=True,
            context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None, artist_pk=None):
        queryset = self.get_queryset().get(pk=pk, artist__id=artist_pk)
        serializer = serializers.ShowSerializer(queryset,
            context={'request': request})
        return Response(serializer.data)

    def create(self, request, artist_pk=None):
        """
        Create a new show
        """
        try:
            serializer = serializers.ShowSerializer(data=request.data,
                context={'request': request, 'artist_pk': artist_pk})
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except errors.PermissionDenied:
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
          raise e

    def update(self, request, pk=None, artist_pk=None):
        """
        Update an existing show
        """
        try:
            instance = self.get_queryset().get(pk=pk, artist__id=artist_pk)
            serializer = serializers.ShowSerializer(instance, data=request.data,
                context={'request': request, 'artist_pk': artist_pk})
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except errors.PermissionDenied:
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
          raise e

    def destroy(self, request, pk=None, artist_pk=None):
        queryset = self.get_queryset()
        show = get_object_or_404(queryset, pk=pk)
        try:
            services.delete_show(request.user.username, show)
        except errors.PermissionDenied:
            return Response('Cannot update another artist\'s show',
                status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MessageViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsArtistOrReadOnly,)
    serializer_class = serializers.MessageSerializer

    def get_queryset(self):
        return services.get_all_messages()

    def list(self, request, artist_pk=None):
        queryset = self.get_queryset().filter(artist__id=artist_pk)
        # because we override the queryset here, we must
        # manually invoke the pagination methods
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.MessageSerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.MessageSerializer(queryset, many=True,
            context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None, artist_pk=None):
        try:
            queryset = self.get_queryset().get(pk=pk, artist__id=artist_pk)
            serializer = serializers.MessageSerializer(queryset,
                context={'request': request})
            return Response(serializer.data)
        except models.Message.DoesNotExist:
            return Response('Message not found',
                    status=status.HTTP_404_NOT_FOUND)

    def create(self, request, artist_pk=None):
        """
        Create a new message
        """
        try:
            serializer = serializers.MessageSerializer(data=request.data,
                context={'request': request, 'artist_pk': artist_pk})
            if not serializer.is_valid():
                logger.error('%s' % serializer.errors)
                return Response(serializer.errors,
                    status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except errors.PermissionDenied:
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
          raise e

    def destroy(self, request, pk=None, artist_pk=None):
        queryset = self.get_queryset()
        message = get_object_or_404(queryset, pk=pk)
        try:
            services.delete_message(request.user.username, message)
        except errors.PermissionDenied:
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)


class FanMessageViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.Anyone,)
    serializer_class = serializers.MessageSerializer

    def get_queryset(self):
        return services.get_all_messages()

    def list(self, request, profile_pk=None):
        basic_profile = models.BasicProfile.objects.get(id=profile_pk)
        queryset = services.get_all_unread_messages(basic_profile.user.username)
        # because we override the queryset here, we must
        # manually invoke the pagination methods
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = serializers.MessageSerializer(page,
                context={'request': request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = serializers.MessageSerializer(queryset, many=True,
            context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None, profile_pk=None):
        return Response('Not implemented', status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, profile_pk=None):
        return Response('Not implemented', status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, profile_pk=None):
        queryset = self.get_queryset()
        basic_profile = models.BasicProfile.objects.get(id=profile_pk)
        message = get_object_or_404(queryset, pk=pk)
        try:
            services.mark_message_as_read(basic_profile.user.username, message)
        except errors.PermissionDenied:
            return Response('Permission Denied',
                status=status.HTTP_403_FORBIDDEN)
        return Response(status=status.HTTP_204_NO_CONTENT)
