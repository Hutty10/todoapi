from rest_framework.test import APITestCase
from django.urls import reverse
from faker import Faker

class TestSetUp(APITestCase):
    
    def setUp(self):
        self.register_url = reverse('account:register')
        self.login_url = reverse('account:login')
        self.fake = Faker()

        self.user_data = {
            'email': self.fake.email(),
            'username': self.fake.email().split('@')[0],
            'password': self.fake.email().split('@')[0],
        }
        
        return super().setUp()

    def tearDown(self):
        return super().tearDown()