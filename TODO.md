## TODO:

### Important Tasks:

###### UI Work:
 * Add layout for image displays
 * Add button to open a QWidget containing the video feed

 * Put the behavior class inside of the image processor and pass the
 whole processor to the slider widget. Get the behavior from the processor
 and use that to setup the widget. Connect the slider widget on_val_changed
 signal with a slot inside of each image processor. When the slider value is changed
 do the processing (possibly pass the output window into the processor also,
 so that the processor can display the image automatically.

###### Technical Work:
 * Integrate filtering behaviors into the project
    * Subclass an abstract behavior model for these
 * Integrate the ability to open up webcam and apply live image recognition to the video feed