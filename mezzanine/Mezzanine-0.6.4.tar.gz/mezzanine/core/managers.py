
from datetime import datetime
from operator import ior, iand
from string import punctuation

from django.db.models import Manager, Q, CharField, TextField, get_models
from django.db.models.query import QuerySet

from mezzanine.settings import CONTENT_STATUS_PUBLISHED, STOP_WORDS


class PublishedManager(Manager):
    """
    Provides filter for restricting items returned by status and publish date
    when the given user is not a staff member.
    """

    def published(self, for_user=None):
        if for_user is not None and for_user.is_staff:
            return self.all()
        return self.filter( 
            Q(publish_date__lte=datetime.now()) | Q(publish_date__isnull=True), 
            Q(expiry_date__gte=datetime.now()) | Q(expiry_date__isnull=True),
            Q(status=CONTENT_STATUS_PUBLISHED))

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)


class KeywordManager(Manager):
    """
    Provides natural key method.
    """
    def get_by_natural_key(self, value):
        return self.get(value=value)


class SearchableQuerySet(QuerySet):
    """
    QuerySet providing main search functionality for ``SearchableManager``.
    """

    def __init__(self, *args, **kwargs):
        self._search_ordered = False
        self._search_terms = set()
        self._search_fields = kwargs.pop("search_fields", {})
        super(SearchableQuerySet, self).__init__(*args, **kwargs)

    def search(self, query, search_fields=None):
        """
        Build a queryset matching words in the given search query, treating
        quoted terms as exact phrases and taking into account + and - symbols
        as modifiers controlling which terms to require and exclude.
        """

        #### DETERMINE FIELDS TO SEARCH ###
        # Use fields arg if given, otherwise check internal list which if
        # empty, populate from model attr or char-like fields.
        if search_fields is None:
            search_fields = self._search_fields
        if len(search_fields) == 0:
            search_fields = getattr(self.model, "search_fields", [])
        if len(search_fields) == 0:
            search_fields = [f.name for f in self.model._meta.fields
                if issubclass(f.__class__, CharField) or
                issubclass(f.__class__, TextField)]
        if len(search_fields) == 0:
            return self.none()
        # Search fields can be a dict or sequence of pairs mapping fields to
        # their relevant weight in ordering the results. If a mapping isn't
        # used then assume a sequence of field names and give them equal
        # weighting.
        try:
            search_fields = dict(search_fields)
            int(search_fields.values()[0])
        except (TypeError, ValueError):
            search_fields = dict(zip(search_fields, [1] * len(search_fields)))
        if not isinstance(self._search_fields, dict):
            self._search_fields = {}
        self._search_fields.update(search_fields)

        #### BUILD LIST OF TERMS TO SEARCH FOR ###
        # Remove extra spaces, put modifiers inside quoted terms.
        terms = " ".join(query.split()).replace("+ ", "+")      \
                                        .replace('+"', '"+')    \
                                        .replace("- ", "-")     \
                                        .replace('-"', '"-')    \
                                        .split('"')
        # Strip punctuation other than modifiers from terms and create terms
        # list - first from quoted terms and then remaining words.
        terms = [("" if t[0] not in "+-" else t[0]) + t.strip(punctuation)
            for t in terms[1::2] + "".join(terms[::2]).split()]
        # Remove stop words from terms that aren't quoted or use modifiers,
        # since words with these are an explicit part of the search query. If
        # doing so ends up with an empty term list, then keep the stop words.
        terms_no_stopwords = [t for t in terms if t.lower() not in STOP_WORDS]
        get_positive_terms = lambda terms: [t.lower().strip(punctuation)
            for t in terms if t[0] != "-"]
        positive_terms = get_positive_terms(terms_no_stopwords)
        if positive_terms:
            terms = terms_no_stopwords
        else:
            positive_terms = get_positive_terms(terms)
        # Append positive terms (those without the negative modifier) to the
        # internal list for sorting when results are iterated.
        if not positive_terms:
            return self.none()
        else:
            self._search_terms.update(positive_terms)

        #### BUILD QUERYSET FILTER ###
        # Create the queryset combining each set of terms.
        excluded = [reduce(iand, [~Q(**{"%s__icontains" % f: t[1:]}) for f in
            search_fields.keys()]) for t in terms if t[0] == "-"]
        required = [reduce(ior, [Q(**{"%s__icontains" % f: t[1:]}) for f in
            search_fields.keys()]) for t in terms if t[0] == "+"]
        optional = [reduce(ior, [Q(**{"%s__icontains" % f: t}) for f in
            search_fields.keys()]) for t in terms if t[0] not in "+-"]
        queryset = self
        if excluded:
            queryset = queryset.filter(reduce(iand, excluded))
        if required:
            queryset = queryset.filter(reduce(iand, required))
        # Optional terms aren't relevant to the filter if there are terms
        # that are explicitly required
        elif optional:
            queryset = queryset.filter(reduce(ior, optional))
        return queryset

    def _clone(self, *args, **kwargs):
        """
        Ensure attributes are copied to subsequent queries.
        """
        for attr in ("_search_terms", "_search_fields", "_search_ordered"):
            kwargs[attr] = getattr(self, attr)
        return super(SearchableQuerySet, self)._clone(*args, **kwargs)

    def order_by(self, *field_names):
        """
        Mark the filter as being ordered if search has occurred.
        """
        if not self._search_ordered:
            self._search_ordered = len(self._search_terms) > 0
        return super(SearchableQuerySet, self).order_by(*field_names)

    def iterator(self):
        """
        If search has occured and no ordering has occurred, decorate each
        result with the number of search terms so that it can be sorted by
        the number of occurrence of terms.
        """
        results = super(SearchableQuerySet, self).iterator()
        if self._search_terms and not self._search_ordered:
            results = list(results)
            for i, result in enumerate(results):
                count = 0
                for (field, weight) in self._search_fields.items():
                    for term in self._search_terms:
                        field_value = getattr(result, field)
                        if field_value:
                            count += field_value.lower().count(term) * weight
                results[i].result_count = count
            return iter(results)
        return results


class SearchableManager(Manager):
    """
    Manager providing a chainable queryset.
    Adapted from http://www.djangosnippets.org/snippets/562/
    search method supports spanning across models that subclass the model
    being used to search.
    """

    def __init__(self, *args, **kwargs):
        self._search_fields = kwargs.pop("search_fields", [])
        super(SearchableManager, self).__init__(*args, **kwargs)

    def get_query_set(self):
        search_fields = self._search_fields
        return SearchableQuerySet(self.model, search_fields=search_fields)

    def search(self, *args, **kwargs):
        """
        Proxy to queryset's search method for the manager's model and any
        models that subclass from this manager's model if the model is
        abstract.
        """
        all_results = []
        if getattr(self.model._meta, "abstract", False):
            models = [m for m in get_models() if issubclass(m, self.model)]
        else:
            models = [self.model]
        for model in models:
            results = model.objects.get_query_set().search(*args, **kwargs)
            all_results.extend(results)
        sort_key = lambda r: r.result_count
        return sorted(all_results, key=sort_key, reverse=True)


class DisplayableManager(PublishedManager, SearchableManager):
    """
    Combined manager for the ``Displayable`` model.
    """
    pass
