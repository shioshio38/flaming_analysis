$(window).load(function(){
    function send_ch(btn,did,ev,col_name){
	$.getJSON('/set_info',{'did':did,'event':ev,'col_name':col_name},function(data){
	    btn.css("background-color", "red");
	    btn.css("color",'white');
	    console.log(data);
	});
    }
    $(function(){
	$("#acMenu dt").on("click", function() {
	    $(this).next().slideToggle();
	});
    });
    $('button').on('click', function(){
	var btn=$(this);
	var ev=$(this).data('event');
	var did=$(this).data('id');
	var col_name=$(this).data('col_name')
	console.log("col_name=:"+col_name+"\tevent=:"+ev+"\tdid="+did);
	send_ch(btn,did,ev,col_name);
	if(ev=='reset'){
	    var rl=['criticism_','intoline_','adovocacy_','impression_','other_','unknown_','duplicate_','irrelevant_','reset_'];
	    $.each(rl,function(i,m){
		var kk='button#'+m+did;
		console.log(kk);
		var b=$(kk);
		console.log(b);
		b.css("background-color", "lightgray");
		b.css("color",'black');
	    });
	}
    });
});
