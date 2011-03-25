# -*- coding: utf-8 -*-

import datetime

from django.contrib.auth.models import User, UserManager
from django.core.cache import cache
from django.db import models
from django.utils.translation import ugettext as _

import filter


LOOKUP_CHOICES = (
    (u"L", _(u"Lookup")),
    (u"D", _(u"Detail"))
)

COMMENT_TABLES = (
    ("feld", _(u"Field")),
    ("tabelle", _(u"Table"))
)


def save_user_trigger(sender, instance, **kwds):
    if cache.has_key("user:%d" % instance.id):
        cache.delete("user:%d" % instance.id)
    if cache.has_key("user_popup:%d" % instance.id):
        cache.delete("user_popup:%d" % instance.id)


class Model(models.Model):
    """Base class for all model classes."""

    class Meta:
        abstract = True

    @classmethod
    def get_by_id(cls, id):
        """Returns a query object by it's primary key.

        :param id: Id of the query object
        :returns: Instance of cls or None
        """
        try:
            id = int(id)
        except (ValueError, TypeError):
            return None
        query = cls.objects.filter(id=id)
        if query.count() == 0:
            raise cls.DoesNotExist
        elif query.count() == 1:
            return query[0]
        return query

    def save(self, *args, **kwds):
        """Derived save method to automatically save timestamp values."""
        now = datetime.datetime.now()
        user = kwds.pop('user')
        if not self.id:
            self.created = now
            self.created_by = user
        self.updated = now
        self.updated_by = user
        super(Model, self).save(*args, **kwds)


class DefaultInfo(models.Model):
    """Base class for all models in this module.

    This base class provides default fields that should be used by all
    models in this module.
    """

    created_by = models.IntegerField(blank=True, null=True, editable=False)  # references User
    updated_by = models.IntegerField(blank=True, null=True, editable=False) # references User
    created = models.DateTimeField(auto_now_add=True, db_column="crdate")
    updated = models.DateTimeField(auto_now=True, db_column="upddate")

    class Meta:
        abstract = True


class Account(User):
    """Extends the django default user."""

    starred_fields = []
    starred_tables = []

    class Meta:
        proxy = True

    @classmethod
    def get_account_for_user(cls, user):
        assert user.email
        query = Account.objects.filter(email=user.email)
        account = tuple(query)[0] or None
        if account is not None:
            return account

    @property
    def nickname(self):
        if self.first_name and self.last_name:
            return u"%s %s" % (self.first_name, self.last_name)
        else:
            return self.username

    @property
    def num_comments(self):
        num = 0L
        comments = TableComment.objects.filter(created_by=self.id)
        comments = comments.filter(is_draft=False)
        num += comments.count()
        comments = FieldComment.objects.filter(created_by=self.id)
        comments = comments.filter(is_draft=False)
        num += comments.count()
        return num

    @property
    def num_tables(self):
        tables = Table.objects.filter(created_by=self.id)
        return tables.count()


models.signals.post_save.connect(save_user_trigger, sender=User)


class Project(Model):

    id = models.AutoField(primary_key=True, db_column="pr_id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=80, db_column="pr_name", null=False,
                            blank=False, verbose_name=_(u"Name"))
    short_description = models.CharField(max_length=40,
                                         db_column="pr_zuname", null=True,
                                         blank=True,
                                         verbose_name=_(u"Short description"))
    description = models.CharField(max_length=256, db_column="pr_txt",
                                   null=True, blank=True,
                                   verbose_name=_(u"Description"))
    created_by = models.ForeignKey(User, db_column="pr_crid",
                                   null=True, related_name="project_creators",
                                   verbose_name=_(u"Created by"))
    created = models.DateTimeField(db_column="pr_crdate",
                                   verbose_name=_(u"Created"))
    updated_by = models.ForeignKey(User, db_column="pr_updid",
                                   null=True, related_name="account_updators",
                                   verbose_name=_(u"Updated by"))
    updated = models.DateTimeField(db_column="pr_upddate",
                                   verbose_name=_(u"Updated"))

    class Meta:
        db_table = u"projekt"
        ordering = ("name",)
        verbose_name = _(u"Project")
        verbose_name_plural = _(u"Projects")

    def __unicode__(self):
        return self.name

    def count_tables(self):
        return Table.objects.filter(project=self.id).count()


