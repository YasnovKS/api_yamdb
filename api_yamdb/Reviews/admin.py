from django.contrib import admin

from .models import Category, Genre


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name', 'slug')


class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name', 'slug')


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
