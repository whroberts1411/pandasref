
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Value, IntegerField

from pdref.models import PandasRef, AppliesTo, Category
import plotly.io as pio
import plotly.express as ex
import pandas as pd

# Define the default template for our plots, combining two built-in templates.
pio.templates.default = 'ggplot2+xgridoff'

#------------------------------------------------------------------------------
@login_required
def stats(request):
    """ Display a selection of counts and charts of the database contents. """

    # Export the overall record totals. ---------------------------------------
    tot = getTotals()

    # Export the category data and bar graph. ---------------------------------
    cat = getCategories()
    df = pd.DataFrame(list(cat))
    fig = ex.bar(df, x='category__category', y='count',
            title='Category Breakdown',
            color="category__category", hover_name='category__category',
            labels={'category__category':'Category'})
    fig.update_xaxes(title_text='Category')
    fig.update_layout(showlegend=False)
    graph = fig.to_html(include_plotlyjs='cdn')

    # Export the applies-to data and pie chart. -------------------------------
    typ = getAppliesTo()
    df2 = pd.DataFrame(list(typ))
    fig2 = ex.pie(df2, values='count', names='appliesto__appliesto',
                title='Type Breakdown', hover_name='appliesto__appliesto',
                height=350, labels={'appliesto__appliesto':'  Type'})
    #fig2.update_traces(textposition='inside', textinfo='percent+label')
    pie = fig2.to_html(include_plotlyjs='cdn')

    # Export the combined category/applies-to data and bar chart. -------------
    ret = getCombined()
    df3 = pd.DataFrame(list(ret[0]))
    fig3 = ex.bar(df3, x='category__category', y='count',
                color='appliesto__appliesto', title='Types per Category',
                labels={'appliesto__appliesto':'  Type',
                        'category__category':'Category'},
                hover_name='appliesto__appliesto')
                
    # NB - 'categoryorder' and 'category ascending' are plotly built-in parameter
    #       names, and have no connection to our database 'category' column.
    fig3.update_xaxes(title_text='Category', categoryorder='category ascending')
    bars = fig3.to_html(include_plotlyjs='cdn')

    # Pass all the datasets and charts to the template. -----------------------
    context = {'tot':tot, 'cat':cat, 'graph':graph, 'typ':typ, 'pie':pie,
                'comb':ret[1], 'bars':bars}
    return render(request, 'stats/stats.html', context )

#------------------------------------------------------------------------------
def getTotals():
    """ Get the totals of all tables from the database. """

    pan = PandasRef.objects.all().count()
    cat = Category.objects.all().count()
    typ = AppliesTo.objects.all().count()
    return [pan,cat,typ]

#------------------------------------------------------------------------------
def getCategories():
    """ Return a queryset of all Category values with totals. """

    cat1 = PandasRef.objects.values('category__category')\
                        .annotate(count=Count('category'))
    cat2 = Category.objects.values('category')\
                        .filter(pandasref=None)\
                        .annotate(count=Value(0, output_field=IntegerField()))
    cat = cat1.union(cat2)
    return cat

#------------------------------------------------------------------------------
def getAppliesTo():
    """ Return a queryset of all AppliesTo values with counts.  """

    typ = PandasRef.objects.values('appliesto__appliesto')\
                        .annotate(count=Count('appliesto'))
    return typ

#------------------------------------------------------------------------------
def getCombined():
    """ Get a combined breakdown of categories by applies-to, with counts.
        Convert to a list, and eliminate duplicate category names so that
        they're not repeated in the first column (replace with a single
        space character). """

    res = PandasRef.objects.values('category__category','appliesto__appliesto')\
                            .order_by('category__category', 'appliesto__appliesto')\
                            .annotate(count=Count('category'))

    # Convert queryset to a list of dictionaries.
    lst = list(res)
    # Convert to a list of lists.
    ret = []
    for idx in range(len(lst)):
        ret.append(list(lst[idx].values()))
    # Replace duplicate Category values with a single space.
    curr = ''
    for idx in range(len(ret)):
        if ret[idx][0] == curr: ret[idx][0] = ' '
        else: curr = ret[idx][0]

    return [res, ret]

#------------------------------------------------------------------------------

    # Create a html table from a dataframe. Not very nice - just a plain table.
    # tbl = df.to_html(columns=['category__category', 'count'],index=False)
    # Create a list of rows from a dataframe - can be iterated over in the template.
    # lst = df.values.tolist()

#------------------------------------------------------------------------------