/**
 * Created by user on 20/04/2017.
 */

/********* Global Variables **************/
/********* Areas of Interest **************/
var text_data = [];
var all_aois = [];

/********* Font **************/
var exp_font;
var font_family;
var font_size = 0;
var st_h = 0;
var space = 0;
var tempOffset = [];
var leading = 0;

/********* Font Layout **************/
var offset = 700;
var offset_x = 0;
var offset_y = 0;

/********* Fixations **************/
var all_fix_data = [];
var all_sacc_data = [];
var all_drift_data = [];
var sacc_trial_data = [];
var drift_trial_data = [];
var fixations = [];
var fixationsCircles = [];
var sel_fixes = [];
var dur_scale = 0;

// Left Fixations are odd and right fixations are even
var lFixShown = -1;
var rFixShown = -2;
var lMax = 1;
var rMax = 0;


/********* Container/Stage  **************/
var stage;

/*** AOI Layers ***/
var aoiLayer = new Konva.Layer();
var letterAOILayer = new Konva.Layer();


/*** Text Layers ***/
var textLayer = new Konva.Layer();
var letterTextLayer = new Konva.Layer();

var fixLayer = new Konva.Layer();
var mouseLayer = new Konva.Layer();
var con_width = window.innerWidth;
var con_height = window.innerHeight;

/****************** ***********************/
/********* Used for Sorting **************/
/****************** ***********************/
var sortById = function (x, y) {
    return x.id - y.id;
};

var sortByWord = function (x, y) {
    return x.word - y.word;
};

/****************** ***********************/
/********* Shapes for Data **************/
/****************** ***********************/
var Rectangle = function (x, y, textInfo, type) {
    this.left = x-1;
    this.top = y - (leading / 2);
    this.right = x + textInfo.width;
    this.bottom = textInfo.height + leading + (y - (leading / 2));
    this.text = textInfo.text;
    this.x = x;
    this.y = y;
    this.selected = false;
    this.row = textInfo.row;
    this.col = textInfo.col;
    this.word = textInfo.word;
    this.name = "r" + textInfo.row + "c" + textInfo.col;
    this.width = textInfo.width;
    this.height = textInfo.height + leading;
    this.fbAscent = textInfo.fontBoundingBoxAscent;
    this.texttop = textInfo.fontBoundingBoxAscent + y;
    this.type = type;
};

var Circle = function (fix) {
    this.x = fix.x;
    this.y = fix.y;
    this.eye = fix.eye;
    this.st = fix.st;
    this.et = fix.et;
    this.dur = fix.dur;
    this.pupil = fix.pupil;
    this.id = fix.id;
    this.trial = document.getElementById("trials_sel").value - 1;
    this.dur = fix.dur;
    this.blink = fix.blink;
    this.raw = fix.raw;
};

/****************** ***********************/
/********* Change Display Options **************/
/****************** ***********************/
var handleTabChange = function (tab) {
    if (tab === "aoi") {
        window.removeEventListener("keydown", doKeyDown, false);
        var x = document.getElementById("fixOptions");
        if (x.style.display === "block") {
            x.style.display = "none";
        }
        var y = document.getElementById("scanOptions");
        if (y.style.display === "block") {
            y.style.display = "none";
        }
        var lEye = document.getElementById("show_L_eye");
        lEye.checked = false;
        var rEye = document.getElementById("show_R_eye");
        rEye.checked = false;
        var boxes = aoiLayer.find('Rect');
        for (var i = 0; i < boxes.length; i++) {
            boxes[i].listening(true);
        }
        var letterboxes = letterAOILayer.find('Rect');
        for (var i = 0; i < letterboxes.length; i++) {
            letterboxes[i].listening(true);
        }
    }
    if (tab === "fix") {
        window.addEventListener("keydown", doKeyDown, false);
        var x = document.getElementById("fixOptions");
        if (x.style.display === "none") {
            x.style.display = "block";
        }
        var y = document.getElementById("scanOptions");
        if (y.style.display === "block") {
            y.style.display = "none";
        }
    }
    if (tab === "scan") {
        var x = document.getElementById("fixOptions");
        if (x.style.display === "none") {
            x.style.display = "block";
        }
        var y = document.getElementById("scanOptions");
        if (y.style.display === "none") {
            y.style.display = "block";
        }
    }
    if (tab === "fix" || tab === "scan") {
        var rEye = document.getElementById("show_R_eye");
        rEye.checked = true;
        var editing = document.getElementById("editing");
        editing.checked = false;
        //un_merge_aois();
        window.addEventListener("keydown", doKeyDown, false);
        var boxes = aoiLayer.find('Rect');
        for (var i = 0; i < boxes.length; i++) {
            boxes[i].listening(false);
        }
        letterboxes = letterAOILayer.find('Rect');
        for (var i = 0; i < letterboxes.length; i++) {
            letterboxes[i].listening(false);
        }
    }
    if (tab === "playback") {

    }
    drawData(tab);

};

