# Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: Viachaslau_Karachun@epam.com
# Maintained By: Viachaslau_Karachun@epam.com

"""Assessment Templates on Audit page smoke tests"""

import pytest

from lib import environment
from lib.base import Test
from lib.constants import url
from lib.page.widget.generic_widget import AssessmentTemplates


class TestAuditAssessmentTemplatesWidget(Test):
  """Assessment Templates widget on Audit page tests"""

  @pytest.mark.smoke_tests
  def test_create_assessment_template(self, selenium, new_audit_rest):
    """Creates Assessment Template on Audit page"""
    assessment_template_widget_url = environment.APP_URL + url.AUDIT.format(
        new_audit_rest["id"]) + url.Widget.ASSESSMENT_TEMPLATES
    selenium.get(assessment_template_widget_url)
    assessment_templates_widget = AssessmentTemplates(selenium)
    create_assessment_template_modal = assessment_templates_widget\
        .click_on_map_assessment_templates_button()\
        .click_on_create_new_assessment_template_button()
