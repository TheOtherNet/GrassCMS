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

function persistent(class_, type, use_parent){
    /*
        Make an object transparently persistent in size and position.
        @param class_: Base div class (You have to include the ".")
        @param type: Type, usually this is the child's class.
    */

    $.each($(class_), function(it){
        var element=$(this); // get the element in a variable, for future usage. This is probably better in performance
        if (element.parent().attr('id') != "filedrag" || class_ == ".img" ){
            element.parent().css('top',  '0px'); // Default top and left values to 100px, so that will be the start of every object
            element.parent().css('left', '0px');
        }
        $.getJSON('/get_position/' + type + "/" + element.attr('id'), function(where){ // Get the object's position
                if (element.parent().attr('id') != "filedrag" || class_ == ".img" ){
                    element.parent().css('top',  where[0] + "px"); // And apply it to current object
                    element.parent().css('left', where[1] + "px"); 
                } else {
                    element.css('top',  where[0] + "px"); // And apply it to current object
                    element.css('left', where[1] + "px"); 
                }
        });
    });

    if ( $(class_).parent().attr('id') != "filedrag" || class_ == ".img" ){

        $(class_).resizable({ // Make it resizable
            stop: function(ev, ui){  // When you stop the resize, execute the ajax call to set it on the server.
                $.ajax(
                    { 
                        url: '/set_dimensions/' + type + "/" +
                        $(this).children(type).attr('id').replace(type.replace('.',''), '') + // This means child's ids need to be {type}{id}
                        "?width=" + ui.size.width + "&height=" + ui.size.height 
                    }
                );
            }
        }).parent().draggable({
            stop: function(ev, ui){
                if (class_ != ".static_html"){
                     $.ajax(
                        {
                            url: '/set_position/' + type + "/" +
                            $(this).children(type).attr('id').replace(type, '') +
                            "?x=" + ui.position.top + "&y=" + ui.position.left
                        });
                } else {
                     $.ajax(
                        {
                            url: '/set_position/' + type + "/" +
                            $(this).attr('id').replace(type, '') +
                            "?x=" + ui.position.top + "&y=" + ui.position.left
                        });
                }
            }
        }); 

    } else {

        $(class_).resizable({ // Make it resizable
            stop: function(ev, ui){  // When you stop the resize, execute the ajax call to set it on the server.
                $.ajax(
                    { 
                        url: '/set_dimensions/' + type + "/" +
                        $(this).children(type).attr('id').replace(type.replace('.',''), '') + // This means child's ids need to be {type}{id}
                        "?width=" + ui.size.width + "&height=" + ui.size.height 
                    }
                );
            }
        }).draggable({
            stop: function(ev, ui){
                if (class_ != ".static_html"){
                     $.ajax(
                        {
                            url: '/set_position/' + type + "/" +
                            $(this).children(type).attr('id').replace(type, '') +
                            "?x=" + ui.position.top + "&y=" + ui.position.left
                        });
                } else {
                     $.ajax(
                        {
                            url: '/set_position/' + type + "/" +
                            $(this).attr('id').replace(type, '') +
                            "?x=" + ui.position.top + "&y=" + ui.position.left
                        });
                }
            }
        }); 

    }

}

/* other */
function grasscms_startup(){
    /*
        Startup function, called on every admin page init.
    */
    persistent('.img', 'img'); // Make images and static html widgets persistent
    persistent('.static_html', 'menu');
    setup_text(); // Make text editor persistent
    $(".draggable-x-handle").each(function() { makeGuideX(this); });
    $(".draggable-y-handle").each(function() { makeGuideY(this); });
    $('#fakefiles').live('click', function () { $('#files').click(); }); // Stylize file input.
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