var change_trials = function () {
    un_merge_aois();
    // AOI layers
    aoiLayer.removeChildren();
    letterAOILayer.removeChildren();

    // Text layers
    textLayer.removeChildren();
    letterTextLayer.removeChildren();

    // Fixation layer
    fixLayer.removeChildren();
    get_aois_info();
};
/****************** ***********************/
/********* Set Up for Data **************/
/****************** ***********************/
var process_data = function (html_data, fix_data, sacc_data, drift_data) {
    text_data = html_data;
    getAllAOIData();
    var font_info = text_data[0];
    var trial_sel = document.getElementById("trials_sel");
    for (var i = 1; i <= font_info[0]; i++) {
        var option = document.createElement("option");
        option.text = "" + i;
        trial_sel.add(option);
    }
    trial_sel.value = 1;

    all_fix_data = fix_data;
    all_sacc_data = sacc_data;
    all_drift_data = drift_data;
};

var getAllAOIData = function () {
    all_aois = [];
    //Set up font
    var font_info = text_data[0];
    var font_text = '/static/EyeMap2/fonts/expFonts/' + font_info[font_info.length - 1];
    opentype.load(font_text, function (err, font) {
        if (err) {
            alert('Font could not be loaded: ' + err);
        } else {
            exp_font = font;
            font_family = font_info[2];
            font_size = Number(font_info[3]);
            leading = Number(font_info[4]);
            st_h = get_dimensions('ty', 0, 0, 0).height;
            space = Math.floor(get_dimensions(' ', 0, 0, 0).width);
            setOffset(Number(font_info[5]), Number(font_info[6]));
            for (var i = 0; i < text_data[1].length; i++) {
                var trial_sel = i;
                all_aois.push(prepAOI(text_data[1][trial_sel]));
            }
            get_aois_info();
        }
    });
};

var setOffset = function (xPos, yPos) {
    var x = 0;
    var y = 0;
    if (xPos > offset && yPos > offset) {
        offset_x = xPos - offset;
        x = offset;
        offset_y = yPos - offset;
        y = offset;
    } else {
        x = xPos;
        offset_x = 0;
        y = yPos;
        offset_y = 0;
    }
    tempOffset = [x, y];
};

var get_dimensions = function (text, row, col, wordCount) {
    var ascent = 0;
    var descent = 0;
    var width = 0;
    var scale = 1 / exp_font.unitsPerEm * font_size;
    var glyphs = exp_font.stringToGlyphs(text);
    for (var i = 0; i < glyphs.length; i++) {
        var glyph = glyphs[i];
        if (glyph.advanceWidth) {
            width += glyph.advanceWidth * scale;
        }
        if (i < glyphs.length - 1) {
            var kerningValue = exp_font.getKerningValue(glyph, glyphs[i + 1]);
            width += kerningValue * scale;
        }
        ascent = Math.max(ascent, glyph.yMax);
        descent = Math.min(descent, glyph.yMin);
    }
    return {
        text: text,
        width: Math.floor(width),
        height: (exp_font.ascender * scale) - (exp_font.descender * scale),
        actualBoundingBoxAscent: ascent * scale,
        actualBoundingBoxDescent: descent * scale,
        fontBoundingBoxAscent: exp_font.ascender * scale,
        fontBoundingBoxDescent: exp_font.descender * scale,
        row: row,
        col: col,
        word: wordCount
    };
};

