// *********************************** //
// ** New Experiment Data Variables ** //
// *********************************** //

var expName;
var expDesc;
var trialData;
var configData;
var partData = [];
var partFileNames = [];

(function () {
    // *********************************** //
    // ************ File Upload ********** //
    // *********************************** //
    // getElementById
    function $id(id) {
        return document.getElementById(id);
    }

    // output information
    function Output(msg, place) {
        var m = $id(place);
        m.innerHTML = msg + m.innerHTML;
    }

    // file drag hover
    function FileDragHover(e) {
        e.stopPropagation();
        e.preventDefault();
        e.target.className = (e.type === "dragover" ? "hover" : "");
    }

    // *********************************** //
    // ********* File Drag HTML ********** //
    // *********************************** //
    // file selection
    function HTMLFileSelectHandler(e) {
        // cancel event and hover styling
        FileDragHover(e);
        // fetch FileList object
        var files = e.target.files || e.dataTransfer.files;
        // process all File objects
        for (var i = 0, f; f = files[i]; i++) {
            if (f.type === "text/html") {
                ParseHTMLFile(f);
            }
        }
    }

    // HTML file information
    function ParseHTMLFile(file) {
        //Check File Type for HTML
        // Pass message to Output for display on screen
        Output(
            "<p>HTML File information: <strong>" + file.name + "</p>",
            "HTMLMessages"
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

    // *********************************** //
    // ********* File Drag Config ******** //
    // *********************************** //
    // file selection
    function ConfigFileSelectHandler(e) {

        // cancel event and hover styling
        FileDragHover(e);

        // fetch FileList object
        var files = e.target.files || e.dataTransfer.files;
        // process all File objects
        for (var i = 0, f; f = files[i]; i++) {
            ParseConfigFile(f);
        }
    }

    // output file information
    function ParseConfigFile(file) {
        //Check File Type for HTML or XML
        if (file.type === "text/xml") {
            //If the file is called "config.xml"
            if (file.name === "config.xml") {
                Output(
                    "<p>Config File Name: <strong>" + file.name + "</p>",
                    "ConfigMessages"
                );
                //get the contents of the config.xml file and read it in as a string
                var contents;
                var reader = new FileReader();
                reader.onload = function (e) {
                    contents = e.target.result;
                    configData = contents;
                };
                reader.readAsText(file);
            }
        }
    }

    // *********************************** //
    // **** File Drag Participant ******** //
    // *********************************** //
    // file selection
    function ParticipantFileSelectHandler(e) {
        // cancel event and hover styling
        FileDragHover(e);
        // fetch FileList object
        var files = e.target.files || e.dataTransfer.files;
        // process all File objects
        for (var i = 0, f; f = files[i]; i++) {
            ParseParticipantFiles(f);
        }
    }

    // output file information
    function ParseParticipantFiles(file) {
        //Check File Type for XML and not config
        if (file.type === "text/xml" && file.name !== "config.xml") {
            //Must be participant file
            Output(
                    "<p>Participant File Name: <strong>" + file.name + "</p>",
                    "PartMessages"
                );
            //Multiple participant files available/expected
            //get the contents of the xml file and add it a
            //list to pass all participant data at once as Sttrings
            var contents;
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

    // initialize
    function Init() {
        var textFile = $id("textFile"), textFileDrag = $id("textFileDrag");
        var configFile = $id("configFile"), configFileDrag = $id("configFileDrag");
        var partFiles = $id("partFiles"), partFilesDrag = $id("partFilesDrag");

        // file select
        textFile.addEventListener("change", HTMLFileSelectHandler, false);
        configFile.addEventListener("change", ConfigFileSelectHandler, false);
        partFiles.addEventListener("change", ParticipantFileSelectHandler, false);

        // is XHR2 available?
        var xhr = new XMLHttpRequest();
        if (xhr.upload) {
            // file drop XML
            textFileDrag.addEventListener("dragover", FileDragHover, false);
            textFileDrag.addEventListener("dragleave", FileDragHover, false);
            textFileDrag.addEventListener("drop", HTMLFileSelectHandler, false);
            textFileDrag.style.display = "block";

            configFileDrag.addEventListener("dragover", FileDragHover, false);
            configFileDrag.addEventListener("dragleave", FileDragHover, false);
            configFileDrag.addEventListener("drop", ConfigFileSelectHandler, false);
            configFileDrag.style.display = "block";

            partFilesDrag.addEventListener("dragover", FileDragHover, false);
            partFilesDrag.addEventListener("dragleave", FileDragHover, false);
            partFilesDrag.addEventListener("drop", ParticipantFileSelectHandler, false);
            partFilesDrag.style.display = "block";
        }
    }

    // call initialization file
    if (window.File && window.FileList && window.FileReader) {
        Init();
    }
})();

// When page is loaded
$(document).ready(function () {


});
