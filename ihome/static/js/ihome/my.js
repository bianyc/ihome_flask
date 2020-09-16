function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

// 点击退出按钮时执行的函数
function logout() {
    $.ajax({
        url: "/api/v1.0/session",
        type: "delete",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        dataType: "json",
        success: function (resp) {
            if ("0" === resp.errno) {
                location.href = "/index.html";
            }
        }
    });
}

$(document).ready(function(){
    $.get("api/v1.0/user", function (resp) {
        // 查询到用户信息
        if (resp.errno === "0") {
            $("#user-name").html(resp.data.nickname);
            $("#user-mobile").html(resp.data.mobile);
            if (resp.data.avatar_url) {
                var avatarUrl = resp.data.avatar_url;
                $("#user-avatar").attr("src", avatarUrl);
            }
        } else if (resp.errno === "4101") {
            location.href = "/login.html";
        }
    }, "json");
})