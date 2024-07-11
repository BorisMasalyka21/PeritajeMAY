from django.urls import path
from .views import CombinedView, imagen_auto,borrar_marcas, borrar_marca, guardar_imagen, home, registrar_usuario, ver_peritaje,imprimir,custom_logout,CustomUserCreateView, ver_auto, editar_peritaje, reporte, excel
from .forms import CustomUserCreationForm, CustomAuthenticationForm 
from django.views.generic.edit import CreateView
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('register/', CustomUserCreateView.as_view(), name='register'),
    path('', LoginView.as_view(template_name='login.html', authentication_form=CustomAuthenticationForm, success_url='/home/'), name='login'),
    path('logout/', custom_logout, name='logout'),
    path('home/', home, name='home'),
    #path('peritaje/<int:coche_id>/<int:equip_id>/', CombinedView.as_view(), name='peritaje_form'),
    path('peritaje/', CombinedView.as_view(), name='peritaje_form_empty') ,
    path('registrar_usuario/', registrar_usuario, name='registrar_usuario'),
    path('imagen_auto/<int:peritaje_id>/', imagen_auto, name='imagen_auto'),
    path('borrar_marcas/', borrar_marcas, name='borrar_marcas'),
    path('borrar_marca/<int:marca_id>/', borrar_marca, name='borrar_marca'),
    path('guardar_imagen/<int:peritaje_id>/', guardar_imagen, name='guardar_imagen'),
    path('ver_peritaje/<int:peritaje_id>/', ver_peritaje, name='ver_peritaje'),
    path('imprimir/', imprimir, name='imprimir'),
    path('imprimir/<int:peritaje_id>/', imprimir, name='imprimir'),
    path('ver_auto/<int:peritaje_id>/', ver_auto, name='ver_auto'),
    path('editar_peritaje/<int:peritaje_id>/', editar_peritaje, name='editar_peritaje'),
    path('reporte/', reporte, name='reporte'),
    path('excel/', excel, name='excel'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)