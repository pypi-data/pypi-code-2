from django.http import HttpResponse, HttpResponseNotAllowed,\
    HttpResponseBadRequest, HttpResponseForbidden
from django.conf import settings
from django.views.generic import list_detail, simple
from django.shortcuts import get_object_or_404

from fromagerie.authentication import HttpBasicAuthentication
from fromagerie.models import Package, Release, Classifier
from fromagerie.forms import ReleaseForm, ReleaseUploadForm
from fromagerie.http import HttpResponseUnauthorized,\
    parse_post_and_files, HttpResponseNotImplemented

ACTION_KEY = ':action'
METADATA_VERSION_KEY = 'metadata_version'
PROTOCOL_VERSION_KEY = 'protocol_version'
# distutils actions
DISTUTILS_ACTIONS = 'verify list_classifiers user password_reset submit file_upload'.split()

class SimplePackageIndex(object):
    """
    A simple interface to the index that is distutils compatible.
    """
    authentication_backend = HttpBasicAuthentication()
    mime_type = 'text/plain'
    actions = DISTUTILS_ACTIONS
    
    def is_authenticated(self, request):
        return self.authentication_backend.is_authenticated(request)
    
    def challenge(self, request):
        return self.authentication_backend.challenge(request)

    def get_content_type(self, request, action=None):
        return '%s; encoding=%s' % (self.mime_type, settings.DEFAULT_CHARSET)
    
    def get_not_implemented_response(self, request, action):
        return HttpResponseNotImplemented(action, 
                                          content_type=self.get_content_type(request, action))

    def get_error_response(self, request, action=None, message=None):
        if not message and action:
            message = 'Bad request for action %s' % action
        elif not message:
            message = 'Bad request'
        return HttpResponseBadRequest(message,
                                      content_type=self.get_content_type(request, action))

    def get_forbidden_response(self, request, action=None, message=None):
        if not message:
            message = 'You do not have permission to perform the requested operation'
        return HttpResponseForbidden(message,
                                     content_type=self.get_content_type(request, action))

    def get_success_response(self, request, action=None, message=None):
        if not message and action:
            message = 'Successfully processed request for action %s' % action
        elif not message:
            message = 'Successfully processed request'
        return HttpResponse(message, content_type=self.get_content_type(request, action))

    def dispatch(self, action, request, data, files):
        """
        Pass the request and data off to the appropriate handler.
        """
        try:
            action_callback = getattr(self, action)
        except AttributeError:
            return self.get_not_implemented_response(request, action)
        return action_callback(request, data, files)

    def __call__(self, request):
        """
        Validate action and pass along parsed POST data.
        """
        if request.method == 'POST':
            data, files = parse_post_and_files(request)
        else:
            data, files = request.GET, request.FILES
        action = data.get(ACTION_KEY)
        if not action:
            return self.default(request, data, files)
        elif not action in self.actions:
            return self.get_error_response(request, message='Unrecognized action')
        return self.dispatch(action, request, data, files)

    # Action callbacks

    def default(self, request, data, files):
        """
        A default response generator.
        """
        return self.get_error_response(request)

    def verify(self, request, post_data, files):
        """
        Validate release metadata.
        """
        action = 'verify'
        release_form = ReleaseForm(post_data)
        if not release_form.is_valid():
            return self.get_error_response(request, action, release_form._errors.as_text())
        return self.get_success_response(request, action, 'Metadata is valid')

    def list_classifiers(self, request, data, files):
        """
        Return a list of all known classifiers.
        """
        classifiers = Classifier.objects.values_list('name', flat=True)
        return self.get_success_response(request,
                                         'list_classifiers',
                                         '\n'.join(classifiers) + '\n')

    def user(self, request, post_data, files):
        """
        Register a new user with the index.
        """
        action = 'user'
        try:
            data = {'username': post_data.get('name'),
                    'email': post_data.get('email'),
                    'password1': post_data.get('password'),
                    'password2': post_data.get('confirm')}
            from registration.forms import RegistrationFormUniqueEmail
            registration_form = RegistrationFormUniqueEmail(data)
            if registration_form.is_valid():
                user = registration_form.save()
                return self.get_success_response(request,
                                                 action,
                                                 'An email has been sent giving instructions on how to active the account for %s' % unicode(user))
            return self.get_error_response(request,
                                           action,
                                           registration_form._errors.as_text())
        except ImportError:
            return self.get_not_implemented_response(request, action)

    def password_reset(self, request, data, files):
        """
        Reset an existing user's password.
        """
        # ensure post?
        action = 'password_reset'
        from django.contrib.auth.forms import PasswordResetForm
        password_reset_form = PasswordResetForm(data)
        if password_reset_form.is_valid():
            password_reset_form.save()
            return self.get_success_response(request, action,
                                             'A password reset confirmation email has been sent with further instructions.')
        return self.get_error_response(request, action, password_reset_form._errors.as_text())

    def submit(self, request, post_data, files):
        """
        Register a release with the index.
        """
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
        action = 'submit'
        if not self.is_authenticated(request):
            return self.challenge(request)
        release_form = ReleaseForm(post_data)
        if not release_form.is_valid():
            return self.get_error_response(request, action, release_form._errors.as_text())
        name, version = release_form.cleaned_data['name'], release_form.cleaned_data['version']
        try:
            package = Package.objects.get(name=name)
        except Package.DoesNotExist:
            # Check if user has package creation permissions
            if not request.user.has_perm(Package._meta.app_label + '.' + Package._meta.get_add_permission()):
                return self.get_forbidden_response(request, action,
                                                   'You do not have permission to register new packages')
            package = Package(name=name)
            package.save()
        # Check user has a role for this package
        try:
            release = Release.objects.get(package=package, version=version)
            # We already have this release
            return self.get_error_response(request, action,
                                           '%s already exists' % unicode(release))
        except Release.DoesNotExist:
            release = release_form.save(commit=False)
            release.package = package
            release.save()
            release_form.save_m2m()
        return self.get_success_response(request, action, '%s registered' % unicode(release))

    def file_upload(self, request, post_data, files):
        """
        Upload a distribution file for a release.
        """
        if request.method != 'POST':
            return HttpResponseNotAllowed(['POST'])
        action = 'file_upload'
        if not self.is_authenticated(request):
            return self.challenge(request)
        release_form = ReleaseForm(post_data)
        if not release_form.is_valid():
            return self.get_error_response(request, action, release_form._errors.as_text())
        name, version = release_form.cleaned_data['name'], release_form.cleaned_data['version']
        try:
            release = Release.objects.get(package__name=name, version=version)
        except Release.DoesNotExist:
            # Register?
            return self.get_error_response(request, action,
                                           '%s-%s has not been registered' % (name, version))
        # Check user has a role for this package
        release_upload_form = ReleaseUploadForm(post_data, files, release=release)
        if not release_upload_form.is_valid():
            return self.get_error_response(request, action,
                                           release_upload_form._errors.as_text())
        upload = release_upload_form.save()
        return self.get_success_response(request, action,
                                         'Distribution file successfully registered')


def package_list(request, **kwargs):
    defaults = {
        'template_object_name': 'package',
        'queryset': Package.objects.filter(releases__hidden=False).distinct()
    }
    defaults.update(kwargs)
    return list_detail.object_list(request, **defaults)

def package_overview(request, name=None, template_name='fromagerie/package_overview.html', extra_context=None):
    package = get_object_or_404(Package.objects.filter(releases__hidden=False).distinct(), name=name)
    releases = package.releases.filter(hidden=False)
    context = {'package': package, 'releases': releases}
    if extra_context:
        context.update(extra_context)
    return simple.direct_to_template(request, template_name, extra_context=context)

def release_overview(request, name=None, version=None, template_name='fromagerie/release_overview.html', extra_context=None):
    package = get_object_or_404(Package.objects.filter(releases__hidden=False).distinct(), name=name)
    release = get_object_or_404(package.releases.all(), version=version)
    context = {'package': package, 'release': release}
    if extra_context:
        context.update(extra_context)
    return simple.direct_to_template(request, template_name, extra_context=context)


class EnhancedPackageIndex(SimplePackageIndex):
    def default(self, request, data, files):
        return package_list(request)

