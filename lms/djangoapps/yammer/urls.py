"""
URLs for Yammer.
"""
from django.conf.urls import patterns, url

urlpatterns = patterns('yammer.views',
    url(r'', 'yammer', name='yammer'),
)
