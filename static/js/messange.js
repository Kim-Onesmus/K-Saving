document.getElementById("#alarmmsg").innerHTML = msg;

setTimeout(function () {
    document.getElementById("#alarmmsg").innerHTML = '';
}, 3000);