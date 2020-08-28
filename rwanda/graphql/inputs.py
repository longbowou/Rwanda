import graphene


class UserInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    first_name = graphene.String()
    last_name = graphene.String()
    email = graphene.String(required=True)
    password = graphene.String(required=True)
    password_confirmation = graphene.String(required=True)


class UserUpdateInput(graphene.InputObjectType):
    username = graphene.String()
    first_name = graphene.String()
    last_name = graphene.String()
    email = graphene.String()


class LoginInput(graphene.InputObjectType):
    login = graphene.String(required=True)
    password = graphene.String(required=True)


class ChangePasswordInput(graphene.InputObjectType):
    current_password = graphene.String(required=True)
    password = graphene.String(required=True)
    password_confirmation = graphene.String(required=True)
