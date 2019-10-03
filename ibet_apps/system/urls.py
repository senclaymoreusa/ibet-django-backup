from system.views import permissionviews, logstreamview
from django.urls import path

urlpatterns = [
    path('api/getadminuser/', permissionviews.GetAdminUser.as_view(), name='get_admin_user'),
    path('api/getadminprofile/', permissionviews.GetAdminProfile.as_view(), name='get_admin_profile'),
    path('api/logstreamtos3/', logstreamview.LogStreamToS3.as_view(), name='log_stream_to_s3')
]