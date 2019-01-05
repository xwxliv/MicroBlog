$(document).ready(function () {
    updateComment();
})

function updateComment() {
    $(document).on('submit', 'form.add_comment', function (event) {
        event.preventDefault();
        var pid = $(this).attr('id');
        var comment_content = $("#new" + pid).val();
        console.log(pid)
        $.ajax({
            async: false,
            cache: false,
            dataType: 'json',
            type: 'POST',
            url: '/addComment',
            data: {'comment_content': comment_content, 'pid': pid},

            success: function (data) {
                $("#new" + pid).val('');
                $("#user_comments" + pid).append(
                    "<div class=\"mb-1 text-muted\">" +
                    "<img id=\"postimage\" src=\"" + data.image + "\">" +
                    "<a href=\"/userstream?username=\"" + data.username + "\">" + data.username + "</a>" + " on " + data.time +
                    "</div>" +
                    "<p class=\"card-text mb-auto\">" + data.content + "</p>" +
                    "</div>"
                );
            },
        });
    });
}