class Table(Model):

    id = models.AutoField(primary_key=True, db_column="ta_id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=30, db_column="ta_name", null=False,
                            blank=False, verbose_name=_(u"Name"))
    prefix = models.CharField(max_length=3, db_column="ta_prae", null=True,
                              blank=True, verbose_name=_(u"Prefix"))
    type = models.ForeignKey("TableType", db_column="ta_ttid", null=False,
                             blank=False, verbose_name=_(u"Type"))
    short_description = models.CharField(max_length=40,
                                         db_column="ta_zuname", null=True,
                                         blank=True,
                                         verbose_name=_(u"Short description"))
    description = models.CharField(max_length=2000, db_column="ta_txt",
                                   null=True, blank=True,
                                   verbose_name=_(u"Description"))
    project = models.ForeignKey("Project", db_column="ta_prid", null=False,
                                blank=False, verbose_name=_(u"Project"))
    first_extension = models.IntegerField(db_column="ta_fext", null=True,
                                          blank=True,
                                          verbose_name=_(u"First extension"))
    next_extension = models.IntegerField(db_column="ta_next", null=True,
                                         blank=True,
                                         verbose_name=_(u"Next extension"))
    db_space = models.IntegerField(db_column="ta_dbspc", null=True,
                                   blank=True,
                                   verbose_name=_(u"Database space"))
    lock_mode = models.CharField(max_length=1, db_column="ta_lckmode",
                                 null=True, blank=True,
                                 verbose_name=_(u"Lockmode"))
    storage_clause = models.CharField(max_length=4000, db_column="ta_stclause",
                                      null=True, blank=True,
                                      verbose_name=_(u"Storage clause"))
    created_by = models.ForeignKey(User, db_column="ta_crid",
                                   null=True, related_name="table_creators",
                                   verbose_name=_(u"Created by"))
    created = models.DateTimeField(db_column="ta_crdate",
                                   verbose_name=_(u"Created"))
    updated_by = models.ForeignKey(User, db_column="ta_updid",
                                   null=True, related_name="table_updators",
                                   verbose_name=_(u"Updated by"))
    updated = models.DateTimeField(db_column="ta_upddate",
                                   verbose_name=_(u"Updated"))

    #project.project_filter = True

    _is_starred = None

    class Meta:
        db_table = u"tabelle"
        ordering = ("name",)
        verbose_name = _(u"Table")
        verbose_name_plural = _(u"Tables")

    def __unicode__(self):
        return self.name

    @property
    def foreign_keys(self):
        fields = Field.objects.filter(table=self.id)
        fields = fields.filter(foreign__isnull=False)
        fields = fields.order_by("position")
        return fields

    @property
    def is_starred(self):
        """Whether the current user has this booking starred."""
        if self._is_starred is not None:
            return self._is_starred
        account = Account.current_user_account
        self._is_starred = account is not None and self.id in account.starred_tables
        return self._is_starred

    def count_comments(self):
        comments = TableComment.objects.select_related()
        return comments.filter(table=self, is_draft=False).count()
        #return TableComment.objects.filter(table=self, is_draft=False).count()

    def count_drafts(self):
        account = Account.current_user_account
        if account is None:
            return 0
        else:
            drafts = TableComment.objects.filter(table=self)
            drafts = drafts.filter(created_by=account)
            drafts = drafts.filter(is_draft=True)
            return drafts.count()

    def count_fields(self):
        return Field.objects.filter(table=self.id).count()

    def get_fields(self, ordered=True):
        query = Field.objects.filter(table=self.id)
        if ordered:
            query = query.order_by("position")
        return query


