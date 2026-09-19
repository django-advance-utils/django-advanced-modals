[![PyPI version](https://badge.fury.io/py/django-nested-modals.svg)](https://badge.fury.io/py/django-nested-modals)

Add to installed apps in settings   
`'bootstrap_modals',`
    

Add to template
  
    <script src="{% static 'django_modals/js/modals.js' %}"></script>
    <link rel="stylesheet" type="text/css" href="{% static 'django_modals/css/modals.css' %}"/>

####See django_examples for example usage

 

## Bootstrap 4 or Bootstrap 5

django-modals ships one template pack per Bootstrap version and defaults to Bootstrap 4, so
an existing project picks up this release with no change at all. To render for Bootstrap 5:

    DJANGO_MODALS_TEMPLATE_PACK = 'bootstrap5'

The setting may instead be a dotted path to a callable taking the request and returning a pack
name, for a project that has to serve both — that is what the example app does to put a version
toggle in its nav bar. A pack name never contains a dot, which is what tells the two apart.

### What else Bootstrap 5 needs

Forms still go through crispy-forms, and crispy's Bootstrap 5 pack is a separate package:

    pip install crispy-bootstrap5

    INSTALLED_APPS = [..., 'crispy_forms', 'crispy_bootstrap5']

    # crispy 1.14's own allowed list stops at bootstrap4 and it raises on anything outside it.
    CRISPY_ALLOWED_TEMPLATE_PACKS = ('bootstrap', 'uni_form', 'bootstrap3', 'bootstrap4', 'bootstrap5')

`CRISPY_TEMPLATE_PACK` itself does not have to change: django-modals sets `template_pack` on
every helper it builds, so crispy follows `DJANGO_MODALS_TEMPLATE_PACK` per form. That is
deliberate — without it a project could get Bootstrap 5 field markup wrapped in Bootstrap 4
layout markup, and nothing would say so.

Bootstrap 5 itself is not loaded for you unless a django-modals template builds the whole page.
`django_modals.includes.Bootstrap5` is there if you want it (ajax_helpers still pins 4.6.0):

    {% lib_include 'ajax_helpers' 'FontAwesome' module='ajax_helpers.includes' %}
    {% lib_include 'Bootstrap5' 'Modals' 'Toggle5' 'select2' module='django_modals.includes' %}

Load it **after** the `ajax_helpers` group. modals.js is written against Bootstrap's jQuery
plugin interface, and Bootstrap 5 only registers that interface — and only keeps firing jQuery
events beside its native ones — when jQuery is already on the page.

Use `Toggle5` in place of `Toggle`: bootstrap5-toggle keeps the same `bootstrapToggle()` plugin
but marks its input with `data-bs-toggle`, which is why the toggle widget is a packed template.

### Overriding a template

Every template that carries Bootstrap markup lives in `django_modals/bootstrap4/…` and
`django_modals/bootstrap5/…`, with a one-line forwarder left at the flat path it always had.
So a project that already overrides, say, `django_modals/fields/label_checkbox.html` keeps that
override and it applies to both packs — the DIRS loader runs ahead of the app-directories one.
To override one version only, put the file at the pack path instead.

Paths passed in Python — `FieldEx(template='django_modals/fields/label_checkbox.html')`,
`helper.template = 'django_modals/formset/table_inline_formset.html'` — are the flat ones and
do not change.

`django_modals/modal_base.html` is **not** packed. Projects `{% extends %}` it, and a forwarder
renders a flattened context that would silently drop their `{% block %}` overrides. It no longer
needs packing: `data-backdrop` and `data-keyboard` moved into the Bootstrap constructor call in
modals.js, because Bootstrap 5 reads only their `data-bs-` spelling.

### Known gaps on Bootstrap 5

- select2 still uses the `bootstrap4` theme, and the theme CSS vendored in `modals.css` is the
  Bootstrap 4 one. It renders acceptably on Bootstrap 5; swapping in select2-bootstrap-5-theme
  is a separate job.
- `ajax_helpers.includes.Bootstrap` is pinned at 4.6.0 upstream, and its tooltip template still
  uses `.arrow` rather than `.tooltip-arrow`.
