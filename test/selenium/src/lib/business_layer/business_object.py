class BusinessObject(dict):
  """Model representing business entities used for REST queries."""

  def __init__(self, obj_id, href, obj_type):
    super(BusinessObject, self).__init__()
    self["id"] = obj_id
    self["href"] = href
    self["type"] = obj_type
