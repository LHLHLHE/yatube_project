import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User

USER = 'Name'
TEXT1 = 'Тестовый текст 1'
TEXT2 = 'Тестовый текст 2'
TEXT3 = 'Тестовый текст 3'
SLUG1 = 'test-slug-1'
SLUG2 = 'test-slug-2'
TITLE1 = 'Тестовое название 1'
TITLE2 = 'Тестовое название 2'
DESCRIPTION1 = 'Тестовое описание 1'
DESCRIPTION2 = 'Тестовое описание 2'

CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', kwargs={'username': USER})

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USER)
        cls.form = PostForm()
        cls.post_group_1 = Group.objects.create(
            title=TITLE1,
            slug=SLUG1,
            description=DESCRIPTION1
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text=TEXT1,
            author=cls.user,
            group=cls.post_group_1
        )
        cls.EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.id})
        cls.DETAIL_URL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id})

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        post_ids = set(Post.objects.all().values_list('id', flat=True))
        form_data = {
            'text': TEXT2,
            'group': self.post_group_1.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PROFILE_URL)
        posts = Post.objects.exclude(id__in=post_ids)
        self.assertEqual(len(posts), 1)
        post = posts[0]
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image, 'posts/small.gif')

    def test_edit_post(self):
        post_group_2 = Group.objects.create(
            title=TITLE2,
            slug=SLUG2,
            description=DESCRIPTION2)
        form_data = {
            'text': TEXT3,
            'group': post_group_2.id,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            self.EDIT_URL,
            data=form_data,
            follow=True
        )
        edited_post = response.context['post']
        self.assertRedirects(response, self.DETAIL_URL)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.author, self.post.author)
        self.assertEqual(edited_post.group.id, form_data['group'])
        self.assertEqual(edited_post.image.read(), form_data['image'].read())

    def test_post_create_edit_pages_show_correct_context(self):
        urls = [
            CREATE_URL,
            self.EDIT_URL
        ]
        for url in urls:
            response = self.authorized_client.get(url)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)