class TableType(Model):

    id = models.AutoField(primary_key=True, db_column="tt_id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=15, db_column="tt_name", null=False,
                            blank=False, unique=True,
                            verbose_name=_(u"Name"))
    short_name = models.CharField(max_length=15, db_column="tt_short_name",
                                  null=False, blank=False, unique=True,
                                  verbose_name=_(u"Short name"))

    class Meta:
        db_table = u"tabellentyp"
        ordering = ("name",)
        verbose_name = _(u"Tabletype")
        verbose_name_plural = _(u"Tabletypes")

    def __unicode__(self):
        return self.name


class Field(Model):

    _is_starred = None
    _n_comments = None
    _n_drafts = None

    id = models.AutoField(primary_key=True, db_column="fe_id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=60, db_column="fe_name", null=False,
                            blank=False, verbose_name=_(u"Name"))
    position = models.IntegerField(db_column="fe_pos", null=True, blank=True,
                                   verbose_name=_(u"Position"))
    short_description = models.CharField(max_length=60, db_column="fe_zuname",
                                         null=False, blank=False,
                                         verbose_name=_(u"Short description"))
    description = models.CharField(max_length=2000, db_column="fe_txt",
                                   null=True, blank=True,
                                   verbose_name=_(u"Description"))
    label = models.CharField(max_length=60, db_column="fe_label", null=False,
                             blank=False, verbose_name=_(u"Label"))
    type = models.ForeignKey("FieldType", db_column="fe_ftid", null=False,
                             blank=False, verbose_name=_(u"Type"))
    precision = models.CharField(max_length=12, db_column="fe_zus1",
                                 null=True, blank=True,
                                 verbose_name=_(u"Precision"))
    scaling = models.CharField(max_length=12, db_column="fe_zus2",
                               null=True, blank=True,
                               verbose_name=_(u"Scaling"))
    primary = models.BooleanField(db_column="fe_prim", null=False, blank=False,
                                  verbose_name=_(u"Primary"))
    foreign = models.ForeignKey("Field", db_column="fe_fremd",
                                null=True, blank=True,
                                verbose_name=_(u"Foreign key"))
    lookup = models.CharField(max_length=2, db_column="fe_look",
                              null=True, blank=True, choices=LOOKUP_CHOICES,
                              verbose_name=_(u"Lookup"))
    nullable = models.BooleanField(db_column="fe_null", null=False,
                                   blank=False,
                                   verbose_name=_(u"Nullable"))
    mask_length = models.IntegerField(db_column="fe_mlang", null=False,
                                      blank=False, default=0,
                                      verbose_name=_(u"Mask length"))
    default_value = models.CharField(max_length=32, db_column="fe_default",
                                     null=True, blank=True,
                                     verbose_name=_(u"Default value"))
    cascading_delete = models.BooleanField(db_column="fe_loesch",
                                           default=False,
                                           verbose_name=_(u"Cascading delete"))
    table = models.ForeignKey("Table", db_column="fe_taid", null=False,
                              blank=False, related_name="fields",
                              verbose_name=_(u"Table"))
    created_by = models.ForeignKey(User, db_column="ta_crid",
                                   null=True, related_name="field_creators",
                                   verbose_name=_(u"Created by"))
    created = models.DateTimeField(db_column="fe_crdate",
                                   verbose_name=_(u"Created"))
    updated_by = models.ForeignKey(User, db_column="fe_updid",
                                   null=True, related_name="field_updators",
                                   verbose_name=_(u"Updated by"))
    updated = models.DateTimeField(db_column="fe_upddate",
                                   verbose_name=_(u"Updated"))


    class Meta:
        db_table = u"feld"
        ordering = ("position",)
        verbose_name = _(u"Field")
        verbose_name_plural = _(u"Fields")

    def __unicode__(self):
        return self.name

    def _get_num_comments(self, drafts_only=False):
        return FieldComment.objects.filter(
            field=self, is_draft=drafts_only).count()

    @property
    def is_starred(self):
        """Whether the current user has this field starred."""
        if self._is_starred is not None:
            return self._is_starred
        account = Account.current_user_account
        self._is_starred = account is not None and self.id in account.starred_fields
        return self._is_starred

    @property
    def num_comments(self):
        if self._n_comments is None:
            self._n_comments = self._get_num_comments()
        return self._n_comments

    @property
    def num_drafts(self):
        if self._n_drafts is None:
            self._n_drafts = self._get_num_comments(drafts_only=True)
        return self._n_drafts

    def count_drafts(self):
        account = Account.current_user_account
        if account is None:
            return 0
        else:
            drafts = FieldComment.objects.filter(field=self,
                                                 created_by=account,
                                                 is_draft=True)
            return drafts.count()

    def full_name(self):
        if self.table.prefix:
            return "%s_%s" % (self.table.prefix, self.name)
        else:
            return self.name

    def full_type(self):
        retval = "%s" % self.type
        if self.precision and self.scaling:
            retval += " (%s, %s)" % (self.precision, self.scaling)
        elif self.precision and not self.scaling:
            retval += " (%s)" % self.precision
        return retval

    def get_comments_by_date(self):
        return FieldComment.objects.filter(field=self,
                                           is_draft=False).order_by("created")

    def set_next_position(self, table=None):
        if not table:
            table = self.table
        fields = Field.objects.filter(table=table)
        max = fields.aggregate(models.Max("position"))["position__max"] or 0
        self.position = max + 1


