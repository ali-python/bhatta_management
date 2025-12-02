from product.forms import (
    ProductCategoryForm, ProductForm, StockInForm, StockOutForm
)
from product.models import (
    ProductCategory, Product, StockIn, StockOut
)
from django.views.generic import ListView, FormView, UpdateView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from customer.models import Customer

class AddProductCategory(FormView):
    form_class = ProductCategoryForm
    template_name = 'product/add_category.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            AddProductCategory, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('product:add'))

    def form_invalid(self, form):
        return super(AddProductCategory, self).form_invalid(form)


class AddProduct(FormView):
    form_class = ProductForm
    template_name = 'product/add_product.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            AddProduct, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('product:list'))

    def form_invalid(self, form):
        return super(AddProduct, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(AddProduct, self).get_context_data(**kwargs)
        category = ProductCategory.objects.all()
        context.update({
            'category': category
        })
        return context


class UpdateProduct(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'product/update_product.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            UpdateProduct, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(reverse('product:list'))

    def form_invalid(self, form):
        return super(UpdateProduct, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(UpdateProduct, self).get_context_data(**kwargs)
        categories = ProductCategory.objects.all()
        context.update({
            'categories': categories
        })
        return context


class ProductList(ListView):
    model = Product
    template_name = 'product/product_list.html'
    paginate_by = 100
    ordering = '-id'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            ProductList, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        queryset = self.queryset
        if not queryset:
            queryset = Product.objects.all().order_by('-id')

        if self.request.GET.get('product_name'):
            queryset = queryset.filter(
                name__contains=self.request.GET.get('product_name')
            )

        if self.request.GET.get('product_category'):
            queryset = queryset.filter(
                category__category__contains=self.request.GET.get('product_category')
            )

        return queryset.order_by('-id')


class StockInProduct(FormView):
    form_class = StockInForm
    template_name = 'product/add_stock_item.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            StockInProduct, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        obj = form.save()
        return HttpResponseRedirect(reverse('product:stockin_detail',
                                            kwargs={'pk': obj.product.id}))

    def form_invalid(self, form):
        return super(StockInProduct, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(StockInProduct, self).get_context_data(**kwargs)
        try:
            product = (
                Product.objects.get(id=self.kwargs.get('pk'))
            )
        except ObjectDoesNotExist:
            raise Http404('Product not found')
        context.update({
            'product': product
        })
        return context


class StockOutProduct(FormView):
    form_class = StockOutForm
    template_name = 'product/stock_out_item.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            StockOutProduct, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        obj = form.save()
        return HttpResponseRedirect(reverse('product:stockout_detail',
                                            kwargs={'pk': obj.product.id}))

    def form_invalid(self, form):
        return super(StockOutProduct, self).form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(StockOutProduct, self).get_context_data(**kwargs)

        try:
            product = (
                Product.objects.get(id=self.kwargs.get('pk'))
            )
        except ObjectDoesNotExist:
            raise Http404('Product not found')

        context.update({
            'product': product
        })
        return context


class StockInDetail(ListView):
    template_name = 'product/stockin_detail.html'
    paginate_by = 100
    model = StockIn

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            StockInDetail, self).dispatch(request, *args, **kwargs)

    def get_queryset(self, **kwargs):

        queryset = self.queryset

        if not queryset:
            queryset = self.model.objects.filter(
                product__id=self.kwargs.get('pk'))

        if self.request.GET.get('date'):
            queryset = queryset.filter(
                dated_order__icontains=self.request.GET.get('date')
            )

        return queryset.order_by('-id')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(
            StockInDetail, self).get_context_data(**kwargs)

        try:
            product = Product.objects.get(id=self.kwargs.get('pk'))
        except Product.DoesNotExist:
            raise Http404('Product does not exits!')

        context.update({
            'product': product
        })
        return context


class StockOutDetail(ListView):
    template_name = 'product/stockout_detail.html'
    paginate_by = 100
    model = StockOut

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('common:login'))

        return super(
            StockOutDetail, self).dispatch(request, *args, **kwargs)

    def get_queryset(self, **kwargs):

        queryset = self.queryset

        if not queryset:
            queryset = self.model.objects.filter(
                product__id=self.kwargs.get('pk')).order_by('-date')

        if self.request.GET.get('date'):
            queryset = queryset.filter(
                date__icontains=self.request.GET.get('date')
            )

        return queryset.order_by('-id')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(
            StockOutDetail, self).get_context_data(**kwargs)

        try:
            product = Product.objects.get(id=self.kwargs.get('pk'))
        except Product.DoesNotExist:
            raise Http404('Product does not exits!')

        context.update({
            'product': product
        })
        return context
