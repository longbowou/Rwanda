from django import forms
from django.core.exceptions import ImproperlyConfigured
from graphene import ID, Boolean, Float, Int, List, String, UUID, Date, DateTime, Time
from graphene_django.forms import GlobalIDMultipleChoiceField, GlobalIDFormField
from graphene_django.utils import import_single_dispatch

singledispatch = import_single_dispatch()


@singledispatch
def convert_form_field(field, for_update=True):
    raise ImproperlyConfigured(
        "Don't know how to convert the Django form field %s (%s) "
        "to Graphene type" % (field, field.__class__)
    )


@convert_form_field.register(forms.fields.BaseTemporalField)
@convert_form_field.register(forms.CharField)
@convert_form_field.register(forms.EmailField)
@convert_form_field.register(forms.SlugField)
@convert_form_field.register(forms.URLField)
@convert_form_field.register(forms.ChoiceField)
@convert_form_field.register(forms.RegexField)
@convert_form_field.register(forms.Field)
def convert_form_field_to_string(field, for_update):
    return String(description=field.help_text, required=get_required_value(field, for_update))


@convert_form_field.register(forms.UUIDField)
def convert_form_field_to_uuid(field, for_update):
    return UUID(description=field.help_text, required=get_required_value(field, for_update))


@convert_form_field.register(forms.IntegerField)
@convert_form_field.register(forms.NumberInput)
def convert_form_field_to_int(field, for_update):
    return Int(description=field.help_text, required=get_required_value(field, for_update))


@convert_form_field.register(forms.BooleanField)
def convert_form_field_to_boolean(field, for_update):
    return Boolean(description=field.help_text, required=get_required_value(field, for_update))


@convert_form_field.register(forms.NullBooleanField)
def convert_form_field_to_nullboolean(field, for_update):
    return Boolean(description=field.help_text, required=get_required_value(field, for_update))


@convert_form_field.register(forms.DecimalField)
@convert_form_field.register(forms.FloatField)
def convert_form_field_to_float(field, for_update=False):
    return Float(description=field.help_text, required=get_required_value(field, for_update))


@convert_form_field.register(forms.ModelMultipleChoiceField)
@convert_form_field.register(GlobalIDMultipleChoiceField)
def convert_form_field_to_list(field, for_update):
    return List(ID, required=get_required_value(field, for_update))


@convert_form_field.register(forms.DateField)
def convert_form_field_to_date(field, for_update):
    return Date(description=field.help_text, required=get_required_value(field, for_update))


@convert_form_field.register(forms.DateTimeField)
def convert_form_field_to_datetime(field, for_update):
    return DateTime(description=field.help_text, required=get_required_value(field, for_update))


@convert_form_field.register(forms.TimeField)
def convert_form_field_to_time(field, for_update):
    return Time(description=field.help_text, required=get_required_value(field, for_update))


@convert_form_field.register(forms.ModelChoiceField)
@convert_form_field.register(GlobalIDFormField)
def convert_form_field_to_id(field, for_update):
    return ID(required=get_required_value(field, for_update))


def get_required_value(field, for_update):
    required = field.required
    if for_update:
        required = False
    return required
