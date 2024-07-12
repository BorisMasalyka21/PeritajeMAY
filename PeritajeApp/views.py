from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from .forms import CochePeritajeForm, EquipamientoForm, FotoPeritajeForm,InspeccionCubiertasForm, ClientePeritarForm, InspeccionGralForm, CustomUserCreationForm, Gastos_totalForm, BranchForm, UnidadForm 
from .models import FotoPeritaje, ClientePeritar, Marca, Peritaje, ImagenMarcada, CustomUser, CreadoPor, CochePeritaje, Equipamiento, InspeccionCubiertas,InspeccionGral, Gastos_total, Branch, Unidad_negocio, Cambios
from django.http import JsonResponse
from PIL import Image
from django.core.mail import send_mail
import uuid
from django.contrib.auth import logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
import os
from django.conf import settings
import random
import string
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from decimal import InvalidOperation, Decimal
from django.http import HttpResponseNotAllowed
from django.utils import timezone
from django.http import HttpResponse
from openpyxl import Workbook
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from datetime import datetime



# COMPRESOR
def compress_and_save_image(image):
    # Abrir la imagen usando Pillow
    img = Image.open(image)

    # Convertir la imagen al modo RGB si no es RGB
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # Crear un objeto BytesIO para guardar la imagen comprimida
    im_io = BytesIO()

    # Comprimir la imagen y guardarla en el objeto BytesIO
    img_format = 'JPEG'  # Default format
    extension = os.path.splitext(image.name)[1].lower()
    if extension == '.png':
        img_format = 'PNG'
    elif extension == '.gif':
        img_format = 'GIF'

    img.save(im_io, format=img_format, quality=60)  # Puedes ajustar la calidad según sea necesario

    # Crear un nombre de archivo único
    filename = os.path.join('peritaje_fotos', image.name)

    # Guardar la imagen comprimida en el directorio media/peritaje_fotos
    image_path = os.path.join(settings.MEDIA_ROOT, filename)
    with open(image_path, 'wb') as f:
        f.write(im_io.getvalue())

    return filename


# CERRAR SESION
def custom_logout(request):
    logout(request)
    messages.success(request, "Has cerrado sesión exitosamente.")
    return redirect('login')



def formatear_numero(numero):
    try:
        return "{:,.2f}".format(numero).replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return numero
    
    
# COMBINED VIEW
    
class CombinedView(LoginRequiredMixin, View):
    template_name = 'coche_peritaje_form.html'

    def get(self, request):
        context = self._get_initial_context(request)
        return render(request, self.template_name, context)

    def post(self, request):
        post_data = request.POST.copy()
        file_data = request.FILES.getlist('fotos')
        
        if 'ultimo_cambio_distribucion_fecha' in post_data and post_data['ultimo_cambio_distribucion_fecha']:
            post_data['ultimo_cambio_distribucion_fecha'] += '-01'
        
        # Valores correspondientes a los campos _entrega y _duenio
        entrega_to_duenio_mapping = {
            'nombre_apellido_entrega': 'nombre_apellido_duenio',
            'telefono_entrega': 'telefono_duenio',
            'email_entrega': 'email_duenio',
            'cuil_entrega': 'cuil_duenio',
        }
        
        # Asignar valores de _entrega a _duenio si están vacíos
        for entrega_field, duenio_field in entrega_to_duenio_mapping.items():
            if not post_data.get(duenio_field):
                post_data[duenio_field] = post_data.get(entrega_field, '')
        
        for field_name in post_data:
            if field_name.startswith('gastos_') or field_name.endswith('_gasto') or field_name == 'total_gastos' or field_name == 'valor_mercado' or field_name == 'precio_info_auto' or field_name == 'precio_valor_toma':
                field_value = post_data[field_name]
                if field_value:
                    # Eliminar el signo $
                    field_value_str = field_value.replace('$', '').replace('.', '').replace(',', '.')
                    try:
                        post_data[field_name] = str(Decimal(field_value_str))
                    except InvalidOperation:
                        post_data[field_name] = '0'
                    
        usuario = request.user
        es_gerente = usuario.groups.filter(name='Gerente').exists()
        
        if not es_gerente:
            post_data['precio_valor_toma'] = None

        # Inicializar los formularios con post_data y file_data
        forms = self._initialize_forms(post_data, request.FILES)

        if self._validate_forms(forms):
            peritaje = self._create_peritaje(request, forms)
            return redirect('imagen_auto', peritaje_id=peritaje.id)
        else:
            # Si hay errores, volver a renderizar la página con los datos ingresados
            context = self._get_error_context(forms, file_data)
            return render(request, self.template_name, context)

    def _get_initial_context(self, request):
        usuario = request.user
        es_gerente = usuario.groups.filter(name='Gerente').exists()
        branches = Branch.objects.all()
        unidades_negocio = Unidad_negocio.objects.all()
        
        # Obtener la fecha actual
        fecha_actual = datetime.now()
        
        # Inicializar el formulario CochePeritajeForm con la fecha actual
        coche_form = CochePeritajeForm(initial={'fecha_tasacion': fecha_actual})
        
        return {
            'es_gerente': es_gerente,
            'usuario': request.user,
            'branches': branches,
            'unidades_negocio': unidades_negocio,
            'equipamiento_form': EquipamientoForm(),
            'coche_form': CochePeritajeForm(),
            'clienteperitar_form': ClientePeritarForm(),
            'inspeccion_cubiertas_form': InspeccionCubiertasForm(),
            'inspeccion_gral_form': InspeccionGralForm(),
            'gastos_total_form': Gastos_totalForm(),
            'fecha_actual':fecha_actual,
        }

    def _initialize_forms(self, post_data, file_data):
        return [
            Gastos_totalForm(post_data, file_data),
            EquipamientoForm(post_data, file_data),
            CochePeritajeForm(post_data, file_data),
            ClientePeritarForm(post_data, file_data),
            InspeccionCubiertasForm(post_data, file_data),
            InspeccionGralForm(post_data, file_data),
        ]

    def _validate_forms(self, forms):
        return all(form.is_valid() for form in forms)

    def _create_peritaje(self, request, forms):
        usuario = request.user
        branch_id = request.POST.get('branch')
        branch = get_object_or_404(Branch, id=branch_id)
        unidad_negocio_id = request.POST.get('unidad_negocio')
        unidad_negocio = get_object_or_404(Unidad_negocio, id=unidad_negocio_id)

        destinatario = self._get_destinatario(usuario)
        ultimo_identificador = Peritaje.objects.last().identificador if Peritaje.objects.last() else 0
        peritaje = Peritaje.objects.create(
            identificador=ultimo_identificador + 1,
            usuario=usuario,
            destinatario=destinatario,
            estado='CREANDO',
            branch=branch,
            unidad_negocio=unidad_negocio,
        )

        for form in forms:
            if form.is_valid():
                obj = form.save(commit=False)
                if isinstance(obj, CochePeritaje):
                    obj.fecha_tasacion = datetime.now()  # Asignar la fecha actual a fecha_tasacion
                obj.peritaje = peritaje
                obj.save()

        for f in request.FILES.getlist('fotos'):
            FotoPeritaje.objects.create(peritaje=peritaje, foto=f)
        return peritaje

    def _get_destinatario(self, usuario):
        try:
            creado_por = CreadoPor.objects.get(usuario=usuario)
            return creado_por.creado_por
        except CreadoPor.DoesNotExist:
            return usuario

    def _get_error_context(self, forms, file_data):
        errors = {form.__class__.__name__: form.errors for form in forms if not form.is_valid()}
        context = self._get_initial_context(self.request)
        # Actualizar el contexto con los formularios llenos y archivos
        context.update({
            'equipamiento_form': forms[1],
            'coche_form': forms[2],
            'clienteperitar_form': forms[3],
            'inspeccion_cubiertas_form': forms[4],
            'inspeccion_gral_form': forms[5],
            'gastos_total_form': forms[0],
            'errors': errors,
            'file_data': file_data,
        })
        return context



