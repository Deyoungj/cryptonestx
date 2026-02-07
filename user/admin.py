from django.contrib import admin
from .models import CustomUser, Profile
import re
from django.http import HttpResponseRedirect
from django.urls import path
from django.db.models import Q
from django.contrib import messages

class CustomUserAdmin(admin.ModelAdmin):
    search_fields = ['email']
    actions = ['delete_users_with_links']
    
    # Define a custom action
    def delete_users_with_links(self, request, queryset):
        # Regex pattern to detect specific content, e.g., URLs
        pattern = re.compile(r'https?://[^\s/$.?#].[^\s]*')
        
        # Filter users whose full_name contains a URL
        # users_to_delete = queryset.filter(full_name__iregex=pattern.pattern)
        users_to_delete = CustomUser.objects.filter(Q(full_name__iregex=pattern.pattern))
        count = users_to_delete.count()
        
        print('users', users_to_delete)
        print('users count', count)

        # Delete matched users
        users_to_delete.delete()
        
        # if count:
        #     modeladmin.message_user(request, f"Deleted {count} user(s) with URLs in their full name.", messages.SUCCESS)
        # else:
        #     modeladmin.message_user(request, "No users with URLs found.", messages.INFO)

        # Notify the admin of the deletion
        self.message_user(request, f"Deleted {count} user(s) with URLs in their full name.")

    delete_users_with_links.short_description = "delete_users_with_links"
    
    
    

    
    
    
class ProfileAdmin(admin.ModelAdmin):
    search_fields = ['user__email']
    

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)