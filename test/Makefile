USER_PERIPHERALS = \
	byte_example \
	edge_counter \
	pwm_sk \
	full_example \
	uart \
	matt_encoder.test \
	ledstrip.test \
	impostor_ws2812b.test \
	matt_pwm.test

.PHONY: all $(USER_PERIPHERALS)

%-results.xml:
	make -f test_$*.mk clean
	make -f test_$*.mk
	mv results.xml $@

peri-%.xml:
	make -f test_basic.mk clean
	MODULE=user_peripherals.$* make -f test_basic.mk
	mv results.xml $@

all: clean basic-results.xml prog-results.xml $(USER_PERIPHERALS:%=peri-%.xml)
	cat *results.xml peri-*.xml > results.xml

$(USER_PERIPHERALS): %: peri-%.xml

clean:
	rm *results.xml peri-*.xml || true
