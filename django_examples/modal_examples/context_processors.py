import os

from django.conf import settings

SESSION_KEY = 'modal_example_bootstrap'
SUPPORTED = ('4', '5')


def template_pack_for_request(request):
    """The django_modals template pack this request should render with.

    Pointed at by DJANGO_MODALS_TEMPLATE_PACK in settings. A project that serves one Bootstrap
    version just names the pack there; the example app serves both, so it resolves per request
    from the same session key the nav bar toggle writes.
    """
    return f'bootstrap{_version_for(request)}'


def _version_for(request):
    version = None
    if request is not None and hasattr(request, 'session'):
        version = request.session.get(SESSION_KEY)
    if version not in SUPPORTED:
        version = getattr(settings, 'MODALS_EXAMPLE_BOOTSTRAP', None)
    if version is None:
        version = os.environ.get('MODALS_EXAMPLE_BOOTSTRAP', '4')
    version = str(version)
    return version if version in SUPPORTED else '4'


def bootstrap_version(request):
    """Which Bootstrap the example app should load, and the link that flips it.

    django-modals ships a template pack per Bootstrap version. That is only worth anything if
    someone can look at both, and the useful way to look is to flip back and forth on the page
    in front of you rather than restart the server. So the choice lives in the session, and
    `?bootstrap=5` on any URL sets it:

        http://localhost:8000/?bootstrap=5

    The nav bar carries a toggle that does exactly that. `MODALS_EXAMPLE_BOOTSTRAP=5` in the
    environment, or in settings, still sets where a fresh session starts.

    The same session key drives both halves: this processor picks which Bootstrap the page
    loads, and template_pack_for_request above picks which pack the modals render from.

    Bootstrap 4 stays the default, because that is what the rest of the stack -- django-menus
    on main, show_src_code, django_datatables -- still emits. Under 5 the modals are correct
    and some of those libraries' markup is not, which is the point of having the switch: it
    shows what is left to do.
    """
    requested = request.GET.get('bootstrap')
    if requested in SUPPORTED and hasattr(request, 'session'):
        request.session[SESSION_KEY] = requested

    version = _version_for(request)
    other = '5' if version == '4' else '4'
    # Keep whatever else is on the URL, so the toggle does not drop a page's own query string.
    params = request.GET.copy()
    params['bootstrap'] = other
    return {
        'bootstrap_version': version,
        'bootstrap_other_version': other,
        'bootstrap_toggle_url': f'{request.path}?{params.urlencode()}',
    }
