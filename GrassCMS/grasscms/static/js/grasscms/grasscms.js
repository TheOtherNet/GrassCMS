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

var newImageZIndex = 1;         // To make sure newly-loaded images land on top of images on the table
var loaded = false;             // Used to prevent initPhotos() running twice
var imageBeingRotated = false;  // The DOM image currently being rotated (if any)
var mouseStartAngle = false;    // The angle of the mouse relative to the image centre at the start of the rotation
var imageStartAngle = false;    // The rotation angle of the image at the start of the rotation



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
                    if ( imageBeingRotated && class_ == ".img" ){  return false; }
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
                    if ( imageBeingRotated && class_ == ".img" ){  return false; }
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

function update_widget_rotation(id_, angle){
    if (!angle || angle == "NAN" ){ return; }
    $.ajax({ url: "/set_rotation/img/" + id_ + "/" + angle })  // TODO: This only supports images =(
    console.debug(id_); console.debug(angle);
}

function make_rotable(class_, type_){
    $('#filedrag ' + class_).each( function(index) { // Preprocess photos to store rotation.
        element = this;
        $.ajax({ 
            url: '/get_rotation/' + type_ + "/" + $(this).attr('id').replace(class_.replace('.', ''), ''),
            success: function(angle){  console.debug(angle);
               $(element).css( 'transform', 'rotate(' + angle + 'rad)' );   
               $(element).css( '-moz-transform', 'rotate(' + angle + 'rad)' );   
               $(element).css( '-webkit-transform', 'rotate(' + angle + 'rad)' );
               $(element).css( '-o-transform', 'rotate(' + angle + 'rad)' );
               $(element).data('currentRotation', angle * Math.PI / 180 );
            }
        });
    });
}


function rotateImage( e ) {

  // Exit if we're not rotating an image
  if ( !e.shiftKey ) return;
  if ( !imageBeingRotated ) return;

  // Calculate the new mouse angle relative to the image centre
  var imageCentre = getImageCentre( imageBeingRotated );
  var mouseXFromCentre = e.pageX - imageCentre[0];
  var mouseYFromCentre = e.pageY - imageCentre[1];
  var mouseAngle = Math.atan2( mouseYFromCentre, mouseXFromCentre );

  // Calculate the new rotation angle for the image
  var rotateAngle = mouseAngle - mouseStartAngle + imageStartAngle;

  // Rotate the image to the new angle, and store the new angle
  $(imageBeingRotated).css('transform','rotate(' + rotateAngle + 'rad)');
  $(imageBeingRotated).css('-moz-transform','rotate(' + rotateAngle + 'rad)');
  $(imageBeingRotated).css('-webkit-transform','rotate(' + rotateAngle + 'rad)');
  $(imageBeingRotated).css('-o-transform','rotate(' + rotateAngle + 'rad)');
  $(imageBeingRotated).data('currentRotation', rotateAngle );
  update_widget_rotation($(imageBeingRotated).attr('id'), rotateAngle)
  return false;
}

// Calculate the centre point of a given image

function getImageCentre( image ) {

  // Rotate the image to 0 radians
  $(image).css('transform','rotate(0rad)');
  $(image).css('-moz-transform','rotate(0rad)');
  $(image).css('-webkit-transform','rotate(0rad)');
  $(image).css('-o-transform','rotate(0rad)');

  // Measure the image centre
  var imageOffset = $(image).offset();
  var imageCentreX = imageOffset.left + $(image).width() / 2;
  var imageCentreY = imageOffset.top + $(image).height() / 2;

  // Rotate the image back to its previous angle
  var currentRotation = $(image).data('currentRotation');
  $(imageBeingRotated).css('transform','rotate(' + currentRotation + 'rad)');
  $(imageBeingRotated).css('-moz-transform','rotate(' + currentRotation + 'rad)');
  $(imageBeingRotated).css('-webkit-transform','rotate(' + currentRotation + 'rad)');
  $(imageBeingRotated).css('-o-transform','rotate(' + currentRotation + 'rad)');

  // Return the calculated centre coordinates
  return Array( imageCentreX, imageCentreY );
}

function startRotate( e ) {
    console.debug(e.shiftKey);
  // Exit if the shift key wasn't held down when the mouse button was pressed
  if ( !e.shiftKey ) return;

  // Track the image that we're going to rotate
  imageBeingRotated = this;

  // Store the angle of the mouse at the start of the rotation, relative to the image centre
  var imageCentre = getImageCentre( imageBeingRotated );
  var mouseStartXFromCentre = e.pageX - imageCentre[0];
  var mouseStartYFromCentre = e.pageY - imageCentre[1];
  mouseStartAngle = Math.atan2( mouseStartYFromCentre, mouseStartXFromCentre );

  // Store the current rotation angle of the image at the start of the rotation
  imageStartAngle = $(imageBeingRotated).data('currentRotation');

  // Set up an event handler to rotate the image as the mouse is moved
  $(document).mousemove( rotateImage );

  return false;
}

// Stop rotating an image

function stopRotate( e ) {

  // Exit if we're not rotating an image
    console.debug("foo");
  if ( !imageBeingRotated ) return;
  console.debug(imageBeingRotated);

  // Remove the event handler that tracked mouse movements during the rotation
  $(document).unbind( 'mousemove' );

  // Cancel the image rotation by setting imageBeingRotated back to false.
  // Do this in a short while - after the click event has fired -
  // to prevent the lightbox appearing once the Shift key is released.
  setTimeout( function() { imageBeingRotated = false; }, 10 );
  return false;
}


function grasscms_startup(){
    /*
        Startup function, called on every admin page init.
    */

    make_rotable('.img', 'img');
  $(document).mouseup( stopRotate );

    persistent('.img', 'img'); // Make widgets and static html widgets persistent
    $('.img').mousedown( startRotate ); // Make widgets rotable
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


