from django.contrib import admin
from . import models


class ChannelAdmin(admin.ModelAdmin):
    # 设置可显示字段
    list_display = ("title", "gateway_name", "pay_type", "extra_info", "status", "pc", "created")

    # 设置过滤选项
    list_filter = ('created', 'title',)

    # 搜索条件
    search_fields = ("title",)

    # 每页显示条数
    list_per_page = 10

    # 设置可编辑字段
    list_editable = ('extra_info', "status", "pc",)

    # 按照日期月份筛选
    # date_hierarchy = ''

    # 排序
    ordering = ('-created', )


class GatewayAdmin(admin.ModelAdmin):
    # 设置可显示字段
    list_display = ("title", "app_id", "app_key", "pay_url", "created")

    # 设置过滤选项
    list_filter = ('created', 'title',)

    # 每页显示条数
    list_per_page = 10

    # 设置可编辑字段
    list_editable = ()

    # 按照日期月份筛选
    # date_hierarchy = ''

    # 排序
    ordering = ('-created',)


class OrderAdmin(admin.ModelAdmin):
    # 设置可显示字段
    list_display = ("order_no", "games_order", "pay_order", "amount", "pay_amount", "pay_time", "succeeded", "channel_name", "created")

    # 设置过滤选项
    list_filter = ('games_order', 'pay_order', "created", "channel_name", "created")

    # 每页显示条数
    list_per_page = 20

    # 设置可编辑字段
    list_editable = ()

    # 按照日期月份筛选
    # date_hierarchy = ''

    # 排序
    ordering = ('-created',)


admin.site.register(models.Channel, ChannelAdmin)
admin.site.register(models.Gateway, GatewayAdmin)
admin.site.register(models.Order, OrderAdmin)
admin.site.site_header = "支付管理后台"


