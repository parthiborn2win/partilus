from django.conf.urls.defaults import patterns, include, url
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
     url(r'^$', 'partilus.common.views.home', name='home'),
     
     url(r'^addfolder/(\w+)/$','partilus.common.views.addfolder',name='addfolder'),
     url(r'^searchfile/$', 'partilus.common.views.searchfile', name='searchfile'),
     url(r'^copy/(\w+)/$', 'partilus.common.views.copy', name='copy'),
     url(r'^paste/$', 'partilus.common.views.paste', name='paste'),
     url(r'^delete/$', 'partilus.common.views.delete', name='delete'),
     
     (r'^site_media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT }),
    

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     url(r'^admin/', include(admin.site.urls)),
)
