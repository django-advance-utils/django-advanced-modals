"""The two Bootstrap packs stay in step, and each renders its own version's names.

django-modals ships one template folder per Bootstrap version. That buys clean markup and room
for the versions to diverge structurally, at the cost dual emission did not have: a fix applied
to one pack and not the other is **silent**. Nothing in the rendered page looks wrong on the
version you happen to be looking at, and there is no twin missing from a class attribute for a
scanner to notice.

So the drift is what is pinned here. ``test_packs_are_identical_once_renamed`` normalises every
Bootstrap 4 name in a pack4 template to its Bootstrap 5 spelling and requires the result to
equal the pack5 template exactly. A fix landing in one pack and not the other fails it, naming
the file. When the packs are *meant* to diverge -- a structural difference a rename could not
express, which is the reason for having packs at all -- the file is added to
STRUCTURAL_DIVERGENCE with a note, and that is the moment someone has to think about it.
"""
import os
import re

from django.test import SimpleTestCase, override_settings

import django_modals
from django_modals.packs import DEFAULT_PACK, PACKS, PACK_ATTRIBUTES, PACK_CLASSES, pack_attribute, pack_class, \
    template_pack

TEMPLATE_ROOT = os.path.join(os.path.dirname(os.path.abspath(django_modals.__file__)),
                             'templates', 'django_modals')

# Bootstrap 4 token -> Bootstrap 5 token, applied to normalise a pack4 template before comparing
# it with its pack5 twin. Only renames belong here; anything that changes the shape of the
# markup goes in STRUCTURAL_DIVERGENCE instead.
RENAMES = {
    'float-left': 'float-start', 'float-right': 'float-end',
    'text-left': 'text-start', 'text-right': 'text-end',
    'custom-select': 'form-select',
    # crispy-bootstrap5 spells the field wrapper mb-3, so the packs do too.
    'form-group': 'mb-3',
    'custom-file': 'form-control',
    'sr-only': 'visually-hidden',
    'btn-block': 'w-100',
    'badge-pill': 'rounded-pill',
    'font-italic': 'fst-italic', 'text-monospace': 'font-monospace',
    'data-toggle': 'data-bs-toggle',
    'data-dismiss': 'data-bs-dismiss',
    'data-placement': 'data-bs-placement',
    # The crispy pack the template borrows field markup from moves with ours.
    "'bootstrap4/": "'bootstrap5/", '"bootstrap4/': '"bootstrap5/',
    # month_picker focuses its field from the element carrying the calendar icon. In Bootstrap 4
    # that is the .input-group-append wrapper; Bootstrap 5 dropped the wrapper, leaving the
    # .input-group-text that was inside it.
    '.input-group-append': '.input-group-text',
}
for _c in ('primary', 'secondary', 'success', 'danger', 'warning', 'info', 'light', 'dark'):
    RENAMES[f'badge-{_c}'] = f'text-bg-{_c}'
for _w in ('bold', 'bolder', 'normal', 'light', 'lighter'):
    RENAMES[f'font-weight-{_w}'] = f'fw-{_w}'
_SIZES = [str(n) for n in range(6)] + ['auto'] + [f'n{n}' for n in range(1, 6)]
for _bp in ('', 'sm-', 'md-', 'lg-', 'xl-'):
    for _n in _SIZES:
        RENAMES[f'ml-{_bp}{_n}'] = f'ms-{_bp}{_n}'
        RENAMES[f'mr-{_bp}{_n}'] = f'me-{_bp}{_n}'
        if not _n.startswith('n'):
            RENAMES[f'pl-{_bp}{_n}'] = f'ps-{_bp}{_n}'
            RENAMES[f'pr-{_bp}{_n}'] = f'pe-{_bp}{_n}'

# Templates whose two versions are not the same markup with different names, and why. Each entry
# is a deliberate decision; adding one is how a structural difference gets recorded.
STRUCTURAL_DIVERGENCE = {
    'formset/prepended_appended_text.html':
        'Bootstrap 5 deleted the .input-group-prepend/.input-group-append wrappers, so the '
        '.input-group-text spans sit directly inside .input-group.',
    'widgets/colour_picker_append.html':
        'As above, and the two appended swatch/random spans lose the wrapper that held them.',
    'fields/label_checkbox.html':
        'crispy-bootstrap5 renders radios and multiple checkboxes from one template keyed on '
        'the option type, where the Bootstrap 4 pack has a separate file for each.',
}


