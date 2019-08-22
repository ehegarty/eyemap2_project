/****************** ***********************/
/********* Areas of Interest **************/
/****************** ***********************/
var orig_aois = [];
var new_aois = [];
var sel_aois = [];

var get_aois_info = function () {
    orig_aois = [];
    var trial_sel = document.getElementById("trials_sel").value;
    var data = all_aois[trial_sel - 1];
    setContainer(data.x, data.y, data.data);
    orig_aois = data.data;
    add_aois();
    get_trial_fix_data();
};

var add_aois = function () {
    if (sel_aois.length > 0) {
        add_sel_to_box();
    }
    var temp_aois = [];
    if (new_aois.length > 0) {
        temp_aois = new_aois;
    } else {
        temp_aois = orig_aois;
    }
    for (var i = 0; i < temp_aois.length; i++) {
        if (temp_aois[i].selected) {
            dr_color = 'red';
        } else {
            dr_color = 'blue';
        }

        var group = new Konva.Group({
            id: String(i)
        });

        var box = new Konva.Rect({
            x: temp_aois[i].x,
            y: temp_aois[i].top,
            width: temp_aois[i].width,
            height: temp_aois[i].height,
            name: temp_aois[i].type,
            stroke: dr_color,
            strokeWidth: 1,
            opacity: 0.5,
            id: String(i),
            draggable: false
        });

        extra_aoi_func(box);

        if (box.getAttr("name") === "letter") {
            letterAOILayer.add(box);
        } else if (box.getAttr("name") === "word") {
            aoiLayer.add(box);
        }

        var text = new Konva.Text({
            x: temp_aois[i].x-1,
            y: temp_aois[i].y,
            name: temp_aois[i].type,
            text: temp_aois[i].text,
            fontSize: font_size,
            fontFamily: font_family,
            fill: '#555',
            id: i,
            draggable: false
        });

        //group.add(text);

        if (text.getAttr("name") === "letter") {
            letterTextLayer.add(text);
        }
        else if (text.getAttr("name") === "word") {
            textLayer.add(text);
        }
    }
};

var extra_aoi_func = function (box) {
    if ($('.nav-tabs .active').attr("value") === "aoi") {
        box.on('click', function () {
            var fill = this.fill() === 'red' ? '' : 'red';
            this.fill(fill);
            aoiLayer.draw();
            letterAOILayer.draw();
            clicked_aoi(this);
        });
    }
    box.on('mouseover', function () {
        var temp_aois = [];
        if (new_aois.length > 0) {
            temp_aois = new_aois;
        } else {
            temp_aois = orig_aois;
        }
        display_word_info(temp_aois[Number(this.id())]);
    });
};

var clicked_aoi = function (aoi) {
    var temp_aois = [];
    if (new_aois.length > 0) {
        temp_aois = new_aois;
    } else {
        temp_aois = orig_aois;
    }
    var temp = aoi.id();
    if ($('.nav-tabs .active').attr("value") === "aoi") {
        temp_aois[temp].selected = !temp_aois[temp].selected;
        if (temp_aois[temp].selected === true) {
            sel_aois.push(temp_aois[temp]);
            add_sel_to_box();
        } else if (temp_aois[temp].selected === false && sel_aois.length > 0) {
            for (var j = 0; j < sel_aois.length; j++) {
                if (temp_aois[temp].word === sel_aois[j].word) {
                    sel_aois.splice(j, 1);
                }
            }
            add_sel_to_box();
        }
    }
};

