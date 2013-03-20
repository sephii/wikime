function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            xhr.setRequestHeader("X-CSRFToken", $.cookie('csrftoken'));
        }
    }
});

$(function() {
    $('div.link div.title a').click(function() {
        var link_id = $(this).parents('div.link:first').attr('data-id');

        if($.cookie('last_link') != link_id) {
            $.cookie('last_link', link_id);
            $.post('/w/out/', {
                'id': link_id
            });
        }

        return true;
    });

    $('div.link div.delete a').click(function() {
        var link_container = $(this).parents('div.link:first');
        var link_id = link_container.attr('data-id');

        $.post('/w/delete/', {
            'id': link_id
        }, function(data) {
            link_container.fadeOut('slow', function() {
                link_container.remove();
            });
        });

        return false;
    });
});
