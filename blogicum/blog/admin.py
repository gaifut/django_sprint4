from django.contrib import admin

from .models import Category, Location, Post

admin.site.empty_value_display = 'Не задано'


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'text',
        'is_published',
        'created_at',
        'pub_date',
        'author',
        'category',
        'location'
    )

    list_editable = (
        'is_published',
        'pub_date',
        'category'
    )

    search_fields = ('title',)
    list_filter = ('category',)
    list_display_links = ('title',)


class PostInline(admin.TabularInline):
    model = Post
    extra = 0


class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
    )


admin.site.register(Category, CategoryAdmin)
admin.site.register(Location)
admin.site.register(Post, PostAdmin)
