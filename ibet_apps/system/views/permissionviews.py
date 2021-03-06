from django.shortcuts import render
from xadmin.views import CommAdminView
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse

from system.models import UserGroup, PermissionGroup, UserToUserGroup, UserPermission

from users.models import CustomUser
from utils.constants import *
import simplejson as json
from django.views import View
from django.urls import reverse
from django.core import serializers
from system.models import *
import re
from django.db.models import Q

import logging
logger = logging.getLogger('django')


# Create your views here.
class PermissionGroupView(CommAdminView): 
    def get(self, request):
        pageSize = request.GET.get('pageSize')
        offset = request.GET.get('offset')
        department = request.GET.get('department')
        role = request.GET.get('role')
        market = request.GET.get('market')
        search = request.GET.get('search')
        getType = request.GET.get('type')

        if getType == 'get_select_admin_id':
            userIds = request.GET.get('userIds')
            logger.info('Select multiple admin user\'s ID which are: ' + str(userIds))
            userIds = json.loads(userIds)
            # print(userIds)
            response = []
            for userId in userIds:
                customUsers = CustomUser.objects.get(pk=userId)
                userMap = {
                    'username': customUsers.username,
                    'first_name': customUsers.first_name, 
                    'last_name': customUsers.last_name,
                    'userId': customUsers.pk
                }
                response.append(userMap)

            logger.info('Sending multiple admin user\'s data responses: ' + json.dumps(response))
            return JsonResponse({"data": response})

        if getType == 'edit_user_view':
            userId = request.GET.get('userId')
            # userId = int(userId)
            customUser = CustomUser.objects.get(pk=userId)
            logger.info('View admin user\'s: ' + str(customUser.username) + ' profile')
            department = ''
            if customUser.department:
                # for i in DEPARTMENT_LIST:
                #     if int(i['code']) == int(customUser.department):
                #         department = i['name']
                department = customUser.department
            response = {
                'userId': userId,
                'username': customUser.username,
                'password': "12345678",
                'first_name': customUser.first_name,
                'last_name': customUser.last_name,
                'email': customUser.email,
                'phone': customUser.phone,
                'department': department,
                'role': '',
                'ibetMarkets': [],
                'letouMarkets': []
            }
            if customUser.department:
                role = UserToUserGroup.objects.get(user=customUser)
                ibetMarkets = customUser.ibetMarkets
                ibetMarketsList = ibetMarkets.split(',')
                letouMarkets = customUser.letouMarkets
                letouMarketsList = letouMarkets.split(',')

                response.update(role=role.group.pk, ibetMarkets=ibetMarketsList, letouMarkets=letouMarketsList)
                
            logger.info('Sending admin user\'s "'  + str(customUser.username) + '" profile data response')
            return JsonResponse({ "data": response })

        # print(search, pageSize, offset, department, role, market)

        if pageSize is None:
            pageSize = 20
        else: 
            pageSize = int(pageSize)

        if offset is None:
            offset = 0
        else:
            offset = int(offset)

        context = super().get_context()
        title = _('Group Permission')
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context['title'] = title
        context['time'] = timezone.now()
        roles = UserGroup.objects.all()
        roles = serializers.serialize('json', roles)
        roles = json.loads(roles)
        dataResponse = []
        for r in roles:
            rolesResponse = {
                'roleName': r['fields']['name'],
                'roleId': r['pk']
            }
            dataResponse.append(rolesResponse)
        context['roles'] = dataResponse
        context['departments'] = DEPARTMENT_LIST
        context['imagePath'] = PUBLIC_S3_BUCKET + 'admin_images/'

        markets = {
            'ibetMarket_options': [],
            'letouMarket_options': []
        }
        for countryCode in MARKET_OPTIONS['ibetMarket_options']:
            markets['ibetMarket_options'].append({
                'code': countryCode,
                'name': COUNTRY_CODE_TO_IMG_PREFIX[countryCode]
            })
        for countryCode in MARKET_OPTIONS['letouMarket_options']:
            markets['letouMarket_options'].append({
                'code': countryCode,
                'name': COUNTRY_CODE_TO_IMG_PREFIX[countryCode]
            })

        context['markets'] = markets
        userPermissionList = []

        adminUsers = CustomUser.objects.filter(is_admin=True)
        adminCount = adminUsers.count()
        adminUsers = CustomUser.objects.filter(is_admin=True)[offset:offset+pageSize]
        
        filter = Q(is_admin=True)

        # print(str(search))
        if search:
            logger.info('Query user model by search key: %s',  search)
            filter &= (Q(username__icontains=search)|Q(first_name__icontains=search)|Q(last_name__icontains=search))

        if department:
            logger.info('Query user model by department ID: %s',  department)
            filter &= (
                Q(department=department)
            )

        if market:
            logger.info('Query user model by market ID: %s',  market)
            filter &= (
                Q(ibetMarkets__icontains=market)|Q(letouMarkets__icontains=market)
            )

        if role:
            logger.info('Query user group model by role ID: %s',  int(role))
            userToUserGroups = UserToUserGroup.objects.filter(group=role)
            userIds = []
            for userToUserGroup in userToUserGroups:
                userId = userToUserGroup.user.pk
                if userId not in userIds:
                    userIds.append(userId)
            # print(userIds)
            logger.info('Query user group model by user\'s IDs: [{0}]'.format(', '.join(map(str, userIds))))
            filter &= (
                Q(pk__in=userIds)
            )

        adminUsers = CustomUser.objects.filter(filter)
        adminUsersCount = adminUsers.count()

        adminUsers = adminUsers[offset:offset+pageSize]
        logger.info('Getting user\'s role data index from ' + str(offset) + ' to ' + str(int(offset)+ int(pageSize)))
        

        if offset == 0:
            context['isFirstPage'] = True
        else:
            context['isFirstPage'] = False
        
        if adminUsersCount <= offset+pageSize:
            context['isLastPage'] = True
        else:
            context['isLastPage'] = False

        for user in adminUsers: 
            if user.department:
                userRole = UserToUserGroup.objects.get(user=user)
                # departmentList = json.loads(DEPARTMENT_LIST)
                for i in DEPARTMENT_LIST:
                    # print(type(user.department))
                    # print(type(i['code']))
                    if int(i['code']) == int(user.department):
                        department = i['name']
                seperator = ', '
                ibetMarket = user.ibetMarkets.split(',')
                ibetMarket = seperator.join(ibetMarket)
                letouMarket = user.letouMarkets.split(',')
                letouMarket = seperator.join(letouMarket)
                userPermissionDict = {
                    'userId': user.pk,
                    'username': user.username,
                    'name': user.first_name + ' ' + user.last_name,
                    'department': department,
                    'role': userRole.group.name,
                    'ibetMarkets': ibetMarket,
                    'letouMarkets': letouMarket
                }
            else:
                userPermissionDict = {
                    'userId': user.pk,
                    'username': user.username,
                    'name': user.first_name + user.last_name,
                    'department': '',
                    'role': '',
                    'ibetMarkets': '',
                    'letouMarkets': ''
                }
            userPermissionList.append(userPermissionDict)


        # print(userPermissionList)
        context['userPermissionList'] = userPermissionList

        return render(request, 'group_user.html', context)

    def post(self, request):

        post_type = request.POST.get('type')
        if post_type == 'createUser':
            # print("!!!!!")
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            roleId = request.POST.get('role')
            departmentId = request.POST.get('department')
            ibetMarkets = request.POST.get('ibetMarkets')
            ibetMarketsList = ibetMarkets.split(',')
            letouMarkets = request.POST.get('letouMarkets')
            letouMarketsList = letouMarkets.split(',')

            logger.info('Create a new admin user username: {}, password: {}, email: {}, phone: {}, first_name: {}, last_name: {}, roleId: {}, departmentId: {}, ibetMarkets: {}, letouMarkets: {}' .format
                        (username, password, email, phone, first_name, last_name, roleId, departmentId, ibetMarkets, letouMarkets))
            
            if not departmentId or not departmentId.isdigit():
                return JsonResponse({ "code": 1, "message": "Please choose the department"})

            if not roleId or not roleId.isdigit():
                return JsonResponse({ "code": 1, "message": "Please choose the role"})

            if not username or not password or not email or not phone or not departmentId or not first_name or not last_name and (not ibetMarkets or not letouMarkets) :
                logger.error('Invalid data when create a new user')
                return JsonResponse({ "code": 1, "message": "invalid data"})
            
            if CustomUser.objects.filter(username=username).exists():
                logger.error('Username already be used when create a new user')
                return JsonResponse({ "code": 1, "message": "username already be used"})
            if CustomUser.objects.filter(email=email).exists():
                logger.error('Email already be used when create a new user')
                return JsonResponse({ "code": 1, "message": "email already be used"})

            if not re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email):
                logger.error('Email format is not correct when create a new user')
                return JsonResponse({ "code": 1, "message": "please enter valid email"})

            user = CustomUser.objects.create_superuser(username=username, email=email, phone=phone)
            # user.update(ibetMarkets=ibetMarkets, letouMarkets=letouMarkets, department=department)
            user.ibetMarkets = ibetMarkets
            user.letouMarkets = letouMarkets
            user.department = departmentId
            user.first_name = first_name
            user.last_name = last_name
            user.set_password(password)
            user.save()
            # print(ibetMarketsList)
            # print(letouMarketsList)
            group = UserGroup.objects.get(pk=roleId)
            UserToUserGroup.objects.create(group=group, user=user)

            logger.info('Successfully create a new role')
            return JsonResponse({ "code": 0, "message": "success create a new role"})

        if post_type == 'delete_admin_user':
            deleteUserIds = request.POST.get('userIds')
            deleteUserIds = json.loads(deleteUserIds)
            # print(deleteUserIds)
            for userId in deleteUserIds:
                CustomUser.objects.filter(pk=userId).delete()

            logger.info('Successfully delete a new role')
            return JsonResponse({ "code": 0, "message": "success delete users"})

        if post_type == 'updateRole':
            changeAccessUserIds = request.POST.get('updateUserIds')
            changeAccessUserIds = changeAccessUserIds.split(',')
            role = request.POST.get('roleSelect')
            departmentId = request.POST.get('department')
            ibetMarkets = request.POST.get('ibetMarkets')
            if ibetMarkets:
                ibetMarketsList = ibetMarkets.split(',')
            letouMarkets = request.POST.get('letouMarkets')
            if letouMarkets:
                letouMarketsList = letouMarkets.split(',')
            
            if not changeAccessUserIds or not role or not departmentId or not ibetMarkets or not letouMarkets:
                logger.error('Missing some input fields when update the role for certain users')
                return JsonResponse({ "code": 1, "message": "invalid data"})

            # print(changeAccessUserIds, role, departmentId, ibetMarketsList, letouMarketsList)


            for userId in changeAccessUserIds:
                user = CustomUser.objects.get(pk=userId)
                user.letouMarkets = letouMarkets
                user.ibetMarkets = ibetMarkets
                user.department = departmentId
                user.save()
                # .update(letouMarkets=letouMarkets, ibetMarkets=ibetMarkets)
                group = UserGroup.objects.get(pk=role)
                UserToUserGroup.objects.filter(user=user).update(group=group)

            logger.info('Successfully update new role to certain users: ' + str(changeAccessUserIds))
            return JsonResponse({ "code": 0, "message": "success update users role"})


        if post_type == 'updateUser':
            userId = request.POST.get('userId')
            username = request.POST.get('username')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            roleId = request.POST.get('role')
            departmentId = request.POST.get('department')
            ibetMarkets = request.POST.get('ibetMarkets')
            ibetMarketsList = ibetMarkets.split(',')
            letouMarkets = request.POST.get('letouMarkets')
            letouMarketsList = letouMarkets.split(',')

            if not departmentId or not departmentId.isdigit():
                return JsonResponse({ "code": 1, "message": "Please choose the department"})

            if not roleId or not roleId.isdigit():
                return JsonResponse({ "code": 1, "message": "Please choose the role"})
            # print(username, email, phone, first_name, last_name, roleId, departmentId, ibetMarkets, letouMarkets)

            if not username or not email or not phone or not departmentId or not first_name or not last_name and (not ibetMarkets or not letouMarkets):
                logger.error('Missing some input fields when update the user profile')
                return JsonResponse({ "code": 1, "message": "invalid data"})
            
            if CustomUser.objects.filter(username=username).exclude(pk=userId).exists():
                logger.error('Username already be used when update the user profile')
                return JsonResponse({ "code": 1, "message": "username already be used"})
            if CustomUser.objects.filter(email=email).exclude(pk=userId).exists():
                logger.error('Email already be used when update the user profile')
                return JsonResponse({ "code": 1, "message": "email already be used"})

            if not re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', email):
                logger.error('Email format is not correct when update the user profile')
                return JsonResponse({ "code": 1, "message": "please enter valid email"})


            user = CustomUser.objects.get(pk=userId)
            # user.update(ibetMarkets=ibetMarkets, letouMarkets=letouMarkets, department=department)
            user.ibetMarkets = ibetMarkets
            user.letouMarkets = letouMarkets
            user.department = departmentId
            user.first_name = first_name
            user.last_name = last_name
            user.phone = phone
            user.save()

            if roleId:
                group = UserGroup.objects.get(pk=roleId)
                UserToUserGroup.objects.filter(user=user).delete()
                UserToUserGroup.objects.create(user=user, group=group)

            logger.info("Successfully updated user")
            return JsonResponse({ "code": 0, "message": "success update users role"})

        

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
                return JsonResponse({ "code": 0, "message": "success"})
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
            return JsonResponse({ "code": 0, "message": "success updated"})
        


