# Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: Viachaslau_Karachun@epam.com
# Maintained By: Viachaslau_Karachun@epam.com

# pylint: disable=too-few-public-methods

"""The module provides API for creating and manipulating GGRC's business
objects via REST."""

import json

from lib.business_layer.business_object import BusinessObject
from lib.constants import url
from lib.rest.client import RestClient


class BaseService(object):
  """Base class for business layer's services objects."""
  def __init__(self, endpoint):
    self.client = RestClient(endpoint)

  @staticmethod
  def get_list_of_created_objects(response):
    """The function forms the list of business entities from response."""
    business_objects_list = list()
    for object_element in json.loads(response.text):
      object_key = object_element[1].keys()[0]
      created_object = object_element[1][object_key]
      business_object = BusinessObject(created_object["id"],
                                       created_object["selfLink"],
                                       created_object["type"])
      business_objects_list.append(business_object)
    return business_objects_list


class ControlsService(BaseService):
  """The class incapsulates logic for working with business entity Control."""

  def __init__(self):
    super(ControlsService, self).__init__(url.CONTROLS)

  def create_controls(self, count):
    return self.get_list_of_created_objects(
      self.client.create_objects("control", count=count))


class ProgramsService(BaseService):
  """The class incapsulates logic for working with business entity Program."""

  def __init__(self):
    super(ProgramsService, self).__init__(url.PROGRAMS)

  def create_programs(self, count):
    return self.get_list_of_created_objects(
      self.client.create_objects("program", count=count))


class AuditsService(BaseService):
  """The class incapsulates logic for working with business entity Audit."""

  def __init__(self):
    super(AuditsService, self).__init__(url.AUDITS)

  def create_audits(self, count, program):
    return self.get_list_of_created_objects(
      self.client.create_objects("audit", count=count, program=program))


class AssessmentsService(BaseService):
  """The class incapsulates logic for working with business entity
  Assessment."""

  def __init__(self):
    super(AssessmentsService, self).__init__(url.ASSESSMENTS)

  def create_assessments(self, count, obj, audit):
    return self.get_list_of_created_objects(
      self.client.create_objects("assessment", count=count, object=obj,
                                 audit=audit))
