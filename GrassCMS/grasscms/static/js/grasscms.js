function update_file(obj, id){ 
    $.ajax({
        url:'/update_file/' + id,
        data: {
            'text': $(obj).val() 
        },
        success: function(data){
            console.debug(data);  
        } 
    });
}

function get_blob(page_name){
    blob="";
    $.ajax({
        type : 'POST', 
        url:'/text_blob/' + page_name, 
        complete: function(data){ console.debug("DONE");  location.reload(true); } 
    }); 
}

function update_blob(obj, page_id, id){
    $.ajax({
        url:'/text_blob/' + id, 
        data: { 
            'text': $(obj).val() 
        },
        success: function(data){ 
            console.debug(data);  
        } 
    }); 
}

function get_menu(blog_id){ 
    $.ajax({
        url:'/get_menu/' + blog_id,
        success: function(data){ 
            document.location.href=document.location.href; 
        } 
    }); 
}
        
function create_page(){ 
    $.ajax({
        url:'/new_page/' + $('#new_page').val(),
        success: function(data){ 
            document.location.href=data; 
        } 
    })
}

function get_txt_pos(obj, ui) {
var id=$(obj).children('span').children('.jHtmlArea').children('textarea').attr('id');
return id.replace('text_', '') + "?x=" + ui.position.top + "&y=" + ui.position.left; 
}

function get_pos(obj, ui) { 
    return $(obj).children('img').attr('id') + "?x=" + ui.position.top + "&y=" + ui.position.left; 
}

function get_dimensions(obj, ui){ 
    var a=$(obj).children('img').attr('id') + "?width=" + ui.size.width + "&height=" + ui.size.height; 
    console.debug(a); return a;
}

function grasscms_startup(){
    $.each($('.img'), function(it){
        var img=$(this);
        img.parent().css('top',  '100px');
        img.parent().css('left', '100px');
        $.getJSON('/get/' + img.attr('id'), function(where){
            img.parent().css('top',  where[0] + "px");
            img.parent().css('left', where[1] + "px"); 
        }); 
    });

    $('.img').resizable({ 
        stop: function(ev, ui){ 
            $.ajax({ url: '/set_dimensions/file/' + get_dimensions(this, ui)});
        }
    }).parent().draggable({ 
        stop: function(ev, ui){ 
            $.ajax({ url: '/set_position/file/' + get_pos(this, ui)});}
    });

    $("textarea").htmlarea();     
/*
    $('.text_blob').resizable( {
        alsoResize: '.text_blob textarea', 
        stop: function(ev, ui){ 
            $.ajax({ url: '/set_dimensions/file/' + get_dimensions(this, ui)});
        }
    }).draggable({ 
        stop: function(ev, ui){ 
            $.ajax({ url: '/set_position/file/' + get_pos(this, ui)});}
    });

    $('.text_rst').resizable({ 
        stop: function(ev, ui){ 
            $.ajax({ url: '/set_dimensions/file/' + get_dimensions(this, ui)});
        }
    }).draggable({ 
        stop: function(ev, ui){ 
            $.ajax({ url: '/set_position/file/' + get_pos(this, ui)});}
    });    
*/ // FIXME: Resizable is not working properly.

    $('.text_blob').draggable({ 
        stop: function(ev, ui){ 
            $.ajax({ url: '/set_position/text/' + get_txt_pos(this, ui)});}
    });
    $('.text_rst').draggable({ 
        stop: function(ev, ui){ 
            $.ajax({ url: '/set_position/text/' + get_txt_pos(this, ui)});}
    });    
    

}
