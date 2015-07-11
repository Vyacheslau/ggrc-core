# Copyright (C) 2015 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: miha@reciprocitylabs.com
# Maintained By: miha@reciprocitylabs.com

from dateutil.parser import parse
from sqlalchemy import and_
from sqlalchemy import or_
import re

from ggrc import db
from ggrc.converters import IMPORTABLE
from ggrc.converters import errors
from ggrc.converters.utils import pretty_class_name
from ggrc.login import get_current_user
from ggrc.models import CustomAttributeValue
from ggrc.models import CustomAttributeDefinition
from ggrc.models import Option
from ggrc.models import Person
from ggrc.models import Program
from ggrc.models import Relationship
from ggrc.models.relationship import RelationshipHelper


class ColumnHandler(object):

  def __init__(self, row_converter, key, **options):
    self.row_converter = row_converter
    self.key = key
    self.value = None
    self.raw_value = options.get("raw_value", "").strip()
    self.validator = options.get("validator")
    self.mandatory = options.get("mandatory", False)
    self.default = options.get("default")
    self.description = options.get("description", "")
    self.display_name = options.get("display_name", "")
    self.dry_run = row_converter.block_converter.converter.dry_run
    self.set_value()

  def set_value(self):
    self.value = self.parse_item()

  def get_value(self):
    return getattr(self.row_converter.obj, self.key, self.value)

  def add_error(self, template, **kwargs):
    self.row_converter.add_error(template, **kwargs)

  def add_warning(self, template, **kwargs):
    self.row_converter.add_warning(template, **kwargs)

  def parse_item(self):
    return self.raw_value

  def validate(self):
    if callable(self.validator):
      try:
        self.validator(self.row_converter.obj, self.key, self.value)
      except ValueError:
        self.add_error("invalid status '{}'".format(self.value))
    return True

  def set_obj_attr(self):
    if not self.value:
      return
    setattr(self.row_converter.obj, self.key, self.value)

  def get_default(self):
    if callable(self.default):
      return self.default()
    return self.default

  def insert_object(self):
    """ For inserting fields such as custom attributes and mappings """
    pass


class StatusColumnHandler(ColumnHandler):

  def __init__(self, row_converter, key, **options):
    self.key = key
    valid_states = row_converter.object_class.VALID_STATES
    self.state_mappings = {s.lower(): s for s in valid_states}
    super(StatusColumnHandler, self).__init__(row_converter, key, **options)

  def parse_item(self):
    # TODO: check if mandatory and replace with default if it's wrong
    value = self.raw_value.lower()
    status = self.state_mappings.get(value)
    if status is None:
      self.add_warning(errors.WRONG_REQUIRED_VALUE,
                       value=value[:20],
                       column_name=self.display_name)
      status = self.get_default()
    return status


class UserColumnHandler(ColumnHandler):

  """ Handler for primary and secondary contacts """

  def get_person(self, email):
    new_objects = self.row_converter.block_converter.converter.new_objects
    if email in new_objects[Person]:
      return new_objects[Person].get(email)
    return Person.query.filter(Person.email == email).first()

  def parse_item(self):
    email = self.raw_value.lower()
    person = self.get_person(email)
    if not person and email != "":
      self.add_warning(errors.UNKNOWN_USER_WARNING, email=email)
    return person

  def get_value(self):
    person = getattr(self.row_converter.obj, self.key)
    if person:
      return person.email
    return self.value


class OwnerColumnHandler(UserColumnHandler):

  def parse_item(self):
    owners = set()
    email_lines = self.raw_value.splitlines()
    owner_emails = filter(unicode.strip, email_lines)  # noqa
    for raw_line in owner_emails:
      email = raw_line.strip().lower()
      person = self.get_person(email)
      if person:
        owners.add(person)
      else:
        self.add_warning(errors.UNKNOWN_USER_WARNING, email=email)

    if not owners:
      self.add_warning(errors.OWNER_MISSING)
      owners.add(get_current_user())

    return list(owners)

  def set_obj_attr(self):
    if self.value:
      for owner in self.value:
        self.row_converter.obj.owners.append(owner)

  def get_value(self):
    emails = [owner.email for owner in self.row_converter.obj.owners]
    return "\n".join(emails)


class SlugColumnHandler(ColumnHandler):

  def parse_item(self):
    if self.raw_value:
      return self.raw_value
    return ""


class DateColumnHandler(ColumnHandler):

  def parse_item(self):
    try:
      return parse(self.raw_value)
    except:
      self.add_error(
          u"Unknown date format, use YYYY-MM-DD or MM/DD/YYYY format")

  def get_value(self):
    date = getattr(self.row_converter.obj, self.key)
    if date:
      return date.strftime("%m/%d/%Y")
    return ""


