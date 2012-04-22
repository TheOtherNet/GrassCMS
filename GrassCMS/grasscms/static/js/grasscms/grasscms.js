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

jQuery.fn.outerHTML = function(s) {
    return s
        ? this.before(s).remove()
        : jQuery("<p>").append(this.eq(0).clone()).html();
};


function get_current_page(){
    a=location.pathname.match(/\/(.*)/);
    if (a == ""){ return "index"; }
    return a[1];
}

function get_o(object){ 
    return $(object).parent().parent().parent().parent();
}

function get_number(id){
    return id.replace(/[a-z]/gi, '').replace('_','');
}

function increment_zindex(target){ 
    $(target).persistentcss('z-index', parseInt(target.css('z-index'), 10) + 1 );
}
            
function downgrade_zindex(target){
    $(target).persistentcss('z-index', parseInt(target.css('z-index'), 10) - 1 );
}

function delete_page(){
    if (get_current_page() == "index"){ alert ("You cannot delete index page"); return false; }
    $.ajax({
        url:'/delete/page/' + get_current_page(),
        type : 'DELETE', 
    });
    new_object('menu', 'index'); 
    document.location.href="/"; 
}

function create_page(){ 
    new_object('page', $('#new_page').val());
    new_object('menu', get_current_page());
}


function delete_(object){
    $.ajax({
        url:'/delete/' + $(object).attr('id') + "/", 
        type : 'DELETE', 
        success: function(data_){ $(object).hide(); }
    });
}

function new_object(type, page){
    /*
        Assign / Update a menu to a blog.
        After successful creation, it reloads the page.
    */
    if (!page || page == ""){ page=get_current_page(); }
    if (!page || page == ""){ page="index"; }
    $.ajax({
        url:'/new/' + type +'/' + page,
        type : 'POST', 
        success: function(data_){ 
            if ( type == "menu"  && $('.menu')[0]){ 
                $(".menu").html(data_); 
                $('.static_html').persistent('static_html'); // TODO
                document.location.reload();
            } else {
                $('#filedrag').append(data_); 
                document.location.reload();
           } 
        }
    }); 
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
                $(this.textareaElement.parentNode).children('iframe').toggleClass('with_shadow');
                $(this.toolbar.container).show();
            },
            "blur": function() { 
                $(this.textareaElement.parentNode).children('iframe').toggleClass('with_shadow');
                $(this.textareaElement.parentNode).children('.handler').hide()
                $(this.toolbar.container).hide();
            },
            "change": function() { window.foo=this;
                $(this.textareaElement).persistentdata('content', this.composer.doc.body.innerHTML);
            }
        }}); 
    });

    setup_standard_tools();
    $('#fakefiles').live('click', function () { $('#files').click(); }); 
    $('#filedrag').disableSelection();
    $('.static_html').persistent('static_html');
    $('.static_html').each(function(){ $('#'+$(this).attr('id')).rotatable(); });
    $('.slider').each(function(){
        $(this).slider({ 
            min: 0, 
            max: 1, 
            step: 0.1, 
            value: $(this).parent().parent().parent().css('opacity'), // TODO This should NOT be one, clearly.
            orientation: "horizontal",
            slide: function(e,ui){
                if ($(e.target).parent().parent().parent().parent().attr('id') != "filedrag"){
                    $(e.target).parent().parent().parent().parent().persistentcss('opacity', ui.value);
                }
            }
        });
    });
    options={placement:'bottom'}; 
    $('#addpage').tooltip(options); 
    $('#addmenu').tooltip(options);
    $('#addtext').tooltip(options);
    $('#fakefiles').tooltip(options);
    $('#delpage').tooltip(options);

}

function setup_standard_tools(){

    $("#filedrag>div").hoverIntent({    
        timeout: 500, 
        out: function(e){ $(e.currentTarget).children('.standard_tools').hide(); }, 
        over: function(e){ $(e.currentTarget).children('.standard_tools').show(); }
    });


}
