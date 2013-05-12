// let's go
function onLoad() {
    // 1. handle checkboxes
    var checkboxes = get_all_checkboxes();
    checkboxes.filter(':not(:checked)').parent().parent().hide();
    checkboxes.filter(':checked').parent().parent().addClass('bold');    // em selected
    checkboxes.click(testItem);    // test
    // 2. set All* buttons
    // 3. assign scripts to Group* buttons
    var groupbuttons = $('>button', get_all_groups());
    groupbuttons.filter('.showgroup').click(showGroup);
    groupbuttons.filter('.hidegroup').click(hideGroup);
    groupbuttons.filter('.selectgroup').click(selectGroup);
    groupbuttons.filter('.deselectgroup').click(deselectGroup);
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
function get_group_items(group) {
    return $(">ul>li", group);
};
function get_group_checked(group) {
    return $(">ul>li>label>input:checkbox:checked", group).parent().parent();
};
function get_group_notchecked(group) {
    return $(">ul>li>label>input:checkbox:not(:checked)", group).parent().parent();
};
// 2. checkers
// 3. *All buttons click functions
function showAll() {
    get_all_items().show();
}
function hideAll() {
    get_all_notchecked().hide()
}
function selectAll() {
    $(">label>input:checkbox", get_all_notchecked()).click();
}
function deselectAll() {
    //$(">label>input:checkbox", get_all_checked().click();
    get_all_checkboxes().filter(":checked").click();
}
// 4. *Group buttons click functions
function showGroup() {
    $('ul>li', $(this).parent()).show()
}
function hideGroup() {
    $('ul>li>label>input:checkbox:not(:checked)', $(this).parent()).parent().parent().hide()
}
function selectGroup() {
    $("ul>li>label>input:checkbox:not(:checked)", $(this).parent()).click();
}
function deselectGroup() {
    $("ul>li>label>input:checkbox:checked", $(this).parent()).click();
}
// 5. checkboxes click functions
function testItem() {   // FIXME: work on software click()
    //var all = $('ul#filter>li>ul>li>label>input:checkbox');
    //var selected = all.filter(':checked')
    //var selected = $('ul#filter>li>ul>li>label>input:checkbox:checked');
    //var visible = $('ul#filter>li>ul>li:visible');
    //console.log('All: ', all.length)
    //console.debug('Selected: ', selected.length)
    //console.log('Visible: ', visible.length)
    //console.log('Hidden: ', all.length-visible.length)
    console.log('State: ', $(this).prop('checked')) // bool
}
