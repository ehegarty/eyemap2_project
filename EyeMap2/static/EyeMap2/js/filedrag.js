var trialData;
var configData;
var partData = [];
var partFileNames = [];

(function () {

    // getElementById
    function $id(id) {
        return document.getElementById(id);
    }

    // output information
    function Output(msg) {
        var m = $id("messages");
        m.innerHTML = msg + m.innerHTML;
    }

    // file drag hover
    function FileDragHover(e) {
        e.stopPropagation();
        e.preventDefault();
        e.target.className = (e.type === "dragover" ? "hover" : "");
    }

    // file selection
    function FileSelectHandler(e) {

        // cancel event and hover styling
        FileDragHover(e);

        // fetch FileList object
        var files = e.target.files || e.dataTransfer.files;
        // process all File objects
        for (var i = 0, f; f = files[i]; i++) {
            ParseFile(f);
        }

    }

    // output file information
    function ParseFile(file) {
        //Check File Type for HTML or XML
        if (file.type === "text/html") {
            // Pass message to Output for display on screen
            Output(
                "<p>HTML File information: <strong>" + file.name +
                "</strong> type: <strong>" + file.type +
                "</strong> size: <strong>" + file.size +
                "</strong> bytes</p>"
            );
            //get the contents of the HTML file and read it in as a string
            var contents;
            var reader = new FileReader();
            reader.onload = function (e) {
                contents = e.target.result;
                trialData = contents;
            };
            reader.readAsText(file);
        }
        if (file.type === "text/xml") {
            //If the file is called "config.xml"
            if (file.name === "config.xml") {
                Output(
                    "<p>Config File information: <strong>" + file.name +
                    "</strong> type: <strong>" + file.type +
                    "</strong> size: <strong>" + file.size +
                    "</strong> bytes</p>"
                );
                //get the contents of the config.xml file and read it in as a string
                var reader = new FileReader();
                reader.onload = function (e) {
                    contents = e.target.result;
                    configData = contents;
                };
                reader.readAsText(file);
            }
            else {
                //Must be participant file
                Output(
                    "<p>XML File information: <strong>" + file.name +
                    "</strong> type: <strong>" + file.type +
                    "</strong> size: <strong>" + file.size +
                    "</strong> bytes</p>"
                );
                //Multiple participant files available/expected
                //get the contents of the xml file and add it a
                //list to pass all participant data at once as Sttrings
                var partID = (file.name).substring(0, 2);
                var reader = new FileReader();
                reader.onload = function (e) {
                    contents = e.target.result;
                    partData[Number(partID)] = contents;
                    partFileNames[Number(partID)] = file.name;
                };
                reader.readAsText(file);
            }
        }
    }

    // initialize
    function Init() {
        var fileselect = $id("fileselect"),
            filedrag = $id("filedrag");

        // file select
        fileselect.addEventListener("change", FileSelectHandler, false);
        fileselect.addEventListener("change", FileSelectHandler, false);

        // is XHR2 available?
        var xhr = new XMLHttpRequest();
        if (xhr.upload) {

            // file drop XML
            filedrag.addEventListener("dragover", FileDragHover, false);
            filedrag.addEventListener("dragleave", FileDragHover, false);
            filedrag.addEventListener("drop", FileSelectHandler, false);
            filedrag.style.display = "block";
        }
    }

    // call initialization file
    if (window.File && window.FileList && window.FileReader) {
        Init();
    }
})();

