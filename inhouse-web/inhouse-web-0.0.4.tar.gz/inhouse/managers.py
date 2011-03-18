# -*- coding: utf-8 -*-

"""Managers for the model classes"""

from datetime import datetime

from django.contrib.auth.models import Group
from django.db.models import Manager

import models


class CustomerManager(Manager):

    pass


class DepartmentManager(Manager):

    def get_by_user(self, user):
        """Returns the user`s departments.

        :param user: A :class:`User` model
        :returns: A query object
        """
        query = models.Department.objects.filter(
            departmentuser__user=user)
        return query


class NewsManager(Manager):

    def get_current(self, user):
        """Returns all current news, visible to a user.

        :param user: A :class:`User` instance
        :returns: A query object of :class:`News`
        """
        now = datetime.now()
        query = models.News.objects.filter(valid_from__lte=now,
                                           valid_to__gte=now)
        query = query.filter(newsgroup__group__user=user)
        query = query.order_by('-id')
        return query.distinct()


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
            query = query.filter(
                project__status__in=models.PROJECT_ACTIVE_STATUS)
        if user:
            query = query.filter(projectuser__user=user)
        return query.distinct()

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
        return query.distinct()


class ProjectStepManager(Manager):

    def get_by_name(self, project, name):
        query = models.ProjectStep.objects.filter(project=project, name=name)
        return query
