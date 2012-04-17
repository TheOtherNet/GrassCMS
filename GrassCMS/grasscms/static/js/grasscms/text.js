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

function get_txt_stored_dimensions(editor){ var name = editor.name;
    $.getJSON('/get_position/' + name.replace('_', '/'), function(where){ 
        editor.resize(where[2], where[3]);
    });
}

function get_txt_current_dimensions(name){
    return new Array($('#cke_' + name).css('width').replace('px',''), $('#cke_' + name).css('height').replace('px',''));
}

function get_txt_pos(obj) {
    return $(obj).attr('id') + "?x=" + $(obj).css('top').replace('px','') + "&y=" + $(obj).css('left').replace('px',''); 
}

function setup_editor(editor){
    return;
}

function setup_text(){
    $('.draggable').draggable({handle: '.handler', stop: function(ev, ui){ $.ajax({ url: '/set_position/text/' + get_txt_pos(this, ui)});}});
}


function get_blob(page_name){
    $.ajax({
        type : 'POST', 
        url:'/text_blob/' + page_name +"/", 
        method: 'POST',
        success: function(data){ $('#filedrag').append(data); setup_text(); } 
    }); 
}

function update_blob(obj, page_id, id){
    $.ajax({
        url:'/text_blob/' + page_id +"/" +  id  ,
        method: 'POST',
        type: 'POST',
        data: { 
            'text': obj
        },
        complete: function(data){ 
            console.debug(data); 
            console.debug("FOO"); 
        } 
    }); 

}

function delete_text(elem){
    id=$(elem).parent().parent().attr('id').replace('text_','');
    $.ajax({
        url:'/delete_text_blob/' + id ,
        method: 'DELETE',
        type: 'DELETE',
        complete: function(data){ 
            $(elem).parent().parent().hide();
        } 
    }); 
}
