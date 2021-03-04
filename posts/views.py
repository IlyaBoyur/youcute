from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Group, Post, User
from .settings import POSTS_PER_PAGE, CACHED_TIME_INDEX


def index(request):
    posts_list = Post.objects.all()
    paginator = Paginator(posts_list, POSTS_PER_PAGE)
    page = paginator.get_page(request.GET.get("page"))
    context = {
        "page": page,
        "paginator": paginator,
        "index_page_timeout": CACHED_TIME_INDEX,
    }
    return render(request, "index.html", context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
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


def profile(request, username):
    author = get_object_or_404(User, username=username)
    paginator = Paginator(author.posts.all(), POSTS_PER_PAGE)
    page = paginator.get_page(request.GET.get("page"))
    context = {
        "author": author,
        "page": page,
        "paginator": paginator,
    }
    return render(request, "profile.html", context)


def post_view(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    context = {
        "author": post.author,
        "post": post,
        "comments": post.comments.all(),
        "form": CommentForm(),
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
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return redirect("post", username=username, post_id=post_id)
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = get_object_or_404(Post, id=post_id)
    comment.save()
    return redirect("post", username=username, post_id=post_id)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404,
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
