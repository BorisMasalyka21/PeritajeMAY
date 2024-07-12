from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.contrib.auth import get_user_model
import string
from django.utils import timezone
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


# SUCURSALES    
class Branch(models.Model):
    name = models.CharField(max_length=100)
    image_filename = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class CustomUser(AbstractUser):
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return f"Nombre: {self.username} - Email: {self.email} - Sucursal: {self.branch.name if self.branch else 'Sin asignar'}"
    

    
#  UNIDAD NEGOCIO   
class Unidad_negocio(models.Model):
    unidad = models.CharField(max_length=100,default='')
    def __str__(self):
        return self.unidad
    
    
# MARCA   
class MarcaAuto(models.Model):
    marca_auto = models.CharField(max_length=100,default='')
    def __str__(self):
        return self.marca_auto
    
    
# VENDEDOR    
class Vendedor(models.Model):
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return f" {self.nombre}"
       
# PERITAJE
class Peritaje(models.Model):
    ESTADO_CHOICES = [
        ('ACEPTADO', 'ACEPTADO'),
        ('ESPERA', 'ESPERA'),
        ('RECHAZADO', 'RECHAZADO'),
        ('RENDIDO', 'RENDIDO'),
        ('CREANDO', 'CREANDO'),
        ('ENVIADO', 'ENVIADO')
    ]
    identificador = models.BigIntegerField(unique=True)
    usuario = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    destinatario = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, null=True, related_name='gastos_destinatario'
    )
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='ESPERA')
    codigo_peritaje = models.CharField(max_length=15, blank=True, null=True)
    unidad_negocio = models.ForeignKey('Unidad_negocio', on_delete=models.CASCADE)
    branch = models.ForeignKey('Branch', on_delete=models.CASCADE) 
    

    BRANCH_CODES = {
        1: 'AV01',
        2: 'AV03',
        3: 'AV02',
        4: 'VO01',
        5: 'CH01',
        6: 'CH02',
        7: 'AM01',
        8: 'IQ01',
        9: 'AR01',
        10: 'AR02',
        11: 'AI01',
        12: 'AI03',
    }

    def save(self, *args, **kwargs):
        if not self.codigo_peritaje:
            last_peritaje = Peritaje.objects.filter(branch=self.branch).order_by('id').last()
            if last_peritaje and last_peritaje.codigo_peritaje:
                # Extraer solo la parte numérica del último código
                last_code_segment = last_peritaje.codigo_peritaje.split('/')[-1]
                number_part = ''.join(filter(str.isdigit, last_code_segment))
                if number_part:  # Verificar si hay números en el segmento
                    number = int(number_part) + 1
                else:
                    number = 1  # Si no hay números, empezar desde 1
                new_code = str(number).zfill(7)
            else:
                new_code = '0000001'
            prefix = self.BRANCH_CODES.get(self.branch.id, 'XX')
            self.codigo_peritaje = f"{prefix}/{new_code}"
        super().save(*args, **kwargs)

 
 
# CREADO POR   
class CreadoPor(models.Model):
    usuario = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    creado_por = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='created_users')
    
    def __str__(self):
        return f"Perfil Usuario: {self.usuario} - Creado por {self.creado_por}"


# CLIENTE A PERITAR 
class ClientePeritar(models.Model):
    nombre_apellido_entrega = models.CharField(max_length=200, verbose_name="Nombre y Apellido")
    email_entrega = models.EmailField(verbose_name="Email de Entrega", blank=True)
    cuil_entrega = models.CharField(max_length=13,verbose_name="Cuil de Entrega")
    telefono_entrega = models.CharField(max_length=100, verbose_name="Teléfono de Entrega")
    nombre_apellido_duenio = models.CharField(max_length=200, verbose_name="Nombre y Apellido del dueño", blank=True)
    email_duenio = models.EmailField(verbose_name="Email del Dueño", blank=True)
    cuil_duenio = models.CharField(max_length=13,verbose_name="Cuil de Dueño", blank=True)
    telefono_duenio = models.CharField(max_length=100, verbose_name="Teléfono del Dueño", blank=True)
    peritaje = models.ForeignKey(Peritaje, on_delete=models.CASCADE)
    

 
