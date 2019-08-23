from django.http import JsonResponse
from django.core import serializers

from accounting.models import Transaction
from users.models import CustomUser


def get_transactions(request):
    print(request.GET)
    user = CustomUser.objects.get(username=request.GET["userid"])
    all_transactions = Transaction.objects.filter(user_id=user.id)
    print(all_transactions)
    # res = serializers.serialize('json', all_transactions)
    return JsonResponse({
        'results': list(all_transactions.values())
    })
