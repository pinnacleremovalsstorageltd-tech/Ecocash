from django.contrib import admin

class BaseAdmin(admin.ModelAdmin):
    actions_on_top = True
    actions_on_bottom = True
    list_per_page = 25
    save_on_top = True
    show_full_result_count = True

admin.site.site_header = 'EcoCash Partner Portal'
