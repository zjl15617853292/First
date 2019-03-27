/**
 * Created by tarena on 19-2-16.
 */
/**
 * Created by tarena on 19-2-12.
 */
function checkUname() {
    // 后台地址:/01-checkuname
    // 服务器端:返回1,表示用户名已存在,返回0,表示通过
    // 参数:要检查的用户名称
    // 请求方式:get
    // 同步or异步:异步

    // 声明返回值，来表示验证结果，提供给调用者使用
    var ret = true;//表示用户名称不存在

    //1.创建xhr对象
    var xhr = createXhr();
    //2.创建请求
    var uname = $("#uname").val();
    var url = "/01-checkuname?uname="+uname;
    xhr.open('get', url, false);
    //3.设置回调函数
    xhr.onreadystatechange=function () {
        if(xhr.readyState==4&&xhr.status==200){
            if(xhr.responseText=="1"){
                $("#uname-show").html("用户名称已存在");
                ret = false;
            }else {
                $("#uname-show").html("通过＼（＾ｏ＾）／ＹＥＳ！");
            }
        }
    };
    //4.发送请求
    xhr.send(null)
    return ret;
}

function registerUser() {
    //验证用户名称在数据库中是否存在
    if(checkUname()){
        /**
         * 请求地址:/01-register
         * 请求方式:post
         * 请求参数1:uname
         * 请求参数2:upwd
         * 请求参数3:uemail
         * 返回值:插入成功或失败的结果
         */
        //1.创建xhr对象
        var xhr = createXhr();
        //2.创建请求
        xhr.open('post', '/register', true);
        //3.设置回调函数
        xhr.onreadystatechange=function () {
            if(xhr.readyState==4&&xhr.status==200){
                alert(xhr.responseText);
            }
        };
        //4.设置请求消息头
        xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
        //5.发送请求
        var uname = $("#uname").val();
        var upwd = $("#upwd").val();
        var uemail = $("#uemail").val();
        var params = "uname="+uname+"&upwd="+upwd+"&uemail="+uemail;
        xhr.send(params);
    }else{
        alert("用户名称已存在，不能注册")
    }
}


// 页面加载后要执行的操作
$(function () {
    //1.为#uname绑定blur事件
    $("#uname").blur(function () {
        checkUname();
    });
    //2.为#btnReg绑定click事件
    $("#btnReg").click(function () {
        registerUser();
    });
});