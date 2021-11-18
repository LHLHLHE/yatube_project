from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from users.forms import CreationForm

User = get_user_model()


class UsersFormsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CreationForm()

    def setUp(self):
        self.guest_client = Client()

    def test_create_user(self):
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Dub',
            'last_name': 'Dubdub',
            'username': 'dub',
            'email': 'user.email@maill.com',
            'password1': 'QpWo1023',
            'password2': 'QpWo1023',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