class CustomUserCreateView(CreateView):
    template_name = 'register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')

    def post(self, request, *args, **kwargs):
        self.object = None 
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            contrasena_temporal = generar_contrasena_temporal()
            user.set_password(contrasena_temporal)
            user.save()
            
            # Guarda las relaciones many-to-many (grupos en este caso)
            form.save_m2m()
            
            # Asigna el grupo seleccionado al usuario
            group = form.cleaned_data['group']
            user.groups.add(group)
            
            # Asigna la sucursal seleccionada al usuario
            branch = form.cleaned_data['branch']
            user.branch = branch
            user.save()

            if request.user.is_authenticated:
                CreadoPor.objects.create(usuario=user, creado_por=request.user)
                
            subject = 'Bienvenido a nuestro sitio de peritaje'
            message = f'Hola {user.username},\n\nTu cuenta ha sido creada con éxito. Tu contraseña es: {contrasena_temporal}\n\nSaludos,\nEl equipo. Puede ingresar a la página haciendo click aqui: http://127.0.0.1:8000/login/'
            from_email = 'peritajes@grupoquijada.com.ar'
            recipient_list = [user.email]
            
            send_mail(subject, message, from_email, recipient_list)
            
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
 
# VISTA IMAGEN DEL AUTO       
@login_required      
def imagen_auto(request, peritaje_id):
    peritaje = get_object_or_404(Peritaje, id=peritaje_id)
    imagen_marcada = ImagenMarcada.objects.filter(peritaje=peritaje).first()
    
    if request.method == 'POST':
        x = request.POST.get('x')
        y = request.POST.get('y')
        letra = request.POST.get('letra', 'A')
        
        marca = Marca.objects.create(x=x, y=y, letra=letra)
        
        return JsonResponse({'status': 'ok', 'id': marca.id})

    marcas = Marca.objects.all()
    return render(request, 'imagen_auto.html', {'marcas': marcas,'peritaje':peritaje,'imagen_marcada': imagen_marcada,'MEDIA_URL': settings.MEDIA_URL})

@login_required
def borrar_marcas(request):
    if request.method == 'POST':
        Marca.objects.all().delete()
        return JsonResponse({'status': 'ok'})

@login_required
def borrar_marca(request, marca_id):
    if request.method == 'POST':
        marca = get_object_or_404(Marca, id=marca_id)
        marca.delete()
        return JsonResponse({'status': 'ok'})
    
