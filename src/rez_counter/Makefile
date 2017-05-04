CFLAGS = -O3 -march=armv7-a -mcpu=cortex-a9 -mtune=cortex-a9 -mfpu=neon -mfloat-abi=hard -ffast-math -fsingle-precision-constant -mvectorize-with-neon-quad

all: rez_counter

rez_counter: rez_counter.c
	gcc $(CFLAGS) -o $@ $^ -lm -lconfig
	cp rez_counter ../../

clean:
	rm rez_counter
