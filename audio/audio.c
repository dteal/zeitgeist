/*
 * Attempting to use a microphone array for direction finding.
 */

#include "libfreenect.h"
#include "libfreenect_audio.h"
#include <stdio.h>
#include <signal.h>

static freenect_context* f_context;
static freenect_device* f_device;
int die = 0;

typedef struct {
    int data;
} user_data;

/*
 * Received audio data.
 * num_samples: number of samples in each array
 * mic1-4: microphone data for left through right microphones,
 *         32-bit PCM little-endian samples at 16 kHz
 */
void callback(freenect_device* dev, int num_samples,
            int32_t* mic1, int32_t* mic2,
            int32_t* mic3, int32_t* mic4,
            int16_t* cancelled, void *unknown){
    //printf("Microphone data received!\n");
    //printf("%d\t%d\t%d\t%d\n", mic1[0], mic2[0], mic3[0], mic4[0]);
}

void stop(int sig){
    printf("SIGINT received; stopping.\n");
    die = 1;
}

int main(int argc, char** argv){
    printf("Initializing libfreenect...\n");
    if(freenect_init(&f_context, NULL) < 0){
        printf("Error: initialization failed! Shutting down.\n");
        return 1;
    }
    printf("Done.\n");

    printf("Selecting audio device...\n");
    freenect_select_subdevices(f_context, FREENECT_DEVICE_AUDIO);
    printf("Done.\n");

    printf("Setting log level...\n");
    freenect_set_log_level(f_context, FREENECT_LOG_FATAL);
    printf("Done.\n");

    printf("Finding devices...\n");
    int num_devices = freenect_num_devices(f_context);
    if(num_devices < 1){
        printf("Error: no devices found! Shutting down.\n");
        freenect_shutdown(f_context);
        return 1;
    }
    printf("Done.\n");

    printf("Opening device...\n");
    if(freenect_open_device(f_context, &f_device, 0) < 0){
        printf("Error opening device! Shutting down.\n");
        freenect_shutdown(f_context);
        return 1;
    }
    printf("Done.\n");

    printf("Initializing ephemeral data...\n");
    user_data state;
    state.data = 0;
    freenect_set_user(f_device, &state);
    printf("Done.\n");

    printf("Setting audio data callback...\n");
    freenect_set_audio_in_callback(f_device, callback);
    printf("Done.\n");

    printf("Starting audio recording...\n");
    if(freenect_start_audio(f_device) < 0){
        printf("Error starting audio input! Shutting down.\n");
        freenect_close_device(f_device);
        freenect_shutdown(f_context);
        return 1;
    }
    printf("Done.\n");

    printf("Setting OS kill signal callback...\n");
    signal(SIGINT, stop);
    printf("Done.\n");

    printf("Beginning processing...\n");
    while(!die && freenect_process_events(f_context) >= 0){}
    printf("Done processing.\n");

    printf("Shutting down.\n");
    freenect_close_device(f_device);
    freenect_shutdown(f_context);
    return 0;
}