var prepAOI = function (data) {
    var temp_aois = [];
    var row = 1;
    var col = 1;
    var wordCount = 1;
    var largest_X = 0;
    var x = 0;
    var y = tempOffset[1];
    var orig_y = tempOffset[1];
    var info;
    var temp;
    var letter;
    var wordsSoFar = [];
    var count = 0;
    var longest_sentence = "";

    data[0].charAt(0) === ' ' ? x = tempOffset[0] - space : x = tempOffset[0];

    /*** Letter ***/
    for (var i = 0; i < data.length; i++) {
        for (var j = 0; j < data[i].length; j++) {
            letter = data[i].charAt(j);
            if (data[i] === '\n') {
                x = tempOffset[0];
                if ((i + 1) < data.length) {
                    if (data[i + 1].charAt(0) === ' ') {
                        x = tempOffset[0] - space;
                    }
                }
                y = y + st_h + leading;
                row += 1;
                col = 1;
            } else {
                // if (letter !== ' ') {
                info = get_dimensions(letter, row, col, wordCount);
                temp = new Rectangle(x, y, info, "letter");
                temp_aois.push(temp);
                x = x + info.width;
                if (x > largest_X) {
                    largest_X = x;
                }
                col += 1;
                wordCount += 1;
            }
        }
    }

    // reset all variables to original values
    row = 1, col = 1, wordCount = 1, x = 0, y = tempOffset[1], orig_y = tempOffset[1];
    data[0].charAt(0) === ' ' ? x = tempOffset[0] - space : x = tempOffset[0];

    /*** Word ***/
    for (var i = 0; i < data.length; i++) {
        if (data[i] === '\n') {
            x = tempOffset[0];
            if ((i + 1) < data.length) {
                if (data[i + 1].charAt(0) === ' ') {
                    x = tempOffset[0] - space;
                }
            }
            y = y + st_h + leading;
            row += 1;
            col = 1;
        }
        else {
            info = get_dimensions(data[i], row, col, wordCount);
            temp = new Rectangle(x, y, info, "word");
            temp_aois.push(temp);
            x = x + info.width;
            if (x > largest_X) {
                largest_X = x;
            }
            col += 1;
            wordCount += 1;
        }
    }

    return {'x': (largest_X) + 100, 'y': orig_y, 'data': temp_aois};
};

var drawData = function (tab) {
    tab = tab || $('.nav-tabs .active').attr("value");
    stage.removeChildren();
    stage.add(mouseLayer);

    // Clear selected AOIs' words info when changing between AOI levels
    sel_aois = [];

    // Show Text button
    if (document.getElementById("show_text").checked === true && document.getElementById("select_aoi").value === "letter") {
        stage.add(letterTextLayer);
        alert("Warning: Character AOI's only works for Monospaced text!");
    }
    if (document.getElementById("show_text").checked === true && document.getElementById("select_aoi").value === "word") {
        stage.add(textLayer);
    }

    // Show AOI button
    if (document.getElementById("show_aoi").checked === true && document.getElementById("select_aoi").value === "letter") {
        stage.add(letterAOILayer);
    }
    if (document.getElementById("show_aoi").checked === true && document.getElementById("select_aoi").value === "word") {
        stage.add(aoiLayer);
    }

    //alert($('.nav-tabs .active').attr("value"));
    if (tab === "fix") {
        //var lAlign = document.getElementById("lAlign");
        //var rAlign = document.getElementById("rAlign");
        if (document.getElementById("show_L_eye").checked === true) {
            fixationsDisplay('L', true);
            //lAlign.style.display = "block";
        }
        else {
            fixationsDisplay('L', false);
            //lAlign.style.display = "none";
        }
        if (document.getElementById("show_R_eye").checked === true) {
            fixationsDisplay('R', true);
            //rAlign.style.display = "block";
        }
        else {
            fixationsDisplay('R', false);
            //rAlign.style.display = "none";
        }
        stage.add(fixLayer);
    }
    stage.draw();
};

