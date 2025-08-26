#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char *argv[]) {
    // Build command to call Python with all args
    // This will run: python3 vault_runner.py [args...]
    char command[1024] = "python3 main.py";

    // Append arguments passed to this program
    for (int i = 1; i < argc; i++) {
        strcat(command, " ");
        strcat(command, argv[i]);
    }

    // Run the command
    int ret = system(command);
    return ret;
}
