# Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: Viachaslau_Karachun@epam.com
# Maintained By: Viachaslau_Karachun@epam.com

# pylint: disable=too-few-public-methods

"""The module contains functionality for working with json templates"""

import copy
import json
import os


class TemplateProvider(object):
  """The class proccesses json templates"""
  RELATIVE_PATH_TEMPLATE = "template/{0}.json"
  parsed_data = dict()

  @staticmethod
  def get_template_as_dict(obj_type, **kwargs):
    """The method returns object representation based on json template"""
    try:
      obj = copy.deepcopy(TemplateProvider.parsed_data[obj_type])
    except KeyError:
      path = os.path.join(
        os.path.dirname(__file__),
        TemplateProvider.RELATIVE_PATH_TEMPLATE.format(obj_type))
      with open(path) as json_file:
        json_data = json_file.read()
      data = json.loads(json_data)
      TemplateProvider.parsed_data[obj_type] = data
      obj = copy.deepcopy(data)
    obj.update(kwargs)
    return {obj_type: obj}
