/*
 * Native PS5 first-boot diagnostic for the Tekken 6 port project.
 * Diagnostic only: no game engine, renderer, or game assets are included.
 *
 * The previous console run reported SIGSYS. The title reached the notification,
 * so isolate the sleep syscall by avoiding sleep/exit calls after notification.
 * Close this short diagnostic with the PS button / Close Game.
 */
extern int sceKernelSendNotificationRequest(int device, void *request, int size, int flags);

static void notify(const char *message) {
    char request[3120];
    for (int i = 0; i < (int)sizeof(request); ++i) request[i] = 0;
    for (int i = 0; message[i] && i < 3074; ++i) request[45 + i] = message[i];
    sceKernelSendNotificationRequest(0, request, sizeof(request), 0);
}

int main(void) {
    notify("T6 PS5 port: diagnostic started; no game yet. Press PS to close.");
    /* Deliberately avoid syscalls and returning from main during this test. */
    volatile unsigned long long keep_alive = 0;
    for (;;) {
        ++keep_alive;
    }
}
