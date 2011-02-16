"""
Schema directive
================

  >>> from dolmen.content import schema, get_schema

  >>> class Test(object):
  ...     pass

  >>> print get_schema(Test)
  None
  >>> inst = Test()
  >>> print get_schema(inst)
  None


  >>> class TestWrongSchema(object):
  ...     schema('toto')
  Traceback (most recent call last):
  ...
  GrokImportError: schema directive can only use interface classes.
  toto is not an interface class.


  >>> from zope.interface import Interface

  >>> class SchemaA(Interface):
  ...     pass

  >>> class SchemaB(Interface):
  ...     pass

  >>> class TestWithSingleSchema(object):
  ...     schema(SchemaA)

  >>> get_schema(TestWithSingleSchema)
  [<InterfaceClass dolmen.content.tests.schema.directive.SchemaA>]


  >>> class TestWithMultipleSchema(object):
  ...     schema(SchemaA, SchemaB)

  >>> get_schema(TestWithMultipleSchema)
  [<InterfaceClass dolmen.content.tests.schema.directive.SchemaA>,
   <InterfaceClass dolmen.content.tests.schema.directive.SchemaB>]


  >>> from martian import baseclass
  >>> class baseClass(object):
  ...     baseclass()

  >>> print get_schema(baseClass)
  None

"""
