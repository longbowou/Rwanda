import io
import re
from collections import OrderedDict
from copy import deepcopy

import graphene
import inflect
from django.forms import ModelForm, formset_factory
from graphene import Field, InputField, InputObjectType
from graphene.types.base import BaseType
from graphene.types.mutation import MutationOptions, Mutation as GrapheneMutation
from graphene.types.utils import yank_fields_from_attrs
from graphene.utils.orderedtype import OrderedType
from graphene.utils.thenables import maybe_thenable
from graphene_django.forms.mutation import DjangoModelDjangoFormMutationOptions
from graphene_django.registry import get_global_registry
from graphene_django.types import ErrorType
from rest_framework import serializers
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer

from rwanda.graphql.converters import convert_form_field


class Mutation(GrapheneMutation):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            output=None,
            input_fields=None,
            arguments=None,
            name=None,
            multiple=False,
            **options
    ):
        input_class = getattr(cls, "Input", None)
        base_name = re.sub("Payload$", "", name or cls.__name__)

        assert not output, "Can't specify any output"
        assert not arguments, "Can't specify any arguments"

        bases = (InputObjectType,)
        if input_class:
            bases += (input_class,)

        if not input_fields:
            input_fields = {}

        cls.Input = type(
            "{}Input".format(base_name),
            bases,
            OrderedDict(
                # input_fields, client_mutation_id=String(name="clientMutationId")
                input_fields
            ),
        )

        arguments = OrderedDict(
            input=graphene.List(graphene.NonNull(cls.Input), required=True) if multiple else cls.Input(required=True)
            # 'client_mutation_id': String(name='clientMutationId')
        )
        mutate_and_get_payload = getattr(cls, "mutate_and_get_payload", None)
        if cls.mutate and cls.mutate.__func__ == Mutation.mutate.__func__:
            assert mutate_and_get_payload, (
                "{name}.mutate_and_get_payload method is required"
                " in a Mutation."
            ).format(name=name or cls.__name__)

        if not name:
            name = "{}Payload".format(base_name)

        super(Mutation, cls).__init_subclass_with_meta__(
            output=None, arguments=arguments, name=name, **options
        )
        # cls._meta.fields["client_mutation_id"] = Field(String, name="clientMutationId")

    @classmethod
    def mutate(cls, root, info, input):
        def on_resolve(payload):
            # payload.client_mutation_id = input["client_mutation_id"] if input.__contains__(
            #     "client_mutation_id") else None
            return payload

        result = cls.mutate_and_get_payload(root, info, input)
        return maybe_thenable(result, on_resolve)

    @classmethod
    def mutate_and_get_payload(cls, root, info, input):
        pass


