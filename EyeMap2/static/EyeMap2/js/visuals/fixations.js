/****************** ***********************/
/********* Fixations **************/
/****************** ***********************/

var fix_trial_data = [];


var get_trial_fix_data = function () {
    lFixShown = -1;
    rFixShown = -2;
    var trial_sel = document.getElementById("trials_sel").value;
    fix_trial_data = all_fix_data[trial_sel - 1];
    fix_trial_data = fix_trial_data.sort(sortById);
    get_dur_scale();
    if ($('.nav-tabs .active').attr("value") !== "scan") {
        get_fixes();
    }
    else {
        get_fixes_scan();
    }
    drawData();
};

var get_dur_scale = function () {
    var largest = Number.MIN_VALUE;
    var smallest = Number.MAX_VALUE;
    for (var i in fix_trial_data) {
        if (Number(fix_trial_data[i].dur) > largest) {
            largest = Number(fix_trial_data[i].dur);
        }
        if (Number(fix_trial_data[i].dur) < smallest) {
            smallest = Number(fix_trial_data[i].dur);
        }
    }
    dur_scale = largest;
};

var get_fixes = function () {
    fixations = [];
    fixationsCircles = [];
    var hasBothEyes = checkForBinocularData();
    if(!hasBothEyes){
        for(var i = 0; i < (fix_trial_data.length * 2); i++){
            fixationsCircles.push("");
            fixations.push("");
        }
    }
    var isDurChecked = document.getElementById("dur_radius").checked;
    var radius = 10;
    var dr_color = '';
    var maxScale = 50;
    for (var i in fix_trial_data) {
        if (fix_trial_data[i].eye === 'L') {
            if (isDurChecked) {
                radius = (Number(fix_trial_data[i].dur) / dur_scale) * maxScale;
            }
            if (!isNaN(fix_trial_data[i].blink) && fix_trial_data[i].blink !== null){
                dr_color = 'black';
            }
            else{
                dr_color = 'blue';
            }
            addCircle_fix(fix_trial_data[i], radius, dr_color);
        }
        if (fix_trial_data[i].eye === 'R') {
            if (isDurChecked) {
                radius = (Number(fix_trial_data[i].dur) / dur_scale) * maxScale;
            }
            if (!isNaN(fix_trial_data[i].blink) && fix_trial_data[i].blink !== null){
                dr_color = 'black';
            }
            else{
                dr_color = 'red';
            }
            addCircle_fix(fix_trial_data[i], radius, dr_color);
        }
    }
    var totalFixCount = fix_trial_data.length;
    var isFixCountEven = totalFixCount % 2 === 0;
    if (isFixCountEven) {
        lMax = totalFixCount - 2;
        rMax = totalFixCount - 1;
    }
    else {
        lMax = totalFixCount - 1;
        rMax = totalFixCount - 2;
    }
    setUpRubberRect();
};

var checkForBinocularData = function(){
    var hasREye = false;
    var hasLEye = false;
    for(var x in fix_trial_data){
        var temp = fix_trial_data[x].eye;
        if(temp === "R"){
            hasREye = true;
        }
        if(temp === "L"){
            hasLEye = true;
        }
    }
    return (hasLEye && hasREye);
};

var addCircle_fix = function (fix, radius, dr_color) {
    var circ = new Circle(fix);
    fixationsCircles[Number(fix.id)] = circ;
    var x = fix.x - offset_x;
    var y = fix.y - offset_y;

    var group = new Konva.Group({
        id: fix.id
    });

    var circle = new Konva.Circle({
        x: x,
        y: y,
        radius: radius,
        fill: dr_color,
        opacity: 0.5,
        visible: 'inherit'
    });
    group.add(circle);
    var c1 = new Konva.Line({
        points: [x - 3, y, x + 3, y],
        stroke: 'black',
        strokeWidth: 1,
        visible: 'inherit'
    });
    group.add(c1);
    var c2 = new Konva.Line({
        points: [x, y - 3, x, y + 3],
        stroke: 'black',
        strokeWidth: 1,
        visible: 'inherit'
    });
    group.add(c2);
    extra_fix_func(group);
    //group.visible(false);
    fixLayer.add(group);
    fixations[Number(fix.id)] = group;
};

var extra_fix_func = function (group) {
    group.on('click', function () {
        var shape = group.find('Circle')[0];
        var opacity = shape.opacity() === 0.8 ? 0.5 : 0.8;
        shape.opacity(opacity);
        clicked_fix(group);
        fixLayer.draw();
    });

    group.on('mouseover', function () {
        //Fix this for monocular data
        display_fix_info(fixationsCircles[Number(this.id())]);
    });
};

