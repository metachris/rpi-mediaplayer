# -*- coding: utf-8 -*-
# # Create your views here.

from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from django.shortcuts import render_to_response, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib import auth
from django.core.urlresolvers import reverse_lazy

#from forms import OwnerForm, HeaterForm
#from models import Contact, Heater


class LogoutView(View):
    def get(self, request):
        auth.logout(request)
        return HttpResponseRedirect("/")

#
## ======
## Owners
## ======
#class OwnerList(ListView):
#    model = Contact
#
#
#class OwnerDetail(DetailView):
#    model = Contact
#
#
#class OwnerCreate(CreateView):
#    form_class = OwnerForm
#    model = Contact
#
#    def form_valid(self, form):
#        form.instance.created_by = self.request.user
#        return super(OwnerCreate, self).form_valid(form)
#
#
#class OwnerUpdate(UpdateView):
#    template_name = "main/owner_edit.html"
#    model = Contact
#
#
#class OwnerDelete(DeleteView):
#    model = Contact
#    success_url = reverse_lazy('owner_list')
#
#
## ==========
## Heizkörper
## ==========
#def heater_list(request):
#    heater_all_list = Heater.objects.all()
#    paginator = Paginator(heater_all_list, 25)
#
#    page = request.GET.get('page')
#    try:
#        heaters = paginator.page(page)
#    except PageNotAnInteger:
#        # If page is not an integer, deliver first page.
#        heaters = paginator.page(1)
#    except EmptyPage:
#        # If page is out of range (e.g. 9999), deliver last page of results.
#        heaters = paginator.page(paginator.num_pages)
#    return render(request, 'heater/heater_list.html', {"heaters": heaters})
#
#
#class HeaterDetail(DetailView):
#    model = Heater
#    template_name = "heater/heater_detail.html"
#
#
#class HeaterCreate(CreateView):
#    form_class = HeaterForm
#    model = Heater
#    template_name = "heater/heater_form.html"
#
#    def form_valid(self, form):
#        form.instance.created_by = self.request.user
#        return super(HeaterCreate, self).form_valid(form)
#
#
#class HeaterUpdate(UpdateView):
#    template_name = "heater/heater_edit.html"
#    model = Heater
#
#
#class HeaterDelete(DeleteView):
#    model = Heater
#    success_url = reverse_lazy('heater_list')
#    template_name = "heater/heater_confirm_delete.html"
#
