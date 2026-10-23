/*
 * Native PS5 first-boot diagnostic for the Tekken 6 port project.
 *
 * This is deliberately NOT the game. It proves that the native title remains
 * alive after startup. Native PS5 title entry points should not return from
 * main; the process lifecycle is controlled by the host.
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
    notify("T6 PS5 port: native title is running. Diagnostic only; press PS to close.");
    /* Keep the native title alive; returning from main caused the observed exit/crash. */
    for (;;) {
        sceKernelUsleep(1000000);
    }
}
