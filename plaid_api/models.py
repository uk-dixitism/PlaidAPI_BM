from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
	user = models.ForeignKey(User, on_delete = models.CASCADE)
	item_id =models.CharField(max_length = 200)
	access_token = models.CharField(max_length=200)

	def __str__(self):
		return self.item_id

class Account(models.Model):
	item = models.ForeignKey(Item, on_delete = models.CASCADE)
	account_id = models.CharField(max_length = 200)
	current_balance = models.FloatField(default = None, null = True)
	available_balance = models.FloatField()
	name = models.CharField(max_length = 200)
	account_type = models.CharField(max_length = 200)
	account_subtype = models.CharField(max_length = 200)

	def __str__(self):
		return self.account_id


class Transaction(models.Model):
	account = models.ForeignKey(Account, on_delete = models.CASCADE)
	transaction_id = models.CharField(max_length = 200)
	amount = models.FloatField()
	date = models.DateField()
	name = models.CharField(max_length = 200)
	payment_mode = models.CharField(max_length = 200)

	def __str__(self):
		return self.transaction_id