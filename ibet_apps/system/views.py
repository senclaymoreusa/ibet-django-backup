from django.shortcuts import render
from xadmin.views import CommAdminView
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

from .models import UserGroup, PermissionGroup, UserToUserGroup, UserPermission

from users.models import CustomUser
from utils.constants import *
import simplejson as json
from django.views import View
from django.urls import reverse
from django.core import serializers
from .models import *

import logging
logger = logging.getLogger('django')

# Create your views here.
class PermissionGroupView(CommAdminView): 
    def get(self, request):
        context = super().get_context()
        title = _('Group Permission')
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context['title'] = title
        context['time'] = timezone.now()
        roles = UserGroup.objects.all()
        roles = serializers.serialize('json', roles)
        roles = json.loads(roles)
        dataResponse = []
        for role in roles:
            rolesResponse = {
                'roleName': role['fields']['name'],
                'roleId': role['pk']
            }
            dataResponse.append(rolesResponse)
        context['roles'] = dataResponse
        return render(request, 'group_user.html', context)

    def post(self, request):

        post_type = request.POST.get('type')
        if post_type == 'createUser':
            print("!!!!!")

        # groupName = request.POST.get('groupName')
        # users = request.POST.get('hidden_permission_user')
        # permissionCode = request.POST.get('hidden_permission_code')
        # # print("users: " + users + "permission: " + permissionCode + 'groupName: ' + groupName)
        
        # group = UserGroup.objects.get_or_create(name=groupName, description='', groupType=PERMISSION_GROUP)
        # # groupId = group.pk

        # insert_permissions_list = []
        # users = json.loads(users)
        # permissionCode = json.loads(permissionCode)
        # for i in range(len(permissionCode)):
        #     insert_permissions_list.append(PermissionGroup(group=group, permission_code=permissionCode[i]))
        # # print(insert_permissions_list)
        # PermissionGroup.objects.bulk_create(insert_permissions_list)

        # insert_users_list = []
        # for i in range(len(users)):
        #     userId = int(users[i])
        #     user = CustomUser.objects.get(pk=userId)
        #     insert_users_list.append(UserToUserGroup(group=group, user=user))
        # # print(insert_users_list)
        # UserToUserGroup.objects.bulk_create(insert_users_list)

        return HttpResponseRedirect(reverse('xadmin:permission_group'))
            

