# coding: utf-8

from django.contrib import admin
from .models import Organization, OrganizationType


#########################
# Class: OrganizationAdmin
#########################

class OrganizationAdmin(admin.ModelAdmin):
    search_fields = ['full_name', 'short_name']
    list_display = ['full_name', 'short_name', 'homepage']
    list_filter = ['country__full_name']
    exclude = ['slug']


#########################
# Class: OrganizationTypeAdmin
#########################

class OrganizationTypeAdmin(admin.ModelAdmin):
    model = OrganizationType
    list_display = ['name', 'description']


##################################################
# Register classes
##################################################

admin.site.register(Organization, OrganizationAdmin)
admin.site.register(OrganizationType, OrganizationTypeAdmin)
