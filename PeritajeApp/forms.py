from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from .models import Branch, CochePeritaje, Equipamiento, FotoPeritaje, InspeccionCubiertas, InspeccionGral, ClientePeritar, Vendedor, Gastos_total, ImagenMarcada, Unidad_negocio, MarcaAuto
from django.contrib.auth.forms import AuthenticationForm

class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ('__all__')
 
        
class CustomAuthenticationForm(AuthenticationForm):
    pass


class CustomUserCreationForm(UserCreationForm):
    group = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=True,
        label="Group"
    )
    
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all(),
        required=True,
        label="Sucursal",
    )

    password1 = forms.CharField(widget=forms.HiddenInput(), required=False)
    password2 = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'branch', 'group')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            group = self.cleaned_data['group']
            user.groups.add(group)
            branch = self.cleaned_data.get('branch')
            if branch:
                user.branch = branch
            user.save()
        return user





class UnidadForm(forms.ModelForm):
    class Meta:
        model = Unidad_negocio
        fields =  ('__all__')

# MARCA
class MarcaAutoForm(forms.ModelForm):
    class Meta:
        model: MarcaAuto
        fields = '__all__'
        widgets = {
            'marca_auto': forms.Select(attrs={'class': 'form-control'}),
        }
        
# COCHEPERITAJE         
class CochePeritajeForm(forms.ModelForm):
    class Meta:
        model = CochePeritaje
        fields = '__all__'
        exclude = ['peritaje']
        widgets = {
            'fecha_tasacion': forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date','class': 'form-control', 'style': 'font-size: 13px !important;'}),
            'fecha_recepcion': forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date','class': 'form-control dark-input', 'readonly onmousedown':'return false', 'style': 'font-size: 13px !important;'}),
            'vto_de_vto_o_itv': forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date','class': 'form-control', 'style': 'font-size: 13px !important;'}),
            'ultimo_service_aceite_fecha': forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date','class': 'form-control', 'style': 'font-size: 13px !important;'}),
            'ultimo_cambio_distribucion_fecha': forms.DateInput(format='%d-%m-%Y', attrs={'type': 'month','class': 'form-control', 'style': 'font-size: 13px !important;'}),
            'gnc_metros': forms.TextInput(attrs={'class': 'form-control gnc-field','onkeypress': 'return isNumber(event)', 'style': 'font-size: 13px !important;',  'id': 'id_gnc_metros', 'placeholder': 'Ej.: 20'}),
            'gnc_generacion': forms.TextInput(attrs={'class': 'form-control gnc-field','onkeypress': 'return isNumber(event)', 'style': 'font-size: 13px !important;', 'placeholder': 'Ej.: 1'}),
            'gnc_vtohidraulica': forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date','class': 'form-control gnc-field','style': 'font-size: 13px !important;'}),
            'gnc_vtooblea': forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date','class': 'form-control gnc-field', 'style': 'font-size: 13px !important;'}),
            'bateria_ultimo_cambio': forms.DateInput(format='%d-%m-%Y', attrs={'type': 'date','class': 'form-control','onchange': "toggleObservaciones()", 'style': 'font-size: 13px !important;'}),
            'es_fecha_original': forms.CheckboxInput(),
            'provincia_Radicado': forms.Select(attrs={'class': 'form-control', 'style': 'font-size: 13px !important;'}),
            'marca': forms.Select(attrs={'class': 'form-control', 'style': 'font-size: 13px !important;'}),
            'puertas': forms.Select(attrs={'class': 'form-control', 'style': 'font-size: 13px !important;'}),
            'vendedor': forms.Select(attrs={'class': 'form-control', 'style': 'font-size: 13px !important;'}),
            'man_aut': forms.Select(attrs={'class': 'form-control', 'style': 'font-size: 13px !important;'}),
            'combustible': forms.Select(attrs={'class': 'form-control combustible-select', 'style': 'font-size: 13px !important;'}),
            'peritador': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 13px !important;'}),
            'receptor': forms.TextInput(attrs={'class': 'form-control dark-input', 'readonly onmousedown':'return false', 'style': 'font-size: 13px !important;'}),
            'patente': forms.TextInput(attrs={'class': 'form-control','placeholder': 'AA000AA / AAA000', 'style': 'text-transform: uppercase; font-size: 13px !important;'}),
            'color': forms.Select(attrs={'class': 'form-control',  'style': 'font-size: 13px !important;'}),
            'año': forms.TextInput(attrs={'class': 'form-control year-input', 'onkeypress': 'return isNumber(event)',  'style': 'font-size: 13px !important;', 'maxlength':'4'}),
            'km': forms.TextInput(attrs={'class': 'form-control', 'onkeypress': 'return isNumber(event)', 'id': 'id_km','oninput':'updateKMVisual(this.value)',  'style': 'font-size: 13px !important;', 'placeholder': 'Ej.: 200'}),
            'dueño_mano': forms.TextInput(attrs={'class': 'form-control', 'onkeypress': 'return isNumber(event)',  'style': 'font-size: 13px !important;', 'placeholder': 'Ej.: 2'}),
            'ultimo_service_aceite_km': forms.TextInput(attrs={'class': 'form-control', 'onkeypress': 'return isNumber(event)',  'style': 'font-size: 13px !important;', 'id': 'id_service_aceite_km', 'placeholder': 'Ej.: 365'}),
            'ultimo_cambio_distribucion_km': forms.TextInput(attrs={'class': 'form-control', 'onkeypress': 'return isNumber(event)' ,'style': 'font-size: 13px !important;', 'id': 'id_cambio_distribucion_km', 'placeholder': 'Ej.: 400'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 13px !important;', 'placeholder': 'Ej.: 208'}),
            'bateria_marca': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 13px !important;', 'placeholder': 'Ej.: Moura'}),
            'bateria_medida': forms.TextInput(attrs={'class': 'form-control','list': 'unidadOptions', 'style': 'font-size: 13px !important;', 'placeholder': 'Ej.: 75Ah'}),
            'unidad_negocio': forms.Select(attrs={'class': 'form-control', 'style': 'font-size: 13px !important;'}),
        }
    def clean_unidad_negocio(self):
        unidad_negocio = self.cleaned_data.get('unidad_negocio')
        if not unidad_negocio:
            self.add_error('unidad_negocio', "Debe seleccionar una unidad de negocio.")
        return unidad_negocio


class EquipamientoForm(forms.ModelForm):
    class Meta:
        model = Equipamiento
        fields = '__all__'
        exclude = ['peritaje']
        widgets = {
            'AlzaCristales': forms.Select(attrs={'class': 'form-control'}),
        }
        
class FotoPeritajeForm(forms.ModelForm):
    class Meta:
        model = FotoPeritaje
        fields = ['foto']
        labels = {
            'foto': 'Foto de peritaje'
        }

    def __init__(self, *args, **kwargs):
        super(FotoPeritajeForm, self).__init__(*args, **kwargs)
        # Establece el campo 'foto' como requerido
        self.fields['foto'].required = True
       

 
        
class InspeccionCubiertasForm(forms.ModelForm):
    class Meta:
        model = InspeccionCubiertas
        fields = '__all__'
        exclude = ['peritaje']
        widgets = {
            'marca_delantera_derecha': forms.Select(attrs={'id': 'id_marca_delantera_derecha', 'class': 'form-control', 'style': 'font-size: 13px !important;'}),
            'marca_delantera_izquierda': forms.Select(attrs={'id': 'id_marca_delantera_izquierda', 'class': 'form-control','style': 'font-size: 13px !important;'}),
            'marca_trasera_derecha': forms.Select(attrs={'id': 'id_marca_trasera_derecha', 'class': 'form-control','style': 'font-size: 13px !important;'}),
            'marca_trasera_izquierda': forms.Select(attrs={'id': 'id_marca_trasera_izquierda', 'class': 'form-control','style': 'font-size: 13px !important;'}),
            'marca_auxilio': forms.Select(attrs={'id': 'id_marca_auxilio', 'class': 'form-control','style': 'font-size: 13px !important;'}),
            'medidas_delantera_derecha': forms.TextInput(attrs={'class': 'form-control medida-cubierta', 'placeholder': '000/00R00','style': 'font-size: 13px !important;'}),
            'medidas_delantera_izquierda': forms.TextInput(attrs={'class': 'form-control medida-cubierta', 'placeholder': '000/00R00','style': 'font-size: 13px !important;'}),
            'medidas_trasera_derecha': forms.TextInput(attrs={'class': 'form-control medida-cubierta', 'placeholder': '000/00R00','style': 'font-size: 13px !important;'}),
            'medidas_trasera_izquierda': forms.TextInput(attrs={'class': 'form-control medida-cubierta', 'placeholder': '000/00R00','style': 'font-size: 13px !important;'}),
            'medidas_auxilio': forms.TextInput(attrs={'class': 'form-control medida-cubierta', 'placeholder': '000/00R00','style': 'font-size: 13px !important;'}),
            'vida_util_auxilio': forms.Select(attrs={'class': 'form-control','id': 'id_vida_util_auxilio', 'placeholder': 'Ej. 87%','oninput':'updatePorcentajeVisualAuxilio(this.value)','style': 'font-size: 13px !important;'}),
            'vida_util_delantera_derecha': forms.Select(attrs={'class': 'form-control ','id': 'id_vida_util_delantera_derecha', 'placeholder': 'Ej. 87%','style': 'font-size: 13px !important;'}),
            'vida_util_delantera_izquierda': forms.Select(attrs={'class': 'form-control ','id': 'id_vida_util_delantera_izquierda', 'placeholder': 'Ej. 87%','style': 'font-size: 13px !important;'}),
            'vida_util_trasera_derecha': forms.Select(attrs={'class': 'form-control ','id': 'id_vida_util_trasera_derecha', 'placeholder': 'Ej. 87%','style': 'font-size: 13px !important;'}),
            'vida_util_trasera_izquierda': forms.Select(attrs={'class': 'form-control','id': 'id_vida_util_trasera_izquierda', 'placeholder': 'Ej. 87%','style': 'font-size: 13px !important;'}),
            'gastos_delantera_derecha': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal','id': 'id_gastos_delantera_derecha', 'placeholder': '$1000','style': 'font-size: 13px !important;'}),
            'gastos_delantera_izquierda': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal','id': 'id_gastos_delantera_izquierda', 'placeholder': '$1000','style': 'font-size: 13px !important;'}),
            'gastos_trasera_izquierda': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal','id': 'id_gastos_trasera_izquierda', 'placeholder': '$1000','style': 'font-size: 13px !important;'}),
            'gastos_trasera_derecha': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal','id': 'id_gastos_trasera_derecha', 'placeholder': '$1000','style': 'font-size: 13px !important;'}),
            'gastos_auxilio': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal','id': 'id_gastos_auxilio', 'placeholder': '$1000','style': 'font-size: 13px !important;'}),
            'observaciones_cubiertas': forms.Textarea(attrs={'class': 'form-control',  'style': 'font-size: 13px !important;'}),
        }
   

class InspeccionGralForm(forms.ModelForm):
    class Meta:
        model = InspeccionGral
        fields = '__all__'
        exclude = ['peritaje']
        widgets = {
            'carroceria_general': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'chapa': forms.Select(attrs={'class': 'form-control','style':  'font-size: 10px !important; padding:0px'}),
            'pintura': forms.Select(attrs={'class': 'form-control','style':  'font-size: 10px !important; padding:0px'}),
            'motor': forms.Select(attrs={'class': 'form-control','style':  'font-size: 10px !important; padding:0px'}),
            'diferencial': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'embrague': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'tren_delantero': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'tren_trasero': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'direccion': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'frenos': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'amortiguadores_tras': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'amortiguadores_del': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'arranque': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'radiadores': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'electricidad': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'aacc_calefaccion': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'radio': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'bateria': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'llantas': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'tasas': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'parabrisas': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'asientos': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'tapizado': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'volante': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'freno_de_mano': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'bagueta': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'moldura': forms.Select(attrs={'class': 'form-control','style': 'font-size: 10px !important; padding:0px'}),
            'carroceria_general_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_carroceria_general_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;','style': 'font-size: 13px !important;'}),
            'chapa_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_chapa_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'pintura_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_pintura_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'motor_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_motor_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'diferencial_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_diferencial_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'embrague_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_embrague_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'tren_delantero_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_tren_delantero_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'tren_trasero_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_tren_trasero_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'direccion_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_direccion_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'frenos_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_frenos_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'amortiguadores_tras_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_amortiguadores_tras_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'amortiguadores_del_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_amortiguadores_del_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'arranque_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_arranque_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'radiadores_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_radiadores_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'electricidad_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_electricidad_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'aacc_calefaccion_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_aacc_calefaccion_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'radio_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_radio_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'bateria_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_bateria_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'llantas_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_llantas_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'tasas_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_tasas_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'parabrisas_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_parabrisas_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'asientos_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_asientos_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'tapizado_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_tapizado_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'volante_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_volante_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'freno_de_mano_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_freno_de_mano_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'bagueta_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_bagueta_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'moldura_gasto': forms.TextInput(attrs={'class': 'form-control gasto-input gasto-subtotal2','id':'id_moldura_gasto', 'placeholder':'$1000','style': 'font-size: 13px !important;'}),
            'observaciones_gral': forms.Textarea(attrs={'class': 'form-control',  'style': 'font-size: 13px !important;'}),
        }
        
