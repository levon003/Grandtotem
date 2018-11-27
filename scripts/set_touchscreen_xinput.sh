#!/bin/bash
# Sets the inputs for the touchscreen correctly
# See these links:
#  https://www.raspberrypi.org/forums/viewtopic.php?t=172025
#  https://wiki.ubuntu.com/X/InputCoordinateTransformation

xinput --set-prop "深圳市全动电子技术有限公司 ByQDtech 触控USB鼠标" 'Coordinate Transformation Matrix' 0 -1 1 1 0 0 0 0 1

echo "Finished."
