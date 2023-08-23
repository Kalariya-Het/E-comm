from django.shortcuts import render,redirect
from django.http import HttpResponse
from app1.models import *
# Create your views here.

def data(request):
    return HttpResponse("<h1>This is my first webpage</h1>")


def index(request):
    a=Category.objects.all()
    return render(request,"index.html",{'data':a})

def productall(request):
    a=Product.objects.all()
    return render(request,"product.html",{'data':a})

def productfilter(request,id):
    a=Product.objects.filter(Category=id)
    return render(request,"product.html",{'data':a})

def productget(request,id):
    if 'm' in request.session:
        m=request.session['m']
        del request.session['m']
    else:
        m=""
    a=Product.objects.get(id=id)
    return render(request,'product_details.html',{'data':a,'m':m})


def register(request):
    if request.method=="POST":
        name1=request.POST['name']
        email1=request.POST['email']
        number1=request.POST['number']
        address1=request.POST['address']
        password1=request.POST['password']
        user=Userregister(name=name1,email=email1,number=number1,address=address1,password=password1)
        data=Userregister.objects.filter(email=email1)
        if  len(data)==0:
            user.save()
            return redirect('login')
        else:
            return render(request,"register.html",{'m':'user alredy exist'})
    return render(request,"register.html")

def login(request):
    if request.method=="POST":
        email1=request.POST['email']
        password1=request.POST['password']
        try:
            user=Userregister.objects.get(email=email1,password=password1)
            if user:
                request.session['email']=user.email
                request.session['id']=user.pk
                return redirect('index1')
            else:
                return render(request,"login.html",{'m':'invalid data enter'})
        except:
            return render(request,"login.html",{'m':'invalid data enter'})
    return render(request,"login.html")

def logout(request):
    if 'email' in request.session:
        del request.session['email']
        del request.session['id']
        return redirect('login')
    else:
        return redirect('login')
    

def profile(request):
    if 'email' in request.session:
        user=Userregister.objects.get(email=request.session['email'])
        if request.method=="POST":
            name1=request.POST['name']
            number1=request.POST['number']
            address1=request.POST['address']
            oldpasss=request.POST['oldpassword']
            newpass=request.POST['newpassword']
            user.name=name1
            user.number=number1
            user.address=address1 
            if oldpasss=="" and newpass=="":
                user.save()
                return render(request,'profile.html',{'user':user,'m':'Profile Updated..'})
            if user.password==oldpasss:
                user.password=newpass
                user.save()
                return render(request,'profile.html',{'user':user,'m':'Profile Updated..'})
            else:
                return render(request,'profile.html',{'user':user,'m':'invalid old password..'})
        return render(request,'profile.html',{'user':user})
    else:
        return redirect('login')


def ordertable(request):
    if 'email' in request.session:
        orderdata=Order.objects.filter(userid=request.session['id'])
        productlist=[]
        for i in orderdata:
            print(i.productid)
            productdict={}
            if i.productid !="0":
                productdata=Product.objects.get(id=int(i.productid))
                productdict['image']=productdata.image
                productdict['name']=productdata.name
                productdict['quantity']=i.quantity
                productdict['price']=i.price
                productdict['date']=i.datetime
                productdict['transactionid']=i.transactionid
                productlist.append(productdict)
            elif i.productid=="0":
                cartdata=Cart.objects.filter(orderid=str(i.pk))
                print(cartdata)
                for j in cartdata:
                    productdict={}
                    productdata=Product.objects.get(id=j.productid)
                    productdict['image']=productdata.image
                    productdict['name']=productdata.name
                    productdict['quantity']=j.quantity
                    productdict['price']=j.totalprice
                    productdict['date']=i.datetime
                    productdict['transactionid']=i.transactionid 
                    productlist.append(productdict)
            
        return render(request,'ordertable.html',{'productlist':productlist})
    else:
        return redirect('login')

def ordersucess(request):
    if 'email' in request.session:
        return render(request,'order_sucess.html')
    else:
        return redirect('login')


import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest

def buynow(request):
    if 'email' in request.session:
        if request.method=="POST":
            request.session['productid']=request.POST['productid']
            productdata=Product.objects.get(id=request.POST['productid'])
            request.session['quantity']="1"
            request.session['price']=str(int(request.session['quantity'])*productdata.price)
            request.session['paymentmethod']="Razorpay"
            
            data=Cart()
            data.orderid="0"
            data.userid=request.session['id']
            data.productid=request.POST['productid']
            x=request.POST['productid']
            a=Product.objects.get(id=request.POST['productid'])
            data.vendorid=a.vendorid
            data.quantity="1"
            data.productprice=a.price
            data.totalprice=a.price*int(data.quantity)

            data.save()
            return redirect('razorpayView')  
    else:
        return redirect('login')



