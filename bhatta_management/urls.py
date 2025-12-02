"""
URL configuration for bhatta_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('common.urls', 'common'), namespace='common')),
    path('employee/', include(('employee.urls', 'employee'), namespace='employee')),
    path('brickout/', include(('bricks_out.urls', 'bricks_out'), namespace='bricks_out')),
    path('payment/', include(('payment.urls', 'payment'), namespace='payment')),
    path('product/', include(('product.urls', 'product'), namespace='product')),
    path('tractor/', include(('tractor_account.urls', 'tractor'), namespace='tractor')),
    path('hourly/', include(('hourly_employee_account.urls', 'hourly'), namespace='hourly')),
    path('raw-brick-employee/', include(('raw_bricks_employee.urls', 'raw_bricks_employee'), namespace='raw_bricks_employee')),
    path('kachi/ent/bharai/', include(('kachi_ent_bharai.urls', 'kachi_ent_bharai'), namespace='kachi_ent_bharai')),
    path('worker/', include(('worker.urls', 'worker'), namespace='worker')),
    path('expense/', include(('expense.urls', 'expense'), namespace='expense')),
    path('wood-scrapper/', include(('wood_scrapper.urls', 'wood_scrapper'), namespace='wood_scrapper')),
]


urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
