from django.db import models


__all__ = []


class Order(models.Model):
    order_no = models.CharField(max_length=256, null=False, db_index=True, verbose_name="订单号")
    games_order = models.CharField(max_length=256, null=True, verbose_name="游戏方订单号")
    pay_order = models.CharField(max_length=256, null=True, verbose_name="支付方订单号")

    # 订单创建金额  实际支付金额 支付时间 支付状态
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="订单金额")
    pay_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="实际支付金额", null=True)
    pay_time = models.IntegerField(verbose_name="支付时间", null=True)
    succeeded = models.BooleanField(default=False, verbose_name="支付状态")

    # 支付方式 通道id 通道名字
    pay_type = models.CharField(max_length=128, verbose_name="支付方式")
    channel_id = models.IntegerField(verbose_name="通道Id")
    channel_name = models.CharField(max_length=256, verbose_name="通道名字")

    # 用户相关
    username = models.CharField(max_length=256, verbose_name="用户名字")
    client_ip = models.CharField(max_length=256, verbose_name="用户IP地址")
    # 回调平台地址
    notify_url = models.CharField(max_length=256, verbose_name="回调地址")

    # 记录创建更新时间 以及拓展字段
    created = models.IntegerField(null=False, verbose_name="创建时间")
    updated = models.IntegerField(null=True, verbose_name="更新时间")
    data = models.CharField(null=True, max_length=2048, verbose_name="拓展字段")

    def __str__(self):
        return self.order_no

    class Meta:
        verbose_name = "订单管理"
        verbose_name_plural = "订单管理"


class Gateway(models.Model):
    title = models.CharField(max_length=256, verbose_name="支付方名字", null=False)
    app_id = models.CharField(max_length=256, verbose_name="APP_ID", null=False)
    app_key = models.CharField(max_length=256, verbose_name="APP_KEY", null=False)
    pay_url = models.CharField(max_length=256, verbose_name="发起订单地址", null=False)

    # 记录创建更新时间 以及拓展字段
    created = models.IntegerField(null=False, verbose_name="创建时间")
    updated = models.IntegerField(null=True, verbose_name="更新时间")
    data = models.CharField(null=True, max_length=2048, verbose_name="拓展字段")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "支付管理"
        verbose_name_plural = "支付管理"


class Channel(models.Model):
    title = models.CharField(max_length=256, verbose_name="通道名字", null=False)
    gateway_id = models.IntegerField(verbose_name="三方支付ID")
    gateway_name = models.CharField(max_length=256, verbose_name="三方支付名称")
    extra_info = models.CharField(verbose_name="通道拓展参数，Json数据", max_length=2048)
    pay_type = models.CharField(max_length=256, verbose_name="支付类型")
    # 1开启 0 关闭
    status = models.IntegerField(verbose_name="通道状态(1 开启 0 关闭)")
    pc = models.IntegerField(verbose_name="pc 1 h5 0 银联 2")

    # 记录创建更新时间 以及拓展字段
    created = models.IntegerField(null=False, verbose_name="创建时间")
    updated = models.IntegerField(null=True, verbose_name="更新时间")
    data = models.CharField(null=True, max_length=2048, verbose_name="拓展字段")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "通道管理"
        verbose_name_plural = "通道管理"


# 提现订单表
class Withdrawal(models.Model):
    order_no = models.CharField(max_length=256, null=False, db_index=True, verbose_name="订单号")
    games_order = models.CharField(max_length=256, null=True, verbose_name="游戏方订单号")
    pay_order = models.CharField(max_length=256, null=True, verbose_name="支付方订单号")

    # 订单创建金额  实际支付金额 支付时间 支付状态
    amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="订单金额")
    pay_amount = models.DecimalField(max_digits=18, decimal_places=2, verbose_name="实际支付金额", null=True)
    pay_time = models.IntegerField(verbose_name="支付时间", null=True)
    succeeded = models.BooleanField(default=False, verbose_name="支付状态")

    # 支付方式 通道id 通道名字
    pay_type = models.CharField(max_length=128, verbose_name="支付方式")
    channel_id = models.IntegerField(verbose_name="通道Id")
    channel_name = models.CharField(max_length=256, verbose_name="通道名字")

    # 用户相关
    username = models.CharField(max_length=256, verbose_name="用户名字")
    client_ip = models.CharField(max_length=256, verbose_name="用户IP地址")
    # 回调平台地址
    notify_url = models.CharField(max_length=256, verbose_name="回调地址")

    # 记录创建更新时间 以及拓展字段
    created = models.IntegerField(null=False, verbose_name="创建时间")
    updated = models.IntegerField(null=True, verbose_name="更新时间")
    data = models.CharField(null=True, max_length=2048, verbose_name="拓展字段")

    def __str__(self):
        return self.order_no

    class Meta:
        verbose_name = "提现管理"
        verbose_name_plural = "提现管理"

