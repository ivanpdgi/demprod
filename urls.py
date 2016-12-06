from django.conf.urls import url

from . import views

app_name = 'demprod'

urlpatterns = [
    url(r'^export_products/$', views.export_products, name='export_products'),
    url(r'^import_products/$', views.import_products, name='import_products'),
]