class GetAdminUser(View):

    def get(self, request):
        search = request.GET.get('search')
        i = 0
        adminUser = CustomUser.objects.filter(Q(is_staff=1)&(Q(username__icontains=search)|Q(first_name__icontains=search)|Q(last_name__icontains=search)))
        # print(str(adminUser))
        array = []
        for user in adminUser:
            response = {}
            # response['value'] = i
            # response['id'] = str(user.pk)
            response['username'] = str(user.username)
            # response['continent'] = "PERMISSION"
            # i += 1
            array.append(str(user.username))
        
        logger.info("Sending the search result by key: " + str(search))
        return HttpResponse(json.dumps(array), content_type='application/json')


class GetAdminProfile(View):

    def get(self, request):
        # print("!!!!")
        username = request.GET.get('username')

        adminUser = CustomUser.objects.get(username=username)

        response = {
            'username': adminUser.username,
            'first_name': adminUser.first_name,
            'last_name': adminUser.last_name,
            'email': adminUser.email,
            'phone': adminUser.phone
        }

        ibetMarketList = []
        if adminUser.ibetMarkets:
            countryCodes = adminUser.ibetMarkets.split(',')
            for countryCode in countryCodes:
                ibetMarketList.append({
                    'code': countryCode,
                    'name': COUNTRY_CODE_TO_IMG_PREFIX[countryCode]
                })

        letouMarketList = []
        if adminUser.letouMarkets:
            countryCodes = adminUser.letouMarkets.split(',')
            for countryCode in countryCodes:
                letouMarketList.append({
                    'code': countryCode,
                    'name': COUNTRY_CODE_TO_IMG_PREFIX[countryCode]
                })

        if adminUser.department:
            role = UserToUserGroup.objects.get(user=adminUser)
            department = ''
            for i in DEPARTMENT_LIST:
                if int(i['code']) == int(adminUser.department):
                    department = i['name']
        # print(role.group)
        # print(str(role.group.name))
            updateMap = {
                'ibetMarkets': ibetMarketList,
                'letouMarkets': letouMarketList,
                'department':  department,
                'roleName': role.group.name or ''
            }
        
        else:
            updateMap = {
                'ibetMarkets': ibetMarketList,
                'letouMarkets': letouMarketList,
                'department':  '',
                'roleName': ''
            }
        
        response.update(updateMap)
        # print(response)
        logger.info("Sending the user profile : " + str(username) + ', data: ' + json.dumps(response))
        return JsonResponse({ "code": 0, "data": response})
