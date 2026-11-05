// Attach the CSRF token to every state-changing AJAX request so global
// flask_wtf CSRFProtect accepts same-origin POSTs made with jQuery.
$(function () {
	var csrfToken = $('meta[name=csrf-token]').attr('content');
	$.ajaxSetup({
		beforeSend: function (xhr, settings) {
			if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain && csrfToken) {
				xhr.setRequestHeader('X-CSRFToken', csrfToken);
			}
		}
	});
});

$( '#topheader .navbar-nav a' ).on( 'click', function () {
	$( '#topheader .navbar-nav' ).find( 'li.active' ).removeClass( 'active' );
	$( this ).parent( 'li' ).addClass( 'active' );
});

$(".flashed-messages .alert").delay(4000).slideUp(500, function () {
 $(this).remove();
});
