"""Patch for https://bugs.launchpad.net/zope2/+bug/740831."""
from logging import getLogger
logger = getLogger(__name__)


def supports_retry(self):
  if getattr(self.response, "_streaming", False):
    # we try to retry a request whose response has already (at least partially)
    # been written -- this leads to desaster (wrong responses to subsequents
    # requests). Prevent it.
    logger.error("prevent request retry for which part of its response has already been written")
    return False
  return self._dm_ori_supports_retry()
     

# patch HTTPResponse
from ZPublisher.HTTPRequest import HTTPRequest

HTTPRequest._dm_ori_supports_retry = HTTPRequest.supports_retry
HTTPRequest.supports_retry = supports_retry

logger.info("ZPublisher.HTTPRequest.supports_retry patched.")

