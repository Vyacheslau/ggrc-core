# Copyright (C) 2015 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: jernej@reciprocitylabs.com
# Maintained By: jernej@reciprocitylabs.com

# pylint: disable=too-few-public-methods

"""App enpoints constants"""

API = "api"
AUTHENTICATION = API + "/roles?name__in=Auditor&_=1463991908086"
DASHBOARD = "dashboard"
ADMIN_DASHBOARD = "admin"
PROGRAMS = "programs"
WORKFLOWS = "workflows"
AUDITS = "audits"
AUDIT = AUDITS + "/{0}"
ASSESSMENTS = "assessments"
REQUESTS = "requests"
ISSUES = "issues"
REGULATIONS = "regulations"
POLICIES = "policies"
STANDARDS = "standards"
CONTRACTS = "contracts"
CLAUSES = "clauses"
SECTIONS = "sections"
CONTROLS = "controls"
OBJECTIVES = "objectives"
PEOPLE = "people"
ORG_GROUPS = "org_groups"
VENDORS = "vendors"
ACCESS_GROUPS = "access_groups"
SYSTEMS = "systems"
PROCESSES = "processes"
DATA_ASSETS = "data_assets"
PRODUCTS = "products"
PROJECTS = "projects"
FACILITIES = "facilities"
MARKETS = "markets"
RISKS = "risks"
THREATS = "threats"


class Widget(object):
  """Widget anchors"""
  INFO = "#info_widget"
  CUSTOM_ATTRIBUTES = "#custom_attribute_widget"
  EVENTS = "#events_list_widget"
  ROLES = "#roles_list_widget"
  PEOPLE = "#people_list_widget"
  ASSESSMENTS = "#assessment_widget"
