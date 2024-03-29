from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, GroupForm, PostForm
from .models import Follow, Group, Post, User
from .settings import CACHED_TIME_INDEX, POSTS_PER_PAGE


@cache_page(CACHED_TIME_INDEX)
def index(request):
    posts_list = Post.objects.all()
    posts_list = posts_list.select_related("author", "group")
    posts_list = posts_list.prefetch_related("comments")
    paginator = Paginator(posts_list, POSTS_PER_PAGE)
    page = paginator.get_page(request.GET.get("page"))
    context = {
        "page": page,
        "paginator": paginator,
    }
    return render(request, "index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    posts = posts.select_related("author", "group")
    posts = posts.prefetch_related("comments")
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page = paginator.get_page(request.GET.get("page"))
    context = {
        "group": group,
        "page": page,
        "paginator": paginator,
    }
    return render(request, "group.html", context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if not form.is_valid():
        return render(request, "new_post.html", {"form": form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect("index")


@login_required
def new_group(request):
    form = GroupForm(request.POST or None)
    if not form.is_valid():
        return render(request, "new_group.html", {"form": form})
    group = form.save()
    return redirect("group_posts", slug=group.slug)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.all()
    author_posts = author_posts.select_related("author", "group")
    author_posts = author_posts.prefetch_related("comments")
    paginator = Paginator(author_posts, POSTS_PER_PAGE)
    page = paginator.get_page(request.GET.get("page"))
    following = (request.user.is_authenticated
                 and request.user != author
                 and request.user.follower.filter(author=author).exists())
    context = {
        "author": author,
        "page": page,
        "paginator": paginator,
        "following": following,
    }
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    following = (request.user.is_authenticated
                 and request.user != post.author
                 and request.user.follower.filter(author=post.author).exists())
    context = {
        "author": post.author,
        "post": post,
        "comments": post.comments.all(),
        "form": CommentForm(),
        "following": following,
    }
    return render(request, "post.html", context)


@login_required
def post_edit(request, username, post_id):
    if username != request.user.username:
        return redirect("post", username=username, post_id=post_id)
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if not form.is_valid():
        context = {"form": form, "post": post}
        return render(request, "new_post.html", context)
    form.save()
    return redirect("post", username=username, post_id=post_id)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect("post", username=username, post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    posts = posts.select_related("author", "group")
    posts = posts.prefetch_related("comments")
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page = paginator.get_page(request.GET.get("page"))
    context = {
        "page": page,
        "paginator": paginator,
    }
    return render(request, "follow.html", context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        if not request.user.follower.filter(author=author).exists():
            Follow.objects.create(
                user=request.user,
                author=author,
            )
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow,
        user=request.user,
        author__username=username
    ).delete()
    return redirect("profile", username=username)


def page_not_found(request, exception):
    return render(request,
                  "misc/404.html",
                  {"path": request.path},
                  status=404)


def server_error(request):
    return render(request,
                  "misc/500.html",
                  status=500)
