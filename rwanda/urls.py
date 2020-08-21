from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from rest_framework_jwt.views import obtain_jwt_token

from rwanda.graphql.admin_shema import admin_schema
from rwanda.graphql.shema import schema

urlpatterns = [
    path('admin/', admin.site.urls),
    path("graphql/", csrf_exempt(GraphQLView.as_view(schema=schema, graphiql=True))),
    path("graphql-admin/", csrf_exempt(GraphQLView.as_view(schema=admin_schema, graphiql=True))),
    path("api-token-auth/", obtain_jwt_token),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
