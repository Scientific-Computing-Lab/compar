function handleErrors(errors){
    console.log("handling errors");
    console.log(errors);
    if(errors && errors.makefile_commands){
        document.getElementById('makefileCommandsAlert').innerHTML = errors.makefile_commands;
    }
    else {
        document.getElementById('makefileCommandsAlert').innerHTML = "";
    }
    if(errors && errors.input_directory){
        document.getElementById('inputDirectoryAlert').innerHTML = errors.input_directory;
    }
    else {
        document.getElementById('inputDirectoryAlert').innerHTML = "";
    }
    if(errors && errors.output_directory){
        document.getElementById('outputDirectoryAlert').innerHTML = errors.output_directory;
    }
    else {
        document.getElementById('outputDirectoryAlert').innerHTML = "";
    }
    if(errors && errors.main_file_path){
        document.getElementById('mainFileAlert').innerHTML = errors.main_file_path;
    }
    else {
        document.getElementById('mainFileAlert').innerHTML = "";
    }
    if (errors && errors.test_path){
        document.getElementById('validationPathAlert').innerHTML = errors.test_path;
    }
    else{
        document.getElementById('validationPathAlert').innerHTML = "";
    }
    if(errors && errors.slurm_partition){
        document.getElementById('slurmPartitionAlert').innerHTML = errors.slurm_partition;
    }
    else{
        document.getElementById('slurmPartitionAlert').innerHTML = "";
    }
    if( error && erros.executable_path){
        document.getElementById('executablePathAlert').innerHTML = errors.slurm_partition;
    }
    else {
        document.getElementById('executablePathAlert').innerHTML = "";
    }
    if ( error && error.excecutable_file_name ){
        document.getElementById('executableFileName').innerHTML = errors.slurm_partition;
    }
    else {
        document.getElementById('executableFileName').innerHTML = "";
    }
    if ( errors && errors.jobs_count ){
        document.getElementById('jobsCountAlert').innerHTML = errors.slurm_partition;
    }
    else {
        document.getElementById('jobsCountAlert').innerHTML = "";
    }
}

$(document).ready(function() {
    $('form').submit(function (e) {
        var url = "/makefile_submit"; // send the form data here.
        if(!comparIsRunning){
            submitForm(url);
        }
        e.preventDefault(); // block the traditional submission of the form.
    });
});

function submitForm(url){
console.log($('form').serialize());
var formData = new FormData($('#form')[0]);
$.ajax({
            type: "POST",
            url: url,
            contentType: false,
            processData: false,
            data: formData, // serializes the form's elements.
            success: function (data) {
                console.log("received: ")
                console.log(data)  // display the returned data in the console.
            },
            error: function(error){
                console.log("received errors: ")
                console.log(error)
            }
        })
        .done(function(data) {
            handleErrors(data.errors);
            if(!data.errors){
                run();
            }
        });

    // Inject our CSRF token into our AJAX request.
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", "{{ form.csrf_token._value() }}")
            }
        }
    })
}