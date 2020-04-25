function Upload_file(fileId, textAreaId) {
        var file = document.getElementById(fileId).files[0];
        var code_mirror_source_editor = $('.CodeMirror')[0].CodeMirror;
        if(file){
            console.log("js file test " + file.name);
            var reader = new FileReader();
            reader.readAsText(file, "UTF-8");
             console.log("upload file function");
             reader.onload = function (evt) {
                document.getElementById('source_editor').innerHTML = evt.target.result;
                code_mirror_source_editor.setValue(evt.target.result);
                code_mirror_source_editor.refresh();
             }
             reader.onerror = function (evt) {
                document.getElementById('source_editor').innerHTML = "Error reading file!";
                code_mirror_source_editor.setValue("Error reading file!");
                code_mirror_source_editor.refresh();
             }
         }
    }

function downloadFile(){
    var codeMirrorResultEditor = $('.CodeMirror')[1].CodeMirror;
    resultCode = codeMirrorResultEditor.getValue();
    if (resultCode && !comparIsRunning){
        var anchor=document.createElement('a');
        anchor.setAttribute('href',"/downloadResultFile");
        anchor.setAttribute('download','');
        document.body.appendChild(anchor);
        anchor.click();
        anchor.parentNode.removeChild(anchor);
    }
 }

 upload_source_file.onchange = function(){
    console.log("upload file on change triggered");
    Upload_file('upload_source_file','source_file_code');
}