def _pack_files(pack):
    root = os.path.join(TEMPLATE_ROOT, pack)
    found = set()
    for path, _dirs, files in os.walk(root):
        for name in files:
            if name.endswith('.html'):
                found.add(os.path.relpath(os.path.join(path, name), root))
    return found


def _token_pattern(token):
    """``token`` with a word boundary on whichever end is itself a word character.

    A class name needs both, so that ml-2 does not match inside ml-sm-2. A token like
    "\'bootstrap4/" ends in punctuation and is followed by a filename, so a trailing boundary
    there would never match.
    """
    start = r'(?<![\w-])' if re.match(r'[\w-]', token[0]) else ''
    end = r'(?![\w-])' if re.match(r'[\w-]', token[-1]) else ''
    return rf'{start}{re.escape(token)}{end}'


def _normalise(text):
    """Rewrite every Bootstrap 4 name in ``text`` to its Bootstrap 5 spelling.

    Longest token first, so that ml-sm-2 is not half-rewritten by the rule for ml-2.
    """
    for old in sorted(RENAMES, key=len, reverse=True):
        text = re.sub(_token_pattern(old), RENAMES[old], text)
    return text


class TemplatePackTests(SimpleTestCase):

    def test_both_packs_hold_the_same_files(self):
        """Neither pack has a template the other is missing."""
        self.assertEqual(_pack_files('bootstrap4'), _pack_files('bootstrap5'))

    def test_packs_are_identical_once_renamed(self):
        """A fix has to land in both packs, or the renamed pack4 file stops matching pack5."""
        for name in sorted(_pack_files('bootstrap4')):
            if name in STRUCTURAL_DIVERGENCE:
                continue
            with self.subTest(template=name):
                with open(os.path.join(TEMPLATE_ROOT, 'bootstrap4', name)) as f:
                    four = f.read()
                with open(os.path.join(TEMPLATE_ROOT, 'bootstrap5', name)) as f:
                    five = f.read()
                self.maxDiff = None
                self.assertEqual(
                    _normalise(four), five,
                    f'{name} differs between the packs by more than a Bootstrap rename. If that '
                    f'is deliberate, add it to STRUCTURAL_DIVERGENCE with a note.',
                )

    def test_structural_divergence_entries_are_real_templates(self):
        """A file that stops diverging, or gets renamed, should not sit in the list unnoticed."""
        self.assertEqual(set(STRUCTURAL_DIVERGENCE) - _pack_files('bootstrap4'), set())

    def test_no_bootstrap4_names_survive_in_the_bootstrap5_pack(self):
        """Nothing in the Bootstrap 5 pack still spells a name Bootstrap 5 removed."""
        for name in sorted(_pack_files('bootstrap5')):
            with open(os.path.join(TEMPLATE_ROOT, 'bootstrap5', name)) as f:
                text = f.read()
            for old in RENAMES:
                # The crispy pack path rename is a prefix of the bootstrap5 one it maps to.
                if old.endswith('bootstrap4/'):
                    continue
                with self.subTest(template=name, token=old):
                    self.assertIsNone(
                        re.search(_token_pattern(old), text),
                        f'{name} still uses the Bootstrap 4 name {old!r}',
                    )

    def test_every_flat_path_forwards_to_the_pack(self):
        """Each packed template keeps its old path, holding only a pack_source forwarder.

        That path is the one projects reference -- as a crispy field template, in an
        {% include %}, or as the file they override -- so it has to keep resolving.
        """
        for name in sorted(_pack_files('bootstrap4')):
            flat = os.path.join(TEMPLATE_ROOT, name)
            with self.subTest(template=name):
                self.assertTrue(os.path.exists(flat), f'{name} has no forwarder at its flat path')
                expected = "{% load modal_tags %}{% pack_source '" + name + "' %}"
                with open(flat) as f:
                    self.assertEqual(f.read(), expected)


