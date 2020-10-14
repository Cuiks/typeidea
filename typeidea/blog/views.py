from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from config.models import SideBar
from .models import Tag, Post, Category


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


class CommentViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'sidebars': SideBar.get_all()
        })
        context.update(Category.get_navs())
        return context


class IndexView(CommentViewMixin, ListView):
    queryset = Post.latest_posts()  # 跟model一样 二选一。model没有过滤
    paginate_by = 5  # 分页  每页数量
    context_object_name = "post_list"  # 如果不指定该字段，在模板中使用object_list获取变量
    template_name = "blog/list.html"


class PostDetailView(CommentViewMixin, DetailView):
    queryset = Post.latest_posts()
    template_name = "blog/detail.html"
    context_object_name = "post"
    pk_url_kwarg = "post_id"


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
        tag = get_object_or_404(Category, pk=tag_id)
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
        return queryset.filter(tag_id=tag_id)
