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


function ready_fake_files(){ $('#fakefiles').live('click', function () { $('#files').click(); }); }

function increment_zindex(elem){ var target=$(elem); 
    var id = target.attr('id').replace(/[a-z]/gi, '').replace('_','');
    var type = target.data('type');
    if (target.css('z-index') == "auto" ){ target.css('z-index', 2); }
    target.css('z-index', parseInt(target.css('z-index'), 10) + 1 );
    $.ajax({ url: "/set_zindex/" + type + "/" + id + "/" + target.css('z-index') })  // TODO: This only supports images =(
}
            
function downgrade_zindex(elem){ target=$(elem); 
    var id = target.attr('id').replace(/[a-z]/gi, '').replace('_','');
    var type = target.data('type');
    if (target.css('z-index') == "auto" ){ target.css('z-index', 1); }
    target.css('z-index', parseInt(target.css('z-index'), 10) - 1 );
    $.ajax({ url: "/set_zindex/" +type+"/" + id + "/" + target.css('z-index')})  // TODO: This only supports images =(
}

function delete_page(page_id){
    if (page_id == "index"){ alert ("You cannot delete index page"); return false; }
    $.ajax({ url:'/delete_page/' + page_id, success: function(data){ assign_menu(); document.location.href="/"; }});
}

function create_page(){ 
    /*
        Create a new page in the blog
        @param blog_id: Sadly, this has to be passed on, this should be considered a bug!
    */
    $.ajax({
        url:'/new_page/' + $('#new_page').val(), // Get page name
        success: function(data){ 
            assign_menu(); // Update the menu on page input. This requires static_html.js to be loaded
        } 
    })
}

function makeGuideY(dom_element) {
    $(dom_element).draggable({
        axis: "y",
        containment: "#filedrag",
        drag: function() {
            var position = $(this).position();
            var yPos = $(this).css('top');
            $(this).find($('.pos')).text('Y: ' + yPos);
        },
        start: function() {
            $(this).find($('.pos')).css('display', 'block');
        },
        stop: function() {
            $(this).find($('.pos')).css('display', 'none');

            if ($(this).hasClass("draggable-y-newest")) {
                $(this).removeClass("draggable-y-newest");
                $("#filedrag .y-guide").clone().removeClass("y-guide").addClass("draggable-y-newest").appendTo("#filedrag").each(function() {
                    makeGuideY(this);
                });
            }
        }
    });
}

function makeGuideX(dom_element) {
    $(dom_element).draggable({
        axis: "x",
        containment: "#filedrag",
        drag: function() {
            var position = $(this).position();
            var xPos = $(this).css('left');
            $(this).find($('.pos')).text('X: ' + xPos);
        },
        start: function() {
            $(this).find($('.pos')).css('display', 'block');
        },
        stop: function() {
            $(this).find($('.pos')).css('display', 'none');

            if ($(this).hasClass("draggable-x-newest")) {
                $(this).removeClass("draggable-x-newest");
                $("#filedrag .x-guide").clone().removeClass("x-guide").addClass("draggable-x-newest").appendTo("#filedrag").each(function() {
                    makeGuideX(this);
                });
            }
        }
    });
}

jQuery.fn.extend({ 
        disableSelection : function() { 
                return this.each(function() { 
                        this.onselectstart = function() { return false; }; 
                        this.unselectable = "on"; 
                        jQuery(this).css('user-select', 'none'); 
                        jQuery(this).css('-o-user-select', 'none'); 
                        jQuery(this).css('-moz-user-select', 'none'); 
                        jQuery(this).css('-khtml-user-select', 'none'); 
                        jQuery(this).css('-webkit-user-select', 'none'); 
                }); 
        } 
}); 

function update_object(element, what, properties, transform){
        if (!transform){ transform="elem";}
        $.ajax({ url: "/get/" + what + "/" + element.data('type') +"/" + element.data('id'),
            success: function(data){ 
                $(properties).each(function(){ 
                    element.children('.img').css('top', "auto").css('left', 'auto');
                    element.css(this +"", transform.replace('elem', data));
                });
            }
        }); 
}