class EmailColumnHandler(ColumnHandler):

  def parse_item(self):
    """ emails are case insensitive """
    return self.raw_value.lower()


class TextColumnHandler(ColumnHandler):

  """ Single line text field handler """

  def parse_item(self):
    """ Remove multiple spaces and new lines from text """
    if not self.raw_value:
      return ""

    return self.clean_whitespaces(self.raw_value)

  def clean_whitespaces(self, value):
    clean_value = re.sub(r'\s+', " ", value)
    if clean_value != value:
      self.add_warning(errors.WHITESPACE_WARNING,
                       column_name=self.display_name)
    return value


class RequiredTextColumnHandler(TextColumnHandler):

  def parse_item(self):
    value = self.raw_value or ""
    clean_value = self.clean_whitespaces(value)
    if not clean_value:
      self.add_error(errors.MISSING_VALUE_ERROR, column_name=self.display_name)
    return clean_value


class TextareaColumnHandler(ColumnHandler):

  """ Multi line text field handler """

  def parse_item(self):
    """ Remove multiple spaces and new lines from text """
    if not self.raw_value:
      return ""

    return re.sub(r'\s+', " ", self.raw_value).strip()


class MappingColumnHandler(ColumnHandler):

  """ Handler for mapped objects """

  def __init__(self, row_converter, key, **options):
    self.key = key
    self.mapping_name = key[4:]  # remove "map:" prefix
    self.mapping_object = IMPORTABLE.get(self.mapping_name)
    self.new_slugs = row_converter.block_converter.converter.new_objects[
        self.mapping_object]
    super(MappingColumnHandler, self).__init__(row_converter, key, **options)

  def parse_item(self):
    """ Remove multiple spaces and new lines from text """
    class_ = self.mapping_object
    lines = self.raw_value.splitlines()
    slugs = filter(unicode.strip, lines)  # noqa
    objects = []
    for slug in slugs:
      obj = class_.query.filter(class_.slug == slug).first()
      if obj:
        objects.append(obj)
      elif not (slug in self.new_slugs and self.dry_run):
        self.add_warning(errors.UNKNOWN_OBJECT,
                         object_type=pretty_class_name(class_), slug=slug)
    return objects

  def set_obj_attr(self):
    self.value = self.parse_item()

  def insert_object(self):
    """ Create a new mapping object """
    if not self.value:
      return
    current_obj = self.row_converter.obj
    for obj in self.value:
      if not Relationship.find_related(current_obj, obj):
        mapping = Relationship(source=current_obj, destination=obj)
        db.session.add(mapping)
    db.session.flush()

  def get_value(self):
    related_slugs = []
    related_ids = RelationshipHelper.get_ids_related_to(
        self.mapping_object.__name__,
        self.row_converter.object_class.__name__,
        [self.row_converter.obj.id])
    if related_ids:
      related_objects = self.mapping_object.query.filter(
          self.mapping_object.id.in_(related_ids))
      related_slugs = [o.slug for o in related_objects]
    return "\n".join(related_slugs)

  def set_value(self):
    pass


types = CustomAttributeDefinition.ValidTypes


