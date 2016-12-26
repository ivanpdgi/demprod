from django.conf.urls import url

from . import views

app_name = 'demprod'

urlpatterns = [
    url(r'^catalog/$', views.categoryes, name='categoryes'),
    url(r'^add2basket/$', views.detail_basket, name='detail_basket'),
    url(r'^export_products/$', views.export_products, name='export_products'),
    url(r'^import_products/$', views.import_products, name='import_products'),
    url(r'^export_categorys/$', views.export_categorys, name='export_categorys'),
    url(r'^export_baskets/$', views.export_baskets, name='export_baskets'),
]