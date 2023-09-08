from django.contrib import admin

from users.models import Subscriptions, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
    )
    list_filter = ('email', 'username',)
    search_fields = ('email', 'username',)


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'author',)
    list_editable = ('user', 'author')
