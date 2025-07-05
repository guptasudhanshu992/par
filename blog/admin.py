from django.contrib import admin
from .models import Blog, BlogCategory, BlogTag, Media

@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('-created_at',)

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'published_at', 'reading_time')
    list_filter = ('status', 'published_at', 'categories', 'tags')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['author', 'categories', 'tags']
    date_hierarchy = 'published_at'
    ordering = ('-published_at',)
    
    def get_changeform_initial_data(self, request):
        """
        Set the current user as the default author when opening the form.
        """
        return {'author': request.user.id}

@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ['title', 'media_type', 'uploaded_by', 'uploaded_at']
    search_fields = ['title', 'file']
    list_filter = ['media_type', 'uploaded_at']
    