RAZOR_KEY_ID = 'rzp_test_D2CSJ2vNEiyjL7'
RAZOR_KEY_SECRET = '0j3Gr9p35rAGYRVz4pBFYBG4'
client = razorpay.Client(auth=(RAZOR_KEY_ID, RAZOR_KEY_SECRET))

def razorpayView(request):
    currency = 'INR'
    amount = int(request.session['price'])*100
    # Create a Razorpay Order
    razorpay_order = client.order.create(dict(amount=amount,currency=currency,payment_capture='0'))
    # order id of newly created order.
    razorpay_order_id = razorpay_order['id']
    callback_url = 'http://127.0.0.1:8000/paymenthandler/'    
    # we need to pass these details to frontend.
    context = {}
    context['razorpay_order_id'] = razorpay_order_id
    context['razorpay_merchant_key'] = RAZOR_KEY_ID
    context['razorpay_amount'] = amount
    context['currency'] = currency
    context['callback_url'] = callback_url    
    return render(request,'razorpayDemo.html',context=context)

@csrf_exempt
def paymenthandler(request):
    # only accept POST request.
    if request.method == "POST":
        try:
            # get the required parameters from post request.
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
 
            # verify the payment signature.
            result = client.utility.verify_payment_signature(
                params_dict)
            
            amount = int(request.session['price'])*100  # Rs. 200
            # capture the payemt
            client.payment.capture(payment_id, amount)

            #Order Save Code
            orderModel = Order()
            orderModel.userid=request.session['id']
            if 'name' in request.session:
                print(5555)
                orderModel.name=request.session['name']
                orderModel.email=request.session['email']
                orderModel.number=request.session['number']
                orderModel.address=request.session['address']
                orderModel.price = request.session['price']
                orderModel.paymentmethod = request.session['paymentmethod']
                orderModel.transactionid = payment_id
                print(5555)
                orderModel.productid="0"
                print(5555)
                orderModel.save()
                orderdata=Order.objects.latest('id')
                data=Cart.objects.filter(userid=request.session['id']) and Cart.objects.filter(orderid="0")
                for i in data:
                    productdata=Product.objects.get(id=i.productid)
                    productdata.quantity-=int(i.quantity)
                    i.orderid=orderdata.pk
                    i.save()
                    productdata.save()
                del request.session['name']
                del request.session['number']
                del request.session['address']
                del request.session['price']
                del request.session['paymentmethod']
            
                return redirect('orderSuccessView')
            else:
                userdata=Userregister.objects.get(id=request.session['id'])
                orderModel.name=userdata.name
                orderModel.email=userdata.email
                orderModel.number=userdata.number
                orderModel.address=userdata.address
                print(111)
                orderModel.productid=request.session['productid']
                print(2)
                orderModel.quantity=request.session['quantity']
                print(3)
                orderModel.price = request.session['price']
                print(4)
                orderModel.paymentmethod = "Razorpay"
                print('s')
                orderModel.transactionid = payment_id
                productdata=Product.objects.get(id=request.session['productid'])
                productdata.quantity=productdata.quantity-int(request.session['quantity'])
                productdata.save()
                orderModel.save()
                cartdata=Cart.objects.latest('id')
                orderdata=Order.objects.latest('id')
                cartdata.orderid=orderdata.pk
                cartdata.save()
                print(111)
                
                del request.session['productid']
                del request.session['quantity']
                del request.session['price']
                del request.session['paymentmethod']
                
            
                return redirect('orderSuccessView')
        except:
            print("Hello")
            # if we don't find the required parameters in POST data
            return HttpResponseBadRequest()
    else:
        print("Hello1")
       # if other than POST request is made.
        return HttpResponseBadRequest()

def vendorregister(request):
    if request.method=="POST":
        name1=request.POST['name']
        email1=request.POST['email']
        number1=request.POST['number']
        address1=request.POST['address']
        password1=request.POST['password']
        user=Vendorregister(name=name1,email=email1,number=number1,address=address1,password=password1)
        data=Vendorregister.objects.filter(email=email1)
        if  len(data)==0:
            user.save()
            return redirect('vendorlogin1')
        else:
            return render(request,"register.html",{'m':'user alredy exist'})
    return render(request,"register.html")

def vendorlogin(request):
    if request.method=="POST":
        email1=request.POST['email']
        password1=request.POST['password']
        try:
            user=Vendorregister.objects.get(email=email1,password=password1)
            if user:
                request.session['vendoremail']=user.email
                request.session['vendorid']=user.pk
                return redirect('index1')
            else:
                return render(request,"login.html",{'m':'invalid data enter'})
        except:
            return render(request,"login.html",{'m':'invalid data enter'})
    return render(request,"login.html")

