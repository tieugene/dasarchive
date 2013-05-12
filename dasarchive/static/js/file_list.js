// let's go
// flag to enable checkboxes handle clicks
handlechecks = true

function onLoad() {
    // 1. handle checkboxes
    var checkboxes = get_all_checkboxes();
    var checked = checkboxes.filter(':checked');
    checkboxes.filter(':not(:checked)').parent().parent().hide();
    checked.parent().parent().addClass('bold');    // em selected
    checkboxes.click(onItemClick);    // test
    // 2. set All* buttons visibility
    $("#showall").attr("disabled", checked.length == checkboxes.length);
    $("#hideall").attr("disabled", true);
    $("#selectall").attr("disabled", true);
    $("#deselectall").attr("disabled", checked.length == 0);
    //console.log("All:", checkboxes.length, ", checked:", checked.length)
    // 3. Handle Group* buttons visibility and scripts
    get_all_groups().each(function(index) {
        var a = get_group_items(this).length;
        var s = get_group_checked(this).length;
        // show group
        var button = $(">button.showgroup", this);
        button.attr("disabled", s == a);
        button.click(showGroup);
        // hide group
        button = $(">button.hidegroup", this);
        button.attr("disabled", true);
        button.click(hideGroup);
        // select group
        button = $(">button.selectgroup", this);
        button.attr("disabled", true);
        button.click(selectGroup);
        // deselect group
        button = $(">button.deselectgroup", this);
        button.attr("disabled", s == 0);
        button.click(deselectGroup);
    });
}
// 1. helpers (get...)
// 1.1. all
function get_all_groups() {
    return $("ul#filter>li");
};
function get_all_items() {
    return $("ul#filter>li>ul>li");
};
function get_all_checkboxes() {
    return $("ul#filter>li>ul>li>label>input:checkbox");
};
function get_all_checked() {
    return $("ul#filter>li>ul>li>label>input:checkbox:checked").parent().parent();
};
function get_all_notchecked() {
    return $("ul#filter>li>ul>li>label>input:checkbox:not(:checked)").parent().parent();
};
function get_all_sv() {
    // return "all visible are checked" for all items
    return get_all_checked().length >= get_all_items().filter(":visible").length;
}
function get_group_items(group) {
    return $(">ul>li", group);
};
function get_group_checked(group) {
    return $(">ul>li>label>input:checkbox:checked", group).parent().parent();
};
function get_group_notchecked(group) {
    return $(">ul>li>label>input:checkbox:not(:checked)", group).parent().parent();
};
function get_group_sv(group) {
    // return "all visible are checked" for group
    return get_group_checked(group).length >= get_group_items(group).filter(":visible").length;
}
// 2. checkers
// 3. *All buttons click functions
function showAll() {
    get_all_items().filter(":hidden").show();   // show all hidden
    $("#showall").attr("disabled", true);
    $("#hideall").attr("disabled", false);
    $("#selectall").attr("disabled", false);
    // deselect all - skip
    get_all_groups().each(function(index) {
        var disable = get_group_items(this).length == get_group_checked(this).length;
        $(">button.showgroup", this).attr("disabled", false);
        $(">button.hidegroup", this).attr("disabled", disable);
        $(">button.selectgroup", this).attr("disabled", disable);
        // deselect group - skip
    });
}
function hideAll() {
    get_all_notchecked().filter(":visible").hide(); // hide all visible
    $("#showall").attr("disabled", false);
    $("#hideall").attr("disabled", true);
    $("#selectall").attr("disabled", true);
    // deselect all - skip
    get_all_groups().each(function(index) {
        $(">button.showgroup", this).attr("disabled", get_group_items(this).filter(":hidden").length == 0);
        $(">button.hidegroup", this).attr("disabled", true);
        $(">button.selectgroup", this).attr("disabled", true);
        // deselect group - skip
    });
}

function selectAll() {
    handlechecks = false;
    $(">label>input:checkbox", get_all_notchecked().filter(":visible")).click();   // check all visible
    handlechecks = true;
    // show all - skip
    $("#hideall").attr("disabled", true);
    $("#selectall").attr("disabled", true);
    $("#deselectall").attr("disabled", false);
    get_all_groups().each(function(index) {
        // showgroup - skip
        $(">button.hidegroup", this).attr("disabled", true);
        $(">button.selectgroup", this).attr("disabled", true);
        $(">button.deselectgroup", this).attr("disabled", get_group_sv(this));
    });
}

