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
      totalCombinationsToRun = 0;
      ranCombination = 0;
      speedup = 0;
      slurmJobs = new Set();
      document.getElementById("outputFolder").innerHTML = "Compar in progress ...";
      startComparButton.disabled = true;
      progress_bar = document.getElementById("progress_bar");
      progress_bar.style.display = 'flex';
      speedup = document.getElementById("speed_up");
      speedup.style.display = 'none';
      run_progress = document.getElementById("run_progress");
      run_progress.style.height = "100%";
      resetProgressBar();

      for await (let line of makeTextFileLineIterator("stream_progress")) {
                parseLine(line);
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
          document.getElementById("outputFolder").innerHTML = "";
          if(data['success'] === 1)
          {
              var message = document.createElement('div');
              message.innerHTML += data['text'];
              message.classList.add('success');

              var result = document.createElement('div');
              result.classList.add('flex-row');
              result.style.marginTop= '12px';
              result.style.alignItems = 'center';

              var directoryImage = document.createElement('img');
              directoryImage.setAttribute('src', "/static/assets/directory.png");
              directoryImage.setAttribute('alt', 'NA');
              directoryImage.height = '35';
              directoryImage.width = '35';

              var path = document.createElement('div');
              path.innerHTML += data['path'];
              path.classList.add('result-path');
              path.style.marginLeft = '12px';

              result.appendChild(directoryImage);
              result.appendChild(path);

              document.getElementById("outputFolder").appendChild(message);
              document.getElementById("outputFolder").appendChild(result);
          }
          else
          {
              var message = document.createElement('div');
              message.innerHTML += data['text'];
              message.classList.add('fail');

              var directoryImage = document.createElement('img');
              directoryImage.setAttribute('src', "/static/assets/sad.png");
              directoryImage.setAttribute('alt', 'NA');
              directoryImage.height = '35';
              directoryImage.width = '35';

              document.getElementById("outputFolder").appendChild(message);
              document.getElementById("outputFolder").appendChild(directoryImage);

          }
      });
      comparIsRunning = false;
      startComparButton.disabled = false;
  }
}
