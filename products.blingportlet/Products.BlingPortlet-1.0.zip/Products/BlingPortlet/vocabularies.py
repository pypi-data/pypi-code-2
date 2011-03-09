from zope.schema.vocabulary import SimpleVocabulary


changeVocabulary = SimpleVocabulary([
                        SimpleVocabulary.createTerm(u'Random'),
                        SimpleVocabulary.createTerm(u'Each second'),
                        SimpleVocabulary.createTerm(u'Each minute'),
                        SimpleVocabulary.createTerm(u'Each hour'),
                        SimpleVocabulary.createTerm(u'Each day'),
                        SimpleVocabulary.createTerm(u'Each week'),
                        SimpleVocabulary.createTerm(u'Each month'),
                        SimpleVocabulary.createTerm(u'Each year')])

orderingVocabulary = SimpleVocabulary([
    SimpleVocabulary.createTerm(u'Random'),
    SimpleVocabulary.createTerm(u'Sequential')])
    