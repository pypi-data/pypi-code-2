from XMLModel import XMLModel
from rightscale.util import ElementTreeValueOK
from Tag import Tag
from Tags import Tags
from ServerSettings import ServerSettings
from ServerTemplate import ServerTemplate

# TODO(sissel): Refactor
import xml.etree.ElementTree as ElementTree
XMLCLASS = ElementTree.XML("<a />").__class__

class Server(XMLModel):
  _nickname = None
  _href = None
  _state = None
  _created_at = None
  _current_instance_href = None
  _tags = list()

  _server_template = None
  _server_template_href = None

  _deployment = None
  _deployment_href = None

  # ServerSettings
  _settings = None

  def __str__(self):
    return "%s" % (self.nickname)

  @property
  def href(self):
    return self._href

  @href.setter
  @ElementTreeValueOK
  def href(self, value):
    self._href = value

  @property
  def settings(self):
    if self._settings is None:
      self._settings = ServerSettings("%s/settings" % self._href, self.rsapi)
    return self._settings

  @settings.setter
  @ElementTreeValueOK
  def settings(self, value):
    self._settings = ServerSettings(value, self.rsapi)

  @property
  def server_template(self):
    # TODO(sissel): Do lazy loading.
    if self._server_template is None:
      self.get_server_template
    return self._server_template

  def get_server_template(self):
    self._server_template = ServerTemplate(self.server_template_href, self.rsapi)
  # def get_server_template

  @server_template.setter
  @ElementTreeValueOK
  def server_template(self, value):
    # Defer loading ServerTemplate until it is requested.
    self._server_template_href = value

  @property
  def current_instance_href(self):
    return self._current_instance_href

  @current_instance_href.setter
  @ElementTreeValueOK
  def current_instance_href(self, value):
    self._current_instance_href = value

  @property
  def deployment_href(self):
    return self._deployment_href

  @deployment_href.setter
  @ElementTreeValueOK
  def deployment_href(self, value):
    self._deployment_href = value

  @property
  def deployment(self):
    assert self._deployment_href
    from Deployment import Deployment
    return Deployment(self._deployment_href, self.rsapi)

  @property
  def nickname(self):
    return self._nickname

  @nickname.setter
  @ElementTreeValueOK
  def nickname(self, value):
    self._nickname = value

  @property
  def tags(self):
    if not self._tags:
      self._tags = Tags(rsapi=self.rsapi)
      # Use current_instance_href if it is present, otherwise
      # use the normal server href.
      if self.current_instance_href:
        self._tags.for_resource(self.current_instance_href)
      else:
        self._tags.for_resource(self.href)
    #self._tags = current_tags
    return self._tags

  @tags.setter
  def tags(self, value):
    self.taint("tags")
    print "Setting tags for %s to %s" % (self, value)
    if isinstance(value, XMLCLASS) and value.tag == "tags":
      self._tags = list()
      for element in value:
        self.tags.append(Tag(element, self.rsapi))
      # for element ...
    else:
      self._tags = value
  # def tags

  def save(self):
    if self.tainted["tags"]:
      self.rsapi.save_tags(self, self.tags)
  # def save

  ELEMENTS = {
    "current-instance-href": current_instance_href, 
    "href": href, 
    "nickname": nickname, 
    "server-template-href": server_template,
    "settings": settings, 
    "deployment-href": deployment_href,

    # TODO(sissel): Implement these
    "updated-at": None,
    "created-at": None,
    "state": None,
    "server-type": None,

    # Ignore the 'tags' data as this data is for the 'next' server version,
    # not the current instance.
    "tags": None
  }
# class Server