var add_sel_to_box = function () {
    sel_aois = sel_aois.sort(sortByWord);
    var display_area = document.getElementById("tool_display");
    display_area.innerHTML = '';

    var word_area = document.createElement("div");

    if (sel_aois.length > 0) {
        word_area.setAttribute("class", "well well-sm");
        var title = document.createElement("h5");
        title.setAttribute("class", "text-primary");
        title.appendChild(document.createTextNode("Selected AOI's"));
        word_area.appendChild(title);
    }

    var rows = [];
    var current = 0;
    for (var i = 0; i < sel_aois.length; i++) {
        if (sel_aois[i].row !== current) {
            rows.push(sel_aois[i].row);
            current = sel_aois[i].row;
        }
    }
    for (var i = 0; i < rows.length; i++) {
        var p = document.createElement("p");
        p.setAttribute("class", "text-primary");
        p.appendChild(document.createTextNode("Line " + rows[i]));
        word_area.appendChild(p);
        for (var j = 0; j < sel_aois.length; j++) {
            if (sel_aois[j].row === rows[i]) {
                var p2 = document.createElement("p");
                p2.setAttribute("class", "text-danger");
                // sel_aois[j].text.substring(1))
                p2.appendChild(document.createTextNode(sel_aois[j].text));
                word_area.appendChild(p2);
            }
        }
    }
    if (sel_aois.length > 0) {
        var button = document.createElement("button");
        button.setAttribute("class", "btn btn-outline btn-primary btn-block");
        button.setAttribute("onclick", "un_merge_aois()");
        button.appendChild(document.createTextNode("Clear selected"));
        word_area.appendChild(button);
    }
    /*
    if (sel_aois.length > 1) {
        var button = document.createElement("button");
        button.setAttribute("class", "btn btn-outline btn-primary btn-block");
        button.setAttribute("onclick", "merge_aois()");
        button.appendChild(document.createTextNode("Merge"));
        word_area.appendChild(button);
    }*/
    if (new_aois.length > 0) {
        var button2 = document.createElement("button");
        button2.setAttribute("class", "btn btn-outline btn-danger btn-block");
        button2.setAttribute("onclick", "un_merge_aois()");
        button2.appendChild(document.createTextNode("Un-Merge All"));
        word_area.appendChild(button2);
    }
    display_area.appendChild(word_area);
};

var un_merge_aois = function () {
    new_aois = [];
    sel_aois = [];
    for (var i = 0; i < orig_aois.length; i++) {
        orig_aois[i].selected = false;
    }
    add_sel_to_box();
    // AOI layers
    aoiLayer.removeChildren();
    letterAOILayer.removeChildren();


    // Text layers
    textLayer.removeChildren();
    letterTextLayer.removeChildren();

    add_aois();
};

var merge_aois = function () {
    var temp_aois = [];
    if (new_aois.length > 0) {
        temp_aois = new_aois;
        new_aois = [];
    } else {
        temp_aois = orig_aois;
    }
    for (var i = 0; i < temp_aois.length; i++) {
        if (!temp_aois[i].selected) {
            new_aois.push(temp_aois[i]);
        } else {
            var j = i;
            var combo_word = "";
            //var extra = 2;
            var r = temp_aois[i].row;
            while (j < temp_aois.length && temp_aois[j].selected && temp_aois[j].row === r) {
                combo_word = combo_word + temp_aois[j].text;
                //extra = extra + 2;
                j += 1;
            }
            var info = get_dimensions(combo_word, temp_aois[i].row, temp_aois[i].col, temp_aois[i].word);
            var rect = new Rectangle(temp_aois[i].x, temp_aois[i].y, info);
            new_aois.push(rect);
            i = j - 1;
        }
    }
    sel_aois = [];

    // AOI layers
    aoiLayer.removeChildren();
    letterAOILayer.removeChildren();

    // Text layers
    textLayer.removeChildren();
    letterTextLayer.removeChildren();

    add_aois();
    drawData();
    var tool_display = document.getElementById("tool_display");
    tool_display.innerHTML = '';

};

var display_word_info = function (word) {
    var display_area = document.getElementById("dis_area");
    display_area.innerHTML = '';

    var word_area = document.createElement("div");
    word_area.setAttribute("class", "well well-sm");

    var p = document.createElement("h4");
    p.setAttribute("class", "text-primary");
    p.appendChild(document.createTextNode("Word Information"));
    var p1 = document.createElement("p");
    p1.setAttribute("class", "text-primary");
    if (word.text.charAt(0) === ' ') {
        p1.appendChild(document.createTextNode("word: " + "'" + word.text.substring(1) + "'"));
    }
    else {
        p1.appendChild(document.createTextNode("word: " + "'" + word.text + "'"));
    }

    var p2 = document.createElement("p");
    p2.setAttribute("class", "text-primary");
    p2.appendChild(document.createTextNode("position: " + word.name));
    var p3 = document.createElement("p");
    p3.setAttribute("class", "text-primary");
    p3.appendChild(document.createTextNode("width: " + Math.round(word.width * 100) / 100));

    word_area.appendChild(p);
    word_area.appendChild(p1);
    word_area.appendChild(p2);
    word_area.appendChild(p3);
    display_area.appendChild(word_area);
};
