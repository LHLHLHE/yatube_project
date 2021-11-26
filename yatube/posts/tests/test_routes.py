from django.test import TestCase
from django.urls.base import reverse

USERNAME = 'username'
SLUG = 'test-slug'
POST_ID = 1


class PostsRoutesTest(TestCase):

    def test_routes(self):
        cases = [
            ['/', 'index', []],
            ['/create/', 'post_create', []],
            [f'/profile/{USERNAME}/', 'profile', [USERNAME]],
            [f'/group/{SLUG}/', 'group_list', [SLUG]],
            [f'/posts/{POST_ID}/', 'post_detail', [POST_ID]],
            [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
            [f'/posts/{POST_ID}/comment/', 'add_comment', [POST_ID]],
            ['/follow/', 'follow_index', []],
            [f'/profile/{USERNAME}/follow/', 'profile_follow', [USERNAME]],
            [f'/profile/{USERNAME}/unfollow/', 'profile_unfollow', [USERNAME]],
        ]
        for url, name, arg in cases:
            with self.subTest(url=url):
                self.assertEqual(
                    url, reverse('posts:' + name, args=arg))
