from django.urls import path
# from app1.views import data,index,productall,productfilter,login,productget
from app1.views import *
urlpatterns = [
    path('data/',data),
    path('',index,name="index1"),
    path('product-all/',productall,name="allproduct"),
    path('product-filter/<int:id>/',productfilter),
    path('product-get/<int:id>/',productget,name="productdetails"),
    path('register/',register),
    path('login/',login,name="login"),
    path('logout/',logout,name="logout"),
    path('profile',profile,name="profile1"),
    path('buynow/',buynow,name="buy"),
    path('ordertable/',ordertable,name="myorder"),
    path('razorpayView/',razorpayView,name='razorpayView'),
    path('paymenthandler/',paymenthandler,name='paymenthandler'),
    path('successview/',ordersucess,name="orderSuccessView"),
    path('vendor-Register/',vendorregister,name="vendor_register"),
    path('vendor-Login/',vendorlogin,name="vendorlogin1"),
    path('vendor-Logout/',vendorlogout,name='vendorlogout2'),
    path('Add-Product/',addproduct,name="addproduct1"),
    path('add-Cart/',addcart,name="addcart12"),
    path('cart/',cart,name="cart123"),
    path('item-remove/<int:id>/',removeitem,name="removeitem123"),
    path('removeallitem/',removeallitem,name="removeallitem"),
    path('shiping/',shiping,name="shiping"),
    path('vendor-order/',vendororder,name="vendor_order")
]