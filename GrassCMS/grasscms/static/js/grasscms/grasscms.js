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

function show_standard_tools(e){ $(e).children('.standard_tools').show(); }
function hide_standard_tools(e){ $(e).children('.standard_tools').hide(); }
function ready_fake_files(){ $('#fakefiles').live('click', function () { $('#files').click(); }); }

function increment_zindex(elem){ var target=$(elem); 
    target.css('z-index', parseInt(target.css('z-index'), 10) + 1 );
    $.ajax({ url: "/set_zindex/img/" + target.attr('id').replace('img','') + "/" + target.css('z-index') })  // TODO: This only supports images =(
}
            
function downgrade_zindex(elem){ target=$(elem); 
    target.css('z-index', parseInt(target.css('z-index'), 10) - 1 );
    $.ajax({ url: "/set_zindex/img/" + target.attr('id').replace('img','') + "/" + target.css('z-index')})  // TODO: This only supports images =(
}

function delete_page(page_id){
    if (page_id == "index"){ alert ("You cannot delete index page"); return false; }
    $.ajax({ url:'/delete_page/' + page_id, success: function(data){ document.location.href(data); }});
}

function create_page(blog_id){ 
    /*
        Create a new page in the blog
        @param blog_id: Sadly, this has to be passed on, this should be considered a bug!
    */
    $.ajax({
        url:'/new_page/' + $('#new_page').val(), // Get page name
        success: function(data){ 
            assign_menu(blog_id); // Update the menu on page input. This requires static_html.js to be loaded
            document.location.reload(true);
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
        if (element.children(type).length > 0){ 
            var id = element.children(type).attr('id').replace(/[a-z]/gi, '').replace('_','');
        } else {
            var id = element.attr('id').replace(/[a-z]/gi, '').replace('_','');
        }
        if (element.parent().attr('id') != "filedrag" ){ element=element.parent();}

        element.data('id', $(this).attr('id'));
        element.data('type', type);

        if (element.parent().attr('id') == "filedrag" && type != "img"){ 
            element.resizable({ stop: function(ev, ui){ set_dimensions(type, id, ui); }}).draggable({ stop:function(ev, ui){ set_position(type, id, ui); }});
        } else {
            element.resizable({ stop: function(ev, ui){ set_dimensions(type, id, ui); }}).parent().draggable({ stop:function(ev, ui){ set_position(type, id, ui); }});
            element=element.parent()
        }
            
        element.append($('#standard_tools_model').html());        
        $.getJSON('/get_position/' + type + "/" + id, function(where){
            element.css('top',  where[0] + "px");
            element.css('left', where[1] + "px"); 
        });

        var element=$(this); 
        id_=element.attr('id').replace('img','').replace($(element.data('type')), '');
        
        $.ajax({ url: "/get_zindex/" + element.data('type') +"/" + id_, complete: function(data){ 
           zindex=$.parseJSON(data.responseText); 
           element.css('z-index', zindex);
        }});  // TODO: This only supports images =(

        $.ajax({ url: "/get_opacity/" + element.data('type')+ "/" + id_, complete: function(data){ 
           opacity=$.parseJSON(data.responseText); 
           element.css('opacity', opacity);
        }});  // TODO: This only supports images =(

        $.ajax({ url: "/get_rotation/"+ element.data('type') +"/" + id_, complete: function(data){ 
           degree=$.parseJSON(data.responseText); 
           element.css('-moz-transform', 'rotate(' + degree + 'deg)');
           element.css('-webkit-transform', 'rotate(' + degree + 'deg)');
           element.css('-o-transform', 'rotate(' + degree + 'deg)');
           element.css('-ms-transform', 'rotate(' + degree + 'deg)');
        }});  // TODO: This only supports images =(
    });
}});

function grasscms_startup(){
    // Set up media element player
    $('video,audio').mediaelementplayer(/* Options */);
    // Make stuff persistent
    $('.img').persistent('img'); // Make widgets and static html widgets persistent
    $('.static_html.menu').persistent('static_html');
    $('.static_html.video').persistent('video');
    // Setup standard tools
    setup_standard_tools();
    // Get file upload button ready
    ready_fake_files();
    // Setup text editor
    setup_text(); // Make text editor persistent
    // Add x and y handles
    $(".draggable-x-handle").each(function() { makeGuideX(this); });
    $(".draggable-y-handle").each(function() { makeGuideY(this); });
    // Disable selection on filedrag
    $('#filedrag').disableSelection();
}

function setup_standard_tools(){
    return;
    $("#filedrag>div").hoverIntent({    
        timeout: 500, 
        out: function(e){ hide_standard_tools($(e.currentTarget));},
        over: function(e){ show_standard_tools($(e.currentTarget));},
    });
    $('.slider').slider({ 
        min: 0, 
        max: 1, 
        step: 0.01, 
        value: 1,
        orientation: "horizontal",
        slide: function(e,ui){
            if ($(e.target).parent().parent().parent().parent().data('type') == "static_html"){
                target=$(e.target).parent().parent().parent().parent();
            } else {
                target=$(e.target).parent().parent().parent().parent().children('.'+$(e.target).data('type'));
            }
            if ($(e.target).parent().parent().parent().data('type') == "video"){
                target=$(e.target).parent().parent().parent();
            }

            type = $(target).data('type');
            id_=$(target).attr('id').replace($(target).data('type'), '').replace('menu','');

            $.ajax({ url: "/set_opacity/" +type+"/" + id_ + "/" + ui.value })  // TODO: This only supports images =(
        }
    });
}
