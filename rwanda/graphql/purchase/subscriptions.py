import channels_graphql_ws
import graphene

from rwanda.graphql.types import ServicePurchaseChatMessageType
from rwanda.purchase.models import ChatMessage


class ChatSubscription(channels_graphql_ws.Subscription):
    name = "chat-{}"
    message = graphene.Field(ServicePurchaseChatMessageType)

    class Arguments:
        auth_token = graphene.String(required=True)
        service_purchase = graphene.UUID(required=True)

    @staticmethod
    def subscribe(root, info, auth_token, service_purchase):
        return [ChatSubscription.name.format(service_purchase.urn[9:])]

    @staticmethod
    def publish(chat_message_id, info, auth_token, service_purchase):
        if info.context.is_authenticated:
            chat_message = ChatMessage.objects.get(pk=chat_message_id)
            last_message: ChatMessage = ChatMessage.objects.exclude(id=chat_message_id).order_by('-created_at').first()
            chat_message_type = chat_message.to_chat_message_type(info,
                                                                  last_message.created_at if last_message is not None else None)
            return ChatSubscription(message=chat_message_type)

        return channels_graphql_ws.Subscription.SKIP

    @staticmethod
    def unsubscribed(root, info, auth_token, service_purchase):
        pass


class PurchaseSubscriptions(graphene.ObjectType):
    chat_subscription = ChatSubscription.Field()
