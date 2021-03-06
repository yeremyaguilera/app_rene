"""reneapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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

from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.views.i18n import JavaScriptCatalog


urlpatterns = [
    path(''                         , views.panel                   , name = 'panel'),
    path('gestion/'                 , views.tabla_clientes          , name = 'tabla_clientes'),
    path('detalle_oferta/'          , views.detalle_oferta          , name = 'detalle_oferta'),
    path('info_clientes/'           , views.info_clientes           , name = 'info_clientes'),
    path('jsi18n/'                  , JavaScriptCatalog.as_view()   , name = 'javascript-catalog'),
    path('actualizador_de_gestion/' , views.actualizador_de_gestion , name = 'actualizador_de_gestion'),
    path('asignador_de_cartera/'    , views.asignador_de_cartera    , name = 'asignador_de_cartera'),
    path('contrapartes/'            , views.contrapartes            , name = 'contrapartes'),
    path('distribucion_de_gestion/' , views.distribucion_de_gestion , name = 'distribucion_de_gestion'),
    path('consolidado_gestion/'     , views.consolidado_gestion     , name = 'consolidado_gestion'),
]