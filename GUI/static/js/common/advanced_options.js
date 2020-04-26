var showAdvanced = false;

function showAdvancedOptions() {
    showAdvanced = !showAdvanced;
    var advanced = document.getElementById('advanced');
    if(showAdvanced){
        advanced.style.display = "flex";
    }
    else{
        advanced.style.display = "none";
    }
}

function addParameter(inputId, textAreaId) {
    var paramsInput = document.getElementById(inputId);
    var params = document.getElementById(textAreaId);
    if(params.innerHTML === ''){
        params.innerHTML += paramsInput.value;
    }
    else{
       params.innerHTML += ' ' + paramsInput.value;
    }

}

function removeParameter(textAreaId) {
    var params = document.getElementById(textAreaId);
    var p = params.value.split(' ');
    p.pop();
    params.innerHTML = p.join(' ');
}