def vendorlogout(request):
    if 'vendoremail' in request.session:
        del request.session['vendoremail']
        del request.session['vendorid']
        return redirect('vendorlogin1')
    else:
        return redirect('vendorlogin1')
    
def addproduct(request):
    if 'vendoremail' in request.session:
        a=Category.objects.all()
        if request.method=="POST" and request.FILES:
            pro=Product()
            pro.vendorid=request.session['vendorid']
            pro.name=request.POST['name']
            pro.price=request.POST['price']
            pro.quantity=request.POST['quantity']
            pro.discription=request.POST['desc']
            pro.image=request.FILES['img']
            cat=Category.objects.get(id=request.POST['category'])
            pro.Category=cat
            pro.save()
        return render(request,'addproduct.html',{'data':a})
    else:
        return redirect('vendorlogin1')
    
def addcart(request):
    if 'email' in request.session:
        if request.POST:
            try:
                data=Cart()
                data.orderid="0"
                data.userid=request.session['id']
                data.productid=request.POST['productid']
                x=request.POST['productid']
                a=Product.objects.get(id=request.POST['productid'])
                data.vendorid=a.vendorid
                data.quantity=request.POST['quantity']
                data.productprice=a.price
                data.totalprice=a.price*int(data.quantity)
                s=Cart.objects.filter(productid=x) & Cart.objects.filter(orderid="0")
                print(len(s))
                if len(s)==0:
                    data.save()
                    request.session['m']="product added into Cart"
                    return redirect('productdetails',x)
                else:
                    request.session['m']="product already into Cart"
                    return redirect('productdetails',x)
            except:
                request.session['m']="type valid quantity"
                return redirect('productdetails',x)
    else:
        return redirect('login')
    
def cart(request):
    if 'email' in request.session:
        data=Cart.objects.filter(userid=request.session['id']) and Cart.objects.filter(orderid="0")
        p=[]
        final=0
        for i in data:
            final+=int(i.totalprice)
            pro={}
            prodata=Product.objects.get(id=i.productid)
            pro['name']=prodata.name
            pro['id']=i.pk
            pro['img']=prodata.image
            pro['price']=i.productprice
            pro["quantity"]=i.quantity
            pro['totalprice']=i.totalprice
            p.append(pro)
        return render(request,'cart.html',{"productlist":p,'no':len(p),'final':final})
    else:
        return redirect('login')

def removeitem(request,id):
    if 'email' in request.session:
        item=Cart.objects.get(id=id)
        item.delete()
        return redirect('cart123')
    else:
        return redirect('login')
    
def removeallitem(request):
    if 'email' in request.session:
        item=Cart.objects.filter(userid=request.session['id']) and Cart.objects.filter(orderid="0")
        item.delete()
        return redirect('cart123')
    else:
        return redirect('login')
    


def shiping(request):
    if 'email' in request.session:
        userdata=Userregister.objects.get(id=request.session['id'])
        data=Cart.objects.filter(userid=request.session['id']) and Cart.objects.filter(orderid="0")
        p=[]
        final=0
        for i in data:
            final+=int(i.totalprice)
        if request.method=="POST":
            request.session['name']=request.POST['name']
            request.session['email']=request.POST['email']
            request.session['address']=request.POST['address']
            request.session['number']=request.POST['number']
            request.session['price']=final
            request.session['paymentmethod']="Razorpay"
            return redirect('razorpayView') 
        return render(request,'shiping.html',{'final':final,'userdata':userdata})
    else:
        return redirect('login')
    

def vendororder(request):
    if 'vendoremail' in request.session: 
        orderdata=Order.objects.all()
        productlist=[]
        for i in orderdata:
            print(i.productid)
            productdict={}
            if i.productid !="0":
                productdata=Product.objects.get(id=int(i.productid),vendorid=request.session['vendorid'])
                productdict['image']=productdata.image
                productdict['name']=productdata.name
                productdict['quantity']=i.quantity
                productdict['price']=i.price
                productdict['date']=i.datetime
                productdict['transactionid']=i.transactionid
                productdict['buyer']=Userregister.objects.get(id=i.userid).name
                productlist.append(productdict)
            elif i.productid=="0":
                cartdata=Cart.objects.filter(orderid=str(i.pk))
                print(cartdata)
                for j in cartdata:
                    productdict={}
                    productdata=Product.objects.get(id=j.productid,vendorid=request.session['vendorid'])
                    productdict['image']=productdata.image
                    productdict['name']=productdata.name
                    productdict['quantity']=j.quantity
                    productdict['price']=j.totalprice
                    productdict['date']=i.datetime
                    productdict['transactionid']=i.transactionid 
                    productdict['buyer']=Userregister.objects.get(id=i.userid).name
                    productlist.append(productdict)
            
        return render(request,'ordertable.html',{'productlist':productlist})