function initSwitch(id,state,change) {
    $(id).bootstrapSwitch({    //初始化按钮 是否拦截
        state:state,
        onText:"是",
        offText:"否",
        onColor:"success",
        offColor:"info",
        onSwitchChange:change
     }); 
}

function write_Clipper(text){
	// 创建input元素，给input传值，将input放入html里，选择input
	var w = document.createElement('input');
	w.value = text;
	document.body.appendChild(w);
	w.select(); 
	// 调用浏览器的复制命令
	document.execCommand("Copy"); 
	// 将input元素隐藏，通知操作完成！
    w.style.display='none';
    w.parentNode.removeChild(w);
}  