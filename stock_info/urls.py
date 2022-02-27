from django.contrib import admin
from django.urls import path
from stock_info import views
from django.conf.urls import url
''' All URLS used for webpages are customized or created here. '''
urlpatterns = [
    # url(r'^covidin$',views.COVID_India_request),
    url(r'^$', views.index,name='home'),
    url(r'^nse$',views.nse,name="nse_indices"),
    url(r'^stock/(.*)$',views.stock,name='stock'),
    url(r'^indices/(.*)$',views.indices,name='index'),
    url(r'^base$',views.base,name='base'),
    url(r'^news$',views.news,name='news')
]