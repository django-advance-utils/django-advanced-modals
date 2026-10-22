"""Modals put to the project's permission check (``django_modals.permissions``)."""

from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings
from django.urls import include, path

from django_modals.modals import Modal

CHECK = 'django_modals.test_permissions.check'

ASKED = []
REFUSED = set()


def check(request, kind, name, obj=None):
    ASKED.append((kind, name))
    return name not in REFUSED


class InvoiceModal(Modal):
    opened = False

    def get(self, request, *args, **kwargs):
        InvoiceModal.opened = True
        return HttpResponse('the invoice')

    def modal_permission_denied(self):
        return HttpResponse('refused')


urlpatterns = [path('invoices/', include(([path('modal/', InvoiceModal.as_view(), name='modal')], 'invoices')))]


@override_settings(ROOT_URLCONF='django_modals.test_permissions')
class ModalPermissionTestBase(SimpleTestCase):
    def setUp(self):
        ASKED.clear()
        REFUSED.clear()
        InvoiceModal.opened = False

    def open(self):
        from django.urls import resolve

        request = RequestFactory().get('/invoices/modal/')
        request.resolver_match = resolve('/invoices/modal/')
        return InvoiceModal.as_view()(request)


class WithNoCheckSetTests(ModalPermissionTestBase):
    def test_the_modal_opens_as_before(self):
        self.assertEqual(self.open().content, b'the invoice')


@override_settings(DJANGO_ADVANCED_PERMISSION_CHECK=CHECK)
class WithACheckSetTests(ModalPermissionTestBase):
    def test_it_is_asked_about_by_its_url_name(self):
        self.open()

        self.assertEqual(ASKED, [('modal', 'invoices:modal')])

    def test_a_refused_modal_does_not_open(self):
        REFUSED.add('invoices:modal')

        response = self.open()

        self.assertEqual(response.content, b'refused')
        self.assertFalse(InvoiceModal.opened)

    def test_drawn_from_another_view_it_is_named_by_its_class(self):
        modal = InvoiceModal()
        modal.request = RequestFactory().get('/somewhere-else/')
        modal.request.resolver_match = None

        self.assertEqual(modal.modal_permission_name(), 'django_modals.test_permissions.InvoiceModal')

    def test_a_given_permission_name_wins(self):
        modal = InvoiceModal()
        modal.permission_name = 'invoice_edit'

        self.assertEqual(modal.modal_permission_name(), 'invoice_edit')

    def test_a_menu_item_opening_it_is_asked_about_by_its_url_name(self):
        from django_menus.menu import MenuItem

        item = MenuItem('invoices:modal', 'Invoice')

        self.assertTrue(InvoiceModal.view_permission(RequestFactory().get('/'), item))
        self.assertEqual(ASKED, [('modal', 'invoices:modal')])

    def test_a_refused_modal_hides_the_menu_item_opening_it(self):
        from django_menus.menu import MenuItem

        REFUSED.add('invoices:modal')

        self.assertFalse(InvoiceModal.view_permission(RequestFactory().get('/'), MenuItem('invoices:modal', 'Invoice')))

    def test_a_bare_message_modal_is_never_asked(self):
        modal = Modal()
        modal.request = RequestFactory().get('/')

        self.assertTrue(modal.modal_permission())
        self.assertEqual(ASKED, [])


class PlainInvoiceModal(Modal):
    pass


@override_settings(
    DJANGO_ADVANCED_PERMISSION_CHECK=CHECK,
    INSTALLED_APPS=[
        'django.contrib.contenttypes',
        'django.contrib.auth',
        'django.contrib.staticfiles',
        'ajax_helpers',
        'django_menus',
        'django_modals',
    ],
    STATIC_URL='/static/',
)
class TheDefaultRefusalTests(ModalPermissionTestBase):
    def test_opening_a_refused_modal_shows_a_message_not_an_error(self):
        REFUSED.add('django_modals.test_permissions.PlainInvoiceModal')
        request = RequestFactory().get('/', headers={'x-requested-with': 'XMLHttpRequest'})
        request.resolver_match = None

        response = PlainInvoiceModal.as_view()(request)
        response.render()

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Permission denied', response.content)
