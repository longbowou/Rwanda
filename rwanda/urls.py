from decorator_include import decorator_include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from rwanda.administration.views_mails import VerifyAccountMailPreviewView, PurchaseInitiatedMailPreviewView, \
    PurchaseAcceptedOrRejectedMailPreviewView, OrderInitiatedMailPreviewView, UpdateInitiatedMailPreviewView, \
    LitigationInitiatedMailPreviewView, LitigationHandledMailPreviewView
from rwanda.decorators import account_required, admin_required
from rwanda.graphql.schemas.account import schema
from rwanda.graphql.schemas.admin import admin_schema

urlpatterns = [
    path('admin/', admin.site.urls),
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=True))),
    path("graphql-admin/", csrf_exempt(GraphQLView.as_view(schema=admin_schema, graphiql=True))),
    path('account/', decorator_include(account_required, include("rwanda.account.urls"))),
    path('administration/', decorator_include(admin_required, include("rwanda.administration.urls"))),
    path('payments/', include("rwanda.payments.urls")),

    path('emails/verify-account', VerifyAccountMailPreviewView.as_view()),
    path('emails/purchases/initiated', PurchaseInitiatedMailPreviewView.as_view()),
    path('emails/purchases/accepted-or-rejected', PurchaseAcceptedOrRejectedMailPreviewView.as_view()),
    path('emails/orders/initiated', OrderInitiatedMailPreviewView.as_view()),
    path('emails/updates/initiated', UpdateInitiatedMailPreviewView.as_view()),
    path('emails/disputes/initiated', LitigationInitiatedMailPreviewView.as_view()),
    path('emails/disputes/handeled', LitigationHandledMailPreviewView.as_view()),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
