function Upload_file(fileId, textAreaId) {
        var file = document.getElementById(fileId).files[0];
        var code_mirror_source_editor = $('.CodeMirror')[0].CodeMirror;
        if(file){
            var reader = new FileReader();
            reader.readAsText(file, "UTF-8");
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

 upload_source_file.onchange = function(){
    Upload_file('upload_source_file','source_file_code');
}