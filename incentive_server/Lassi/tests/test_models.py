from django.test import TestCase
from incentive.models import Complaint


class ComplaintTest(TestCase):
    """ Test module for Puppy model """

    def setUp(self):
        Complaint.objects.create(
            app_id='1', user_id='1231', content='bla bla')
        Complaint.objects.create(
            app_id='1', user_id='12532', content='bla bla bla')

    def test_puppy_breed(self):
        first_user = Complaint.objects.get(user_id='1231')
        second_user = Complaint.objects.get(user_id='12532')
        self.assertEqual(
            str(first_user.content),
            'bla bla'
        )
        self.assertEqual(
            str(second_user.content),
            'bla bla bla'
        )