@login_required
def home(request):
    usuario = request.user
    es_gerente = usuario.groups.filter(name='Gerente').exists()
 
    peritajes_creados = Peritaje.objects.filter(usuario=usuario)
    peritajes_destinatario = Peritaje.objects.filter(destinatario=usuario)
    peritajes = peritajes_creados | peritajes_destinatario
 
    # Filtrado por nombre de entrega, patente o modelo
    if request.method == 'POST':
        nombre_entrega_query = request.POST.get('nombre_entrega')
        patente_query = request.POST.get('patente')
        modelo_query = request.POST.get('modelo')
 
        if nombre_entrega_query:
            peritajes = peritajes.filter(clienteperitar__nombre_apellido_entrega__icontains=nombre_entrega_query)
        if patente_query:
            peritajes = peritajes.filter(cocheperitaje__patente__icontains=patente_query)
        if modelo_query:
            peritajes = peritajes.filter(cocheperitaje__modelo__icontains=modelo_query)
 
    # Crear una lista de peritajes con la fecha de tasación
    peritajes_con_fechas = []
    for peritaje in peritajes:
        coche_peritaje = CochePeritaje.objects.filter(peritaje=peritaje).first()
        if coche_peritaje:
            peritajes_con_fechas.append({'peritaje': peritaje,'fecha_tasacion': coche_peritaje.fecha_tasacion})
        else:
            peritajes_con_fechas.append({'peritaje': peritaje, 'fecha_tasacion': None})
           
    paginator = Paginator(peritajes_con_fechas,3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
 
    return render(request, 'home.html', {'peritajes_con_fechas': peritajes_con_fechas, 'usuario': usuario, 'es_gerente': es_gerente,'page_obj':page_obj})

@login_required
def registrar_usuario(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            contrasena_temporal = generar_contrasena_temporal()
            user.set_password(contrasena_temporal)
            user.save()
            form.save_m2m()
            CreadoPor.objects.create(usuario=user, creado_por=request.user)
            
            # Enviar correo electrónico con la contraseña temporal
            subject = 'Bienvenido a nuestro sitio'
            message = f'Hola {user.first_name},\n\nTu cuenta ha sido creada con éxito. Tu contraseña temporal es: {contrasena_temporal}\n\nSaludos,\nEl equipo.'
            from_email = 'peritajes@grupoquijada.com.ar'
            recipient_list = [user.email]
            
            send_mail(subject, message, from_email, recipient_list)
            
            return redirect('home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registrar_usuario.html', {'form': form})

def generar_contrasena_temporal():
    caracteres = string.ascii_letters + string.digits
    contrasena_temporal = ''.join(random.choice(caracteres) for _ in range(6))  
    return contrasena_temporal

@login_required
def guardar_imagen(request, peritaje_id):
    usuario = request.user
    peritaje = Peritaje.objects.get(id=peritaje_id)
    if request.method == 'POST':
        imagen_data = request.FILES.get('imagen')
        observaciones = request.POST.get('observaciones', '')

        if imagen_data:
            try:
                img = Image.open(imagen_data)
                nombre_imagen = str(uuid.uuid4()) + '.png'
                img_path = os.path.join('peritaje_fotos', nombre_imagen)
                full_path = os.path.join(settings.MEDIA_ROOT, img_path)
                img.save(full_path)

                imagen = ImagenMarcada.objects.create(
                    nombre=nombre_imagen, 
                    ruta=img_path, 
                    peritaje=peritaje,
                    observaciones=observaciones
                )
                # Cambiar el estado del peritaje a "ENVIADO"
                peritaje.estado = 'ENVIADO'
                peritaje.save()
                
                try:
                    creado_por = CreadoPor.objects.get(usuario=usuario).creado_por
                except CreadoPor.DoesNotExist:
                    creado_por = usuario
                if creado_por:
                    subject = 'Peritaje recibido'
                    message = f'El usuario {usuario.username} ha presentado una rendicion de gastos. Haga <a href="http://peritaje.grupoquijada.com.ar">clic aqui</a> para ver su rendicion'
                    from_email = 'peritajes@grupoquijada.com.ar'
                    recipient_list = [creado_por.email]
                    
                    send_mail(subject, message, from_email, recipient_list)

                return JsonResponse({'status': 'ok'})
            except Peritaje.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Peritaje no encontrado'})
            except Exception as e:
                print(str(e))
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'No se proporcionó ninguna imagen'})
    else:
        return JsonResponse({'status': 'error', 'message': 'La solicitud no es de tipo POST'})
    
