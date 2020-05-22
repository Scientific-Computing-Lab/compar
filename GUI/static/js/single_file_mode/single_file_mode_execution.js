var comparIsRunning = false;
var totalCombinationsToRun = 0;
var ranCombination = 0;
var speedup = 0;
var slurmJobs = new Set();

async function* makeTextFileLineIterator(fileURL) {
  const utf8Decoder = new TextDecoder('utf-8');
  const response = await fetch(fileURL, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify ({'mode': 'single-file-mode'})
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
      totalCombinationsToRun = 0;
      ranCombination = 0;
      speedup = 0;
      slurmJobs = new Set();
      terminateButton = document.getElementById("terminate_button");
      terminateButton.style.display = 'inline';
      startComparButton = document.getElementById("startComparButton");
      startComparButton.style.display = 'none';
      var codeMirrorResultEditor = $('.CodeMirror')[1].CodeMirror;
      var codeMirrorSourceEditor = $('.CodeMirror')[0].CodeMirror;
      codeMirrorSourceEditor.setOption("readOnly", true)
      codeMirrorResultEditor.setValue("Compar in progress ...");
      codeMirrorResultEditor.refresh();
      startComparButton.disabled = true;
      browse_button.disabled = true;
      download_button.disabled = true;
      progress_bar = document.getElementById("progress_bar");
      progress_bar.style.display = 'flex';
      speedup = document.getElementById("speed_up");
      speedup.style.display = 'none';
      run_progress = document.getElementById("run_progress");
      run_progress.style.height = "auto";
      resetProgressBar();

      for await (let line of makeTextFileLineIterator("stream_progress")) {
            parseLine(line);
            var item = document.createElement('li');
            item.textContent = line;
            output.appendChild(item);
      }

      var url = "/result_file"
      fetch(url)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        var codeMirrorResultEditor = $('.CodeMirror')[1].CodeMirror;
        codeMirrorResultEditor.setValue(data.text);
        codeMirrorResultEditor.refresh();
      });
      comparIsRunning = false;
      terminateButton.style.display = 'none';
      startComparButton.style.display = 'inline';
      codeMirrorSourceEditor.setOption("readOnly", false)
      startComparButton.disabled = false;
      browse_button.disabled = false;
      download_button.disabled = false;
  }
}
