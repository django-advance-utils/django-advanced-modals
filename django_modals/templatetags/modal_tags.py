from django import template
from django.utils.safestring import mark_safe
from ajax_helpers.templatetags.ajax_helpers import ajax_button

from django_modals.helper import show_modal as show_modal_helper, modal_buttons, \
    modal_button_method as modal_button_method_helper
from django_modals.packs import pack_attribute, pack_class, pack_template, template_pack

register = template.Library()


@register.simple_tag
def show_modal(modal, *args, **kwargs):
    return mark_safe(show_modal_helper(modal, *args, **kwargs))


@register.simple_tag
def modal_delete(url_name, slug=None, text=None, **kwargs):
    if not text:
        text = modal_buttons['delete'] + ' Delete'
    return ajax_button(text, 'delete', url_name=url_name, url_args=[slug], css_class='btn btn-danger', **kwargs)


@register.simple_tag
def modal_button_method(title, method_name, **kwargs):
    return modal_button_method_helper(title, method_name, **kwargs)


@register.filter()
def function_friendly(value):
    return mark_safe(value.replace('-', '_'))


@register.simple_tag(takes_context=True)
def pack_source(context, name):
    """Render the Bootstrap pack's copy of a template, in this template's own context.

    Every file under django_modals/ that carries Bootstrap markup is one of these, and the
    markup itself lives in django_modals/bootstrap4/ and django_modals/bootstrap5/. The flat
    path stays the name projects use -- in an {% include %}, as a crispy field template, or as
    the path they override -- and this picks the version behind it. See django_modals.packs.
    """
    return mark_safe(pack_template(name, context.get('request')).render(context.flatten()))


@register.simple_tag(takes_context=True)
def pack_name(context):
    """The pack this request renders with, for handing to JavaScript or a template test."""
    return template_pack(context.get('request'))


@register.simple_tag(takes_context=True)
def pack_css(context, name):
    """A Bootstrap class string spelled for this request's pack."""
    return pack_class(name, context.get('request'))


@register.simple_tag(takes_context=True)
def pack_attr(context, name):
    """A Bootstrap data attribute name spelled for this request's pack."""
    return pack_attribute(name, context.get('request'))
