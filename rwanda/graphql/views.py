# from graphene_django.views import GraphQLView as BaseGraphQLView
#
#
# class GraphQLView(BaseGraphQLView):
#     @staticmethod
#     def format_error(error):
#         formatted_error = super(GraphQLView, GraphQLView).format_error(error)
#
#         if error.original_error.code:
#             formatted_error['code'] = error.original_error.code
#
#         return formatted_error
