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

async function parseLine(line){
    var job_sent_to_slurm_regex = /Job [0-9]+ sent to slurm system/;
    var job_finished_from_slurm_regex = /Job [0-9]+ status is COMPLETE/;
    var new_combination_regex = /Working on (.)+ combination/;
    var total_combinations_regex = /[0-9]+ combinations in total/;
    var speedup_regex = /final results speedup is [+-]?([0-9]*[.])?[0-9]+/;
    var found_job_sent_to_slurm = line.match(job_sent_to_slurm_regex);
    var found_job_finished_from_slurm = line.match(job_finished_from_slurm_regex);
    var found_new_combination = line.match(new_combination_regex);
    var found_total_combinations = line.match(total_combinations_regex);
    var found_speedup = line.match(speedup_regex);

    if (found_job_sent_to_slurm){
        var job_id = found_job_sent_to_slurm[0].replace(/[^0-9]/g,'');
        console.log("job sent to slurm:", job_id);
        slurmJobs.add(job_id);
    }
    else if (found_job_finished_from_slurm){
        var job_id = found_job_finished_from_slurm[0].replace(/[^0-9]/g,'');
        console.log("job sent to slurm:", job_id);
        slurmJobs.delete(job_id);
    }
    else if (found_new_combination){
        ranCombination += 1;
        console.log("new combination is running, total:", ranCombination);
        // update here progress bar
    }
    else if (found_total_combinations){
        totalCombinationsToRun = found_total_combinations[0].replace(/[^0-9]/g,'');
        console.log("total combination to run:", totalCombinationsToRun);
        // update here progress bar
    }
    else if (found_speedup){
        speedup = parseFloat(found_speedup[0].split(" ")[found_speedup[0].split(" ").length-1]);
        console.log("speedup is:", speedup)
        // call here to show speedup on screen
    }

}

async function run() {
  if (!comparIsRunning){
      output.innerHTML = "";
      comparIsRunning = true;
      totalJobs = 0;
      ranJobs = 0;
      slurmJobs = new Set();
      var codeMirrorResultEditor = $('.CodeMirror')[1].CodeMirror;
      var codeMirrorSourceEditor = $('.CodeMirror')[0].CodeMirror;
      codeMirrorSourceEditor.setOption("readOnly", true)
      codeMirrorResultEditor.setValue("Compar in progress ...");
      codeMirrorResultEditor.refresh();
      startComparButton.disabled = true;
      browse_button.disabled = true;
      download_button.disabled = true;

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
      codeMirrorSourceEditor.setOption("readOnly", false)
      startComparButton.disabled = false;
      browse_button.disabled = false;
      download_button.disabled = false;
  }
}
