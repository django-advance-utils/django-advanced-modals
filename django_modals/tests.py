"""The layout objects in ``django_modals.fields`` render under crispy-forms 1.x and 2.x.

crispy-forms 2 dropped ``form_style`` from a layout object's ``render()``, so it calls
``render(form, context, template_pack=...)`` where 1.x called
``render(form, form_style, context, template_pack=...)``. Written for 1.x, every form modal
raised ``TypeError: FieldEx.render() missing 1 required positional argument: 'context'``.
These run under whichever crispy-forms is installed; run them under both.
"""

from crispy_forms.layout import Layout
from crispy_forms.utils import render_crispy_form
from django import forms
from django.test import SimpleTestCase
from django.utils.safestring import mark_safe

from django_modals.fields import FieldEx, FieldNoLabel, Flex, Label, MultiFieldRow
from django_modals.form_helpers import RegularHelper
from django_modals.widgets.jquery_datepicker import DatePicker
from django_modals.widgets.month_picker import MonthPicker


class _Form(forms.Form):
    name = forms.CharField(label='Name')
    price = forms.CharField(label='Price')
    code = forms.CharField(label='Code')
    note = forms.CharField(label='Note')

    def __init__(self, *layout, **kwargs):
        super().__init__(**kwargs)
        # Read by the layout objects, as CrispyFormMixin sets it.
        self.mode = []
        self.helper = RegularHelper(self)
        self.helper.form_tag = False
        self.helper.layout = Layout(*layout)


def rendered(*layout):
    return render_crispy_form(_Form(*layout))


class EachLayoutObjectRenders(SimpleTestCase):

    def test_field_ex(self):
        html = rendered(FieldEx('name'))

        self.assertIn('name="name"', html)
        self.assertIn('Name', html)

    def test_field_ex_with_prepended_and_appended_text(self):
        html = rendered(FieldEx('price', prepended_text='£', appended_text='.00'))

        self.assertIn('name="price"', html)
        self.assertIn('£', html)
        self.assertIn('.00', html)

    def test_flex(self):
        html = rendered(Flex(FieldEx('name'), FieldEx('code')))

        self.assertIn('d-flex', html)
        self.assertIn('name="name"', html)
        self.assertIn('name="code"', html)

    def test_flex_puts_the_form_mode_back(self):
        form = _Form(Flex(FieldEx('name')))
        render_crispy_form(form)

        self.assertEqual([], form.mode)

    def test_multi_field_row(self):
        html = rendered(MultiFieldRow('Both', 'name', 'code'))

        self.assertIn('Both', html)
        self.assertIn('name="name"', html)
        self.assertIn('name="code"', html)

    def test_multi_field_row_puts_the_form_mode_back(self):
        form = _Form(MultiFieldRow('Both', 'name', 'code'))
        render_crispy_form(form)

        self.assertEqual([], form.mode)

    def test_label(self):
        html = rendered(Label('note', 'Free text'))

        self.assertIn('>Note</div>', html)
        self.assertIn('>Free text</div>', html)

    def test_field_no_label(self):
        html = rendered(FieldNoLabel('note'))

        self.assertIn('name="note"', html)
        self.assertIn('d-none', html)


class PrependedAndAppendedTextIsEscapedUnlessMarkedSafe(SimpleTestCase):
    """crispy-forms 1.x printed it with ``|safe``; crispy-bootstrap4 escapes it.

    So HTML in ``prepended_text``/``appended_text`` has to be marked safe to render on 2.x, and
    marked safe it renders the same on both.
    """

    ICON = '<i class="fas fa-calendar-alt fa-fw"></i>'

    def test_marked_safe_it_is_markup(self):
        self.assertIn(self.ICON, rendered(FieldEx('price', appended_text=mark_safe(self.ICON))))

    def test_the_picker_widgets_icons_are_markup(self):
        for widget in (DatePicker, MonthPicker):
            with self.subTest(widget=widget.__name__):
                html = rendered(FieldEx('price', appended_text=widget.crispy_kwargs['appended_text']))

                self.assertIn(self.ICON, html)
