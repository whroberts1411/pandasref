
from django.http.request import host_validation_re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template import loader
from django.db.models import Count, Value, IntegerField

from .models import PandasRef, AppliesTo, Category
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
import io
from utilities import misc

#------------------------------------------------------------------------------
@login_required
def index(request):
    """ Main startup screen, which will display a table of the current
        database records, for the Pandas reference data.  """

    fl = {}
    opts = []
    command, example, appliesto, category, description = '','','','',''
    all, query = '',''

    if request.method == 'POST':
        # Store the filter values from the screen
        command = request.POST['command']
        example = request.POST['example']
        temp = request.POST.getlist('appliesto')
        if temp: appliesto = temp[0]
        temp = request.POST.getlist('category')
        if temp: category = temp[0]
        description = request.POST['description']
        all = request.POST['all']

         # Assemble the AND filter condition (as a dictionary)
        if command: fl['command__icontains'] = command
        if example: fl['example__icontains'] = example
        if appliesto: fl['appliesto__appliesto'] = appliesto
        if category: fl['category__category'] = category
        if description: fl['description__icontains'] = description
        # Assemble the OR conditions
        if all != '': query = misc.getQuery(all)

        # Store the values for later screen refreshes
        request.session['0'] = fl
        request.session['filter'] = [command,example,appliesto,category,description,all]
        opts = request.session['filter']
    else:
        if '0' in request.session: fl = request.session['0']
        if 'filter' in request.session:
            opts = request.session['filter']
            if opts[5] != '': query = misc.getQuery(opts[5])

    # Get the required records from database
    app = AppliesTo.objects.all().order_by('appliesto')
    cat = Category.objects.all().order_by('category')
    if query == '':
        pds = PandasRef.objects.filter(**fl).order_by('category__category','command')
    else:
        pds = PandasRef.objects.filter(query,**fl).order_by('category__category','command')
    # Create the screen context dictionary
    context = {'pds':pds, 'app':app, 'cat':cat, 'opts':opts}
    return render(request, 'pdref/index.html', context)

#------------------------------------------------------------------------------
@login_required
def newrec(request):
    """ Add a new pandas reference record to the database.  """

    message = ''
    if request.method == 'POST':
        # Store the new values from the screen
        command = request.POST['command']
        example = request.POST['example']
        desc = request.POST['description']
        appliesto = request.POST.getlist('appliesto')[0]
        category = request.POST.getlist('category')[0]
        if 'inplace' in request.POST:
            inplace = True
        else:
            inplace = False

        # Create a new PandasRef record from the entered details
        app = AppliesTo.objects.get(appliesto=appliesto)
        cat = Category.objects.get(category=category)
        PandasRef.objects.create(command=command,example=example,description=desc,
                                    appliesto=app,category=cat,inplace=inplace)
        message = 'New record details have been created'

    app = AppliesTo.objects.all().order_by('appliesto')
    cat = Category.objects.all().order_by('category')
    return render(request, 'pdref/newrec.html',{'app':app,'cat':cat,'message':message})

#------------------------------------------------------------------------------
@login_required
def fulldets(request, id, dir, dup, msg=''):
    """ Display the full details of the requested record. """

    # Check if we want the current record, or the next/previous one
    if '0' in request.session: fl = request.session['0']
    else: fl = {}
    query = ''
    if 'filter' in request.session:
        opts = request.session['filter']
        if opts[5] != '': query = misc.getQuery(opts[5])

    id = misc.pager(id, dir, fl, query)

    message = ''
    if request.method == 'POST':
        dup = 'none'
        # Store the amended values from the screen
        command = request.POST['command']
        example = request.POST['example']
        desc = request.POST['description']
        appliesto = request.POST.getlist('appliesto')[0]
        category = request.POST.getlist('category')[0]
        if 'inplace' in request.POST:
            inplace = True
        else:
            inplace = False

        # Update the PandasRef record from the updated details
        app = AppliesTo.objects.get(appliesto=appliesto)
        cat = Category.objects.get(category=category)
        PandasRef.objects.filter(id=id).update(command=command, example=example,
                    description=desc,appliesto=app,category=cat,inplace=inplace)
        message = 'Record details have been updated'

    dets = PandasRef.objects.get(id=id)
    t1 = str(dets.appliesto)
    app = AppliesTo.objects.all().order_by('appliesto')
    cat = Category.objects.all().order_by('category')
    if dup == 'dup':
        message = 'Duplicate created - amend and save changes'
        dets = PandasRef.objects.create(command=dets.command, example=dets.example,
                        description=dets.description, category_id=dets.category_id,
                        appliesto_id=dets.appliesto_id, inplace=dets.inplace)
    display = t1 != 'Other'
    if message == '' and msg != '':  message = msg
    return render(request, 'pdref/fulldets.html',{'dets':dets,'app':app,
                                                'cat':cat,'display':display,
                                                'message':message})

#------------------------------------------------------------------------------
@login_required
def pdfprint(request):
    """ Display some options for pdf printing. """

    if request.method == 'POST':
        filename = request.POST['filename']
        option = request.POST['option']

        return redirect('pdflist', doctype=option, filename=filename)

    if '0' in request.session: fl = request.session['0']
    else: fl = {}
    query = ''
    if 'filter' in request.session:
        opts = request.session['filter']
        if opts[5] != '': query = misc.getQuery(opts[5])

    if query == '':
        recs = PandasRef.objects.filter(**fl).count()
    else:
        recs = PandasRef.objects.filter(query, **fl).count()
    return render(request, 'pdref/print.html', {'recs':recs})

#------------------------------------------------------------------------------
def pdflist(request, doctype, filename):
    """ Output a pdf list of the selected pandas commands. If doctype='list'
        output brief details, otherwise output all available details.
        NB - Django does not have a Boolean type for url passthrough, so
        'footer' will be passed as a string ('True' or 'False').    """

    if not filename.endswith('.pdf'): filename += '.pdf'
    from django.conf import settings
    css = str(settings.BASE_DIR) + '/static/' + 'style.css'
    bootstrap = str(settings.BASE_DIR) + '/static/' + 'bootstrap.min.css'

    # Get the filter info, if exists.
    fl = {}
    query = ''
    if '0' in request.session: fl = request.session['0']
    if 'filter' in request.session:
        opts = request.session['filter']
        if opts[5] != '': query = misc.getQuery(opts[5])

    # Get the required recordset, which may be filtered or complete.
    if query == '':
        pds = PandasRef.objects.filter(**fl).order_by('category__category','command')
    else:
        pds = PandasRef.objects.filter(query, **fl).order_by('category__category','command')
    for rec in pds:
        rec.description = rec.description.replace('\n', '<br>')

    # Pass the recordset to the pdflist.html or pdfdets.html template.
    if doctype == 'list':
        html_string = render_to_string('pdref/pdflist.html', {'pds':pds})
    else:
        html_string = render_to_string('pdref/pdfdets.html', {'pds':pds})
    html = HTML(string=html_string)

    # Produce and download the pdf file.
    pdf = html.write_pdf(stylesheets=[CSS(css), CSS(bootstrap)])
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + filename
    return response

#------------------------------------------------------------------------------
@login_required
def delete(request, id):
    """ Delete the requested record, after confirmation.  """

    if request.method == 'POST':
        # The DELETE button has been clicked
        ret = PandasRef.objects.filter(id=id).delete()
        return redirect('fulldets', id, 'next', 'none', 'Requested record deleted')

    dets = PandasRef.objects.get(id=id)
    return render(request, 'pdref/delete.html', {'dets':dets})

#------------------------------------------------------------------------------