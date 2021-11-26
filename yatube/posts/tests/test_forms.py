import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.test.utils import override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Group, Post, User, Comment

USER = 'Name'
AUTHOR = 'Author'
TEXT1 = 'Тестовый текст 1'
TEXT2 = 'Тестовый текст 2'
TEXT3 = 'Тестовый текст 3'
SLUG1 = 'test-slug-1'
SLUG2 = 'test-slug-2'
TITLE1 = 'Тестовое название 1'
TITLE2 = 'Тестовое название 2'
DESCRIPTION1 = 'Тестовое описание 1'
DESCRIPTION2 = 'Тестовое описание 2'
SMALL_GIF = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)
COMMENT_TEXT = 'Коммент'

CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', kwargs={'username': AUTHOR})
LOGIN_URL = reverse('users:login')

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username=AUTHOR)
        cls.user = User.objects.create_user(username=USER)
        cls.form = PostForm()
        cls.post_group_1 = Group.objects.create(
            title=TITLE1,
            slug=SLUG1,
            description=DESCRIPTION1
        )
        uploaded = SimpleUploadedFile(
            name='sm.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text=TEXT1,
            author=cls.post_author,
            group=cls.post_group_1,
            image=uploaded
        )
        cls.EDIT_URL = reverse(
            'posts:post_edit',
            kwargs={'post_id': cls.post.id})
        cls.DETAIL_URL = reverse(
            'posts:post_detail',
            kwargs={'post_id': cls.post.id})
        cls.COMMENT_URL = reverse(
            'posts:add_comment',
            kwargs={'post_id': cls.post.id}
        )
        cls.guest = Client()
        cls.author = Client()
        cls.another = Client()
        cls.author.force_login(cls.post_author)
        cls.another.force_login(cls.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        post_ids = set(Post.objects.all().values_list('id', flat=True))
        form_data = {
            'text': TEXT2,
            'group': self.post_group_1.id,
            'image': uploaded
        }
        response = self.author.post(
            CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, PROFILE_URL)
        posts = Post.objects.exclude(id__in=post_ids)
        self.assertEqual(len(posts), 1)
        post = posts[0]
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.post_author)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image, 'posts/small.gif')

    def test_edit_post(self):
        uploaded = SimpleUploadedFile(
            name='sml.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        post_group_2 = Group.objects.create(
            title=TITLE2,
            slug=SLUG2,
            description=DESCRIPTION2)
        form_data = {
            'text': TEXT3,
            'group': post_group_2.id,
            'image': uploaded
        }
        response = self.author.post(
            self.EDIT_URL,
            data=form_data,
            follow=True
        )
        edited_post = response.context['post']
        self.assertRedirects(response, self.DETAIL_URL)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.author, self.post.author)
        self.assertEqual(edited_post.group.id, form_data['group'])
        self.assertEqual(edited_post.image, 'posts/sml.gif')

    def test_post_create_edit_pages_show_correct_context(self):
        urls = [
            CREATE_URL,
            self.EDIT_URL
        ]
        for url in urls:
            response = self.author.get(url)
            form_fields = {
                'text': forms.fields.CharField,
                'group': forms.fields.ChoiceField,
                'image': forms.fields.ImageField
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_create_comment(self):
        comment_ids = set(Comment.objects.all().values_list('id', flat=True))
        form_data = {
            'text': COMMENT_TEXT,
        }
        response = self.author.post(
            self.COMMENT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.DETAIL_URL)
        comments = Comment.objects.exclude(id__in=comment_ids)
        self.assertEqual(len(comments), 1)
        comment = comments[0]
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.post_author)
        self.assertEqual(comment.post, self.post)

    def test_anonymous_try_create_post_and_comment(self):
        cases = [
            [Post, TEXT1, CREATE_URL],
            [Comment, COMMENT_TEXT, self.COMMENT_URL]
        ]
        for model, text, url in cases:
            object_ids = set(model.objects.all().values_list('id', flat=True))
            form_data = {
                'text': text,
            }
            self.guest.post(
                url,
                data=form_data,
                follow=True
            )
            objects = model.objects.exclude(id__in=object_ids)
            self.assertEqual(len(objects), 0)

    def test_not_author_try_edit_post(self):
        post_group_2 = Group.objects.create(
            title=TITLE2,
            slug=SLUG2,
            description=DESCRIPTION2)
        uploaded = SimpleUploadedFile(
            name='s.gif',
            content=SMALL_GIF,
            content_type='image/gif'
        )
        form_data = {
            'text': TEXT3,
            'group': post_group_2.id,
            'image': uploaded
        }
        clients = [self.guest, self.another]
        for client in clients:
            with self.subTest(client=client):
                client.post(
                    self.EDIT_URL,
                    data=form_data,
                    follow=True
                )
                edited_post = Post.objects.filter(id=self.post.id).get()
                self.assertEqual(self.post.text, edited_post.text)
                self.assertEqual(self.post.group, edited_post.group)
                self.assertEqual(self.post.author, edited_post.author)
                self.assertEqual(self.post.image, edited_post.image)
