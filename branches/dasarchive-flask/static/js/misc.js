// ask2del.js
function confirmDelete(delUrl) {
	if (confirm("Are you sure you want to delete"))
		{ document.location = delUrl; }
}

function set_delete_form (url, form) {
	$("a[href=" + url + "]").click(function() {
		if (confirm('Are you sure you want to delete selected objects?'))
			document.forms[form].submit();
	});
}