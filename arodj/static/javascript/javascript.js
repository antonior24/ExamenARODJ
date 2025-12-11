// que solamente al entrar a la pagina me pida si quiero entrar o no
window.onload = function() {
    // Si ya contestó antes, no preguntamos más
    if (localStorage.getItem("accesoPermitido") === "true") {
        return;
    }

    let aceptar = confirm("¿Desea entrar en la página?");
    if (!aceptar) {
        window.location.href = "https://www.google.com";
    } else {
        // Guardamos que ya aceptó
        localStorage.setItem("accesoPermitido", "true");
    }
}

function eliminar() {
    var x = confirm("¿Está seguro de que desea eliminar este producto?");
    if (x)
        return true;
    else
        return false;
}
