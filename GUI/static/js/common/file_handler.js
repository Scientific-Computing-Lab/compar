async function downloadFile(action){
    var codeMirrorResultEditor = $('.CodeMirror')[1].CodeMirror;
    resultCode = codeMirrorResultEditor.getValue();

    var comparStatusCode = 0;
    var url = "/checkComparStatus";
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify ({'action': action})
      })
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
        anchor.setAttribute('href',"/"+action);
        anchor.setAttribute('download','');
        document.body.appendChild(anchor);
        anchor.click();
        anchor.parentNode.removeChild(anchor);
    }
 }

async function terminateCompar(){
    fetch('/terminateCompar');
 }