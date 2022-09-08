from django.contrib import admin
from .models import Pilot, PendingPilot

# Register your models here.
class PendingPilotAdmin(admin.ModelAdmin):
    list_display = ['first_name']


class Filter(admin.ModelAdmin):
    list_display =  ('e_id', 'first_name', 'last_name', 'extra', 'extra_locked', 'approved')
    readonly_fields = ('extra_locked',)
    actions = ['approve']

    @admin.action(description='Approve')
    def approve(self, request, queryset):
        queryset.update(approved=True)


# class Filter1(admin.ModelAdmin):
#     list_display =  ('e_id', 'first_name', 'last_name', 'extra', 'approved')
#     actions = ['approve_inactive', 'approve_active']
# 
#     @admin.action(description='Approve & Inactive')
#     def approve_inactive(self, request, queryset):
#         for obj in queryset:
#             obj, create = Pilot.objects.update_or_create(e_id=obj.e_id,
#                                                          defaults={'first_name': obj.first_name,
#                                                                    'last_name': obj.last_name,
#                                                                    'extra': obj.extra})
#             
#             # tosave = Pilot(e_id=obj.e_id, first_name=obj.first_name, last_name=obj.last_name, extra_locked=obj.extra)
#             # Pilot.save(tosave)
#             obj.delete()
# 
# 
#     @admin.action(description='Approve & Active')
#     def approve_active(self, request, queryset):
#         print('approved')


admin.site.register(Pilot, Filter)
# admin.site.register(PendingPilot, Filter1)