#  COCHE PRITAJE  
class CochePeritaje(models.Model):
    PROVINCIAS_CHOICES = [('Buenos Aires','Buenos Aires'),
    ('Ciudad Autónoma de Buenos Aires','Ciudad Autónoma de Buenos Aires'),
    ('Catamarca','Catamarca'),
    ('Chaco','Chaco'),
    ('Chubut','Chubut'),
    ('Córdoba','Córdoba'),
    ('Corrientes','Corrientes'),
    ('Entre Ríos','Entre Ríos'),
    ('Formosa','Formosa'),
    ('Jujuy','Jujuy'),
    ('La Pampa','La Pampa'),
    ('La Rioja','La Rioja'),
    ('Mendoza','Mendoza'),
    ('Misiones','Misiones'),
    ('Neuquén','Neuquén'),
    ('Río Negro','Río Negro'),
    ('Salta','Salta'),
    ('San Juan','San Juan'),
    ('San Luis','San Luis'),
    ('Santa Cruz','Santa Cruz'),
    ('Santa Fe','Santa Fe'),
    ('Santiago del Estero','Santiago del Estero'),
    ('Tierra del Fuego','Tierra del Fuego'),
    ('Tucumán','Tucumán'),]
    CAJA_CHOICES = [('Manual', 'Manual'),('Automatico', 'Automatico'),]
    COMBUSTIBLE_CHOICES = [('NAFTA', 'NAFTA'),('DIESEL', 'DIESEL'),('GNC', 'GNC')]
    PUERTAS_CHOICES= [('2', '2'),('3', '3'),('4', '4'),('5', '5')]
    COLORES_CHOICES = [
    ('amarillo', 'Amarillo'),
    ('azul', 'Azul'),
    ('azul_metalico', 'Azul Metálico'),
    ('blanco', 'Blanco'),
    ('blanco_banquise', 'Blanco Banquise'),
    ('blanco_negro', 'Blanco / Negro'),
    ('borgona', 'Borgoña'),
    ('cassiopee', 'Cassiopee'),
    ('champagne', 'Champagne'),
    ('cobre', 'Cobre'),
    ('dorado', 'Dorado'),
    ('dune_beige', 'Dune Beige'),
    ('fuego', 'Fuego'),
    ('generico', 'Generico'),
    ('gris', 'Gris'),
    ('gris_etoile', 'Gris Etoile'),
    ('gris_perla', 'Gris Perla'),
    ('gris_plata', 'Gris Plata'),
    ('gris_quartz', 'Gris Quartz'),
    ('marron', 'Marrón'),
    ('naranja', 'Naranja'),
    ('negro', 'Negro'),
    ('plateado', 'Plateado'),
    ('rojo', 'Rojo'),
    ('rojo_fuego', 'Rojo Fuego'),
    ('rosa', 'Rosa'),
    ('turquesa', 'Turquesa'),
    ('verde', 'Verde'),
    ('verde_militar', 'Verde Militar'),
    ('violeta', 'Violeta')
]
    fecha_tasacion = models.DateTimeField(verbose_name="Fecha de Tasacion")
    peritador = models.CharField(max_length=100, verbose_name="Peritador")
    receptor = models.CharField(max_length=100, verbose_name="Receptor", blank=True, null=True)
    fecha_recepcion = models.DateTimeField(verbose_name="Fecha de Recepcion", blank=True, null=True)
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, null=False, blank=False,default=False)
    provincia_Radicado = models.CharField(max_length=100, verbose_name="Provincia Radicado",choices=PROVINCIAS_CHOICES,null=False,blank=False,default=False)
    vto_de_vto_o_itv = models.DateTimeField(max_length=100, verbose_name="Vto de VTO o ITV", blank=True, null=True)
    marca = models.ForeignKey(MarcaAuto, on_delete=models.CASCADE, null=False, blank=False,default=False)
    formato_cubiertas_validator = RegexValidator(regex=r'^\d{3}/\d{2}R\d{2}$',message="El formato de las medidas debe ser '000/00R00'.")
    patente = models.CharField(max_length=7,verbose_name="Patente")
    modelo = models.CharField(max_length=100, verbose_name="Modelo")
    puertas = models.CharField(max_length=10, verbose_name="Puertas", choices=PUERTAS_CHOICES,default=False)
    man_aut = models.CharField(max_length=50, verbose_name="Manual o Automatico",choices=CAJA_CHOICES,default=False)
    combustible = models.CharField(max_length=50, verbose_name="Combustible",choices=COMBUSTIBLE_CHOICES,default=False)
    color = models.CharField(max_length=50, verbose_name="Color", choices=COLORES_CHOICES,default=False)
    año = models.IntegerField(verbose_name="Año")
    km = models.BigIntegerField(verbose_name="Kilometraje")
    dueño_mano = models.CharField(max_length=100, verbose_name="Dueño Mano")
    ultimo_service_aceite_fecha = models.DateTimeField(verbose_name="Ultimo Service de Aceite (Fecha)",)
    ultimo_service_aceite_km = models.BigIntegerField(verbose_name="Ultimo Service de Aceite (Km)")
    ultimo_cambio_distribucion_fecha = models.DateTimeField(verbose_name="Ultimo Cambio de Distribucion (Fecha)",null=True, blank=True)
    ultimo_cambio_distribucion_km = models.BigIntegerField(verbose_name="Ultimo Cambio de Distribucion (Km)",null=True, blank=True)
    gnc_vtohidraulica = models.DateTimeField(verbose_name="GNC Vto Hidrulica",blank=True, null=True)
    gnc_vtooblea = models.DateTimeField(verbose_name="GNC Vto Oblea",blank=True, null=True)
    gnc_metros = models.BigIntegerField(verbose_name="GNC Metros",blank=True, null=True)
    gnc_generacion = models.BigIntegerField(verbose_name="GNC Generacion", null=True,blank=True)
    bateria_marca = models.CharField(max_length=100, verbose_name="Bateria Marca")
    bateria_medida = models.CharField(max_length=50, verbose_name="Bateria Medida")
    bateria_ultimo_cambio = models.DateTimeField(verbose_name="Fecha de ultimo cambio bateria", null=True, blank=True)
    es_fecha_original = models.BooleanField(default=False)
    
    peritaje = models.ForeignKey(Peritaje, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.patente}"



