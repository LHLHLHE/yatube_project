import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post, User
from posts.settings import POSTS_ON_PAGE

SLUG1 = 'test-slug-1'
SLUG2 = 'test-slug-2'
TEXT = 'Тестовый текст'
TEXT_2 = 'Тестовый текст 2'
TEXT_3 = 'Тестовый текст 3'
TEXT_4 = 'Тестовый текст 4'
COMMENT_TEXT = 'Комментарий'
USER = 'Name'
TITLE = 'Тестовое название'
DESCRIPTION = 'Тестовое описание'
FOLLOWER = 'Follower'
NOT_FOLLOWER = 'NotFollower'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)

INDEX_URL = reverse('posts:index')
PROFILE_URL = reverse('posts:profile', kwargs={'username': USER})
GROUP_URL = reverse('posts:group_list', kwargs={'slug': SLUG1})
OTHER_GROUP_URL = reverse('posts:group_list', kwargs={'slug': SLUG2})
FOLLOW_URL = reverse('posts:follow_index')
PROFILE_FOLLOW_URL = reverse(
    'posts:profile_follow',
    kwargs={'username': USER}
)
PROFILE_UNFOLLOW_URL = reverse(
    'posts:profile_unfollow',
    kwargs={'username': USER}
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER)
        cls.follower = User.objects.create_user(username=FOLLOWER)
        cls.not_follower = User.objects.create_user(username=NOT_FOLLOWER)
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG1,
            description=DESCRIPTION
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text=TEXT,
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            text=COMMENT_TEXT,
            author=cls.user,
            post=cls.post
        )
        cls.DETAIL_URL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id})
        cls.guest = Client()
        cls.authorized_client = Client()
        cls.follower_client = Client()
        cls.not_follower_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.follower_client.force_login(cls.follower)
        cls.not_follower_client.force_login(cls.not_follower)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()

    def test_pages_show_correct_contexts(self):
        Follow.objects.create(user=self.follower, author=self.user)
        urls = [
            INDEX_URL,
            GROUP_URL,
            PROFILE_URL,
            self.DETAIL_URL,
            FOLLOW_URL,
        ]
        for url in urls:
            response = self.follower_client.get(url)
            if 'page_obj' not in response.context:
                post = response.context['post']
            else:
                self.assertEqual(len(response.context['page_obj']), 1)
                post = response.context['page_obj'][0]
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group.id, self.post.group.id)
            self.assertEqual(post.id, self.post.id)
            self.assertEqual(post.image, self.post.image)

    def test_post_isnt_on_other_group_page(self):
        Group.objects.create(
            title=TITLE,
            slug=SLUG2,
            description=DESCRIPTION
        )
        response = self.authorized_client.get(OTHER_GROUP_URL)
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_author_on_profile(self):
        response = self.authorized_client.get(PROFILE_URL)
        self.assertEqual(response.context['author'], self.user)

    def test_group_on_group_list(self):
        response = self.guest.get(GROUP_URL)
        self.assertEqual(response.context['group'].id, self.group.id)
        self.assertEqual(response.context['group'].title, self.group.title)
        self.assertEqual(response.context['group'].slug, self.group.slug)
        self.assertEqual(
            response.context['group'].description, self.group.description)

    def test_comment_on_post_detail_page(self):
        response = self.authorized_client.get(self.DETAIL_URL)
        self.assertEqual(response.context['post'].comments.count(), 1)
        comment = response.context['post'].comments.all()[0]
        self.assertIn(comment.text, self.comment.text)
        self.assertEqual(comment.author, self.comment.author)
        self.assertEqual(comment.post, self.comment.post)

    def test_cache(self):
        response1 = self.authorized_client.get(INDEX_URL)
        Post.objects.all().delete()
        response2 = self.authorized_client.get(INDEX_URL)
        cache.clear()
        response3 = self.authorized_client.get(INDEX_URL)
        self.assertEqual(response2.content, response1.content)
        self.assertNotEqual(response3.content, response2.content)

    def test_follow_not_on_page(self):
        self.assertNotIn(
            self.post,
            self.not_follower_client.get(FOLLOW_URL).context['page_obj'])

    def test_follow(self):
        response = self.follower_client.get(
            PROFILE_FOLLOW_URL,
            follow=True
        )
        self.assertRedirects(response, PROFILE_URL)
        self.assertTrue(
            get_object_or_404(Follow, user=self.follower, author=self.user))

    def test_unfollow(self):
        Follow.objects.create(user=self.follower, author=self.user)
        response = self.follower_client.get(
            PROFILE_UNFOLLOW_URL,
            follow=True
        )
        self.assertRedirects(response, PROFILE_URL)
        self.assertFalse(Follow.objects.filter(
            user=self.follower,
            author=self.user).exists())


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER)
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG1,
            description=DESCRIPTION
        )
        cls.POSTS_NUM = POSTS_ON_PAGE + 3
        Post.objects.bulk_create(Post(
            text=f'{TEXT} {i}',
            author=cls.user,
            group=cls.group) for i in range(cls.POSTS_NUM))

    def setUp(self):
        self.guest = Client()
        cache.clear()

    def test_paginators(self):
        pages_and_records = {
            INDEX_URL: POSTS_ON_PAGE,
            INDEX_URL + '?page=2': self.POSTS_NUM - POSTS_ON_PAGE,
            GROUP_URL: POSTS_ON_PAGE,
            GROUP_URL + '?page=2': self.POSTS_NUM - POSTS_ON_PAGE,
            PROFILE_URL: POSTS_ON_PAGE,
            PROFILE_URL + '?page=2': self.POSTS_NUM - POSTS_ON_PAGE,
        }
        for page, records in pages_and_records.items():
            with self.subTest(page=page):
                response = self.guest.get(page)
                self.assertEqual(len(response.context['page_obj']), records)
