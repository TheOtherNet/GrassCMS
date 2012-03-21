var newImageZIndex = 1;         // To make sure newly-loaded images land on top of images on the table
var loaded = false;             // Used to prevent initPhotos() running twice
var imageBeingRotated = false;  // The DOM image currently being rotated (if any)
var mouseStartAngle = false;    // The angle of the mouse relative to the image centre at the start of the rotation
var imageStartAngle = false;    // The rotation angle of the image at the start of the rotation

function startRotate( e ) {
    console.debug(e.shiftKey);
  // Exit if the shift key wasn't held down when the mouse button was pressed
  if ( !e.shiftKey ) return;

  // Track the image that we're going to rotate
  imageBeingRotated = this;
  console.debug(imageBeingRotated);
  // Store the angle of the mouse at the start of the rotation, relative to the image centre
  var imageCentre = getImageCentre( imageBeingRotated );
  var mouseStartXFromCentre = e.pageX - imageCentre[0];
  var mouseStartYFromCentre = e.pageY - imageCentre[1];
  mouseStartAngle = Math.atan2( mouseStartYFromCentre, mouseStartXFromCentre );

  // Store the current rotation angle of the image at the start of the rotation
  imageStartAngle = $(imageBeingRotated).data('currentRotation');
    console.debug("BAZ");
    console.debug(imageStartAngle);
  // Set up an event handler to rotate the image as the mouse is moved
  $(document).mousemove( rotateImage );
  return false;
}

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

function update_widget_rotation(id_, angle){
    console.debug(angle);
    if (!angle || angle == "NAN" ){ return; }
    $.ajax({ url: "/set_rotation/img/" + id_ + "/" + angle })  // TODO: This only supports images =(
    console.debug(id_); console.debug(angle);
}

function make_rotable(class_, type_){
    $('#filedrag ' + class_).each( function(index) { // Preprocess photos to store rotation.
        console.debug("PROCESSING ELEMENT");
        element = this;
        $.ajax({ 
            url: '/get_rotation/' + type_ + "/" + $(this).attr('id').replace(class_.replace('.', ''), ''),
            success: function(angle){ 
               console.debug(angle); console.debug("THAT");
               $(element).css( 'transform', 'rotate(' + angle + 'rad)' );   
               $(element).css( '-moz-transform', 'rotate(' + angle + 'rad)' );   
               $(element).css( '-webkit-transform', 'rotate(' + angle + 'rad)' );
               $(element).css( '-o-transform', 'rotate(' + angle + 'rad)' );
                console.debug("STUFFING");
                console.debug(parseFloat(angle) * Math.PI / 180);
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
    console.debug("FOO");
    console.debug(rotateAngle);
    console.debug(mouseAngle);
    console.debug(mouseStartAngle);
    console.debug(imageStartAngle);
    console.debug("BAR");
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