from django.db import models
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile

class FotoPeritaje(models.Model):
    foto = models.ImageField(upload_to='peritaje_fotos/', verbose_name='Foto del peritaje', max_length=255)
    peritaje = models.ForeignKey(Peritaje, on_delete=models.CASCADE) 
    def __str__(self):
        return f"Foto de {self.peritaje.marca} {self.peritaje.modelo}"

    
# EQUIPAMIENTO
class Equipamiento(models.Model):
    Aire_climatizador = models.BooleanField(default=False, verbose_name="Aire Climatizador")
    DirElectricaoHidraulica = models.BooleanField(default=False, verbose_name="Dirección Electrónica/Hidráulica")
    CierraCentralizado = models.BooleanField(default=False, verbose_name="Cierre Centralizado")
    TechoCorredizo = models.BooleanField(default=False, verbose_name="Techo Corredizo")
    LlantasDeAleacion = models.BooleanField(default=False, verbose_name="Llantas de Aleación")
    Airbags = models.BooleanField(default=False, verbose_name="Airbags")
    ABS = models.BooleanField(default=False, verbose_name="ABS ")
    ESP = models.BooleanField(default=False, verbose_name="ESP")
    Alarma = models.BooleanField(default=False, verbose_name="Alarma")
    Polarizado = models.BooleanField(default=False, verbose_name="Polarizado")
    GatoLlave = models.BooleanField(default=False, verbose_name="Gato y Llave para Ruedas")
    StereoOriginal = models.BooleanField(default=False, verbose_name="Stereo Original")
    EspejosElectricos = models.BooleanField(default=False, verbose_name="Espejos Eléctricos")
    CamaraRetroceso = models.BooleanField(default=False, verbose_name="Cámara de Retroceso")
    SensoresEst = models.BooleanField(default=False, verbose_name="Sensores de Estacionamiento")
    Pantalla = models.BooleanField(default=False, verbose_name="Pantalla")
    ControlVelCrucero = models.BooleanField(default=False, verbose_name="Control de Velocidad Crucero")
    FarosAntiniebla = models.BooleanField(default=False, verbose_name="Faros Antiniebla")
    DuplicadoLlave = models.BooleanField(default=False, verbose_name="Duplicado de Llave")
    Manuales = models.BooleanField(default=False, verbose_name="Manuales")
    CodigoStereo = models.BooleanField(default=False, verbose_name="Código de Stereo")
    TuercaSeguridad = models.BooleanField(default=False, verbose_name="Tuerca de Seguridad")
    Matafuegos = models.BooleanField(default=False, verbose_name="Matafuegos")
    CortaCorriente = models.BooleanField(default=False, verbose_name="Corta Corriente")
    peritaje = models.ForeignKey(Peritaje, on_delete=models.CASCADE)
    ALZACRISTALES_CHOICES = [('NO', 'No'),('2', '2 Puertas'),('4', '4 Puertas')]
    AlzaCristales = models.CharField(max_length=2,choices=ALZACRISTALES_CHOICES,default='NO',verbose_name="Alza Cristales")

    def __str__(self):
        return f"Equipamiento ID: {self.id}"
 
 