var clicked_fix = function (circle) {
    var temp = circle.id();
    var isNew = true;
    if (sel_fixes.length > 0) {
        for (var i = 0; i < sel_fixes.length; i++) {
            if (temp === sel_fixes[i].id) {
                sel_fixes.splice(i, 1);
                isNew = false;
            }
        }
    }
    if (isNew) {
        for (var i = 0; i < fixationsCircles.length; i++) {
            if (temp === fixationsCircles[i].id) {
                sel_fixes.push(fixationsCircles[i])
            }
        }
    }
    add_fix_to_box();
    setFixOpacity();
};

var setFixOpacity = function () {
    for (var i = 0; i < sel_fixes.length; i++) {
        for (var j = 0; j < fixations.length; j++) {
            if(fixations[j]!== ""){
                if (sel_fixes[i].id === fixations[j].id()) {
                    var shape = fixations[j].find('Circle')[0];
                    shape.opacity(0.8);
                }
            }
        }
    }
};

var add_fix_to_box = function () {
    sel_fixes = sel_fixes.sort(sortById);
    var display_area = document.getElementById("fix_display");
    display_area.innerHTML = '';

    //var alignSel = document.getElementById("alignSel");
    var word_area = document.createElement("div");
    if (sel_fixes.length > 0) {
        word_area.setAttribute("class", "well well-sm");
        var title = document.createElement("h5");
        title.setAttribute("class", "text-primary");
        title.appendChild(document.createTextNode("Selected Fixations"));
        word_area.appendChild(title);
        for (var i = 0; i < sel_fixes.length; i++) {
            var p = document.createElement("p");
            p.setAttribute("class", "text-primary");
            p.appendChild(document.createTextNode("Fix " + sel_fixes[i].id + ", Eye: " + sel_fixes[i].eye));
            word_area.appendChild(p);
        }
        var button = document.createElement("button");
        button.setAttribute("class", "btn btn-outline btn-primary btn-block");
        button.setAttribute("onclick", "clearSelFixes()");
        button.appendChild(document.createTextNode("Clear selected fixes"));
        word_area.appendChild(button);
        //alignSel.style.display = "block";
    }
    else {
        //alignSel.style.display = "none";
    }
    display_area.appendChild(word_area)

};

var clearSelFixes = function () {
    sel_fixes = [];
    fixLayer.removeChildren();
    get_trial_fix_data();
    var display_area = document.getElementById("fix_display");
    display_area.innerHTML = '';
    drawData();
};

var display_fix_info = function (fix) {
    var display_area = document.getElementById("dis_area");
    display_area.innerHTML = '';

    var word_area = document.createElement("div");
    word_area.setAttribute("class", "well well-sm");

    var p = document.createElement("h4");
    p.setAttribute("class", "text-primary");
    p.appendChild(document.createTextNode("Fixation Information"));
    var p1 = document.createElement("p");
    p1.setAttribute("class", "text-primary");
    p1.appendChild(document.createTextNode("Fix ID: " + "'" + fix.id + "'"));
    var p2 = document.createElement("p");
    p2.setAttribute("class", "text-primary");
    p2.appendChild(document.createTextNode("Eye: " + "'" + fix.eye + "'"));
    var p3 = document.createElement("p");
    p3.setAttribute("class", "text-primary");
    p3.appendChild(document.createTextNode("x pos: " + fix.x));
    var p4 = document.createElement("p");
    p4.setAttribute("class", "text-primary");
    p4.appendChild(document.createTextNode("y pos: " + fix.y));

    word_area.appendChild(p);
    word_area.appendChild(p1);
    word_area.appendChild(p2);
    word_area.appendChild(p3);
    word_area.appendChild(p4);
    display_area.appendChild(word_area);
};

