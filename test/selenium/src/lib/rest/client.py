# Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: Viachaslau_Karachun@epam.com
# Maintained By: Viachaslau_Karachun@epam.com

# pylint: disable=too-few-public-methods

"""The module contains classes for working with REST api."""

import Cookie
import json

import requests

from lib import environment
from lib.constants import url
from lib.rest.template_provider import TemplateProvider
from lib.utils.test_utils import append_random_string


class BusinessObject(object):
  """Model representing business entities used for REST queries."""

  def __init__(self, obj_id, href, obj_type):
    self.obj_id = obj_id
    self.href = href
    self.obj_type = obj_type

  def as_dict(self):
    return {"id": self.obj_id, "href": self.href, "type": self.obj_type}


class RestClient(object):
  """The class used for HTTP interactions with App's REST API."""
  BASIC_HEADERS = {'X-Requested-By': 'gGRC',
                   'Content-Type': 'application/json',
                   'Accept-Encoding': 'gzip, deflate'}

  def __init__(self, endpoint):
    self.url = "{0}{1}/{2}".format(environment.APP_URL, url.API, endpoint)
    self.session = None

  def init_session(self):
    """Returns authorization cookie value."""
    response = requests.get(environment.APP_URL + url.AUTHENTICATION)
    cookie = Cookie.SimpleCookie()
    cookie.load(response.headers["Set-Cookie"])
    self.session = cookie["session"].value

  def get_headers(self):
    headers = self.BASIC_HEADERS
    if not self.session:
      self.init_session()
    headers["Cookie"] = "session={0}".format(self.session)
    return headers

  def create_objects(self, obj_type, count=1, title_postfix=None, **kwargs):
    """The method sends HTTP request for objects creation via REST API."""
    request_body = self.generate_body_by_template(count=count,
                                                  template_name=obj_type,
                                                  title_postfix=title_postfix,
                                                  **kwargs)
    headers = self.get_headers()
    response = requests.post(url=self.url, data=request_body, headers=headers)
    return response

  def generate_body_by_template(self, count, template_name, title_postfix=None,
                                **kwargs):
    """The function generates list of objects based on object type  (assessment,
    control, etc) from json templates."""
    objects = list()
    for _ in xrange(count):
      obj_title = append_random_string(template_name)
      if title_postfix:
        obj_title += title_postfix
      objects.append(
        TemplateProvider.get_template_as_dict(template_name, title=obj_title,
                                              **kwargs))
    return json.dumps(objects)
