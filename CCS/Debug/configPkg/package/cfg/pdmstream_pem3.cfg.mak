# invoke SourceDir generated makefile for pdmstream.pem3
pdmstream.pem3: .libraries,pdmstream.pem3
.libraries,pdmstream.pem3: package/cfg/pdmstream_pem3.xdl
	$(MAKE) -f C:\Users\steve\OneDrive\Desktop\test\locksense-hw\CCS/src/makefile.libs

clean::
	$(MAKE) -f C:\Users\steve\OneDrive\Desktop\test\locksense-hw\CCS/src/makefile.libs clean

