import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from posts.models import Group, Post, User, Comment
from posts.settings import POSTS_ON_PAGE

SLUG1 = 'test-slug-1'
SLUG2 = 'test-slug-2'
TEXT = 'Тестовый текст'
TEXT_2 = 'Тестовый текст 2'
TEXT_3 = 'Тестовый текст 3'
COMMENT_TEXT = 'Комментарий'
USER = 'Name'
TITLE = 'Тестовое название'
DESCRIPTION = 'Тестовое описание'

INDEX_URL = reverse('posts:index')
PROFILE_URL = reverse('posts:profile', kwargs={'username': USER})
GROUP_URL = reverse('posts:group_list', kwargs={'slug': SLUG1})
OTHER_GROUP_URL = reverse('posts:group_list', kwargs={'slug': SLUG2})

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER)
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG1,
            description=DESCRIPTION
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
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
        cls.COMMENT_URL = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.post.id}
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_show_correct_contexts(self):
        urls = [
            INDEX_URL,
            GROUP_URL,
            PROFILE_URL,
            self.DETAIL_URL
        ]
        for url in urls:
            response = self.authorized_client.get(url)
            if 'post' in response.context:
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
        response = self.guest.get(PROFILE_URL)
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
        self.assertIn(self.comment, response.context['comments'])


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
