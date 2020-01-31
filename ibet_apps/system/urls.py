from system.views import permissionviews, logstreamview, cachehelperview, reportviews
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('api/getadminuser/', permissionviews.GetAdminUser.as_view(), name='get_admin_user'),
    path('api/getadminprofile/', permissionviews.GetAdminProfile.as_view(), name='get_admin_profile'),
    path('api/logstreamtos3/', csrf_exempt(logstreamview.LogStreamToS3.as_view()), name='log_stream_to_s3'),
    path('api/cachehelper/', csrf_exempt(cachehelperview.CacheHelperTest.as_view()), name='cache_helper'),
    path('api/history-analysis/', reportviews.UserGameBetHistory.as_view(), name="history_analysis")
]
