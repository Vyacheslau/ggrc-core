# Copyright (C) 2016 Google Inc., authors, and contributors <see AUTHORS file>
# Licensed under http://www.apache.org/licenses/LICENSE-2.0 <see LICENSE file>
# Created By: Viachaslau_Karachun@epam.com
# Maintained By: Viachaslau_Karachun@epam.com

"""Model for Map Assessment Templates modal window"""

from lib import base
from lib.constants import locator
from lib.page.modal.create_new_object import AssessmentTemplates


class MapAssessmentTemplates(base.Modal):
  """Class representing Map Assessment Templates modal window"""

  def __init__(self, driver):
    super(MapAssessmentTemplates, self).__init__(driver)
    self.create_new_assessment_template_button = base.Button(
        driver,
        locator.ModalMapAssessmentTemplates.
            CREATE_NEW_ASSESSMENT_TEMPLATE_BUTTON)

  def click_on_create_new_assessment_template_button(self):
    """Clicks on Create New Assessment Template button"""
    self.create_new_assessment_template_button.click()
    return AssessmentTemplates(self._driver)
