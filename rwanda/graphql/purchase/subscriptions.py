import channels_graphql_ws
import graphene

from rwanda.graphql.types import ServicePurchaseChatMessageType, ServicePurchaseType
from rwanda.purchase.models import ChatMessage, ServicePurchase


class ChatMessageSubscription(channels_graphql_ws.Subscription):
    name = "chat-message-{}"
    message = graphene.Field(ServicePurchaseChatMessageType)

    class Arguments:
        service_purchase = graphene.UUID(required=True)

    @staticmethod
    def subscribe(root, info, service_purchase):
        return [ChatMessageSubscription.name.format(str(service_purchase))]

    @staticmethod
    def publish(chat_message_id, info, service_purchase):
        def get_chat_message_type(account, chat_message_id):
            chat_message = ChatMessage.objects.get(pk=chat_message_id)
            last_message: ChatMessage = ChatMessage.objects.exclude(id=chat_message_id).order_by('-created_at').first()
            chat_message_type = chat_message.display(account,
                                                     last_message.created_at if last_message is not None else None)
            return chat_message_type

        if info.context.is_authenticated:
            return ChatMessageSubscription(message=get_chat_message_type(info.context.user.account, chat_message_id))

        return channels_graphql_ws.Subscription.SKIP

    @staticmethod
    def unsubscribed(root, info, service_purchase):
        pass


class ServicePurchaseSubscription(channels_graphql_ws.Subscription):
    name = "service-purchase-{}"
    service_purchase = graphene.Field(ServicePurchaseType)

    class Arguments:
        id = graphene.UUID(required=True)

    @staticmethod
    def subscribe(root, info, id):
        return [ServicePurchaseSubscription.name.format(str(id))]

    @staticmethod
    def publish(payload, info, id):
        if info.context.is_authenticated:
            return ServicePurchaseSubscription(service_purchase=ServicePurchase.objects.get(pk=id))

        return channels_graphql_ws.Subscription.SKIP

    @staticmethod
    def unsubscribed(root, info, id):
        pass


class PurchaseSubscriptions(graphene.ObjectType):
    chat_message_subscription = ChatMessageSubscription.Field()
    service_purchase_subscription = ServicePurchaseSubscription.Field()