class InspeccionCubiertas(models.Model):
    formato_cubiertas_validator = RegexValidator(regex=r'^\d{3}/\d{2}R\d{2}$',message="El formato de las medidas debe ser '000/00R00'.")
    MARCA_CHOICES = [('Bridgestone ', 'Bridgestone '),('Continental ', 'Continental'),('Pirelli', 'Pirelli'),('Kumho', 'Kumho'),('Good year', 'Good year'),('Fate', 'Fate'),('Firestone', 'Firestone'),('Dunlop', 'Dunlop'),('Michelin', 'Michelin'),('Hankook', 'Hankook'),('Otras', 'Otras')]
    VIDA_UTIL_CHOICES = [('0% ', '0% '),('25% ', '25% '),('50% ', '50% '),('75% ', '75% '),('100% ', '100% ')]
    # Cubierta delantera derecha
    marca_delantera_derecha = models.CharField(max_length=50,choices=MARCA_CHOICES,default=False)
    medidas_delantera_derecha = models.CharField(max_length=50, validators=[formato_cubiertas_validator])
    vida_util_delantera_derecha =  models.CharField(max_length=50,choices=VIDA_UTIL_CHOICES,default=False)
    gastos_delantera_derecha = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Cubierta delantera izquierda
    marca_delantera_izquierda = models.CharField(max_length=50,choices=MARCA_CHOICES,default=False)
    medidas_delantera_izquierda = models.CharField(max_length=50, validators=[formato_cubiertas_validator])
    vida_util_delantera_izquierda =  models.CharField(max_length=50,choices=VIDA_UTIL_CHOICES,default=False)
    gastos_delantera_izquierda = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Cubierta trasera derecha
    marca_trasera_derecha = models.CharField(max_length=50,choices=MARCA_CHOICES,default=False)
    medidas_trasera_derecha = models.CharField(max_length=50, validators=[formato_cubiertas_validator])
    vida_util_trasera_derecha =  models.CharField(max_length=50,choices=VIDA_UTIL_CHOICES,default=False)
    gastos_trasera_derecha = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Cubierta trasera izquierda
    marca_trasera_izquierda = models.CharField(max_length=50,choices=MARCA_CHOICES,default=False)
    medidas_trasera_izquierda = models.CharField(max_length=50, validators=[formato_cubiertas_validator])
    vida_util_trasera_izquierda =  models.CharField(max_length=50,choices=VIDA_UTIL_CHOICES,default=False)
    gastos_trasera_izquierda = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    # Cubierta de auxilio
    marca_auxilio = models.CharField(max_length=50,choices=MARCA_CHOICES,default=False,  blank=True, null=True)
    medidas_auxilio = models.CharField(max_length=50, validators=[formato_cubiertas_validator],  blank=True, null=True)
    vida_util_auxilio =  models.CharField(max_length=50, choices=VIDA_UTIL_CHOICES,blank=True, null=True,default=False)
    gastos_auxilio = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    peritaje = models.ForeignKey(Peritaje, on_delete=models.CASCADE)
    
    observaciones_cubiertas = models.TextField(verbose_name="Observaciones Cubiertas", blank=True)
    
    def __str__(self):
        return f"Información de las cubiertas del vehículo"

    class Meta:
        verbose_name_plural = "Inspecciones de Cubiertas"


