# Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: Viachaslau_Karachun@epam.com
# Maintained By: Viachaslau_Karachun@epam.com

"""Tests Audit object"""
# pylint: disable=no-self-use
# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=unused-argument

import pytest  # pylint: disable=import-error

from lib import base, environment
from lib.business_layer.rest_service import AssessmentsService
from lib.constants import url
from lib.page.widget import generic_widget


class TestAuditPage(base.Test):
  """Tests Audit page."""

  @pytest.mark.smoke_tests
  def test_assessments_widget_has_correct_page_count(self, selenium,
                                                     rest_create_audit,
                                                     rest_create_control):
    """Checks if assessments widget contains pagination after big count of
    assessments is generated."""
    assessments_count = 50
    items_per_page = 10
    expected_page_count = assessments_count / items_per_page

    AssessmentsService().create_assessments(count=assessments_count,
                                            obj=rest_create_control,
                                            audit=rest_create_audit)
    selenium.get(environment.APP_URL + url.AUDIT.format(
      rest_create_audit["id"]) + url.Widget.ASSESSMENTS)
    assessments_widget = generic_widget.Assessments(selenium)
    assessments_widget.pagination_control.select_items_per_page(items_per_page)
    actual_page_count = assessments_widget.pagination_control.get_page_count()

    assert expected_page_count == actual_page_count
