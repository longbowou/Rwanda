from decorator_include import decorator_include
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

from rwanda.decorators import account_required
from rwanda.graphql.schemas.account import schema
from rwanda.graphql.schemas.admin import admin_schema

urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += i18n_patterns(
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=True))),
    path("graphql-admin/", csrf_exempt(GraphQLView.as_view(schema=admin_schema, graphiql=True))),
    path('account/', decorator_include(account_required, include("rwanda.account.urls"))),
    prefix_default_language=False
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
