from django.core.cache import cache
from django.test import Client, TestCase
from django.urls.base import reverse

from posts.models import Follow, Group, Post, User

SLUG = 'test-slug'
TEXT = 'Тестовый текст'
TEXT_2 = 'Тестовый текст 2'
TEXT_3 = 'Тестовый текст 3'
USER = 'Name'
AUTHOR = 'V'
TITLE = 'Тестовое название'
DESCRIPTION = 'Тестовое описание'
NEW_USER = 'NewUser'

INDEX_URL = reverse('posts:index')
CREATE_POST_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', kwargs={'username': AUTHOR})
GROUP_URL = reverse('posts:group_list', kwargs={'slug': SLUG})
LOGIN_URL = reverse('users:login')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
PROFILE_FOLLOW_URL = reverse(
    'posts:profile_follow',
    kwargs={'username': AUTHOR}
)
PROFILE_UNFOLLOW_URL = reverse(
    'posts:profile_unfollow',
    kwargs={'username': AUTHOR}
)


class URLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER)
        cls.author_post = User.objects.create_user(username=AUTHOR)
        cls.new_user = User.objects.create_user(username=NEW_USER)
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
        Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRIPTION
        )
        cls.guest = Client()
        cls.another = Client()
        cls.author = Client()
        cls.new_client = Client()
        cls.another.force_login(cls.user)
        cls.author.force_login(cls.author_post)
        cls.new_client.force_login(cls.new_user)

    def setUp(self):
        cache.clear()

    def test_pages_urls_exist_at_desired_location_posts(self):
        Follow.objects.create(user=self.user, author=self.author_post)
        cases = [
            [INDEX_URL, self.guest, 200],
            [GROUP_URL, self.guest, 200],
            [PROFILE_URL, self.another, 200],
            [self.POST_DETAIL_URL, self.guest, 200],
            [CREATE_POST_URL, self.another, 200],
            [self.POST_EDIT_URL, self.author, 200],
            ['/unexisting_page/', self.guest, 404],
            [CREATE_POST_URL, self.guest, 302],
            [self.POST_EDIT_URL, self.another, 302],
            [self.POST_EDIT_URL, self.guest, 302],
            [FOLLOW_INDEX_URL, self.another, 200],
            [FOLLOW_INDEX_URL, self.guest, 302],
            [PROFILE_FOLLOW_URL, self.new_client, 302],
            [PROFILE_FOLLOW_URL, self.guest, 302],
            [PROFILE_UNFOLLOW_URL, self.another, 302],
            [PROFILE_UNFOLLOW_URL, self.guest, 302],
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
                self.POST_DETAIL_URL],
            [PROFILE_FOLLOW_URL,
                self.new_client,
                PROFILE_URL],
            [PROFILE_FOLLOW_URL,
                self.guest,
                LOGIN_URL + '?next=' + PROFILE_FOLLOW_URL],
            [PROFILE_FOLLOW_URL,
                self.another,
                PROFILE_URL],
            [PROFILE_UNFOLLOW_URL,
                self.guest,
                LOGIN_URL + '?next=' + PROFILE_UNFOLLOW_URL],
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
            self.POST_EDIT_URL: 'posts/create_post.html',
            FOLLOW_INDEX_URL: 'posts/follow.html'
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                self.assertTemplateUsed(
                    self.author.get(adress),
                    template
                )
