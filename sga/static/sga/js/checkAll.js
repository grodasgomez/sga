
/**
 * Funcion que permite seleccionar todos los checkbox de un formulario,
 * se necesita un checkbox con id "checkAll" para que funcione.
 */
document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = [...document.querySelectorAll('input[type="checkbox"]:not(#check-all)')];
    const checkAll = document.getElementById('check-all');
    const areAllChecked = checkboxes.every((checkbox)=> checkbox.checked)
    checkAll.checked = areAllChecked;

    checkAll.onclick = function() {
        // Obtenemos el valor del checkbox con id "check-all"
        const checked = checkAll.checked;

        // Seleccionamos todos los inputs con type checkbox y seteamos su valor
        for (let checkbox of checkboxes) {
            checkbox.checked = checked;
        }
    };

});
