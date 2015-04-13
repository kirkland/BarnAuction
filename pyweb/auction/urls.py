from django.conf.urls import patterns, url

from auction import views

urlpatterns = patterns('', 
        url(r'^$', views.index, name='index'), 
        url(r'^bill/', views.bill, name='bill' ),
        url(r'^winners/', views.winners, name='winners' ),
)
