import requests
from django.contrib import admin

# Register your models here.
from django.contrib.admin.models import LogEntry
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.auth import get_permission_codename

from typeidea.base_admin import BaseOwnerAdmin
from .adminforms import PostAdminForm
from .models import Post, Category, Tag
from typeidea.custom_site import custom_site


class PostInline(admin.TabularInline):  # StackedInline 样式不同
    fields = ("title", "desc")
    extra = 1
    model = Post


@admin.register(Category, site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'is_nav', 'owner', 'created_time')
    fields = ('name', 'status', 'is_nav')
    # 标签页可以直接编辑文章
    inlines = [PostInline, ]

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(CategoryAdmin, self).save_model(request, obj, form, change)


@admin.register(Tag, site=custom_site)
class TagAdmin(BaseOwnerAdmin):
    list_display = ('name', 'status', 'owner', 'created_time')
    fields = ('name', 'status')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(TagAdmin, self).save_model(request, obj, form, change)


class CategoryOwnerFilter(admin.SimpleListFilter):
    """自定义过滤器只展示当前用户分类"""

    title = "分类过滤器"
    parameter_name = "owner_category"

    def lookups(self, request, model_admin):
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=self.value())
        return queryset


PERMISSION_API = "http://permission.sso.com/has__perm?user={}&perm_code={}"


@admin.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    # 自定义form
    form = PostAdminForm

    # 配置页面展示哪些字段
    list_display = (
        'title', 'category', 'status',
        'created_time', 'owner'
    )
    # 配置哪些字段可以作为链接，点击他们可以进入编辑页面
    list_display_links = []

    # 配置页面过滤器，可以通过哪些字段在页面进行过滤
    list_filter = [CategoryOwnerFilter]
    # 配置搜索字段
    search_fields = ['title', 'category__name']

    # 动作相关的配置，是否展示在顶部
    actions_on_top = True
    # 动作相关的配置，是否展示在底部
    actions_on_bottom = True

    # 保存、编辑、保存并新建按钮是否在顶部展示
    save_on_top = True

    # 调整页面展示
    # fields = (
    #     ('category', 'title'),
    #     'desc',
    #     'status',
    #     'content',
    #     'tag',
    # )

    fieldsets = (
        ('基础配置', {
            "description": "基础配置描述",
            "fields": (
                ("title", "category"),
                "status"
            )
        }),
        ("内容", {
            "fields": (
                "desc",
                "content"
            )
        }),
        ("额外信息", {
            "classes": ("collapse",),
            "fields": ("tag",),
        })
    )
    """
    fieldsets 用来控制布局，要求的格式是有两个元素的tuple的list，如:
    fieldsets = (
        (名称, { 内容 }),
        (名称, { 内容 })
    )
    第一个元素是当前板块的名称,第二部分是当前板块的描述、字段和样式配置。
    也就是说第一个是string,第二个是dict,dict的key可以是fields、description、classes
        fields 同上面一样,控制展示哪些元素,也可以给元素排序并组合元素位置
        classes 的作用是给配置的模块加上加上一些CSS属性, Django admin默认支持的是collapse和wide。当然也可以写其他属性，然后自己来处理样式
    """

    # filter_horizontal 或 filter_vertical 控制多对多字段的展示效果
    # filter_horizontal = ('tag',)
    filter_vertical = ('tag',)

    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('custom_site:blog_post_change', args=(obj.id,))
        )

    operator.short_description = "操作"

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(PostAdmin, self).save_model(request, obj, form, change)

    # 让用户只能看到自己的文章
    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)

    # 自定义静态资源加载
    # class Media:
    #     css = {
    #         "all": ("https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/css/bootstrap.min.css",)
    #     }
    #     js = ("https://cdn.jsdelivr.net/npm/bootstrap@3.3.7/dist/js/bootstrap.min.js",)

    # 自定义oss权限验证
    # def has_add_permission(self, request):
    #     opts = self.opts
    #     codename = get_permission_codename('add', opts)
    #     perm_code = "%s.%s" % (opts.app_label, codename)
    #     resp = requests.get(PERMISSION_API.format(request.user.username, perm_code))
    #     if resp.status_code == 200:
    #         return True
    #     else:
    #         return False


@admin.register(LogEntry, site=custom_site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = ['object_repr', 'object_id', 'action_flag', 'user', 'change_message']