class FieldProperty(Model):

    id = models.AutoField(primary_key=True, db_column="fei_id",
                          verbose_name=_(u"Id"))
    position = models.IntegerField(db_column="fei_pos", null=False,
                                   verbose_name=_(u"Position"))
    property = models.ForeignKey("Property", db_column="fei_etid", null=False,
                                 blank=False,
                                 verbose_name=_(u"Property"))
    field = models.ForeignKey("Field", db_column="fei_feid", null=False,
                              blank=False,
                              verbose_name=_(u"Field"))
    value = models.CharField(max_length=256, db_column="fei_wert",
                             verbose_name=_(u"Value"))
    created_by = models.ForeignKey(User, db_column="fei_crid",
                                   null=True,
                                   related_name="field_property_creators",
                                   verbose_name=_(u"Created by"))
    created = models.DateTimeField(db_column="fei_crdate",
                                   verbose_name=_(u"Created"))
    updated_by = models.ForeignKey(User, db_column="fei_updid",
                                   null=True,
                                   related_name="field_property_updators",
                                   verbose_name=_(u"Updated by"))
    updated = models.DateTimeField(db_column="fei_upddate",
                                   verbose_name=_(u"Updated"))

    class Meta:
        db_table = u"feldeigenschaft"
        verbose_name = _(u"Field property")
        verbose_name_plural = _(u"Field properties")


class FieldType(Model):

    id = models.AutoField(primary_key=True, db_column="ft_id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=15, db_column="ft_name", null=False,
                            blank=False, unique=True,
                            verbose_name=_(u"Name"))
    short_name = models.CharField(max_length=15, db_column="ft_short_name",
                                  null=False, blank=False, unique=True,
                                  verbose_name=_(u"Short name"))
    precision = models.CharField(max_length=1, db_column="ft_zus1", null=False,
                                 blank=False,
                                 verbose_name=_(u"Precision"))
    scaling = models.CharField(max_length=1, db_column="ft_zus2", null=False,
                               blank=False,
                               verbose_name=_(u"Scaling"))

    class Meta:
        db_table = u"feldtyp"
        ordering = ("name",)
        verbose_name = _(u"Fieldtype")
        verbose_name_plural = _(u"Fieldtypes")

    def __unicode__(self):
        return self.name


