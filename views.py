# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Product, Category, Basket, BasketItem
import csv
import uuid
import decimal
import json
from .forms import UploadFileForm
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
@staff_member_required
def import_products(request):
    form = UploadFileForm(request.POST, request.FILES)
    nl = 0
    if form.is_valid(): # а куда она денется
        f = request.FILES['file']
        first = True
        reader = csv.reader(f)
        for row in reader:
            if not first:
                oid = row[0]
                article = row[1]
                shortname = row[2]
                name = row[3]
                active = row[4]
                baseprice = row[5]
                description = row[6]
                properties = row[7]

                if oid != '':
                    oid = uuid.UUID(oid, version=4)
                    try:
                        product = Product.objects.get(pk=oid)
                    except Product.DoesNotExist:
                        product = Product()
                else:
                    product = Product()
                product.article = article
                product.shortname = shortname
                product.name = name
                if active in ('1', 'True'):
                    product.active = True
                else:
                    product.active = False
                product.baseprice = decimal.Decimal(baseprice)
                if description != '':
                    product.description = description
                if properties != '':
                    try:
                        obj = json.loads(properties)
                        product.properties = properties
                    except ValueError:
                        pass # bad json
                product.save()
                nl += 1
            first = False
    return HttpResponse("Ok {} products".format(nl))


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
    response['Content-Disposition'] = 'attachment; filename="products.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'id',
        'article',
        'shortname',
        'name',
        'active',
        'baseprice',
        'description',
        'properties',
        ])
    for obj in Product.objects.all():
        writer.writerow([
            as_s(obj.id),
            as_s(obj.article),
            as_s(obj.shortname),
            as_s(obj.name),
            as_s(obj.active),
            as_s(obj.baseprice),
            as_s(obj.description),
            as_s(obj.properties)
            ])
    return response

@login_required
@staff_member_required
def export_categorys(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="categorys.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'id',
        'shortname',
        'name',
        'description',
        'active',
        'properties',
        ])
    for obj in Category.objects.all():
        writer.writerow([
            as_s(obj.id),
            as_s(obj.shortname),
            as_s(obj.name),
            as_s(obj.description),
            as_s(obj.active),
            as_s(obj.properties)
            ])
    return response

@login_required
@staff_member_required
def export_baskets(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="categorys.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'user id',
        'user name',
        'user phone',
        'user email',
        'created',
        'posted',
        'modified',
        'state',
        'shortname',
        'cnt',
        'price',
        ])    
    for basket in Basket.objects.filter(state=1):
        for item in basket.basketitem_set.all():        
         writer.writerow([
            as_s(basket.user_id),
            as_s(basket.user_name),
            as_s(basket.user_phone),
            as_s(basket.user_email),
            as_s(basket.created),
            as_s(basket.posted),
            as_s(basket.modified),
            as_s(basket.state),
            as_s(item.shortname),
            as_s(item.cnt),
            as_s(item.price)
            ])
    return response

def get_basket(request):
    bid = request.session.get('bid', None)
    if bid is None:
        basket = Basket()
        basket.save()
        bid = basket.id
    else:
        try:
            bid = uuid.UUID(bid, version=4)
            basket = Basket.objects.get(pk=bid)
        except ValueError, Basket.DoesNotExist:
            basket = Basket()
            basket.save()
            bid = basket.id

    if basket.state != 0:
        # Если корзина уже обработана, то пользователю с ней работать НЕЛЬЗЯ
        basket = Basket()
        basket.save()
        bid = basket.id

    request.session['bid'] = str(bid)
    return basket


def add_to_basket(request):
    basket = get_basket(request)
    if request.method == 'GET':
        data = request.GET
    elif request.method == 'POST':
        data = request.POST

    oid = data['oid']
    oid = uuid.UUID(oid, version=4)

    cnt = data['count']
    if '.' in cnt:
        cnt = decimal.Decimal(cnt)
    else:
        cnt = int(cnt)
    price_item = Product.objects.get(pk=oid)
    Basket.basketitem_set.create(
        article=price_item.article,
        shortname=price_item.shortname,
        cnt=cnt,
        price=price_item.baseprice   # TODO если будут несколько цен это надо обработать
        )
    return HttpResponse("Ok")


def del_from_basket(request):
    if request.method == 'GET':
        data = request.GET
    elif request.method == 'POST':
        data = request.POST
    oid = data['oid']
    oid = uuid.UUID(oid, version=4)
    basket_item = BasketItem.objects.get(pk=oid)
    if basket_item.basket_ref.state == 0:
        basket_item.delete()
    return HttpResponse("Ok")

def detail_basket (request):
    return HttpResponse("Ok detail")


def categoryes(request):
    category_list = Category.objects.all()
    cat_id = category_list[0].id
    if 'cat_id' in request.GET:
        cat_id = uuid.UUID(request.GET['cat_id'], version=4)
    product_list = Product.objects.filter(categories=cat_id)
    paginator = Paginator(product_list, 5) 
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products= paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    
    return render (request, 'catalog.html', 
                             {'category_list': category_list, 
                              'cat_id': cat_id, 
                              'products': products, 
                              'paginator': paginator
                              })
