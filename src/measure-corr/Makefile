CFLAGS = -O3 -march=armv7-a -mcpu=cortex-a9 -mtune=cortex-a9 -mfpu=neon -mfloat-abi=hard -ffast-math -fsingle-precision-constant -mvectorize-with-neon-quad

all: measure-corr

measure-corr: measure-corr.c
	gcc $(CFLAGS) -o $@ $^ -lm -lconfig
	cp measure-corr ../../

clean:
	rm measure-corr
