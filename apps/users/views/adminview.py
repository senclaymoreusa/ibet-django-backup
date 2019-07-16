from xadmin.views import CommAdminView
from django.core import serializers
from django.http import HttpResponse
from django.db.models import Sum
from datetime import timedelta
from django.db.models import Q
import boto3
from botocore.exceptions import ClientError
from botocore.exceptions import NoCredentialsError
from django.conf import settings
from django.utils import timezone
from ..models import *
from accounting.models import Transaction
from django.shortcuts import render

import logging


logger = logging.getLogger('django')


class UserDetailView(CommAdminView):
    def get(self, request, *args, **kwargs):
        context = super().get_context()
        title = 'Member ' + self.kwargs.get('pk')
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context["title"] = title
        context['time'] = timezone.now()
        customUser = CustomUser.objects.get(pk=self.kwargs.get('pk'))
        context['customuser'] = customUser
        context['userPhotoId'] = self.download_user_photo_id(customUser.username)
        context['userLoginActions'] = UserAction.objects.filter(user=customUser, event_type=0)[:20]
        transaction = Transaction.objects.filter(user_id=customUser)


        statusMap = {}
        for t in Transaction._meta.get_field('status').choices:
            statusMap[t[0]] = t[1]

        transTypeMap = {}
        for t in Transaction._meta.get_field('transaction_type').choices:
            transTypeMap[t[0]] = t[1]
        
        productMap = {}
        for t in Transaction._meta.get_field('product').choices:
            productMap[t[0]] = t[1]

        currencyMap = {}
        for t in Transaction._meta.get_field('currency').choices:
            currencyMap[t[0]] = t[1]
        
        channelMap = {}
        for t in Transaction._meta.get_field('channel').choices:
            channelMap[t[0]] = t[1]


        if Transaction.objects.filter(user_id=customUser).count() == 0:
            context['userTransactions'] = ''
        else:
            transactions = Transaction.objects.filter(user_id=customUser).order_by("-request_time")[:20]
            transactions = serializers.serialize('json', transactions)
            transactions = json.loads(transactions)

            trans = []
            for tran in transactions:
                try:
                    time = datetime.datetime.strptime(tran['fields']['request_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(tran['fields']['request_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %I:%M %p")
                transDict = {
                    'transactionId': str(tran['pk']),
                    'category': str(transTypeMap[tran['fields']['transaction_type']]),
                    'transType': transTypeMap[tran['fields']['transaction_type']],
                    'transTypeCode': tran['fields']['transaction_type'],
                    'product': productMap[tran['fields']['product']],
                    'toWhichWallet': str(tran['fields']['transfer_to']),
                    'currency': currencyMap[tran['fields']['currency']],
                    'time': time,
                    'amount': tran['fields']['amount'],
                    'balance': tran['fields']['amount'],
                    'status': statusMap[tran['fields']['status']],
                    'bank': str(tran['fields']['bank']),
                    'channel': channelMap[tran['fields']['channel']],
                    'method': tran['fields']['method'],
                }
                # transDict = serializers.serialize('json')
                trans.append(transDict)
            context['userTransactions'] = trans
            

        userLastLogin = UserAction.objects.filter(user=customUser, event_type=0).order_by('-created_time').first()   
        context['userLastIpAddr'] = userLastLogin
        context['loginCount'] = UserAction.objects.filter(user=customUser, event_type=0).count()

        transaction = Transaction.objects.filter(user_id=customUser)
        if transaction.count() <= 20:
            context['isLastPage'] = True
        else:
            context['isLastPage'] = False

        depositAmount = Transaction.objects.filter(user_id=customUser, transaction_type=0).aggregate(Sum('amount'))
        withdrawAmount = Transaction.objects.filter(user_id=customUser, transaction_type=1).aggregate(Sum('amount'))
        depositCount = Transaction.objects.filter(user_id=customUser, transaction_type=0).count()
        withdrawCount = Transaction.objects.filter(user_id=customUser, transaction_type=1).count()
        bonusAmount = Transaction.objects.filter(user_id=customUser, transaction_type=6).aggregate(Sum('amount'))

        if bonusAmount['amount__sum'] is None:
            bonusAmount['amount__sum'] = 0
        if withdrawAmount['amount__sum'] is None:
            withdrawAmount['amount__sum'] = 0
        if depositAmount['amount__sum'] is None:
            depositAmount['amount__sum'] = 0

        if depositAmount['amount__sum'] == 0:
            withdrawRate = 0
            bonusRate = 0
        else:
            withdrawRate = withdrawAmount['amount__sum']/depositAmount['amount__sum']
            bonusRate = bonusAmount['amount__sum']/depositAmount['amount__sum']
        
        context['withdrawDepositRate'] = "%.2f" % withdrawRate
        context['bonusDepositRate'] = "%.2f" % bonusRate
        context['depositCount'] = depositCount
        context['withdrawCount'] = withdrawCount
        context['depositAmount'] = depositAmount['amount__sum']
        context['withdrawAmount'] = withdrawAmount['amount__sum']
        
        if userLastLogin is None:
            context['relativeAccount'] = ''
        else:
            context['relativeAccount'] = self.account_by_ip(userLastLogin.ip_addr, userLastLogin.user)
        # print(str(context['relativeAccount']))

        deposits = Transaction.objects.filter(user_id=customUser, transaction_type=0).order_by('-request_time').first()
        if deposits:
            deposits = serializers.serialize('json', [deposits])
            deposits = json.loads(deposits)
            lastDeposit = []
            for deposit in deposits:
                try:
                    time = datetime.datetime.strptime(deposit['fields']['request_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(deposit['fields']['request_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %I:%M %p")
                depositDict = {
                    'transactionId': str(deposit['pk']),
                    'category': str(transTypeMap[deposit['fields']['transaction_type']]),
                    'transType': transTypeMap[deposit['fields']['transaction_type']],
                    'transTypeCode': deposit['fields']['transaction_type'],
                    'product': productMap[deposit['fields']['product']],
                    'toWhichWallet': str(deposit['fields']['transfer_to']),
                    'currency': currencyMap[deposit['fields']['currency']],
                    'time': time,
                    'amount': deposit['fields']['amount'],
                    'status': statusMap[deposit['fields']['status']],
                    'bank': str(deposit['fields']['bank']),
                    'channel': channelMap[deposit['fields']['channel']],
                    'method': deposit['fields']['method'],
                }
                lastDeposit.append(depositDict)
            context['lastDeposits'] = lastDeposit[:1]
        else:
            context['lastDeposits'] = ''

        withdraws = Transaction.objects.filter(user_id=customUser, transaction_type=1).order_by('-request_time').first() 
        if withdraws:
            withdraws = serializers.serialize('json', [withdraws])
            withdraws = json.loads(withdraws)
            lastWithdraw = []
            for withdraw in withdraws:
                try:
                    time = datetime.datetime.strptime(withdraw['fields']['request_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(withdraw['fields']['request_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %I:%M %p")
                withdrawDict = {
                    'transactionId': str(withdraw['pk']),
                    'category': withdraw['fields']['transaction_type'],
                    'transType': transTypeMap[withdraw['fields']['transaction_type']],
                    'transTypeCode': withdraw['fields']['transaction_type'],
                    'product': productMap[withdraw['fields']['product']],
                    'toWhichWallet': str(withdraw['fields']['transfer_to']),
                    'currency': currencyMap[withdraw['fields']['currency']],
                    'time': time,
                    'amount': withdraw['fields']['amount'],
                    'status': statusMap[withdraw['fields']['status']],
                    'bank': str(withdraw['fields']['bank']),
                    'channel': channelMap[withdraw['fields']['channel']],
                    'method': withdraw['fields']['method'],
                }
                lastWithdraw.append(withdrawDict)
            context['lastWithdraws'] = lastWithdraw[:1]
        else:
            context['lastWithdraws'] = ''


        activity = UserActivity.objects.filter(user=customUser).order_by("-created_time")
        if activity:
            context['activity'] = activity
        else:
            context['activity'] = ''


        return render(request, 'user_detail.html', context)


    def post(self, request):
        post_type = request.POST.get('type')
        user_id = request.POST.get('user_id')

        if post_type == 'edit_user_detail':
            username = request.POST.get('username')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            birthday = request.POST.get('birthday')
            address = request.POST.get('address')
            city = request.POST.get('city')
            zipcode = request.POST.get('zipcode')
            country = request.POST.get('country')
            user_id_img = request.POST.get('user_id_img')
            # upload image to S3
            self.upload_user_photo_id(username, user_id_img)

            CustomUser.objects.filter(pk=user_id).update(
                username=username, first_name=first_name, 
                last_name=last_name, email=email, 
                phone=phone, date_of_birth=birthday, 
                street_address_1=address, city=city,
                zipcode=zipcode, country=country)
            
            logger.info('Finished update user: ' + str(username) + 'info to DB')
            # print(CustomUser.objects.get(pk=user_id).id_image)

            return HttpResponseRedirect(reverse('xadmin:user_detail', args=[user_id]))
        
        elif post_type == 'update_message':
            admin_user = request.POST.get('admin_user')
            message = request.POST.get('message')

            UserActivity.objects.create(
                user = CustomUser.objects.filter(pk=user_id).first(),
                admin = CustomUser.objects.filter(username=admin_user).first(),
                message = message,
                activity_type = 3,
            )

            logger.info('Finished create activity to DB')
            return HttpResponseRedirect(reverse('xadmin:user_detail', args=[user_id]))

        elif post_type == 'activity_filter':
            activity_type = request.POST.get('activity_type')

            user = CustomUser.objects.get(pk=user_id)
            # print(str(activity_type))
            
            if activity_type == 'all':
                activitys = UserActivity.objects.filter(user=user).order_by('-created_time')
            else:
                activitys = UserActivity.objects.filter(user=user, activity_type=activity_type).order_by('-created_time')
            
            activitys = serializers.serialize('json', activitys)
            activitys = json.loads(activitys)
            response = []
            for act in activitys:
                actDict = {}
                try:
                    time = datetime.datetime.strptime(act['fields']['created_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                except:
                    time = datetime.datetime.strptime(act['fields']['created_time'], "%Y-%m-%dT%H:%M:%SZ")
                time = time.strftime("%B %d, %Y, %I:%M %p")
                actDict['time'] = time
                adminUser = CustomUser.objects.get(pk=act['fields']['admin'])
                actDict['adminUser'] = str(adminUser.username)
                actDict['message'] = act['fields']['message']
                response.append(actDict)
            # print(str(response))

            return HttpResponse(json.dumps(response), content_type='application/json')

        elif post_type == 'get_user_transactions':
            time_from = request.POST.get('from')
            time_to = request.POST.get('to')
            pageSize = int(request.POST.get('pageSize'))
            fromItem = int(request.POST.get('fromItem'))
            endItem = fromItem + pageSize
            category = request.POST.get('transaction_category')
            user = CustomUser.objects.get(pk=user_id)

            if time_from == 'Invalid date':
                time_from = datetime.datetime(2000, 1, 1)
            if time_to == 'Invalid date':
                time_to = datetime.datetime(2400, 1, 1)

            logger.info('Transactions filter: username "' + str(user.username) + '" send transactions filter request which time form: ' + str(time_from) + ',to: ' + str(time_to) + ',category: ' + str(category))
            logger.info('Pagination: Maximum size of the page is ' + str(pageSize) + 'and from item #' + str(fromItem) + ' to item # ' + str(endItem))
            
            if category == 'all':
                transactions = Transaction.objects.filter(
                    Q(user_id=user) & Q(request_time__range=[time_from, time_to])
                ).order_by('-request_time')[fromItem:endItem]
                count = Transaction.objects.filter(Q(user_id=user) & Q(request_time__range=[time_from, time_to])).count()
            else:
                transactions = Transaction.objects.filter(
                    Q(user_id=user) & Q(transaction_type=category) & Q(request_time__range=[time_from, time_to])
                ).order_by('-request_time')[fromItem:endItem]
                count = Transaction.objects.filter(Q(user_id=user) & Q(transaction_type=category) & Q(request_time__range=[time_from, time_to])).count()

            response = {}
            if endItem >= count:
                response['isLastPage'] = True
            else:
                response['isLastPage'] = False

            if fromItem == 0:
                response['isFirstPage'] = True
            else:
                response['isFirstPage'] = False

            transactionsJson = serializers.serialize('json', transactions)
            transactionsList = json.loads(transactionsJson)
            statusMap = {}
            for t in Transaction._meta.get_field('status').choices:
                statusMap[t[0]] = t[1]

            for tran in transactionsList:
                tran['fields']['status'] = statusMap[tran['fields']['status']]
            
            # transactionsJson = json.dumps(transactionsList)
            response['transactions'] = transactionsList

            return HttpResponse(json.dumps(response), content_type='application/json')

    
    def account_by_ip(self, userIp, username):
        relative_account = UserAction.objects.filter(ip_addr=userIp, event_type=0).exclude(user=username).values('user_id').distinct()
        # print(relative_account)

        accounts = []
        for item in relative_account:
            userDict = {}
            # user = CustomUser.objects.get(username=i.user)
            user = CustomUser.objects.get(pk=item['user_id'])
            userDict['id'] = user.pk
            userDict['username'] = user.username
            userDict['source'] = user.get_user_attribute_display
            userDict['channel'] = user.get_user_attribute_display
            depositSucc = Transaction.objects.filter(user_id=user, transaction_type=0, status=3).count()
            depositCount = Transaction.objects.filter(user_id=user, transaction_type=0).count()
            userDict['deposit'] = str(depositSucc) + '/' + str(depositCount)
            userDict['turnover'] = ''
            withdrawAmount = Transaction.objects.filter(user_id=user, transaction_type=1).aggregate(Sum('amount'))
            if withdrawAmount['amount__sum'] is None:
                withdrawAmount['amount__sum'] = 0
            userDict['withdrawal'] = withdrawAmount['amount__sum']
            userDict['contribution'] = ''
            userDict['riskLevel'] = 'A'
            accounts.append(userDict)
        return accounts




    def download_user_photo_id(self, username):
        aws_session = boto3.Session()
        s3_client = aws_session.client('s3')
        file_name = self.get_user_photo_file_name(username)

        success = False
        try:
            s3_response_object = s3_client.get_object(Bucket=settings.AWS_S3_ADMIN_BUCKET, Key=file_name)
            success = True
        except ClientError as e:
            # AllAccessDisabled error == bucket or object not found
            logger.error(e)
        except NoCredentialsError as e:
            logger.error(e)
        if not success:
            logger.info('Cannout find any image from this user: ' + username)
            return None

        object_content = s3_response_object['Body'].read()
        object_content = object_content.decode('utf-8')

        logger.info('Finished download username: ' + username + ' and file: ' + file_name + ' to S3!!!')
        return object_content


    def upload_user_photo_id(self, username, content):
        aws_session = boto3.Session()
        s3 = aws_session.resource('s3')
        file_name = self.get_user_photo_file_name(username)

        success = False
        try:
            obj = s3.Object(settings.AWS_S3_ADMIN_BUCKET, file_name)
            obj.put(Body=content)
            success = True
            logger.info('Finished upload username: ' + username + 'and file: ' + file_name + ' to S3!!!')
        except NoCredentialsError as e:
            logger.error(e)
        if not success:
            logger.info('Cannout upload image: ' + username)
            return None


    def get_user_photo_file_name(self, username):
        return username + '_photo_id'       


class UserListView(CommAdminView): 
    def get(self, request):

        # print(request.GET)
        search = request.GET.get('search')
        pageSize = request.GET.get('pageSize')
        offset = request.GET.get('offset')

        # print("search: " + str(search))

        if pageSize is None:
            pageSize = 20
        else: 
            pageSize = int(pageSize)

        if offset is None:
            offset = 0
        else:
            offset = int(offset)

        context = super().get_context()
        title = 'Member List'
        context['breadcrumbs'].append({'url': '/cwyadmin/', 'title': title})
        context['title'] = title
        context['time'] = timezone.now()
        if search:
            count = CustomUser.objects.filter(Q(pk__contains=search)|Q(username__contains=search)|Q(email__contains=search)|Q(phone__contains=search)|Q(first_name__contains=search)|Q(last_name__contains=search)).count()
            customUser = CustomUser.objects.filter(Q(pk__contains=search)|Q(username__contains=search)|Q(email__contains=search)|Q(phone__contains=search)|Q(first_name__contains=search)|Q(last_name__contains=search))[offset:offset+pageSize]

            if count == 0:
                count = CustomUser.objects.all().count()
                customUser = CustomUser.objects.all()[offset:offset+pageSize]
                context['searchError'] = _("No search data")

        else:
            count = CustomUser.objects.all().count()
            customUser = CustomUser.objects.all()[offset:offset+pageSize]

        if offset == 0:
            context['isFirstPage'] = True
        else:
            context['isFirstPage'] = False
        
        if count <= offset+pageSize:
            context['isLastPage'] = True
        else:
            context['isLastPage'] = False

        user_data = []
        for user in customUser:
            userDict = {}
            userDict['id'] = user.pk
            userDict['username'] = user.username
            userDict['source'] = str(user.get_user_attribute_display())
            userDict['risk_level'] = ''
            userDict['balance'] = user.main_wallet + user.other_game_wallet
            userDict['product_attribute'] = ''
            userDict['time_of_registration'] = user.time_of_registration
            userDict['ftd_time'] = user.ftd_time
            userDict['verfication_time'] = user.verfication_time
            userDict['id_location'] = user.id_location
            userDict['phone'] = user.phone
            userDict['address'] = str(user.street_address_1) + ', ' + str(user.street_address_2) + ', ' + str(user.city) + ', ' + str(user.state) + ', ' + str(user.country) 
            userDict['deposit_turnover'] = ''
            userDict['bonus_turnover'] = ''
            userDict['contribution'] = 0
            depositTimes = Transaction.objects.filter(user_id=user, transaction_type=0).count()
            withdrawTimes = Transaction.objects.filter(user_id=user, transaction_type=1).count()
            betTims = Transaction.objects.filter(user_id=user, transaction_type=2).count()
            activeDays = int(depositTimes) + int(withdrawTimes) + int(betTims)
            userDict['active_days'] = ''
            userDict['bet_platform'] = user.product_attribute


            userDict['last_login_time'] = user.last_login_time
            userDict['last_betting_time'] = user.last_betting_time
            userDict['login'] = UserAction.objects.filter(user=user, event_type=0).count()
            userDict['betting'] = Transaction.objects.filter(user_id=user, transaction_type=2).count()
            userDict['turnover'] = ''
            userDict['deposit'] = Transaction.objects.filter(user_id=user, transaction_type=0).count()
            userDict['deposit_amount'] = Transaction.objects.filter(user_id=user, transaction_type=0).aggregate(Sum('amount'))
            userDict['withdrawal'] = Transaction.objects.filter(user_id=user, transaction_type=1).count()
            userDict['withdrawal_amount'] = Transaction.objects.filter(user_id=user, transaction_type=1).aggregate(Sum('amount'))
            userDict['last_login_ip'] = UserAction.objects.filter(user=user, event_type=0).order_by('-created_time').first()
            # print("object: " + str(userDict))
            user_data.append(userDict)
        
        context['user_data'] = user_data


        return render(request, 'user_list.html', context)

    
    def post(self, request):
        post_type = request.POST.get('type')
        # user_id = request.POST.get('user_id')

        if post_type == 'user_list_time_range_filter':
            time_from = request.POST.get('from')
            time_to = request.POST.get('to')
            # print("from: " + str(time_from) + 'to: ' + str(time_to))
            Customuser = CustomUser.objects.all()
            # context['customuser'] = Customuser
            
            updated_data = []
            for user in Customuser:
                userDict = {}
                userDict['login_times'] = UserAction.objects.filter(user=user, event_type=0, created_time__range=[time_from, time_to]).count()
                userDict['betting_times'] = Transaction.objects.filter(user_id=user, transaction_type=2, request_time__range=[time_from, time_to]).count()
                userDict['deposit_times'] = Transaction.objects.filter(user_id=user, transaction_type=0, request_time__range=[time_from, time_to]).count()
                userDict['deposit_amount'] = Transaction.objects.filter(user_id=user, transaction_type=0, request_time__range=[time_from, time_to]).aggregate(Sum('amount'))
                userDict['withdrawal_times'] = Transaction.objects.filter(user_id=user, transaction_type=1, request_time__range=[time_from, time_to]).count()
                userDict['withdrawal_amount'] = Transaction.objects.filter(user_id=user, transaction_type=1, request_time__range=[time_from, time_to]).aggregate(Sum('amount'))
                # add GGR amount, turnover amount, contribution
                updated_data.append(userDict)
                # print(userDict)
            
            # print("sending data")
            return HttpResponse(json.dumps(updated_data), content_type="application/json")

        elif post_type == 'user_list_filter':
            time_from = request.POST.get('from')
            time_to = request.POST.get('to')
            pageSize = int(request.POST.get('pageSize'))
            fromItem = int(request.POST.get('fromItem'))
            endItem = fromItem + pageSize

            if time_from == 'Invalid date':
                time_from = datetime.datetime(2000, 1, 1)
            if time_to == 'Invalid date':
                time_to = datetime.datetime(2400, 1, 1)

            # print('fromItem: ' + str(fromItem))
            # print('endItem: ' + str(endItem))
            users = CustomUser.objects.all()[fromItem:endItem]
            count = CustomUser.objects.all().count()
            # print(str(count))
            # usersJson = serializers.serialize('json', users)

            # usersList = json.loads(usersJson)            
            response = {}
            if endItem >= count:
                response['isLastPage'] = True
            else:
                response['isLastPage'] = False

            if fromItem == 0:
                response['isFirstPage'] = True
            else:
                response['isFirstPage'] = False
            
            sourceMap = {}
            for t in CustomUser._meta.get_field('user_attribute').choices:
                sourceMap[t[0]] = t[1]

            usersList = []
            for user in users:
                userDict = {}
                userDict['id'] = user.pk
                userDict['username'] = user.username
                userDict['source'] = str(sourceMap[user.user_attribute])
                userDict['balance'] = user.main_wallet + user.other_game_wallet
                userDict['product_attribute'] = ''
                userDict['time_of_registration'] = str(user.time_of_registration)
                userDict['ftd_time'] = str(user.ftd_time)
                userDict['verfication_time'] = str(user.verfication_time)
                userDict['id_location'] = user.id_location
                userDict['phone'] = user.phone
                userDict['address'] = str(user.street_address_1) + ', ' + str(user.street_address_2) + ', ' + str(user.city) + ', ' + str(user.state) + ', ' + str(user.country) 
                userDict['deposit_turnover'] = ''
                userDict['bonus_turnover'] = ''
                userDict['contribution'] = 0
                depositTimes = Transaction.objects.filter(user_id=user, transaction_type=0).count()
                # print(type(depositTimes))
                withdrawTimes = Transaction.objects.filter(user_id=user, transaction_type=1).count()
                betTimes = Transaction.objects.filter(user_id=user, transaction_type=2).count()
                activeDays = int(depositTimes) + int(withdrawTimes) + int(betTimes)
                userDict['active_days'] = ''
                userDict['bet_platform'] = user.product_attribute

                # print("object: " + str(userDict))
                usersList.append(userDict)
            response['usersList'] = usersList
            # response = json.loads(response)
            return HttpResponse(json.dumps(response), content_type="application/json")    