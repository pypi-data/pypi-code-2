from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
from languages.models import Language
from projects.models import Project
from txcommon.log import log_model

class TeamManager(models.Manager):

    def get_or_none(self, project, language_code):
        """
        Return a Team object or None if it doesn't exist.
        """
        if project.outsource:
            project=project.outsource
        try:
            return self.get(project__pk=project.pk, 
                language__code__exact=language_code)
        except Team.DoesNotExist:
            return None

class Team(models.Model):
    """
    A team is a set of people that work together in pro of a project in a 
    specific language.
    """
    project = models.ForeignKey(Project, verbose_name=_('Project'),
        blank=False, null=False,
        help_text=_("The project which this team belongs to."))
    language = models.ForeignKey(Language, verbose_name=_('Language'), 
        blank=False, null=False,
        help_text=_("People in this team will only be able to submit "
                    "translations files related to the specific language."))
    coordinators = models.ManyToManyField(User, verbose_name=_('Coordinators'), 
        related_name='team_coordinators', blank=False, null=False)
    members = models.ManyToManyField(User, verbose_name=_('Members'),
        related_name='team_members', blank=True, null=True)

    mainlist = models.EmailField(_('Mainlist'), max_length=50, blank=True, 
        null=True, help_text=_("The main mailing list of the team."))

    creator = models.ForeignKey(User, verbose_name=_('creator'), blank=False, 
        null=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    # Managers
    objects = TeamManager()

    def __unicode__(self):
        return u'%s.%s' % (self.project.slug, self.language.code)

    def __repr__(self):
        return '<Team: %s.%s>' % (self.project.slug, self.language.code)

    class Meta:
        unique_together = ("project", "language")
        verbose_name = _('team')
        verbose_name_plural = _('teams')

    @property
    def full_name(self):
        return "team.%s.%s" % (self.project.slug, self.language.code)

log_model(Team)


class TeamRequest(models.Model):
    project = models.ForeignKey(Project, verbose_name=_('Project'),
        blank=False, null=False,
        help_text=_("The project which this team belongs to."))
    language = models.ForeignKey(Language, verbose_name=_('Language'), 
        blank=False, null=False,
        help_text=_("People in this team will only be able to submit "
                    "translations files related to the specific language."))
    user = models.ForeignKey(User, verbose_name=_('User'), 
        blank=False, null=False)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    def __unicode__(self):
        return u'%s.%s' % (self.project.slug, 
            self.language.code)

    def __repr__(self):
        return '<TeamRequest: %s.%s>' % (self.project.slug,
            self.language.code)

    class Meta:
        unique_together = ("project", "language")
        verbose_name = _('team creation request')
        verbose_name_plural = _('team creation requests')

log_model(TeamRequest)


class TeamAccessRequestManager(models.Manager):

    def get_or_none(self, team, user):
        """
        Return a TeamAccessRequest object or None if it doesn't exist.
        """
        try:
            return self.get(team__pk=team.pk, 
                user__pk__exact=user.pk)
        except TeamAccessRequest.DoesNotExist:
            return None

class TeamAccessRequest(models.Model):
    team = models.ForeignKey(Team, verbose_name=_('Team'),
        blank=False, null=False)
    user = models.ForeignKey(User, verbose_name=_('User'), 
        blank=False, null=False)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    objects = TeamAccessRequestManager()

    def __unicode__(self):
        return u'%s.%s' % (self.team, self.user)

    def __repr__(self):
        return '<TeamAccessRequest: %s.%s>' % (self.team, self.user)

    class Meta:
        unique_together = ("team", "user")
        verbose_name = _('team access request')
        verbose_name_plural = _('team access requests')

log_model(TeamAccessRequest)