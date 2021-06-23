
from pdref.models import PandasRef, AppliesTo, Category

#------------------------------------------------------------------------------
def pager(id, direction, fl, query):
    """ Get the previous/next id from the currently selected subset of
        records (or the whole record set if no selection). Loop around if
        the start/end of the recordset is reached. """

    if direction == 'none': return id
    current = 0

    # Get a list of id values we need to page through. This may be all the
    # records (fl will be empty), or just a filtered subset (fl will have content).
    if query == '':
        ids = list(PandasRef.objects.filter(**fl)\
                    .order_by('category__category','command')\
                    .values_list('pk', flat=True))
    else:
        ids = list(PandasRef.objects.filter(query, **fl)\
                .order_by('category__category','command')\
                .values_list('pk', flat=True))

    # Identify and store the index of the currently-displayed record.
    for i in range(0, len(ids)):
        if id == ids[i]:
            current = i
            break

    # Get the next/previous id value. When the end/beginning is reached,
    # loop around to the other end of the set.
    if direction == 'next':
        if current + 1 >= len(ids): return ids[0]
        else: return ids[current + 1]
    else:
        if current == 0: return ids[len(ids) - 1]
        else: return ids[current - 1]

#------------------------------------------------------------------------------
def getQuery(match):
    """ Construct a dynamic OR query string. """

    from functools import reduce
    from operator import or_
    from django.db.models import Q

    parts = []
    fields = ('command__icontains','example__icontains','description__icontains')
    for field in fields:
        parts.append(Q(**{field:match}))
    query = reduce(or_, parts)
    return query

    # | = OR, & = AND, ~ = NOT (all can be combined)
    # test = 'con'
    # Q1 = Q(author__icontains=test)
    # Q2 = Q(title__icontains=test)
    # res = FlatBook.objects.filter(Q1|Q2)

#------------------------------------------------------------------------------