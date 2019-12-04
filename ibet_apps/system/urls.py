from system.views import permissionviews, logstreamview, cachehelperview
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from background.tasks import onebook_getBetDetail, kaiyuan_getBets

urlpatterns = [
    path('api/getadminuser/', permissionviews.GetAdminUser.as_view(), name='get_admin_user'),
    path('api/getadminprofile/', permissionviews.GetAdminProfile.as_view(), name='get_admin_profile'),
    path('api/logstreamtos3/', logstreamview.LogStreamToS3.as_view(), name='log_stream_to_s3'),
    path('api/cachehelper/', csrf_exempt(cachehelperview.CacheHelperTest.as_view()), name='cache_helper')
]

# demo_task(repeat=5)


