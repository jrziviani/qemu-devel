human_arch	= PowerPC 64el
build_arch	= powerpc
header_arch	= $(build_arch)
defconfig	= pseries_le_defconfig
flavours	= ibm-gt
build_image	= vmlinux.strip
kernel_file	= arch/$(build_arch)/boot/vmlinux.strip
install_file	= vmlinux

loader		= grub
vdso		= vdso_install

disable_d_i	= true
no_dumpfile	= true
opal_signed	= false

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
