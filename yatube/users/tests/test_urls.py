from django.contrib.auth import get_user_model
from django.test import TestCase, Client

User = get_user_model()


class URLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_urls_exist_at_desired_location_users(self):
        urls = [
            '/auth/signup/',
            '/auth/login/'
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_pages_urls_exist_at_desired_location_authorized_posts(self):
        urls = [
            '/auth/logout/',
            '/auth/password_change/',
            '/auth/password_change/done/',
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            '/auth/reset/done/'
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url, follow=True)
                self.assertEqual(response.status_code, 200)

    def test_urls_redirect_anonymous_on_login_users(self):
        url_names_redirections = {
            '/auth/password_change/':
            '/auth/login/?next=/auth/password_change/',
            '/auth/password_change/done/':
            '/auth/login/?next=/auth/password_change/done/',
        }
        for url, redirection in url_names_redirections.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, redirection)
