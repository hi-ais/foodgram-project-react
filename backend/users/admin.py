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
    list_filter = ('username', 'email')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Follow)
