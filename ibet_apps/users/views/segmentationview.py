from django.db.models import Count
from django.shortcuts import render
from django.utils import timezone
from xadmin.views.base import CommAdminView

from users.models import Segmentation, CustomUser


class SegmentationView(CommAdminView):
    def get(self, request):
        context = super().get_context()
        context['time'] = timezone.now()
        title = "Segmentation Settings"
        context["breadcrumbs"].append({'title': title})
        context["title"] = title

        context["empty_manager_group"] = "Please create VIP Manager group in System Admin. "
        vip_groups = CustomUser.objects.filter(vip_level__isnull=False).values('vip_level') \
            .annotate(total=Count('pk')).order_by('vip_level')
        segment_list = []
        for vip_group in vip_groups:
            segment_level = Segmentation.objects.get(level=vip_group['vip_level'])
            segment = {
                'level': vip_group['vip_level'],
                'name': segment_level.name,
                'players': vip_group['total'],
                'turnover_threshold': segment_level.turnover_threshold,
                'annual_threshold': segment_level.annual_threshold,
                'platform_turnover_daily': segment_level.platform_turnover_daily,
                'deposit_amount_daily': segment_level.deposit_amount_daily,
                'deposit_amount_monthly': segment_level.deposit_amount_monthly,
                'general_bonuses': segment_level.general_bonuses,
                'product_turnover_bonuses': segment_level.product_turnover_bonuses
            }
            segment_list.append(segment)
        context['segment_list'] = segment_list
        return render(request, 'vip/segmentation.html', context)
