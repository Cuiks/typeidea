from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from config.models import SideBar
from .models import Tag, Post, Category
from comment.forms import CommentForm
from comment.models import Comment


def post_list(request, category_id=None, tag_id=None):
    tag = None
    category = None
    if tag_id:
        posts, tag = Post.get_by_tag(tag_id)
    elif category_id:
        posts, category = Post.get_by_category(category_id)
    else:
        posts = Post.latest_posts()
    context = {
        "category": category,
        "tag": tag,
        "post_list": posts,
        "sidebars": SideBar.get_all(),
    }
    context.update(Category.get_navs())

    return render(request, 'blog/list.html', context=context)


def post_detail(request, post_id=None):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        post = None

    context = {
        "post": post,
        "sidebars": SideBar.get_all(),
    }
    context.update(Category.get_navs())

    return render(request, 'blog/detail.html', context=context)


class CommonViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'sidebars': SideBar.get_all()
        })
        context.update(Category.get_navs())
        return context


class IndexView(CommonViewMixin, ListView):
    queryset = Post.latest_posts()  # 跟model一样 二选一。model没有过滤
    paginate_by = 5  # 分页  每页数量
    context_object_name = "post_list"  # 如果不指定该字段，在模板中使用object_list获取变量
    template_name = "blog/list.html"


class PostDetailView(CommonViewMixin, DetailView):
    queryset = Post.latest_posts()
    template_name = "blog/detail.html"
    context_object_name = "post"
    pk_url_kwarg = "post_id"  # 路由地址中字段名

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "comment_form": CommentForm,
            "comment_list": Comment.get_by_target(self.request.path)
        })
        return context


class CategoryView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id)
        context.update({
            'category': category
        })
        return context

    def get_queryset(self):
        """
        重写queryset逻辑，根据分类过滤
        :return:
        """
        queryset = super().get_queryset()
        category_id = self.kwargs.get('category_id')
        return queryset.filter(category_id=category_id)


class TagView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_id = self.kwargs.get('tag_id')
        tag = get_object_or_404(Tag, pk=tag_id)
        context.update({
            'tag': tag
        })
        return context

    def get_queryset(self):
        """
        重写queryset逻辑，根据分类过滤
        :return:
        """
        queryset = super().get_queryset()
        tag_id = self.kwargs.get('tag_id')
        return queryset.filter(tag__id=tag_id)


class SearchView(IndexView):
    def get_context_data(self):
        context = super().get_context_data()
        context.update({
            'keyword': self.request.GET.get("keyword", "")
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.GET.get("keyword")
        if not keyword:
            return queryset
        return queryset.filter(Q(title__icontains=keyword) | Q(desc__icontains=keyword))


class AuthorView(IndexView):
    def get_queryset(self):
        queryset = super().get_queryset()
        author_id = self.kwargs.get("owner_id")
        return queryset.filter(owner_id=author_id)
