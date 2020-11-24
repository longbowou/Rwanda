import json
import logging

from django.db import transaction
from django.utils.crypto import get_random_string
from django.views import View

from rwanda.account.models import Deposit
from rwanda.accounting.models import Operation
from rwanda.graphql.purchase.operations import credit_account, debit_account
from rwanda.payments.models import Payment
from rwanda.payments.utils import check_status


class PaymentView(View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        prefix = get_random_string(5)

        logger = logging.getLogger('rwanda.payments')
        logger.info("#{} Request: ".format(prefix) + json.dumps(request.POST))

        if request.POST.__contains__('cpm_trans_id'):
            payment = Payment.objects.get(pk=request.POST['cpm_trans_id'])
            if payment.initiated:
                result = check_status(payment)

                logger.info("#{} Check Status: ".format(prefix) + json.dumps(result))

                if result.__contains__('transaction') and result['transaction'].__contains__('cpm_result'):
                    if int(result['transaction']['cpm_amount']) != payment.amount or \
                            result['transaction']['signature'] != payment.signature:
                        logger.warning("#{} Mismatches with payment Id: ".format(prefix) + str(payment.id))
                        return

                    if result['transaction']['cpm_result'] == '00':
                        payment.set_as_confirmed()

                        deposit = Deposit(account=payment.account, amount=payment.amount, payment=payment)
                        deposit.save()

                        credit_account(payment.account, payment.amount, Operation.DESC_CREDIT_FOR_DEPOSIT)
                    else:
                        payment.set_as_canceled()

                    payment.cpm_payid = result['transaction']['cpm_result']
                    payment.payment_method = result['transaction']['payment_method']
                    payment.cpm_phone_prefixe = result['transaction']['cpm_phone_prefixe']
                    payment.cel_phone_num = result['transaction']['cel_phone_num']
                    payment.cpm_result = result['transaction']['cpm_result']
                    payment.cpm_trans_status = result['transaction']['cpm_trans_status']
                    payment.save()

        if request.POST.__contains__('client_transaction_id'):
            payment = Payment.objects.get(pk=request.POST['client_transaction_id'])
            if payment.initiated:
                if int(request.POST['amount']) != payment.amount:
                    logger.warning("#{} Mismatches with payment Id: ".format(prefix) + str(payment.id))
                    return

                if request.POST['treatment_status'] == 'VAL':
                    payment.set_as_confirmed()

                    debit_account(payment.account, payment.amount, Operation.DESC_DEBIT_FOR_REFUND)
                else:
                    payment.set_as_canceled()

                payment.cpm_payid = request.POST['transaction_id']
                payment.payment_method = request.POST['operator']
                payment.cpm_result = request.POST['treatment_status']