# VENDEDOR    
class VendedorForm(forms.ModelForm):
    class Meta:
        model: Vendedor
        fields = '__all__'
        widgets = {
            'vendedor': forms.Select(attrs={'class': 'form-control'}),
        }
        
class ImagenMarcadaForm(forms.ModelForm):
    class Meta:
        model: ImagenMarcada
        fields = '__all__'
        exclud   = ['peritaje']
        
class Gastos_totalForm(forms.ModelForm):
    class Meta:
        model = Gastos_total
        fields = '__all__'  # Asegúrate de que todos los campos excepto 'peritaje' estén incluidos
        exclude = ['peritaje']  # Excluyendo 'peritaje' como ya lo has definido
        widgets = {
            'total_gastos': forms.TextInput(attrs={'class': 'form-control', 'id': 'totalGastos', 'onkeypress': 'return isNumber(event)', 'readonly onmousedown':'return false'}),
            'valor_mercado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Valor del mercado','id':'id_valor_mercado'}),
            'precio_info_auto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Precio InfoAuto','id':'id_precio_info'}),
            'precio_valor_toma': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Precio del Valor de Toma','id':'id_precio_toma'}),
        }
        
class ClientePeritarForm(forms.ModelForm):
    class Meta:
        model = ClientePeritar
        fields = '__all__'
        exclude = ['peritaje']
        widgets = {
            'nombre_apellido_entrega': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 13px !important;','oninput': 'capitalizeWords(event)','onblur': 'capitalizeWords(event)',}),
            'telefono_entrega': forms.TextInput(attrs={'class': 'form-control telefono_duenio', 'placeholder': 'Ej.: 54 9 (XXX) XXX XXXX','onkeypress': 'return isNumberKey(event)',  'oninput': 'formatArgentinianPhone(this)', 'style': 'font-size: 13px !important;'}),
            'nombre_apellido_duenio': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 13px !important;','oninput': 'capitalizeWords(event)','onblur': 'capitalizeWords(event)',}),
            'telefono_duenio': forms.TextInput(attrs={'class': 'form-control telefono_duenio','placeholder': 'Ej.: 54 9 (XXX) XXX XXXX', 'onkeypress': 'return isNumberKey(event)',  'oninput': 'formatArgentinianPhone(this)', 'style': 'font-size: 13px !important;'}),
            'email_entrega': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 13px !important;', 'placeholder': 'Ej.: pedro@gmail.com'}),
            'email_duenio': forms.TextInput(attrs={'class': 'form-control', 'style': 'font-size: 13px !important;', 'placeholder': 'Ej.: pedro@gmail.com'}),
            'cuil_entrega': forms.TextInput(attrs={'class': 'form-control cuil-input', 'style': 'font-size: 13px !important;', 'placeholder':'Ej.: 11-11111111-1'}),
            'cuil_duenio': forms.TextInput(attrs={'class': 'form-control cuil-input', 'style': 'font-size: 13px !important;', 'placeholder':'Ej.: 11-11111111-1'}),
        }
    def clean_email_entrega(self):
        email = self.cleaned_data.get('email_entrega').lower()
        invalid_emails = [
            "noposee@gmail.com",
            "noposee@gmial.com",
            "np@hotmail.com",
            "aconfirmar@gmail.com",
            "ACONFIRMAR@HOTMAIL.COM",
            "ACONFIRMAR@GMAIL.COM",
            "ACONFIIRMAR@GMAIL.COM",
            "ACONFIRMA@HOTMAIL.COM",
            "aconfirmar@hotmail.com",
            "noposee@hotmail.com",
            "NOPOSEE@HOTMAIL.COM",
            "NOPOSEE@gmail.com",
            "NOPOSEE@NOPOSEE.COM",
            "[No Posee]",
            "notiene@notiene.com.ar",
            "notiene@notiene.com",
            "1234@1234.com.ar",
            "123@123.com",
            "aaa@aaa.com.ar"
        ]
        if email in invalid_emails:
            self.add_error('email_entrega', "Por favor, ingrese un correo electrónico válido.")
        return email
        