# MARCA DE LA IMAGEN
class Marca(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    letra = models.CharField(max_length=10, default='P')
    
    def str(self):
        return f"Marca {self.letra} en ({self.x}, {self.y})"
    
# IMAGEN MARCADA
class ImagenMarcada(models.Model):
    nombre = models.CharField(max_length=255)
    ruta = models.CharField(max_length=255)
    peritaje = models.ForeignKey(Peritaje, on_delete=models.CASCADE)
    observaciones = models.TextField(verbose_name="Observaciones", blank=True)
    
# INSPECCION GENERAL
class InspeccionGral(models.Model):
    
    OPCIONES_CARROCERIA = [('NO','NO'),('B','B'),('R','R'),('M','M')]
    carroceria_general = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    carroceria_general_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    chapa = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    chapa_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pintura = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    pintura_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    motor = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    motor_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    diferencial = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    diferencial_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    embrague = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    embrague_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tren_delantero = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    tren_delantero_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tren_trasero = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    tren_trasero_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    direccion = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    direccion_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    frenos = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    frenos_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amortiguadores_tras = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    amortiguadores_tras_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amortiguadores_del = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    amortiguadores_del_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    arranque = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    arranque_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    radiadores = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    radiadores_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    electricidad = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    electricidad_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    aacc_calefaccion = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    aacc_calefaccion_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    radio = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    radio_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bateria = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    bateria_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    llantas = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    llantas_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tasas = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    tasas_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    parabrisas = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    parabrisas_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    asientos = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    asientos_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    tapizado = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    tapizado_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    volante = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    volante_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    freno_de_mano = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    freno_de_mano_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    bagueta = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    bagueta_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    moldura = models.CharField(max_length=2,choices=OPCIONES_CARROCERIA,default='')
    moldura_gasto = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    observaciones_gral = models.TextField(verbose_name="ObservacionesGral", blank=True)
    
    peritaje = models.ForeignKey(Peritaje, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Inspección general"
    
#  GASTOS TOTAL   
class Gastos_total(models.Model):
        total_gastos = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True)
        valor_mercado = models.DecimalField(max_digits=10, decimal_places=2)
        precio_info_auto = models.DecimalField(max_digits=10, decimal_places=2)
        precio_valor_toma = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
        peritaje = models.ForeignKey(Peritaje, on_delete=models.CASCADE)
        
        
class Cambios(models.Model):
    fecha_cambio = models.DateTimeField(verbose_name="Fecha de Cambios")
    peritaje_cambio = models.ForeignKey(Peritaje, on_delete=models.CASCADE)
    usuario_cambio = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)