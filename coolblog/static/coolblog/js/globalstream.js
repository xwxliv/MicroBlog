$(document).ready(function () {
    updateComment();
    window.setInterval(updatePosts, 5000);
})

function updatePosts() {
    $.ajax({
        async: false,
        cache: false,
        dataType: 'json',
        type: 'GET',
        url: '/updateGlobalstream',

        success: function (posts) {
            $.each(posts, function (index, post) {
                $('#update_posts').prepend(
                    "<div class=\"d-flex flex-row justify-content-center pb-1 pt-2 align-self-center\">" +
                    "<div class=\"card flex-md-row mb-4 shadow-sm h-md-250\" style=\"width: 30rem;\">" +
                    "<div class=\"card-body d-flex flex-column align-items-start\">" +
                    "<div class=\"mb-1 text-muted\">" +
                    "<img id=\"postimage\" src=\"" + post.image + "\">" +
                    "<a href=\"/userstream?username=\"" + post.username + "\">" + post.username + "</a>" + " on " + post.time +
                    "</div>" +
                    "<p class=\"card-text mb-auto\">" + post.content + "</p>" +
                    "</div>" +
                    "</div>" +
                    "</div>"
                )
                ;
            });
        },
    });
}

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