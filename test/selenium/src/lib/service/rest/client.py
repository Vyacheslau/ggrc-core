# Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: Viachaslau_Karachun@epam.com
# Maintained By: Viachaslau_Karachun@epam.com

# pylint: disable=too-few-public-methods

"""The module contains classes for working with REST api"""

import Cookie
import json

import requests

from lib import environment
from lib.service.rest.template_provider import TemplateProvider
from lib.constants import url
from lib.utils.test_utils import append_random_string


class RestClient(object):
  """The class used for HTTP interactions with App's REST API"""
  BASIC_HEADERS = {'X-Requested-By': 'gGRC',
                   'Content-Type': 'application/json',
                   'Accept-Encoding': 'gzip, deflate'}
  AUTH = url.API + "/roles?name__in=Auditor&_=1463991908086"

  def __init__(self, endpoint):
    self.url = "{0}{1}/{2}".format(environment.APP_URL, url.API, endpoint)
    self.session = None

  def init_session(self):
    """Returns authorization cookie value"""
    response = requests.get(environment.APP_URL + self.AUTH)
    cookie = Cookie.SimpleCookie()
    cookie.load(response.headers["Set-Cookie"])
    self.session = cookie["session"].value

  def get_headers(self):
    """Returns prepared header for HTTP call"""
    headers = self.BASIC_HEADERS
    if self.session is None:
      self.init_session()
    headers["Cookie"] = "session={0}".format(self.session)
    return headers

  def create_objects(self, obj_type, count=1, title_postfix=None, **kwargs):
    """The method sends HTTP request for objects creation via REST API"""
    request_body = generate_body_by_template(count=count,
                                             template_name=obj_type,
                                             title_postfix=title_postfix,
                                             **kwargs)
    headers = self.get_headers()
    response = requests.post(url=self.url, data=request_body, headers=headers)
    return response


def generate_body_by_template(count, template_name, title_postfix=None,
                              **kwargs):
  """The function generates list of objects based on object type  (assessment,
  control, etc) from json templates"""

  def upgrade_template(template_name, title_postfix=None, **kwargs):
    """The function return updated template json with random title by template
    name"""
    obj_title = append_random_string(template_name)
    if title_postfix is not None:
      obj_title += title_postfix
    return TemplateProvider.get_template_as_dict(template_name, title=obj_title,
                                                 **kwargs)

  objects = [upgrade_template(template_name=template_name,
                              title_postfix=title_postfix,
                              **kwargs) for _ in xrange(count)]
  return json.dumps(objects)
