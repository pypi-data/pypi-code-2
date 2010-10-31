#coding: utf-8
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from merchant_api.fields import ISO8601Field
from merchant_api.managers import TestOrderManager, RealOrderManager

# По правилам проектирования БД тут должны были быть модели Order и
# OrderStateChange. Но для удобства работы оставлена только модель
# Order - насколько я понял, для каждого Order при нынешней схеме работы
# vkontakte будет 1 OrderStateChange, эти модели объединены в одну.

# Если все-же будет больше 1 изменения статуса у заказа, информация
# не потеряется, т.к. ведется аудит-лог (модель OrderChange).
# FIXME: аудит-лог сейчас не ведется ;)

class Order(models.Model):
    order_id = models.IntegerField(u'id заказа', help_text=u'Идентификатор заказа в платёжной систем')
    wish_id = models.IntegerField(u'Идентификатор желания', null=True, blank=True)
    merchant_id = models.IntegerField(u'Идентификатор продавца')
    created_at = models.DateTimeField(u'Дата/время создания', auto_now_add = True)

    is_test = models.BooleanField(u'Тестовый заказ', default=False, blank=True)

    notification_type = models.CharField(u'Тип уведомления', max_length=40)
    new_state = models.CharField(u'Новый статус заказа', max_length=20) # chargeable - готов к оплате
    currency = models.CharField(u'Числовой код валюты', max_length=3, help_text=u'Числовой код валюты заказа в формате ISO 4217')
    currency_str = models.CharField(u'Строковый код валюты', max_length=3, help_text=u'Строковый код валюты заказа ﻿в формате ISO 4217')
    amount = models.DecimalField(u'Сумма заказа', max_digits=20, decimal_places=2)
    order_date = ISO8601Field(u'Дата изменения статуса заказа')

    django_user = models.ForeignKey(User, verbose_name = u'Пользователь, совершающий оплату', blank=True, null=True,
                                    related_name = 'vk_%(class)ss')

    user_id = models.IntegerField(u'id пользователя ВКонтакте, совершающего оплату')
    user_name = models.CharField(u'Имя пользователя, совершающего оплату', max_length=100, blank=True, null=True)
    shipping_email = models.EmailField(u'Контактный e-mail', blank=True, null=True)

    shipping_method = models.CharField(u'идентификатор варианта доставки', null=True, blank=True, max_length=100)
    shipping_country = models.CharField(u'страна', null=True, blank=True, max_length=2, help_text=u'в формате ISO 3166-1 alpha-2')
    shipping_country_str = models.CharField(u'название страны', null=True, blank=True, max_length=30)
    shipping_code = models.CharField(u'почтовый индекс', null=True, blank=True, max_length=20)
    shipping_city = models.CharField(u'название города', null=True, blank=True, max_length=50)
    shipping_street = models.CharField(u'название улицы', null=True, blank=True, max_length=50)
    shipping_house = models.CharField(u'номер дома', null=True, blank=True, max_length=20)
    shipping_flat = models.CharField(u'номер квартиры', null=True, blank=True, max_length=10)
    shipping_phone = models.CharField(u'номер телефона', null=True, blank=True, max_length=100)
    recipient_name = models.CharField(u'имя получателя', null=True, blank=True, max_length=100)
    order_comment = models.TextField(u'комментарий к заказу', null=True, blank=True)

    recipient_phone = models.CharField(u'телефон получателя', max_length=100, null=True, blank=True)

    objects = models.Manager()
    test = TestOrderManager()
    real = RealOrderManager()


    def save(self, *args, **kwargs):
        self.is_test = '-test' in self.notification_type

        if not self.django_user:
            try:
                self.django_user = User.objects.get(username = str(self.user_id))
            except User.DoesNotExist:
                pass
        return super(Order, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"[vk] Заказ %s" % self.order_id

    class Meta:
        unique_together = ['order_id', 'is_test']
        verbose_name = u'[vk] Заказ'
        verbose_name_plural = u'[vk] Заказы'


# ===== свои поля в заказе ========

class CustomField(models.Model):
    number = models.PositiveIntegerField(u'Номер в заказе')
    value = models.TextField(u'Значение')
    order = models.ForeignKey(Order, related_name='custom_fields')

    def __unicode__(self):
        return u"[vk] Поле #%s к %s" % (self.number, self.order_id,)

    class Meta:
        verbose_name = u'[vk] Дополнительное поле к заказу'
        verbose_name_plural = u'[vk] Дополнительные поля к заказам'
        unique_together = ("number", "order")

# ==== позиции заказа =======

class Item(models.Model):
    order = models.ForeignKey(Order, related_name='items')
    number = models.PositiveIntegerField(u'Номер в заказе')
    item_id = models.CharField(u'id позиции', max_length=100)
    price = models.DecimalField(u'Стоимость', max_digits=20, decimal_places=2)
    quantity = models.PositiveIntegerField(u'Количество')
    currency = models.CharField(u'Числовой код валюты', max_length=3, help_text=u'в формате ISO 4217')
    currency_str = models.CharField(u'Строковый код валюты﻿', max_length=3, help_text=u'в формате ISO 4217')

    def __unicode__(self):
        return u"[vk] Позиция #%s в заказе %s" % (self.number, self.order_id,)

    class Meta:
        verbose_name = u'[vk] Позиции заказа'
        verbose_name_plural = u'[vk] Позиции заказов'
        unique_together = ("number", "order")


# ====== аудит-лог =========

class OrderChange(models.Model):
    order = models.ForeignKey(Order)
    changed_at = models.DateTimeField(u'Дата/время изменения', default=datetime.now)
    changes = models.TextField(u'Что изменилось')

    class Meta:
        verbose_name = u'[vk] Изменение в заказе'
        verbose_name_plural = u'[vk] Журнал изменений заказов'
        ordering=['-id']
