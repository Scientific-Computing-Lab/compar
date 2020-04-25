
var comparIsRunning = false;

$(document).ready(function() {
    $('form').submit(function (e) {
        var url = "/multiple_files_submit/"; // send the form data here.
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

async function* makeTextFileLineIterator(fileURL) {
  const utf8Decoder = new TextDecoder('utf-8');
  const response = await fetch(fileURL, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify ({'mode': 'multiple-files-mode'})
  });
  const reader = response.body.getReader();
  let { value: chunk, done: readerDone } = await reader.read();
  chunk = chunk ? utf8Decoder.decode(chunk) : '';

  const re = /\n|\r|\r\n/gm;
  let startIndex = 0;
  let result;

  for (;;) {
    let result = re.exec(chunk);
    if (!result) {
      if (readerDone) {
        break;
      }
      let remainder = chunk.substr(startIndex);
      ({ value: chunk, done: readerDone } = await reader.read());
      chunk = remainder + (chunk ? utf8Decoder.decode(chunk) : '');
      startIndex = re.lastIndex = 0;
      continue;
    }
    yield chunk.substring(startIndex, result.index);
    startIndex = re.lastIndex;
  }
  if (startIndex < chunk.length) {
    // last line didn't end in a newline char
    yield chunk.substr(startIndex);
  }
}

async function run() {
  if (!comparIsRunning){
      output.innerHTML = "";
      comparIsRunning = true;
      startComparButton.disabled = true;

      for await (let line of makeTextFileLineIterator("stream_progress")) {
                var item = document.createElement('li');
                item.textContent = line;
                output.appendChild(item);
      }

      var url = "/showFilesStructure/"
      fetch(url)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        console.log(data);
      });

      comparIsRunning = false;
      startComparButton.disabled = false;
  }
}
