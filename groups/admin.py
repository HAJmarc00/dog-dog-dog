from django.contrib import admin
from .models import Group, GroupMember, GroupInvite

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_public', 'created_at')
    search_fields = ('name', 'owner__username')  # فرض کردم user مدل username داره
    list_filter = ('is_public', 'created_at')
    readonly_fields = ('created_at',)
    # برای نمایش عکس آواتار در ادمین، می‌تونیم متدی اضافه کنیم
    def avatar_preview(self, obj):
        if obj.avatar:
            return f'<img src="{obj.avatar.url}" style="height: 50px;"/>'
        return "-"
    avatar_preview.allow_tags = True
    avatar_preview.short_description = 'Avatar Preview'
    # برای اضافه کردن preview توی فرم ادمین، میشه اینطوری
    fields = ('name', 'description', 'avatar', 'avatar_preview', 'is_public', 'owner', 'pinned_message', 'created_at')
    readonly_fields = ('created_at', 'avatar_preview')

@admin.register(GroupMember)
class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'is_admin', 'is_approved', 'joined_at')
    list_filter = ('is_admin', 'is_approved', 'joined_at')
    search_fields = ('user__username', 'group__name')
    readonly_fields = ('joined_at',)
    # اگر لازم داری بشه به سرعت ادمین یا تایید رو تغییر داد، می‌تونی این فیلدها رو توی لیست هم قابل ویرایش کنی:
    list_editable = ('is_admin', 'is_approved')

@admin.register(GroupInvite)
class GroupInviteAdmin(admin.ModelAdmin):
    list_display = ('group', 'inviter', 'code', 'is_used', 'created_at')
    list_filter = ('is_used', 'created_at')
    search_fields = ('group__name', 'inviter__username', 'code')
    readonly_fields = ('created_at',)

