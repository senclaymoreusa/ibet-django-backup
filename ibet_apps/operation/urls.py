
from . import views
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('api/read_message/<int:pk>', csrf_exempt(views.NotificationUserIsReadAPI.as_view()), name="read_message"),
    path('api/delete_message/<int:pk>', csrf_exempt(views.NotificationUserIsDeleteAPI.as_view()), name="delete_message"),
    path('api/notification-detail/<int:pk>', views.NotificationDetailAPIView.as_view(), name='notification-detail'),
    path('api/notification', views.NotificationAPIView.as_view(), name='notification'),
    path('api/notification-log', views.NotificationLogView.as_view(), name='notification-log'),
    path('api/notification-count/<int:pk>', views.NotificationToUsersUnreadCountView.as_view(), name='notification-count'),
    path('api/notificationsforuser', views.NotificationsForUserAPIView.as_view(), name='notificationsforuser'),
    path('api/notification-users/<int:pk>', views.NotificationToUsersDetailView.as_view(), name='notification-users'),
    path('api/notification-users', views.NotificationToUsersView.as_view(), name='notification-users'),
    path('api/create-topic', views.AWSTopicView.as_view(), name='create-topic'),
    path('api/create-message', views.CreateNotificationAPIView.as_view(), name='create-message'),
    path('api/notifier-search/', views.NotifierSearchAutocomplete.as_view(), name='notifier-search'),
    path('api/notifier-tags', views.NotifierTagsInput.as_view(), name='notifier-tags'),
    path('api/notification-search/', views.NotificationSearchAutocomplete.as_view(), name='notification-search'),
    path('api/timerange/', views.NotificationDateFilterAPI.as_view(), name='timerange'),
    path('api/group-filter', views.MessageGroupUserAPI.as_view(), name='group-filter'),
    path('api/group-detail', views.MessageGroupDetailAPI.as_view(), name='group-detail'),
    path('api/group-update/', views.MessageGroupUpdateAPI.as_view(), name='group-update'),
    path('api/user-valid/', views.UserIsValidAPI.as_view(), name='user-valid'),
    path('api/static-group-validation/', views.StaticGroupValidationAPI.as_view(), name='static-group-validation'),
]