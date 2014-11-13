from django.conf.urls import include, url

from skills import views

urlpatterns = (
    url(r'^$', views.index, name='skills'),
)
