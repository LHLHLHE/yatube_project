import textwrap

from django.test import TestCase
from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст текст текст',
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        field_strs = {
            str(self.post):
                f'{textwrap.shorten(self.post.text, width=15)}, '
                f'{self.post.pub_date}, '
                f'{self.post.author.username}, '
                f'{self.post.group.title}',
            str(self.group): self.group.title
        }
        for field, value in field_strs.items():
            with self.subTest(field=field):
                self.assertEqual(field, value)

    def test_post_verbose_name(self):
        """Проверяем, verbose_name модели Post."""
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name, value
                )

    def test_post_help_text(self):
        """Проверяем, help_text модели Post."""
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу'
        }
        for field, value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).help_text, value
                )
