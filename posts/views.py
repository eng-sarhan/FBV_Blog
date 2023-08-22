from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import ListView

from .forms import CommentForm, PostForm
from .models import Post, Author, PostView, Category


def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None


def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(categories__title__icontains=query)
        ).order_by('-timestamp').distinct()
    context = {
        'queryset': queryset
    }
    return render(request, 'posts/search_results.html', context)


def get_category_count():
    queryset = Post \
        .objects \
        .values('categories__title') \
        .annotate(Count('categories__title'))
    return queryset


def post_list(request):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    cats = Category.objects.all()
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'queryset': paginated_queryset,
        'most_recent': most_recent,
        'page_request_var': page_request_var,
        'category_count': category_count,

    }
    return render(request, 'posts/blog.html', context)


def CategoryView(request, cats):
    category_posts = Post.objects.filter(categories__title=cats.replace('-', ' '))
    return render(request, 'posts/categories.html',
                  {'cats': cats.replace('-', ' ').title(), 'category_posts': category_posts})


def post(request, id):
    post = get_object_or_404(Post, id=id)

    context = {
        'post': post
    }
    return render(request, 'posts:post.html', context)


class UserPostListView(ListView):
    model = Post
    template_name = 'posts/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 4

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-timestamp')


class PostListAuthor(ListView):
    model = Post, Author
    template_name = 'posts/post_author_list.html'
    context_object_name = 'author_posts'
    paginate_by = 4

    def get_queryset(self):
        author_id = self.kwargs['author_id']
        return Post.objects.filter(author=int(author_id)).order_by("-timestamp")


def post_detail(request, id):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post = get_object_or_404(Post, id=id)

    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user, post=post)

    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse("posts:post-detail", kwargs={
                'id': post.id
            }))
    context = {
        'post': post,
        'most_recent': most_recent,
        'category_count': category_count,
        'form': form
    }
    return render(request, 'posts/post.html', context)


def post_create(request):
    title = 'Create'
    form = PostForm(request.POST or None, request.FILES or None)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("posts:post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "posts/post_create.html", context)


def post_update(request, id):
    title = 'Update'
    post = get_object_or_404(Post, id=id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("posts:post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "posts/post_create.html", context)


def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse("posts:post-list"))


def about(request):
    return render(request, 'posts/about.html')


def categoriesPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    categories = Category.objects.filter(title__icontains=q)
    return render(request, 'posts/categories.html', {'categories': categories})
