from django.contrib import admin

# Register your models here.
from django.urls import reverse
from django.utils.html import format_html

from .models import Post, Category, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'is_nav', 'owner', 'created_time')
    fields = ('name', 'status', 'is_nav')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(CategoryAdmin, self).save_model(request, obj, form, change)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'owner', 'created_time')
    fields = ('name', 'status')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(TagAdmin, self).save_model(request, obj, form, change)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # 配置页面展示哪些字段
    list_display = (
        'title', 'category', 'status',
        'created_time', 'owner'
    )
    # 配置哪些字段可以作为链接，点击他们可以进入编辑页面
    list_display_links = []

    # 配置页面过滤器，可以通过哪些字段在页面进行过滤
    list_filter = ['category', ]
    # 配置搜索字段
    search_fields = ['title', 'category__name']

    # 动作相关的配置，是否展示在顶部
    actions_on_top = True
    # 动作相关的配置，是否展示在底部
    actions_on_bottom = True

    # 保存、编辑、保存并新建按钮是否在顶部展示
    save_on_top = True

    fields = (
        ('category', 'title'),
        'desc',
        'status',
        'content',
        'tag',
    )

    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('admin:blog_post_change', args=(obj.id,))
        )

    operator.short_description = "操作"

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(PostAdmin, self).save_model(request, obj, form, change)
