#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "libfreenect.h"
#include <math.h>
#include "CImg.h"

using namespace cimg_library;

volatile int die = 0;

//int g_argc;
//char **g_argv;

int window;

uint8_t *depth_mid, *depth_front;
uint8_t *rgb_back, *rgb_mid, *rgb_front;

int camera_rotate = 0;
int tilt_changed = 0;

freenect_context *f_ctx;
freenect_device *f_dev;
int freenect_angle = 0;
int freenect_led;

freenect_video_format requested_format = FREENECT_VIDEO_RGB;
freenect_video_format current_format = FREENECT_VIDEO_RGB;

int got_rgb = 0;
int got_depth = 0;

void depth_cb(freenect_device *dev, void *v_depth, uint32_t timestamp) {
	printf("Got depth!\n"); 

}

void rgb_cb(freenect_device *dev, void *rgb, uint32_t timestamp) {
	printf("Got RGB!\n");

}

int main(int argc, char **argv)
{
	printf("Allocating video memory...\n");
	depth_mid = (uint8_t*)malloc(640*480*3);
	depth_front = (uint8_t*)malloc(640*480*3);
	rgb_back = (uint8_t*)malloc(640*480*3);
	rgb_mid = (uint8_t*)malloc(640*480*3);
	rgb_front = (uint8_t*)malloc(640*480*3);

	printf("Initializing freenect...\n");
	if (freenect_init(&f_ctx, NULL) < 0) {
		printf("freenect_init() failed\n");
		return 1;
	}

	printf("Selecting options...\n");
	freenect_set_log_level(f_ctx, FREENECT_LOG_FATAL);
	freenect_select_subdevices(f_ctx, (freenect_device_flags)(FREENECT_DEVICE_CAMERA));

	int nr_devices = freenect_num_devices (f_ctx);
	printf ("Number of devices found: %d\n", nr_devices);

	printf("Connecting to device...\n");
	if (nr_devices < 1) {
		printf("No devices found. Exiting.\n");
		freenect_shutdown(f_ctx);
		return 1;
	}

	if (freenect_open_device(f_ctx, &f_dev, 0) < 0) {
		printf("Could not open device.\n");
		freenect_shutdown(f_ctx);
		return 1;
	}


	freenect_set_led(f_dev,LED_GREEN);
	freenect_set_depth_callback(f_dev, depth_cb);
	freenect_set_video_callback(f_dev, rgb_cb);
	freenect_set_video_mode(f_dev, freenect_find_video_mode(FREENECT_RESOLUTION_LOW, current_format));
	freenect_set_depth_mode(f_dev, freenect_find_depth_mode(FREENECT_RESOLUTION_LOW, FREENECT_DEPTH_11BIT));
	freenect_set_video_buffer(f_dev, rgb_back);
	freenect_set_depth_buffer(f_dev, depth_mid);

	freenect_start_depth(f_dev);
	freenect_start_video(f_dev);

	//printf("'w' - tilt up, 's' - level, 'x' - tilt down, '0'-'6' - select LED mode, '+' & '-' - change IR intensity \n");
	//printf("'f' - change video format, 'm' - mirror video, 'o' - rotate video with accelerometer \n");
	//printf("'e' - auto exposure, 'b' - white balance, 'r' - raw color, 'n' - near mode (K4W only) \n");

	while (!die && freenect_process_events(f_ctx) >= 0) {
		/*
		if (requested_format != current_format) {
			freenect_stop_video(f_dev);
			freenect_set_video_mode(f_dev, freenect_find_video_mode(FREENECT_RESOLUTION_MEDIUM, requested_format));
			freenect_start_video(f_dev);
			current_format = requested_format;
		}
		*/
	}

	printf("\nshutting down streams...\n");

	freenect_stop_depth(f_dev);
	freenect_stop_video(f_dev);

	freenect_close_device(f_dev);
	freenect_shutdown(f_ctx);

	printf("-- done!\n");
	return NULL;


	return 0;
}