@login_required
def ver_peritaje(request, peritaje_id):
    peritaje = get_object_or_404(Peritaje, id=peritaje_id)
    usuario = request.user
    es_gerente = usuario.groups.filter(name='Gerente').exists()
    
    branch = peritaje.branch
    branch_image_url = f'images/{branch.image_filename}'
    ultima_imagen_marcada = ImagenMarcada.objects.filter(peritaje=peritaje).order_by('-id').first()
    
    fotos_peritaje = FotoPeritaje.objects.filter(peritaje=peritaje)
    imagen_marcada = ImagenMarcada.objects.filter(peritaje=peritaje).first()
    gastos_total_instance = get_object_or_404(Gastos_total, peritaje=peritaje)
    coche_peritaje_instance = get_object_or_404(CochePeritaje, peritaje=peritaje)
    clienteperitar_instance = get_object_or_404(ClientePeritar, peritaje=peritaje)
    inspeccioncubiertas_instance = get_object_or_404(InspeccionCubiertas, peritaje=peritaje)
    equipamiento_instance = get_object_or_404(Equipamiento, peritaje=peritaje)
    inspecciongral_instance = get_object_or_404(InspeccionGral, peritaje=peritaje)
    unidad_negocio = peritaje.unidad_negocio
    
    if request.method == 'POST' and es_gerente:
        if 'aprobado' in request.POST:
            peritaje.estado = 'ACEPTADO'
            # Enviar correo electrónico
            subject = 'Bienvenido a nuestro sitio'
            message = f'Hola {peritaje.usuario.first_name} {peritaje.usuario.last_name},\n\nTu peritaje ha sido aprobado con éxito.\n\nSaludos,\nEl equipo.'
            from_email = 'peritajes@grupoquijada.com.ar'
            recipient_list = [peritaje.usuario.email]
            send_mail(subject, message, from_email, recipient_list)
        elif 'rechazado' in request.POST:
            peritaje.estado = 'RECHAZADO'
            # Enviar correo electrónico
            subject = 'Bienvenido a nuestro sitio'
            message = f'Hola {peritaje.usuario.first_name} {peritaje.usuario.last_name},\n\nTu peritaje ha sido rechazado. Póngase en contacto con su supervisor.\n\nSaludos,\nEl equipo.'
            from_email = 'peritajes@grupoquijada.com.ar'
            recipient_list = [peritaje.usuario.email]
            send_mail(subject, message, from_email, recipient_list)
        peritaje.save()
        messages.info(request, f'El peritaje ha sido {peritaje.estado.lower()}.')
        return redirect('home')
    else:
        # Formatear los valores decimales para mostrarlos correctamente inspeccion cubiertas
        inspeccioncubiertas_instance.gastos_delantera_derecha = formatear_numero(inspeccioncubiertas_instance.gastos_delantera_derecha)
        inspeccioncubiertas_instance.gastos_delantera_izquierda = formatear_numero(inspeccioncubiertas_instance.gastos_delantera_izquierda)
        inspeccioncubiertas_instance.gastos_trasera_derecha = formatear_numero(inspeccioncubiertas_instance.gastos_trasera_derecha)
        inspeccioncubiertas_instance.gastos_trasera_izquierda = formatear_numero(inspeccioncubiertas_instance.gastos_trasera_izquierda)
        inspeccioncubiertas_instance.gastos_auxilio = formatear_numero(inspeccioncubiertas_instance.gastos_auxilio)
        # Formatear los valores decimales para mostrarlos correctamente gastos inspeccion general
        inspecciongral_instance.carroceria_general_gasto = formatear_numero(inspecciongral_instance.carroceria_general_gasto)
        inspecciongral_instance.chapa_gasto = formatear_numero(inspecciongral_instance.chapa_gasto)
        inspecciongral_instance.pintura_gasto = formatear_numero(inspecciongral_instance.pintura_gasto)
        inspecciongral_instance.motor_gasto = formatear_numero(inspecciongral_instance.motor_gasto)
        inspecciongral_instance.diferencial_gasto = formatear_numero(inspecciongral_instance.diferencial_gasto)
        inspecciongral_instance.embrague_gasto = formatear_numero(inspecciongral_instance.embrague_gasto)
        inspecciongral_instance.tren_delantero_gasto = formatear_numero(inspecciongral_instance.tren_delantero_gasto)
        inspecciongral_instance.tren_trasero_gasto = formatear_numero(inspecciongral_instance.tren_trasero_gasto)
        inspecciongral_instance.direccion_gasto = formatear_numero(inspecciongral_instance.direccion_gasto)
        inspecciongral_instance.frenos_gasto = formatear_numero(inspecciongral_instance.frenos_gasto)
        inspecciongral_instance.amortiguadores_tras_gasto = formatear_numero(inspecciongral_instance.amortiguadores_tras_gasto)
        inspecciongral_instance.amortiguadores_del_gasto = formatear_numero(inspecciongral_instance.amortiguadores_del_gasto)
        inspecciongral_instance.arranque_gasto = formatear_numero(inspecciongral_instance.arranque_gasto)
        inspecciongral_instance.radiadores_gasto = formatear_numero(inspecciongral_instance.radiadores_gasto)
        inspecciongral_instance.electricidad_gasto = formatear_numero(inspecciongral_instance.electricidad_gasto)
        inspecciongral_instance.aacc_calefaccion_gasto = formatear_numero(inspecciongral_instance.aacc_calefaccion_gasto)
        inspecciongral_instance.radio_gasto = formatear_numero(inspecciongral_instance.radio_gasto)
        inspecciongral_instance.bateria_gasto = formatear_numero(inspecciongral_instance.bateria_gasto)
        inspecciongral_instance.llantas_gasto = formatear_numero(inspecciongral_instance.llantas_gasto)
        inspecciongral_instance.tasas_gasto = formatear_numero(inspecciongral_instance.tasas_gasto)
        inspecciongral_instance.parabrisas_gasto = formatear_numero(inspecciongral_instance.parabrisas_gasto)
        inspecciongral_instance.asientos_gasto = formatear_numero(inspecciongral_instance.asientos_gasto)
        inspecciongral_instance.tapizado_gasto = formatear_numero(inspecciongral_instance.tapizado_gasto)
        inspecciongral_instance.volante_gasto = formatear_numero(inspecciongral_instance.volante_gasto)
        inspecciongral_instance.freno_de_mano_gasto = formatear_numero(inspecciongral_instance.freno_de_mano_gasto)
        inspecciongral_instance.bagueta_gasto = formatear_numero(inspecciongral_instance.bagueta_gasto)
        inspecciongral_instance.moldura_gasto = formatear_numero(inspecciongral_instance.moldura_gasto)
        
        initial_data = {
            'gastos_delantera_derecha': inspeccioncubiertas_instance.gastos_delantera_derecha,
            'gastos_delantera_izquierda': inspeccioncubiertas_instance.gastos_delantera_izquierda,
            'gastos_trasera_derecha': inspeccioncubiertas_instance.gastos_trasera_derecha,
            'gastos_trasera_izquierda': inspeccioncubiertas_instance.gastos_trasera_izquierda,
            'gastos_auxilio': inspeccioncubiertas_instance.gastos_auxilio,
            'carroceria_general_gasto':inspecciongral_instance.carroceria_general_gasto,
            'chapa_gasto': inspecciongral_instance.chapa_gasto,
            'pintura_gasto':inspecciongral_instance.pintura_gasto,
            'motor_gasto': inspecciongral_instance.motor_gasto,
            'diferencial_gasto': inspecciongral_instance.diferencial_gasto,
            'embrague_gasto': inspecciongral_instance.embrague_gasto,
            'tren_delantero_gasto': inspecciongral_instance.tren_delantero_gasto,
            'tren_trasero_gasto':inspecciongral_instance.tren_trasero_gasto,
            'direccion_gasto': inspecciongral_instance.direccion_gasto,
            'frenos_gasto': inspecciongral_instance.frenos_gasto,
            'amortiguadores_tras_gasto': inspecciongral_instance.amortiguadores_tras_gasto,
            'amortiguadores_del_gasto': inspecciongral_instance.amortiguadores_del_gasto,
            'arranque_gasto': inspecciongral_instance.arranque_gasto,
            'radiadores_gasto': inspecciongral_instance.radiadores_gasto,
            'electricidad_gasto': inspecciongral_instance.electricidad_gasto,
            'aacc_calefaccion_gasto': inspecciongral_instance.aacc_calefaccion_gasto,
            'radio_gasto': inspecciongral_instance.radio_gasto,
            'bateria_gasto': inspecciongral_instance.bateria_gasto,
            'llantas_gasto': inspecciongral_instance.llantas_gasto,
            'tasas_gasto': inspecciongral_instance.tasas_gasto,
            'parabrisas_gasto': inspecciongral_instance.parabrisas_gasto,
            'asientos_gasto': inspecciongral_instance.asientos_gasto,
            'tapizado_gasto': inspecciongral_instance.tapizado_gasto,
            'volante_gasto': inspecciongral_instance.volante_gasto,
            'freno_de_mano_gasto': inspecciongral_instance.freno_de_mano_gasto,
            'bagueta_gasto': inspecciongral_instance.bagueta_gasto,
            'moldura_gasto': inspecciongral_instance.moldura_gasto,
        }

        gastos_total_form = Gastos_totalForm(instance=gastos_total_instance)
        coche_form = CochePeritajeForm(instance=coche_peritaje_instance, initial=initial_data)
        clienteperitar_form = ClientePeritarForm(instance=clienteperitar_instance)
        inspeccion_cubiertas_form = InspeccionCubiertasForm(initial=initial_data,instance=inspeccioncubiertas_instance)
        equipamiento_form = EquipamientoForm(instance=equipamiento_instance)
        inspeccion_gral_form = InspeccionGralForm(initial=initial_data,instance=inspecciongral_instance)
    
    fecha_tasacion_formateada = coche_peritaje_instance.fecha_tasacion.strftime('%d/%m/%Y') if coche_peritaje_instance.fecha_tasacion else ''
    fecha_vto_e_itv_formateada = coche_peritaje_instance.vto_de_vto_o_itv.strftime('%d/%m/%Y') if coche_peritaje_instance.vto_de_vto_o_itv else 'No tiene'
    fecha_service_aceite_formateada = coche_peritaje_instance.ultimo_service_aceite_fecha.strftime('%d/%m/%Y') if coche_peritaje_instance.ultimo_service_aceite_fecha else ''
    fecha_cambio_distribucion_formateada = coche_peritaje_instance.ultimo_cambio_distribucion_fecha.strftime('%d/%m/%Y') if coche_peritaje_instance.ultimo_cambio_distribucion_fecha else ''
    fecha_gnc_vto_hidraulica_formateada = coche_peritaje_instance.gnc_vtohidraulica.strftime('%d/%m/%Y') if coche_peritaje_instance.gnc_vtohidraulica else 'No posee GNC'
    fecha_gnc_vto_oblea_formateada = coche_peritaje_instance.gnc_vtooblea.strftime('%d/%m/%Y') if coche_peritaje_instance.gnc_vtooblea else 'No posee GNC'
    fecha_ultimo_cambio_bateria = coche_peritaje_instance.bateria_ultimo_cambio.strftime('%d/%m/%Y')  if coche_peritaje_instance.bateria_ultimo_cambio else ''
        
    context = {
        'usuario' : usuario,
        'branch_image_url': branch_image_url,
        'fecha_ultimo_cambio_bateria': fecha_ultimo_cambio_bateria,
        'fecha_gnc_vto_oblea_formateada': fecha_gnc_vto_oblea_formateada,
        'fecha_gnc_vto_hidraulica_formateada': fecha_gnc_vto_hidraulica_formateada,
        'fecha_cambio_distribucion_formateada': fecha_cambio_distribucion_formateada,
        'fecha_service_aceite_formateada': fecha_service_aceite_formateada,
        'fecha_vto_e_itv_formateada': fecha_vto_e_itv_formateada,
        'fecha_tasacion_formateada': fecha_tasacion_formateada,
        'fotos_peritaje': fotos_peritaje,
        'es_gerente': es_gerente,
        'peritaje': peritaje,
        'coche_form': coche_form,
        'clienteperitar_form': clienteperitar_form,
        'inspeccion_cubiertas_form': inspeccion_cubiertas_form,
        'equipamiento_form': equipamiento_form,
        'inspeccion_gral_form': inspeccion_gral_form,
        'gastos_total_form': gastos_total_form,
        'ultima_imagen_marcada': ultima_imagen_marcada,
        'MEDIA_URL': settings.MEDIA_URL,
        'branch': branch,
        'unidad_negocio': unidad_negocio,  
    }
    
    return render(request, 'ver_peritaje.html', context)