class DjangoModelMutation(Mutation):
    class Meta:
        abstract = True

    errors = graphene.List(ErrorType)

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            model_type=None,
            return_field_name=None,
            fields="__all__",
            only_fields=(),
            exclude_fields=(),
            extra_input_fields=None,
            for_update=False,
            multiple=False,
            custom_input_fields=None,
            custom_form_instance=False,
            **options
    ):
        if extra_input_fields is None:
            extra_input_fields = {}

        if custom_input_fields is None:
            custom_input_fields = {}

        if not isinstance(extra_input_fields, dict):
            raise Exception("extra fields must be a dictionary")

        if not model_type and model_type.Meta.model:
            raise Exception("model type and model")

        model = model_type._meta.model

        form = cls.form_class(model, fields, {})
        input_fields = fields_for_form(form, only_fields, exclude_fields, custom_input_fields, for_update)

        if for_update:
            if not custom_form_instance:
                input_fields["id"] = graphene.UUID(required=True)
        else:
            if "id" in input_fields:
                input_fields.pop("id")

        form_fields = input_fields.copy()
        if "id" in form_fields:
            form_fields.pop("id")
        form_fields = form_fields.keys()

        for k, v in extra_input_fields.items():
            if not isinstance(v, (BaseType, OrderedType)):
                raise Exception(f"{k} extra field must be a graphql type.")

            input_fields[k] = v

        registry = get_global_registry()
        if not registry.get_type_for_model(model):
            registry.register(model_type)

        if not return_field_name:
            model_name = model.__name__
            return_field_name = model_name[:1].lower() + model_name[1:]

        if multiple:
            cls.errors = graphene.List(graphene.List(ErrorType))
            return_field_name = inflect.engine().plural(return_field_name)

        output_fields = OrderedDict()
        output_fields[return_field_name] = graphene.List(model_type) if multiple else graphene.Field(model_type)

        if multiple:
            output_fields["total_error_count"] = graphene.Int()

        _meta = DjangoModelDjangoFormMutationOptions(cls)
        _meta.model = model
        _meta.model_type = model_type
        _meta.return_field_name = return_field_name
        _meta.form_fields = form_fields
        _meta.multiple = multiple
        _meta.for_update = for_update
        _meta.custom_form_instance = custom_form_instance
        _meta.fields = yank_fields_from_attrs(output_fields, _as=Field)

        input_fields = yank_fields_from_attrs(input_fields, _as=InputField)
        super(DjangoModelMutation, cls).__init_subclass_with_meta__(
            _meta=_meta,
            input_fields=input_fields,
            name=cls.__name__,
            multiple=multiple,
            **options
        )

    @classmethod
    def mutate_and_get_payload(cls, root, info, input):
        form, old_obj = cls.get_form(info, input)
        if isinstance(form, cls):
            return form

        pre_form_validations = cls.pre_validations(info, input, form)
        if isinstance(pre_form_validations, cls):
            return pre_form_validations

        if form.is_valid():
            post_form_validations = cls.post_validations(info, input, form)
            if isinstance(post_form_validations, cls):
                return post_form_validations

            return cls.perform_mutate(info, form, old_obj, input)
        else:
            errors = from_multiple_errors(form.errors) if cls._meta.multiple else ErrorType.from_errors(form.errors)
            return cls.respond(input, errors=errors, old_obj=old_obj, form=form)

    @classmethod
    def perform_mutate(cls, info, form, old_obj, input):
        pre_mutate = cls.pre_save(info, old_obj, form, input)
        if isinstance(pre_mutate, cls):
            return pre_mutate

        if cls._meta.multiple:
            obj = [form_form.save() for form_form in form.forms]
        else:
            obj = form.save()

        post_mutate = cls.post_save(info, old_obj, form, obj, input)
        if isinstance(post_mutate, cls):
            return post_mutate

        kwargs = {cls._meta.return_field_name: obj}
        return cls.respond(input, errors=[], kwargs=kwargs, old_obj=old_obj, form=form, obj=obj)

    @classmethod
    def get_form(cls, info, input):
        form_kwargs, old_obj = cls.get_form_multiple_kwargs(info, input) \
            if cls._meta.multiple else cls.get_form_kwargs(info, input)
        if isinstance(form_kwargs, cls):
            return form_kwargs, None

        return cls.form_multiple_class(cls._meta.model, cls._meta.form_fields, form_kwargs) \
                   if cls._meta.multiple else cls.form_class(cls._meta.model, cls._meta.form_fields,
                                                             form_kwargs), old_obj

    @classmethod
    def form_class(cls, form_model, form_fields, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        class Form(ModelForm):
            class Meta:
                model = form_model
                fields = form_fields

        return Form(**form_kwargs)

    @classmethod
    def form_multiple_class(cls, form_model, form_fields, form_kwargs=None):
        if form_kwargs is None:
            form_kwargs = {}

        class Form(ModelForm):
            class Meta:
                model = form_model
                fields = form_fields

        return formset_factory(Form)(**form_kwargs)

    @classmethod
    def get_form_kwargs(cls, info, input):
        kwargs = {"data": input, "files": info.context.FILES, "instance": cls._meta.model()}

        old_obj = None
        if cls._meta.for_update:
            if cls._meta.custom_form_instance:
                instance = cls.custom_form_instance(info, input)
            else:
                pk = input.id
                try:
                    instance = cls._meta.model._default_manager.get(pk=input)
                except Exception:
                    return cls.respond(input, errors=not_found_error(cls._meta.model.__name__, pk)), None

            old_obj = deepcopy(instance)

            class Serializer(serializers.ModelSerializer):
                class Meta:
                    model = cls._meta.model
                    fields = "__all__"

            data = JSONParser().parse(io.BytesIO(JSONRenderer().render(Serializer(instance).data)))
            data.update(input)
            kwargs["instance"] = instance
            kwargs["data"] = data

        return kwargs, old_obj

    @classmethod
    def get_form_multiple_kwargs(cls, info, input):
        initial = []
        errors = []
        if cls._meta.for_update:
            for input_data in input:
                if isinstance(input_data, dict) and input_data.__contains__("id"):
                    pk = input_data["id"]

                    try:
                        initial += [cls._meta.model._default_manager.get(pk=pk).__dict__]
                    except Exception:
                        errors.append(not_found_error(cls._meta.model.__name__, pk))

        if errors.__len__() > 0:
            return cls.respond(input, errors=errors), None

        old_obj = deepcopy(initial)
        data = {}
        index = 0
        for input_data in input:
            if isinstance(input_data, dict):
                for k, v in input_data.items():
                    data[f"form-{index}-{k}"] = v

                index += 1

        data["form-TOTAL_FORMS"] = index
        data["form-INITIAL_FORMS"] = "0"
        data["form-MAX_NUM_FORMS"] = ""

        kwargs = {"data": data, "initial": initial}

        return kwargs, old_obj

    @classmethod
    def pre_validations(cls, info, input, form):
        pass

    @classmethod
    def post_validations(cls, info, input, form):
        pass

    @classmethod
    def pre_save(cls, info, old_obj, form, input):
        pass

    @classmethod
    def post_save(cls, info, old_obj, form, obj, input):
        pass

    @classmethod
    def respond(cls, input, errors=None, kwargs=None, old_obj=None, form=None, obj=None):
        if kwargs is None:
            kwargs = {}

        if errors is None:
            errors = []

        if cls._meta.multiple and form is not None:
            kwargs['total_error_count'] = form.total_error_count()

        return cls(errors=errors, **kwargs)

    @classmethod
    def custom_form_instance(cls, info, input):
        pass


def from_multiple_errors(errors):
    errors_types = []
    for form_errors in errors:
        errors_types.append(ErrorType.from_errors(form_errors))

    return errors_types


class DjangoModelDjangoDeleteMutationOptions(MutationOptions):
    model = None
    return_field_name = None


class DjangoModelDeleteMutation(GrapheneMutation):
    class Meta:
        abstract = True

    errors = graphene.List(ErrorType)

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            model_type=None,
            return_field_name=None,
            **options
    ):
        if not model_type:
            raise Exception("model type is required for DjangoModelDeleteMutation")

        model = model_type._meta.model

        registry = get_global_registry()
        if not registry.get_type_for_model(model):
            registry.register(model_type)

        arguments = {}
        multiple = options["multiple"] if options.__contains__("multiple") else False
        if multiple:
            arguments["id"] = graphene.List(graphene.NonNull(graphene.UUID), required=True)
        else:
            arguments["id"] = graphene.UUID(required=True)

        _meta = DjangoModelDjangoDeleteMutationOptions(cls)
        _meta.model = model
        _meta.model_type = model_type
        _meta.multiple = multiple

        super(DjangoModelDeleteMutation, cls).__init_subclass_with_meta__(
            _meta=_meta, arguments=arguments, **options
        )

    @classmethod
    def mutate(cls, root, info, id):
        errors = []
        if cls._meta.multiple:
            old_obj = []
            for _id in id:
                multiple_errors, multiple_old_obj = cls.perform_delete(info, _id)
                old_obj.append(multiple_old_obj)
                if multiple_errors.__len__() > 0:
                    errors += multiple_errors
        else:
            errors, old_obj = cls.perform_delete(info, id)
            if isinstance(errors, cls):
                return errors, None

        return cls.respond(old_obj, errors=errors)

    @classmethod
    def perform_delete(cls, info, id):
        instance = None
        old_obj = None
        errors = []
        try:
            instance = cls._meta.model._default_manager.get(pk=id)
            old_obj = deepcopy(instance)
        except Exception:
            errors += not_found_error(cls._meta.model.__name__, id)

        pre_delete = cls.pre_delete(info, instance)
        if isinstance(pre_delete, cls):
            return pre_delete

        instance.delete()

        post_delete = cls.post_delete(info, old_obj)
        if isinstance(post_delete, cls):
            return post_delete, None

        return errors, old_obj

    @classmethod
    def pre_delete(cls, info, obj):
        pass

    @classmethod
    def post_delete(cls, info, old_obj):
        pass

    @classmethod
    def respond(cls, old_obj, errors=None):
        return cls(errors=errors)


def not_found_error(model_name, id):
    return ErrorType.from_errors({"id": ["{} instance not found for id {}".format(model_name, id)]})


def fields_for_form(form, only_fields, exclude_fields, custom_input_fields, for_update):
    fields = OrderedDict()
    for name, field in form.fields.items():
        is_not_in_only = only_fields and name not in only_fields
        is_excluded = (name in exclude_fields)

        if is_not_in_only or is_excluded:
            continue

        if name in custom_input_fields:
            if not isinstance(custom_input_fields[name], (BaseType, OrderedType)):
                raise Exception(f"{name} custom input field must be a graphql type.")

            fields[name] = custom_input_fields[name]
            continue

        fields[name] = convert_form_field(field, for_update=for_update)

    return fields
