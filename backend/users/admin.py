from django.contrib import admin
from django.contrib.auth import get_user_model
from users.models import Follow

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email'
    )
    search_fields = ('first_name', 'last_name', 'email',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('user__username',
                     'author__email',)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