class PackLookupTests(SimpleTestCase):

    def test_default_is_bootstrap4(self):
        self.assertEqual(template_pack(), DEFAULT_PACK)
        self.assertEqual(DEFAULT_PACK, 'bootstrap4')

    @override_settings(DJANGO_MODALS_TEMPLATE_PACK='bootstrap5')
    def test_setting_names_a_pack(self):
        self.assertEqual(template_pack(), 'bootstrap5')
        self.assertEqual(pack_class('fields_wrap'), 'row')
        self.assertEqual(pack_attribute('dismiss'), 'data-bs-dismiss')

    @override_settings(DJANGO_MODALS_TEMPLATE_PACK=lambda request: 'bootstrap5')
    def test_setting_may_be_a_callable(self):
        self.assertEqual(template_pack(None), 'bootstrap5')

    @override_settings(
        DJANGO_MODALS_TEMPLATE_PACK='modal_examples.context_processors.template_pack_for_request')
    def test_setting_may_be_a_dotted_path(self):
        """The example app's per-request callable, which falls back to 4 without a request."""
        self.assertEqual(template_pack(None), 'bootstrap4')

    def test_every_pack_defines_every_key(self):
        """A key added for one pack and forgotten in the other would raise only at render."""
        for table in (PACK_CLASSES, PACK_ATTRIBUTES):
            expected = set(table[DEFAULT_PACK])
            for pack in PACKS:
                with self.subTest(pack=pack, table=table[DEFAULT_PACK].keys()):
                    self.assertEqual(set(table[pack]), expected)


class ForwarderRenderTests(SimpleTestCase):
    """The flat path a project references still renders, and renders this request's pack.

    The drift test above compares files. These two render them, which is what catches a
    forwarder that was never written, a pack_source tag that cannot find its template, and the
    template-loader ordering that makes the whole scheme work.
    """

    CASES = {
        'django_modals/widgets/toggle.html': ('data-toggle="toggle"', 'data-bs-toggle="toggle"'),
        'django_modals/widgets/month_picker.html': ('.input-group-append', '.input-group-text'),
    }

    def _context(self):
        from django import forms
        form = forms.Form()
        form.fields['on'] = forms.BooleanField(required=False)
        return {'widget': {'name': 'on', 'type': 'checkbox', 'attrs': {'id': 'id_on'}, 'value': None},
                'field': form['on']}

    def test_forwarder_renders_the_pack_for_the_setting(self):
        from django.template.loader import render_to_string
        for path, (four, five) in self.CASES.items():
            for pack, wanted, unwanted in (('bootstrap4', four, five), ('bootstrap5', five, four)):
                with self.subTest(template=path, pack=pack):
                    with override_settings(DJANGO_MODALS_TEMPLATE_PACK=pack):
                        html = render_to_string(path, self._context())
                    self.assertIn(wanted, html)
                    self.assertNotIn(unwanted, html)


class CrispyPackTests(SimpleTestCase):
    """Crispy renders a modal's form with the same pack the modal templates use.

    Without this the two halves of a form drift apart silently: Bootstrap 5 field markup
    wrapped in Bootstrap 4 layout markup, on a page that looks almost right.
    """

    def _form(self):
        from django import forms
        from django_modals.fields import FieldEx
        from django_modals.forms import CrispyForm
        from django_modals.form_helpers import TwoColumnRegularHelper

        class Demo(CrispyForm):
            name = forms.CharField()
            colour = forms.ChoiceField(choices=[('r', 'Red'), ('b', 'Blue')])

            def post_init(self, *args, **kwargs):
                return [self.row('name'),
                        FieldEx('colour', template='django_modals/fields/label_checkbox.html')]

        return Demo(helper_class=TwoColumnRegularHelper)

    def test_helper_follows_the_modals_setting(self):
        for pack in PACKS:
            with self.subTest(pack=pack):
                with override_settings(DJANGO_MODALS_TEMPLATE_PACK=pack):
                    self.assertEqual(self._form().helper.template_pack, pack)

    def test_rendered_form_carries_this_pack_s_class_names(self):
        from crispy_forms.utils import render_crispy_form
        # custom-select/form-select comes from the packed label_checkbox template, reached
        # through its flat path by crispy's own field rendering -- the path downstream
        # FieldEx(template=...) arguments take.
        expected = {
            'bootstrap4': (['form-group row', 'form-row', 'custom-select'], ['mb-3 row', 'form-select']),
            'bootstrap5': (['mb-3 row', 'form-select'], ['form-group row', 'form-row', 'custom-select']),
        }
        for pack, (wanted, unwanted) in expected.items():
            with override_settings(DJANGO_MODALS_TEMPLATE_PACK=pack):
                html = render_crispy_form(self._form())
            for token in wanted:
                with self.subTest(pack=pack, token=token):
                    self.assertIn(token, html)
            for token in unwanted:
                with self.subTest(pack=pack, token=token):
                    self.assertNotIn(token, html)