var fixationsDisplay = function (eye, visual) {
    var check;
    if (eye === 'R') {
        check = 0;
    }
    else {
        check = 1;
    }
    for (var i = 0; i < fixations.length; i = i + 1) {
        if (fixations[i] !== "") {
            if (fixations[i].id() % 2 === check) {
                if (visual) {
                    fixations[i].visible(true);
                    fixations[i].listening(true);
                }
                else {
                    fixations[i].visible(false);
                    fixations[i].listening(false);
                }
            }
        }
    }
    fixLayer.draw();
};
/****************** ******************/
/********* Canvas Stage **************/
/****************** ******************/
var setContainer = function (x, y, data) {
    y = y + y;
    y = y + st_h + leading;
    var row = 1;
    for (var i = 0; i < data.length; i++) {
        if (data[i].row === (row + 1)) {
            y = y + st_h + leading;
            row = row + 1;
        }
    }
    if (x < document.getElementById("container").offsetWidth) {
        con_width = document.getElementById("container").offsetWidth
    }
    else {
        con_width = x;
    }
    con_height = y;
    stage = new Konva.Stage({
        container: 'container',
        width: con_width,
        height: con_height
    });

    stage.on('mouseout', function () {
        var display_area = document.getElementById("dis_area");
        display_area.innerHTML = '';
        var x = 0;
        var y = 0;
        writeMessage('');
    });

    stage.on('mousemove', function () {
        var mousePos = stage.getPointerPosition();
        var x = mousePos.x + offset_x;
        var y = mousePos.y + offset_y;
        writeMessage('x: ' + x + ', y: ' + y);
    });

    var rect = new Konva.Rect({
        x: 0,
        y: 0,
        width: con_width,
        height: con_height,
        fill: 'white',
        stroke: 'black',
        strokeWidth: 1,
        draggable: false
    });

    var text = new Konva.Text({
        x: con_width - 150,
        y: 5,
        fontFamily: 'Calibri',
        fontSize: 20,
        text: '',
        fill: 'blue',
        draggable: false
    });

    function writeMessage(message) {
        text.setText(message);
        mouseLayer.draw();
    }

    mouseLayer.add(rect);
    mouseLayer.add(text);
};

/*************************************/
/*         Img Download              */
/*************************************/

function downloadURI(uri, name) {
    var link = document.createElement("a");
    link.download = name;
    link.href = uri;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    delete link;
}

document.getElementById('save').addEventListener('click', function () {
    var dataURL = stage.toDataURL();
    var currentexp = document.getElementById("current_exp").innerHTML;
    var name = currentexp + '.png';
    downloadURI(dataURL, name);
}, false);


function doKeyDown(e) {
    var tab = $('.nav-tabs .active').attr("value");
    var code = e.keyCode || e.which;
    if ([32, 37, 38, 39, 40].indexOf(e.keyCode) > -1) {
        e.preventDefault();
    }
    /*if (code === 39) {
        if (rFixShown < rMax && lFixShown < lMax) {
            lFixShown += 2;
            rFixShown += 2;
        }
    }
    if (code === 37) {
        if (rFixShown > 1 && lFixShown > 2) {
            lFixShown -= 2;
            rFixShown -= 2;
        }
    }
    if (code === 65 || code === 97) {
        lFixShown = lMax + 1;
        rFixShown = rMax + 1;
    }
    if (code === 67 || code === 99) {
        lFixShown = -1;
        rFixShown = -2;
    }
    show_fixes(lFixShown, rFixShown);*/
    if (document.getElementById("editing").checked === true && sel_fixes.length > 0) {
        if (code === 38) {
            moveSelected(-5);
        }
        if (code === 40) {
            moveSelected(5);
        }
    }
};