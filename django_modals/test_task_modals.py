import json

from django.test import RequestFactory, SimpleTestCase

from django_modals.task_modals import TaskModal


class _Result:
    id = 'abc'

    def __init__(self, info, states=('PROGRESS',)):
        self._info = info
        self.states = list(states)

    @property
    def state(self):
        return self.states.pop(0) if len(self.states) > 1 else self.states[0]

    @property
    def info(self):
        return self._info


class _Task:
    def __init__(self, result):
        self.result = result

    def AsyncResult(self, _task_id):
        return self.result


def poll(info, states=('PROGRESS',)):
    modal = TaskModal(task=_Task(_Result(info, states)))
    modal.request = RequestFactory().post('/task/modal/')
    commands = json.loads(modal.ajax_check_result(task_id='abc').content)
    return [command['function'] for command in commands], commands


class ProgressPollTests(SimpleTestCase):
    def test_progress_is_drawn(self):
        functions, commands = poll({'current': 40, 'message': 'Importing 2 of 5...'})

        self.assertEqual(functions, ['set_css', 'html', 'timeout'])
        self.assertEqual(commands[0]['val'], '40%')
        self.assertEqual(commands[1]['html'], 'Importing 2 of 5...')

    def test_finished_result_is_not_drawn_as_progress(self):
        functions, _ = poll({'commands': [], 'message': 'Done'})

        self.assertEqual(functions, ['timeout'])

    def test_exception_is_not_drawn_as_progress(self):
        functions, _ = poll(RuntimeError('boom'))

        self.assertEqual(functions, ['timeout'])

    def test_no_info_polls_again(self):
        functions, _ = poll(None)

        self.assertEqual(functions, ['timeout'])

    def test_state_is_read_once(self):
        functions, _ = poll({'commands': []}, states=('REVOKED', 'PROGRESS'))

        self.assertIn('message', functions)
