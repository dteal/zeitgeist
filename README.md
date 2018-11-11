# zeitgeist

We're building a robotic grocery cart.


## audio

The materials for experimentation in tracking a ultrasonic sound source (phone) from a microphone array. Tracking works up to at most a couple feet with ~30 degree resolution (not near good enough for a robot cart inside a grocery store).

## control

Programs to control a new, monolithic hoverboard control board from a Raspberry Pi.

## cv

Scripts related to Kinect-based computer vision for tracking a customer and detecting obstacles.

## serial

Files (scripts and PCB sources) used for decoding serial communication in between the two boards that controlled the original hoverboard. This communication bus could be read to determine the state of each hoverboard side (angle, wheel speed, etc), but could not be written to, making it unusable for hoverboard control from an external computer.