jQuery.fn.extend({
    persistent: function(type){
    /*
        Make an object transparently persistent in size and position.
        @param type: Type, how to identify this kind of object in the server 
    */

    function set_dimensions(type, id, ui){ $.ajax({ url: '/set_dimensions/' + type + "/" + id + "?width=" + ui.size.width + "&height=" + ui.size.height });}
    function set_position(type, id, ui){ if ( rotating && type == "img" ){  return false; }; $.ajax({url: '/set_position/' + type + "/" + id + "?x=" + ui.position.top + "&y=" + ui.position.left }); }


    return this.each(function(){ 
        var element=$(this); 
        console.debug(element);
        if (element.children(type).length > 0){ 
            var id = element.children(type).attr('id').replace(/[a-z]/gi, '').replace('_','');
        } else {
            var id = element.attr('id').replace(/[a-z]/gi, '').replace('_','');
        }

        if (element.parent().attr('id') != "filedrag" ){ element=element.parent();}
        if (type == "img"){ element.resizable({ stop: function(ev, ui){ set_dimensions(type, id, ui); }}).parent().draggable({ stop:function(ev, ui){ set_position(type, id, ui); }} ); element=element.parent(); } else { element.resizable({ alsoResize: element.children('textarea'), stop: function(ev, ui){ set_dimensions(type, id, ui); }} ).draggable({ stop:function(ev, ui){ set_position(type, id, ui); }} ); }

        if (type == "img"){ 
            element.parent().data('id', id);
            element.parent().data('type', type);
        } 
        element.data('id', id);
        element.data('type', type);
        element.append($('#standard_tools_model').html());
 
        update_object(element, 'zindex', Array('opacity'));
        update_object(element, 'opacity', Array('opacity'));
        update_object(element, 'rotation', Array('-moz-transform', '-webkit-transform', '-o-transform', '-ms-transform'), 'rotate(elem)');
        update_object(element, 'x', Array('top'), 'elempx');
        update_object(element, 'y', Array('left'), 'elempx');
    });
}});

function get_current_page(){
    a=location.pathname.match(/\/page\/(.*)/)[1];
    if (!a){ return "index"; }
    return a
}

function get_number(id){
    return id.replace(/[a-z]/gi, '').replace('_','');
}

function grasscms_startup(){ 
    console.debug(get_current_page());
    $('video,audio').mediaelementplayer(/* Options */);
    $('.img').persistent('img'); // Make widgets and static html widgets persistent

    $('.static_html').persistent('static_html');
    $('textarea').each(function(){ id=$(this).parent().attr('id') + "_textarea"; $(this).attr('id', id); $('#'+id).wysihtml5({"events": {
        "focus": function(el) { 
            $(this.textareaElement.parentNode).children('.handler').show()
            $(this.toolbar.container).show();
        },
        "blur": function() { 
            $(this.textareaElement.parentNode).children('.handler').hide()
            $(this.toolbar.container).hide();
        },
        "change": function() { console.debug("CHANGED"); 
            update_blob(this.composer.doc.body.innerHTML, get_current_page(), get_number($(this.textarea.element).attr('id')) ); 
        }}} ); });
    $('.static_html.video').persistent('video');
    setup_standard_tools();
    ready_fake_files();
    $(".draggable-x-handle").each(function() { makeGuideX(this); });
    $(".draggable-y-handle").each(function() { makeGuideY(this); });
    $('#filedrag').disableSelection();
    $(document).mousemove( mouse );
}

function setup_standard_tools(){
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
            if ($(e.target).parent().parent().parent().parent().data('type') == "static_html"){
                target=$(e.target).parent().parent().parent().parent();
            } else {
                target=$(e.target).parent().parent().parent().parent().children('.'+$(e.target).parent().parent().parent().parent().data('type'));
            }
            if ($(e.target).parent().parent().parent().data('type') == "video"){
                target=$(e.target).parent().parent().parent();
            }
            $.ajax({ url: "/set_opacity/" + target.parent().data('type')+"/" + target.parent().data('id') + "/" + ui.value })  // TODO: This only supports images =(
            target.css('opacity', ui.value);
        }
    });
}
