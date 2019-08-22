from django.conf.urls import url
from . import views

app_name = 'EyeMap2'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^visualise/$', views.visualise, name='visualise'),
    url(r'^analysis/$', views.analysis, name='analysis'),
    url(r'^new_experiment/$', views.new_experiment, name='new_experiment'),
    url(r'^save_new_experiment/$', views.save_new_experiment, name='save_new_experiment'),
    url(r'^check_font/$', views.check_font, name='check_font'),
    url(r'^register/$', views.register, name='register'),
    url(r'^user_login/$', views.user_login, name='user_login'),
    url(r'^user_logout/$', views.user_logout, name='user_logout'),
    # url(r'^update_aoi_data/$', views.update_aoi_data, name='update_aoi_data'),
    # url(r'^upload_font/$', views.upload_font, name='upload_font'),
    # url(r'^save_new_font/$', views.save_new_font, name='save_new_font'),
    # url(r'^poll_state/$', views.poll_state, name='poll_state'),
    # url(r'^update_fix_data/$', views.update_fix_data, name='update_fix_data'),
    url(r'^update_data/$', views.update_data, name='update_data'),
    url(r'^generate_file/$', views.generate_file, name='generate_file'),
    url(r'^gen_report/$', views.gen_report, name='gen_report'),
]
