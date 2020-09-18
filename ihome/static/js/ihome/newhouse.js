function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // 向后端发送请求获取城区信息
    $.get("api/v1.0/areas", function (resp) {
        if (resp.errno === "0") {
            var areas = resp.data;
            // for (i=0; i<areas.length; i++) {
            //     var area = areas[i];
            //     $("#area-id").append('<option value="'+ area.id +'">'+ area.name +'</option>');
            // }

            // 使用js模板
            var html = template("area-tmp", {areas: areas})
            $("#area-id").html(html);
        } else {
            alert(resp.errmsg);
        }
    }, "json");

    $("#form-house-info").submit(function (e) {
        e.preventDefault();

        // 处理表单数据
        var form_data = {};
        $("#form-house-info").serializeArray().map(function (form) {
            form_data[form.name] = form.value
        });

        // 收集设施id信息
        var facilities = [];
        $(":checked[name=facility]").each(function (index, value) {
            facilities[index] = $(value).val();
        });
        form_data.facility = facilities;

        // 向后端发送请求
        var dataJson = JSON.stringify(form_data);
        $.ajax({
            url: "api/v1.0/house/info",
            type: "post",
            data: dataJson,
            dataType: "json",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno === "4101") {
                    // 用户未登录
                    location.href = "/login.html";
                } else if (resp.errno === "0") {
                    // 隐藏基本信息表单
                    $("#form-house-info").hide();
                    // 显示图片表单
                    $("#form-house-image").show();
                    // 设置图片表单中的house_id
                    $("#house-id").val(resp.data.house_id);
                } else {
                    alert(resp.errmsg);
                }
            }
        })
    });

    $("#form-house-image").submit(function (x) {
        // 阻止表单的默认行为
        x.preventDefault();

        // 利用jquery.form.min.js提供的ajaxSubmit对表单进行异步提交
        $(this).ajaxSubmit({
            url: "/api/v1.0/house/image",
            type: "post",
            dataType: "json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            success: function (resp) {
                if (resp.errno === "4101") {
                    location.href = "/login.html";
                } else if (resp.errno === "0") {
                    var imageUrl = resp.data.image_url;
                    $(".house-image-cons").append(
                        '<img src="'+ imageUrl +'">'
                    );
                }else {
                    alert(resp.errmsg);
                }
            }
        })
    });
})