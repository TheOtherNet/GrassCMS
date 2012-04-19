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

function get_current_page(){
    a=location.pathname.match(/\/(.*)/);
    if (!a){ return "index"; }
    return a[1];
}

function get_number(id){
    return id.replace(/[a-z]/gi, '').replace('_','');
}

function ready_fake_files(){ $('#fakefiles').live('click', function () { $('#files').click(); }); }

function increment_zindex(elem){ var target=$(elem); 
    var id = target.attr('id').replace(/[a-z]/gi, '').replace('_','');
    var type = target.data('type');
    if (target.css('z-index') == "auto" ){ target.css('z-index', 2); }
    target.css('z-index', parseInt(target.css('z-index'), 10) + 1 );
    $.ajax({ url: "/set/zindex/" + type + "/" + id + "/" + target.css('z-index') })  // TODO: This only supports images =(
}
            
function downgrade_zindex(elem){ target=$(elem); 
    var id = target.attr('id').replace(/[a-z]/gi, '').replace('_','');
    var type = target.data('type');
    if (target.css('z-index') == "auto" ){ target.css('z-index', 1); }
    target.css('z-index', parseInt(target.css('z-index'), 10) - 1 );
    $.ajax({ url: "/set/zindex/" +type+"/" + id + "/" + target.css('z-index')})  // TODO: This only supports images =(
}

function delete_page(){
    if (page_id == "index"){ alert ("You cannot delete index page"); return false; }
    $.ajax({ url:'/delete/page/' + get_current_page(), 
        success: function(data){ 
            new_object('menu', get_current_page()); 
            document.location.href="/"; 
    }});
}

function create_page(){ 
    new_object('page', $('#new_page').val());
    new_object('menu', get_current_page());
}

function grasscms_startup(){ 
    $('video,audio').mediaelementplayer(/* Options */);
    $(".draggable-x-handle").each(function() { makeGuideX(this); });
    $(".draggable-y-handle").each(function() { makeGuideY(this); });


    $('textarea').each(function(){ 
        id=$(this).parent().attr('id') + "_textarea"; 
        $(this).attr('id', id); 
        $('#'+id).wysihtml5({"events": {
            "focus": function(el) { 
                $(this.textareaElement.parentNode).children('.handler').show()
                $(this.toolbar.container).show();
            },
            "blur": function() { 
                $(this.textareaElement.parentNode).children('.handler').hide()
                $(this.toolbar.container).hide();
            },
            "change": function() { 
                update_blob(this.composer.doc.body.innerHTML, 
                    get_current_page(), 
                    get_number($(this.textarea.element).attr('id')) ); 
            }
        }}); 
    });

    $('.static_html').persistent('static_html');

    setup_standard_tools();
    ready_fake_files();
    $('#filedrag').disableSelection();
}

function setup_standard_tools(){

    $("#filedrag>div>img").hoverIntent({    
        timeout: 500, 
        out: function(e){ $('.standard_tools').hide(); }, 
        over: function(e){ $(e.currentTarget).parent().children('.standard_tools').show(); }
    });

    $("#filedrag>div>textarea").hoverIntent({    
        timeout: 500, 
        out: function(e){ $(e.currentTarget).children('.standard_tools').parent().hide(); }, 
        over: function(e){ $(e.currentTarget).children('.standard_tools').parent().show(); }
    });

    $("#filedrag>div").hoverIntent({    
        timeout: 500, 
        out: function(e){ $(e.currentTarget).children('.standard_tools').hide(); }, 
        over: function(e){ $(e.currentTarget).children('.standard_tools').show(); }
    });

    $('.slider').slider({ 
        min: 0, 
        max: 1, 
        step: 0.01, 
        value: 1,
        orientation: "horizontal",
        slide: function(e,ui){ // HOrrible hacks =(
            target = get_o(e.target);
            $.ajax({ url: "/set/opacity/" + target.attr('id') + "/" + ui.value }) 
            $(e.target).css('opacity', ui.value);
        }
    });
}

function get_o(object){ return $(object).parent().parent().parent().parent();}
function assign_menu(){ new_object('menu'); }

function delete_(object){
    $.ajax({
        url:'/delete/' + object.attr('id'),
        type : 'DELETE', 
        success: function(data_){ object.hide(); }
    });
}

function new_object(type, page){
    /*
        Assign / Update a menu to a blog.
        After successful creation, it reloads the page.
    */
    if (!page){ page=get_current_page(); }
    $.ajax({
        url:'/new/' + type +'/' + page,
        type : 'POST', 
        success: function(data_){ 
            if ( type == "menu"  && $('.menu')){ 
                $(".menu").html(data_); 
                $('.static_html').persistent('static_html'); // TODO
            } else {
                $('#filedrag').append(data_); 
           } 
        }
    }); 
}