class Group(Model):

    id = models.AutoField(primary_key=True, db_column="gr_id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=60, db_column="gr_name", blank=False,
                            null=False, verbose_name=_(u"Name"))
    created_by = models.ForeignKey(User, db_column="gr_crid",
                                   null=True, related_name="group_creators",
                                   verbose_name=_(u"Created by"))
    created = models.DateTimeField(db_column="gr_crdate",
                                   verbose_name=_(u"Created"))
    updated_by = models.ForeignKey(User, db_column="gr_updid",
                                   null=True, related_name="group_updators",
                                   verbose_name=_(u"Updated by"))
    updated = models.DateTimeField(db_column="gr_upddate",
                                   verbose_name=_(u"Updated"))

    class Meta:
        db_table = u"gruppe"
        ordering = ("name",)
        verbose_name = _(u"Group")
        verbose_name_plural = _(u"Groups")

    def __unicode__(self):
        return self.name


class Property(Model):

    id = models.AutoField(primary_key=True, db_column="et_id",
                          verbose_name=_(u"Id"))
    name = models.CharField(max_length=60, db_column="et_bez", blank=False,
                            null=False, verbose_name=_(u"Name"))
    created_by = models.ForeignKey(User, db_column="et_crid",
                                   null=True, related_name="property_creators",
                                   verbose_name=_(u"Created by"))
    created = models.DateTimeField(db_column="et_crdate",
                                   verbose_name=_(u"Created"))
    updated_by = models.ForeignKey(User, db_column="et_updid",
                                   null=True, related_name="property_updators",
                                   verbose_name=_(u"Updated by"))
    updated = models.DateTimeField(db_column="et_upddate",
                                   verbose_name=_(u"Updated"))


    class Meta:
        db_table = u"eigenschafttyp"
        ordering = ("name",)
        verbose_name = _(u"Property")
        verbose_name_plural = _(u"Properties")

    def __unicode__(self):
        return self.name


class TableGroup(Model):

    id = models.AutoField(primary_key=True, db_column="tg_id",
                          verbose_name=_(u"Id"))
    table = models.ForeignKey("Table", db_column="tg_taid", blank=False,
                              null=False, verbose_name=_(u"Table"))
    group = models.ForeignKey("Group", db_column="tg_grid", blank=False,
                              null=False, verbose_name=_(u"Group"))
    created_by = models.ForeignKey(User, db_column="tg_crid",
                                   null=True,
                                   related_name="tablegroup_creators",
                                   verbose_name=_(u"Created by"))
    created = models.DateTimeField(db_column="tg_crdate",
                                   verbose_name=_(u"Created"))
    updated_by = models.ForeignKey(User, db_column="tg_updid",
                                   null=True,
                                   related_name="tablegroup_updators",
                                   verbose_name=_(u"Updated by"))
    updated = models.DateTimeField(db_column="tg_upddate",
                                   verbose_name=_(u"Updated"))

    class Meta:
        db_table = u"tabgruppe"
        verbose_name = _(u"Table group")
        verbose_name_plural = _(u"Table groups")


class Key(Model):

    id = models.AutoField(primary_key=True, db_column="sc_id",
                          verbose_name=_(u"Id"))
    unique = models.BooleanField(db_column="sc_uni", default=False,
                                 verbose_name=_(u"Unique"))
    table = models.ForeignKey("Table", db_column="sc_taid",
                              verbose_name=_(u"Table"))
    name = models.CharField(max_length=255, db_column="sc_name",
                            verbose_name=_(u"Name"))
    created_by = models.ForeignKey(User, db_column="sc_crid",
                                   null=True, related_name="key_creators",
                                   verbose_name=_(u"Created by"))
    created = models.DateTimeField(db_column="sc_crdate",
                                   verbose_name=_(u"Created"))
    updated_by = models.ForeignKey(User, db_column="sc_updid",
                                   null=True, related_name="key_updators",
                                   verbose_name=_(u"Updated by"))
    updated = models.DateTimeField(db_column="sc_upddate",
                                   verbose_name=_(u"Updated"))

    class Meta:
        db_table = u"schluess"
        ordering = ("name",)
        verbose_name = _(u"Key")
        verbose_name_plural = _(u"Keys")

    def __unicode__(self):
        return self.name


