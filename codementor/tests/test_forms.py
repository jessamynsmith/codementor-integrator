import datetime

from django.test import TestCase

from codementor import forms as codementor_forms


class TestScheduleDataForm(TestCase):

    def test_valid(self):
        input_data = {
            "schedule_data": """8/19 6-10
8/20 off
8/21 6-10
8/22 1-5
8/23 4-8
8/24 12-8:30
8/25 off""",
            "summary": "Test event"
        }

        form = codementor_forms.ScheduleDataForm(data=input_data)

        is_valid = form.is_valid()

        self.assertTrue(is_valid)
        expected_data = [
            (datetime.datetime(2019, 8, 19, 18, 0, 0), datetime.datetime(2019, 8, 19, 22, 0, 0)),
            (datetime.datetime(2019, 8, 21, 18, 0, 0), datetime.datetime(2019, 8, 21, 22, 0, 0)),
            (datetime.datetime(2019, 8, 22, 13, 0, 0), datetime.datetime(2019, 8, 22, 17, 0, 0)),
            (datetime.datetime(2019, 8, 23, 16, 0, 0), datetime.datetime(2019, 8, 23, 20, 0, 0)),
            (datetime.datetime(2019, 8, 24, 12, 0, 0), datetime.datetime(2019, 8, 24, 20, 30, 0)),
        ]
        self.assertEqual(expected_data, form.cleaned_data['schedule_data'])