class CustomAttributeColumHandler(TextColumnHandler):

  _type_handlers = {
      types.TEXT: lambda self: self.get_text_value(),
      types.DATE: lambda self: self.get_date_value(),
      types.DROPDOWN: lambda self: self.get_dropdown_value(),
      types.CHECKBOX: lambda self: self.get_checkbox_value(),
      types.RICH_TEXT: lambda self: self.get_rich_text_value(),
  }

  def parse_item(self):
    self.definition = self.get_ca_definition()
    value = CustomAttributeValue(custom_attribute_id=self.definition.id)
    value_handler = self._type_handlers[self.definition.attribute_type]
    value.attribute_value = value_handler(self)
    if value.attribute_value is None:
      return None
    return value

  def set_obj_attr(self):
    if self.value:
      self.row_converter.obj.custom_attribute_values.append(self.value)

  def insert_object(self):
    if self.value is None:
      return
    self.value.attributable_type = self.row_converter.obj.__class__.__name__
    self.value.attributable_id = self.row_converter.obj.id
    db.session.add(self.value)

  def get_ca_definition(self):
    for definition in self.row_converter.object_class\
            .get_custom_attribute_definitions():
      if definition.title == self.key:
        return definition
    return None

  def get_date_value(self):
    if not self.mandatory and self.raw_value == "":
      return None  # ignore empty fields
    value = None
    try:
      value = parse(self.raw_value)
    except:
      self.add_warning(errors.WRONG_VALUE, column_name=self.display_name)
    if self.mandatory and value is None:
      self.add_error(errors.MISSING_VALUE_ERROR, column_name=self.display_name)
    return value

  def get_checkbox_value(self):
    if not self.mandatory and self.raw_value == "":
      return None  # ignore empty fields
    value = self.raw_value.lower() in ("yes", "true")
    if self.raw_value.lower() not in ("yes", "true", "no", "false"):
      self.add_warning(errors.WRONG_VALUE, column_name=self.display_name)
      value = None
    if self.mandatory and value is None:
      self.add_error(errors.MISSING_VALUE_ERROR, column_name=self.display_name)
    return value

  def get_dropdown_value(self):
    choices_list = self.definition.multi_choice_options.split(",")
    valid_choices = map(unicode.strip, choices_list)  # noqa
    choice_map = {choice.lower(): choice for choice in valid_choices}
    value = choice_map.get(self.raw_value.lower())
    if value is None and self.raw_value != "":
      self.add_warning(errors.WRONG_VALUE, column_name=self.display_name)
    if self.mandatory and value is None:
      self.add_error(errors.MISSING_VALUE_ERROR, column_name=self.display_name)
    return value

  def get_text_value(self):
    if not self.mandatory and self.raw_value == "":
      return None  # ignore empty fields
    value = self.clean_whitespaces(self.raw_value)
    if self.mandatory and not value:
      self.add_error(errors.MISSING_VALUE_ERROR, column_name=self.display_name)
    return value

  def get_rich_text_value(self):
    if not self.mandatory and self.raw_value == "":
      return None  # ignore empty fields
    if self.mandatory and not self.raw_value:
      self.add_error(errors.MISSING_VALUE_ERROR, column_name=self.display_name)
    return self.raw_value


class OptionColumnHandler(ColumnHandler):

  def parse_item(self):
    prefixed_key = "{}_{}".format(
        self.row_converter.object_class._inflector.table_singular, self.key)
    item = Option.query.filter(
        and_(Option.title == self.raw_value.strip(),
             or_(Option.role == self.key,
                 Option.role == prefixed_key))).first()
    return item

  def get_value(self):
    option = getattr(self.row_converter.obj, self.key, None)
    return "" if option is None else option.title


class CheckboxColumnHandler(ColumnHandler):

  def parse_item(self):
    """ mandatory checkboxes will get evelauted to false on empty value """
    if self.raw_value == "":
      return False
    value = self.raw_value.lower() in ("yes", "true")
    if self.raw_value.lower() not in ("yes", "true", "no", "false"):
      self.add_warning(errors.WRONG_VALUE, column_name=self.display_name)
    return value

  def get_value(self):
    val = getattr(self.row_converter.obj, self.key, False)
    return "true" if val else "false"


class ProgramColumnHandler(ColumnHandler):

  def parse_item(self):
    """ get a program from slugs """
    new_objects = self.row_converter.block_converter.converter.new_objects
    new_programs = new_objects[Program]
    if self.raw_value == "":
      self.add_error(errors.MISSING_VALUE_ERROR, column_name=self.display_name)
      return None
    slug = self.raw_value
    if slug in new_programs:
      program = new_programs[slug]
    else:
      program = Program.query.filter(Program.slug == slug).first()

    if program is None:
      self.add_error(errors.UNKNOWN_OBJECT, object_type="Program", slug=slug)

    return program.id

  def get_value(self):
    val = getattr(self.row_converter.obj, self.key, False)
    return "true" if val else "false"


COLUMN_HANDLERS = {
    "contact": UserColumnHandler,
    "description": TextareaColumnHandler,
    "end_date": DateColumnHandler,
    "kind": OptionColumnHandler,
    "link": TextColumnHandler,
    "email": EmailColumnHandler,
    "means": OptionColumnHandler,
    "notes": TextareaColumnHandler,
    "owners": OwnerColumnHandler,
    "private": CheckboxColumnHandler,
    "report_end_date": DateColumnHandler,
    "report_start_date": DateColumnHandler,
    "secondary_contact": UserColumnHandler,
    "secondary_assessor": UserColumnHandler,
    "principal_assessor": UserColumnHandler,
    "slug": SlugColumnHandler,
    "start_date": DateColumnHandler,
    "status": StatusColumnHandler,
    "test_plan": TextareaColumnHandler,
    "title": RequiredTextColumnHandler,
    "verify_frequency": OptionColumnHandler,
    "program_id": ProgramColumnHandler,
}
