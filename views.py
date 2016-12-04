# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Product
import csv

def as_s(o):
    if isinstance(o, unicode):
        return o.encode('utf-8')
    if o is None:
        return ''
    return str(o)


@login_required
@staff_member_required
def export_products(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'id',
        'article',
        'shortname',
        'name',
        'active',
        'baseprice',
        'description'
        ])
    for obj in Product.objects.all():
        writer.writerow([
            as_s(obj.id),
            as_s(obj.article),
            as_s(obj.shortname),
            as_s(obj.name),
            as_s(obj.active),
            as_s(obj.baseprice),
            as_s(obj.description)
            ])
    return response
