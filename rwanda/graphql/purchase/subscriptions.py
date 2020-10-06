import channels_graphql_ws
import graphene
from graphql_jwt.shortcuts import get_user_by_token

from rwanda.graphql.types import ServicePurchaseChatMessageType
from rwanda.purchase.models import ChatMessage


class ChatMessageSubscription(channels_graphql_ws.Subscription):
    name = "chat-message-{}"
    message = graphene.Field(ServicePurchaseChatMessageType)

    class Arguments:
        auth_token = graphene.String(required=True)
        service_purchase = graphene.UUID(required=True)

    @staticmethod
    def subscribe(root, info, auth_token, service_purchase):
        return [ChatMessageSubscription.name.format(service_purchase.urn[9:])]

    @staticmethod
    def publish(chat_message_id, info, auth_token, service_purchase):
        try:
            user = get_user_by_token(auth_token)
            return ChatMessageSubscription(message=get_chat_message_type(user.account, chat_message_id))
        except Exception:
            pass

        return channels_graphql_ws.Subscription.SKIP

    @staticmethod
    def unsubscribed(root, info, auth_token, service_purchase):
        pass


def get_chat_message_type(account, chat_message_id):
    chat_message = ChatMessage.objects.get(pk=chat_message_id)
    last_message: ChatMessage = ChatMessage.objects.exclude(id=chat_message_id).order_by('-created_at').first()
    chat_message_type = chat_message.to_chat_message_type(account,
                                                          last_message.created_at if last_message is not None else None)
    return chat_message_type


class PurchaseSubscriptions(graphene.ObjectType):
    chat_message_subscription = ChatMessageSubscription.Field()