class PermissionRoleView(CommAdminView): 
    def get(self, request):
        context = super().get_context()
        title = _('Roles')
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context['title'] = title
        context['time'] = timezone.now()

        pageSize = request.GET.get('pageSize')
        offset = request.GET.get('offset')
        get_type = request.GET.get('type')

        if get_type == 'view_permission':
            groupName = request.GET.get('groupName')
            logger.info("Viewing the permission group name: " + str(groupName))
            group = UserGroup.objects.get(name=groupName)
            permissions = PermissionGroup.objects.filter(group=group)
            # print(permissions)
            data = serializers.serialize('json', permissions)
            logger.info("Get the permission base on the group name: " + str(data))
            data = json.loads(data)
            permissions = []
            for i in data:
                # permissionsMap = {
                #     'permission': i.permission_code
                # }
                permissions.append(i['fields']['permission_code'])
            # print(permissions)
            response = {
                "code": 0,
                "data": permissions, 
                "groupName": groupName,
                "groupId": group.pk
            }
            if group.approvals:
                response.update(approvals=group.approvals.pk)
                logger.info("This permission group is approved by: " + str(group.approvals.name) + "which foregin key is: " + str(group.approvals.pk))
            # print(response)
            logger.info("Send the response for viewing one role of permission:" + str(response))
            return JsonResponse(response)

        if pageSize is None:
            pageSize = 20
        else: 
            pageSize = int(pageSize)

        if offset is None:
            offset = 0
        else:
            offset = int(offset)

        context['permissionList'] = PERMISSION_CODE
        
        userGroup = UserGroup.objects.all()
        userGroupAllLen = userGroup.count()
        userGroup = UserGroup.objects.all()[offset:offset+pageSize]

        if offset == 0:
            context['isFirstPage'] = True
        else:
            context['isFirstPage'] = False
        
        if userGroupAllLen <= offset+pageSize:
            context['isLastPage'] = True
        else:
            context['isLastPage'] = False

        data = serializers.serialize('json', userGroup)
        data = json.loads(data)
        logger.info("Display all role:" + str(data))
        # print(data)
        permissionGroupName = []
        permissionMap = {}
        for i in data:
            permissionMap = {
                'groupName': i['fields']['name'],
                # 'approvals': approvalGroup,
            }

            if i['fields']['approvals']:
                approvalGroup = UserGroup.objects.get(pk=i['fields']['approvals'])
                permissionMap.update({'approvals': approvalGroup.name})

            userCount = UserToUserGroup.objects.filter(group__name=i['fields']['name']).count()
            permissionMap.update(
                { 'userCount': userCount }
            )
            # print(i['fields']['approvals'])
            # print(permissionMap['userCount'])
            permissionGroupName.append(permissionMap)
        
        context['approvalOption'] = userGroup
        context['permission'] = permissionGroupName
        # print(permissionGroupName)
        # print(context['permissionList'])

        logger.info("Rendering the roles.html.......")
        return render(request, 'roles.html', context)

    def post(self, request):

        post_type = request.POST.get('type')
        # print(str(post_type))
        # print(str(request.user))
        groupId = request.POST.get('pk')
        groupName = request.POST.get('roleName')
        approvals = request.POST.get('approval')
        # member = request.POST.get('Members')
        memeber_list = request.POST.get('Members list')
        memeber_detail = request.POST.get('Member details')
        report = request.POST.get('Report')
        bonuses = request.POST.get('Bonuses')
        risk_control = request.POST.get('Risk control')
        # marketing = request.POST.get('Marketing')
        vip = request.POST.get('VIP')
        telesales = request.POST.get('Telesales')
        interal_messaging = request.POST.get('Interal messaging')
        # affiliates = request.POST.get('Affiliates')
        affiliates_list = request.POST.get('Affiliates list')
        affiliate_details  = request.POST.get('Affiliate details')
        # messaging = request.POST.get('Messaging')
        messages = request.POST.get('Messages')
        group = request.POST.get('Group')
        campaigns = request.POST.get('Campaigns')
        # finance = request.POST.get('Finance')
        deposit = request.POST.get('Deposits')
        withdrawals = request.POST.get('Withdrawals')
        settings = request.POST.get('Settings')
        content_management = request.POST.get('Content management')
        # system_admin = request.POST.get('System admin')
        users = request.POST.get('Users')
        roles = request.POST.get('Roles')

        arr = []

        arr.append(memeber_list)
        arr.append(memeber_detail)
        # arr.append(report)
        # arr.append(bonuses)
        # arr.append(risk_control)
        arr.append(vip)
        arr.append(telesales)
        arr.append(interal_messaging)
        arr.append(affiliates_list)
        arr.append(affiliate_details)
        arr.append(messages)
        arr.append(group)
        arr.append(campaigns)
        arr.append(deposit)
        arr.append(withdrawals)
        arr.append(settings)
        # arr.append(content_management)
        arr.append(users)
        arr.append(roles)

        # print(arr)
        logger.info("New role created and the permission codes are:" + str(arr))
        # print(groupId)
        # print( memeber_list, memeber_detail, report, bonuses, risk_control, vip, telesales, interal_messaging, affiliates_list)
        # print( affiliate_details, messages, group, campaigns, deposit, withdrawals, settings, content_management, users, roles)

        if post_type == 'createPermission':
            if groupName and not UserGroup.objects.filter(name=groupName).exists():
                # print(str(groupName))
                approvals = int(approvals)
                if approvals != 0: 
                    approval = UserGroup.objects.get(pk=approvals)
                    group = UserGroup.objects.create(name=groupName, groupType=PERMISSION_GROUP, approvals=approval)
                else:
                    group = UserGroup.objects.create(name=groupName, groupType=PERMISSION_GROUP)
                # groupId = group.pk
                # print(str(group))
                objs = [
                    PermissionGroup(
                        group=group,
                        permission_code=e
                    )
                    for e in arr
                ]

                permissions = PermissionGroup.objects.bulk_create(objs)
                logger.info("Successfully created all the permissions")
                return JsonResponse({ "code": 0, "message": "sucess"})
                # print(str(permissions))
            else:
                logger.info("The group name" + str(groupName) + " already exsit")
                return JsonResponse({ "code": 1, "message": "group name already exsit"})

        elif post_type == 'updatePermission':
            if groupName:
                group = UserGroup.objects.get(pk=groupId)
                if group.name != groupName:
                    logger.info("Updating the group name from {} to {}".format(group.name, groupName))
                    UserGroup.objects.filter(pk=groupId).update(name=groupName)

                PermissionGroup.objects.filter(group=group).delete()
                
                objs = [
                    PermissionGroup(
                        group=group,
                        permission_code=e
                    )
                    for e in arr
                ]
                permissions = PermissionGroup.objects.bulk_create(objs)
            logger.info("Successfully updated all the permissions")
            return JsonResponse({ "code": 0, "message": "sucess updated"})
        




class GetAdminUser(View):

    def get(self, request):
        i = 0
        adminUser = CustomUser.objects.filter(is_staff=1)
        # print(str(adminUser))
        array = []
        for user in adminUser:
            response = {}
            response['value'] = i
            response['id'] = str(user.pk)
            response['text'] = str(user.username)
            response['continent'] = "PERMISSION"
            i += 1
            array.append(response)
        
        return HttpResponse(json.dumps(array), content_type='application/json')
