from django.test import Client, TestCase
from django.urls.base import reverse

from posts.models import Group, Post, User

SLUG = 'test-slug'
TEXT = 'Тестовый текст'
TEXT_2 = 'Тестовый текст 2'
TEXT_3 = 'Тестовый текст 3'
USER = 'Name'
AUTHOR = 'V'
TITLE = 'Тестовое название'
DESCRIPTION = 'Тестовое описание'

INDEX_URL = reverse('posts:index')
CREATE_POST_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', kwargs={'username': USER})
GROUP_URL = reverse('posts:group_list', kwargs={'slug': SLUG})
LOGIN_URL = reverse('users:login')


class URLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER)
        cls.author_post = User.objects.create_user(username=AUTHOR)
        cls.post = Post.objects.create(
            text=TEXT,
            author=cls.author_post,
        )
        cls.POST_EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.id})
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id})
        cls.COMMENT_URL = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.post.id}
        )
        Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRIPTION
        )

    def setUp(self):
        self.guest = Client()
        self.another = Client()
        self.author = Client()
        self.another.force_login(self.user)
        self.author.force_login(self.author_post)

    def test_pages_urls_exist_at_desired_location_posts(self):
        cases = [
            [INDEX_URL, self.guest, 200],
            [GROUP_URL, self.guest, 200],
            [PROFILE_URL, self.guest, 200],
            [self.POST_DETAIL_URL, self.guest, 200],
            [CREATE_POST_URL, self.another, 200],
            [self.POST_EDIT_URL, self.author, 200],
            ['/unexisting_page/', self.guest, 404],
            [CREATE_POST_URL, self.guest, 302],
            [self.POST_EDIT_URL, self.another, 302],
            [self.POST_EDIT_URL, self.guest, 302],
            [self.COMMENT_URL, self.guest, 302],
        ]
        for url, client, code in cases:
            with self.subTest(url=url, client=client):
                self.assertEqual(client.get(url).status_code, code)

    def test_urls_redirects_posts(self):
        cases = [
            [CREATE_POST_URL,
                self.guest,
                LOGIN_URL + '?next=' + CREATE_POST_URL],
            [self.POST_EDIT_URL,
                self.guest,
                LOGIN_URL + '?next=' + self.POST_EDIT_URL],
            [self.POST_EDIT_URL,
                self.another,
                self.POST_DETAIL_URL]
        ]
        for url, client, redirect_url in cases:
            with self.subTest(url=url, client=client):
                self.assertRedirects(
                    client.get(url, follow=True), redirect_url)

    def test_urls_use_correct_templates_posts(self):
        templates_url_names = {
            INDEX_URL: 'posts/index.html',
            GROUP_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            CREATE_POST_URL: 'posts/create_post.html',
            self.POST_EDIT_URL: 'posts/create_post.html'
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                self.assertTemplateUsed(
                    self.author.get(adress),
                    template
                )
