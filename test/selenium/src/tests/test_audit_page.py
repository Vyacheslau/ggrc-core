# Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: Viachaslau_Karachun@epam.com
# Maintained By: Viachaslau_Karachun@epam.com

# pylint: disable=invalid-name
# pylint: disable=no-self-use
# pylint: disable=too-many-arguments

"""Tests Audit object"""

import math
import random

import pytest

from lib import base, environment
from lib.base import Pagination
from lib.business_layer.rest_service import AssessmentsService
from lib.constants import url
from lib.page.widget import generic_widget


class TestAuditPage(base.Test):
  """Tests Audit page."""

  ITEMS_PER_PAGE = 10

  @pytest.mark.smoke_tests
  def test_assessments_widget_has_correct_page_count(self, selenium,
                                                     rest_create_audit,
                                                     rest_create_control):
    """Checks if assessments widget shows correct page count."""
    assessments_count = random.randint(1, 100)
    expected_page_count = int(math.ceil(
      float(assessments_count) / self.ITEMS_PER_PAGE))

    AssessmentsService().create_assessments(count=assessments_count,
                                            obj=rest_create_control,
                                            audit=rest_create_audit)
    selenium.get(environment.APP_URL + url.AUDIT.format(
      rest_create_audit["id"]) + url.Widget.ASSESSMENTS)
    assessments_widget = generic_widget.Assessments(selenium)
    assessments_widget.pagination_control.select_items_per_page(
      self.ITEMS_PER_PAGE)

    actual_page_count = assessments_widget.pagination_control.get_page_count()

    assert expected_page_count == actual_page_count

  @pytest.mark.parametrize("expected_items_count", [10, 25, 50])
  @pytest.mark.smoke_tests
  def test_assessments_widget_shows_correct_items_count_per_page \
      (self, selenium, rest_create_audit, rest_create_control,
       expected_items_count):
    """Checks if assessments widget shows correct items count per page."""
    assessments_count = expected_items_count + 1
    AssessmentsService().create_assessments(count=assessments_count,
                                            obj=rest_create_control,
                                            audit=rest_create_audit)
    selenium.get(environment.APP_URL + url.AUDIT.format(
      rest_create_audit["id"]) + url.Widget.ASSESSMENTS)
    assessments_widget = generic_widget.Assessments(selenium)
    assessments_widget.pagination_control.select_items_per_page(
      expected_items_count)

    assessments_widget_refreshed = generic_widget.Assessments(selenium)

    assert expected_items_count == len(
      assessments_widget_refreshed.members_listed)

  @pytest.mark.parametrize("assessments_count,button_name,expected_page_number",
                           [(21, Pagination.NEXT_PAGE, 2),
                            (21, Pagination.LAST_PAGE, 3)])
  @pytest.mark.smoke_tests
  def test_switch_page_forward_buttons_work_correct_on_assessments_widget(
    self, selenium, rest_create_audit, rest_create_control,
    assessments_count, button_name, expected_page_number):
    """Checks that switch page forward buttons (NEXT_PAGE, LAST_PAGE)."""
    AssessmentsService().create_assessments(count=assessments_count,
                                            obj=rest_create_control,
                                            audit=rest_create_audit)
    selenium.get(environment.APP_URL + url.AUDIT.format(
      rest_create_audit["id"]) + url.Widget.ASSESSMENTS)
    assessments_widget = generic_widget.Assessments(selenium)
    assessments_widget.pagination_control.select_items_per_page(
      self.ITEMS_PER_PAGE)
    assessments_widget.pagination_control.switch_page(button_name)

    actual_page_number = assessments_widget.pagination_control. \
      get_displayed_page_number()

    assert expected_page_number == actual_page_number

  @pytest.mark.parametrize("assessments_count,button_name,expected_page_number",
                           [(31, Pagination.PREVIOUS_PAGE, 3),
                            (31, Pagination.FIRST_PAGE, 1)])
  @pytest.mark.smoke_tests
  def test_switch_page_back_buttons_work_correct_on_assessments_widget(
    self, selenium, rest_create_audit, rest_create_control, assessments_count,
    button_name, expected_page_number):
    """Checks that switch page back buttons (PREVIOUS_PAGE, FIRST_PAGE)."""
    AssessmentsService().create_assessments(count=assessments_count,
                                            obj=rest_create_control,
                                            audit=rest_create_audit)
    selenium.get(environment.APP_URL + url.AUDIT.format(
      rest_create_audit["id"]) + url.Widget.ASSESSMENTS)
    assessments_widget = generic_widget.Assessments(selenium)
    assessments_widget.pagination_control.select_items_per_page(
      self.ITEMS_PER_PAGE)
    assessments_widget.pagination_control.switch_page(Pagination.LAST_PAGE)

    assessments_widget.pagination_control.switch_page(button_name)

    actual_page_number = assessments_widget.pagination_control. \
      get_displayed_page_number()

    assert expected_page_number == actual_page_number
