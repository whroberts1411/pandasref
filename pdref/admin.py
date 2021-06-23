from django.contrib import admin
from .models import PandasRef, Category, AppliesTo

#------------------------------------------------------------------------------
class PandasRefAdmin(admin.ModelAdmin):

    list_display = ('command','appliesto', 'category')
    ordering = ('command', 'appliesto')
    search_fields = ('command',)

#------------------------------------------------------------------------------
class CategoryAdmin(admin.ModelAdmin):

    list_display = ('category',)
    ordering = ('category',)
    search_fields = ('category',)

#------------------------------------------------------------------------------
class AppliesToAdmin(admin.ModelAdmin):

    list_display = ('appliesto',)
    ordering = ('appliesto',)
    search_fields = ('appliesto',)

#------------------------------------------------------------------------------

admin.site.register(PandasRef, PandasRefAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(AppliesTo, AppliesToAdmin)

#------------------------------------------------------------------------------