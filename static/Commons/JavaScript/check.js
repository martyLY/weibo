
//    用户名
    function YHMonblus(){
        var username=document.getElementById("username");
       // var reN =/^\d{6,18}$/;
        var re = /^[a-zA-Z_]{6,18}$/;
        if(username.value==""){
            document.getElementById('YHMerror').innerText="请输入用户名";
        }
        else if(username.value.length < 6 ||username.value.length > 18){
            console.log(username.value);
            document.getElementById('YHMerror').innerText="格式错误,长度应为6-18个字符";
        }
        else if(!re.test(username.value)){

            document.getElementById('YHMerror').innerText="格式错误,只能包含英文字母和下划线";
        }
        else {
            document.getElementById('YHMerror').innerText ="";
        }
    }
    function YHMonfocu(){
            document.getElementById('YHMerror').innerText ="";
    }
//   密码
    function MMonblus(){
          var password=document.getElementById("upassword");
          var re = /^(?=.*\d)(?=.*[a-zA-Z])[\da-zA-Z]{6,}$/;
         // var reg=/[A-Za-z].*[0-9]|[0-9].*[A-Za-z]/;

        if(password.value==""){
        document.getElementById('MMerror').innerText="请输入密码";
        }
          else if(password.value.length < 6){
             document.getElementById('MMerror').innerText="格式错误,,密码长度至少为6位";
         }

         else if(!re.test(password.value)){
             document.getElementById('MMerror').innerText="格式错误,必须包含英文字母大小写和数字";
        }
         else {
        document.getElementById('MMerror').innerText ="";
        }
}
    function MMonfocu(){
        document.getElementById('MMerror').innerText ="";
    }


//    确认密码
    function QRMMonblus(){
        var password=document.getElementById("qrpassword");
        var confirmPassword=document.getElementById("upassword");
        if(confirmPassword.value==""){
            document.getElementById('QRMMerror').innerText="请输入确认密码";
        }
        else if(password.value != confirmPassword.value){
            document.getElementById('QRMMerror').innerText="两次密码输入不一致";
        }
        else {
            document.getElementById('QRMMerror').innerText ="";
        }
    }
    function QRMMonfocu(){
        document.getElementById('QRMMerror').innerText ="";
    }

//    性别
    function XBonblus(){
//        var radios = document.getElementsByName("gender");
//        if(radios.checked == false){
//            document.getElementById('XBerror').innerText="请选择性别";
//        }else {
//            document.getElementById('XBerror').innerText ="";
//        }
    }
    function XBonfocu(){
//        document.getElementById('XBerror').innerText ="";
    }

//    爱好
    function AHonblus(){
        var hobbys = document.getElementsByName("hobby");
        if(hobbys[0].checked == false&&hobbys[1].checked == false&&hobbys[2].checked == false){
            document.getElementById('AHerror').innerText="请选择爱好";
        }else {
            document.getElementById('AHerror').innerText ="";
        }
    }
    function AHonfocu(){
        document.getElementById('AHerror').innerText ="";
    }
//    联系电话
    function LXDHonblus(){
        var phone=document.getElementById("phone");
        var re = /^1\d{10}$/;
        if(phone.value==""){
            document.getElementById('LXDHerror').innerText="请输入联系电话";
        }
        else if(!re.test(phone)){
            document.getElementById('LXDHerror').innerText="电话格式输入错误";
        }
        else {
            document.getElementById('LXDHerror').innerText ="";
        }
    }
    function LXDHonfocu(){
        document.getElementById('LXDHerror').innerText ="";
    }
//    电子邮箱
    function DZYXonblus(){
        var email=document.getElementById("email");
        var re= /[a-zA-Z0-9]{1,10}@[a-zA-Z0-9]{1,5}\.[a-zA-Z0-9]{1,5}/;
        if(email.value==""){
            document.getElementById('DZYXerror').innerText="请输入电子邮箱";
        }
        else if(!re.test(email.value)){
            document.getElementById("DZYXerror").innerHTML="邮箱格式不正确";
        }
        else {
            document.getElementById('DZYXerror').innerText ="";
        }
    }
    function DZYXonfocu(){
        document.getElementById('DZYXerror').innerText ="";
    }

