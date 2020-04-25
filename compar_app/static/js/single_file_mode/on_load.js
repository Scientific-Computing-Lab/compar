function init() {

    var code_mirror_source_editor = CodeMirror.fromTextArea(document.getElementById('source_editor'), {
        mode: "clike",
        theme: "dracula",
        lineNumbers: true,
        autoCloseBrackets: true
    });

    var code_mirror_result_editor = CodeMirror.fromTextArea(document.getElementById('result_editor'), {
        mode: "clike",
        theme: "dracula",
        lineNumbers: true,
        autoCloseBrackets: true,
        readOnly: true
    });

    var singleModNav = document.getElementById('singlemod');
    singleModNav.style.color = "white";
    singleModNav.style.fontWeight = "bold";
    singleModNav.style.fontSize = "18px";
    singleModNav.style.textDecoration = "underline"
    code_mirror_source_editor.on("change",function(cm,change){
        source_editor.value = code_mirror_source_editor.getValue();
    });

}
