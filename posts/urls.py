from django.urls import path, re_path
from posts import views
from posts.views import UserPostListView, post_list, post_create, post_detail, post_update, post_delete, search, post, \
    CategoryView

app_name = 'posts'
urlpatterns = [
    path('', post_list, name='post-list'),
    path('post/<id>', post, name='post-detail'),
    re_path(r'^user/(?P<username>\w{0,50})/$', UserPostListView.as_view(), name='user-posts'),
    path('search/', search, name='search'),
    path('create/', post_create, name='post-create'),
    path('post/<id>/', post_detail, name='post-detail'),
    path('post/<id>/update/', post_update, name='post-update'),
    path('post/<id>/delete/', post_delete, name='post-delete'),

    path("author/<int:author_id>/", views.PostListAuthor.as_view(), name="author"),
    path('categories/<str:cats>/', CategoryView, name='categories'),

    path('about/', views.about, name="blog-about"),
]
