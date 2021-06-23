
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from pdref import views
from users import views as user_views
from stats import views as stats_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('index/', views.index, name='index'),
    path('newrec/', views.newrec, name='newrec'),
    path('fulldets/<int:id>/<dir>/<dup>/', views.fulldets, name='fulldets'),
    path('fulldets/<int:id>/<dir>/<dup>/<msg>/', views.fulldets, name='fulldets'),
    path('delete/<int:id>/', views.delete, name='delete'),

    # URL routing for statistics function
    path('stats/', stats_views.stats, name='stats'),

    # URL routing for pdf printing function
    path('pdfprint/', views.pdfprint, name='pdfprint'),
    path('pdflist/<doctype>/<filename>/', views.pdflist, name='pdflist'),

    # URL routing for user authentication functions...
    path('register/', user_views.register, name='register'),
    path('login/', user_views.login_user, name='login'),
    path('logout/', user_views.logout_user, name='logout'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
