var comparIsRunning = false;

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

      var url = "/showFilesStructure"
      fetch(url)
      .then((response) => {
        return response.json();
      })
      .then((data) => {
        document.getElementById("outputFolder").innerHTML = data['text'];
      });

      comparIsRunning = false;
      startComparButton.disabled = false;
  }
}
