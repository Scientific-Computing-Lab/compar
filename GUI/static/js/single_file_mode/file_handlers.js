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

function downloadFile(){
    var codeMirrorResultEditor = $('.CodeMirror')[1].CodeMirror;
    resultCode = codeMirrorResultEditor.getValue();

    var comparStatusCode = 0;
    var url = "/checkComparStatus"
      fetch(url)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
          if(data['success'] === 1){
             comparStatusCode = 1;
          }
          else if(data['success'] === 0){
            comparStatusCode = 0;
          }
       });


    if (resultCode && comparStatusCode && !comparIsRunning){
        var anchor=document.createElement('a');
        anchor.setAttribute('href',"/downloadResultFile");
        anchor.setAttribute('download','');
        document.body.appendChild(anchor);
        anchor.click();
        anchor.parentNode.removeChild(anchor);
    }
 }

 upload_source_file.onchange = function(){
    Upload_file('upload_source_file','source_file_code');
}