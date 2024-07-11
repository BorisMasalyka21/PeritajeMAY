// MEDIDAS RODADO 

document.addEventListener('DOMContentLoaded', function() {
  const inputs = document.querySelectorAll('.medida-cubierta');

  inputs.forEach(input => {
      formatMeasures(input);
  });

  function formatMeasures(input) {
      input.addEventListener('input', function(e) {
          let value = e.target.value.replace(/\D/g, ''); 
          let formatted = '';
          if (value.length > 0) formatted += value.substring(0, 3);
          if (value.length > 3) formatted += '/' + value.substring(3, 5);
          if (value.length > 5) formatted += 'R' + value.substring(5, 7);
          e.target.value = formatted;
      });
  }
});



// TELEFONO SOLO ACEPTE NUMERO 
function isNumber(event) {
  var charCode = (event.which) ? event.which : event.keyCode;
  if (charCode > 31 && (charCode < 48 || charCode > 57)) {
      return false;
  }
  return true;
}

//  DESMARCAR CHECK 
document.addEventListener('DOMContentLoaded', function() {
  const allRadios = document.querySelectorAll('input[type="radio"]');
  allRadios.forEach(radio => {
      radio.addEventListener('click', function() {
          let isChecked = this.dataset.checked === 'true';
          if (isChecked) {
              this.checked = false;
              this.dataset.checked = 'false';
          } else {
              this.checked = true;
              this.dataset.checked = 'true';
             
              allRadios.forEach(otherRadio => {
                  if (otherRadio !== this && otherRadio.name === this.name) {
                      otherRadio.dataset.checked = 'false';
                  }
              });
          }
      });
  });
});

// FORMATO PATENTE  
function validatePatente(event) {
  const key = event.key.toUpperCase();
  const input = event.target;
  const value = input.value;
  const regexLetters = /^[A-Z]$/;
  const regexNumbers = /^[0-9]$/;

  if (['ArrowLeft', 'ArrowRight', 'Backspace', 'Delete', 'Tab'].includes(event.key)) {
      return true;
  }
  if (!key.match(/[A-Z0-9]/)) {
      event.preventDefault();
      return false;
  }
  if (value.length < 2 && !key.match(regexLetters)) {
      event.preventDefault(); 
  } else if (value.length === 2 && value.match(/^[A-Z]{2}$/) && !key.match(regexNumbers)) {
      event.preventDefault(); o
  } else if (value.length >= 3 && value.length < 5) {
      if (!key.match(regexNumbers)) {
          event.preventDefault(); 
      }
  } else if (value.length >= 6) {
      if (!key.match(regexLetters)) {
          event.preventDefault();
      }
  }
}


// Cambios 8/7 Primera con mayuscula seguida de minusculas
function capitalizeWords(event) {
  let input = event.target;
  let words = input.value.split(' ');
  for (let i = 0; i < words.length; i++) {
      words[i] = words[i].charAt(0).toUpperCase() + words[i].slice(1).toLowerCase();
  }
  input.value = words.join(' ');
}

document.addEventListener('DOMContentLoaded', (event) => {
    const inputsToFormat = [
        'id_valor_mercado',
        'id_precio_info',
        'id_precio_toma',
    ];
  
    const inputsCubiertas = [
        'id_gastos_delantera_derecha',
        'id_gastos_delantera_izquierda',
        'id_gastos_trasera_izquierda',
        'id_gastos_trasera_derecha',
        'id_gastos_auxilio'
    ];
  
    const inputsPartes = [
        'id_carroceria_general_gasto',
        'id_chapa_gasto',
        'id_pintura_gasto',
        'id_motor_gasto',
        'id_diferencial_gasto',
        'id_embrague_gasto',
        'id_tren_delantero_gasto',
        'id_tren_trasero_gasto',
        'id_direccion_gasto',
        'id_frenos_gasto',
        'id_amortiguadores_tras_gasto',
        'id_amortiguadores_del_gasto',
        'id_arranque_gasto',
        'id_radiadores_gasto',
        'id_electricidad_gasto',
        'id_aacc_calefaccion_gasto',
        'id_radio_gasto',
        'id_bateria_gasto',
        'id_llantas_gasto',
        'id_tasas_gasto',
        'id_parabrisas_gasto',
        'id_asientos_gasto',
        'id_tapizado_gasto',
        'id_volante_gasto',
        'id_freno_de_mano_gasto',
        'id_bagueta_gasto',
        'id_moldura_gasto'
    ];
  
    const subTotalCubiertasInput = document.getElementById('sub_total_cubiertas');
    const subTotalPartesInput = document.getElementById('sub_total_partes');
    const totalGastosInput = document.getElementById('totalGastos');
  
    function formatNumber(inputValue) {
        let numericValue = inputValue.replace(/[^\d,]/g, '');
        let parts = numericValue.split(',');
        let integerPart = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        let decimalPart = parts.length > 1 ? ',' + parts[1].substring(0, 2) : '';
        return '$' + integerPart + decimalPart;
    }
  
    function parseFormattedNumber(value) {
        return parseFloat(value.replace(/\./g, '').replace(',', '.').replace('$', '')) || 0;
    }
  
    function updateSubtotal(inputs, outputInput) {
        let subtotal = inputs.reduce((sum, id) => {
            let input = document.getElementById(id);
            return sum + parseFormattedNumber(input.value);
        }, 0);
        outputInput.value = formatNumber(subtotal.toFixed(2).toString().replace('.', ','));
        updateTotalGastos();
    }
  
    function updateTotalGastos() {
        let subTotalCubiertas = parseFormattedNumber(subTotalCubiertasInput.value);
        let subTotalPartes = parseFormattedNumber(subTotalPartesInput.value);
        let total = subTotalCubiertas + subTotalPartes;
        totalGastosInput.value = formatNumber(total.toFixed(2).toString().replace('.', ','));
    }
  
    function addInputListener(id, inputs, outputInput) {
        let input = document.getElementById(id);
        input.addEventListener('input', function() {
            this.value = formatNumber(this.value);
            updateSubtotal(inputs, outputInput);
        });
    }
  
    function addFormattingListener(id) {
        let input = document.getElementById(id);
        input.addEventListener('input', function() {
            let cursorPosition = this.selectionStart;
            let previousLength = this.value.length;
  
            let formattedValue = formatNumber(this.value);
            this.value = formattedValue;
  
            let newLength = formattedValue.length;
            let newCursorPosition = cursorPosition + (newLength - previousLength);
  
            this.setSelectionRange(newCursorPosition, newCursorPosition);
        });
    }
  
    inputsCubiertas.forEach(id => addInputListener(id, inputsCubiertas, subTotalCubiertasInput));
    inputsPartes.forEach(id => addInputListener(id, inputsPartes, subTotalPartesInput));
  
    // Adding formatting listener to the specific inputs
    inputsToFormat.forEach(id => addFormattingListener(id));
  
    // Initial calculation
    updateSubtotal(inputsCubiertas, subTotalCubiertasInput);
    updateSubtotal(inputsPartes, subTotalPartesInput);
  });


//Script Metros
document.addEventListener('DOMContentLoaded', (event) => {
    const handleInputMetros = (event) => {
        let input = event.target;
        let value = input.value.trim();
        if (value.length > 0) {
            input.parentNode.classList.add('input-focus'); // Agregar clase para mostrar el sufijo
        } else {
            input.parentNode.classList.remove('input-focus'); // Quitar clase si el campo está vacío
        }
    };

});

