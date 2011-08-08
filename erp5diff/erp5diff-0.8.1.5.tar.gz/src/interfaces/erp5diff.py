from zope.interface import Interface

class IERP5Diff(Interface):
  """
    Make a difference between two XML documents using XUpdate.
    Use some assumptions in ERP5's data representation.

    The strategy is:
      1. Find a matching element among elements of the other XML document at the same depth.
      2. Use the first matching element, even if there can be other better elements.
      3. Assume that two elements are matching, if the tag names are identical. If either of
         them has an attribute 'id', the values of the attrib 'id' also must be identical.
      4. Don't use xupdate:rename for elements. It should be quite rare to rename tag names
         in ERP5, and it is too complicated to support this renaming.
      5. Ignore some types of nodes, such as EntityReference and Comment, because they are not
         used in ERP5 XML documents.
  """

  def compare(self, old_xml, new_xml):
    """
      Compare two given XML documents.
      If an argument is a string, it is assumed to be a XML document itself.
      Otherwise, it is assumed to be a file object which contains a XML document.
    """

  def output(self, output_file=None):
    """
      Output the result of parsing XML documents to 'output_file'.
      If it is not specified, stdout is assumed.
    """


  def outputString(self):
    """
      Return the result as a string object.
    """

  def main():
    """
      The main routine of ERP5Diff.
    """