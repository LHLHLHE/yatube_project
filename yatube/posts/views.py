from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Comment, Group, Post, User
from .settings import POSTS_ON_PAGE

INDEX_HTML = 'posts/index.html'
GROUP_HTML = 'posts/group_list.html'
PROFILE_HTML = 'posts/profile.html'
DETAIL_HTML = 'posts/post_detail.html'
CREATE_HTML = 'posts/create_post.html'


def page_obj(request, model):
    post_list = model.all()
    paginator = Paginator(post_list, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    return render(
        request,
        INDEX_HTML,
        {'page_obj': page_obj(request, Post.objects)}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    return render(request, GROUP_HTML, {
        'group': group,
        'page_obj': page_obj(request, group.posts),
    })


def profile(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, PROFILE_HTML, {
        'page_obj': page_obj(request, user.posts),
        'author': user,
    })


def post_detail(request, post_id):
    return render(request, DETAIL_HTML, {
        'post': get_object_or_404(Post, id=post_id),
        'form': CommentForm(request.POST or None),
        'comments': Comment.objects.filter(post=post_id)
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if not form.is_valid():
        return render(request, CREATE_HTML, {
            'form': form,
        })
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', username=request.user)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        return render(request, CREATE_HTML, {
            'form': form,
            'is_edit': True,
        })
    form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)
