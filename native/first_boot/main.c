/*
 * Native PS5 first-boot diagnostic for the Tekken 6 port project.
 *
 * This is deliberately NOT the game. It proves the native-title toolchain
 * and launch path before we attempt the much larger ReXGlue/rendering port.
 * Built using the public ps5link SDK model. Keep the message short.
 */
extern int sceKernelSendNotificationRequest(int device, void *request, int size, int flags);
extern int sceKernelUsleep(unsigned int microseconds);

static void notify(const char *message) {
    char request[3120];
    for (int i = 0; i < (int)sizeof(request); ++i) request[i] = 0;
    for (int i = 0; message[i] && i < 3074; ++i) request[45 + i] = message[i];
    sceKernelSendNotificationRequest(0, request, sizeof(request), 0);
}

int main(void) {
    notify("T6 PS5 port: native title booted. This is a diagnostic, not the game.");
    sceKernelUsleep(15000000);
    return 0;
}