@login_required
def imprimir(request, peritaje_id):
    peritaje = get_object_or_404(Peritaje, pk=peritaje_id)
    usuario = request.user
    es_gerente = usuario.groups.filter(name='Gerente').exists()
    
    unidad_negocio = peritaje.unidad_negocio
    
    branch = peritaje.branch
    branch_image_url = f'images/{branch.image_filename}'
    
    ultima_imagen_marcada = ImagenMarcada.objects.filter(peritaje=peritaje).order_by('-id').first()
    
    fotos_peritaje = FotoPeritaje.objects.filter(peritaje=peritaje)
    imagen_marcada = ImagenMarcada.objects.filter(peritaje=peritaje).first()
    gastos_total_instance = get_object_or_404(Gastos_total, peritaje=peritaje)
    coche_peritaje_instance = get_object_or_404(CochePeritaje, peritaje=peritaje)
    clienteperitar_instance = get_object_or_404(ClientePeritar, peritaje=peritaje)
    inspeccioncubiertas_instance = get_object_or_404(InspeccionCubiertas, peritaje=peritaje)
    equipamiento_instance = get_object_or_404(Equipamiento, peritaje=peritaje)
    inspecciongral_instance = get_object_or_404(InspeccionGral, peritaje=peritaje)
    gastos_total_form = Gastos_totalForm(instance=gastos_total_instance)
    coche_form = CochePeritajeForm(instance=coche_peritaje_instance)
    clienteperitar_form = ClientePeritarForm(instance=clienteperitar_instance)
    inspeccion_cubiertas_form = InspeccionCubiertasForm(instance=inspeccioncubiertas_instance)
    equipamiento_form = EquipamientoForm(instance=equipamiento_instance)
    inspeccion_gral_form = InspeccionGralForm(instance=inspecciongral_instance)
    
    fecha_tasacion_formateada = coche_peritaje_instance.fecha_tasacion.strftime('%d/%m/%Y') if coche_peritaje_instance.fecha_tasacion else ''
    fecha_vto_e_itv_formateada = coche_peritaje_instance.vto_de_vto_o_itv.strftime('%d/%m/%Y') if coche_peritaje_instance.vto_de_vto_o_itv else 'No tiene'
    fecha_service_aceite_formateada = coche_peritaje_instance.ultimo_service_aceite_fecha.strftime('%d/%m/%Y') if coche_peritaje_instance.ultimo_service_aceite_fecha else ''
    fecha_cambio_distribucion_formateada = coche_peritaje_instance.ultimo_cambio_distribucion_fecha.strftime('%d/%m/%Y') if coche_peritaje_instance.ultimo_cambio_distribucion_fecha else ''
    fecha_gnc_vto_hidraulica_formateada = coche_peritaje_instance.gnc_vtohidraulica.strftime('%d/%m/%Y') if coche_peritaje_instance.gnc_vtohidraulica else 'No posee GNC'
    fecha_gnc_vto_oblea_formateada = coche_peritaje_instance.gnc_vtooblea.strftime('%d/%m/%Y') if coche_peritaje_instance.gnc_vtooblea else 'No posee GNC'
    fecha_ultimo_cambio_bateria = coche_peritaje_instance.bateria_ultimo_cambio.strftime('%d/%m/%Y') if coche_peritaje_instance.bateria_ultimo_cambio else ''
    
    context = {
        'branch_image_url': branch_image_url,
        'fecha_ultimo_cambio_bateria': fecha_ultimo_cambio_bateria,
        'fecha_gnc_vto_oblea_formateada': fecha_gnc_vto_oblea_formateada,
        'fecha_gnc_vto_hidraulica_formateada': fecha_gnc_vto_hidraulica_formateada,
        'fecha_cambio_distribucion_formateada': fecha_cambio_distribucion_formateada,
        'fecha_service_aceite_formateada': fecha_service_aceite_formateada,
        'fecha_vto_e_itv_formateada': fecha_vto_e_itv_formateada,
        'fecha_tasacion_formateada': fecha_tasacion_formateada,
        'fotos_peritaje': fotos_peritaje,
        'es_gerente': es_gerente,
        'peritaje': peritaje,
        'coche_form': coche_form,
        'clienteperitar_form': clienteperitar_form,
        'inspeccion_cubiertas_form': inspeccion_cubiertas_form,
        'equipamiento_form': equipamiento_form,
        'inspeccion_gral_form': inspeccion_gral_form,
        'gastos_total_form': gastos_total_form,
        'peritaje': peritaje,
        'ultima_imagen_marcada': ultima_imagen_marcada,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'imprimir.html', context)

