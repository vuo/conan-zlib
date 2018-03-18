#include <stdio.h>
#define Z_SOLO
#include <zlib/zlib.h>

int main()
{
	printf("Successfully initialized zlib %s\n", zlibVersion());
	return 0;
}
