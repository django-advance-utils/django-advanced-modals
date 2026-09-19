from crispy_forms.helper import FormHelper
from crispy_forms.utils import TEMPLATE_PACK

from django_modals.packs import pack_class, template_pack


class WrapperHelper(FormHelper):
    def get_attributes(self, template_pack=TEMPLATE_PACK):
        items = super().get_attributes(template_pack)
        if hasattr(self, 'wrapper_class'):
            items['wrapper_class'] = self.wrapper_class
        return items

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self, 'form_attrs'):
            self.attrs = self.form_attrs
        # crispy passes the form positionally, but FormHelper(form=...) is equally valid. The
        # form carries the request when a modal view built it, and None otherwise.
        form = args[0] if args else kwargs.get('form')
        self.request = getattr(form, 'request', None)
        # Point crispy's own rendering at the same pack the modal templates use. Without this a
        # project could set DJANGO_MODALS_TEMPLATE_PACK to bootstrap5 and still get Bootstrap 4
        # markup out of every crispy layout object, silently. FormHelper has no template_pack
        # attribute of its own -- the {% crispy %} tag reads it inside a try/except -- so setting
        # it here is the supported hook.
        self.template_pack = template_pack(self.request)


class InlineFormset(WrapperHelper):
    template = 'django_modals/multi_form/table_formset.html'
    disable_csrf = True


class TwoColumnHelper(WrapperHelper):

    flex_label_class = 'col-form-label col-form-label-sm mx-1'
    flex_field_class = 'input-group-sm'
    label_class = 'col-md-4 col-form-label-sm'
    field_class = 'col-md-8 input-group-sm'
    form_class = 'form-horizontal'
    wrapper_class = 'col-lg-6'
    fields_wrap_class = 'row'
    disable_csrf = True


class HorizontalHelper(WrapperHelper):

    flex_label_class = 'col-form-label col-form-label-sm mx-1'
    flex_field_class = 'input-group-sm'
    label_class = 'col-md-3 col-form-label-sm'
    field_class = 'col-md-9 col-lg-6 input-group-sm'
    form_class = 'form-horizontal'
    disable_csrf = True


class SmallHelper(WrapperHelper):

    flex_label_class = 'col-form-label col-form-label-sm mx-1'
    flex_field_class = 'input-group-sm'
    label_class = 'col-md-3 col-form-label-sm'
    field_class = 'col-md-9 input-group-sm'
    form_class = 'form-horizontal'
    disable_csrf = True


class RegularHelper(WrapperHelper):

    flex_label_class = 'col-form-label col-form-label-sm mx-1'
    flex_field_class = 'input-group-sm'
    label_class = ''
    field_class = 'input-group-sm'
    form_class = ''
    disable_csrf = True
    auto_placeholder = True


class TwoColumnRegularHelper(RegularHelper):
    wrapper_class = 'col-lg-6'

    @property
    def fields_wrap_class(self):
        # form-row went in Bootstrap 5; a plain row with its own gutters replaces it.
        return pack_class('fields_wrap', self.request)


class NoLabelsRegularHelper(RegularHelper):
    form_show_labels = False


class HorizontalNoEnterHelper(HorizontalHelper):
    form_attrs = {'no_enter': True}
