def initialize(context):
    from Products.BooleanIndex.BooleanIndex import BooleanIndex
    from Products.BooleanIndex.BooleanIndex import manage_addBooleanIndex
    from Products.BooleanIndex.BooleanIndex import manage_addBooleanIndexForm

    context.registerClass(
        BooleanIndex,
        permission='Add Pluggable Index',
        constructors=(manage_addBooleanIndexForm,
                      manage_addBooleanIndex),
        icon='www/index.gif',
        visibility=None
    )

    # Don't add a hard dependency on ATContentTypes
    try:
        from Products.ATContentTypes.criteria import _criterionRegistry
        from Products.ATContentTypes.criteria.boolean import ATBooleanCriterion
    except ImportError:
        pass
    else:
        # Make boolean criteria available for the BooleanIndex
        crit_id = ATBooleanCriterion.meta_type
        crit_reg = _criterionRegistry
        index = BooleanIndex.meta_type

        indices = crit_reg.criterion2index.get(crit_id, ())
        crit_reg.criterion2index[crit_id] = indices + (index, )

        value = crit_reg.index2criterion.get(index, ())
        crit_reg.index2criterion[index] = value + (crit_id,)
