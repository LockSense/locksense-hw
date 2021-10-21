################################################################################
# Automatically-generated file. Do not edit!
################################################################################

SHELL = cmd.exe

# Add inputs and outputs from these tool invocations to the build variables 
CFG_SRCS += \
../pdmstream.cfg 

CMD_SRCS += \
../CC2650STK.cmd 

C_SRCS += \
../CC2650STK.c \
../ccfg.c \
../mic_test.c 

GEN_CMDS += \
./configPkg/linker.cmd 

GEN_FILES += \
./configPkg/linker.cmd \
./configPkg/compiler.opt 

GEN_MISC_DIRS += \
./configPkg/ 

C_DEPS += \
./CC2650STK.d \
./ccfg.d \
./mic_test.d 

GEN_OPTS += \
./configPkg/compiler.opt 

OBJS += \
./CC2650STK.obj \
./ccfg.obj \
./mic_test.obj 

GEN_MISC_DIRS__QUOTED += \
"configPkg\" 

OBJS__QUOTED += \
"CC2650STK.obj" \
"ccfg.obj" \
"mic_test.obj" 

C_DEPS__QUOTED += \
"CC2650STK.d" \
"ccfg.d" \
"mic_test.d" 

GEN_FILES__QUOTED += \
"configPkg\linker.cmd" \
"configPkg\compiler.opt" 

C_SRCS__QUOTED += \
"../CC2650STK.c" \
"../ccfg.c" \
"../mic_test.c" 