class FieldKey(Model):

    id = models.AutoField(primary_key=True, db_column="fs_id",
                          verbose_name=_(u"Id"))
    field = models.ForeignKey("Field", db_column="fs_feid", null=False,
                              blank=False, verbose_name=_(u"Field"))
    key = models.ForeignKey("Key", db_column="fs_scid", null=False,
                            blank=False, verbose_name=_(u"Key"))
    position = models.IntegerField(db_column="fs_pos", null=False, blank=False,
                                   verbose_name=_(u"Position"))
    created_by = models.ForeignKey(User, db_column="fs_crid",
                                   null=True, related_name="field_key_creators",
                                   verbose_name=_(u"Created by"))
    created = models.DateTimeField(db_column="fs_crdate",
                                   verbose_name=_(u"Created"))
    updated_by = models.ForeignKey(User, db_column="fs_updid",
                                   null=True, related_name="field_key_updators",
                                   verbose_name=_(u"Updated by"))
    updated = models.DateTimeField(db_column="fs_upddate",
                                   verbose_name=_(u"Updated"))

    class Meta:
        db_table = u"feldschl"
        verbose_name = _(u"Field key")
        verbose_name_plural = _(u"Field keys")


class DefaultField(Model):

    id = models.AutoField(primary_key=True, db_column="sf_id",
                          verbose_name=_(u"Id"))
    project = models.ForeignKey("Project", db_column="sf_prid", null=False,
                                blank=False, verbose_name=_(u"Project"))
    name = models.CharField(max_length=60, db_column="sf_name", null=False,
                            blank=False, verbose_name=_(u"Name"))
    position = models.IntegerField(db_column="sf_pos", null=True, blank=True,
                                   verbose_name=_(u"Position"))
    short_description = models.CharField(max_length=60, db_column="sf_zuname",
                                         null=False, blank=False,
                                         verbose_name=_(u"Short description"))
    description = models.CharField(max_length=2000, db_column="sf_txt",
                                   null=True, blank=True,
                                   verbose_name=_(u"Description"))
    label = models.CharField(max_length=60, db_column="sf_label", null=False,
                             blank=False, verbose_name=_(u"Label"))
    type = models.ForeignKey("FieldType", db_column="sf_ftid", null=False,
                             blank=False, verbose_name=_(u"Type"))
    precision = models.CharField(max_length=12, db_column="sf_zus1",
                                 null=True, blank=True,
                                 verbose_name=_(u"Precision"))
    scaling = models.CharField(max_length=12, db_column="sf_zus2",
                               null=True, blank=True,
                               verbose_name=_(u"Scaling"))
    primary = models.BooleanField(db_column="sf_prim", null=False, blank=False,
                                  verbose_name=_(u"Primary"))
    foreign = models.ForeignKey("Field", db_column="sf_fremd",
                                null=True, blank=True,
                                verbose_name=_(u"Foreign key"))
    lookup = models.CharField(max_length=2, db_column="sf_look",
                              null=True, blank=True, choices=LOOKUP_CHOICES,
                              verbose_name=_(u"Lookup"))
    nullable = models.BooleanField(db_column="sf_null", null=False,
                                   blank=False,
                                   verbose_name=_(u"Nullable"))
    mask_length = models.IntegerField(db_column="sf_mlang", null=False,
                                      blank=False, default=0,
                                      verbose_name=_(u"Mask length"))
    default_value = models.CharField(max_length=32, db_column="sf_default",
                                     null=True, blank=True,
                                     verbose_name=_(u"Default value"))
    cascading_delete = models.BooleanField(db_column="sf_loesch",
                                           default=False,
                                           verbose_name=_(u"Cascading delete"))
    created_by = models.ForeignKey(User, db_column="ta_crid",
                                   null=True,
                                   related_name="default_field_creators",
                                   verbose_name=_(u"Created by"))
    created = models.DateTimeField(db_column="sf_crdate",
                                   verbose_name=_(u"Created"))
    updated_by = models.ForeignKey(User, db_column="sf_updid",
                                   null=True,
                                   related_name="default_field_updators",
                                   verbose_name=_(u"Updated by"))
    updated = models.DateTimeField(db_column="sf_upddate",
                                   verbose_name=_(u"Updated"))

    class Meta:
        db_table = u"standardfeld"
        verbose_name = _(u"Default field")
        verbose_name_plural = _(u"Default fields")

    def __unicode__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def full_name(self):
        if self.table.prefix:
            return "%s_%s" % (self.table.prefix, self.name)
        else:
            return self.name

    def full_type(self):
        retval = "%s" % self.type
        if self.precision and self.scaling:
            retval += " (%s, %s)" % (self.precision, self.scaling)
        elif self.precision and not self.scaling:
            retval += " (%s)" % self.precision
        return retval


