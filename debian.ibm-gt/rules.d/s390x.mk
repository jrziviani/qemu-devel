human_arch	= System 390x
build_arch	= s390
header_arch	= $(build_arch)
defconfig	= defconfig
flavours	= ibm-gt
build_image	= bzImage
kernel_file	= arch/$(build_arch)/boot/bzImage
install_file	= vmlinuz

vdso		= vdso_install

disable_d_i	= true
no_dumpfile	= true

do_common_headers_indep	= false
do_doc_package		= false
do_extras_package	= true
do_libc_dev_package 	= false
do_source_package 	= false
do_tools_common		= false
do_tools_cpupower	= true
do_tools_perf		= true
do_tools_usbip		= true
do_zfs			= true
