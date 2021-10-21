# invoke SourceDir generated makefile for pdmstream.pem3
pdmstream.pem3: .libraries,pdmstream.pem3
.libraries,pdmstream.pem3: package/cfg/pdmstream_pem3.xdl
	$(MAKE) -f C:\Users\steve\workspace_v10\mic_test_CC2650STK_TI/src/makefile.libs

clean::
	$(MAKE) -f C:\Users\steve\workspace_v10\mic_test_CC2650STK_TI/src/makefile.libs clean