function deselectAll() {
    //$(">label>input:checkbox", get_all_checked().click();
    handlechecks = false;
    get_all_checkboxes().filter(":checked:visible").click();
    handlechecks = true;
    // show all - skip
    $("#hideall").attr("disabled", false);
    $("#selectall").attr("disabled", false);
    $("#deselectall").attr("disabled", true);
    get_all_groups().each(function(index) {
        var invisible = get_group_items(this).filter(":visible").length == 0;
        // showgroup - skip
        $(">button.hidegroup", this).attr("disabled", invisible);
        $(">button.selectgroup", this).attr("disabled", invisible);
        $(">button.deselectgroup", this).attr("disabled", true);
    });
}

// 4. *Group buttons click functions
function showGroup() {
    //$('ul>li', $(this).parent()).show()
    // 0. action
    group = $(this).parent();
    get_group_items(group).filter(":hidden").show();
    // 1. global
    $("#showall").attr("disabled", get_all_items().filter(":hidden").length == 0);
    $("#hideall").attr("disabled", false);
    $("#selectall").attr("disabled", false);
    // deselect all - skip
    // 2. this group
    $(">button.showgroup", group).attr("disabled", true);
    $(">button.hidegroup", group).attr("disabled", false);
    $(">button.selectgroup", group).attr("disabled", false);
    // deselectgroup - skip
}

function hideGroup() {
    //$('ul>li>label>input:checkbox:not(:checked)', $(this).parent()).parent().parent().hide()
    // 0. action
    group = $(this).parent();
    get_group_notchecked(group).filter(":visible").hide();
    // 1. global
    var nosv = get_all_sv()
    $("#showall").attr("disabled", false);
    $("#hideall").attr("disabled", nosv);
    $("#selectall").attr("disabled", nosv);
    // deselect all - skip
    // 2. this group
    $(">button.showgroup", group).attr("disabled", false);
    $(">button.hidegroup", group).attr("disabled", true);
    $(">button.selectgroup", group).attr("disabled", true);
    // deselectgroup - skip
}

function selectGroup() {
    //$("ul>li>label>input:checkbox:not(:checked)", $(this).parent()).click();
    // 0. action
    group = $(this).parent();
    handlechecks = false;
    $(">ul>li:visible>label>input:checkbox:not(:checked)", group).click();
    handlechecks = true;
    // 1. global
    var nosv = get_all_sv()
    // showall - skip
    $("#hideall").attr("disabled", nosv);
    $("#selectall").attr("disabled", nosv);
    $("#deselectall").attr("disabled", false);
    // 2. this group
    // showgroup - skip
    $(">button.hidegroup", group).attr("disabled", true);
    $(">button.selectgroup", group).attr("disabled", true);
    $(">button.deselectgroup", group).attr("disabled", false);
}

function deselectGroup() {
    group = $(this).parent();
    handlechecks = false;
    $("ul>li>label>input:checkbox:checked", group).click();
    handlechecks = true;
    // showall - skip
    $("#hideall").attr("disabled", false);
    $("#selectall").attr("disabled", false);
    $("#deselectall").attr("disabled", get_all_checked().length == 0);
    // 2. this group
    // showgroup - skip
    $(">button.hidegroup", group).attr("disabled", false);
    $(">button.selectgroup", group).attr("disabled", false);
    $(">button.deselectgroup", group).attr("disabled", true);
}

// 5. checkboxes click functions
function onItemClick() {
    if (handlechecks) handle_checkbox($(this));
}

function handle_checkbox(cb) {
    group = cb.parent().parent().parent().parent();
    if (cb.prop('checked')) {   // On
        // 1. global
        var nosv = get_all_sv();
        // showall - skip
        $("#hideall").attr("disabled", nosv);
        $("#selectall").attr("disabled", nosv);
        $("#deselectall").attr("disabled", false);
        // 2. this group
        nosv = get_group_sv(group);
        // showgroup - skip
        $(">button.hidegroup", group).attr("disabled", nosv);
        $(">button.selectgroup", group).attr("disabled", nosv);
        $(">button.deselectgroup", group).attr("disabled", false);
    } else {                    // Off
        // showall - skip
        $("#hideall").attr("disabled", false);
        $("#selectall").attr("disabled", false);
        $("#deselectall").attr("disabled", get_all_checked().length == 0);
        // 2. this group
        // showgroup - skip
        $(">button.hidegroup", group).attr("disabled", false);
        $(">button.selectgroup", group).attr("disabled", false);
        $(">button.deselectgroup", group).attr("disabled", get_group_checked(group).length == 0);
    }
}