var setUpRubberRect = function () {
    var rect = new Konva.Rect({
        x: 0,
        y: 0,
        width: con_width,
        height: con_height,
        draggable: false
    });
    fixLayer.add(rect);
    rect.moveToBottom();
    var rubber = new Konva.Rect({
        x: 0,
        y: 0,
        width: 0,
        height: 0,
        stroke: 'green',
        dash: [2, 2]
    });

    rubber.listening(false);
    fixLayer.add(rubber);

    var posStart;
    var posNow;
    var mode = '';

    function startDrag(posIn) {
        posStart = {x: posIn.x, y: posIn.y};
        posNow = {x: posIn.x, y: posIn.y};
    }

    function updateDrag(posIn, isLEye, isREye) {
        // update rubber rect position
        posNow = {x: posIn.x, y: posIn.y};
        var posRect = reverse(posStart, posNow);
        rubber.x(posRect.x1);
        rubber.y(posRect.y1);
        rubber.width(posRect.x2 - posRect.x1);
        rubber.height(posRect.y2 - posRect.y1);
        rubber.visible(true);

        fixLayer.draw();
    }

    rect.on('mousedown', function (e) {
        mode = 'drawing';
        startDrag({x: e.evt.layerX, y: e.evt.layerY});
    });

    // update the rubber rect on mouse move - note use of 'mode' var to avoid drawing after mouse released.
    rect.on('mousemove', function (e) {
        if (mode === 'drawing') {
            updateDrag({x: e.evt.layerX, y: e.evt.layerY});
        }
    });

    rect.on('mouseup', function (e) {
        var isREye = document.getElementById("show_R_eye").checked;
        var isLEye = document.getElementById("show_L_eye").checked;
        // run the collision check loop
        if (isLEye) {
            for (var i = 1; i < fixations.length; i = i + 2) {
                if (hitCheck(fixations[i], rubber)) {
                    clicked_fix(fixations[i]);
                }
            }
        }
        if (isREye) {
            for (var i = 0; i < fixations.length; i = i + 2) {
                if (hitCheck(fixations[i], rubber)) {
                    clicked_fix(fixations[i]);
                }
            }
        }
        mode = '';
        rubber.visible(false);
        stage.draw();
    });

    // reverse co-ords if user drags left / up
    function reverse(r1, r2) {
        var r1x = r1.x, r1y = r1.y, r2x = r2.x, r2y = r2.y, d;
        if (r1x > r2x) {
            d = Math.abs(r1x - r2x);
            r1x = r2x;
            r2x = r1x + d;
        }
        if (r1y > r2y) {
            d = Math.abs(r1y - r2y);
            r1y = r2y;
            r2y = r1y + d;
        }
        return ({x1: r1x, y1: r1y, x2: r2x, y2: r2y}); // return the corrected rect.
    }

    function hitCheck(shape1, shape2) {

        var s1 = shape1.getClientRect(); // use this to get bounding rect for shapes other than rectangles.
        var s2 = shape2.getClientRect();

        // corners of shape 1
        var X = s1.x;
        var Y = s1.y;
        var A = s1.x + s1.width;
        var B = s1.y + s1.height;

        // corners of shape 2
        var X1 = s2.x;
        var A1 = s2.x + s2.width;
        var Y1 = s2.y;
        var B1 = s2.y + s2.height;

        // Simple overlapping rect collision test
        if (A < X1 || A1 < X || B < Y1 || B1 < Y) {
            return false;
        }
        else {
            return true;
        }
    }
};

/****************** ******************/
/********* Editing **************/
/****************** ******************/
var showEditOptions = function () {
    var x = document.getElementById("editFixOptions");
    if (document.getElementById("editing").checked === true) {
        //x.style.display = "block";
    }
    else {
        //x.style.display = "none";
    }
};

var moveSelected = function (dist) {
    var fixGroups = fixLayer.find('Group');
    for (var i = 0; i < fixGroups.length; i++) {
        for (var j = 0; j < sel_fixes.length; j++) {
            if (fixGroups[i].id() === sel_fixes[j].id) {
                fixGroups[i].move({x: 0, y: dist});
                var pos = Number(sel_fixes[j].y) + dist;
                sel_fixes[j].y = String(pos);
            }
        }
    }
    fixLayer.draw();

    for (var i = 0; i < sel_fixes.length; i++) {
        for (var j = 0; j < fixationsCircles.length; j++) {
            if (sel_fixes[i].id === fixationsCircles[j].id) {
                fixationsCircles[j].y = sel_fixes[i].y;
            }
        }
    }
};

/****************** ******************/
/********* Animations **************/
/****************** ******************/


var show_fixes = function (lFix, rFix) {
    var isREye = document.getElementById("show_R_eye").checked;
    var isLEye = document.getElementById("show_L_eye").checked;
    if (isLEye) {
        var fixGroups = fixLayer.find('Group');
        for (var i = 0; i < fixGroups.length; i = i + 2) {
            if (fixGroups[i].id() <= lFix) {
                fixGroups[i].show();
            }
            else {
                fixGroups[i].hide();
            }
        }
    }
    if (isREye) {
        for (var i = 1; i < fixGroups.length; i = i + 2) {
            if (fixGroups[i].id() <= rFix) {
                fixGroups[i].show();
            }
            else {
                fixGroups[i].hide();
            }
        }
    }
    fixLayer.draw();
};
