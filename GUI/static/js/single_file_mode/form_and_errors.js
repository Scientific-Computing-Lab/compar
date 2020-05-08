function handleErrors(errors){
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
    if ( errors && errors.jobs_count){
        document.getElementById('jobsCountAlert').innerHTML = errors.jobs_count;
    }
    else {
        document.getElementById('jobsCountAlert').innerHTML = "";
    }
    if ( errors && errors.multiple_combinations){
        document.getElementById('multipleCombinationsAlert').innerHTML = errors.multiple_combinations;
    }
    else {
        document.getElementById('multipleCombinationsAlert').innerHTML = "";
    }
}

$(document).ready(function() {
    $('form').submit(function (e) {
        var url = "/single_file_submit"; // send the form data here.
        if(!comparIsRunning){
            source_editor.innerHTML = ($('.CodeMirror')[0].CodeMirror).getValue();
            submitForm(url);
        }
        e.preventDefault(); // block the traditional submission of the form.
    });
});

function submitForm(url){
var formData = new FormData($('#form')[0]);
$.ajax({
            type: "POST",
            url: url,
            contentType: false,
            processData: false,
            data: formData, // serializes the form's elements.
            success: function (data) {
            },
            error: function(error){
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