$(document).ready(function(){
    // $(".auth-warn").show();
    // 查询用户的实名认证信息
    $.get("api/v1.0/users/auth", function (resp) {
        // 4101未登录，跳转登录页面
        if (resp.errno === "4101") {
            location.href = "/login.html";
        } else if (resp.errno === "0") {
            // 未认证的用户，在页面中展示 "去认证"的按钮
            if (!(resp.data.real_name && resp.data.id_card)) {
                $(".auth-warn").show();
                return;
            }
            // 已认证的用户，请求其之前发布的房源信息
            $.get("/api/v1.0/user/houses", function (resp) {
                if (resp.errno === "0") {
                    $("#houses-list").html(template("houses-list-tmp", {houses: resp.data.houses}))
                } else {
                    $("#houses-list").html(template("houses-list-tmp", {houses:[]}));
                }
            });
        }
    });
})