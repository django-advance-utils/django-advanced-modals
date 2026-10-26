"""The progress poll of a task modal (``django_modals.task_modals.TaskModal``)."""

import json

from django.test import RequestFactory, SimpleTestCase

from django_modals.task_modals import TaskModal


class _Result:
    """What Celery's ``AsyncResult`` does while a task has not finished: ask the result backend
    again on every access of ``info``, so two reads in a row can see two different results."""

    id = 'abc'
    state = 'PROGRESS'

    def __init__(self, infos):
        self.infos = list(infos)
        self.reads = 0

    @property
    def info(self):
        self.reads += 1
        return self.infos.pop(0) if len(self.infos) > 1 else self.infos[0]


class _Task:
    def __init__(self, result):
        self.result = result

    def AsyncResult(self, _task_id):
        return self.result


PROGRESS = {'current': 40, 'message': 'Importing 2 of 5...'}
FINISHED = {'commands': []}


def poll(infos):
    result = _Result(infos)
    modal = TaskModal(task=_Task(result))
    modal.request = RequestFactory().post('/task/modal/')
    response = modal.ajax_check_result(task_id='abc')
    return result, json.loads(response.content)


class ProgressPollTests(SimpleTestCase):
    def test_progress_is_drawn_and_the_poll_goes_on(self):
        _, commands = poll([PROGRESS])

        functions = [command['function'] for command in commands]
        self.assertEqual(functions, ['set_css', 'html', 'timeout'])
        self.assertEqual(commands[0]['val'], '40%')
        self.assertEqual(commands[1]['html'], 'Importing 2 of 5...')

    def test_a_task_that_finishes_between_two_reads_of_its_info_does_not_break_the_poll(self):
        """``'message' in task_result.info`` and ``task_result.info['message']`` were two reads, so a
        task that finished in between was a KeyError, and a 500 that left the modal on its opening
        message for good (the page has no handler for a failed poll)."""
        result, commands = poll([PROGRESS, PROGRESS, PROGRESS, FINISHED])

        self.assertEqual(commands[-1]['function'], 'timeout')
        self.assertEqual(result.reads, 1)

    def test_a_task_that_fails_between_the_state_and_the_info_does_not_break_the_poll(self):
        """The failure is only seen as a state by the next poll; until then ``info`` is the exception,
        which has no ``get``."""
        _, commands = poll([RuntimeError('boom')])

        self.assertEqual([command['function'] for command in commands], ['timeout'])

    def test_a_task_with_nothing_to_report_yet_just_polls_again(self):
        _, commands = poll([None])

        self.assertEqual([command['function'] for command in commands], ['timeout'])
