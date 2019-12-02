from system.views import permissionviews, logstreamview, cachehelperview
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

# import games.views.kygameviews as kyviews

# kyviews.getBets(repeat=300, repeat_until=None)

from background.tasks import demo_task, onebook_getBetDetail, kaiyuan_getBets

urlpatterns = [
    path('api/getadminuser/', permissionviews.GetAdminUser.as_view(), name='get_admin_user'),
    path('api/getadminprofile/', permissionviews.GetAdminProfile.as_view(), name='get_admin_profile'),
    path('api/logstreamtos3/', logstreamview.LogStreamToS3.as_view(), name='log_stream_to_s3'),
    path('api/cachehelper/', csrf_exempt(cachehelperview.CacheHelperTest.as_view()), name='cache_helper')
]

demo_task(repeat=5)
onebook_getBetDetail(repeat=300,repeat_until=None)
kaiyuan_getBets(repeat=300, repeat_until=None)

