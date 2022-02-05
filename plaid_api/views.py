import datetime
import plaid
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .serializers import AccessToken
from .tasks import delete_transactions, fetch_transactions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from plaid_api.serializers import AccessToken
from rest_framework.permissions import IsAuthenticated
from .models import Item
from .keys import *
from django.utils.decorators import method_decorator


client = plaid.Client(client_id=PLAID_CLIENT_ID,public_key=PLAID_PUBLIC_KEY ,secret=PLAID_SECRET, environment=PLAID_ENV, api_version='2020-09-14')

@method_decorator(csrf_exempt,name='dispatch')
class ExchangeToken(APIView):
    """
    Exchanges Public token for access token
    """
    permission_classes = [IsAuthenticated]
    @csrf_exempt
    def post(self, request):
        request_data = request.POST
        public_token = request_data.get('public_token')
        try:
            exchange_response = client.Item.public_token.exchange(public_token)
            serializer = AccessToken(data=exchange_response)
            if serializer.is_valid():
                access_token = serializer.validated_data['access_token']
                item = Item.objects.create(access_token=access_token,
                                           item_id=serializer.validated_data['item_id'],
                                           user=self.request.user
                                           )
                item.save()

                # Async Task
                fetch_transactions.delay(access_token)

        except plaid.errors.PlaidError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(data=exchange_response, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt,name='dispatch')
class GetTransaction(APIView):
    """
    Retrieve transactions for credit and depository accounts.
    """
    permission_classes = [IsAuthenticated]
    @csrf_exempt
    def post(self, request):
        item = Item.objects.filter(user=request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']

            # transactions of two years i.e. 730 days
            start_date = '{:%Y-%m-%d}'.format(
                datetime.datetime.now() + datetime.timedelta(-730))
            end_date = '{:%Y-%m-%d}'.format(datetime.datetime.now())

            try:
                transactions_response = client.Transactions.get(
                    access_token, start_date, end_date)
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'error': None, 'transactions': transactions_response}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class Identity(APIView):
    """
    Retrieve Identity information on file with the bank.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']
            try:
                identity_response = client.Identity.get(access_token)
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'error': None, 'identity': identity_response}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class Balance(APIView):
    """
    Gets all the information about balance of the Item.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']
            try:
                balance_response = client.Accounts.balance.get(access_token)
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'error': None, 'balance': balance_response}, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class ItemInfo(APIView):
    """
    Retrieve information about an Item, like the institution, billed products,
    available products, and webhook information.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']
            try:
                item_response = client.Item.get(access_token)
                institution_response = client.Institutions.get_by_id(
                    item_response['item']['institution_id'])
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(
                data={'error': None, 'item': item_response['item'], 'institution': institution_response['institution']},
                status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class AccountInfo(APIView):
    """
    Retrieve high-level information about all accounts associated with an Item.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        item = Item.objects.filter(user=self.request.user)
        if item.count() > 0:
            access_token = item.values('access_token')[0]['access_token']
            try:
                accounts_response = client.Accounts.get(access_token)
            except plaid.errors.PlaidError as e:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'accounts': accounts_response, 'error': None, }, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


@csrf_exempt
def webhook(request):
    request_data = request.POST
    webhook_type = request_data.get('webhook_type')
    webhook_code = request_data.get('webhook_code')

    if webhook_type == 'TRANSACTIONS':
        item_id = request_data.get('item_id')
        if webhook_code == 'TRANSACTIONS_REMOVED':
            removed_transactions = request_data.get('removed_transactions')
            delete_transactions.delay(item_id, removed_transactions)

        else:
            new_transactions = request_data.get('new_transactions')
            fetch_transactions.delay(None, item_id, new_transactions)

    return HttpResponse('Webhook received', status=status.HTTP_202_ACCEPTED)


def index(request):
    return HttpResponse("<h1>This is an app built in Django with Plaid API</h1>")