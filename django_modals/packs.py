"""Which Bootstrap the modals render for, and where the templates for it live.

Modals ships one folder of templates per supported Bootstrap version:

    django_modals/templates/django_modals/bootstrap4/
    django_modals/templates/django_modals/bootstrap5/

``DJANGO_MODALS_TEMPLATE_PACK`` picks between them, defaulting to Bootstrap 4:

    DJANGO_MODALS_TEMPLATE_PACK = 'bootstrap5'

It may instead be a dotted path to a callable taking the request and returning a pack name,
for a project that has to serve both -- the example app uses that to put a version toggle in
its nav bar. A pack name never contains a dot, which is what tells the two apart.

This follows django-cards and django-menus, which do the same thing with the same setting
name pattern. The pack names are also crispy's own template pack names, deliberately: a form
rendered inside a modal goes through crispy, and ``WrapperHelper`` hands this name straight to
``FormHelper.template_pack`` so the two cannot disagree. See ``form_helpers``.

The flat paths stay the public names
------------------------------------
django-menus ships nothing at its flat template paths and resolves ``select_template([flat,
pack])`` so a project override still wins. Modals cannot: projects reference these paths
directly -- ``django_modals/fields/label_checkbox.html`` as a crispy ``FieldEx(template=...)``,
``django_modals/widgets/select2.html`` in an ``{% include %}``, ``django_modals/formset/
table_inline_formset.html`` as a ``helper.template``. So every packed template keeps a file at
its old flat path holding one ``{% pack_source %}`` tag that renders the pack's copy:

    django_modals/fields/label_checkbox.html              {% pack_source 'fields/label_checkbox.html' %}
    django_modals/bootstrap4/fields/label_checkbox.html   the Bootstrap 4 markup
    django_modals/bootstrap5/fields/label_checkbox.html   the Bootstrap 5 markup

A project's own file at the flat path still shadows the forwarder -- the DIRS loader runs
before the app-directories one -- so overrides keep working untouched, and they apply to both
packs. A project that wants to override one version only puts its file at the pack path.

``pack_template`` therefore resolves the pack path alone. Trying the flat path first, the way
menus does, would find the forwarder and recurse.

``modal_base.html`` is not packed
---------------------------------
It is the one template downstream projects ``{% extends %}`` -- jms_cloud alone does it in a
dozen templates -- and a ``{% pack_source %}`` forwarder renders a flattened context, which
would silently drop every ``{% block %}`` override. It does not need packing anyway: its only
Bootstrap-versioned content was ``data-backdrop``/``data-keyboard``, and those are now passed
from ``modals.js`` as constructor options instead, which both versions read the same way.
"""
from django.conf import settings
from django.template.loader import get_template
from django.utils.module_loading import import_string

DEFAULT_PACK = 'bootstrap4'
PACKS = ('bootstrap4', 'bootstrap5')

# The Bootstrap naming that is built in Python rather than written in a template, and so
# cannot live in the pack folder. Everything else a pack varies is in its templates.
PACK_CLASSES = {
    'bootstrap4': {
        # Div wrapper round a label/field pair in a horizontal form (BaseForm.row).
        'form_group_row': 'form-group row',
        # The helper attribute that wraps a form's fields (TwoColumnRegularHelper).
        'fields_wrap': 'form-row',
        # The button row above a multi-form formset.
        'text_end': 'text-right',
        'float_start': 'float-left',
        'float_end': 'float-right',
        # The gap after an inline button or field. Bootstrap 5 renamed the directional spacing
        # utilities from left/right to start/end.
        'margin_end': 'mr-2',
    },
    'bootstrap5': {
        # form-group went entirely in Bootstrap 5; the margin it carried is now a utility.
        'form_group_row': 'row mb-3',
        # form-row went too -- a plain row with Bootstrap 5's own gutters replaces it.
        'fields_wrap': 'row',
        'text_end': 'text-end',
        'float_start': 'float-start',
        'float_end': 'float-end',
        'margin_end': 'me-2',
    },
}

# Bootstrap 5 prefixed its own data attributes with bs-. These are the ones modals writes from
# Python; the ones it writes in a template are spelled in the pack template itself.
PACK_ATTRIBUTES = {
    'bootstrap4': {
        'dismiss': 'data-dismiss',
        'toggle': 'data-toggle',
        'placement': 'data-placement',
    },
    'bootstrap5': {
        'dismiss': 'data-bs-dismiss',
        'toggle': 'data-bs-toggle',
        'placement': 'data-bs-placement',
    },
}


def template_pack(request=None):
    """The pack name for this request, from the setting."""
    configured = getattr(settings, 'DJANGO_MODALS_TEMPLATE_PACK', DEFAULT_PACK)
    if callable(configured):
        return configured(request)
    if '.' in configured:
        return import_string(configured)(request)
    return configured


def pack_class(name, request=None):
    """A Bootstrap class string spelled for this request's pack."""
    pack = template_pack(request)
    return PACK_CLASSES.get(pack, PACK_CLASSES[DEFAULT_PACK])[name]


def pack_attribute(name, request=None):
    """A Bootstrap attribute name spelled for this request's pack."""
    pack = template_pack(request)
    return PACK_ATTRIBUTES.get(pack, PACK_ATTRIBUTES[DEFAULT_PACK])[name]


def pack_template(name, request=None):
    """The pack's copy of ``name``, which is a path below the pack folder.

    Pack-only on purpose: the flat path in front of it is either a project's override or the
    forwarder that calls this, and resolving it here would send the forwarder back to itself.
    """
    return get_template(f'django_modals/{template_pack(request)}/{name}')


def render_pack_template(name, context, request=None):
    return pack_template(name, request).render(context)
