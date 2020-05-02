var binaryCompilerFlags = new Map();
var slurmParametersList = new Map();
var mainFileParamList = new Map();
var makefileCommands = new Map();
var ignoreFoldersList = new Map();
var includeFoldersList = new Map();
var extraFilesPathsList = new Map();

var mapsWithApostrophes = [
    'binaryCompilerFlags',
    'slurmParametersList',
    'makefileCommands',
    'ignoreFoldersList',
    'includeFoldersList',
    'extraFilesPathsList'
]

var mapDictionary = {
    'binaryCompilerFlags': binaryCompilerFlags,
    'slurmParametersList': slurmParametersList,
    'mainFileParamList': mainFileParamList,
    'makefileCommands': makefileCommands,
    'ignoreFoldersList': ignoreFoldersList,
    'includeFoldersList': includeFoldersList,
    'extraFilesPathsList': extraFilesPathsList
}

function addItem(mapName, inputName, divName){
    var input = document.getElementById(inputName);
    value = input.value;
    input.value = "";
    if(value !== "")
    {
        var itemId = Date.now();
        mapDictionary[mapName].set(itemId, value);
        appendChilds(mapName, divName);
        updateItem(mapName);
    }
}

function removeItem(mapName, itemId, divName) {
    mapDictionary[mapName].delete(itemId);
    appendChilds(mapName, divName);
    updateItem(mapName);
}

function createChild(mapName, itemId, value, divName) {
    var containerDiv = document.createElement("div");
    containerDiv.classList.add("flex-row");

    var innerDiv = document.createElement("div");
    innerDiv.innerHTML = value;
    innerDiv.style.width = '210px';
    innerDiv.style.overflow = 'scroll';
    innerDiv.style.margin = '2px 0px';

    var innerButton = document.createElement("button");
    innerButton.innerHTML = "-";
    innerButton.classList.add("mybutton");
    innerButton.classList.add("negative");
    innerButton.onclick = function(){ removeItem(mapName, itemId, divName) };
    innerButton.setAttribute('type', 'button');

    containerDiv.appendChild(innerDiv);
    containerDiv.appendChild(innerButton);

    return containerDiv;
}

function appendChilds(mapName, divName){
    var dynamicList = document.getElementById(divName);
    dynamicList.innerHTML = '';
    for(var [itemId, value] of mapDictionary[mapName]){
       var child = createChild(mapName, itemId, value, divName);
       dynamicList.appendChild(child);
    }
}

function updateItem(mapName){
    mapValuesArray = Array.from(mapDictionary[mapName].values())
    if (mapsWithApostrophes.includes(mapName)){
        mapValuesArray = mapValuesArray.map(x => "'" + x + "'")
    }
    arrayAsText = Array.from(mapValuesArray).join(' ');
    document.getElementById(mapName).value = arrayAsText;
}
