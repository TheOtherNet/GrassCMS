/*
    GrassCMS - CMS for the mases
    Copyright (C) 2012 GrassCMS team

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU General Public License
    as published by the Free Software Foundation; either version 2
    of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

    GrassCMS javascript functions.
*/

/* Action ajax */
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
        url:'/text_blob/' + page_name +"/", 
        method: 'POST',
        complete: function(data){ console.debug("DONE");  location.reload(true); } 
    }); 
}

function update_blob(obj, page_id, id){
    $.ajax({
        url:'/text_blob/' + page_id + "/" +  id ,
        method: 'POST',
        type: 'POST',
        data: { 
            'text': obj
        },
        success: function(data){ 
            console.debug(data);  
        } 
    }); 
}

function get_links(blog, data){
    var data = $.parseJSON(data), data_2 = "";
    $(data).each(function(element){  data_2 += "<li><a href=\"/" + blog + "/" + data[element] + "\"> " + data[element] + "</a></li>";  });
    console.debug(data_2);
    console.debug(data);
    return "<ul style='list-style:none; display:inline; margin-right:3px;'>"+ data_2 + "</ul>";
}

function unassign_menu(blog, blog_id){
    return ;
}

function delete_image(blog, image_id){
    return ;
}

function assign_menu(blog_id){ 
    $.ajax({
        url:'/update_menu/' + blog_id +'/', 
        type : 'POST', 
        success: function(data_){
            location.reload(true);
        } 
    }); 
}
        
function create_page(blog_id){ 
    $.ajax({
        url:'/new_page/' + $('#new_page').val(),
        success: function(data){ 
            assign_menu(blog_id);
        } 
    })
}

/* Position and dimensions stuff */

function get_txt_pos(obj) {
    return $(obj).attr('id') + "?x=" + $(obj).css('top').replace('px','') + "&y=" + $(obj).css('left').replace('px',''); 
}

function get_pos(obj, ui, class_) { 
    return $(obj).children(class_).attr('id').replace(class_.replace('.',''), '') + "?x=" + ui.position.top + "&y=" + ui.position.left; 
}

function get_dimensions(obj, ui, class_){ 
    return $(obj).children(class_).attr('id').replace(class_.replace('.',''), '') + "?width=" + ui.size.width + "&height=" + ui.size.height; 
}

function get_txt_stored_dimensions(editor){ var name = editor.name;
    $.getJSON('/get/' + name.replace('text_', ''), function(where){ 
        editor.resize(where[2], where[3]);
    });
}

function get_txt_current_dimensions(name){
    return new Array($('#cke_' + name).css('width').replace('px',''), $('#cke_' + name).css('height').replace('px',''));
}

function addevents(editor){
    editor=CKEDITOR.instances[$(editor).attr('id')];
    get_txt_stored_dimensions(editor);
    editor.on( 'saveSnapshot', function(e) { save(e.editor); });

    editor.on("blur", function(event) { 
            $('.container').css('height','auto');
            $("#handler_" + event.editor.name ).toggle(); 
            $("#cke_top_" + event.editor.name ).toggle(); 
            $("#cke_bottom_" + event.editor.name ).toggle(); 
            save(event.editor)
    });

    editor.on("focus", function(event) { 
        $('.container').css('height','5em');
        $("#handler_" + event.editor.name ).toggle(); 
        $("#cke_top_" + event.editor.name ).toggle(); 
        $("#cke_bottom_" + event.editor.name ).toggle(); 
        save(event.editor);
    });
}

/* setup images and text */

function setup_static_html(){
    $.each($('.static'), function(it){
        var static_=$(this);
        static_.parent().css('top',  '100px');
        static_.parent().css('left', '100px');
        $.getJSON('/get/' + static_.attr('id'), function(where){
            static_.parent().css('top',  where[0] + "px");
            static_.parent().css('left', where[1] + "px"); 
        }); 
    });

    $('.static').resizable({ 
            stop: function(ev, ui){ 
                $.ajax({ url: '/set_dimensions/html/' + get_dimensions(this, ui, '.static_html')}); }}).parent().draggable({
                    stop: function(ev, ui){ $.ajax({ url: '/set_position/html/' + get_pos(this, ui, '.static')});}});

}

function setup_images(){
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
        stop: function(ev, ui){ $.ajax({ url: '/set_dimensions/file/' + get_dimensions(this, ui, 'img')}); }}).parent().draggable({stop: function(ev, ui){ $.ajax({ url: '/set_position/file/' + get_pos(this, ui, 'img')});}});

    $('.img').resizable().parent().draggable();

}

function setup_text(){
    $('.draggable').draggable({handle: '.handler', stop: function(ev, ui){ $.ajax({ url: '/set_position/text/' + get_txt_pos(this, ui)});}});
    $('.CKeditor_blob').ckeditor(addevents);
}

/* other */
function grasscms_startup(){
    setup_images();
    setup_static_html();
    setup_text();
    $('#fakefiles').live('click', function () { $('#files').click(); });
}

function display_toolbar(id){
    var id = id + ' .ToolBar';
    $(id).toggle();
}