class TableComment(Model):

    id = models.AutoField(primary_key=True, db_column="tk_id",
                          verbose_name=_(u"Id"))
    table = models.ForeignKey(Table, db_column="tk_taid",
                              null=False, blank=False,
                              verbose_name=_(u"Table"))
    text = models.CharField(max_length=2000, db_column="tk_txt",
                            verbose_name=_(u"Text"))
    is_draft = models.BooleanField(db_column="tk_entwurf",
                                   verbose_name=_(u"Is draft"))
    created_by = models.ForeignKey(User, db_column="tk_crid",
                                   null=True,
                                   related_name="table_comment_creators",
                                   verbose_name=_(u"Created by"))
    created = models.DateTimeField(db_column="tk_crdate",
                                   verbose_name=_(u"Created"))
    updated_by = models.ForeignKey(User, db_column="tk_updid",
                                   null=True,
                                   related_name="table_comment_updators",
                                   verbose_name=_(u"Updated by"))
    updated = models.DateTimeField(db_column="tk_upddate",
                                   verbose_name=_(u"Updated"))

    class Meta:
        db_table = u"tabellekommentar"
        ordering = ("-created",)
        verbose_name = _(u"Table comment")
        verbose_name_plural = _(u"Table comments")


class FieldComment(Model):

    id = models.AutoField(primary_key=True, db_column="fk_id",
                          verbose_name=_(u"Id"))
    field = models.ForeignKey(Field, db_column="fk_feid",
                              null=False, blank=False,
                              verbose_name=_(u"Field"))
    text = models.CharField(max_length=2000, db_column="fk_txt",
                            verbose_name=_(u"Text"))
    is_draft = models.BooleanField(db_column="fk_entwurf",
                                   verbose_name=_(u"Is draft"))
    created_by = models.ForeignKey(User, db_column="fk_crid",
                                   null=True,
                                   related_name="field_comment_creators",
                                   verbose_name=_(u"Created by"))
    created = models.DateTimeField(db_column="fk_crdate",
                                   verbose_name=_(u"Created"))
    updated_by = models.ForeignKey(User, db_column="fk_updid",
                                   null=True,
                                   related_name="field_comment_updators",
                                   verbose_name=_(u"Updated by"))
    updated = models.DateTimeField(db_column="fk_upddate",
                                   verbose_name=_(u"Updated"))

    class Meta:
        db_table = u"feldkommentar"
        ordering = ("-created",)
        verbose_name = _(u"Field comment")
        verbose_name_plural = _(u"Field comments")
