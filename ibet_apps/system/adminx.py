from xadmin import views
import xadmin
from system.views.permissionviews import PermissionGroupView, PermissionRoleView
from system.views.reportviews import ReportView

# xadmin.site.register_view(r'userdetail/(?P<pk>\d+)/$', UserDetailView, name='user_detail')
# xadmin.site.register_view(r'userdetail/$', UserDetailView, name='user_detail')
xadmin.site.register_view(r'permission/', PermissionGroupView, name='permission_group')
xadmin.site.register_view(r'roles/', PermissionRoleView, name='permission_roles')
xadmin.site.register_view(r'performance-report/', ReportView, name='performance_report')