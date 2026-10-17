"""A close that comes back while its modal is still opening.

Bootstrap takes about 300ms to bring a modal in, and its hide does nothing until that is over. The
child form here replaces a chooser in the same container, as a picker's "new" form does, so nothing
marks the page busy while it comes in, and the page submits it 50ms into its entrance -- quicker
than a person could, as a test driving a browser does. The answer, a close followed by a command
for the parent, arrives while the child is still opening.

Every save of the child is logged on the page, and so is every time the parent hears of one. The
child should save once, the parent hear once, and the parent stay open. Had the close been lost,
the child would have stayed on top and the post_modal meant for the parent would have gone to the
child, which has no button_child_saved and so takes the post as a submit: it saves again.
"""
from django.forms.fields import CharField
from django.urls import reverse
from django.utils.html import format_html
from show_src_code.modals import FormModal, Modal

from django_modals.forms import CrispyForm
from django_modals.helper import modal_button, modal_button_method
from .views import MainMenuTemplateView


def log(view, text):
    view.add_command('append_to', selector='#close-timing-log', html=format_html('<li>{}</li>', text))


class CloseTiming(MainMenuTemplateView):

    template_name = 'example_views/close_timing.html'

    def setup_menu(self):
        super().setup_menu()
        self.add_menu('modals', 'buttons', ).add_items(
            ('close_timing_parent,-', 'Open the parent'),
        )


class CloseTimingParent(Modal):
    modal_title = 'Parent'

    def modal_content(self):
        return 'The child opens on top of this one and is submitted while it is still opening.'

    def get_modal_buttons(self):
        return [modal_button('Add a child',
                             {'function': 'show_modal', 'modal': reverse('close_timing_chooser', args=['-'])}),
                modal_button('Close', 'close', 'btn-secondary')]

    def button_child_saved(self, **_kwargs):
        log(self, 'The parent heard that the child saved')
        return self.command_response()


class CloseTimingChooser(Modal):
    modal_title = 'Choose a child'

    def modal_content(self):
        return 'There are no children to choose from yet.'

    def get_modal_buttons(self):
        return [modal_button_method('New child', 'new_child'),
                modal_button('Cancel', 'close', 'btn-secondary')]

    def button_new_child(self, **_kwargs):
        return self.modal_replace('close_timing_child')


class ChildForm(CrispyForm):
    name = CharField(initial='A child')


class CloseTimingChild(FormModal):
    form_class = ChildForm
    modal_title = 'Child'

    def form_valid(self, form):
        log(self, f'The child saved "{form.cleaned_data["name"]}"')
        self.add_command('close', no_refresh=True)
        # Meant for the parent. send_inputs posts to whichever modal is on top, so it reaches the
        # parent only if the child has gone by the time it runs.
        self.add_command('post_modal', button='child_saved')
        return self.command_response()

