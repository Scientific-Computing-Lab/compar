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
    if (comparIsRunning){
     const response = await fetch('/terminateCompar', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify ({'jobs': Array.from(slurmJobs)})
      });
    }
 }

 function updateProgressBar (percentage) {
    progress = document.getElementById("progress_run");
    progress.style.width = percentage;

    info = document.getElementById("percentage");
    info.innerHTML = percentage + "%";
 }

 function showSpeedup (speedup) {
    window = document.getElementById("run-progress");
    var speed = document.createElement('div');
    path.innerHTML += "Speedup Gained: speedup";
    path.style.marginTop = '12px';
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
        console.log("job finished from slurm:", job_id);
        slurmJobs.delete(job_id);
    }
    else if (found_new_combination){
        ranCombination += 1;
        console.log("new combination is running, total:", ranCombination);
        var percentage = totalCombinationsToRun / ranCombination;
        updateProgressBar(percentage);
    }
    else if (found_total_combinations){
        totalCombinationsToRun = found_total_combinations[0].replace(/[^0-9]/g,'');
        console.log("total combination to run:", totalCombinationsToRun);
        updateProgressBar(0);
    }
    else if (found_speedup){
        speedup = parseFloat(found_speedup[0].split(" ")[found_speedup[0].split(" ").length-1]);
        console.log("speedup is:", speedup)
        showSpeedup(speedup);
    }
}

