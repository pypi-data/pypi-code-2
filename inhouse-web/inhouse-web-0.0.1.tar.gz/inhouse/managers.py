# -*- coding: utf-8 -*-

"""Managers for the model classes"""

from django.db.models import Manager

import models


class CustomerManager(Manager):

    pass


class NewsManager(Manager):

    def get_current(self):
        pass


class ProjectManager(Manager):

    def get_by_customer(self, customer, active_only=True, user=None):
        """Return a customer's projects.

        :param customer: A :class:`Customer` model
        :param active_only: Display only bookable projects
        :param user: A :class:`User` model

        :returns: A query object
        """
        query = models.Project.objects.select_related().filter(
            customer=customer)
        if active_only:
            query = query.filter(project__status__in=(
                models.PROJECT_STATUS_IDLE, models.PROJECT_STATUS_OPEN))
        if user:
            query = query.filter(projectuser__user=user)
        return query

    def get_by_user(self, user, active_only=True):
        """Returns all project a user is working for.

        :param user: A :class:`User` model
        :param active_only: Display only bookable projects

        :returns: A query object
        """
        query = models.Project.objects.select_related().filter(
            projectuser__user=user)
        if active_only:
            query = query.filter(project__status__in=(
                models.PROJECT_STATUS_IDLE, models.PROJECT_STATUS_OPEN))
        return query
