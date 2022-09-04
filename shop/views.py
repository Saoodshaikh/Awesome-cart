from django.shortcuts import render
from .models import Product, Contact, Orders, OrderUpdate
from  django.http import HttpResponse
from math import ceil, prod
import json
from django.views.decorators.csrf import csrf_exempt
from .PayTm import  Checksum
MERCHANT_KEY='QNFrblpyjDdG@8gp'

# Create your views here.
def index(request):
    # products = Product.objects.all()
    # print(products)
    
    
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod = Product.objects.filter(category = cat)
        n=len(prod)
        nSlides = n//4 + ceil((n/4)-(n//4)) 
        allprods.append([prod, range(1, nSlides), nSlides])
       
          
    #params = {'no of slides':nSlides, 'range': range(1,nSlides), 'product': products}
    # allprods= [[products, range(1, nSlides), nSlides],
    #           [products, range(1, nSlides), nSlides]]
    params = {'allprods':allprods}
    return render(request, 'shop/index.html', params)

def searchMatch(query, item):
    ''' return True if query matches the item '''
    if query in item.desc.lower() or query in item.product_name.lower() or query in item.category.lower():
        return True
    return False

def search(request):
    query = request.GET.get('search')
    allprods = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp = Product.objects.filter(category = cat)
        prod= [item for item in prodtemp if searchMatch(query, item)]
        n=len(prod)
        nSlides = n//4 + ceil((n/4)-(n//4)) 
        if len(prod) !=0:
           allprods.append([prod, range(1, nSlides), nSlides])
    params = {'allprods':allprods, "msg":""}
    if len(allprods)==0 or len(query)<4:
        params = {'msg':"please make sure to enter relevent search query"}
    return render(request, 'shop/.html', params)
     

def about(request): 
    return render(request, 'shop/about.html')

def contact(request):
     thank = False
     if request.method=='POST':
          name = request.POST.get('name','')
          phone = request.POST.get('phone','')
          email = request.POST.get('email','')
          desc = request.POST.get('desc','')
          print(name, phone, email, desc)
          contact= Contact(name=name, phone=phone, email=email, desc=desc)
          contact.save()
          thank = True
     return render(request, 'shop/contact.html', {'thank': thank})
   


def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')

    return render(request, 'shop/tracker.html')
   



def productView(request, myid):
     # fetch the product using the id
     product = Product.objects.filter(id=myid)
     print(product)
     return render(request, 'shop/prodView.html', {'product':product[0]})


     
def checkout(request):
     if request.method=='POST':
          items_json = request.POST.get('itemsJson','')
          name = request.POST.get('name','')
          amount = request.POST.get('amount','')
          email = request.POST.get('email','')
          address = request.POST.get('address','') + " " + request.POST.get('address2','')
          city = request.POST.get('city','')
          state = request.POST.get('state','')
          zip_code = request.POST.get('zip_code','')
          phone = request.POST.get('phone','')
          order= Orders(items_json=items_json, name=name, email=email, address=address, city=city, state=state, zip_code=zip_code, phone=phone, amount=amount)
          order.save()
          update = OrderUpdate(order_id=order.order_id, update_desc=" The order has been placed")
          update.save()
          thank =True
          id = order.order_id
     # return render(request, 'shop/checkout.html', {'thank':thank, 'id': id})
    #request paytm to transfer the amount to your account after payment by user
          param_dict={

                'MID': 'DGjsIa88874455691234',
                'ORDER_ID': str('order.order_id'),
                'TXN_AMOUNT': '1',
                'CUST_ID': 'email',
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/shop/handlerequest/',

          }
          param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)
          return  render(request, 'shop/paytm.html', {'param_dict': param_dict})
     return render(request, 'shop/checkout.html')
          #return render(request, 'shop/checkout.html', {'thank':thank, 'id':id})
          # Request paytm to transfer the amount to your account afterb payment by user
    
 
@csrf_exempt
def handlerequest(request):
    # pqytm wlll send post request
     # paytm will send you post request here
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})
     
    