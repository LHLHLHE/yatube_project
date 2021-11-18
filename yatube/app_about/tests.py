from django.test import TestCase, Client


class StaticURLTests(TestCase):

    def setUp(self):
        self.guest_client = Client()

    def test_pages_urls_exist_at_desired_location_app_about(self):
        urls = [
            '/about/author/',
            '/about/tech/'
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_urls_use_correct_templates_app_about(self):
        templates_url_names = {
            '/about/author/': 'app_about/author.html',
            '/about/tech/': 'app_about/tech.html'
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertTemplateUsed(response, template)