def ver_auto(request, peritaje_id):
    peritaje = get_object_or_404(Peritaje, pk=peritaje_id)
    ultima_imagen_marcada = ImagenMarcada.objects.filter(peritaje=peritaje).order_by('-id').first()

    context = {
        'ultima_imagen_marcada': ultima_imagen_marcada,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render (request, 'ver_auto.html', context)



# EDITAR PERITAJE 

@login_required
def editar_peritaje(request, peritaje_id):
    
    peritaje = get_object_or_404(Peritaje, id=peritaje_id)
    usuario = request.user
    es_gerente = usuario.groups.filter(name='Gerente').exists()
    
    if not es_gerente:
        return HttpResponseNotAllowed(['POST'])
    
    branch = peritaje.branch
    branch_image_url = f'images/{branch.image_filename}'
    ultima_imagen_marcada = ImagenMarcada.objects.filter(peritaje=peritaje).order_by('-id').first()
    
    forms = ""

    fotos_peritaje = FotoPeritaje.objects.filter(peritaje=peritaje)
    imagen_marcada = ImagenMarcada.objects.filter(peritaje=peritaje).first()
    gastos_total_instance = get_object_or_404(Gastos_total, peritaje=peritaje)
    coche_peritaje_instance = get_object_or_404(CochePeritaje, peritaje=peritaje)
    clienteperitar_instance = get_object_or_404(ClientePeritar, peritaje=peritaje)
    inspeccioncubiertas_instance = get_object_or_404(InspeccionCubiertas, peritaje=peritaje)
    equipamiento_instance = get_object_or_404(Equipamiento, peritaje=peritaje)
    inspecciongral_instance = get_object_or_404(InspeccionGral, peritaje=peritaje)
    unidades_negocio = Unidad_negocio.objects.all()
    branches = Branch.objects.all()

    if request.method == 'POST':
        post_data = request.POST.copy()

        for field_name in post_data:
            if field_name.startswith('gastos_') or field_name.endswith('_gasto') or field_name == 'total_gastos':
                field_value = post_data[field_name]
                if field_value:
                    field_value_str = field_value.replace('.', '').replace(',', '.')
                    try:
                        post_data[field_name] = str(Decimal(field_value_str))
                    except InvalidOperation:
                        post_data[field_name] = '0'
        
        if not es_gerente:
            post_data['precio_valor_toma'] = None

        gastos_total_form = Gastos_totalForm(post_data, instance=gastos_total_instance)
        coche_form = CochePeritajeForm(post_data, instance=coche_peritaje_instance)
        clienteperitar_form = ClientePeritarForm(post_data, instance=clienteperitar_instance)
        inspeccion_cubiertas_form = InspeccionCubiertasForm(post_data, instance=inspeccioncubiertas_instance)
        equipamiento_form = EquipamientoForm(post_data, instance=equipamiento_instance)
        inspeccion_gral_form = InspeccionGralForm(post_data, instance=inspecciongral_instance)

        forms = [
            gastos_total_form, coche_form, clienteperitar_form,
            inspeccion_cubiertas_form, equipamiento_form, inspeccion_gral_form
        ]

        if all([form.is_valid() for form in forms]):
            for form in forms:
                form.save()
            peritaje.unidad_negocio_id = post_data.get('unidad_negocio')
            peritaje.branch_id = post_data.get('branch')
            peritaje.save()
            # Crear un registro de cambio
            Cambios.objects.create(
                fecha_cambio=timezone.now(),
                peritaje_cambio=peritaje,
                usuario_cambio=usuario
            )
            return redirect('home')
    else:
        initial_data = {
            'fecha_tasacion': coche_peritaje_instance.fecha_tasacion,
            'vto_de_vto_o_itv': coche_peritaje_instance.vto_de_vto_o_itv,
            'ultimo_service_aceite_fecha': coche_peritaje_instance.ultimo_service_aceite_fecha,
            'ultimo_cambio_distribucion_fecha': coche_peritaje_instance.ultimo_cambio_distribucion_fecha,
            'gnc_vtohidraulica': coche_peritaje_instance.gnc_vtohidraulica,
            'gnc_vtooblea': coche_peritaje_instance.gnc_vtooblea,
            'bateria_ultimo_cambio': coche_peritaje_instance.bateria_ultimo_cambio,
        }

        gastos_total_form = Gastos_totalForm(instance=gastos_total_instance)
        coche_form = CochePeritajeForm(instance=coche_peritaje_instance, initial=initial_data)
        clienteperitar_form = ClientePeritarForm(instance=clienteperitar_instance)
        inspeccion_cubiertas_form = InspeccionCubiertasForm(instance=inspeccioncubiertas_instance)
        equipamiento_form = EquipamientoForm(instance=equipamiento_instance)
        inspeccion_gral_form = InspeccionGralForm(instance=inspecciongral_instance)

    context = {
        'errors': {form.__class__.__name__: form.errors for form in forms if not form.is_valid()},
        'branch_image_url': branch_image_url,
        'fotos_peritaje': fotos_peritaje,
        'es_gerente': es_gerente,
        'peritaje': peritaje,
        'coche_form': coche_form,
        'clienteperitar_form': clienteperitar_form,
        'inspeccion_cubiertas_form': inspeccion_cubiertas_form,
        'equipamiento_form': equipamiento_form,
        'inspeccion_gral_form': inspeccion_gral_form,
        'gastos_total_form': gastos_total_form,
        'ultima_imagen_marcada': ultima_imagen_marcada,
        'MEDIA_URL': settings.MEDIA_URL,
        'branch': branch,
        'unidades_negocio': unidades_negocio,
        'branches': branches,
    }

    return render(request, 'editar_peritaje.html', context)


@login_required
def reporte(request):
    # Obtener el mes y año de los parámetros GET
    fecha_desde = request.GET.get('fecha_inicio')
    fecha_hasta = request.GET.get('fecha_fin')
    branch_id = request.GET.get('branch')

    peritajes = Peritaje.objects.all()

    # Filtrar peritajes por mes y año si se proporcionan
    if fecha_desde and fecha_hasta:
        anio_desde, mes_desde = fecha_desde.split('-')
        anio_hasta, mes_hasta = fecha_hasta.split('-')
        peritajes = peritajes.filter(
            cocheperitaje__fecha_tasacion__year__gte=anio_desde,
            cocheperitaje__fecha_tasacion__year__lte=anio_hasta,
            cocheperitaje__fecha_tasacion__month__gte=mes_desde,
            cocheperitaje__fecha_tasacion__month__lte=mes_hasta
        )
    elif fecha_desde:
        anio, mes = fecha_desde.split('-')
        peritajes = peritajes.filter(
            cocheperitaje__fecha_tasacion__year=anio,
            cocheperitaje__fecha_tasacion__month=mes
        )
    elif fecha_hasta:
        anio, mes = fecha_hasta.split('-')
        peritajes = peritajes.filter(
            cocheperitaje__fecha_tasacion__year=anio,
            cocheperitaje__fecha_tasacion__month=mes
        )

    # Filtrar peritajes por branch si se proporciona
    if branch_id:
        peritajes = peritajes.filter(branch_id=branch_id)
    
    peritajes_con_fechas = []
    for peritaje in peritajes:
        coche_peritaje = CochePeritaje.objects.filter(peritaje=peritaje).first()
        cliente_peritar = ClientePeritar.objects.filter(peritaje=peritaje).first()
        total_gastos = Gastos_total.objects.filter(peritaje=peritaje).first()
        if coche_peritaje:
            peritajes_con_fechas.append({
                'peritaje': peritaje,
                'fecha_tasacion': coche_peritaje.fecha_tasacion,
                'coche_peritaje': coche_peritaje,
                'cliente_peritar': cliente_peritar,
                'total_gastos': total_gastos,
            })
        else:
            peritajes_con_fechas.append({
                'peritaje': peritaje,
                'fecha_tasacion': None,
                'coche_peritaje': None,
                'cliente_peritar': cliente_peritar,
                'total_gastos': total_gastos,
            })

    # Ordenar por fecha de tasación de mayor a menor
    peritajes_con_fechas.sort(key=lambda x: (x['fecha_tasacion'] is None, x['fecha_tasacion']), reverse=True)

    # Obtener todas las branches para el select
    branches = Branch.objects.all()
    
    # Obtener la cantidad de peritajes
    cantidad = len(peritajes_con_fechas)

    context = {
        'peritajes': peritajes_con_fechas,
        'branches': branches,
        'cantidad': cantidad,
    }
    
    return render(request, 'reporte.html', context)

@login_required
def excel(request):
    # Obtener el mes y año de los parámetros GET
    fecha = request.GET.get('fecha')
    branch_id = request.GET.get('branch')

    # Filtrar peritajes por mes y año si se proporcionan
    if fecha:
        anio, mes = fecha.split('-')
        peritajes = Peritaje.objects.filter(
            cocheperitaje__fecha_tasacion__year=anio,
            cocheperitaje__fecha_tasacion__month=mes
        )
    else:
        peritajes = Peritaje.objects.all()

    # Filtrar peritajes por branch si se proporciona
    if branch_id:
        peritajes = peritajes.filter(branch_id=branch_id)
    
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = 'Peritajes'

    # Escribir encabezados de la tabla
    headers = ['ID', 'Nombre Apellido', 'Apellido', 'Patente', 'Modelo', 'Fecha Tasacion']
    sheet.append(headers)

    # Obtener los datos de los peritajes
    for peritaje in peritajes:
        coche_peritaje = CochePeritaje.objects.filter(peritaje=peritaje).first()
        cliente_peritar = ClientePeritar.objects.filter(peritaje=peritaje).first()
        
        if coche_peritaje and cliente_peritar:
            row = [
                peritaje.id,
                cliente_peritar.nombre_apellido_entrega,
                cliente_peritar.nombre_apellido_duenio,
                coche_peritaje.patente,
                coche_peritaje.modelo,
                coche_peritaje.fecha_tasacion.strftime('%Y-%m-%d') if coche_peritaje.fecha_tasacion else ''
            ]
        else:
            row = [
                peritaje.id,
                cliente_peritar.nombre_apellido_entrega if cliente_peritar else '',
                cliente_peritar.nombre_apellido_duenio if cliente_peritar else '',
                coche_peritaje.patente if coche_peritaje else '',
                coche_peritaje.modelo if coche_peritaje else '',
                coche_peritaje.fecha_tasacion.strftime('%Y-%m-%d') if coche_peritaje and coche_peritaje.fecha_tasacion else ''
            ]
        
        sheet.append(row)
    
    # Configurar la respuesta HTTP
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=peritajes.xlsx'
    workbook.save(response)
    return response