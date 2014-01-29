# Build time setting
%define rhev 0

%if %{rhev}
    %bcond_with     guest_agent     # disabled
%else
    %bcond_without  guest_agent     # enabled
%endif

%global SLOF_gittagdate 20120731

%global have_usbredir 1

%ifarch %{ix86} x86_64
    %global have_seccomp 1
    %global have_spice   1
%else
    %global have_usbredir 0
%endif

%ifnarch s390 s390x
    %global have_librdma 1
%endif

%ifnarch x86_64
    %global build_only_sub 1
    %global debug_package %{nil}
%endif

%ifarch %{ix86}
    %global kvm_target    i386
%endif
%ifarch x86_64
    %global kvm_target    x86_64
%endif
%ifarch ppc64
    %global kvm_target    ppc64
%endif
%ifarch s390x
    %global kvm_target    s390x
%endif

#Versions of various parts:

%define pkgname qemu-kvm
%define rhel_suffix -rhel
%define rhev_suffix -rhev

# Setup for RHEL/RHEV package handling
# We need to define tree suffixes:
# - pkgsuffix:             used for package name
# - extra_provides_suffix: used for dependency checking of other packages
# - conflicts_suffix:      used to prevent installation of both RHEL and RHEV

%if %{rhev}
    %global pkgsuffix %{rhev_suffix}
    %global extra_provides_suffix %{nil}
    %global conflicts_suffix %{rhel_suffix}
    %global obsoletes_version 15:0-0
%else
    %global pkgsuffix %{nil}
    %global extra_provides_suffix %{rhel_suffix}
    %global conflicts_suffix %{rhev_suffix}
%endif

# Macro to properly setup RHEL/RHEV conflict handling
%define rhel_rhev_conflicts()                                         \
Conflicts: %1%{conflicts_suffix}                                      \
Provides: %1%{extra_provides_suffix} = %{epoch}:%{version}-%{release} \
    %if 0%{?obsoletes_version:1}                                          \
Obsoletes: %1 < %{obsoletes_version}                                      \
    %endif

Summary: QEMU is a FAST! processor emulator
Name: %{pkgname}%{?pkgsuffix}
Version: 1.5.3
Release: 44%{?dist}
# Epoch because we pushed a qemu-1.0 package. AIUI this can't ever be dropped
Epoch: 10
License: GPLv2+ and LGPLv2+ and BSD
Group: Development/Tools
URL: http://www.qemu.org/
# RHEV will build Qemu only on x86_64:
%if %{rhev}
ExclusiveArch: x86_64
%endif
Requires: seabios-bin >= 1.7.2.2-5
Requires: sgabios-bin
Requires: seavgabios-bin
Requires: ipxe-roms-qemu
Requires: %{pkgname}-common%{?pkgsuffix} = %{epoch}:%{version}-%{release}
        %if 0%{?have_seccomp:1}
Requires: libseccomp >= 1.0.0
        %endif

# OOM killer breaks builds with parallel make on s390(x)
%ifarch s390 s390x
    %define _smp_mflags %{nil}
%endif

Source0: http://wiki.qemu-project.org/download/qemu-%{version}.tar.bz2

Source1: qemu.binfmt
# Loads kvm kernel modules at boot
# Not needed anymore - required only for kvm on non i86 archs 
# where we do not ubuild kvm
# Source2: kvm.modules
# Creates /dev/kvm
Source3: 80-kvm.rules
# KSM control scripts
Source4: ksm.service
Source5: ksm.sysconfig
Source6: ksmctl.c
Source7: ksmtuned.service
Source8: ksmtuned
Source9: ksmtuned.conf
Source10: qemu-guest-agent.service
Source11: 99-qemu-guest-agent.rules
Source12: bridge.conf
Source13: qemu-ga.sysconfig
Source14: rhel6-virtio.rom
Source15: rhel6-pcnet.rom
Source16: rhel6-rtl8139.rom
Source17: rhel6-ne2k_pci.rom
Source18: bios-256k.bin

# libcacard build fixes (heading upstream)
Patch1: 0000-libcacard-fix-missing-symbols-in-libcacard.so.patch

# Fix migration from qemu-kvm 1.2 to qemu 1.3
#Patch3: 0002-Fix-migration-from-qemu-kvm-1.2.patch

# Flow control series
#Patch4: 0100-char-Split-out-tcp-socket-close-code-in-a-separate-f.patch
#Patch5: 0101-char-Add-a-QemuChrHandlers-struct-to-initialise-char.patch
#Patch6: 0102-iohandlers-Add-enable-disable_write_fd_handler-funct.patch
#Patch7: 0103-char-Add-framework-for-a-write-unblocked-callback.patch
#Patch8: 0104-char-Update-send_all-to-handle-nonblocking-chardev-w.patch
#Patch9: 0105-char-Equip-the-unix-tcp-backend-to-handle-nonblockin.patch
#Patch10: 0106-char-Throttle-when-host-connection-is-down.patch
#Patch11: 0107-virtio-console-Enable-port-throttling-when-chardev-i.patch
#Patch12: 0108-spice-qemu-char.c-add-throttling.patch
#Patch13: 0109-spice-qemu-char.c-remove-intermediate-buffer.patch
#Patch14: 0110-usb-redir-Add-flow-control-support.patch
#Patch15: 0111-char-Disable-write-callback-if-throttled-chardev-is-.patch
#Patch16: 0112-hw-virtio-serial-bus-replay-guest-open-on-destinatio.patch

# Migration compatibility
#Patch17: configure-add-enable-migration-from-qemu-kvm.patch
#Patch18: acpi_piix4-condition-on-minimum_version_id.patch
#Patch19: i8254-fix-migration-from-qemu-kvm-1.1.patch
#Patch20: pc_piix-add-compat-handling-for-qemu-kvm-vga-mem-size.patch
#Patch21: qxl-add-rom_size-compat-property.patch
#Patch22: docs-fix-generating-qemu-doc.html-with-texinfo5.patch
#Patch23: rtc-test-Fix-test-failures-with-recent-glib.patch
#Patch24: iscsi-look-for-pkg-config-file-too.patch
#Patch25: tcg-fix-occcasional-tcg-broken-problem.patch
#Patch26: qxl-better-vga-init-in-enter_vga_mode.patch

# Enable/disable supported features
#Patch27: make-usb-devices-configurable.patch
#Patch28: fix-scripts-make_device_config-sh.patch
Patch29: disable-unsupported-usb-devices.patch
Patch30: disable-unsupported-emulated-scsi-devices.patch
Patch31: disable-various-unsupported-devices.patch
Patch32: disable-unsupported-audio-devices.patch
Patch33: disable-unsupported-emulated-network-devices.patch
Patch34: use-kvm-by-default.patch
Patch35: disable-hpet-device.patch
Patch36: rename-man-page-to-qemu-kvm.patch
Patch37: change-path-from-qemu-to-qemu-kvm.patch

# Fix CPUID model/level values on Conroe/Penryn/Nehalem CPU models 
Patch38: pc-replace-upstream-machine-types-by-rhel7-types.patch
Patch39: target-i386-update-model-values-on-conroe-penryn-nehalem-cpu-models.patch
Patch40: target-i386-set-level-4-on-conroe-penryn-nehalem.patch

# RHEL guest( sata disk ) can not boot up (rhbz #981723)
#Patch41: ahci-Fix-FLUSH-command.patch
# Kill the "use flash device for BIOS unless KVM" misfeature (rhbz #963280)
Patch42: pc-Disable-the-use-flash-device-for-BIOS-unless-KVM-misfeature.patch
# Provide RHEL-6 machine types (rhbz #983991)
Patch43: qemu-kvm-Fix-migration-from-older-version-due-to-i8254-changes.patch
Patch44: pc-Add-machine-type-rhel6-0-0.patch
Patch45: pc-Drop-superfluous-RHEL-6-compat_props.patch
Patch46: vga-Default-vram_size_mb-to-16-like-prior-versions-of-RHEL.patch
Patch47: pc-Drop-RHEL-6-USB-device-compat_prop-full-path.patch
Patch48: pc-Drop-RHEL-6-compat_props-virtio-serial-pci-max_ports-vectors.patch
Patch49: pc-Drop-RHEL-6-compat_props-apic-kvm-apic-vapic.patch
Patch50: qxl-set-revision-to-1-for-rhel6-0-0.patch
Patch51: pc-Give-rhel6-0-0-a-kvmclock.patch
Patch52: pc-Add-machine-type-rhel6-1-0.patch
Patch53: pc-Add-machine-type-rhel6-2-0.patch
Patch54: pc-Add-machine-type-rhel6-3-0.patch
Patch55: pc-Add-machine-type-rhel6-4-0.patch
Patch56: pc-Add-machine-type-rhel6-5-0.patch
Patch57: e1000-Keep-capabilities-list-bit-on-for-older-RHEL-machine-types.patch
# Change s3/s4 default to "disable". (rhbz #980840)  
Patch58: misc-disable-s3-s4-by-default.patch
Patch59: pc-rhel6-compat-enable-S3-S4-for-6-1-and-lower-machine-types.patch
# Support Virtual Memory Disk Format in qemu (rhbz #836675)
Patch60: vmdk-Allow-reading-variable-size-descriptor-files.patch
Patch61: vmdk-refuse-to-open-higher-version-than-supported.patch
#Patch62: vmdk-remove-wrong-calculation-of-relative-path.patch
Patch63: block-add-block-driver-read-only-whitelist.patch

# query mem info from monitor would cause qemu-kvm hang [RHEL-7] (rhbz #970047)
Patch64: kvm-char-io_channel_send-don-t-lose-written-bytes.patch
Patch65: kvm-monitor-maintain-at-most-one-G_IO_OUT-watch.patch
# Throttle-down guest to help with live migration convergence (backport to RHEL7.0) (rhbz #985958)
Patch66: kvm-misc-Introduce-async_run_on_cpu.patch
Patch67: kvm-misc-Add-auto-converge-migration-capability.patch
Patch68: kvm-misc-Force-auto-convegence-of-live-migration.patch
# disable (for now) EFI-enabled roms (rhbz #962563)
Patch69: kvm-misc-Disable-EFI-enabled-roms.patch
# qemu-kvm "vPMU passthrough" mode breaks migration, shouldn't be enabled by default (rhbz #853101)
Patch70: kvm-target-i386-Pass-X86CPU-object-to-cpu_x86_find_by_name.patch
Patch71: kvm-target-i386-Disable-PMU-CPUID-leaf-by-default.patch
Patch72: kvm-pc-set-compat-pmu-property-for-rhel6-x-machine-types.patch
# Remove pending watches after virtserialport unplug (rhbz #992900)
# Patch73: kvm-virtio-console-Use-exitfn-for-virtserialport-too.patch
# Containment of error when an SR-IOV device encounters an error... (rhbz #984604)
Patch74: kvm-linux-headers-Update-to-v3-10-rc5.patch
Patch75: kvm-vfio-QEMU-AER-Qemu-changes-to-support-AER-for-VFIO-PCI-devices.patch

# update qemu-ga config & init script in RHEL7 wrt. fsfreeze hook (rhbz 969942)
Patch76: kvm-misc-qga-fsfreeze-main-hook-adapt-to-RHEL-7-RH-only.patch
# RHEL7 does not have equivalent functionality for __com.redhat_qxl_screendump (rhbz 903910)
Patch77: kvm-misc-add-qxl_screendump-monitor-command.patch
# SEP flag behavior for CPU models of RHEL6 machine types should be compatible (rhbz 960216)
Patch78: kvm-pc_piix-disable-CPUID_SEP-for-6-4-0-machine-types-and-below.patch
# crash command can not read the dump-guest-memory file when paging=false [RHEL-7] (rhbz 981582)
Patch79: kvm-dump-Move-stubs-into-libqemustub-a.patch
Patch80: kvm-cpu-Turn-cpu_paging_enabled-into-a-CPUState-hook.patch
Patch81: kvm-memory_mapping-Move-MemoryMappingList-typedef-to-qemu-typedefs-h.patch
Patch82: kvm-cpu-Turn-cpu_get_memory_mapping-into-a-CPUState-hook.patch
Patch83: kvm-dump-Abstract-dump_init-with-cpu_synchronize_all_states.patch
Patch84: kvm-memory_mapping-Improve-qemu_get_guest_memory_mapping-error-reporting.patch
Patch85: kvm-dump-clamp-guest-provided-mapping-lengths-to-ramblock-sizes.patch
Patch86: kvm-dump-introduce-GuestPhysBlockList.patch
Patch87: kvm-dump-populate-guest_phys_blocks.patch
Patch88: kvm-dump-rebase-from-host-private-RAMBlock-offsets-to-guest-physical-addresses.patch
# RHEL 7 qemu-kvm fails to build on F19 host due to libusb deprecated API (rhbz 996469)
Patch89: kvm-usb-host-libusb-Fix-building-with-libusb-git-master-code.patch
# Live migration support in virtio-blk-data-plane (rhbz 995030)
#Patch90: kvm-dataplane-sync-virtio-c-and-vring-c-virtqueue-state.patch
#Patch91: kvm-virtio-clear-signalled_used_valid-when-switching-from-dataplane.patch
#Patch92: kvm-vhost-clear-signalled_used_valid-on-vhost-stop.patch
Patch93: kvm-migration-notify-migration-state-before-starting-thread.patch
Patch94: kvm-dataplane-enable-virtio-blk-x-data-plane-on-live-migration.patch
#Patch95: kvm-dataplane-refuse-to-start-if-device-is-already-in-use.patch
# qemu-img resize can execute successfully even input invalid syntax (rhbz 992935)
Patch96: kvm-qemu-img-Error-out-for-excess-arguments.patch
# For bz#964304 - Windows guest agent service failed to be started
Patch97: kvm-osdep-add-qemu_get_local_state_pathname.patch
# For bz#964304 - Windows guest agent service failed to be started
Patch98: kvm-qga-determine-default-state-dir-and-pidfile-dynamica.patch
# For bz#964304 - Windows guest agent service failed to be started
Patch99: kvm-configure-don-t-save-any-fixed-local_statedir-for-wi.patch
# For bz#964304 - Windows guest agent service failed to be started
Patch100: kvm-qga-create-state-directory-on-win32.patch
# For bz#964304 - Windows guest agent service failed to be started
Patch101: kvm-qga-save-state-directory-in-ga_install_service-RHEL-.patch
# For bz#964304 - Windows guest agent service failed to be started
Patch102: kvm-Makefile-create-.-var-run-when-installing-the-POSIX-.patch
# For bz#980782 - kernel_irqchip defaults to off instead of on without -machine
Patch103: kvm-qemu-option-Fix-qemu_opts_find-for-null-id-arguments.patch
# For bz#980782 - kernel_irqchip defaults to off instead of on without -machine
Patch104: kvm-qemu-option-Fix-qemu_opts_set_defaults-for-corner-ca.patch
# For bz#980782 - kernel_irqchip defaults to off instead of on without -machine
Patch105: kvm-vl-New-qemu_get_machine_opts.patch
# For bz#980782 - kernel_irqchip defaults to off instead of on without -machine
Patch106: kvm-Fix-machine-options-accel-kernel_irqchip-kvm_shadow_.patch
# For bz#980782 - kernel_irqchip defaults to off instead of on without -machine
Patch107: kvm-microblaze-Fix-latent-bug-with-default-DTB-lookup.patch
# For bz#980782 - kernel_irqchip defaults to off instead of on without -machine
Patch108: kvm-Simplify-machine-option-queries-with-qemu_get_machin.patch
# For bz#838170 - Add live migration support for USB [xhci, usb-uas]
Patch109: kvm-pci-add-VMSTATE_MSIX.patch
# For bz#838170 - Add live migration support for USB [xhci, usb-uas]
Patch110: kvm-xhci-add-XHCISlot-addressed.patch
# For bz#838170 - Add live migration support for USB [xhci, usb-uas]
Patch111: kvm-xhci-add-xhci_alloc_epctx.patch
# For bz#838170 - Add live migration support for USB [xhci, usb-uas]
Patch112: kvm-xhci-add-xhci_init_epctx.patch
# For bz#838170 - Add live migration support for USB [xhci, usb-uas]
Patch113: kvm-xhci-add-live-migration-support.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch114: kvm-pc-set-level-xlevel-correctly-on-486-qemu32-CPU-mode.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch115: kvm-pc-Remove-incorrect-rhel6.x-compat-model-value-for-C.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch116: kvm-pc-rhel6.x-has-x2apic-present-on-Conroe-Penryn-Nehal.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch117: kvm-pc-set-compat-CPUID-0x80000001-.EDX-bits-on-Westmere.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch118: kvm-pc-Remove-PCLMULQDQ-from-Westmere-on-rhel6.x-machine.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch119: kvm-pc-SandyBridge-rhel6.x-compat-fixes.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch120: kvm-pc-Haswell-doesn-t-have-rdtscp-on-rhel6.x.patch
# For bz#972433 - "INFO: rcu_sched detected stalls" after RHEL7 kvm vm migrated
Patch121: kvm-i386-fix-LAPIC-TSC-deadline-timer-save-restore.patch
# For bz#996258 - boot guest with maxcpu=255 successfully but actually max number of vcpu is 160
Patch122: kvm-all.c-max_cpus-should-not-exceed-KVM-vcpu-limit.patch
# For bz#906937 - [Hitachi 7.0 FEAT][QEMU]Add a time stamp to error message (*)
Patch123: kvm-add-timestamp-to-error_report.patch
# For bz#906937 - [Hitachi 7.0 FEAT][QEMU]Add a time stamp to error message (*)
Patch124: kvm-Convert-stderr-message-calling-error_get_pretty-to-e.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch125: kvm-block-package-preparation-code-in-qmp_transaction.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch126: kvm-block-move-input-parsing-code-in-qmp_transaction.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch127: kvm-block-package-committing-code-in-qmp_transaction.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch128: kvm-block-package-rollback-code-in-qmp_transaction.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch129: kvm-block-make-all-steps-in-qmp_transaction-as-callback.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch130: kvm-blockdev-drop-redundant-proto_drv-check.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch131: kvm-block-Don-t-parse-protocol-from-file.filename.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch132: kvm-Revert-block-Disable-driver-specific-options-for-1.5.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch133: kvm-qcow2-Add-refcount-update-reason-to-all-callers.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch134: kvm-qcow2-Options-to-enable-discard-for-freed-clusters.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch135: kvm-qcow2-Batch-discards.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch136: kvm-block-Always-enable-discard-on-the-protocol-level.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch137: kvm-qapi.py-Avoid-code-duplication.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch138: kvm-qapi.py-Allow-top-level-type-reference-for-command-d.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch139: kvm-qapi-schema-Use-BlockdevSnapshot-type-for-blockdev-s.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch140: kvm-qapi-types.py-Implement-base-for-unions.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch141: kvm-qapi-visit.py-Split-off-generate_visit_struct_fields.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch142: kvm-qapi-visit.py-Implement-base-for-unions.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch143: kvm-docs-Document-QAPI-union-types.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch144: kvm-qapi-Add-visitor-for-implicit-structs.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch145: kvm-qapi-Flat-unions-with-arbitrary-discriminator.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch146: kvm-qapi-Add-consume-argument-to-qmp_input_get_object.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch147: kvm-qapi.py-Maintain-a-list-of-union-types.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch148: kvm-qapi-qapi-types.py-native-list-support.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch149: kvm-qapi-Anonymous-unions.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch150: kvm-block-Allow-driver-option-on-the-top-level.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch151: kvm-QemuOpts-Add-qemu_opt_unset.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch152: kvm-blockdev-Rename-I-O-throttling-options-for-QMP.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch153: kvm-qemu-iotests-Update-051-reference-output.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch154: kvm-blockdev-Rename-readonly-option-to-read-only.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch155: kvm-blockdev-Split-up-cache-option.patch
# For bz#1005818 - qcow2: Backport discard command line options
Patch156: kvm-qcow2-Use-dashes-instead-of-underscores-in-options.patch
# For bz#1006959 - qemu-iotests false positives
Patch157: kvm-qemu-iotests-filter-QEMU-version-in-monitor-banner.patch
# For bz#1006959 - qemu-iotests false positives
Patch158: kvm-tests-set-MALLOC_PERTURB_-to-expose-memory-bugs.patch
# For bz#1006959 - qemu-iotests false positives
Patch159: kvm-qemu-iotests-Whitespace-cleanup.patch
# For bz#1006959 - qemu-iotests false positives
Patch160: kvm-qemu-iotests-Fixed-test-case-026.patch
# For bz#1006959 - qemu-iotests false positives
Patch161: kvm-qemu-iotests-Fix-test-038.patch
# For bz#1006959 - qemu-iotests false positives
Patch162: kvm-qemu-iotests-Remove-lsi53c895a-tests-from-051.patch
# For bz#974887 - the screen of guest fail to display correctly when use spice + qxl driver
Patch163: kvm-spice-fix-display-initialization.patch
# For bz#921983 - Disable or remove emulated network devices that we will not support
Patch164: kvm-Remove-i82550-network-card-emulation.patch
# For bz#903914 - Disable or remove usb related devices that we will not support
Patch165: kvm-Remove-usb-wacom-tablet.patch
# For bz#903914 - Disable or remove usb related devices that we will not support
Patch166: kvm-Disable-usb-uas.patch
# For bz#947441 - HPET device must be disabled
Patch168: kvm-Remove-no-hpet-option.patch
# For bz#1002286 - Disable or remove device isa-parallel
Patch169: kvm-Disable-isa-parallel.patch
# For bz#949514 - fail to passthrough the USB3.0 stick to windows guest with xHCI controller under pc-i440fx-1.4
Patch170: kvm-xhci-implement-warm-port-reset.patch
# For bz#953304 - Serial number of some USB devices must be fixed for older RHEL machine types
Patch171: kvm-usb-add-serial-bus-property.patch
# For bz#953304 - Serial number of some USB devices must be fixed for older RHEL machine types
Patch172: kvm-rhel6-compat-usb-serial-numbers.patch
# For bz#995866 - fix vmdk support to ESX images
Patch173: kvm-vmdk-fix-comment-for-vmdk_co_write_zeroes.patch
# For bz#1007226 - Introduce bs->zero_beyond_eof
Patch174: kvm-gluster-Add-image-resize-support.patch
# For bz#1007226 - Introduce bs->zero_beyond_eof
Patch175: kvm-block-Introduce-bs-zero_beyond_eof.patch
# For bz#1007226 - Introduce bs->zero_beyond_eof
Patch176: kvm-block-Produce-zeros-when-protocols-reading-beyond-en.patch
# For bz#1007226 - Introduce bs->zero_beyond_eof
Patch177: kvm-gluster-Abort-on-AIO-completion-failure.patch
# For bz#1001131 - Disable or remove device usb-bt-dongle
Patch178: kvm-Preparation-for-usb-bt-dongle-conditional-build.patch
# For bz#1001131 - Disable or remove device usb-bt-dongle
Patch179: kvm-Remove-dev-bluetooth.c-dependency-from-vl.c.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch180: kvm-exec-Fix-Xen-RAM-allocation-with-unusual-options.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch181: kvm-exec-Clean-up-fall-back-when-mem-path-allocation-fai.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch182: kvm-exec-Reduce-ifdeffery-around-mem-path.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch183: kvm-exec-Simplify-the-guest-physical-memory-allocation-h.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch184: kvm-exec-Drop-incorrect-dead-S390-code-in-qemu_ram_remap.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch185: kvm-exec-Clean-up-unnecessary-S390-ifdeffery.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch186: kvm-exec-Don-t-abort-when-we-can-t-allocate-guest-memory.patch
# For bz#1009328 - [RFE] Nicer error report when qemu-kvm can't allocate guest RAM
Patch187: kvm-pc_sysfw-Fix-ISA-BIOS-init-for-ridiculously-big-flas.patch
# For bz#903918 - Disable or remove emulated SCSI devices we will not support
Patch188: kvm-virtio-scsi-Make-type-virtio-scsi-common-abstract.patch
# For bz#1009491 - move qga logfiles to new /var/log/qemu-ga/ directory [RHEL-7]
Patch189: kvm-qga-move-logfiles-to-new-directory-for-easier-SELinu.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch190: kvm-target-i386-add-cpu64-rhel6-CPU-model.patch
# For bz#903889 - The value of steal time in "top" command always is "0.0% st" after guest migration
Patch191: kvm-fix-steal-time-MSR-vmsd-callback-to-proper-opaque-ty.patch
# For bz#995866 - fix vmdk support to ESX images
Patch192: kvm-vmdk-Make-VMDK3Header-and-VmdkGrainMarker-QEMU_PACKE.patch
# For bz#995866 - fix vmdk support to ESX images
Patch193: kvm-vmdk-use-unsigned-values-for-on-disk-header-fields.patch
# For bz#995866 - fix vmdk support to ESX images
Patch194: kvm-qemu-iotests-add-poke_file-utility-function.patch
# For bz#995866 - fix vmdk support to ESX images
Patch195: kvm-qemu-iotests-add-empty-test-case-for-vmdk.patch
# For bz#995866 - fix vmdk support to ESX images
Patch196: kvm-vmdk-check-granularity-field-in-opening.patch
# For bz#995866 - fix vmdk support to ESX images
Patch197: kvm-vmdk-check-l2-table-size-when-opening.patch
# For bz#995866 - fix vmdk support to ESX images
Patch198: kvm-vmdk-check-l1-size-before-opening-image.patch
# For bz#995866 - fix vmdk support to ESX images
Patch199: kvm-vmdk-use-heap-allocation-for-whole_grain.patch
# For bz#995866 - fix vmdk support to ESX images
Patch200: kvm-vmdk-rename-num_gtes_per_gte-to-num_gtes_per_gt.patch
# For bz#995866 - fix vmdk support to ESX images
Patch201: kvm-vmdk-Move-l1_size-check-into-vmdk_add_extent.patch
# For bz#995866 - fix vmdk support to ESX images
Patch202: kvm-vmdk-fix-L1-and-L2-table-size-in-vmdk3-open.patch
# For bz#995866 - fix vmdk support to ESX images
Patch203: kvm-vmdk-support-vmfsSparse-files.patch
# For bz#995866 - fix vmdk support to ESX images
Patch204: kvm-vmdk-support-vmfs-files.patch
# For bz#1005036 - When using “-vga qxl” together with “-display vnc=:5” or “-display  sdl” qemu displays  pixel garbage
Patch205: kvm-qxl-fix-local-renderer.patch
# For bz#1008987 - pvticketlocks: add kvm feature kvm_pv_unhalt
Patch206: kvm-linux-headers-update-to-kernel-3.10.0-26.el7.patch
# For bz#1008987 - pvticketlocks: add kvm feature kvm_pv_unhalt
Patch207: kvm-target-i386-add-feature-kvm_pv_unhalt.patch
# For bz#1010881 - backport vcpu soft limit warning
Patch208: kvm-warn-if-num-cpus-is-greater-than-num-recommended.patch
# For bz#1007222 - QEMU core dumped when do hot-unplug virtio serial port during transfer file between host to guest with virtio serial through TCP socket
Patch209: kvm-char-move-backends-io-watch-tag-to-CharDriverState.patch
# For bz#1007222 - QEMU core dumped when do hot-unplug virtio serial port during transfer file between host to guest with virtio serial through TCP socket
Patch210: kvm-char-use-common-function-to-disable-callbacks-on-cha.patch
# For bz#1007222 - QEMU core dumped when do hot-unplug virtio serial port during transfer file between host to guest with virtio serial through TCP socket
Patch211: kvm-char-remove-watch-callback-on-chardev-detach-from-fr.patch
# For bz#1017049 - qemu-img refuses to open the vmdk format image its created
Patch212: kvm-block-don-t-lose-data-from-last-incomplete-sector.patch
# For bz#1017049 - qemu-img refuses to open the vmdk format image its created
Patch213: kvm-vmdk-fix-cluster-size-check-for-flat-extents.patch
# For bz#1017049 - qemu-img refuses to open the vmdk format image its created
Patch214: kvm-qemu-iotests-add-monolithicFlat-creation-test-to-059.patch
# For bz#1001604 - usb hub doesn't work properly (win7 sees downstream port #1 only).
Patch215: kvm-xhci-fix-endpoint-interval-calculation.patch
# For bz#1001604 - usb hub doesn't work properly (win7 sees downstream port #1 only).
Patch216: kvm-xhci-emulate-intr-endpoint-intervals-correctly.patch
# For bz#1001604 - usb hub doesn't work properly (win7 sees downstream port #1 only).
Patch217: kvm-xhci-reset-port-when-disabling-slot.patch
# For bz#1001604 - usb hub doesn't work properly (win7 sees downstream port #1 only).
Patch218: kvm-Revert-usb-hub-report-status-changes-only-once.patch
# For bz#1004290 - Use model 6 for qemu64 and intel cpus
Patch219: kvm-target-i386-Set-model-6-on-qemu64-qemu32-CPU-models.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch220: kvm-pc-rhel6-doesn-t-have-APIC-on-pentium-CPU-models.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch221: kvm-pc-RHEL-6-had-x2apic-set-on-Opteron_G-123.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch222: kvm-pc-RHEL-6-don-t-have-RDTSCP.patch
# For bz#1009285 - -device usb-storage,serial=... crashes with SCSI generic drive
Patch223: kvm-scsi-Fix-scsi_bus_legacy_add_drive-scsi-generic-with.patch
# For bz#1004175 - '-sandbox on'  option  cause  qemu-kvm process hang
Patch224: kvm-seccomp-fine-tuning-whitelist-by-adding-times.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch225: kvm-block-add-bdrv_write_zeroes.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch226: kvm-block-raw-add-bdrv_co_write_zeroes.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch227: kvm-rdma-export-qemu_fflush.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch228: kvm-block-migration-efficiently-encode-zero-blocks.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch229: kvm-Fix-real-mode-guest-migration.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch230: kvm-Fix-real-mode-guest-segments-dpl-value-in-savevm.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch231: kvm-migration-add-autoconvergence-documentation.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch232: kvm-migration-send-total-time-in-QMP-at-completed-stage.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch233: kvm-migration-don-t-use-uninitialized-variables.patch
# For bz#921465 - Migration can not finished even the "remaining ram" is already 0 kb
Patch234: kvm-pc-drop-external-DSDT-loading.patch
# For bz#954195 - RHEL machines <=6.4 should not use mixemu
Patch235: kvm-hda-codec-refactor-common-definitions-into-a-header-.patch
# For bz#954195 - RHEL machines <=6.4 should not use mixemu
Patch236: kvm-hda-codec-make-mixemu-selectable-at-runtime.patch
# For bz#954195 - RHEL machines <=6.4 should not use mixemu
Patch237: kvm-audio-remove-CONFIG_MIXEMU-configure-option.patch
# For bz#954195 - RHEL machines <=6.4 should not use mixemu
Patch238: kvm-pc_piix-disable-mixer-for-6.4.0-machine-types-and-be.patch
# For bz#994414 - hot-unplug chardev with pty backend caused qemu Segmentation fault
Patch239: kvm-chardev-fix-pty_chr_timer.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch240: kvm-qemu-socket-zero-initialize-SocketAddress.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch241: kvm-qemu-socket-drop-pointless-allocation.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch242: kvm-qemu-socket-catch-monitor_get_fd-failures.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch243: kvm-qemu-char-check-optional-fields-using-has_.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch244: kvm-error-add-error_setg_file_open-helper.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch245: kvm-qemu-char-use-more-specific-error_setg_-variants.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch246: kvm-qemu-char-print-notification-to-stderr.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch247: kvm-qemu-char-fix-documentation-for-telnet-wait-socket-f.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch248: kvm-qemu-char-don-t-leak-opts-on-error.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch249: kvm-qemu-char-use-ChardevBackendKind-in-CharDriver.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch250: kvm-qemu-char-minor-mux-chardev-fixes.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch251: kvm-qemu-char-add-chardev-mux-support.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch252: kvm-qemu-char-report-udp-backend-errors.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch253: kvm-qemu-socket-don-t-leak-opts-on-error.patch
# For bz#922010 - RFE: support hotplugging chardev & serial ports
Patch254: kvm-chardev-handle-qmp_chardev_add-KIND_MUX-failure.patch
# For bz#1019474 - RHEL-7 can't load piix4_pm migration section from RHEL-6.5
Patch255: kvm-acpi-piix4-Enable-qemu-kvm-compatibility-mode.patch
# For bz#1004743 - XSAVE migration format not compatible between RHEL6 and RHEL7
Patch256: kvm-target-i386-support-loading-of-cpu-xsave-subsection.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch257: kvm-vl-Clean-up-parsing-of-boot-option-argument.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch258: kvm-qemu-option-check_params-is-now-unused-drop-it.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch259: kvm-vl-Fix-boot-order-and-once-regressions-and-related-b.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch260: kvm-vl-Rename-boot_devices-to-boot_order-for-consistency.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch261: kvm-pc-Make-no-fd-bootchk-stick-across-boot-order-change.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch262: kvm-doc-Drop-ref-to-Bochs-from-no-fd-bootchk-documentati.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch263: kvm-libqtest-Plug-fd-and-memory-leaks-in-qtest_quit.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch264: kvm-libqtest-New-qtest_end-to-go-with-qtest_start.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch265: kvm-qtest-Don-t-reset-on-qtest-chardev-connect.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch266: kvm-boot-order-test-New-covering-just-PC-for-now.patch
# For bz#1019352 - qemu-guest-agent: "guest-fsfreeze-freeze" deadlocks if the guest have mounted disk images
Patch267: kvm-qemu-ga-execute-fsfreeze-freeze-in-reverse-order-of-.patch
# For bz#989608 - [7.0 FEAT] qemu runtime support for librbd backend (ceph)
Patch268: kvm-rbd-link-and-load-librbd-dynamically.patch
# For bz#989608 - [7.0 FEAT] qemu runtime support for librbd backend (ceph)
Patch269: kvm-rbd-Only-look-for-qemu-specific-copy-of-librbd.so.1.patch
# For bz#989677 - [HP 7.0 FEAT]: Increase KVM guest supported memory to 4TiB
Patch270: kvm-seabios-paravirt-allow-more-than-1TB-in-x86-guest.patch
# For bz#1006468 - libiscsi initiator name should use vm UUID
Patch271: kvm-scsi-prefer-UUID-to-VM-name-for-the-initiator-name.patch
# For bz#928867 - Virtual PMU support during live migration - qemu-kvm
Patch272: kvm-target-i386-remove-tabs-from-target-i386-cpu.h.patch
# For bz#928867 - Virtual PMU support during live migration - qemu-kvm
Patch273: kvm-migrate-vPMU-state.patch
# For bz#1009993 - RHEL7 guests do not issue fdatasyncs on virtio-blk
Patch274: kvm-blockdev-do-not-default-cache.no-flush-to-true.patch
# For bz#1009993 - RHEL7 guests do not issue fdatasyncs on virtio-blk
Patch275: kvm-virtio-blk-do-not-relay-a-previous-driver-s-WCE-conf.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch276: kvm-rng-random-use-error_setg_file_open.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch277: kvm-block-mirror_complete-use-error_setg_file_open.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch278: kvm-blockdev-use-error_setg_file_open.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch279: kvm-cpus-use-error_setg_file_open.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch280: kvm-dump-qmp_dump_guest_memory-use-error_setg_file_open.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch281: kvm-savevm-qmp_xen_save_devices_state-use-error_setg_fil.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch282: kvm-block-bdrv_reopen_prepare-don-t-use-QERR_OPEN_FILE_F.patch
# For bz#907743 - qemu-ga: empty reason string for OpenFileFailed error
Patch283: kvm-qerror-drop-QERR_OPEN_FILE_FAILED-macro.patch
# For bz#787463 - disable ivshmem (was: [Hitachi 7.0 FEAT] Support ivshmem (Inter-VM Shared Memory))
Patch284: kvm-rhel-Drop-ivshmem-device.patch
# For bz#1001144 - Disable or remove device usb-host-linux
Patch285: kvm-usb-remove-old-usb-host-code.patch
# For bz#997702 - Migration from RHEL6.5 host to RHEL7.0 host is failed with virtio-net device
Patch286: kvm-Fix-migration-from-rhel6.5-to-rhel7-with-ipxe.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch287: kvm-pc-Don-t-prematurely-explode-QEMUMachineInitArgs.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch288: kvm-pc-Don-t-explode-QEMUMachineInitArgs-into-local-vari.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch289: kvm-smbios-Normalize-smbios_entry_add-s-error-handling-t.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch290: kvm-smbios-Convert-to-QemuOpts.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch291: kvm-smbios-Improve-diagnostics-for-conflicting-entries.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch292: kvm-smbios-Make-multiple-smbios-type-accumulate-sanely.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch293: kvm-smbios-Factor-out-smbios_maybe_add_str.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch294: kvm-hw-Pass-QEMUMachine-to-its-init-method.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch295: kvm-smbios-Set-system-manufacturer-product-version-by-de.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch296: kvm-smbios-Decouple-system-product-from-QEMUMachine.patch
# For bz#994490 - Set per-machine-type SMBIOS strings
Patch297: kvm-rhel-SMBIOS-type-1-branding.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch298: kvm-cow-make-reads-go-at-a-decent-speed.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch299: kvm-cow-make-writes-go-at-a-less-indecent-speed.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch300: kvm-cow-do-not-call-bdrv_co_is_allocated.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch301: kvm-block-keep-bs-total_sectors-up-to-date-even-for-grow.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch302: kvm-block-make-bdrv_co_is_allocated-static.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch303: kvm-block-do-not-use-total_sectors-in-bdrv_co_is_allocat.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch304: kvm-block-remove-bdrv_is_allocated_above-bdrv_co_is_allo.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch305: kvm-block-expect-errors-from-bdrv_co_is_allocated.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch306: kvm-block-Fix-compiler-warning-Werror-uninitialized.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch307: kvm-qemu-img-always-probe-the-input-image-for-allocated-.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch308: kvm-block-make-bdrv_has_zero_init-return-false-for-copy-.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch309: kvm-block-introduce-bdrv_get_block_status-API.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch310: kvm-block-define-get_block_status-return-value.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch311: kvm-block-return-get_block_status-data-and-flags-for-for.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch312: kvm-block-use-bdrv_has_zero_init-to-return-BDRV_BLOCK_ZE.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch313: kvm-block-return-BDRV_BLOCK_ZERO-past-end-of-backing-fil.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch314: kvm-qemu-img-add-a-map-subcommand.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch315: kvm-docs-qapi-document-qemu-img-map.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch316: kvm-raw-posix-return-get_block_status-data-and-flags.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch317: kvm-raw-posix-report-unwritten-extents-as-zero.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch318: kvm-block-add-default-get_block_status-implementation-fo.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch319: kvm-block-look-for-zero-blocks-in-bs-file.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch320: kvm-qemu-img-fix-invalid-JSON.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch321: kvm-block-get_block_status-set-pnum-0-on-error.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch322: kvm-block-get_block_status-avoid-segfault-if-there-is-no.patch
# For bz#989646 - Support backup vendors in qemu to access qcow disk readonly
Patch323: kvm-block-get_block_status-avoid-redundant-callouts-on-r.patch
# For bz#1025740 - Saving VM state on qcow2 images results in VM state corruption
Patch324: kvm-qcow2-Restore-total_sectors-value-in-save_vmstate.patch
# For bz#1025740 - Saving VM state on qcow2 images results in VM state corruption
Patch325: kvm-qcow2-Unset-zero_beyond_eof-in-save_vmstate.patch
# For bz#1025740 - Saving VM state on qcow2 images results in VM state corruption
Patch326: kvm-qemu-iotests-Test-for-loading-VM-state-from-qcow2.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch327: kvm-apic-rename-apic-specific-bitopts.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch328: kvm-hw-import-bitmap-operations-in-qdev-core-header.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch329: kvm-qemu-help-Sort-devices-by-logical-functionality.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch330: kvm-devices-Associate-devices-to-their-logical-category.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch331: kvm-Mostly-revert-qemu-help-Sort-devices-by-logical-func.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch332: kvm-qdev-monitor-Group-device_add-help-and-info-qdm-by-c.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch333: kvm-qdev-Replace-no_user-by-cannot_instantiate_with_devi.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch334: kvm-sysbus-Set-cannot_instantiate_with_device_add_yet.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch335: kvm-cpu-Document-why-cannot_instantiate_with_device_add_.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch336: kvm-apic-Document-why-cannot_instantiate_with_device_add.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch337: kvm-pci-host-Consistently-set-cannot_instantiate_with_de.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch338: kvm-ich9-Document-why-cannot_instantiate_with_device_add.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch339: kvm-piix3-piix4-Clean-up-use-of-cannot_instantiate_with_.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch340: kvm-vt82c686-Clean-up-use-of-cannot_instantiate_with_dev.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch341: kvm-isa-Clean-up-use-of-cannot_instantiate_with_device_a.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch342: kvm-qdev-Do-not-let-the-user-try-to-device_add-when-it-c.patch
# For bz#1001216 - Fix no_user or provide another way make devices unavailable with -device / device_add
Patch343: kvm-rhel-Revert-unwanted-cannot_instantiate_with_device_.patch
# For bz#1001076 - Disable or remove other block devices we won't support
Patch344: kvm-rhel-Revert-downstream-changes-to-unused-default-con.patch
# For bz#1001076 - Disable or remove other block devices we won't support
Patch345: kvm-rhel-Drop-cfi.pflash01-and-isa-ide-device.patch
# For bz#1001088 - Disable or remove display devices we won't support
Patch346: kvm-rhel-Drop-isa-vga-device.patch
# For bz#1001088 - Disable or remove display devices we won't support
Patch347: kvm-rhel-Make-isa-cirrus-vga-device-unavailable.patch
# For bz#1001123 - Disable or remove device ccid-card-emulated
Patch348: kvm-rhel-Make-ccid-card-emulated-device-unavailable.patch
# For bz#1005695 - QEMU should hide CPUID.0Dh values that it does not support
Patch349: kvm-x86-fix-migration-from-pre-version-12.patch
# For bz#1005695 - QEMU should hide CPUID.0Dh values that it does not support
Patch350: kvm-x86-cpuid-reconstruct-leaf-0Dh-data.patch
# For bz#920021 - qemu-kvm segment fault when reboot guest after hot unplug device with option ROM
Patch351: kvm-kvmvapic-Catch-invalid-ROM-size.patch
# For bz#920021 - qemu-kvm segment fault when reboot guest after hot unplug device with option ROM
Patch352: kvm-kvmvapic-Enter-inactive-state-on-hardware-reset.patch
# For bz#920021 - qemu-kvm segment fault when reboot guest after hot unplug device with option ROM
Patch353: kvm-kvmvapic-Clear-also-physical-ROM-address-when-enteri.patch
# For bz#987582 - Initial Virtualization Differentiation for RHEL7 (Live snapshots)
Patch354: kvm-block-optionally-disable-live-block-jobs.patch
# For bz#1022392 - Disable live-storage-migration in qemu-kvm (migrate -b/-i)
Patch355: kvm-migration-disable-live-block-migration-b-i-for-rhel-.patch
# For bz#987583 - Initial Virtualization Differentiation for RHEL7 (Ceph enablement)
Patch356: kvm-Build-ceph-rbd-only-for-rhev.patch
# For bz#1001180 - Disable or remove devices pci-serial-2x, pci-serial-4x
Patch357: kvm-rhel-Make-pci-serial-2x-and-pci-serial-4x-device-una.patch
# For bz#980415 - libusbx: error [_open_sysfs_attr] open /sys/bus/usb/devices/4-1/bConfigurationValue failed ret=-1 errno=2
Patch358: kvm-usb-host-libusb-Fix-reset-handling.patch
# For bz#980383 - The usb3.0 stick can't be returned back to host after shutdown guest with usb3.0 pass-through
Patch359: kvm-usb-host-libusb-Configuration-0-may-be-a-valid-confi.patch
# For bz#980383 - The usb3.0 stick can't be returned back to host after shutdown guest with usb3.0 pass-through
Patch360: kvm-usb-host-libusb-Detach-kernel-drivers-earlier.patch
# For bz#1010858 - Disable unused human monitor commands
Patch361: kvm-monitor-Remove-pci_add-command-for-Red-Hat-Enterpris.patch
# For bz#1010858 - Disable unused human monitor commands
Patch362: kvm-monitor-Remove-pci_del-command-for-Red-Hat-Enterpris.patch
# For bz#1010858 - Disable unused human monitor commands
Patch363: kvm-monitor-Remove-usb_add-del-commands-for-Red-Hat-Ente.patch
# For bz#1010858 - Disable unused human monitor commands
Patch364: kvm-monitor-Remove-host_net_add-remove-for-Red-Hat-Enter.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch365: kvm-fw_cfg-add-API-to-find-FW-cfg-object.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch366: kvm-pvpanic-use-FWCfgState-explicitly.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch367: kvm-pvpanic-initialization-cleanup.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch368: kvm-pvpanic-fix-fwcfg-for-big-endian-hosts.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch369: kvm-hw-misc-make-pvpanic-known-to-user.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch370: kvm-gdbstub-do-not-restart-crashed-guest.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch371: kvm-gdbstub-fix-for-commit-87f25c12bfeaaa0c41fb857713bbc.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch372: kvm-vl-allow-cont-from-panicked-state.patch
# For bz#990601 - pvpanic device triggers guest bugs when present by default
Patch373: kvm-hw-misc-don-t-create-pvpanic-device-by-default.patch
# For bz#1007176 - Add VPC and VHDX file formats as supported in qemu-kvm (read-only)
Patch374: kvm-block-vhdx-add-migration-blocker.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch375: kvm-block-drop-bs_snapshots-global-variable.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch376: kvm-block-move-snapshot-code-in-block.c-to-block-snapsho.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch377: kvm-block-fix-vvfat-error-path-for-enable_write_target.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch378: kvm-block-Bugfix-format-and-snapshot-used-in-drive-optio.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch379: kvm-iscsi-use-bdrv_new-instead-of-stack-structure.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch380: kvm-qcow2-Add-corrupt-bit.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch381: kvm-qcow2-Metadata-overlap-checks.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch382: kvm-qcow2-Employ-metadata-overlap-checks.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch383: kvm-qcow2-refcount-Move-OFLAG_COPIED-checks.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch384: kvm-qcow2-refcount-Repair-OFLAG_COPIED-errors.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch385: kvm-qcow2-refcount-Repair-shared-refcount-blocks.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch386: kvm-qcow2_check-Mark-image-consistent.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch387: kvm-qemu-iotests-Overlapping-cluster-allocations.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch388: kvm-w32-Fix-access-to-host-devices-regression.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch389: kvm-add-qemu-img-convert-n-option-skip-target-volume-cre.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch390: kvm-bdrv-Use-Error-for-opening-images.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch391: kvm-bdrv-Use-Error-for-creating-images.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch392: kvm-block-Error-parameter-for-open-functions.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch393: kvm-block-Error-parameter-for-create-functions.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch394: kvm-qemu-img-create-Emit-filename-on-error.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch395: kvm-qcow2-Use-Error-parameter.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch396: kvm-qemu-iotests-Adjustments-due-to-error-propagation.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch397: kvm-block-raw-Employ-error-parameter.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch398: kvm-block-raw-win32-Employ-error-parameter.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch399: kvm-blkdebug-Employ-error-parameter.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch400: kvm-blkverify-Employ-error-parameter.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch401: kvm-block-raw-posix-Employ-error-parameter.patch
# For bz#1026524 - Backport block layer error parameter patches
Patch402: kvm-block-raw-win32-Always-use-errno-in-hdev_open.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch403: kvm-qmp-Documentation-for-BLOCK_IMAGE_CORRUPTED.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch404: kvm-qcow2-Correct-snapshots-size-for-overlap-check.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch405: kvm-qcow2-CHECK_OFLAG_COPIED-is-obsolete.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch406: kvm-qcow2-Correct-endianness-in-overlap-check.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch407: kvm-qcow2-Switch-L1-table-in-a-single-sequence.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch408: kvm-qcow2-Use-pread-for-inactive-L1-in-overlap-check.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch409: kvm-qcow2-Remove-wrong-metadata-overlap-check.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch410: kvm-qcow2-Use-negated-overflow-check-mask.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch411: kvm-qcow2-Make-overlap-check-mask-variable.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch412: kvm-qcow2-Add-overlap-check-options.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch413: kvm-qcow2-Array-assigning-options-to-OL-check-bits.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch414: kvm-qcow2-Add-more-overlap-check-bitmask-macros.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch415: kvm-qcow2-Evaluate-overlap-check-options.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch416: kvm-qapi-types.py-Split-off-generate_struct_fields.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch417: kvm-qapi-types.py-Fix-enum-struct-sizes-on-i686.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch418: kvm-qapi-types-visit.py-Pass-whole-expr-dict-for-structs.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch419: kvm-qapi-types-visit.py-Inheritance-for-structs.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch420: kvm-blockdev-Introduce-DriveInfo.enable_auto_del.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch421: kvm-Implement-qdict_flatten.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch422: kvm-blockdev-blockdev-add-QMP-command.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch423: kvm-blockdev-Separate-ID-generation-from-DriveInfo-creat.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch424: kvm-blockdev-Pass-QDict-to-blockdev_init.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch425: kvm-blockdev-Move-parsing-of-media-option-to-drive_init.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch426: kvm-blockdev-Move-parsing-of-if-option-to-drive_init.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch427: kvm-blockdev-Moving-parsing-of-geometry-options-to-drive.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch428: kvm-blockdev-Move-parsing-of-boot-option-to-drive_init.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch429: kvm-blockdev-Move-bus-unit-index-processing-to-drive_ini.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch430: kvm-blockdev-Move-virtio-blk-device-creation-to-drive_in.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch431: kvm-blockdev-Remove-IF_-check-for-read-only-blockdev_ini.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch432: kvm-qemu-iotests-Check-autodel-behaviour-for-device_del.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch433: kvm-blockdev-Remove-media-parameter-from-blockdev_init.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch434: kvm-blockdev-Don-t-disable-COR-automatically-with-blockd.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch435: kvm-blockdev-blockdev_init-error-conversion.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch436: kvm-sd-Avoid-access-to-NULL-BlockDriverState.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch437: kvm-blockdev-fix-cdrom-read_only-flag.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch438: kvm-block-fix-backing-file-overriding.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch439: kvm-block-Disable-BDRV_O_COPY_ON_READ-for-the-backing-fi.patch
# For bz#978402 - [RFE] Add discard support to qemu-kvm layer
Patch440: kvm-block-Don-t-copy-backing-file-name-on-error.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch441: kvm-qemu-iotests-Try-creating-huge-qcow2-image.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch442: kvm-block-move-qmp-and-info-dump-related-code-to-block-q.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch443: kvm-block-dump-snapshot-and-image-info-to-specified-outp.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch444: kvm-block-add-snapshot-info-query-function-bdrv_query_sn.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch445: kvm-block-add-image-info-query-function-bdrv_query_image.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch446: kvm-qmp-add-ImageInfo-in-BlockDeviceInfo-used-by-query-b.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch447: kvm-vmdk-Implement-.bdrv_has_zero_init.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch448: kvm-qemu-iotests-Add-basic-ability-to-use-binary-sample-.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch449: kvm-qemu-iotests-Quote-TEST_IMG-and-TEST_DIR-usage.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch450: kvm-qemu-iotests-fix-test-case-059.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch451: kvm-qapi-Add-ImageInfoSpecific-type.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch452: kvm-block-Add-bdrv_get_specific_info.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch453: kvm-block-qapi-Human-readable-ImageInfoSpecific-dump.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch454: kvm-qcow2-Add-support-for-ImageInfoSpecific.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch455: kvm-qemu-iotests-Discard-specific-info-in-_img_info.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch456: kvm-qemu-iotests-Additional-info-from-qemu-img-info.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch457: kvm-vmdk-convert-error-code-to-use-errp.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch458: kvm-vmdk-refuse-enabling-zeroed-grain-with-flat-images.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch459: kvm-qapi-Add-optional-field-compressed-to-ImageInfo.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch460: kvm-vmdk-Only-read-cid-from-image-file-when-opening.patch
# For bz#980771 - [RFE]  qemu-img should be able to tell the compat version of a qcow2 image
Patch461: kvm-vmdk-Implment-bdrv_get_specific_info.patch
# For bz#1025877 - pci-assign lacks MSI affinity support
Patch462: kvm-pci-assign-Add-MSI-affinity-support.patch
# For bz#1025877 - pci-assign lacks MSI affinity support
Patch463: kvm-Fix-potential-resource-leak-missing-fclose.patch
# For bz#1025877 - pci-assign lacks MSI affinity support
Patch464: kvm-pci-assign-remove-the-duplicate-function-name-in-deb.patch
# For bz#922589 - e1000/rtl8139: qemu mac address can not be changed via set the hardware address in guest
Patch465: kvm-net-update-nic-info-during-device-reset.patch
# For bz#922589 - e1000/rtl8139: qemu mac address can not be changed via set the hardware address in guest
Patch466: kvm-net-e1000-update-network-information-when-macaddr-is.patch
# For bz#922589 - e1000/rtl8139: qemu mac address can not be changed via set the hardware address in guest
Patch467: kvm-net-rtl8139-update-network-information-when-macaddr-.patch
# For bz#1026689 - virtio-net: macaddr is reset but network info of monitor isn't updated
Patch468: kvm-virtio-net-fix-up-HMP-NIC-info-string-on-reset.patch
# For bz#1025477 - VFIO MSI affinity
Patch469: kvm-vfio-pci-VGA-quirk-update.patch
# For bz#1025477 - VFIO MSI affinity
Patch470: kvm-vfio-pci-Add-support-for-MSI-affinity.patch
# For bz#1026550 - QEMU VFIO update ROM loading code
Patch471: kvm-vfio-pci-Test-device-reset-capabilities.patch
# For bz#1026550 - QEMU VFIO update ROM loading code
Patch472: kvm-vfio-pci-Lazy-PCI-option-ROM-loading.patch
# For bz#1026550 - QEMU VFIO update ROM loading code
Patch473: kvm-vfio-pci-Cleanup-error_reports.patch
# For bz#1026550 - QEMU VFIO update ROM loading code
Patch474: kvm-vfio-pci-Add-dummy-PCI-ROM-write-accessor.patch
# For bz#1026550 - QEMU VFIO update ROM loading code
Patch475: kvm-vfio-pci-Fix-endian-issues-in-vfio_pci_size_rom.patch
# For bz#1025472 - Nvidia GPU device assignment - qemu-kvm - bus reset support
Patch476: kvm-linux-headers-Update-to-include-vfio-pci-hot-reset-s.patch
# For bz#1025472 - Nvidia GPU device assignment - qemu-kvm - bus reset support
Patch477: kvm-vfio-pci-Implement-PCI-hot-reset.patch
# For bz#1025474 - Nvidia GPU device assignment - qemu-kvm - NoSnoop support
Patch478: kvm-linux-headers-Update-for-KVM-VFIO-device.patch
# For bz#1025474 - Nvidia GPU device assignment - qemu-kvm - NoSnoop support
Patch479: kvm-vfio-pci-Make-use-of-new-KVM-VFIO-device.patch
# For bz#995866 - fix vmdk support to ESX images
Patch480: kvm-vmdk-Fix-vmdk_parse_extents.patch
# For bz#995866 - fix vmdk support to ESX images
Patch481: kvm-vmdk-fix-VMFS-extent-parsing.patch
# For bz#922589 - e1000/rtl8139: qemu mac address can not be changed via set the hardware address in guest
#Patch482: kvm-e1000-rtl8139-update-HMP-NIC-when-every-bit-is-writt.patch
# Patch 482 removed as it has to be discussed and should not be applied yet
# For bz#1005039 - add compat property to disable ctrl_mac_addr feature
Patch483: kvm-don-t-disable-ctrl_mac_addr-feature-for-6.5-machine-.patch
# For bz#848203 - MAC Programming for virtio over macvtap - qemu-kvm support
Patch484: kvm-qapi-qapi-visit.py-fix-list-handling-for-union-types.patch
# For bz#848203 - MAC Programming for virtio over macvtap - qemu-kvm support
Patch485: kvm-qapi-qapi-visit.py-native-list-support.patch
# For bz#848203 - MAC Programming for virtio over macvtap - qemu-kvm support
Patch486: kvm-qapi-enable-generation-of-native-list-code.patch
# For bz#848203 - MAC Programming for virtio over macvtap - qemu-kvm support
Patch487: kvm-net-add-support-of-mac-programming-over-macvtap-in-Q.patch
# For bz#1029539 - Machine type rhel6.1.0 and  balloon device cause migration fail from RHEL6.5 host to RHEL7.0 host
Patch488: kvm-pc-drop-virtio-balloon-pci-event_idx-compat-property.patch
# For bz#922463 - qemu-kvm core dump when virtio-net multi queue guest hot-unpluging vNIC
Patch489: kvm-virtio-net-only-delete-bh-that-existed.patch
# For bz#1029370 - [whql][netkvm][wlk] Virtio-net device handles RX multicast filtering improperly
Patch490: kvm-virtio-net-broken-RX-filtering-logic-fixed.patch
# For bz#1025138 - Read/Randread/Randrw performance regression
Patch491: kvm-block-Avoid-unecessary-drv-bdrv_getlength-calls.patch
# For bz#1025138 - Read/Randread/Randrw performance regression
Patch492: kvm-block-Round-up-total_sectors.patch
# For bz#1016952 - qemu-kvm man page guide wrong path for qemu-bridge-helper
Patch493: kvm-doc-fix-hardcoded-helper-path.patch
# For bz#971933 - QMP: add RHEL's vendor extension prefix
Patch494: kvm-introduce-RFQDN_REDHAT-RHEL-6-7-fwd.patch
# For bz#971938 - QMP: Add error reason to BLOCK_IO_ERROR event
Patch495: kvm-error-reason-in-BLOCK_IO_ERROR-BLOCK_JOB_ERROR-event.patch
# For bz#895041 - QMP: forward port I/O error debug messages
Patch496: kvm-improve-debuggability-of-BLOCK_IO_ERROR-BLOCK_JOB_ER.patch
# For bz#1029275 - Guest only find one 82576 VF(function 0) while use multifunction
Patch497: kvm-vfio-pci-Fix-multifunction-on.patch
# For bz#1026739 - qcow2: Switch to compat=1.1 default for new images
Patch498: kvm-qcow2-Change-default-for-new-images-to-compat-1.1.patch
# For bz#1026739 - qcow2: Switch to compat=1.1 default for new images
Patch499: kvm-qcow2-change-default-for-new-images-to-compat-1.1-pa.patch
# For bz#1032862 - virtio-rng-egd: repeatedly read same random data-block w/o considering the buffer offset
Patch500: kvm-rng-egd-offset-the-point-when-repeatedly-read-from-t.patch
# For bz#1007334 - CVE-2013-4344 qemu-kvm: qemu: buffer overflow in scsi_target_emulate_report_luns [rhel-7.0]
Patch501: kvm-scsi-Allocate-SCSITargetReq-r-buf-dynamically-CVE-20.patch
# For bz#1033810 - memory leak in using object_get_canonical_path()
Patch502: kvm-virtio-net-fix-the-memory-leak-in-rxfilter_notify.patch
# For bz#1033810 - memory leak in using object_get_canonical_path()
Patch503: kvm-qom-Fix-memory-leak-in-object_property_set_link.patch
# For bz#1036537 - Cross version migration from RHEL6.5 host to RHEL7.0 host with sound device failed.
Patch504: kvm-fix-intel-hda-live-migration.patch
# For bz#1029743 - qemu-kvm core dump after hot plug/unplug 82576 PF about 100 times
Patch505: kvm-vfio-pci-Release-all-MSI-X-vectors-when-disabled.patch
# For bz#921490 - qemu-kvm core dumped after hot plugging more than 11 VF through vfio-pci
Patch506: kvm-Query-KVM-for-available-memory-slots.patch
# For bz#1039501 - [provisioning] discard=on broken
Patch507: kvm-block-Dont-ignore-previously-set-bdrv_flags.patch
# For bz#997832 - Backport trace fixes proactively to avoid confusion and silly conflicts
Patch508: kvm-cleanup-trace-events.pl-New.patch
# For bz#997832 - Backport trace fixes proactively to avoid confusion and silly conflicts
Patch509: kvm-slavio_misc-Fix-slavio_led_mem_readw-_writew-tracepo.patch
# For bz#997832 - Backport trace fixes proactively to avoid confusion and silly conflicts
Patch510: kvm-milkymist-minimac2-Fix-minimac2_read-_write-tracepoi.patch
# For bz#997832 - Backport trace fixes proactively to avoid confusion and silly conflicts
Patch511: kvm-trace-events-Drop-unused-events.patch
# For bz#997832 - Backport trace fixes proactively to avoid confusion and silly conflicts
Patch512: kvm-trace-events-Fix-up-source-file-comments.patch
# For bz#997832 - Backport trace fixes proactively to avoid confusion and silly conflicts
Patch513: kvm-trace-events-Clean-up-with-scripts-cleanup-trace-eve.patch
# For bz#997832 - Backport trace fixes proactively to avoid confusion and silly conflicts
Patch514: kvm-trace-events-Clean-up-after-removal-of-old-usb-host-.patch
# For bz#1027571 - [virtio-win]win8.1 guest network can not resume automatically after do "set_link tap1 on"
Patch515: kvm-net-Update-netdev-peer-on-link-change.patch
# For bz#1003773 - When virtio-blk-pci device with dataplane is failed to be added, the drive cannot be released.
Patch516: kvm-qdev-monitor-Unref-device-when-device_add-fails.patch
# For bz#1003773 - When virtio-blk-pci device with dataplane is failed to be added, the drive cannot be released.
Patch517: kvm-qdev-Drop-misleading-qdev_free-function.patch
# For bz#1003773 - When virtio-blk-pci device with dataplane is failed to be added, the drive cannot be released.
Patch518: kvm-blockdev-fix-drive_init-opts-and-bs_opts-leaks.patch
# For bz#1003773 - When virtio-blk-pci device with dataplane is failed to be added, the drive cannot be released.
Patch519: kvm-libqtest-rename-qmp-to-qmp_discard_response.patch
# For bz#1003773 - When virtio-blk-pci device with dataplane is failed to be added, the drive cannot be released.
Patch520: kvm-libqtest-add-qmp-fmt-.-QDict-function.patch
# For bz#1003773 - When virtio-blk-pci device with dataplane is failed to be added, the drive cannot be released.
Patch521: kvm-blockdev-test-add-test-case-for-drive_add-duplicate-.patch
# For bz#1003773 - When virtio-blk-pci device with dataplane is failed to be added, the drive cannot be released.
Patch522: kvm-qdev-monitor-test-add-device_add-leak-test-cases.patch
# For bz#1003773 - When virtio-blk-pci device with dataplane is failed to be added, the drive cannot be released.
Patch523: kvm-qtest-Use-display-none-by-default.patch
# For bz#1034876 - export acpi tables to guests
Patch524: kvm-range-add-Range-structure.patch
# For bz#1034876 - export acpi tables to guests
Patch525: kvm-range-add-Range-to-typedefs.patch
# For bz#1034876 - export acpi tables to guests
Patch526: kvm-range-add-min-max-operations-on-ranges.patch
# For bz#1034876 - export acpi tables to guests
Patch527: kvm-qdev-Add-SIZE-type-to-qdev-properties.patch
# For bz#1034876 - export acpi tables to guests
Patch528: kvm-qapi-make-visit_type_size-fallback-to-type_int.patch
# For bz#1034876 - export acpi tables to guests
Patch529: kvm-pc-move-IO_APIC_DEFAULT_ADDRESS-to-include-hw-i386-i.patch
# For bz#1034876 - export acpi tables to guests
Patch530: kvm-pci-add-helper-to-retrieve-the-64-bit-range.patch
# For bz#1034876 - export acpi tables to guests
Patch531: kvm-pci-fix-up-w64-size-calculation-helper.patch
# For bz#1034876 - export acpi tables to guests
Patch532: kvm-refer-to-FWCfgState-explicitly.patch
# For bz#1034876 - export acpi tables to guests
Patch533: kvm-fw_cfg-move-typedef-to-qemu-typedefs.h.patch
# For bz#1034876 - export acpi tables to guests
Patch534: kvm-arch_init-align-MR-size-to-target-page-size.patch
# For bz#1034876 - export acpi tables to guests
Patch535: kvm-loader-store-FW-CFG-ROM-files-in-RAM.patch
# For bz#1034876 - export acpi tables to guests
Patch536: kvm-pci-store-PCI-hole-ranges-in-guestinfo-structure.patch
# For bz#1034876 - export acpi tables to guests
Patch537: kvm-pc-pass-PCI-hole-ranges-to-Guests.patch
# For bz#1034876 - export acpi tables to guests
Patch538: kvm-pc-replace-i440fx_common_init-with-i440fx_init.patch
# For bz#1034876 - export acpi tables to guests
Patch539: kvm-pc-don-t-access-fw-cfg-if-NULL.patch
# For bz#1034876 - export acpi tables to guests
Patch540: kvm-pc-add-I440FX-QOM-cast-macro.patch
# For bz#1034876 - export acpi tables to guests
Patch541: kvm-pc-limit-64-bit-hole-to-2G-by-default.patch
# For bz#1034876 - export acpi tables to guests
Patch542: kvm-q35-make-pci-window-address-size-match-guest-cfg.patch
# For bz#1034876 - export acpi tables to guests
Patch543: kvm-q35-use-64-bit-window-programmed-by-guest.patch
# For bz#1034876 - export acpi tables to guests
Patch544: kvm-piix-use-64-bit-window-programmed-by-guest.patch
# For bz#1034876 - export acpi tables to guests
Patch545: kvm-pc-fix-regression-for-64-bit-PCI-memory.patch
# For bz#1034876 - export acpi tables to guests
Patch546: kvm-cleanup-object.h-include-error.h-directly.patch
# For bz#1034876 - export acpi tables to guests
Patch547: kvm-qom-cleanup-struct-Error-references.patch
# For bz#1034876 - export acpi tables to guests
Patch548: kvm-qom-add-pointer-to-int-property-helpers.patch
# For bz#1034876 - export acpi tables to guests
Patch549: kvm-fw_cfg-interface-to-trigger-callback-on-read.patch
# For bz#1034876 - export acpi tables to guests
Patch550: kvm-loader-support-for-unmapped-ROM-blobs.patch
# For bz#1034876 - export acpi tables to guests
Patch551: kvm-pcie_host-expose-UNMAPPED-macro.patch
# For bz#1034876 - export acpi tables to guests
Patch552: kvm-pcie_host-expose-address-format.patch
# For bz#1034876 - export acpi tables to guests
Patch553: kvm-q35-use-macro-for-MCFG-property-name.patch
# For bz#1034876 - export acpi tables to guests
Patch554: kvm-q35-expose-mmcfg-size-as-a-property.patch
# For bz#1034876 - export acpi tables to guests
Patch555: kvm-i386-add-ACPI-table-files-from-seabios.patch
# For bz#1034876 - export acpi tables to guests
Patch556: kvm-acpi-add-rules-to-compile-ASL-source.patch
# For bz#1034876 - export acpi tables to guests
Patch557: kvm-acpi-pre-compiled-ASL-files.patch
# For bz#1034876 - export acpi tables to guests
Patch558: kvm-acpi-ssdt-pcihp-updat-generated-file.patch
# For bz#1034876 - export acpi tables to guests
Patch559: kvm-loader-use-file-path-size-from-fw_cfg.h.patch
# For bz#1034876 - export acpi tables to guests
Patch560: kvm-i386-add-bios-linker-loader.patch
# For bz#1034876 - export acpi tables to guests
Patch561: kvm-loader-allow-adding-ROMs-in-done-callbacks.patch
# For bz#1034876 - export acpi tables to guests
Patch562: kvm-i386-define-pc-guest-info.patch
# For bz#1034876 - export acpi tables to guests
Patch563: kvm-acpi-piix-add-macros-for-acpi-property-names.patch
# For bz#1034876 - export acpi tables to guests
Patch564: kvm-piix-APIs-for-pc-guest-info.patch
# For bz#1034876 - export acpi tables to guests
Patch565: kvm-ich9-APIs-for-pc-guest-info.patch
# For bz#1034876 - export acpi tables to guests
Patch566: kvm-pvpanic-add-API-to-access-io-port.patch
# For bz#1034876 - export acpi tables to guests
Patch567: kvm-hpet-add-API-to-find-it.patch
# For bz#1034876 - export acpi tables to guests
Patch568: kvm-hpet-fix-build-with-CONFIG_HPET-off.patch
# For bz#1034876 - export acpi tables to guests
Patch569: kvm-acpi-add-interface-to-access-user-installed-tables.patch
# For bz#1034876 - export acpi tables to guests
Patch570: kvm-pc-use-new-api-to-add-builtin-tables.patch
# For bz#1034876 - export acpi tables to guests
Patch571: kvm-i386-ACPI-table-generation-code-from-seabios.patch
# For bz#1034876 - export acpi tables to guests
Patch572: kvm-ssdt-fix-PBLK-length.patch
# For bz#1034876 - export acpi tables to guests
Patch573: kvm-ssdt-proc-update-generated-file.patch
# For bz#1034876 - export acpi tables to guests
Patch574: kvm-pc-disable-pci-info.patch
# For bz#1034876 - export acpi tables to guests
Patch575: kvm-acpi-build-fix-build-on-glib-2.22.patch
# For bz#1034876 - export acpi tables to guests
Patch576: kvm-acpi-build-fix-build-on-glib-2.14.patch
# For bz#1034876 - export acpi tables to guests
Patch577: kvm-acpi-build-fix-support-for-glib-2.22.patch
# For bz#1034876 - export acpi tables to guests
Patch578: kvm-acpi-build-Fix-compiler-warning-missing-gnu_printf-f.patch
# For bz#1034876 - export acpi tables to guests
Patch579: kvm-exec-Fix-prototype-of-phys_mem_set_alloc-and-related.patch
# For bz#1034876 - export acpi tables to guests
Patch580: kvm-hw-i386-Makefile.obj-use-PYTHON-to-run-.py-scripts-c.patch
# For bz#1026314
Patch581: kvm-seccomp-add-kill-to-the-syscall-whitelist.patch
Patch582: kvm-json-parser-fix-handling-of-large-whole-number-value.patch
Patch583: kvm-qapi-add-QMP-input-test-for-large-integers.patch
Patch584: kvm-qapi-fix-visitor-serialization-tests-for-numbers-dou.patch
Patch585: kvm-qapi-add-native-list-coverage-for-visitor-serializat.patch
Patch586: kvm-qapi-add-native-list-coverage-for-QMP-output-visitor.patch
Patch587: kvm-qapi-add-native-list-coverage-for-QMP-input-visitor-.patch
Patch588: kvm-qapi-lack-of-two-commas-in-dict.patch
Patch589: kvm-tests-QAPI-schema-parser-tests.patch
Patch590: kvm-tests-Use-qapi-schema-test.json-as-schema-parser-tes.patch
Patch591: kvm-qapi.py-Restructure-lexer-and-parser.patch
Patch592: kvm-qapi.py-Decent-syntax-error-reporting.patch
Patch593: kvm-qapi.py-Reject-invalid-characters-in-schema-file.patch
Patch594: kvm-qapi.py-Fix-schema-parser-to-check-syntax-systematic.patch
Patch595: kvm-qapi.py-Fix-diagnosing-non-objects-at-a-schema-s-top.patch
Patch596: kvm-qapi.py-Rename-expr_eval-to-expr-in-parse_schema.patch
Patch597: kvm-qapi.py-Permit-comments-starting-anywhere-on-the-lin.patch
Patch598: kvm-scripts-qapi.py-Avoid-syntax-not-supported-by-Python.patch
Patch599: kvm-tests-Fix-schema-parser-test-for-in-tree-build.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch600: kvm-add-a-header-file-for-atomic-operations.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch601: kvm-savevm-Fix-potential-memory-leak.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch602: kvm-migration-Fail-migration-on-bdrv_flush_all-error.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch603: kvm-rdma-add-documentation.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch604: kvm-rdma-introduce-qemu_update_position.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch605: kvm-rdma-export-yield_until_fd_readable.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch606: kvm-rdma-export-throughput-w-MigrationStats-QMP.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch607: kvm-rdma-introduce-qemu_file_mode_is_not_valid.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch608: kvm-rdma-introduce-qemu_ram_foreach_block.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch609: kvm-rdma-new-QEMUFileOps-hooks.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch610: kvm-rdma-introduce-capability-x-rdma-pin-all.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch611: kvm-rdma-update-documentation-to-reflect-new-unpin-suppo.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch612: kvm-rdma-bugfix-ram_control_save_page.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch613: kvm-rdma-introduce-ram_handle_compressed.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch614: kvm-rdma-core-logic.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch615: kvm-rdma-send-pc.ram.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch616: kvm-rdma-allow-state-transitions-between-other-states-be.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch617: kvm-rdma-introduce-MIG_STATE_NONE-and-change-MIG_STATE_S.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch618: kvm-rdma-account-for-the-time-spent-in-MIG_STATE_SETUP-t.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch619: kvm-rdma-bugfix-make-IPv6-support-work.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch620: kvm-rdma-forgot-to-turn-off-the-debugging-flag.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch621: kvm-rdma-correct-newlines-in-error-statements.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch622: kvm-rdma-don-t-use-negative-index-to-array.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch623: kvm-rdma-qemu_rdma_post_send_control-uses-wrongly-RDMA_W.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch624: kvm-rdma-use-DRMA_WRID_READY.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch625: kvm-rdma-memory-leak-RDMAContext-host.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch626: kvm-rdma-use-resp.len-after-validation-in-qemu_rdma_regi.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch627: kvm-rdma-validate-RDMAControlHeader-len.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch628: kvm-rdma-check-if-RDMAControlHeader-len-match-transferre.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch629: kvm-rdma-proper-getaddrinfo-handling.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch630: kvm-rdma-IPv6-over-Ethernet-RoCE-is-broken-in-linux-work.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch631: kvm-rdma-remaining-documentation-fixes.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch632: kvm-rdma-silly-ipv6-bugfix.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch633: kvm-savevm-fix-wrong-initialization-by-ram_control_load_.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch634: kvm-arch_init-right-return-for-ram_save_iterate.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch635: kvm-rdma-clean-up-of-qemu_rdma_cleanup.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch636: kvm-rdma-constify-ram_chunk_-index-start-end.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch637: kvm-migration-Fix-debug-print-type.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch638: kvm-arch_init-make-is_zero_page-accept-size.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch639: kvm-migration-ram_handle_compressed.patch
# For bz#1011720 - [HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM
Patch640: kvm-migration-fix-spice-migration.patch
# For bz#678368 - RFE: Support more than 8 assigned devices
Patch641: kvm-pci-assign-cap-number-of-devices-that-can-be-assigne.patch
# For bz#678368 - RFE: Support more than 8 assigned devices
Patch642: kvm-vfio-cap-number-of-devices-that-can-be-assigned.patch
# For bz#1039513 - backport remote wakeup for ehci
Patch643: kvm-Revert-usb-tablet-Don-t-claim-wakeup-capability-for-.patch
# For bz#1026554 - qemu: mempath: prefault pages manually
Patch644: kvm-mempath-prefault-pages-manually-v4.patch
# For bz#1007710 - [RFE] Enable qemu-img to support VMDK version 3
# For bz#1029852 - qemu-img fails to convert vmdk image with "qemu-img: Could not open 'image.vmdk'"
Patch645: kvm-vmdk-Allow-read-only-open-of-VMDK-version-3.patch
# For bz#1035132 - fail to boot and call trace with x-data-plane=on specified for rhel6.5 guest
Patch646: kvm-virtio_pci-fix-level-interrupts-with-irqfd.patch
# For bz#889051 - Commands "__com.redhat_drive_add/del" don' t exist in RHEL7.0
Patch647: kvm-QMP-Forward-port-__com.redhat_drive_del-from-RHEL-6.patch
# For bz#889051 - Commands "__com.redhat_drive_add/del" don' t exist in RHEL7.0
Patch648: kvm-QMP-Forward-port-__com.redhat_drive_add-from-RHEL-6.patch
# For bz#889051 - Commands "__com.redhat_drive_add/del" don' t exist in RHEL7.0
Patch649: kvm-HMP-Forward-port-__com.redhat_drive_add-from-RHEL-6.patch
# For bz#889051 - Commands "__com.redhat_drive_add/del" don' t exist in RHEL7.0
Patch650: kvm-QMP-Document-throttling-parameters-of-__com.redhat_d.patch
# For bz#889051 - Commands "__com.redhat_drive_add/del" don' t exist in RHEL7.0
Patch651: kvm-HMP-Disable-drive_add-for-Red-Hat-Enterprise-Linux.patch
Patch652: kvm-Revert-HMP-Disable-drive_add-for-Red-Hat-Enterprise-2.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch653: kvm-block-change-default-of-.has_zero_init-to-0.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch654: kvm-iscsi-factor-out-sector-conversions.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch655: kvm-iscsi-add-logical-block-provisioning-information-to-.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch656: kvm-iscsi-add-.bdrv_get_block_status.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch657: kvm-iscsi-split-discard-requests-in-multiple-parts.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch658: kvm-block-make-BdrvRequestFlags-public.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch659: kvm-block-add-flags-to-bdrv_-_write_zeroes.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch660: kvm-block-introduce-BDRV_REQ_MAY_UNMAP-request-flag.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch661: kvm-block-add-logical-block-provisioning-info-to-BlockDr.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch662: kvm-block-add-wrappers-for-logical-block-provisioning-in.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch663: kvm-block-iscsi-add-.bdrv_get_info.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch664: kvm-block-add-BlockLimits-structure-to-BlockDriverState.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch665: kvm-block-raw-copy-BlockLimits-on-raw_open.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch666: kvm-block-honour-BlockLimits-in-bdrv_co_do_write_zeroes.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch667: kvm-block-honour-BlockLimits-in-bdrv_co_discard.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch668: kvm-iscsi-set-limits-in-BlockDriverState.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch669: kvm-iscsi-simplify-iscsi_co_discard.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch670: kvm-iscsi-add-bdrv_co_write_zeroes.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch671: kvm-block-introduce-bdrv_make_zero.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch672: kvm-block-get_block_status-fix-BDRV_BLOCK_ZERO-for-unall.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch673: kvm-qemu-img-add-support-for-fully-allocated-images.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch674: kvm-qemu-img-conditionally-zero-out-target-on-convert.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch675: kvm-block-generalize-BlockLimits-handling-to-cover-bdrv_.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch676: kvm-block-add-flags-to-BlockRequest.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch677: kvm-block-add-flags-argument-to-bdrv_co_write_zeroes-tra.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch678: kvm-block-add-bdrv_aio_write_zeroes.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch679: kvm-block-handle-ENOTSUP-from-discard-in-generic-code.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch680: kvm-block-make-bdrv_co_do_write_zeroes-stricter-in-produ.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch681: kvm-vpc-vhdx-add-get_info.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch682: kvm-block-drivers-add-discard-write_zeroes-properties-to.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch683: kvm-block-drivers-expose-requirement-for-write-same-alig.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch684: kvm-block-iscsi-remove-.bdrv_has_zero_init.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch685: kvm-block-iscsi-updated-copyright.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch686: kvm-block-iscsi-check-WRITE-SAME-support-differently-dep.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch687: kvm-scsi-disk-catch-write-protection-errors-in-UNMAP.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch688: kvm-scsi-disk-reject-ANCHOR-1-for-UNMAP-and-WRITE-SAME-c.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch689: kvm-scsi-disk-correctly-implement-WRITE-SAME.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch690: kvm-scsi-disk-fix-WRITE-SAME-with-large-non-zero-payload.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch691: kvm-raw-posix-implement-write_zeroes-with-MAY_UNMAP-for-.patch.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch692: kvm-raw-posix-implement-write_zeroes-with-MAY_UNMAP-for-.patch.patch.patch.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch693: kvm-raw-posix-add-support-for-write_zeroes-on-XFS-and-bl.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch694: kvm-qemu-iotests-033-is-fast.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch695: kvm-qemu-img-add-support-for-skipping-zeroes-in-input-du.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch696: kvm-qemu-img-fix-usage-instruction-for-qemu-img-convert.patch.patch
# For bz#1007815 - fix WRITE SAME support
Patch697: kvm-block-iscsi-set-bdi-cluster_size.patch.patch
# For bz#1039557 - optimize qemu-img for thin provisioned images
Patch698: kvm-block-add-opt_transfer_length-to-BlockLimits.patch.patch
# For bz#1039557 - optimize qemu-img for thin provisioned images
Patch699: kvm-block-iscsi-set-bs-bl.opt_transfer_length.patch.patch
# For bz#1039557 - optimize qemu-img for thin provisioned images
Patch700: kvm-qemu-img-dynamically-adjust-iobuffer-size-during-con.patch.patch
# For bz#1039557 - optimize qemu-img for thin provisioned images
Patch701: kvm-qemu-img-round-down-request-length-to-an-aligned-sec.patch.patch
# For bz#1039557 - optimize qemu-img for thin provisioned images
Patch702: kvm-qemu-img-decrease-progress-update-interval-on-conver.patch.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch703: kvm-block-qemu-iotests-for-vhdx-read-sample-dynamic-imag.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch704: kvm-block-qemu-iotests-add-quotes-to-TEST_IMG-usage-io-p.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch705: kvm-block-qemu-iotests-fix-_make_test_img-to-work-with-s.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch706: kvm-block-qemu-iotests-add-quotes-to-TEST_IMG.base-usage.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch707: kvm-block-qemu-iotests-add-quotes-to-TEST_IMG-usage-in-0.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch708: kvm-block-qemu-iotests-removes-duplicate-double-quotes-i.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch709: kvm-block-vhdx-minor-comments-and-typo-correction.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch710: kvm-block-vhdx-add-header-update-capability.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch711: kvm-block-vhdx-code-movement-VHDXMetadataEntries-and-BDR.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch712: kvm-block-vhdx-log-support-struct-and-defines.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch713: kvm-block-vhdx-break-endian-translation-functions-out.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch714: kvm-block-vhdx-update-log-guid-in-header-and-first-write.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch715: kvm-block-vhdx-code-movement-move-vhdx_close-above-vhdx_.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch716: kvm-block-vhdx-log-parsing-replay-and-flush-support.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch717: kvm-block-vhdx-add-region-overlap-detection-for-image-fi.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch718: kvm-block-vhdx-add-log-write-support.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch719: kvm-block-vhdx-write-support.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch720: kvm-block-vhdx-remove-BAT-file-offset-bit-shifting.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch721: kvm-block-vhdx-move-more-endian-translations-to-vhdx-end.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch722: kvm-block-vhdx-break-out-code-operations-to-functions.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch723: kvm-block-vhdx-fix-comment-typos-in-header-fix-incorrect.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch724: kvm-block-vhdx-add-.bdrv_create-support.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch725: kvm-block-vhdx-update-_make_test_img-to-filter-out-vhdx-.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch726: kvm-block-qemu-iotests-for-vhdx-add-write-test-support.patch
# For bz#879234 - [RFE] qemu-img: Add/improve support for VHDX format
Patch727: kvm-block-vhdx-qemu-iotest-log-replay-of-data-sector.patch
# For bz#965636 - streaming with no backing file should not do anything
Patch728: kvm-block-stream-Don-t-stream-unbacked-devices.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch729: kvm-qemu-io-Let-open-pass-options-to-block-driver.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch730: kvm-qcow2.py-Subcommand-for-changing-header-fields.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch731: kvm-qemu-iotests-Remaining-error-propagation-adjustments.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch732: kvm-qemu-iotests-Add-test-for-inactive-L2-overlap.patch
# For bz#1004347 - Backport qcow2 corruption prevention patches
Patch733: kvm-qemu-iotests-Adjust-test-result-039.patch
# For bz#1048671 - virtio-net: mac_table change isn't recovered in error state
Patch734: kvm-virtio-net-don-t-update-mac_table-in-error-state.patch
# For bz#1032904 - qemu-img can not create libiscsi qcow2_v3 image
Patch735: kvm-qcow2-Zero-initialise-first-cluster-for-new-images.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch736: kvm-option-Add-assigned-flag-to-QEMUOptionParameter.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch737: kvm-qcow2-refcount-Snapshot-update-for-zero-clusters.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch738: kvm-qemu-iotests-Snapshotting-zero-clusters.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch739: kvm-block-Image-file-option-amendment.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch740: kvm-qcow2-cache-Empty-cache.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch741: kvm-qcow2-cluster-Expand-zero-clusters.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch742: kvm-qcow2-Save-refcount-order-in-BDRVQcowState.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch743: kvm-qcow2-Implement-bdrv_amend_options.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch744: kvm-qcow2-Correct-bitmap-size-in-zero-expansion.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch745: kvm-qcow2-Free-only-newly-allocated-clusters-on-error.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch746: kvm-qcow2-Add-missing-space-in-error-message.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch747: kvm-qemu-iotest-qcow2-image-option-amendment.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch748: kvm-qemu-iotests-New-test-case-in-061.patch
# For bz#1033490 - Cannot upgrade/downgrade qcow2 images
Patch749: kvm-qemu-iotests-Preallocated-zero-clusters-in-061.patch
# For bz#972773 - RHEL7: Clarify support statement in KVM help
Patch750: kvm-Add-support-statement-to-help-output.patch
# For bz#903910 - RHEL7 does not have equivalent functionality for __com.redhat_qxl_screendump
Patch751: kvm-__com.redhat_qxl_screendump-add-docs.patch
# For bz#999836 - -m 1 crashes
Patch752: kvm-vl-Round-memory-sizes-below-2MiB-up-to-2MiB.patch
# For bz#1044845 - QEMU seccomp sandbox - exit if seccomp_init() fails
Patch753: kvm-seccomp-exit-if-seccomp_init-fails.patch
# For bz#1034876 - export acpi tables to guests
Patch754: kvm-configure-make-iasl-option-actually-work.patch
# For bz#1034876 - export acpi tables to guests
Patch755: kvm-acpi-build-disable-with-no-acpi.patch
# For bz#1039513 - backport remote wakeup for ehci
Patch756: kvm-ehci-implement-port-wakeup.patch
# For bz#1026712 - Qemu core dumpd when boot guest with driver name as "virtio-pci"
# For bz#1046007 - qemu-kvm aborted when hot plug PCI device to guest with romfile and rombar=0
Patch757: kvm-qdev-monitor-Fix-crash-when-device_add-is-called-wit.patch
# For bz#1035001 - VHDX: journal log should not be replayed by default, but rather via qemu-img check -r all
Patch758: kvm-block-vhdx-improve-error-message-and-.bdrv_check-imp.patch
# For bz#1017650 - need to update qemu-img man pages on "VHDX" format
Patch759: kvm-docs-updated-qemu-img-man-page-and-qemu-doc-to-refle.patch
# For bz#1052340 - pvticketlocks: default on
Patch760: kvm-enable-pvticketlocks-by-default.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch761: kvm-fix-boot-strict-regressed-in-commit-6ef4716.patch
# For bz#997817 - -boot order and -boot once regressed since RHEL-6
Patch762: kvm-vl-make-boot_strict-variable-static-not-used-outside.patch
# For bz#997559 - Improve live migration bitmap handling
Patch763: kvm-bitmap-use-long-as-index.patch
# For bz#997559 - Improve live migration bitmap handling
Patch764: kvm-memory-cpu_physical_memory_set_dirty_flags-result-is.patch
# For bz#997559 - Improve live migration bitmap handling
Patch765: kvm-memory-cpu_physical_memory_set_dirty_range-return-vo.patch
# For bz#997559 - Improve live migration bitmap handling
Patch766: kvm-exec-use-accessor-function-to-know-if-memory-is-dirt.patch
# For bz#997559 - Improve live migration bitmap handling
Patch767: kvm-memory-create-function-to-set-a-single-dirty-bit.patch
# For bz#997559 - Improve live migration bitmap handling
Patch768: kvm-exec-drop-useless-if.patch
# For bz#997559 - Improve live migration bitmap handling
Patch769: kvm-exec-create-function-to-get-a-single-dirty-bit.patch
# For bz#997559 - Improve live migration bitmap handling
Patch770: kvm-memory-make-cpu_physical_memory_is_dirty-return-bool.patch
# For bz#997559 - Improve live migration bitmap handling
Patch771: kvm-memory-all-users-of-cpu_physical_memory_get_dirty-us.patch
# For bz#997559 - Improve live migration bitmap handling
Patch772: kvm-memory-set-single-dirty-flags-when-possible.patch
# For bz#997559 - Improve live migration bitmap handling
Patch773: kvm-memory-cpu_physical_memory_set_dirty_range-always-di.patch
# For bz#997559 - Improve live migration bitmap handling
Patch774: kvm-memory-cpu_physical_memory_mask_dirty_range-always-c.patch
# For bz#997559 - Improve live migration bitmap handling
Patch775: kvm-memory-use-bit-2-for-migration.patch
# For bz#997559 - Improve live migration bitmap handling
Patch776: kvm-memory-make-sure-that-client-is-always-inside-range.patch
# For bz#997559 - Improve live migration bitmap handling
Patch777: kvm-memory-only-resize-dirty-bitmap-when-memory-size-inc.patch
# For bz#997559 - Improve live migration bitmap handling
Patch778: kvm-memory-cpu_physical_memory_clear_dirty_flag-result-i.patch
# For bz#997559 - Improve live migration bitmap handling
Patch779: kvm-bitmap-Add-bitmap_zero_extend-operation.patch
# For bz#997559 - Improve live migration bitmap handling
Patch780: kvm-memory-split-dirty-bitmap-into-three.patch
# For bz#997559 - Improve live migration bitmap handling
Patch781: kvm-memory-unfold-cpu_physical_memory_clear_dirty_flag-i.patch
# For bz#997559 - Improve live migration bitmap handling
Patch782: kvm-memory-unfold-cpu_physical_memory_set_dirty-in-its-o.patch
# For bz#997559 - Improve live migration bitmap handling
Patch783: kvm-memory-unfold-cpu_physical_memory_set_dirty_flag.patch
# For bz#997559 - Improve live migration bitmap handling
Patch784: kvm-memory-make-cpu_physical_memory_get_dirty-the-main-f.patch
# For bz#997559 - Improve live migration bitmap handling
Patch785: kvm-memory-cpu_physical_memory_get_dirty-is-used-as-retu.patch
# For bz#997559 - Improve live migration bitmap handling
Patch786: kvm-memory-s-mask-clear-cpu_physical_memory_mask_dirty_r.patch
# For bz#997559 - Improve live migration bitmap handling
Patch787: kvm-memory-use-find_next_bit-to-find-dirty-bits.patch
# For bz#997559 - Improve live migration bitmap handling
Patch788: kvm-memory-cpu_physical_memory_set_dirty_range-now-uses-.patch
# For bz#997559 - Improve live migration bitmap handling
Patch789: kvm-memory-cpu_physical_memory_clear_dirty_range-now-use.patch
# For bz#997559 - Improve live migration bitmap handling
Patch790: kvm-memory-s-dirty-clean-in-cpu_physical_memory_is_dirty.patch
# For bz#997559 - Improve live migration bitmap handling
Patch791: kvm-memory-make-cpu_physical_memory_reset_dirty-take-a-l.patch
# For bz#997559 - Improve live migration bitmap handling
Patch792: kvm-exec-Remove-unused-global-variable-phys_ram_fd.patch
# For bz#997559 - Improve live migration bitmap handling
Patch793: kvm-memory-cpu_physical_memory_set_dirty_tracking-should.patch
# For bz#997559 - Improve live migration bitmap handling
Patch794: kvm-memory-move-private-types-to-exec.c.patch
# For bz#997559 - Improve live migration bitmap handling
Patch795: kvm-memory-split-cpu_physical_memory_-functions-to-its-o.patch
# For bz#997559 - Improve live migration bitmap handling
Patch796: kvm-memory-unfold-memory_region_test_and_clear.patch
# For bz#997559 - Improve live migration bitmap handling
Patch797: kvm-use-directly-cpu_physical_memory_-api-for-tracki.patch
# For bz#997559 - Improve live migration bitmap handling
Patch798: kvm-refactor-start-address-calculation.patch
# For bz#997559 - Improve live migration bitmap handling
Patch799: kvm-memory-move-bitmap-synchronization-to-its-own-functi.patch
# For bz#997559 - Improve live migration bitmap handling
Patch800: kvm-memory-syncronize-kvm-bitmap-using-bitmaps-operation.patch
# For bz#997559 - Improve live migration bitmap handling
Patch801: kvm-ram-split-function-that-synchronizes-a-range.patch
# For bz#997559 - Improve live migration bitmap handling
Patch802: kvm-migration-synchronize-memory-bitmap-64bits-at-a-time.patch
# For bz#947785 - In rhel6.4 guest  sound recorder doesn't work when  playing audio
Patch803: kvm-intel-hda-fix-position-buffer.patch
# For bz#1003467 - Backport migration fixes from post qemu 1.6
Patch804: kvm-The-calculation-of-bytes_xfer-in-qemu_put_buffer-is-.patch
# For bz#1003467 - Backport migration fixes from post qemu 1.6
Patch805: kvm-migration-Fix-rate-limit.patch
# For bz#1017636 - PATCH: fix qemu using 50% host cpu when audio is playing
Patch806: kvm-audio-honor-QEMU_AUDIO_TIMER_PERIOD-instead-of-wakin.patch
# For bz#1017636 - PATCH: fix qemu using 50% host cpu when audio is playing
Patch807: kvm-audio-Lower-default-wakeup-rate-to-100-times-second.patch
# For bz#1017636 - PATCH: fix qemu using 50% host cpu when audio is playing
Patch808: kvm-audio-adjust-pulse-to-100Hz-wakeup-rate.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch809: kvm-pc-Fix-rhel6.-3dnow-3dnowext-compat-bits.patch
# For bz#1038603 - make seabios 256k for rhel7 machine types
Patch810: kvm-add-firmware-to-machine-options.patch
# For bz#1038603 - make seabios 256k for rhel7 machine types
Patch811: kvm-switch-rhel7-machine-types-to-big-bios.patch
# For bz#1034518 - boot order wrong with q35
Patch812: kvm-pci-fix-pci-bridge-fw-path.patch
# For bz#1031098 - Disable device smbus-eeprom
Patch813: kvm-hw-cannot_instantiate_with_device_add_yet-due-to-poi.patch
# For bz#1031098 - Disable device smbus-eeprom
Patch814: kvm-qdev-Document-that-pointer-properties-kill-device_ad.patch
# For bz#1044742 - Cannot create guest on remote RHEL7 host using F20 virt-manager, libvirt's qemu -no-hpet detection is broken
Patch815: kvm-Add-back-no-hpet-but-ignore-it.patch
# For bz#669524 - Confusing error message from -device <unknown dev>
Patch816: kvm-Revert-qdev-monitor-Fix-crash-when-device_add-is-cal.patch
# For bz#669524 - Confusing error message from -device <unknown dev>
Patch817: kvm-Revert-qdev-Do-not-let-the-user-try-to-device_add-wh.patch
# For bz#669524 - Confusing error message from -device <unknown dev>
Patch818: kvm-qdev-monitor-Clean-up-qdev_device_add-variable-namin.patch
# For bz#669524 - Confusing error message from -device <unknown dev>
Patch819: kvm-qdev-monitor-Fix-crash-when-device_add-is-called.2.patch.patch
# For bz#669524 - Confusing error message from -device <unknown dev>
Patch820: kvm-qdev-monitor-Avoid-qdev-as-variable-name.patch
# For bz#669524 - Confusing error message from -device <unknown dev>
Patch821: kvm-qdev-monitor-Inline-qdev_init-for-device_add.patch
# For bz#669524 - Confusing error message from -device <unknown dev>
Patch822: kvm-qdev-Do-not-let-the-user-try-to-device_add-when-it.2.patch.patch
# For bz#669524 - Confusing error message from -device <unknown dev>
Patch823: kvm-qdev-monitor-Avoid-device_add-crashing-on-non-device.patch
# For bz#669524 - Confusing error message from -device <unknown dev>
Patch824: kvm-qdev-monitor-Improve-error-message-for-device-nonexi.patch
# For bz#1003535 - qemu-kvm core dump when boot vm with more than 32 virtio disks/nics
Patch825: kvm-exec-change-well-known-physical-sections-to-macros.patch
# For bz#1003535 - qemu-kvm core dump when boot vm with more than 32 virtio disks/nics
Patch826: kvm-exec-separate-sections-and-nodes-per-address-space.patch
# For bz#1053699 - Backport Cancelled race condition fixes
Patch827: kvm-avoid-a-bogus-COMPLETED-CANCELLED-transition.patch
# For bz#1053699 - Backport Cancelled race condition fixes
Patch828: kvm-introduce-MIG_STATE_CANCELLING-state.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch829: kvm-vvfat-use-bdrv_new-to-allocate-BlockDriverState.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch830: kvm-block-implement-reference-count-for-BlockDriverState.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch831: kvm-block-make-bdrv_delete-static.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch832: kvm-migration-omit-drive-ref-as-we-have-bdrv_ref-now.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch833: kvm-xen_disk-simplify-blk_disconnect-with-refcnt.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch834: kvm-nbd-use-BlockDriverState-refcnt.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch835: kvm-block-use-BDS-ref-for-block-jobs.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch836: kvm-block-Make-BlockJobTypes-const.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch837: kvm-blockjob-rename-BlockJobType-to-BlockJobDriver.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch838: kvm-qapi-Introduce-enum-BlockJobType.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch839: kvm-qapi-make-use-of-new-BlockJobType.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch840: kvm-mirror-Don-t-close-target.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch841: kvm-mirror-Move-base-to-MirrorBlockJob.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch842: kvm-block-Add-commit_active_start.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch843: kvm-commit-Support-commit-active-layer.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch844: kvm-qemu-iotests-prefill-some-data-to-test-image.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch845: kvm-qemu-iotests-Update-test-cases-for-commit-active.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch846: kvm-commit-Remove-unused-check.patch
# For bz#921890 - Core dump when block mirror with "sync" is "none" and mode is "absolute-paths"
Patch847: kvm-blockdev-use-bdrv_getlength-in-qmp_drive_mirror.patch
# For bz#921890 - Core dump when block mirror with "sync" is "none" and mode is "absolute-paths"
Patch848: kvm-qemu-iotests-make-assert_no_active_block_jobs-common.patch
# For bz#921890 - Core dump when block mirror with "sync" is "none" and mode is "absolute-paths"
Patch849: kvm-block-drive-mirror-Check-for-NULL-backing_hd.patch
# For bz#921890 - Core dump when block mirror with "sync" is "none" and mode is "absolute-paths"
Patch850: kvm-qemu-iotests-Extend-041-for-unbacked-mirroring.patch
# For bz#921890 - Core dump when block mirror with "sync" is "none" and mode is "absolute-paths"
Patch851: kvm-qapi-schema-Update-description-for-NewImageMode.patch
# For bz#921890 - Core dump when block mirror with "sync" is "none" and mode is "absolute-paths"
Patch852: kvm-block-drive-mirror-Reuse-backing-HD-for-sync-none.patch
# For bz#921890 - Core dump when block mirror with "sync" is "none" and mode is "absolute-paths"
Patch853: kvm-qemu-iotests-Fix-test-041.patch
# For bz#1035644 - rhel7.0host + windows guest + virtio-win + 'chkdsk' in the guest gives qemu assertion in scsi_dma_complete
Patch854: kvm-scsi-bus-fix-transfer-length-and-direction-for-VERIF.patch
# For bz#1035644 - rhel7.0host + windows guest + virtio-win + 'chkdsk' in the guest gives qemu assertion in scsi_dma_complete
Patch855: kvm-scsi-disk-fix-VERIFY-emulation.patch
# For bz#1041301 - live snapshot merge (commit) of the active layer
Patch856: kvm-block-ensure-bdrv_drain_all-works-during-bdrv_delete.patch
# For bz#998708 - qemu-kvm: maximum vcpu should be recommended maximum
Patch857: kvm-use-recommended-max-vcpu-count.patch
# For bz#1049706 - MIss CPUID_EXT_X2APIC in Westmere cpu model
Patch858: kvm-pc-Create-pc_compat_rhel-functions.patch
# For bz#1049706 - MIss CPUID_EXT_X2APIC in Westmere cpu model
Patch859: kvm-pc-Enable-x2apic-by-default-on-more-recent-CPU-model.patch
# For bz#1019221 - Iscsi miss id sub-option in help output
Patch860: kvm-help-add-id-suboption-to-iscsi.patch
# For bz#1037503 - fix thin provisioning support for block device backends
Patch861: kvm-scsi-disk-add-UNMAP-limits-to-block-limits-VPD-page.patch
# For bz#1034876 - export acpi tables to guests
Patch862: kvm-qdev-Fix-32-bit-compilation-in-print_size.patch
# For bz#1034876 - export acpi tables to guests
Patch863: kvm-qdev-Use-clz-in-print_size.patch
# For bz#1026548 - i386: pc: align gpa<->hpa on 1GB boundary
Patch864: kvm-piix-gigabyte-alignment-for-ram.patch
# For bz#1026548 - i386: pc: align gpa<->hpa on 1GB boundary
Patch865: kvm-pc_piix-document-gigabyte_align.patch
# For bz#1026548 - i386: pc: align gpa<->hpa on 1GB boundary
Patch866: kvm-q35-gigabyle-alignment-for-ram.patch
# For bz#983344 - QEMU core dump and host will reboot when do hot-unplug a virtio-blk disk which use  the switch behind switch
Patch867: kvm-virtio-bus-remove-vdev-field.patch
# For bz#983344 - QEMU core dump and host will reboot when do hot-unplug a virtio-blk disk which use  the switch behind switch
Patch868: kvm-virtio-pci-remove-vdev-field.patch
# For bz#983344 - QEMU core dump and host will reboot when do hot-unplug a virtio-blk disk which use  the switch behind switch
Patch869: kvm-virtio-bus-cleanup-plug-unplug-interface.patch
# For bz#983344 - QEMU core dump and host will reboot when do hot-unplug a virtio-blk disk which use  the switch behind switch
Patch870: kvm-virtio-blk-switch-exit-callback-to-VirtioDeviceClass.patch
# For bz#983344 - QEMU core dump and host will reboot when do hot-unplug a virtio-blk disk which use  the switch behind switch
Patch871: kvm-virtio-serial-switch-exit-callback-to-VirtioDeviceCl.patch
# For bz#983344 - QEMU core dump and host will reboot when do hot-unplug a virtio-blk disk which use  the switch behind switch
Patch872: kvm-virtio-net-switch-exit-callback-to-VirtioDeviceClass.patch
# For bz#983344 - QEMU core dump and host will reboot when do hot-unplug a virtio-blk disk which use  the switch behind switch
Patch873: kvm-virtio-scsi-switch-exit-callback-to-VirtioDeviceClas.patch
# For bz#983344 - QEMU core dump and host will reboot when do hot-unplug a virtio-blk disk which use  the switch behind switch
Patch874: kvm-virtio-balloon-switch-exit-callback-to-VirtioDeviceC.patch
# For bz#983344 - QEMU core dump and host will reboot when do hot-unplug a virtio-blk disk which use  the switch behind switch
Patch875: kvm-virtio-rng-switch-exit-callback-to-VirtioDeviceClass.patch
# For bz#983344 - QEMU core dump and host will reboot when do hot-unplug a virtio-blk disk which use  the switch behind switch
Patch876: kvm-virtio-pci-add-device_unplugged-callback.patch
# For bz#1051438 - Error message contains garbled characters when unable to open image due to bad permissions (permission denied).
Patch877: kvm-block-use-correct-filename-for-error-report.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch878: kvm-Partially-revert-rhel-Drop-cfi.pflash01-and-isa-ide-.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch879: kvm-Revert-pc-Disable-the-use-flash-device-for-BIOS-unle.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch880: kvm-memory-Replace-open-coded-memory_region_is_romd.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch881: kvm-memory-Rename-readable-flag-to-romd_mode.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch882: kvm-isapc-Fix-non-KVM-qemu-boot-read-write-memory-for-is.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch883: kvm-add-kvm_readonly_mem_enabled.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch884: kvm-support-using-KVM_MEM_READONLY-flag-for-regions.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch885: kvm-pc_sysfw-allow-flash-pflash-memory-to-be-used-with-K.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch886: kvm-fix-double-free-the-memslot-in-kvm_set_phys_mem.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch887: kvm-sysfw-remove-read-only-pc_sysfw_flash_vs_rom_bug_com.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch888: kvm-pc_sysfw-remove-the-rom_only-property.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch889: kvm-pc_sysfw-do-not-make-it-a-device-anymore.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch890: kvm-hw-i386-pc_sysfw-support-two-flash-drives.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch891: kvm-i440fx-test-qtest_start-should-be-paired-with-qtest_.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch892: kvm-i440fx-test-give-each-GTest-case-its-own-qtest.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch893: kvm-i440fx-test-generate-temporary-firmware-blob.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch894: kvm-i440fx-test-verify-firmware-under-4G-and-1M-both-bio.patch
# For bz#1032346 - basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables)
Patch895: kvm-piix-fix-32bit-pci-hole.patch
# For bz#1041564 - [NFR] qemu: Returning the watermark for all the images opened for writing
Patch896: kvm-qapi-Add-backing-to-BlockStats.patch
# For bz#918907 - provide backwards-compatible RHEL specific machine types in QEMU - CPU features
Patch897: kvm-pc-Disable-RDTSCP-unconditionally-on-rhel6.-machine-.patch
# For bz#1056428 - "rdtscp" flag defined on Opteron_G5 model and cann't be exposed to guest
# For bz#874400 - "rdtscp" flag defined on Opteron_G5 model and cann't be exposed to guest
Patch898: kvm-pc-Disable-RDTSCP-on-AMD-CPU-models.patch
# For bz#1030301 - qemu-img can not merge live snapshot to backing file(r/w backing file via libiscsi)
Patch899: kvm-block-add-.bdrv_reopen_prepare-stub-for-iscsi.patch


BuildRequires: zlib-devel
BuildRequires: SDL-devel
BuildRequires: which
BuildRequires: texi2html
BuildRequires: gnutls-devel
BuildRequires: cyrus-sasl-devel
BuildRequires: libtool
BuildRequires: libaio-devel
BuildRequires: rsync
BuildRequires: python
BuildRequires: pciutils-devel
BuildRequires: pulseaudio-libs-devel
BuildRequires: libiscsi-devel
BuildRequires: ncurses-devel
BuildRequires: libattr-devel
BuildRequires: libusbx-devel
%if 0%{?have_usbredir:1}
BuildRequires: usbredir-devel >= 0.6
%endif
BuildRequires: texinfo
%if 0%{!?build_only_sub:1}
    %if 0%{?have_spice:1}
BuildRequires: spice-protocol >= 0.12.2
BuildRequires: spice-server-devel >= 0.12.0
    %endif
%endif
%if 0%{?have_seccomp:1}
BuildRequires: libseccomp-devel >= 1.0.0
%endif
# For network block driver
BuildRequires: libcurl-devel
%if 0%{!?build_only_sub:1}
# For gluster block driver
BuildRequires: glusterfs-api-devel
BuildRequires: glusterfs-devel
%endif
# We need both because the 'stap' binary is probed for by configure
BuildRequires: systemtap
BuildRequires: systemtap-sdt-devel
# For smartcard NSS support
BuildRequires: nss-devel
# For XFS discard support in raw-posix.c
# For VNC JPEG support
BuildRequires: libjpeg-devel
# For VNC PNG support
BuildRequires: libpng-devel
# For uuid generation
BuildRequires: libuuid-devel
# For BlueZ device support
BuildRequires: bluez-libs-devel
# For Braille device support
BuildRequires: brlapi-devel
# For test suite
BuildRequires: check-devel
# For virtfs
BuildRequires: libcap-devel
# Hard requirement for version >= 1.3
BuildRequires: pixman-devel
# Documentation requirement
BuildRequires: perl-podlators
BuildRequires: texinfo
# For rdma
%if 0%{?have_librdma:1}
BuildRequires: librdmacm-devel
%endif
# iasl and cpp for acpi generation (not a hard requirement as we can use
# pre-compiled files, but it's better to use this)
%ifarch %{ix86} x86_64
BuildRequires: iasl
BuildRequires: cpp
%endif

%if 0%{!?build_only_sub:1}
Requires: qemu-img = %{epoch}:%{version}-%{release}
%endif

# RHEV-specific changes:
# We provide special suffix for qemu-kvm so the conflit is easy
# In addition, RHEV version should obsolete all RHEL version in case both
# RHEL and RHEV channels are used
%rhel_rhev_conflicts qemu-kvm


%define qemudocdir %{_docdir}/%{pkgname}

%description
qemu-kvm is an open source virtualizer that provides hardware emulation for
the KVM hypervisor. qemu-kvm acts as a virtual machine monitor together with
the KVM kernel modules, and emulates the hardware for a full system such as
a PC and its assocated peripherals.

As qemu-kvm requires no host kernel patches to run, it is safe and easy to use.

%package -n qemu-img%{?pkgsuffix}
Summary: QEMU command line tool for manipulating disk images
Group: Development/Tools

%rhel_rhev_conflicts qemu-img

%description -n qemu-img%{?pkgsuffix}
This package provides a command line tool for manipulating disk images.

%if 0%{!?build_only_sub:1}
%package -n qemu-kvm-common%{?pkgsuffix}
Summary: QEMU common files needed by all QEMU targets
Group: Development/Tools
Requires(post): /usr/bin/getent
Requires(post): /usr/sbin/groupadd
Requires(post): /usr/sbin/useradd
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%rhel_rhev_conflicts qemu-kvm-common

%description -n qemu-kvm-common%{?pkgsuffix}
qemu-kvm is an open source virtualizer that provides hardware emulation for
the KVM hypervisor. 

This package provides documentation and auxiliary programs used with qemu-kvm.

%endif

%if %{with guest_agent}
%package -n qemu-guest-agent
Summary: QEMU guest agent
Group: System Environment/Daemons
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description -n qemu-guest-agent
qemu-kvm is an open source virtualizer that provides hardware emulation for
the KVM hypervisor. 

This package provides an agent to run inside guests, which communicates
with the host over a virtio-serial channel named "org.qemu.guest_agent.0"

This package does not need to be installed on the host OS.

%post -n qemu-guest-agent
%systemd_post qemu-guest-agent.service

%preun -n qemu-guest-agent
%systemd_preun qemu-guest-agent.service

%postun -n qemu-guest-agent
%systemd_postun_with_restart qemu-guest-agent.service

%endif

%if 0%{!?build_only_sub:1}
%package -n qemu-kvm-tools%{?pkgsuffix}
Summary: KVM debugging and diagnostics tools
Group: Development/Tools

%rhel_rhev_conflicts qemu-kvm-tools

%description -n qemu-kvm-tools%{?pkgsuffix}
This package contains some diagnostics and debugging tools for KVM,
such as kvm_stat.
%endif

%package -n libcacard%{?pkgsuffix}
Summary:        Common Access Card (CAC) Emulation
Group:          Development/Libraries

%rhel_rhev_conflicts libcacard

%description -n libcacard%{?pkgsuffix}
Common Access Card (CAC) emulation library.

%package -n libcacard-tools%{?pkgsuffix}
Summary:        CAC Emulation tools
Group:          Development/Libraries
Requires:       libcacard = %{epoch}:%{version}-%{release}
# older qemu-img has vscclient which is now in libcacard-tools
Requires:       qemu-img >= 3:1.3.0-5

%rhel_rhev_conflicts libcacard-tools

%description -n libcacard-tools%{?pkgsuffix}
CAC emulation tools.

%package -n libcacard-devel%{?pkgsuffix}
Summary:        CAC Emulation devel
Group:          Development/Libraries
Requires:       libcacard = %{epoch}:%{version}-%{release}

%rhel_rhev_conflicts libcacard-devel

%description -n libcacard-devel%{?pkgsuffix}
CAC emulation development files.

%prep
%setup -q -n qemu-%{version}
cp %{SOURCE18} pc-bios # keep "make check" happy
%patch1 -p1
#%%patch2 -p1
#%%patch3 -p1
#%%patch4 -p1
#%%patch5 -p1
#%%patch6 -p1
#%%patch7 -p1
#%%patch8 -p1
#%%patch9 -p1
#%%patch10 -p1
#%%patch11 -p1
#%%patch12 -p1
#%%patch13 -p1
#%%patch14 -p1
#%%patch15 -p1
#%%patch16 -p1
#%%patch17 -p1
#%%patch18 -p1
#%%patch19 -p1
#%%patch20 -p1
#%%patch21 -p1
#%%patch22 -p1
#%%patch23 -p1
#%%patch24 -p1
#%%patch25 -p1
#%%patch26 -p1
#%%patch27 -p1
#%%patch28 -p1
%patch29 -p1
%patch30 -p1
%patch31 -p1
%patch32 -p1
%patch33 -p1
%patch34 -p1
%patch35 -p1
%patch36 -p1
%patch37 -p1

# Fix CPUID model/level values on Conroe/Penryn/Nehalem CPU models
%patch38 -p1
%patch39 -p1
%patch40 -p1

#%patch41 -p1
%patch42 -p1
%patch43 -p1
%patch44 -p1
%patch45 -p1
%patch46 -p1
%patch47 -p1
%patch48 -p1
%patch49 -p1
%patch50 -p1
%patch51 -p1
%patch52 -p1
%patch53 -p1
%patch54 -p1
%patch55 -p1
%patch56 -p1
%patch57 -p1
%patch58 -p1
%patch59 -p1
%patch60 -p1
%patch61 -p1
#%%patch62 -p1
%patch63 -p1
%patch64 -p1
%patch65 -p1
%patch66 -p1
%patch67 -p1
%patch68 -p1
%patch69 -p1
%patch70 -p1
%patch71 -p1
%patch72 -p1
#%%patch73 -p1
%patch74 -p1
%patch75 -p1

%patch76 -p1
%patch77 -p1
%patch78 -p1
%patch79 -p1
%patch80 -p1
%patch81 -p1
%patch82 -p1
%patch83 -p1
%patch84 -p1
%patch85 -p1
%patch86 -p1
%patch87 -p1
%patch88 -p1
%patch89 -p1
#%%patch90 -p1
#%%patch91 -p1
#%%patch92 -p1
%patch93 -p1
%patch94 -p1
#%%patch95 -p1
%patch96 -p1
%patch97 -p1
%patch98 -p1
%patch99 -p1
%patch100 -p1
%patch101 -p1
%patch102 -p1
%patch103 -p1
%patch104 -p1
%patch105 -p1
%patch106 -p1
%patch107 -p1
%patch108 -p1
%patch109 -p1
%patch110 -p1
%patch111 -p1
%patch112 -p1
%patch113 -p1
%patch114 -p1
%patch115 -p1
%patch116 -p1
%patch117 -p1
%patch118 -p1
%patch119 -p1
%patch120 -p1
%patch121 -p1
%patch122 -p1
%patch123 -p1
%patch124 -p1
%patch125 -p1
%patch126 -p1
%patch127 -p1
%patch128 -p1
%patch129 -p1
%patch130 -p1
%patch131 -p1
%patch132 -p1
%patch133 -p1
%patch134 -p1
%patch135 -p1
%patch136 -p1
%patch137 -p1
%patch138 -p1
%patch139 -p1
%patch140 -p1
%patch141 -p1
%patch142 -p1
%patch143 -p1
%patch144 -p1
%patch145 -p1
%patch146 -p1
%patch147 -p1
%patch148 -p1
%patch149 -p1
%patch150 -p1
%patch151 -p1
%patch152 -p1
%patch153 -p1
%patch154 -p1
%patch155 -p1
%patch156 -p1
%patch157 -p1
%patch158 -p1
%patch159 -p1
%patch160 -p1
%patch161 -p1
%patch162 -p1
%patch163 -p1
%patch164 -p1
%patch165 -p1
%patch166 -p1
%patch168 -p1
%patch169 -p1
%patch170 -p1
%patch171 -p1
%patch172 -p1
%patch173 -p1
%patch174 -p1
%patch175 -p1
%patch176 -p1
%patch177 -p1
%patch178 -p1
%patch179 -p1
%patch180 -p1
%patch181 -p1
%patch182 -p1
%patch183 -p1
%patch184 -p1
%patch185 -p1
%patch186 -p1
%patch187 -p1
%patch188 -p1
%patch189 -p1
%patch190 -p1
%patch191 -p1
%patch192 -p1
%patch193 -p1
%patch194 -p1
%patch195 -p1
%patch196 -p1
%patch197 -p1
%patch198 -p1
%patch199 -p1
%patch200 -p1
%patch201 -p1
%patch202 -p1
%patch203 -p1
%patch204 -p1
%patch205 -p1
%patch206 -p1
%patch207 -p1
%patch208 -p1
%patch209 -p1
%patch210 -p1
%patch211 -p1
%patch212 -p1
%patch213 -p1
%patch214 -p1
%patch215 -p1
%patch216 -p1
%patch217 -p1
%patch218 -p1
%patch219 -p1
%patch220 -p1
%patch221 -p1
%patch222 -p1
%patch223 -p1
%patch224 -p1
%patch225 -p1
%patch226 -p1
%patch227 -p1
%patch228 -p1
%patch229 -p1
%patch230 -p1
%patch231 -p1
%patch232 -p1
%patch233 -p1
%patch234 -p1
%patch235 -p1
%patch236 -p1
%patch237 -p1
%patch238 -p1
%patch239 -p1
%patch240 -p1
%patch241 -p1
%patch242 -p1
%patch243 -p1
%patch244 -p1
%patch245 -p1
%patch246 -p1
%patch247 -p1
%patch248 -p1
%patch249 -p1
%patch250 -p1
%patch251 -p1
%patch252 -p1
%patch253 -p1
%patch254 -p1
%patch255 -p1
%patch256 -p1
%patch257 -p1
%patch258 -p1
%patch259 -p1
%patch260 -p1
%patch261 -p1
%patch262 -p1
%patch263 -p1
%patch264 -p1
%patch265 -p1
%patch266 -p1
%patch267 -p1
%patch268 -p1
%patch269 -p1
%patch270 -p1
%patch271 -p1
%patch272 -p1
%patch273 -p1
%patch274 -p1
%patch275 -p1
%patch276 -p1
%patch277 -p1
%patch278 -p1
%patch279 -p1
%patch280 -p1
%patch281 -p1
%patch282 -p1
%patch283 -p1
%patch284 -p1
%patch285 -p1
%patch286 -p1
%patch287 -p1
%patch288 -p1
%patch289 -p1
%patch290 -p1
%patch291 -p1
%patch292 -p1
%patch293 -p1
%patch294 -p1
%patch295 -p1
%patch296 -p1
%patch297 -p1
%patch298 -p1
%patch299 -p1
%patch300 -p1
%patch301 -p1
%patch302 -p1
%patch303 -p1
%patch304 -p1
%patch305 -p1
%patch306 -p1
%patch307 -p1
%patch308 -p1
%patch309 -p1
%patch310 -p1
%patch311 -p1
%patch312 -p1
%patch313 -p1
%patch314 -p1
%patch315 -p1
%patch316 -p1
%patch317 -p1
%patch318 -p1
%patch319 -p1
%patch320 -p1
%patch321 -p1
%patch322 -p1
%patch323 -p1
%patch324 -p1
%patch325 -p1
%patch326 -p1
%patch327 -p1
%patch328 -p1
%patch329 -p1
%patch330 -p1
%patch331 -p1
%patch332 -p1
%patch333 -p1
%patch334 -p1
%patch335 -p1
%patch336 -p1
%patch337 -p1
%patch338 -p1
%patch339 -p1
%patch340 -p1
%patch341 -p1
%patch342 -p1
%patch343 -p1
%patch344 -p1
%patch345 -p1
%patch346 -p1
%patch347 -p1
%patch348 -p1
%patch349 -p1
%patch350 -p1
%patch351 -p1
%patch352 -p1
%patch353 -p1
%patch354 -p1
%patch355 -p1
%patch356 -p1
%patch357 -p1
%patch358 -p1
%patch359 -p1
%patch360 -p1
%patch361 -p1
%patch362 -p1
%patch363 -p1
%patch364 -p1
%patch365 -p1
%patch366 -p1
%patch367 -p1
%patch368 -p1
%patch369 -p1
%patch370 -p1
%patch371 -p1
%patch372 -p1
%patch373 -p1
%patch374 -p1
%patch375 -p1
%patch376 -p1
%patch377 -p1
%patch378 -p1
%patch379 -p1
%patch380 -p1
%patch381 -p1
%patch382 -p1
%patch383 -p1
%patch384 -p1
%patch385 -p1
%patch386 -p1
%patch387 -p1
%patch388 -p1
%patch389 -p1
%patch390 -p1
%patch391 -p1
%patch392 -p1
%patch393 -p1
%patch394 -p1
%patch395 -p1
%patch396 -p1
%patch397 -p1
%patch398 -p1
%patch399 -p1
%patch400 -p1
%patch401 -p1
%patch402 -p1
%patch403 -p1
%patch404 -p1
%patch405 -p1
%patch406 -p1
%patch407 -p1
%patch408 -p1
%patch409 -p1
%patch410 -p1
%patch411 -p1
%patch412 -p1
%patch413 -p1
%patch414 -p1
%patch415 -p1
%patch416 -p1
%patch417 -p1
%patch418 -p1
%patch419 -p1
%patch420 -p1
%patch421 -p1
%patch422 -p1
%patch423 -p1
%patch424 -p1
%patch425 -p1
%patch426 -p1
%patch427 -p1
%patch428 -p1
%patch429 -p1
%patch430 -p1
%patch431 -p1
%patch432 -p1
%patch433 -p1
%patch434 -p1
%patch435 -p1
%patch436 -p1
%patch437 -p1
%patch438 -p1
%patch439 -p1
%patch440 -p1
%patch441 -p1
%patch442 -p1
%patch443 -p1
%patch444 -p1
%patch445 -p1
%patch446 -p1
%patch447 -p1
%patch448 -p1
%patch449 -p1
%patch450 -p1
%patch451 -p1
%patch452 -p1
%patch453 -p1
%patch454 -p1
%patch455 -p1
%patch456 -p1
%patch457 -p1
%patch458 -p1
%patch459 -p1
%patch460 -p1
%patch461 -p1
%patch462 -p1
%patch463 -p1
%patch464 -p1
%patch465 -p1
%patch466 -p1
%patch467 -p1
%patch468 -p1
%patch469 -p1
%patch470 -p1
%patch471 -p1
%patch472 -p1
%patch473 -p1
%patch474 -p1
%patch475 -p1
%patch476 -p1
%patch477 -p1
%patch478 -p1
%patch479 -p1
%patch480 -p1
%patch481 -p1
#%patch482 -p1
%patch483 -p1
%patch484 -p1
%patch485 -p1
%patch486 -p1
%patch487 -p1
%patch488 -p1
%patch489 -p1
%patch490 -p1
%patch491 -p1
%patch492 -p1
%patch493 -p1
%patch494 -p1
%patch495 -p1
%patch496 -p1
%patch497 -p1
%patch498 -p1
%patch499 -p1
%patch500 -p1
%patch501 -p1
%patch502 -p1
%patch503 -p1
%patch504 -p1
%patch505 -p1
%patch506 -p1
%patch507 -p1
%patch508 -p1
%patch509 -p1
%patch510 -p1
%patch511 -p1
%patch512 -p1
%patch513 -p1
%patch514 -p1
%patch515 -p1
%patch516 -p1
%patch517 -p1
%patch518 -p1
%patch519 -p1
%patch520 -p1
%patch521 -p1
%patch522 -p1
%patch523 -p1
%patch524 -p1
%patch525 -p1
%patch526 -p1
%patch527 -p1
%patch528 -p1
%patch529 -p1
%patch530 -p1
%patch531 -p1
%patch532 -p1
%patch533 -p1
%patch534 -p1
%patch535 -p1
%patch536 -p1
%patch537 -p1
%patch538 -p1
%patch539 -p1
%patch540 -p1
%patch541 -p1
%patch542 -p1
%patch543 -p1
%patch544 -p1
%patch545 -p1
%patch546 -p1
%patch547 -p1
%patch548 -p1
%patch549 -p1
%patch550 -p1
%patch551 -p1
%patch552 -p1
%patch553 -p1
%patch554 -p1
%patch555 -p1
%patch556 -p1
%patch557 -p1
%patch558 -p1
%patch559 -p1
%patch560 -p1
%patch561 -p1
%patch562 -p1
%patch563 -p1
%patch564 -p1
%patch565 -p1
%patch566 -p1
%patch567 -p1
%patch568 -p1
%patch569 -p1
%patch570 -p1
%patch571 -p1
%patch572 -p1
%patch573 -p1
%patch574 -p1
%patch575 -p1
%patch576 -p1
%patch577 -p1
%patch578 -p1
%patch579 -p1
%patch580 -p1
%patch581 -p1
%patch582 -p1
%patch583 -p1
%patch584 -p1
%patch585 -p1
%patch586 -p1
%patch587 -p1
%patch588 -p1
%patch589 -p1
%patch590 -p1
%patch591 -p1
%patch592 -p1
%patch593 -p1
%patch594 -p1
%patch595 -p1
%patch596 -p1
%patch597 -p1
%patch598 -p1
%patch599 -p1
%patch600 -p1
%patch601 -p1
%patch602 -p1
%patch603 -p1
%patch604 -p1
%patch605 -p1
%patch606 -p1
%patch607 -p1
%patch608 -p1
%patch609 -p1
%patch610 -p1
%patch611 -p1
%patch612 -p1
%patch613 -p1
%patch614 -p1
%patch615 -p1
%patch616 -p1
%patch617 -p1
%patch618 -p1
%patch619 -p1
%patch620 -p1
%patch621 -p1
%patch622 -p1
%patch623 -p1
%patch624 -p1
%patch625 -p1
%patch626 -p1
%patch627 -p1
%patch628 -p1
%patch629 -p1
%patch630 -p1
%patch631 -p1
%patch632 -p1
%patch633 -p1
%patch634 -p1
%patch635 -p1
%patch636 -p1
%patch637 -p1
%patch638 -p1
%patch639 -p1
%patch640 -p1
%patch641 -p1
%patch642 -p1
%patch643 -p1
%patch644 -p1
%patch645 -p1
%patch646 -p1
%patch647 -p1
%patch648 -p1
%patch649 -p1
%patch650 -p1
%patch651 -p1
%patch652 -p1
%patch653 -p1
%patch654 -p1
%patch655 -p1
%patch656 -p1
%patch657 -p1
%patch658 -p1
%patch659 -p1
%patch660 -p1
%patch661 -p1
%patch662 -p1
%patch663 -p1
%patch664 -p1
%patch665 -p1
%patch666 -p1
%patch667 -p1
%patch668 -p1
%patch669 -p1
%patch670 -p1
%patch671 -p1
%patch672 -p1
%patch673 -p1
%patch674 -p1
%patch675 -p1
%patch676 -p1
%patch677 -p1
%patch678 -p1
%patch679 -p1
%patch680 -p1
%patch681 -p1
%patch682 -p1
%patch683 -p1
%patch684 -p1
%patch685 -p1
%patch686 -p1
%patch687 -p1
%patch688 -p1
%patch689 -p1
%patch690 -p1
%patch691 -p1
%patch692 -p1
%patch693 -p1
%patch694 -p1
%patch695 -p1
%patch696 -p1
%patch697 -p1
%patch698 -p1
%patch699 -p1
%patch700 -p1
%patch701 -p1
%patch702 -p1
%patch703 -p1
%patch704 -p1
%patch705 -p1
%patch706 -p1
%patch707 -p1
%patch708 -p1
%patch709 -p1
%patch710 -p1
%patch711 -p1
%patch712 -p1
%patch713 -p1
%patch714 -p1
%patch715 -p1
%patch716 -p1
%patch717 -p1
%patch718 -p1
%patch719 -p1
%patch720 -p1
%patch721 -p1
%patch722 -p1
%patch723 -p1
%patch724 -p1
%patch725 -p1
%patch726 -p1
%patch727 -p1
%patch728 -p1
%patch729 -p1
%patch730 -p1
%patch731 -p1
%patch732 -p1
%patch733 -p1
%patch734 -p1
%patch735 -p1
%patch736 -p1
%patch737 -p1
%patch738 -p1
%patch739 -p1
%patch740 -p1
%patch741 -p1
%patch742 -p1
%patch743 -p1
%patch744 -p1
%patch745 -p1
%patch746 -p1
%patch747 -p1
%patch748 -p1
%patch749 -p1
%patch750 -p1
%patch751 -p1
%patch752 -p1
%patch753 -p1
%patch754 -p1
%patch755 -p1
%patch756 -p1
%patch757 -p1
%patch758 -p1
%patch759 -p1
%patch760 -p1
%patch761 -p1
%patch762 -p1
%patch763 -p1
%patch764 -p1
%patch765 -p1
%patch766 -p1
%patch767 -p1
%patch768 -p1
%patch769 -p1
%patch770 -p1
%patch771 -p1
%patch772 -p1
%patch773 -p1
%patch774 -p1
%patch775 -p1
%patch776 -p1
%patch777 -p1
%patch778 -p1
%patch779 -p1
%patch780 -p1
%patch781 -p1
%patch782 -p1
%patch783 -p1
%patch784 -p1
%patch785 -p1
%patch786 -p1
%patch787 -p1
%patch788 -p1
%patch789 -p1
%patch790 -p1
%patch791 -p1
%patch792 -p1
%patch793 -p1
%patch794 -p1
%patch795 -p1
%patch796 -p1
%patch797 -p1
%patch798 -p1
%patch799 -p1
%patch800 -p1
%patch801 -p1
%patch802 -p1
%patch803 -p1
%patch804 -p1
%patch805 -p1
%patch806 -p1
%patch807 -p1
%patch808 -p1
%patch809 -p1
%patch810 -p1
%patch811 -p1
%patch812 -p1
%patch813 -p1
%patch814 -p1
%patch815 -p1
%patch816 -p1
%patch817 -p1
%patch818 -p1
%patch819 -p1
%patch820 -p1
%patch821 -p1
%patch822 -p1
%patch823 -p1
%patch824 -p1
%patch825 -p1
%patch826 -p1
%patch827 -p1
%patch828 -p1
%patch829 -p1
%patch830 -p1
%patch831 -p1
%patch832 -p1
%patch833 -p1
%patch834 -p1
%patch835 -p1
%patch836 -p1
%patch837 -p1
%patch838 -p1
%patch839 -p1
%patch840 -p1
%patch841 -p1
%patch842 -p1
%patch843 -p1
%patch844 -p1
%patch845 -p1
%patch846 -p1
%patch847 -p1
%patch848 -p1
%patch849 -p1
%patch850 -p1
%patch851 -p1
%patch852 -p1
%patch853 -p1
%patch854 -p1
%patch855 -p1
%patch856 -p1
%patch857 -p1
%patch858 -p1
%patch859 -p1
%patch860 -p1
%patch861 -p1
%patch862 -p1
%patch863 -p1
%patch864 -p1
%patch865 -p1
%patch866 -p1
%patch867 -p1
%patch868 -p1
%patch869 -p1
%patch870 -p1
%patch871 -p1
%patch872 -p1
%patch873 -p1
%patch874 -p1
%patch875 -p1
%patch876 -p1
%patch877 -p1
%patch878 -p1
%patch879 -p1
%patch880 -p1
%patch881 -p1
%patch882 -p1
%patch883 -p1
%patch884 -p1
%patch885 -p1
%patch886 -p1
%patch887 -p1
%patch888 -p1
%patch889 -p1
%patch890 -p1
%patch891 -p1
%patch892 -p1
%patch893 -p1
%patch894 -p1
%patch895 -p1
%patch896 -p1
%patch897 -p1
%patch898 -p1
%patch899 -p1

%build
buildarch="%{kvm_target}-softmmu"

# --build-id option is used for giving info to the debug packages.
extraldflags="-Wl,--build-id";
buildldflags="VL_LDFLAGS=-Wl,--build-id"

%ifarch s390
    # drop -g flag to prevent memory exhaustion by linker
    %global optflags %(echo %{optflags} | sed 's/-g//')
    sed -i.debug 's/"-g $CFLAGS"/"$CFLAGS"/g' configure
%endif

dobuild() {
%if 0%{!?build_only_sub:1}
    ./configure \
        --prefix=%{_prefix} \
        --libdir=%{_libdir} \
        --sysconfdir=%{_sysconfdir} \
        --interp-prefix=%{_prefix}/qemu-%%M \
        --audio-drv-list=pa,alsa \
        --with-confsuffix=/%{pkgname} \
        --localstatedir=%{_localstatedir} \
        --libexecdir=%{_libexecdir} \
        --with-pkgversion=%{pkgname}-%{version}-%{release} \
        --disable-strip \
        --extra-ldflags="$extraldflags -pie -Wl,-z,relro -Wl,-z,now" \
        --extra-cflags="%{optflags} -fPIE -DPIE" \
        --enable-trace-backend=dtrace \
        --enable-werror \
        --disable-xen \
        --disable-virtfs \
        --enable-kvm \
        --enable-libusb \
        --enable-spice \
        --enable-seccomp \
        --disable-fdt \
        --enable-docs \
        --disable-sdl \
        --disable-debug-tcg \
        --disable-sparse \
        --disable-brlapi \
        --disable-bluez \
        --disable-vde \
        --disable-curses \
        --disable-curl \
        --enable-vnc-tls \
        --enable-vnc-sasl \
        --enable-linux-aio \
        --enable-smartcard-nss \
        --enable-usb-redir \
        --enable-vnc-png \
        --disable-vnc-jpeg \
        --enable-vnc-ws \
        --enable-uuid \
        --disable-vhost-scsi \
%if %{with guest_agent}
        --enable-guest-agent \
%else
        --disable-guest-agent \
%endif
%if %{rhev}
        --enable-live-block-ops \
        --enable-ceph-support \
%else
        --disable-live-block-ops \
        --disable-ceph-support \
%endif
        --disable-live-block-migration \
        --enable-glusterfs \
%if %{rhev}
        --block-drv-rw-whitelist=qcow2,raw,file,host_device,nbd,iscsi,gluster,rbd \
%else
        --block-drv-rw-whitelist=qcow2,raw,file,host_device,nbd,iscsi,gluster \
%endif
        --block-drv-ro-whitelist=vmdk,vhdx,vpc \
        "$@"

    echo "config-host.mak contents:"
    echo "==="
    cat config-host.mak
    echo "==="

    make V=1 %{?_smp_mflags} $buildldflags
%else
   ./configure --prefix=%{_prefix} \
               --libdir=%{_libdir} \
               --with-pkgversion=%{pkgname}-%{version}-%{release} \
               --disable-guest-agent \
               --target-list= --cpu=%{_arch}

   make libcacard.la %{?_smp_mflags} $buildldflags
   make vscclient %{?_smp_mflags} $buildldflags
   make qemu-img %{?_smp_mflags} $buildldflags
   make qemu-io %{?_smp_mflags} $buildldflags
   make qemu-nbd %{?_smp_mflags} $buildldflags
   make qemu-img.1 %{?_smp_mflags} $buildldflags
   make qemu-nbd.8 %{?_smp_mflags} $buildldflags
   make qemu-ga %{?_smp_mflags} $buildldflags
%endif
}

dobuild --target-list="$buildarch"

%if 0%{!?build_only_sub:1}
        # Setup back compat qemu-kvm binary
        ./scripts/tracetool.py --backend dtrace --format stap \
          --binary %{_libexecdir}/qemu-kvm --target-arch %{kvm_target} \
          --target-type system --probe-prefix \
          qemu.kvm < ./trace-events > qemu-kvm.stp

        cp -a %{kvm_target}-softmmu/qemu-system-%{kvm_target} qemu-kvm


    gcc %{SOURCE6} -O2 -g -o ksmctl
%endif

%install
%define _udevdir %(pkg-config --variable=udevdir udev)/rules.d

%if 0%{!?build_only_sub:1}
    install -D -p -m 0644 %{SOURCE4} $RPM_BUILD_ROOT%{_unitdir}/ksm.service
    install -D -p -m 0644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/ksm
    install -D -p -m 0755 ksmctl $RPM_BUILD_ROOT%{_libexecdir}/ksmctl

    install -D -p -m 0644 %{SOURCE7} $RPM_BUILD_ROOT%{_unitdir}/ksmtuned.service
    install -D -p -m 0755 %{SOURCE8} $RPM_BUILD_ROOT%{_sbindir}/ksmtuned
    install -D -p -m 0644 %{SOURCE9} $RPM_BUILD_ROOT%{_sysconfdir}/ksmtuned.conf

    mkdir -p $RPM_BUILD_ROOT%{_bindir}/
    mkdir -p $RPM_BUILD_ROOT%{_udevdir}

    install -m 0755 scripts/kvm/kvm_stat $RPM_BUILD_ROOT%{_bindir}/
    install -m 0644 %{SOURCE3} $RPM_BUILD_ROOT%{_udevdir}

    make DESTDIR=$RPM_BUILD_ROOT \
        sharedir="%{_datadir}/%{pkgname}" \
        datadir="%{_datadir}/%{pkgname}" \
        install

    mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{pkgname}
    mkdir -p $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset

    # Install compatibility roms
    install %{SOURCE14} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    install %{SOURCE15} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    install %{SOURCE16} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/
    install %{SOURCE17} $RPM_BUILD_ROOT%{_datadir}/%{pkgname}/

    install -m 0755 qemu-kvm $RPM_BUILD_ROOT%{_libexecdir}/
    install -m 0644 qemu-kvm.stp $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/

    rm $RPM_BUILD_ROOT%{_bindir}/qemu-system-%{kvm_target}
    rm $RPM_BUILD_ROOT%{_datadir}/systemtap/tapset/qemu-system-%{kvm_target}.stp

    mkdir -p $RPM_BUILD_ROOT%{qemudocdir}
    install -p -m 0644 -t ${RPM_BUILD_ROOT}%{qemudocdir} Changelog README COPYING COPYING.LIB LICENSE
    mv ${RPM_BUILD_ROOT}%{_docdir}/qemu/qemu-doc.html $RPM_BUILD_ROOT%{qemudocdir}
    mv ${RPM_BUILD_ROOT}%{_docdir}/qemu/qemu-tech.html $RPM_BUILD_ROOT%{qemudocdir}
    mv ${RPM_BUILD_ROOT}%{_docdir}/qemu/qmp-commands.txt $RPM_BUILD_ROOT%{qemudocdir}
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man1/*
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man8/*

    install -D -p -m 0644 qemu.sasl $RPM_BUILD_ROOT%{_sysconfdir}/sasl2/qemu-kvm.conf

    # Provided by package openbios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/openbios-ppc
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/openbios-sparc32
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/openbios-sparc64
    # Provided by package SLOF
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/slof.bin

    # Remove unpackaged files.
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/palcode-clipper
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/petalogix*.dtb
    rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/bamboo.dtb
    rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/ppc_rom.bin
    rm -f ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/spapr-rtas.bin
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/s390-zipl.rom
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/s390-ccw.img

    # Remove efi roms
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/efi*.rom

    # Provided by package ipxe
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/pxe*rom
    # Provided by package vgabios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/vgabios*bin
    # Provided by package seabios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/bios*.bin
    # Provided by package sgabios
    rm -rf ${RPM_BUILD_ROOT}%{_datadir}/%{pkgname}/sgabios.bin

    # the pxe gpxe images will be symlinks to the images on
    # /usr/share/ipxe, as QEMU doesn't know how to look
    # for other paths, yet.
    pxe_link() {
        ln -s ../ipxe/$2.rom %{buildroot}%{_datadir}/%{pkgname}/pxe-$1.rom
    }

    pxe_link e1000 8086100e
    pxe_link ne2k_pci 10ec8029
    pxe_link pcnet 10222000
    pxe_link rtl8139 10ec8139
    pxe_link virtio 1af41000

    rom_link() {
        ln -s $1 %{buildroot}%{_datadir}/%{pkgname}/$2
    }

    rom_link ../seavgabios/vgabios-isavga.bin vgabios.bin
    rom_link ../seavgabios/vgabios-cirrus.bin vgabios-cirrus.bin
    rom_link ../seavgabios/vgabios-qxl.bin vgabios-qxl.bin
    rom_link ../seavgabios/vgabios-stdvga.bin vgabios-stdvga.bin
    rom_link ../seavgabios/vgabios-vmware.bin vgabios-vmware.bin
    rom_link ../seabios/bios.bin bios.bin
    rom_link ../seabios/bios-256k.bin bios-256k.bin
    rom_link ../sgabios/sgabios.bin sgabios.bin
%endif

%if %{with guest_agent}
    # For the qemu-guest-agent subpackage, install:
    # - the systemd service file and the udev rules:
    mkdir -p $RPM_BUILD_ROOT%{_unitdir}
    mkdir -p $RPM_BUILD_ROOT%{_udevdir}
    install -m 0644 %{SOURCE10} $RPM_BUILD_ROOT%{_unitdir}
    install -m 0644 %{SOURCE11} $RPM_BUILD_ROOT%{_udevdir}

    # - the environment file for the systemd service:
    install -D -p -m 0644 %{SOURCE13} \
      $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/qemu-ga

    # - the fsfreeze hook script:
    install -D --preserve-timestamps \
      scripts/qemu-guest-agent/fsfreeze-hook \
      $RPM_BUILD_ROOT%{_sysconfdir}/qemu-ga/fsfreeze-hook

    # - the directory for user scripts:
    mkdir $RPM_BUILD_ROOT%{_sysconfdir}/qemu-ga/fsfreeze-hook.d

    # - and the fsfreeze script samples:
    mkdir --parents $RPM_BUILD_ROOT%{_datadir}/%{name}/qemu-ga/fsfreeze-hook.d/
    install --preserve-timestamps --mode=0644 \
      scripts/qemu-guest-agent/fsfreeze-hook.d/*.sample \
      $RPM_BUILD_ROOT%{_datadir}/%{name}/qemu-ga/fsfreeze-hook.d/

    # - Install dedicated log directory:
    mkdir -p -v $RPM_BUILD_ROOT%{_localstatedir}/log/qemu-ga/
%endif

%if 0%{!?build_only_sub:1}
    # Install rules to use the bridge helper with libvirt's virbr0
    install -m 0644 %{SOURCE12} $RPM_BUILD_ROOT%{_sysconfdir}/%{pkgname}
%endif

make %{?_smp_mflags} $buildldflags DESTDIR=$RPM_BUILD_ROOT install-libcacard
find $RPM_BUILD_ROOT -name "libcacard.so*" -exec chmod +x \{\} \;

find $RPM_BUILD_ROOT -name '*.la' -or -name '*.a' | xargs rm -f

%if 0%{?build_only_sub}
    mkdir -p $RPM_BUILD_ROOT%{_bindir}
    mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1/*
    mkdir -p $RPM_BUILD_ROOT%{_mandir}/man8/*
    libtool --mode=install install -m 0755 vscclient $RPM_BUILD_ROOT%{_bindir}/vscclient
    install -m 0755 qemu-img $RPM_BUILD_ROOT%{_bindir}/qemu-img
    install -m 0755 qemu-io $RPM_BUILD_ROOT%{_bindir}/qemu-io
    install -m 0755 qemu-nbd $RPM_BUILD_ROOT%{_bindir}/qemu-nbd
    install -c -m 0644 qemu-img.1 ${RPM_BUILD_ROOT}%{_mandir}/man1/qemu-img.1
    install -c -m 0644 qemu-nbd.8 ${RPM_BUILD_ROOT}%{_mandir}/man8/qemu-nbd.8
    install -c -m 0755  qemu-ga ${RPM_BUILD_ROOT}%{_bindir}/qemu-ga
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man1/*
    chmod -x ${RPM_BUILD_ROOT}%{_mandir}/man8/*
%endif


%if 0%{!?build_only_sub:1}
%check
    make check
%endif
%post
# load kvm modules now, so we can make sure no reboot is needed.
# If there's already a kvm module installed, we don't mess with it
sh %{_sysconfdir}/sysconfig/modules/kvm.modules &> /dev/null || :
    udevadm trigger --subsystem-match=misc --sysname-match=kvm --action=add || :

%if 0%{!?build_only_sub:1}
%post -n qemu-kvm-common%{?pkgsuffix}
    %systemd_post ksm.service
    %systemd_post ksmtuned.service

    getent group kvm >/dev/null || groupadd -g 36 -r kvm
    getent group qemu >/dev/null || groupadd -g 107 -r qemu
    getent passwd qemu >/dev/null || \
       useradd -r -u 107 -g qemu -G kvm -d / -s /sbin/nologin \
       -c "qemu user" qemu

%preun -n qemu-kvm-common%{?pkgsuffix}
    %systemd_preun ksm.service
    %systemd_preun ksmtuned.service

%postun -n qemu-kvm-common%{?pkgsuffix}
    %systemd_postun_with_restart ksm.service
    %systemd_postun_with_restart ksmtuned.service
%endif

%global kvm_files \
%{_udevdir}/80-kvm.rules

%global qemu_kvm_files \
%{_libexecdir}/qemu-kvm \
%{_datadir}/systemtap/tapset/qemu-kvm.stp

%if 0%{!?build_only_sub:1}
%files -n qemu-kvm-common%{?pkgsuffix}
    %defattr(-,root,root)
    %dir %{qemudocdir}
    %doc %{qemudocdir}/Changelog
    %doc %{qemudocdir}/README
    %doc %{qemudocdir}/qemu-doc.html
    %doc %{qemudocdir}/qemu-tech.html
    %doc %{qemudocdir}/qmp-commands.txt
    %doc %{qemudocdir}/COPYING
    %doc %{qemudocdir}/COPYING.LIB
    %doc %{qemudocdir}/LICENSE
    %dir %{_datadir}/%{pkgname}/
    %{_datadir}/%{pkgname}/keymaps/
    %{_mandir}/man1/%{pkgname}.1*
    %attr(4755, -, -) %{_libexecdir}/qemu-bridge-helper
    %config(noreplace) %{_sysconfdir}/sasl2/%{pkgname}.conf
    %{_unitdir}/ksm.service
    %{_libexecdir}/ksmctl
    %config(noreplace) %{_sysconfdir}/sysconfig/ksm
    %{_unitdir}/ksmtuned.service
    %{_sbindir}/ksmtuned
    %config(noreplace) %{_sysconfdir}/ksmtuned.conf
    %dir %{_sysconfdir}/%{pkgname}
    %config(noreplace) %{_sysconfdir}/%{pkgname}/bridge.conf
%endif

%if %{with guest_agent}
%files -n qemu-guest-agent
    %defattr(-,root,root,-)
    %doc COPYING README
    %{_bindir}/qemu-ga
    %{_unitdir}/qemu-guest-agent.service
    %{_udevdir}/99-qemu-guest-agent.rules
    %{_sysconfdir}/sysconfig/qemu-ga
    %{_sysconfdir}/qemu-ga
    %{_datadir}/%{name}/qemu-ga
    %dir %{_localstatedir}/log/qemu-ga
%endif

%if 0%{!?build_only_sub:1}
%files
    %defattr(-,root,root)
    %{_datadir}/%{pkgname}/acpi-dsdt.aml
    %{_datadir}/%{pkgname}/q35-acpi-dsdt.aml
    %{_datadir}/%{pkgname}/bios.bin
    %{_datadir}/%{pkgname}/bios-256k.bin
    %{_datadir}/%{pkgname}/sgabios.bin
    %{_datadir}/%{pkgname}/linuxboot.bin
    %{_datadir}/%{pkgname}/multiboot.bin
    %{_datadir}/%{pkgname}/kvmvapic.bin
    %{_datadir}/%{pkgname}/vgabios.bin
    %{_datadir}/%{pkgname}/vgabios-cirrus.bin
    %{_datadir}/%{pkgname}/vgabios-qxl.bin
    %{_datadir}/%{pkgname}/vgabios-stdvga.bin
    %{_datadir}/%{pkgname}/vgabios-vmware.bin
    %{_datadir}/%{pkgname}/pxe-e1000.rom
    %{_datadir}/%{pkgname}/pxe-virtio.rom
    %{_datadir}/%{pkgname}/pxe-pcnet.rom
    %{_datadir}/%{pkgname}/pxe-rtl8139.rom
    %{_datadir}/%{pkgname}/pxe-ne2k_pci.rom
    %{_datadir}/%{pkgname}/qemu-icon.bmp
    %{_datadir}/%{pkgname}/rhel6-virtio.rom
    %{_datadir}/%{pkgname}/rhel6-pcnet.rom
    %{_datadir}/%{pkgname}/rhel6-rtl8139.rom
    %{_datadir}/%{pkgname}/rhel6-ne2k_pci.rom
    %config(noreplace) %{_sysconfdir}/%{pkgname}/target-x86_64.conf
    %{?kvm_files:}
    %{?qemu_kvm_files:}

%files -n qemu-kvm-tools%{?pkgsuffix}
    %defattr(-,root,root,-)
    %{_bindir}/kvm_stat
%endif

%files -n qemu-img%{?pkgsuffix}
%defattr(-,root,root)
%{_bindir}/qemu-img
%{_bindir}/qemu-io
%{_bindir}/qemu-nbd
%{_mandir}/man1/qemu-img.1*
%{_mandir}/man8/qemu-nbd.8*

%files -n libcacard%{?pkgsuffix}
%defattr(-,root,root,-)
%{_libdir}/libcacard.so.*

%files -n libcacard-tools%{?pkgsuffix}
%defattr(-,root,root,-)
%{_bindir}/vscclient

%files -n libcacard-devel%{?pkgsuffix}
%defattr(-,root,root,-)
%{_includedir}/cacard
%{_libdir}/libcacard.so
%{_libdir}/pkgconfig/libcacard.pc

%changelog
* Wed Jan 29 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-44.el7
- kvm-Partially-revert-rhel-Drop-cfi.pflash01-and-isa-ide-.patch [bz#1032346]
- kvm-Revert-pc-Disable-the-use-flash-device-for-BIOS-unle.patch [bz#1032346]
- kvm-memory-Replace-open-coded-memory_region_is_romd.patch [bz#1032346]
- kvm-memory-Rename-readable-flag-to-romd_mode.patch [bz#1032346]
- kvm-isapc-Fix-non-KVM-qemu-boot-read-write-memory-for-is.patch [bz#1032346]
- kvm-add-kvm_readonly_mem_enabled.patch [bz#1032346]
- kvm-support-using-KVM_MEM_READONLY-flag-for-regions.patch [bz#1032346]
- kvm-pc_sysfw-allow-flash-pflash-memory-to-be-used-with-K.patch [bz#1032346]
- kvm-fix-double-free-the-memslot-in-kvm_set_phys_mem.patch [bz#1032346]
- kvm-sysfw-remove-read-only-pc_sysfw_flash_vs_rom_bug_com.patch [bz#1032346]
- kvm-pc_sysfw-remove-the-rom_only-property.patch [bz#1032346]
- kvm-pc_sysfw-do-not-make-it-a-device-anymore.patch [bz#1032346]
- kvm-hw-i386-pc_sysfw-support-two-flash-drives.patch [bz#1032346]
- kvm-i440fx-test-qtest_start-should-be-paired-with-qtest_.patch [bz#1032346]
- kvm-i440fx-test-give-each-GTest-case-its-own-qtest.patch [bz#1032346]
- kvm-i440fx-test-generate-temporary-firmware-blob.patch [bz#1032346]
- kvm-i440fx-test-verify-firmware-under-4G-and-1M-both-bio.patch [bz#1032346]
- kvm-piix-fix-32bit-pci-hole.patch [bz#1032346]
- kvm-qapi-Add-backing-to-BlockStats.patch [bz#1041564]
- kvm-pc-Disable-RDTSCP-unconditionally-on-rhel6.-machine-.patch [bz#918907]
- kvm-pc-Disable-RDTSCP-on-AMD-CPU-models.patch [bz#1056428 bz#874400]
- kvm-block-add-.bdrv_reopen_prepare-stub-for-iscsi.patch [bz#1030301]
- Resolves: bz#1030301
  (qemu-img can not merge live snapshot to backing file(r/w backing file via libiscsi))
- Resolves: bz#1032346
  (basic OVMF support (non-volatile UEFI variables in flash, and fixup for ACPI tables))
- Resolves: bz#1041564
  ([NFR] qemu: Returning the watermark for all the images opened for writing)
- Resolves: bz#1056428
  ("rdtscp" flag defined on Opteron_G5 model and cann't be exposed to guest)
- Resolves: bz#874400
  ("rdtscp" flag defined on Opteron_G5 model and cann't be exposed to guest)
- Resolves: bz#918907
  (provide backwards-compatible RHEL specific machine types in QEMU - CPU features)

* Mon Jan 27 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-43.el7
- kvm-piix-gigabyte-alignment-for-ram.patch [bz#1026548]
- kvm-pc_piix-document-gigabyte_align.patch [bz#1026548]
- kvm-q35-gigabyle-alignment-for-ram.patch [bz#1026548]
- kvm-virtio-bus-remove-vdev-field.patch [bz#983344]
- kvm-virtio-pci-remove-vdev-field.patch [bz#983344]
- kvm-virtio-bus-cleanup-plug-unplug-interface.patch [bz#983344]
- kvm-virtio-blk-switch-exit-callback-to-VirtioDeviceClass.patch [bz#983344]
- kvm-virtio-serial-switch-exit-callback-to-VirtioDeviceCl.patch [bz#983344]
- kvm-virtio-net-switch-exit-callback-to-VirtioDeviceClass.patch [bz#983344]
- kvm-virtio-scsi-switch-exit-callback-to-VirtioDeviceClas.patch [bz#983344]
- kvm-virtio-balloon-switch-exit-callback-to-VirtioDeviceC.patch [bz#983344]
- kvm-virtio-rng-switch-exit-callback-to-VirtioDeviceClass.patch [bz#983344]
- kvm-virtio-pci-add-device_unplugged-callback.patch [bz#983344]
- kvm-block-use-correct-filename-for-error-report.patch [bz#1051438]
- Resolves: bz#1026548
  (i386: pc: align gpa<->hpa on 1GB boundary)
- Resolves: bz#1051438
  (Error message contains garbled characters when unable to open image due to bad permissions (permission denied).)
- Resolves: bz#983344
  (QEMU core dump and host will reboot when do hot-unplug a virtio-blk disk which use  the switch behind switch)

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 10:1.5.3-42
- Mass rebuild 2014-01-24

* Wed Jan 22 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-41.el7
- kvm-help-add-id-suboption-to-iscsi.patch [bz#1019221]
- kvm-scsi-disk-add-UNMAP-limits-to-block-limits-VPD-page.patch [bz#1037503]
- kvm-qdev-Fix-32-bit-compilation-in-print_size.patch [bz#1034876]
- kvm-qdev-Use-clz-in-print_size.patch [bz#1034876]
- Resolves: bz#1019221
  (Iscsi miss id sub-option in help output)
- Resolves: bz#1034876
  (export acpi tables to guests)
- Resolves: bz#1037503
  (fix thin provisioning support for block device backends)

* Wed Jan 22 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-40.el7
- kvm-avoid-a-bogus-COMPLETED-CANCELLED-transition.patch [bz#1053699]
- kvm-introduce-MIG_STATE_CANCELLING-state.patch [bz#1053699]
- kvm-vvfat-use-bdrv_new-to-allocate-BlockDriverState.patch [bz#1041301]
- kvm-block-implement-reference-count-for-BlockDriverState.patch [bz#1041301]
- kvm-block-make-bdrv_delete-static.patch [bz#1041301]
- kvm-migration-omit-drive-ref-as-we-have-bdrv_ref-now.patch [bz#1041301]
- kvm-xen_disk-simplify-blk_disconnect-with-refcnt.patch [bz#1041301]
- kvm-nbd-use-BlockDriverState-refcnt.patch [bz#1041301]
- kvm-block-use-BDS-ref-for-block-jobs.patch [bz#1041301]
- kvm-block-Make-BlockJobTypes-const.patch [bz#1041301]
- kvm-blockjob-rename-BlockJobType-to-BlockJobDriver.patch [bz#1041301]
- kvm-qapi-Introduce-enum-BlockJobType.patch [bz#1041301]
- kvm-qapi-make-use-of-new-BlockJobType.patch [bz#1041301]
- kvm-mirror-Don-t-close-target.patch [bz#1041301]
- kvm-mirror-Move-base-to-MirrorBlockJob.patch [bz#1041301]
- kvm-block-Add-commit_active_start.patch [bz#1041301]
- kvm-commit-Support-commit-active-layer.patch [bz#1041301]
- kvm-qemu-iotests-prefill-some-data-to-test-image.patch [bz#1041301]
- kvm-qemu-iotests-Update-test-cases-for-commit-active.patch [bz#1041301]
- kvm-commit-Remove-unused-check.patch [bz#1041301]
- kvm-blockdev-use-bdrv_getlength-in-qmp_drive_mirror.patch [bz#921890]
- kvm-qemu-iotests-make-assert_no_active_block_jobs-common.patch [bz#921890]
- kvm-block-drive-mirror-Check-for-NULL-backing_hd.patch [bz#921890]
- kvm-qemu-iotests-Extend-041-for-unbacked-mirroring.patch [bz#921890]
- kvm-qapi-schema-Update-description-for-NewImageMode.patch [bz#921890]
- kvm-block-drive-mirror-Reuse-backing-HD-for-sync-none.patch [bz#921890]
- kvm-qemu-iotests-Fix-test-041.patch [bz#921890]
- kvm-scsi-bus-fix-transfer-length-and-direction-for-VERIF.patch [bz#1035644]
- kvm-scsi-disk-fix-VERIFY-emulation.patch [bz#1035644]
- kvm-block-ensure-bdrv_drain_all-works-during-bdrv_delete.patch [bz#1041301]
- kvm-use-recommended-max-vcpu-count.patch [bz#998708]
- kvm-pc-Create-pc_compat_rhel-functions.patch [bz#1049706]
- kvm-pc-Enable-x2apic-by-default-on-more-recent-CPU-model.patch [bz#1049706]
- kvm-Build-all-subpackages-for-RHEV.patch [bz#1007204]
- Resolves: bz#1007204
  (qemu-img-rhev  qemu-kvm-rhev-tools are not built for qemu-kvm-1.5.3-3.el7)
- Resolves: bz#1035644
  (rhel7.0host + windows guest + virtio-win + 'chkdsk' in the guest gives qemu assertion in scsi_dma_complete)
- Resolves: bz#1041301
  (live snapshot merge (commit) of the active layer)
- Resolves: bz#1049706
  (MIss CPUID_EXT_X2APIC in Westmere cpu model)
- Resolves: bz#1053699
  (Backport Cancelled race condition fixes)
- Resolves: bz#921890
  (Core dump when block mirror with "sync" is "none" and mode is "absolute-paths")
- Resolves: bz#998708
  (qemu-kvm: maximum vcpu should be recommended maximum)

* Tue Jan 21 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-39.el7
- kvm-Revert-qdev-monitor-Fix-crash-when-device_add-is-cal.patch [bz#669524]
- kvm-Revert-qdev-Do-not-let-the-user-try-to-device_add-wh.patch [bz#669524]
- kvm-qdev-monitor-Clean-up-qdev_device_add-variable-namin.patch [bz#669524]
- kvm-qdev-monitor-Fix-crash-when-device_add-is-called.2.patch.patch [bz#669524]
- kvm-qdev-monitor-Avoid-qdev-as-variable-name.patch [bz#669524]
- kvm-qdev-monitor-Inline-qdev_init-for-device_add.patch [bz#669524]
- kvm-qdev-Do-not-let-the-user-try-to-device_add-when-it.2.patch.patch [bz#669524]
- kvm-qdev-monitor-Avoid-device_add-crashing-on-non-device.patch [bz#669524]
- kvm-qdev-monitor-Improve-error-message-for-device-nonexi.patch [bz#669524]
- kvm-exec-change-well-known-physical-sections-to-macros.patch [bz#1003535]
- kvm-exec-separate-sections-and-nodes-per-address-space.patch [bz#1003535]
- Resolves: bz#1003535
  (qemu-kvm core dump when boot vm with more than 32 virtio disks/nics)
- Resolves: bz#669524
  (Confusing error message from -device <unknown dev>)

* Fri Jan 17 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-38.el7
- kvm-intel-hda-fix-position-buffer.patch [bz#947785]
- kvm-The-calculation-of-bytes_xfer-in-qemu_put_buffer-is-.patch [bz#1003467]
- kvm-migration-Fix-rate-limit.patch [bz#1003467]
- kvm-audio-honor-QEMU_AUDIO_TIMER_PERIOD-instead-of-wakin.patch [bz#1017636]
- kvm-audio-Lower-default-wakeup-rate-to-100-times-second.patch [bz#1017636]
- kvm-audio-adjust-pulse-to-100Hz-wakeup-rate.patch [bz#1017636]
- kvm-pc-Fix-rhel6.-3dnow-3dnowext-compat-bits.patch [bz#918907]
- kvm-add-firmware-to-machine-options.patch [bz#1038603]
- kvm-switch-rhel7-machine-types-to-big-bios.patch [bz#1038603]
- kvm-add-bios-256k.bin-from-seabios-bin-1.7.2.2-10.el7.no.patch [bz#1038603]
- kvm-pci-fix-pci-bridge-fw-path.patch [bz#1034518]
- kvm-hw-cannot_instantiate_with_device_add_yet-due-to-poi.patch [bz#1031098]
- kvm-qdev-Document-that-pointer-properties-kill-device_ad.patch [bz#1031098]
- kvm-Add-back-no-hpet-but-ignore-it.patch [bz#1044742]
- Resolves: bz#1003467
  (Backport migration fixes from post qemu 1.6)
- Resolves: bz#1017636
  (PATCH: fix qemu using 50% host cpu when audio is playing)
- Resolves: bz#1031098
  (Disable device smbus-eeprom)
- Resolves: bz#1034518
  (boot order wrong with q35)
- Resolves: bz#1038603
  (make seabios 256k for rhel7 machine types)
- Resolves: bz#1044742
  (Cannot create guest on remote RHEL7 host using F20 virt-manager, libvirt's qemu -no-hpet detection is broken)
- Resolves: bz#918907
  (provide backwards-compatible RHEL specific machine types in QEMU - CPU features)
- Resolves: bz#947785
  (In rhel6.4 guest  sound recorder doesn't work when  playing audio)

* Wed Jan 15 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-37.el7
- kvm-bitmap-use-long-as-index.patch [bz#997559]
- kvm-memory-cpu_physical_memory_set_dirty_flags-result-is.patch [bz#997559]
- kvm-memory-cpu_physical_memory_set_dirty_range-return-vo.patch [bz#997559]
- kvm-exec-use-accessor-function-to-know-if-memory-is-dirt.patch [bz#997559]
- kvm-memory-create-function-to-set-a-single-dirty-bit.patch [bz#997559]
- kvm-exec-drop-useless-if.patch [bz#997559]
- kvm-exec-create-function-to-get-a-single-dirty-bit.patch [bz#997559]
- kvm-memory-make-cpu_physical_memory_is_dirty-return-bool.patch [bz#997559]
- kvm-memory-all-users-of-cpu_physical_memory_get_dirty-us.patch [bz#997559]
- kvm-memory-set-single-dirty-flags-when-possible.patch [bz#997559]
- kvm-memory-cpu_physical_memory_set_dirty_range-always-di.patch [bz#997559]
- kvm-memory-cpu_physical_memory_mask_dirty_range-always-c.patch [bz#997559]
- kvm-memory-use-bit-2-for-migration.patch [bz#997559]
- kvm-memory-make-sure-that-client-is-always-inside-range.patch [bz#997559]
- kvm-memory-only-resize-dirty-bitmap-when-memory-size-inc.patch [bz#997559]
- kvm-memory-cpu_physical_memory_clear_dirty_flag-result-i.patch [bz#997559]
- kvm-bitmap-Add-bitmap_zero_extend-operation.patch [bz#997559]
- kvm-memory-split-dirty-bitmap-into-three.patch [bz#997559]
- kvm-memory-unfold-cpu_physical_memory_clear_dirty_flag-i.patch [bz#997559]
- kvm-memory-unfold-cpu_physical_memory_set_dirty-in-its-o.patch [bz#997559]
- kvm-memory-unfold-cpu_physical_memory_set_dirty_flag.patch [bz#997559]
- kvm-memory-make-cpu_physical_memory_get_dirty-the-main-f.patch [bz#997559]
- kvm-memory-cpu_physical_memory_get_dirty-is-used-as-retu.patch [bz#997559]
- kvm-memory-s-mask-clear-cpu_physical_memory_mask_dirty_r.patch [bz#997559]
- kvm-memory-use-find_next_bit-to-find-dirty-bits.patch [bz#997559]
- kvm-memory-cpu_physical_memory_set_dirty_range-now-uses-.patch [bz#997559]
- kvm-memory-cpu_physical_memory_clear_dirty_range-now-use.patch [bz#997559]
- kvm-memory-s-dirty-clean-in-cpu_physical_memory_is_dirty.patch [bz#997559]
- kvm-memory-make-cpu_physical_memory_reset_dirty-take-a-l.patch [bz#997559]
- kvm-exec-Remove-unused-global-variable-phys_ram_fd.patch [bz#997559]
- kvm-memory-cpu_physical_memory_set_dirty_tracking-should.patch [bz#997559]
- kvm-memory-move-private-types-to-exec.c.patch [bz#997559]
- kvm-memory-split-cpu_physical_memory_-functions-to-its-o.patch [bz#997559]
- kvm-memory-unfold-memory_region_test_and_clear.patch [bz#997559]
- kvm-use-directly-cpu_physical_memory_-api-for-tracki.patch [bz#997559]
- kvm-refactor-start-address-calculation.patch [bz#997559]
- kvm-memory-move-bitmap-synchronization-to-its-own-functi.patch [bz#997559]
- kvm-memory-syncronize-kvm-bitmap-using-bitmaps-operation.patch [bz#997559]
- kvm-ram-split-function-that-synchronizes-a-range.patch [bz#997559]
- kvm-migration-synchronize-memory-bitmap-64bits-at-a-time.patch [bz#997559]
- Resolves: bz#997559
  (Improve live migration bitmap handling)

* Tue Jan 14 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-36.el7
- kvm-Add-support-statement-to-help-output.patch [bz#972773]
- kvm-__com.redhat_qxl_screendump-add-docs.patch [bz#903910]
- kvm-vl-Round-memory-sizes-below-2MiB-up-to-2MiB.patch [bz#999836]
- kvm-seccomp-exit-if-seccomp_init-fails.patch [bz#1044845]
- kvm-redhat-qemu-kvm.spec-require-python-for-build.patch [bz#1034876]
- kvm-redhat-qemu-kvm.spec-require-iasl.patch [bz#1034876]
- kvm-configure-make-iasl-option-actually-work.patch [bz#1034876]
- kvm-redhat-qemu-kvm.spec-add-cpp-as-build-dependency.patch [bz#1034876]
- kvm-acpi-build-disable-with-no-acpi.patch [bz#1045386]
- kvm-ehci-implement-port-wakeup.patch [bz#1039513]
- kvm-qdev-monitor-Fix-crash-when-device_add-is-called-wit.patch [bz#1026712 bz#1046007]
- kvm-block-vhdx-improve-error-message-and-.bdrv_check-imp.patch [bz#1035001]
- kvm-docs-updated-qemu-img-man-page-and-qemu-doc-to-refle.patch [bz#1017650]
- kvm-enable-pvticketlocks-by-default.patch [bz#1052340]
- kvm-fix-boot-strict-regressed-in-commit-6ef4716.patch [bz#997817]
- kvm-vl-make-boot_strict-variable-static-not-used-outside.patch [bz#997817]
- Resolves: bz#1017650
  (need to update qemu-img man pages on "VHDX" format)
- Resolves: bz#1026712
  (Qemu core dumpd when boot guest with driver name as "virtio-pci")
- Resolves: bz#1034876
  (export acpi tables to guests)
- Resolves: bz#1035001
  (VHDX: journal log should not be replayed by default, but rather via qemu-img check -r all)
- Resolves: bz#1039513
  (backport remote wakeup for ehci)
- Resolves: bz#1044845
  (QEMU seccomp sandbox - exit if seccomp_init() fails)
- Resolves: bz#1045386
  (qemu-kvm: hw/i386/acpi-build.c:135: acpi_get_pm_info: Assertion `obj' failed.)
- Resolves: bz#1046007
  (qemu-kvm aborted when hot plug PCI device to guest with romfile and rombar=0)
- Resolves: bz#1052340
  (pvticketlocks: default on)
- Resolves: bz#903910
  (RHEL7 does not have equivalent functionality for __com.redhat_qxl_screendump)
- Resolves: bz#972773
  (RHEL7: Clarify support statement in KVM help)
- Resolves: bz#997817
  (-boot order and -boot once regressed since RHEL-6)
- Resolves: bz#999836
  (-m 1 crashes)

* Thu Jan 09 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-35.el7
- kvm-option-Add-assigned-flag-to-QEMUOptionParameter.patch [bz#1033490]
- kvm-qcow2-refcount-Snapshot-update-for-zero-clusters.patch [bz#1033490]
- kvm-qemu-iotests-Snapshotting-zero-clusters.patch [bz#1033490]
- kvm-block-Image-file-option-amendment.patch [bz#1033490]
- kvm-qcow2-cache-Empty-cache.patch [bz#1033490]
- kvm-qcow2-cluster-Expand-zero-clusters.patch [bz#1033490]
- kvm-qcow2-Save-refcount-order-in-BDRVQcowState.patch [bz#1033490]
- kvm-qcow2-Implement-bdrv_amend_options.patch [bz#1033490]
- kvm-qcow2-Correct-bitmap-size-in-zero-expansion.patch [bz#1033490]
- kvm-qcow2-Free-only-newly-allocated-clusters-on-error.patch [bz#1033490]
- kvm-qcow2-Add-missing-space-in-error-message.patch [bz#1033490]
- kvm-qemu-iotest-qcow2-image-option-amendment.patch [bz#1033490]
- kvm-qemu-iotests-New-test-case-in-061.patch [bz#1033490]
- kvm-qemu-iotests-Preallocated-zero-clusters-in-061.patch [bz#1033490]
- Resolves: bz#1033490
  (Cannot upgrade/downgrade qcow2 images)

* Wed Jan 08 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-34.el7
- kvm-block-stream-Don-t-stream-unbacked-devices.patch [bz#965636]
- kvm-qemu-io-Let-open-pass-options-to-block-driver.patch [bz#1004347]
- kvm-qcow2.py-Subcommand-for-changing-header-fields.patch [bz#1004347]
- kvm-qemu-iotests-Remaining-error-propagation-adjustments.patch [bz#1004347]
- kvm-qemu-iotests-Add-test-for-inactive-L2-overlap.patch [bz#1004347]
- kvm-qemu-iotests-Adjust-test-result-039.patch [bz#1004347]
- kvm-virtio-net-don-t-update-mac_table-in-error-state.patch [bz#1048671]
- kvm-qcow2-Zero-initialise-first-cluster-for-new-images.patch [bz#1032904]
- Resolves: bz#1004347
  (Backport qcow2 corruption prevention patches)
- Resolves: bz#1032904
  (qemu-img can not create libiscsi qcow2_v3 image)
- Resolves: bz#1048671
  (virtio-net: mac_table change isn't recovered in error state)
- Resolves: bz#965636
  (streaming with no backing file should not do anything)

* Wed Jan 08 2014 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-33.el7
- kvm-block-qemu-iotests-for-vhdx-read-sample-dynamic-imag.patch [bz#879234]
- kvm-block-qemu-iotests-add-quotes-to-TEST_IMG-usage-io-p.patch [bz#879234]
- kvm-block-qemu-iotests-fix-_make_test_img-to-work-with-s.patch [bz#879234]
- kvm-block-qemu-iotests-add-quotes-to-TEST_IMG.base-usage.patch [bz#879234]
- kvm-block-qemu-iotests-add-quotes-to-TEST_IMG-usage-in-0.patch [bz#879234]
- kvm-block-qemu-iotests-removes-duplicate-double-quotes-i.patch [bz#879234]
- kvm-block-vhdx-minor-comments-and-typo-correction.patch [bz#879234]
- kvm-block-vhdx-add-header-update-capability.patch [bz#879234]
- kvm-block-vhdx-code-movement-VHDXMetadataEntries-and-BDR.patch [bz#879234]
- kvm-block-vhdx-log-support-struct-and-defines.patch [bz#879234]
- kvm-block-vhdx-break-endian-translation-functions-out.patch [bz#879234]
- kvm-block-vhdx-update-log-guid-in-header-and-first-write.patch [bz#879234]
- kvm-block-vhdx-code-movement-move-vhdx_close-above-vhdx_.patch [bz#879234]
- kvm-block-vhdx-log-parsing-replay-and-flush-support.patch [bz#879234]
- kvm-block-vhdx-add-region-overlap-detection-for-image-fi.patch [bz#879234]
- kvm-block-vhdx-add-log-write-support.patch [bz#879234]
- kvm-block-vhdx-write-support.patch [bz#879234]
- kvm-block-vhdx-remove-BAT-file-offset-bit-shifting.patch [bz#879234]
- kvm-block-vhdx-move-more-endian-translations-to-vhdx-end.patch [bz#879234]
- kvm-block-vhdx-break-out-code-operations-to-functions.patch [bz#879234]
- kvm-block-vhdx-fix-comment-typos-in-header-fix-incorrect.patch [bz#879234]
- kvm-block-vhdx-add-.bdrv_create-support.patch [bz#879234]
- kvm-block-vhdx-update-_make_test_img-to-filter-out-vhdx-.patch [bz#879234]
- kvm-block-qemu-iotests-for-vhdx-add-write-test-support.patch [bz#879234]
- kvm-block-vhdx-qemu-iotest-log-replay-of-data-sector.patch [bz#879234]
- Resolves: bz#879234
  ([RFE] qemu-img: Add/improve support for VHDX format)

* Mon Jan 06 2014 Michal Novotny <minovotn@redhat.com> - 1.5.3-32.el7
- kvm-block-change-default-of-.has_zero_init-to-0.patch.patch [bz#1007815]
- kvm-iscsi-factor-out-sector-conversions.patch.patch [bz#1007815]
- kvm-iscsi-add-logical-block-provisioning-information-to-.patch.patch [bz#1007815]
- kvm-iscsi-add-.bdrv_get_block_status.patch.patch.patch [bz#1007815]
- kvm-iscsi-split-discard-requests-in-multiple-parts.patch.patch.patch [bz#1007815]
- kvm-block-make-BdrvRequestFlags-public.patch.patch.patch [bz#1007815]
- kvm-block-add-flags-to-bdrv_-_write_zeroes.patch.patch.patch [bz#1007815]
- kvm-block-introduce-BDRV_REQ_MAY_UNMAP-request-flag.patch.patch.patch [bz#1007815]
- kvm-block-add-logical-block-provisioning-info-to-BlockDr.patch.patch.patch [bz#1007815]
- kvm-block-add-wrappers-for-logical-block-provisioning-in.patch.patch.patch [bz#1007815]
- kvm-block-iscsi-add-.bdrv_get_info.patch.patch [bz#1007815]
- kvm-block-add-BlockLimits-structure-to-BlockDriverState.patch.patch.patch [bz#1007815]
- kvm-block-raw-copy-BlockLimits-on-raw_open.patch.patch.patch [bz#1007815]
- kvm-block-honour-BlockLimits-in-bdrv_co_do_write_zeroes.patch.patch.patch [bz#1007815]
- kvm-block-honour-BlockLimits-in-bdrv_co_discard.patch.patch.patch [bz#1007815]
- kvm-iscsi-set-limits-in-BlockDriverState.patch.patch.patch [bz#1007815]
- kvm-iscsi-simplify-iscsi_co_discard.patch.patch.patch [bz#1007815]
- kvm-iscsi-add-bdrv_co_write_zeroes.patch.patch.patch [bz#1007815]
- kvm-block-introduce-bdrv_make_zero.patch.patch.patch [bz#1007815]
- kvm-block-get_block_status-fix-BDRV_BLOCK_ZERO-for-unall.patch.patch.patch [bz#1007815]
- kvm-qemu-img-add-support-for-fully-allocated-images.patch.patch.patch [bz#1007815]
- kvm-qemu-img-conditionally-zero-out-target-on-convert.patch.patch.patch [bz#1007815]
- kvm-block-generalize-BlockLimits-handling-to-cover-bdrv_.patch.patch.patch [bz#1007815]
- kvm-block-add-flags-to-BlockRequest.patch.patch.patch [bz#1007815]
- kvm-block-add-flags-argument-to-bdrv_co_write_zeroes-tra.patch.patch.patch [bz#1007815]
- kvm-block-add-bdrv_aio_write_zeroes.patch.patch.patch [bz#1007815]
- kvm-block-handle-ENOTSUP-from-discard-in-generic-code.patch.patch.patch [bz#1007815]
- kvm-block-make-bdrv_co_do_write_zeroes-stricter-in-produ.patch.patch.patch [bz#1007815]
- kvm-vpc-vhdx-add-get_info.patch.patch.patch [bz#1007815]
- kvm-block-drivers-add-discard-write_zeroes-properties-to.patch.patch.patch [bz#1007815]
- kvm-block-drivers-expose-requirement-for-write-same-alig.patch.patch.patch [bz#1007815]
- kvm-block-iscsi-remove-.bdrv_has_zero_init.patch.patch.patch [bz#1007815]
- kvm-block-iscsi-updated-copyright.patch.patch.patch [bz#1007815]
- kvm-block-iscsi-check-WRITE-SAME-support-differently-dep.patch.patch.patch [bz#1007815]
- kvm-scsi-disk-catch-write-protection-errors-in-UNMAP.patch.patch.patch [bz#1007815]
- kvm-scsi-disk-reject-ANCHOR-1-for-UNMAP-and-WRITE-SAME-c.patch.patch.patch [bz#1007815]
- kvm-scsi-disk-correctly-implement-WRITE-SAME.patch.patch.patch [bz#1007815]
- kvm-scsi-disk-fix-WRITE-SAME-with-large-non-zero-payload.patch.patch.patch [bz#1007815]
- kvm-raw-posix-implement-write_zeroes-with-MAY_UNMAP-for-.patch.patch.patch.patch [bz#1007815]
- kvm-raw-posix-implement-write_zeroes-with-MAY_UNMAP-for-.patch.patch.patch.patch.patch [bz#1007815]
- kvm-raw-posix-add-support-for-write_zeroes-on-XFS-and-bl.patch.patch [bz#1007815]
- kvm-qemu-iotests-033-is-fast.patch.patch [bz#1007815]
- kvm-qemu-img-add-support-for-skipping-zeroes-in-input-du.patch.patch [bz#1007815]
- kvm-qemu-img-fix-usage-instruction-for-qemu-img-convert.patch.patch [bz#1007815]
- kvm-block-iscsi-set-bdi-cluster_size.patch.patch [bz#1007815]
- kvm-block-add-opt_transfer_length-to-BlockLimits.patch.patch [bz#1039557]
- kvm-block-iscsi-set-bs-bl.opt_transfer_length.patch.patch [bz#1039557]
- kvm-qemu-img-dynamically-adjust-iobuffer-size-during-con.patch.patch [bz#1039557]
- kvm-qemu-img-round-down-request-length-to-an-aligned-sec.patch.patch [bz#1039557]
- kvm-qemu-img-decrease-progress-update-interval-on-conver.patch.patch [bz#1039557]
- Resolves: bz#1007815
  (fix WRITE SAME support)
- Resolves: bz#1039557
  (optimize qemu-img for thin provisioned images)

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 10:1.5.3-31
- Mass rebuild 2013-12-27

* Wed Dec 18 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-30.el7
- kvm-Revert-HMP-Disable-drive_add-for-Red-Hat-Enterprise-2.patch.patch [bz#889051]
- Resolves: bz#889051
  (Commands "__com.redhat_drive_add/del" don' t exist in RHEL7.0)

* Wed Dec 18 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-29.el7
- kvm-QMP-Forward-port-__com.redhat_drive_del-from-RHEL-6.patch [bz#889051]
- kvm-QMP-Forward-port-__com.redhat_drive_add-from-RHEL-6.patch [bz#889051]
- kvm-HMP-Forward-port-__com.redhat_drive_add-from-RHEL-6.patch [bz#889051]
- kvm-QMP-Document-throttling-parameters-of-__com.redhat_d.patch [bz#889051]
- kvm-HMP-Disable-drive_add-for-Red-Hat-Enterprise-Linux.patch [bz#889051]
- Resolves: bz#889051
  (Commands "__com.redhat_drive_add/del" don' t exist in RHEL7.0)

* Wed Dec 18 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-28.el7
- kvm-virtio_pci-fix-level-interrupts-with-irqfd.patch [bz#1035132]
- Resolves: bz#1035132
  (fail to boot and call trace with x-data-plane=on specified for rhel6.5 guest)

* Wed Dec 18 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-27.el7
- Change systemd service location [bz#1025217]
- kvm-vmdk-Allow-read-only-open-of-VMDK-version-3.patch [bz#1007710 bz#1029852]
- Resolves: bz#1007710
  ([RFE] Enable qemu-img to support VMDK version 3)
- Resolves: bz#1025217
  (systemd can't control ksm.service and ksmtuned.service)
- Resolves: bz#1029852
  (qemu-img fails to convert vmdk image with "qemu-img: Could not open 'image.vmdk'")

* Wed Dec 18 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-26.el7
- Add BuildRequires to libRDMAcm-devel for RDMA support [bz#1011720]
- kvm-add-a-header-file-for-atomic-operations.patch [bz#1011720]
- kvm-savevm-Fix-potential-memory-leak.patch [bz#1011720]
- kvm-migration-Fail-migration-on-bdrv_flush_all-error.patch [bz#1011720]
- kvm-rdma-add-documentation.patch [bz#1011720]
- kvm-rdma-introduce-qemu_update_position.patch [bz#1011720]
- kvm-rdma-export-yield_until_fd_readable.patch [bz#1011720]
- kvm-rdma-export-throughput-w-MigrationStats-QMP.patch [bz#1011720]
- kvm-rdma-introduce-qemu_file_mode_is_not_valid.patch [bz#1011720]
- kvm-rdma-introduce-qemu_ram_foreach_block.patch [bz#1011720]
- kvm-rdma-new-QEMUFileOps-hooks.patch [bz#1011720]
- kvm-rdma-introduce-capability-x-rdma-pin-all.patch [bz#1011720]
- kvm-rdma-update-documentation-to-reflect-new-unpin-suppo.patch [bz#1011720]- kvm-rdma-bugfix-ram_control_save_page.patch [bz#1011720]
- kvm-rdma-introduce-ram_handle_compressed.patch [bz#1011720]
- kvm-rdma-core-logic.patch [bz#1011720]
- kvm-rdma-send-pc.ram.patch [bz#1011720]
- kvm-rdma-allow-state-transitions-between-other-states-be.patch [bz#1011720]
- kvm-rdma-introduce-MIG_STATE_NONE-and-change-MIG_STATE_S.patch [bz#1011720]
- kvm-rdma-account-for-the-time-spent-in-MIG_STATE_SETUP-t.patch [bz#1011720]
- kvm-rdma-bugfix-make-IPv6-support-work.patch [bz#1011720]
- kvm-rdma-forgot-to-turn-off-the-debugging-flag.patch [bz#1011720]
- kvm-rdma-correct-newlines-in-error-statements.patch [bz#1011720]
- kvm-rdma-don-t-use-negative-index-to-array.patch [bz#1011720]
- kvm-rdma-qemu_rdma_post_send_control-uses-wrongly-RDMA_W.patch [bz#1011720]
- kvm-rdma-use-DRMA_WRID_READY.patch [bz#1011720]
- kvm-rdma-memory-leak-RDMAContext-host.patch [bz#1011720]
- kvm-rdma-use-resp.len-after-validation-in-qemu_rdma_regi.patch [bz#1011720]
- kvm-rdma-validate-RDMAControlHeader-len.patch [bz#1011720]
- kvm-rdma-check-if-RDMAControlHeader-len-match-transferre.patch [bz#1011720]
- kvm-rdma-proper-getaddrinfo-handling.patch [bz#1011720]
- kvm-rdma-IPv6-over-Ethernet-RoCE-is-broken-in-linux-work.patch [bz#1011720]
- kvm-rdma-remaining-documentation-fixes.patch [bz#1011720]
- kvm-rdma-silly-ipv6-bugfix.patch [bz#1011720]
- kvm-savevm-fix-wrong-initialization-by-ram_control_load_.patch [bz#1011720]
- kvm-arch_init-right-return-for-ram_save_iterate.patch [bz#1011720]
- kvm-rdma-clean-up-of-qemu_rdma_cleanup.patch [bz#1011720]
- kvm-rdma-constify-ram_chunk_-index-start-end.patch [bz#1011720]
- kvm-migration-Fix-debug-print-type.patch [bz#1011720]
- kvm-arch_init-make-is_zero_page-accept-size.patch [bz#1011720]
- kvm-migration-ram_handle_compressed.patch [bz#1011720]
- kvm-migration-fix-spice-migration.patch [bz#1011720]
- kvm-pci-assign-cap-number-of-devices-that-can-be-assigne.patch [bz#678368]
- kvm-vfio-cap-number-of-devices-that-can-be-assigned.patch [bz#678368]
- kvm-Revert-usb-tablet-Don-t-claim-wakeup-capability-for-.patch [bz#1039513]
- kvm-mempath-prefault-pages-manually-v4.patch [bz#1026554]
- Resolves: bz#1011720
  ([HP 7.0 Feat]: Backport RDMA based live guest migration changes from upstream to RHEL7.0 KVM)
- Resolves: bz#1026554
  (qemu: mempath: prefault pages manually)
- Resolves: bz#1039513
  (backport remote wakeup for ehci)
- Resolves: bz#678368
  (RFE: Support more than 8 assigned devices)

* Wed Dec 18 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-25.el7
- kvm-Change-package-description.patch [bz#1017696]
- kvm-seccomp-add-kill-to-the-syscall-whitelist.patch [bz#1026314]
- kvm-json-parser-fix-handling-of-large-whole-number-value.patch [bz#997915]
- kvm-qapi-add-QMP-input-test-for-large-integers.patch [bz#997915]
- kvm-qapi-fix-visitor-serialization-tests-for-numbers-dou.patch [bz#997915]
- kvm-qapi-add-native-list-coverage-for-visitor-serializat.patch [bz#997915]
- kvm-qapi-add-native-list-coverage-for-QMP-output-visitor.patch [bz#997915]
- kvm-qapi-add-native-list-coverage-for-QMP-input-visitor-.patch [bz#997915]
- kvm-qapi-lack-of-two-commas-in-dict.patch [bz#997915]
- kvm-tests-QAPI-schema-parser-tests.patch [bz#997915]
- kvm-tests-Use-qapi-schema-test.json-as-schema-parser-tes.patch [bz#997915]
- kvm-qapi.py-Restructure-lexer-and-parser.patch [bz#997915]
- kvm-qapi.py-Decent-syntax-error-reporting.patch [bz#997915]
- kvm-qapi.py-Reject-invalid-characters-in-schema-file.patch [bz#997915]
- kvm-qapi.py-Fix-schema-parser-to-check-syntax-systematic.patch [bz#997915]
- kvm-qapi.py-Fix-diagnosing-non-objects-at-a-schema-s-top.patch [bz#997915]
- kvm-qapi.py-Rename-expr_eval-to-expr-in-parse_schema.patch [bz#997915]
- kvm-qapi.py-Permit-comments-starting-anywhere-on-the-lin.patch [bz#997915]
- kvm-scripts-qapi.py-Avoid-syntax-not-supported-by-Python.patch [bz#997915]
- kvm-tests-Fix-schema-parser-test-for-in-tree-build.patch [bz#997915]
- Resolves: bz#1017696
  ([branding] remove references to dynamic translation and user-mode emulation)
- Resolves: bz#1026314
  (qemu-kvm hang when use '-sandbox on'+'vnc'+'hda')
- Resolves: bz#997915
  (Backport new QAPI parser proactively to help developers and avoid silly conflicts)
    
* Tue Dec 17 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-24.el7
- kvm-range-add-Range-structure.patch [bz#1034876]
- kvm-range-add-Range-to-typedefs.patch [bz#1034876]
- kvm-range-add-min-max-operations-on-ranges.patch [bz#1034876]
- kvm-qdev-Add-SIZE-type-to-qdev-properties.patch [bz#1034876]
- kvm-qapi-make-visit_type_size-fallback-to-type_int.patch [bz#1034876]
- kvm-pc-move-IO_APIC_DEFAULT_ADDRESS-to-include-hw-i386-i.patch [bz#1034876]
- kvm-pci-add-helper-to-retrieve-the-64-bit-range.patch [bz#1034876]
- kvm-pci-fix-up-w64-size-calculation-helper.patch [bz#1034876]
- kvm-refer-to-FWCfgState-explicitly.patch [bz#1034876]
- kvm-fw_cfg-move-typedef-to-qemu-typedefs.h.patch [bz#1034876]
- kvm-arch_init-align-MR-size-to-target-page-size.patch [bz#1034876]
- kvm-loader-store-FW-CFG-ROM-files-in-RAM.patch [bz#1034876]
- kvm-pci-store-PCI-hole-ranges-in-guestinfo-structure.patch [bz#1034876]
- kvm-pc-pass-PCI-hole-ranges-to-Guests.patch [bz#1034876]
- kvm-pc-replace-i440fx_common_init-with-i440fx_init.patch [bz#1034876]
- kvm-pc-don-t-access-fw-cfg-if-NULL.patch [bz#1034876]
- kvm-pc-add-I440FX-QOM-cast-macro.patch [bz#1034876]
- kvm-pc-limit-64-bit-hole-to-2G-by-default.patch [bz#1034876]
- kvm-q35-make-pci-window-address-size-match-guest-cfg.patch [bz#1034876]
- kvm-q35-use-64-bit-window-programmed-by-guest.patch [bz#1034876]
- kvm-piix-use-64-bit-window-programmed-by-guest.patch [bz#1034876]
- kvm-pc-fix-regression-for-64-bit-PCI-memory.patch [bz#1034876]
- kvm-cleanup-object.h-include-error.h-directly.patch [bz#1034876]
- kvm-qom-cleanup-struct-Error-references.patch [bz#1034876]
- kvm-qom-add-pointer-to-int-property-helpers.patch [bz#1034876]
- kvm-fw_cfg-interface-to-trigger-callback-on-read.patch [bz#1034876]
- kvm-loader-support-for-unmapped-ROM-blobs.patch [bz#1034876]
- kvm-pcie_host-expose-UNMAPPED-macro.patch [bz#1034876]
- kvm-pcie_host-expose-address-format.patch [bz#1034876]
- kvm-q35-use-macro-for-MCFG-property-name.patch [bz#1034876]
- kvm-q35-expose-mmcfg-size-as-a-property.patch [bz#1034876]
- kvm-i386-add-ACPI-table-files-from-seabios.patch [bz#1034876]
- kvm-acpi-add-rules-to-compile-ASL-source.patch [bz#1034876]
- kvm-acpi-pre-compiled-ASL-files.patch [bz#1034876]
- kvm-acpi-ssdt-pcihp-updat-generated-file.patch [bz#1034876]
- kvm-loader-use-file-path-size-from-fw_cfg.h.patch [bz#1034876]
- kvm-i386-add-bios-linker-loader.patch [bz#1034876]
- kvm-loader-allow-adding-ROMs-in-done-callbacks.patch [bz#1034876]
- kvm-i386-define-pc-guest-info.patch [bz#1034876]
- kvm-acpi-piix-add-macros-for-acpi-property-names.patch [bz#1034876]
- kvm-piix-APIs-for-pc-guest-info.patch [bz#1034876]
- kvm-ich9-APIs-for-pc-guest-info.patch [bz#1034876]
- kvm-pvpanic-add-API-to-access-io-port.patch [bz#1034876]
- kvm-hpet-add-API-to-find-it.patch [bz#1034876]
- kvm-hpet-fix-build-with-CONFIG_HPET-off.patch [bz#1034876]
- kvm-acpi-add-interface-to-access-user-installed-tables.patch [bz#1034876]
- kvm-pc-use-new-api-to-add-builtin-tables.patch [bz#1034876]
- kvm-i386-ACPI-table-generation-code-from-seabios.patch [bz#1034876]
- kvm-ssdt-fix-PBLK-length.patch [bz#1034876]
- kvm-ssdt-proc-update-generated-file.patch [bz#1034876]
- kvm-pc-disable-pci-info.patch [bz#1034876]
- kvm-acpi-build-fix-build-on-glib-2.22.patch [bz#1034876]
- kvm-acpi-build-fix-build-on-glib-2.14.patch [bz#1034876]
- kvm-acpi-build-fix-support-for-glib-2.22.patch [bz#1034876]
- kvm-acpi-build-Fix-compiler-warning-missing-gnu_printf-f.patch [bz#1034876]
- kvm-exec-Fix-prototype-of-phys_mem_set_alloc-and-related.patch [bz#1034876]
- Resolves: bz#1034876
  (export acpi tables to guests)

* Tue Dec 17 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-23.el7
- kvm-qdev-monitor-Unref-device-when-device_add-fails.patch [bz#1003773]
- kvm-qdev-Drop-misleading-qdev_free-function.patch [bz#1003773]
- kvm-blockdev-fix-drive_init-opts-and-bs_opts-leaks.patch [bz#1003773]
- kvm-libqtest-rename-qmp-to-qmp_discard_response.patch [bz#1003773]
- kvm-libqtest-add-qmp-fmt-.-QDict-function.patch [bz#1003773]
- kvm-blockdev-test-add-test-case-for-drive_add-duplicate-.patch [bz#1003773]
- kvm-qdev-monitor-test-add-device_add-leak-test-cases.patch [bz#1003773]
- kvm-qtest-Use-display-none-by-default.patch [bz#1003773]
- Resolves: bz#1003773
  (When virtio-blk-pci device with dataplane is failed to be added, the drive cannot be released.)

* Tue Dec 17 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-22.el7
- Fix ksmtuned with set_process_name=1 [bz#1027420]
- Fix committed memory when no qemu-kvm running [bz#1027418]
- kvm-virtio-net-fix-the-memory-leak-in-rxfilter_notify.patch [bz#1033810]
- kvm-qom-Fix-memory-leak-in-object_property_set_link.patch [bz#1033810]
- kvm-fix-intel-hda-live-migration.patch [bz#1036537]
- kvm-vfio-pci-Release-all-MSI-X-vectors-when-disabled.patch [bz#1029743]
- kvm-Query-KVM-for-available-memory-slots.patch [bz#921490]
- kvm-block-Dont-ignore-previously-set-bdrv_flags.patch [bz#1039501]
- kvm-cleanup-trace-events.pl-New.patch [bz#997832]
- kvm-slavio_misc-Fix-slavio_led_mem_readw-_writew-tracepo.patch [bz#997832]
- kvm-milkymist-minimac2-Fix-minimac2_read-_write-tracepoi.patch [bz#997832]
- kvm-trace-events-Drop-unused-events.patch [bz#997832]
- kvm-trace-events-Fix-up-source-file-comments.patch [bz#997832]
- kvm-trace-events-Clean-up-with-scripts-cleanup-trace-eve.patch [bz#997832]
- kvm-trace-events-Clean-up-after-removal-of-old-usb-host-.patch [bz#997832]
- kvm-net-Update-netdev-peer-on-link-change.patch [bz#1027571]
- Resolves: bz#1027418
  (ksmtuned committed_memory() still returns "", not 0, when no qemu running)
- Resolves: bz#1027420
  (ksmtuned can’t handle libvirt WITH set_process_name=1)
- Resolves: bz#1027571
  ([virtio-win]win8.1 guest network can not resume automatically after do "set_link tap1 on")
- Resolves: bz#1029743
  (qemu-kvm core dump after hot plug/unplug 82576 PF about 100 times)
- Resolves: bz#1033810
  (memory leak in using object_get_canonical_path())
- Resolves: bz#1036537
  (Cross version migration from RHEL6.5 host to RHEL7.0 host with sound device failed.)
- Resolves: bz#1039501
  ([provisioning] discard=on broken)
- Resolves: bz#921490
  (qemu-kvm core dumped after hot plugging more than 11 VF through vfio-pci)
- Resolves: bz#997832
  (Backport trace fixes proactively to avoid confusion and silly conflicts)

* Tue Dec 03 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-21.el7
- kvm-scsi-Allocate-SCSITargetReq-r-buf-dynamically-CVE-20.patch [bz#1007334]
- Resolves: bz#1007334
  (CVE-2013-4344 qemu-kvm: qemu: buffer overflow in scsi_target_emulate_report_luns [rhel-7.0])

* Thu Nov 28 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-20.el7
- kvm-pc-drop-virtio-balloon-pci-event_idx-compat-property.patch [bz#1029539]
- kvm-virtio-net-only-delete-bh-that-existed.patch [bz#922463]
- kvm-virtio-net-broken-RX-filtering-logic-fixed.patch [bz#1029370]
- kvm-block-Avoid-unecessary-drv-bdrv_getlength-calls.patch [bz#1025138]
- kvm-block-Round-up-total_sectors.patch [bz#1025138]
- kvm-doc-fix-hardcoded-helper-path.patch [bz#1016952]
- kvm-introduce-RFQDN_REDHAT-RHEL-6-7-fwd.patch [bz#971933]
- kvm-error-reason-in-BLOCK_IO_ERROR-BLOCK_JOB_ERROR-event.patch [bz#971938]
- kvm-improve-debuggability-of-BLOCK_IO_ERROR-BLOCK_JOB_ER.patch [bz#895041]
- kvm-vfio-pci-Fix-multifunction-on.patch [bz#1029275]
- kvm-qcow2-Change-default-for-new-images-to-compat-1.1.patch [bz#1026739]
- kvm-qcow2-change-default-for-new-images-to-compat-1.1-pa.patch [bz#1026739]
- kvm-rng-egd-offset-the-point-when-repeatedly-read-from-t.patch [bz#1032862]
- kvm-Fix-rhel-rhev-conflict-for-qemu-kvm-common.patch [bz#1033463]
- Resolves: bz#1016952
  (qemu-kvm man page guide wrong path for qemu-bridge-helper)
- Resolves: bz#1025138
  (Read/Randread/Randrw performance regression)
- Resolves: bz#1026739
  (qcow2: Switch to compat=1.1 default for new images)
- Resolves: bz#1029275
  (Guest only find one 82576 VF(function 0) while use multifunction)
- Resolves: bz#1029370
  ([whql][netkvm][wlk] Virtio-net device handles RX multicast filtering improperly)
- Resolves: bz#1029539
  (Machine type rhel6.1.0 and  balloon device cause migration fail from RHEL6.5 host to RHEL7.0 host)
- Resolves: bz#1032862
  (virtio-rng-egd: repeatedly read same random data-block w/o considering the buffer offset)
- Resolves: bz#1033463
  (can not upgrade qemu-kvm-common to qemu-kvm-common-rhev due to conflicts)
- Resolves: bz#895041
  (QMP: forward port I/O error debug messages)
- Resolves: bz#922463
  (qemu-kvm core dump when virtio-net multi queue guest hot-unpluging vNIC)
- Resolves: bz#971933
  (QMP: add RHEL's vendor extension prefix)
- Resolves: bz#971938
  (QMP: Add error reason to BLOCK_IO_ERROR event)

* Mon Nov 11 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-19.el7
- kvm-qapi-qapi-visit.py-fix-list-handling-for-union-types.patch [bz#848203]
- kvm-qapi-qapi-visit.py-native-list-support.patch [bz#848203]
- kvm-qapi-enable-generation-of-native-list-code.patch [bz#848203]
- kvm-net-add-support-of-mac-programming-over-macvtap-in-Q.patch [bz#848203]
- Resolves: bz#848203
  (MAC Programming for virtio over macvtap - qemu-kvm support)

* Fri Nov 08 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-18.el7
- Removing leaked patch kvm-e1000-rtl8139-update-HMP-NIC-when-every-bit-is-writt.patch

* Thu Nov 07 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-17.el7
- kvm-pci-assign-Add-MSI-affinity-support.patch [bz#1025877]
- kvm-Fix-potential-resource-leak-missing-fclose.patch [bz#1025877]
- kvm-pci-assign-remove-the-duplicate-function-name-in-deb.patch [bz#1025877]
- kvm-Remove-s390-ccw-img-loader.patch [bz#1017682]
- kvm-Fix-vscclient-installation.patch [bz#1017681]
- kvm-Change-qemu-bridge-helper-permissions-to-4755.patch [bz#1017689]
- kvm-net-update-nic-info-during-device-reset.patch [bz#922589]
- kvm-net-e1000-update-network-information-when-macaddr-is.patch [bz#922589]
- kvm-net-rtl8139-update-network-information-when-macaddr-.patch [bz#922589]
- kvm-virtio-net-fix-up-HMP-NIC-info-string-on-reset.patch [bz#1026689]
- kvm-vfio-pci-VGA-quirk-update.patch [bz#1025477]
- kvm-vfio-pci-Add-support-for-MSI-affinity.patch [bz#1025477]
- kvm-vfio-pci-Test-device-reset-capabilities.patch [bz#1026550]
- kvm-vfio-pci-Lazy-PCI-option-ROM-loading.patch [bz#1026550]
- kvm-vfio-pci-Cleanup-error_reports.patch [bz#1026550]
- kvm-vfio-pci-Add-dummy-PCI-ROM-write-accessor.patch [bz#1026550]
- kvm-vfio-pci-Fix-endian-issues-in-vfio_pci_size_rom.patch [bz#1026550]
- kvm-linux-headers-Update-to-include-vfio-pci-hot-reset-s.patch [bz#1025472]
- kvm-vfio-pci-Implement-PCI-hot-reset.patch [bz#1025472]
- kvm-linux-headers-Update-for-KVM-VFIO-device.patch [bz#1025474]
- kvm-vfio-pci-Make-use-of-new-KVM-VFIO-device.patch [bz#1025474]
- kvm-vmdk-Fix-vmdk_parse_extents.patch [bz#995866]
- kvm-vmdk-fix-VMFS-extent-parsing.patch [bz#995866]
- kvm-e1000-rtl8139-update-HMP-NIC-when-every-bit-is-writt.patch [bz#922589]
- kvm-don-t-disable-ctrl_mac_addr-feature-for-6.5-machine-.patch [bz#1005039]
- Resolves: bz#1005039
  (add compat property to disable ctrl_mac_addr feature)
- Resolves: bz#1017681
  (rpmdiff test "Multilib regressions": vscclient is a libtool script on s390/s390x/ppc/ppc64)
- Resolves: bz#1017682
  (/usr/share/qemu-kvm/s390-ccw.img need not be distributed)
- Resolves: bz#1017689
  (/usr/libexec/qemu-bridge-helper permissions should be 4755)
- Resolves: bz#1025472
  (Nvidia GPU device assignment - qemu-kvm - bus reset support)
- Resolves: bz#1025474
  (Nvidia GPU device assignment - qemu-kvm - NoSnoop support)
- Resolves: bz#1025477
  (VFIO MSI affinity)
- Resolves: bz#1025877
  (pci-assign lacks MSI affinity support)
- Resolves: bz#1026550
  (QEMU VFIO update ROM loading code)
- Resolves: bz#1026689
  (virtio-net: macaddr is reset but network info of monitor isn't updated)
- Resolves: bz#922589
  (e1000/rtl8139: qemu mac address can not be changed via set the hardware address in guest)
- Resolves: bz#995866
  (fix vmdk support to ESX images)

* Thu Nov 07 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-16.el7
- kvm-block-drop-bs_snapshots-global-variable.patch [bz#1026524]
- kvm-block-move-snapshot-code-in-block.c-to-block-snapsho.patch [bz#1026524]
- kvm-block-fix-vvfat-error-path-for-enable_write_target.patch [bz#1026524]
- kvm-block-Bugfix-format-and-snapshot-used-in-drive-optio.patch [bz#1026524]
- kvm-iscsi-use-bdrv_new-instead-of-stack-structure.patch [bz#1026524]
- kvm-qcow2-Add-corrupt-bit.patch [bz#1004347]
- kvm-qcow2-Metadata-overlap-checks.patch [bz#1004347]
- kvm-qcow2-Employ-metadata-overlap-checks.patch [bz#1004347]
- kvm-qcow2-refcount-Move-OFLAG_COPIED-checks.patch [bz#1004347]
- kvm-qcow2-refcount-Repair-OFLAG_COPIED-errors.patch [bz#1004347]
- kvm-qcow2-refcount-Repair-shared-refcount-blocks.patch [bz#1004347]
- kvm-qcow2_check-Mark-image-consistent.patch [bz#1004347]
- kvm-qemu-iotests-Overlapping-cluster-allocations.patch [bz#1004347]
- kvm-w32-Fix-access-to-host-devices-regression.patch [bz#1026524]
- kvm-add-qemu-img-convert-n-option-skip-target-volume-cre.patch [bz#1026524]
- kvm-bdrv-Use-Error-for-opening-images.patch [bz#1026524]
- kvm-bdrv-Use-Error-for-creating-images.patch [bz#1026524]
- kvm-block-Error-parameter-for-open-functions.patch [bz#1026524]
- kvm-block-Error-parameter-for-create-functions.patch [bz#1026524]
- kvm-qemu-img-create-Emit-filename-on-error.patch [bz#1026524]
- kvm-qcow2-Use-Error-parameter.patch [bz#1026524]
- kvm-qemu-iotests-Adjustments-due-to-error-propagation.patch [bz#1026524]
- kvm-block-raw-Employ-error-parameter.patch [bz#1026524]
- kvm-block-raw-win32-Employ-error-parameter.patch [bz#1026524]
- kvm-blkdebug-Employ-error-parameter.patch [bz#1026524]
- kvm-blkverify-Employ-error-parameter.patch [bz#1026524]
- kvm-block-raw-posix-Employ-error-parameter.patch [bz#1026524]
- kvm-block-raw-win32-Always-use-errno-in-hdev_open.patch [bz#1026524]
- kvm-qmp-Documentation-for-BLOCK_IMAGE_CORRUPTED.patch [bz#1004347]
- kvm-qcow2-Correct-snapshots-size-for-overlap-check.patch [bz#1004347]
- kvm-qcow2-CHECK_OFLAG_COPIED-is-obsolete.patch [bz#1004347]
- kvm-qcow2-Correct-endianness-in-overlap-check.patch [bz#1004347]
- kvm-qcow2-Switch-L1-table-in-a-single-sequence.patch [bz#1004347]
- kvm-qcow2-Use-pread-for-inactive-L1-in-overlap-check.patch [bz#1004347]
- kvm-qcow2-Remove-wrong-metadata-overlap-check.patch [bz#1004347]
- kvm-qcow2-Use-negated-overflow-check-mask.patch [bz#1004347]
- kvm-qcow2-Make-overlap-check-mask-variable.patch [bz#1004347]
- kvm-qcow2-Add-overlap-check-options.patch [bz#1004347]
- kvm-qcow2-Array-assigning-options-to-OL-check-bits.patch [bz#1004347]
- kvm-qcow2-Add-more-overlap-check-bitmask-macros.patch [bz#1004347]
- kvm-qcow2-Evaluate-overlap-check-options.patch [bz#1004347]
- kvm-qapi-types.py-Split-off-generate_struct_fields.patch [bz#978402]
- kvm-qapi-types.py-Fix-enum-struct-sizes-on-i686.patch [bz#978402]
- kvm-qapi-types-visit.py-Pass-whole-expr-dict-for-structs.patch [bz#978402]
- kvm-qapi-types-visit.py-Inheritance-for-structs.patch [bz#978402]
- kvm-blockdev-Introduce-DriveInfo.enable_auto_del.patch [bz#978402]
- kvm-Implement-qdict_flatten.patch [bz#978402]
- kvm-blockdev-blockdev-add-QMP-command.patch [bz#978402]
- kvm-blockdev-Separate-ID-generation-from-DriveInfo-creat.patch [bz#978402]
- kvm-blockdev-Pass-QDict-to-blockdev_init.patch [bz#978402]
- kvm-blockdev-Move-parsing-of-media-option-to-drive_init.patch [bz#978402]
- kvm-blockdev-Move-parsing-of-if-option-to-drive_init.patch [bz#978402]
- kvm-blockdev-Moving-parsing-of-geometry-options-to-drive.patch [bz#978402]
- kvm-blockdev-Move-parsing-of-boot-option-to-drive_init.patch [bz#978402]
- kvm-blockdev-Move-bus-unit-index-processing-to-drive_ini.patch [bz#978402]
- kvm-blockdev-Move-virtio-blk-device-creation-to-drive_in.patch [bz#978402]
- kvm-blockdev-Remove-IF_-check-for-read-only-blockdev_ini.patch [bz#978402]
- kvm-qemu-iotests-Check-autodel-behaviour-for-device_del.patch [bz#978402]
- kvm-blockdev-Remove-media-parameter-from-blockdev_init.patch [bz#978402]
- kvm-blockdev-Don-t-disable-COR-automatically-with-blockd.patch [bz#978402]
- kvm-blockdev-blockdev_init-error-conversion.patch [bz#978402]
- kvm-sd-Avoid-access-to-NULL-BlockDriverState.patch [bz#978402]
- kvm-blockdev-fix-cdrom-read_only-flag.patch [bz#978402]
- kvm-block-fix-backing-file-overriding.patch [bz#978402]
- kvm-block-Disable-BDRV_O_COPY_ON_READ-for-the-backing-fi.patch [bz#978402]
- kvm-block-Don-t-copy-backing-file-name-on-error.patch [bz#978402]
- kvm-qemu-iotests-Try-creating-huge-qcow2-image.patch [bz#980771]
- kvm-block-move-qmp-and-info-dump-related-code-to-block-q.patch [bz#980771]
- kvm-block-dump-snapshot-and-image-info-to-specified-outp.patch [bz#980771]
- kvm-block-add-snapshot-info-query-function-bdrv_query_sn.patch [bz#980771]
- kvm-block-add-image-info-query-function-bdrv_query_image.patch [bz#980771]
- kvm-qmp-add-ImageInfo-in-BlockDeviceInfo-used-by-query-b.patch [bz#980771]
- kvm-vmdk-Implement-.bdrv_has_zero_init.patch [bz#980771]
- kvm-qemu-iotests-Add-basic-ability-to-use-binary-sample-.patch [bz#980771]
- kvm-qemu-iotests-Quote-TEST_IMG-and-TEST_DIR-usage.patch [bz#980771]
- kvm-qemu-iotests-fix-test-case-059.patch [bz#980771]
- kvm-qapi-Add-ImageInfoSpecific-type.patch [bz#980771]
- kvm-block-Add-bdrv_get_specific_info.patch [bz#980771]
- kvm-block-qapi-Human-readable-ImageInfoSpecific-dump.patch [bz#980771]
- kvm-qcow2-Add-support-for-ImageInfoSpecific.patch [bz#980771]
- kvm-qemu-iotests-Discard-specific-info-in-_img_info.patch [bz#980771]
- kvm-qemu-iotests-Additional-info-from-qemu-img-info.patch [bz#980771]
- kvm-vmdk-convert-error-code-to-use-errp.patch [bz#980771]
- kvm-vmdk-refuse-enabling-zeroed-grain-with-flat-images.patch [bz#980771]
- kvm-qapi-Add-optional-field-compressed-to-ImageInfo.patch [bz#980771]
- kvm-vmdk-Only-read-cid-from-image-file-when-opening.patch [bz#980771]
- kvm-vmdk-Implment-bdrv_get_specific_info.patch [bz#980771]
- Resolves: bz#1004347
  (Backport qcow2 corruption prevention patches)
- Resolves: bz#1026524
  (Backport block layer error parameter patches)
- Resolves: bz#978402
  ([RFE] Add discard support to qemu-kvm layer)
- Resolves: bz#980771
  ([RFE]  qemu-img should be able to tell the compat version of a qcow2 image)

* Thu Nov 07 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-15.el7
- kvm-cow-make-reads-go-at-a-decent-speed.patch [bz#989646]
- kvm-cow-make-writes-go-at-a-less-indecent-speed.patch [bz#989646]
- kvm-cow-do-not-call-bdrv_co_is_allocated.patch [bz#989646]
- kvm-block-keep-bs-total_sectors-up-to-date-even-for-grow.patch [bz#989646]
- kvm-block-make-bdrv_co_is_allocated-static.patch [bz#989646]
- kvm-block-do-not-use-total_sectors-in-bdrv_co_is_allocat.patch [bz#989646]
- kvm-block-remove-bdrv_is_allocated_above-bdrv_co_is_allo.patch [bz#989646]
- kvm-block-expect-errors-from-bdrv_co_is_allocated.patch [bz#989646]
- kvm-block-Fix-compiler-warning-Werror-uninitialized.patch [bz#989646]
- kvm-qemu-img-always-probe-the-input-image-for-allocated-.patch [bz#989646]
- kvm-block-make-bdrv_has_zero_init-return-false-for-copy-.patch [bz#989646]
- kvm-block-introduce-bdrv_get_block_status-API.patch [bz#989646]
- kvm-block-define-get_block_status-return-value.patch [bz#989646]
- kvm-block-return-get_block_status-data-and-flags-for-for.patch [bz#989646]
- kvm-block-use-bdrv_has_zero_init-to-return-BDRV_BLOCK_ZE.patch [bz#989646]
- kvm-block-return-BDRV_BLOCK_ZERO-past-end-of-backing-fil.patch [bz#989646]
- kvm-qemu-img-add-a-map-subcommand.patch [bz#989646]
- kvm-docs-qapi-document-qemu-img-map.patch [bz#989646]
- kvm-raw-posix-return-get_block_status-data-and-flags.patch [bz#989646]
- kvm-raw-posix-report-unwritten-extents-as-zero.patch [bz#989646]
- kvm-block-add-default-get_block_status-implementation-fo.patch [bz#989646]
- kvm-block-look-for-zero-blocks-in-bs-file.patch [bz#989646]
- kvm-qemu-img-fix-invalid-JSON.patch [bz#989646]
- kvm-block-get_block_status-set-pnum-0-on-error.patch [bz#989646]
- kvm-block-get_block_status-avoid-segfault-if-there-is-no.patch [bz#989646]
- kvm-block-get_block_status-avoid-redundant-callouts-on-r.patch [bz#989646]
- kvm-qcow2-Restore-total_sectors-value-in-save_vmstate.patch [bz#1025740]
- kvm-qcow2-Unset-zero_beyond_eof-in-save_vmstate.patch [bz#1025740]
- kvm-qemu-iotests-Test-for-loading-VM-state-from-qcow2.patch [bz#1025740]
- kvm-apic-rename-apic-specific-bitopts.patch [bz#1001216]
- kvm-hw-import-bitmap-operations-in-qdev-core-header.patch [bz#1001216]
- kvm-qemu-help-Sort-devices-by-logical-functionality.patch [bz#1001216]
- kvm-devices-Associate-devices-to-their-logical-category.patch [bz#1001216]
- kvm-Mostly-revert-qemu-help-Sort-devices-by-logical-func.patch [bz#1001216]
- kvm-qdev-monitor-Group-device_add-help-and-info-qdm-by-c.patch [bz#1001216]
- kvm-qdev-Replace-no_user-by-cannot_instantiate_with_devi.patch [bz#1001216]
- kvm-sysbus-Set-cannot_instantiate_with_device_add_yet.patch [bz#1001216]
- kvm-cpu-Document-why-cannot_instantiate_with_device_add_.patch [bz#1001216]
- kvm-apic-Document-why-cannot_instantiate_with_device_add.patch [bz#1001216]
- kvm-pci-host-Consistently-set-cannot_instantiate_with_de.patch [bz#1001216]
- kvm-ich9-Document-why-cannot_instantiate_with_device_add.patch [bz#1001216]
- kvm-piix3-piix4-Clean-up-use-of-cannot_instantiate_with_.patch [bz#1001216]
- kvm-vt82c686-Clean-up-use-of-cannot_instantiate_with_dev.patch [bz#1001216]
- kvm-isa-Clean-up-use-of-cannot_instantiate_with_device_a.patch [bz#1001216]
- kvm-qdev-Do-not-let-the-user-try-to-device_add-when-it-c.patch [bz#1001216]
- kvm-rhel-Revert-unwanted-cannot_instantiate_with_device_.patch [bz#1001216]
- kvm-rhel-Revert-downstream-changes-to-unused-default-con.patch [bz#1001076]
- kvm-rhel-Drop-cfi.pflash01-and-isa-ide-device.patch [bz#1001076]
- kvm-rhel-Drop-isa-vga-device.patch [bz#1001088]
- kvm-rhel-Make-isa-cirrus-vga-device-unavailable.patch [bz#1001088]
- kvm-rhel-Make-ccid-card-emulated-device-unavailable.patch [bz#1001123]
- kvm-x86-fix-migration-from-pre-version-12.patch [bz#1005695]
- kvm-x86-cpuid-reconstruct-leaf-0Dh-data.patch [bz#1005695]
- kvm-kvmvapic-Catch-invalid-ROM-size.patch [bz#920021]
- kvm-kvmvapic-Enter-inactive-state-on-hardware-reset.patch [bz#920021]
- kvm-kvmvapic-Clear-also-physical-ROM-address-when-enteri.patch [bz#920021]
- kvm-block-optionally-disable-live-block-jobs.patch [bz#987582]
- kvm-rpm-spec-template-disable-live-block-ops-for-rhel-en.patch [bz#987582]
- kvm-migration-disable-live-block-migration-b-i-for-rhel-.patch [bz#1022392]
- kvm-Build-ceph-rbd-only-for-rhev.patch [bz#987583]
- kvm-spec-Disable-host-cdrom-RHEL-only.patch [bz#760885]
- kvm-rhel-Make-pci-serial-2x-and-pci-serial-4x-device-una.patch [bz#1001180]
- kvm-usb-host-libusb-Fix-reset-handling.patch [bz#980415]
- kvm-usb-host-libusb-Configuration-0-may-be-a-valid-confi.patch [bz#980383]
- kvm-usb-host-libusb-Detach-kernel-drivers-earlier.patch [bz#980383]
- kvm-monitor-Remove-pci_add-command-for-Red-Hat-Enterpris.patch [bz#1010858]
- kvm-monitor-Remove-pci_del-command-for-Red-Hat-Enterpris.patch [bz#1010858]
- kvm-monitor-Remove-usb_add-del-commands-for-Red-Hat-Ente.patch [bz#1010858]
- kvm-monitor-Remove-host_net_add-remove-for-Red-Hat-Enter.patch [bz#1010858]
- kvm-fw_cfg-add-API-to-find-FW-cfg-object.patch [bz#990601]
- kvm-pvpanic-use-FWCfgState-explicitly.patch [bz#990601]
- kvm-pvpanic-initialization-cleanup.patch [bz#990601]
- kvm-pvpanic-fix-fwcfg-for-big-endian-hosts.patch [bz#990601]
- kvm-hw-misc-make-pvpanic-known-to-user.patch [bz#990601]
- kvm-gdbstub-do-not-restart-crashed-guest.patch [bz#990601]
- kvm-gdbstub-fix-for-commit-87f25c12bfeaaa0c41fb857713bbc.patch [bz#990601]
- kvm-vl-allow-cont-from-panicked-state.patch [bz#990601]
- kvm-hw-misc-don-t-create-pvpanic-device-by-default.patch [bz#990601]
- kvm-block-vhdx-add-migration-blocker.patch [bz#1007176]
- kvm-qemu-kvm.spec-add-vhdx-to-the-read-only-block-driver.patch [bz#1007176]
- kvm-qemu-kvm.spec-Add-VPC-VHD-driver-to-the-block-read-o.patch [bz#1007176]
- Resolves: bz#1001076
  (Disable or remove other block devices we won't support)
- Resolves: bz#1001088
  (Disable or remove display devices we won't support)
- Resolves: bz#1001123
  (Disable or remove device ccid-card-emulated)
- Resolves: bz#1001180
  (Disable or remove devices pci-serial-2x, pci-serial-4x)
- Resolves: bz#1001216
  (Fix no_user or provide another way make devices unavailable with -device / device_add)
- Resolves: bz#1005695
  (QEMU should hide CPUID.0Dh values that it does not support)
- Resolves: bz#1007176
  (Add VPC and VHDX file formats as supported in qemu-kvm (read-only))
- Resolves: bz#1010858
  (Disable unused human monitor commands)
- Resolves: bz#1022392
  (Disable live-storage-migration in qemu-kvm (migrate -b/-i))
- Resolves: bz#1025740
  (Saving VM state on qcow2 images results in VM state corruption)
- Resolves: bz#760885
  (Disable host cdrom passthrough)
- Resolves: bz#920021
  (qemu-kvm segment fault when reboot guest after hot unplug device with option ROM)
- Resolves: bz#980383
  (The usb3.0 stick can't be returned back to host after shutdown guest with usb3.0 pass-through)
- Resolves: bz#980415
  (libusbx: error [_open_sysfs_attr] open /sys/bus/usb/devices/4-1/bConfigurationValue failed ret=-1 errno=2)
- Resolves: bz#987582
  (Initial Virtualization Differentiation for RHEL7 (Live snapshots))
- Resolves: bz#987583
  (Initial Virtualization Differentiation for RHEL7 (Ceph enablement))
- Resolves: bz#989646
  (Support backup vendors in qemu to access qcow disk readonly)
- Resolves: bz#990601
  (pvpanic device triggers guest bugs when present by default)

* Wed Nov 06 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-14.el7
- kvm-target-i386-remove-tabs-from-target-i386-cpu.h.patch [bz#928867]
- kvm-migrate-vPMU-state.patch [bz#928867]
- kvm-blockdev-do-not-default-cache.no-flush-to-true.patch [bz#1009993]
- kvm-virtio-blk-do-not-relay-a-previous-driver-s-WCE-conf.patch [bz#1009993]
- kvm-rng-random-use-error_setg_file_open.patch [bz#907743]
- kvm-block-mirror_complete-use-error_setg_file_open.patch [bz#907743]
- kvm-blockdev-use-error_setg_file_open.patch [bz#907743]
- kvm-cpus-use-error_setg_file_open.patch [bz#907743]
- kvm-dump-qmp_dump_guest_memory-use-error_setg_file_open.patch [bz#907743]
- kvm-savevm-qmp_xen_save_devices_state-use-error_setg_fil.patch [bz#907743]
- kvm-block-bdrv_reopen_prepare-don-t-use-QERR_OPEN_FILE_F.patch [bz#907743]
- kvm-qerror-drop-QERR_OPEN_FILE_FAILED-macro.patch [bz#907743]
- kvm-rhel-Drop-ivshmem-device.patch [bz#787463]
- kvm-usb-remove-old-usb-host-code.patch [bz#1001144]
- kvm-Add-rhel6-pxe-roms-files.patch [bz#997702]
- kvm-Add-rhel6-pxe-rom-to-redhat-rpm.patch [bz#997702]
- kvm-Fix-migration-from-rhel6.5-to-rhel7-with-ipxe.patch [bz#997702]
- kvm-pc-Don-t-prematurely-explode-QEMUMachineInitArgs.patch [bz#994490]
- kvm-pc-Don-t-explode-QEMUMachineInitArgs-into-local-vari.patch [bz#994490]
- kvm-smbios-Normalize-smbios_entry_add-s-error-handling-t.patch [bz#994490]
- kvm-smbios-Convert-to-QemuOpts.patch [bz#994490]
- kvm-smbios-Improve-diagnostics-for-conflicting-entries.patch [bz#994490]
- kvm-smbios-Make-multiple-smbios-type-accumulate-sanely.patch [bz#994490]
- kvm-smbios-Factor-out-smbios_maybe_add_str.patch [bz#994490]
- kvm-hw-Pass-QEMUMachine-to-its-init-method.patch [bz#994490]
- kvm-smbios-Set-system-manufacturer-product-version-by-de.patch [bz#994490]
- kvm-smbios-Decouple-system-product-from-QEMUMachine.patch [bz#994490]
- kvm-rhel-SMBIOS-type-1-branding.patch [bz#994490]
- kvm-Add-disable-rhev-features-option-to-configure.patch []
- Resolves: bz#1001144
  (Disable or remove device usb-host-linux)
- Resolves: bz#1009993
  (RHEL7 guests do not issue fdatasyncs on virtio-blk)
- Resolves: bz#787463
  (disable ivshmem (was: [Hitachi 7.0 FEAT] Support ivshmem (Inter-VM Shared Memory)))
- Resolves: bz#907743
  (qemu-ga: empty reason string for OpenFileFailed error)
- Resolves: bz#928867
  (Virtual PMU support during live migration - qemu-kvm)
- Resolves: bz#994490
  (Set per-machine-type SMBIOS strings)
- Resolves: bz#997702
  (Migration from RHEL6.5 host to RHEL7.0 host is failed with virtio-net device)

* Tue Nov 05 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-13.el7
- kvm-seabios-paravirt-allow-more-than-1TB-in-x86-guest.patch [bz#989677]
- kvm-scsi-prefer-UUID-to-VM-name-for-the-initiator-name.patch [bz#1006468]
- kvm-Fix-incorrect-rhel_rhev_conflicts-macro-usage.patch [bz#1017693]
- Resolves: bz#1006468
  (libiscsi initiator name should use vm UUID)
- Resolves: bz#1017693
  (incorrect use of rhel_rhev_conflicts)
- Resolves: bz#989677
  ([HP 7.0 FEAT]: Increase KVM guest supported memory to 4TiB)

* Mon Nov 04 2013 Michal Novotny <minovotn@redhat.com> - 1.5.3-12.el7
- kvm-vl-Clean-up-parsing-of-boot-option-argument.patch [bz#997817]
- kvm-qemu-option-check_params-is-now-unused-drop-it.patch [bz#997817]
- kvm-vl-Fix-boot-order-and-once-regressions-and-related-b.patch [bz#997817]
- kvm-vl-Rename-boot_devices-to-boot_order-for-consistency.patch [bz#997817]
- kvm-pc-Make-no-fd-bootchk-stick-across-boot-order-change.patch [bz#997817]
- kvm-doc-Drop-ref-to-Bochs-from-no-fd-bootchk-documentati.patch [bz#997817]
- kvm-libqtest-Plug-fd-and-memory-leaks-in-qtest_quit.patch [bz#997817]
- kvm-libqtest-New-qtest_end-to-go-with-qtest_start.patch [bz#997817]
- kvm-qtest-Don-t-reset-on-qtest-chardev-connect.patch [bz#997817]
- kvm-boot-order-test-New-covering-just-PC-for-now.patch [bz#997817]
- kvm-qemu-ga-execute-fsfreeze-freeze-in-reverse-order-of-.patch [bz#1019352]
- kvm-rbd-link-and-load-librbd-dynamically.patch [bz#989608]
- kvm-rbd-Only-look-for-qemu-specific-copy-of-librbd.so.1.patch [bz#989608]
- kvm-spec-Whitelist-rbd-block-driver.patch [bz#989608]
- Resolves: bz#1019352
  (qemu-guest-agent: "guest-fsfreeze-freeze" deadlocks if the guest have mounted disk images)
- Resolves: bz#989608
  ([7.0 FEAT] qemu runtime support for librbd backend (ceph))
- Resolves: bz#997817
  (-boot order and -boot once regressed since RHEL-6)

* Thu Oct 31 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-11.el7
- kvm-chardev-fix-pty_chr_timer.patch [bz#994414]
- kvm-qemu-socket-zero-initialize-SocketAddress.patch [bz#922010]
- kvm-qemu-socket-drop-pointless-allocation.patch [bz#922010]
- kvm-qemu-socket-catch-monitor_get_fd-failures.patch [bz#922010]
- kvm-qemu-char-check-optional-fields-using-has_.patch [bz#922010]
- kvm-error-add-error_setg_file_open-helper.patch [bz#922010]
- kvm-qemu-char-use-more-specific-error_setg_-variants.patch [bz#922010]
- kvm-qemu-char-print-notification-to-stderr.patch [bz#922010]
- kvm-qemu-char-fix-documentation-for-telnet-wait-socket-f.patch [bz#922010]
- kvm-qemu-char-don-t-leak-opts-on-error.patch [bz#922010]
- kvm-qemu-char-use-ChardevBackendKind-in-CharDriver.patch [bz#922010]
- kvm-qemu-char-minor-mux-chardev-fixes.patch [bz#922010]
- kvm-qemu-char-add-chardev-mux-support.patch [bz#922010]
- kvm-qemu-char-report-udp-backend-errors.patch [bz#922010]
- kvm-qemu-socket-don-t-leak-opts-on-error.patch [bz#922010]
- kvm-chardev-handle-qmp_chardev_add-KIND_MUX-failure.patch [bz#922010]
- kvm-acpi-piix4-Enable-qemu-kvm-compatibility-mode.patch [bz#1019474]
- kvm-target-i386-support-loading-of-cpu-xsave-subsection.patch [bz#1004743]
- Resolves: bz#1004743
  (XSAVE migration format not compatible between RHEL6 and RHEL7)
- Resolves: bz#1019474
  (RHEL-7 can't load piix4_pm migration section from RHEL-6.5)
- Resolves: bz#922010
  (RFE: support hotplugging chardev & serial ports)
- Resolves: bz#994414
  (hot-unplug chardev with pty backend caused qemu Segmentation fault)

* Thu Oct 17 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-10.el7
- kvm-xhci-fix-endpoint-interval-calculation.patch [bz#1001604]
- kvm-xhci-emulate-intr-endpoint-intervals-correctly.patch [bz#1001604]
- kvm-xhci-reset-port-when-disabling-slot.patch [bz#1001604]
- kvm-Revert-usb-hub-report-status-changes-only-once.patch [bz#1001604]
- kvm-target-i386-Set-model-6-on-qemu64-qemu32-CPU-models.patch [bz#1004290]
- kvm-pc-rhel6-doesn-t-have-APIC-on-pentium-CPU-models.patch [bz#918907]
- kvm-pc-RHEL-6-had-x2apic-set-on-Opteron_G-123.patch [bz#918907]
- kvm-pc-RHEL-6-don-t-have-RDTSCP.patch [bz#918907]
- kvm-scsi-Fix-scsi_bus_legacy_add_drive-scsi-generic-with.patch [bz#1009285]
- kvm-seccomp-fine-tuning-whitelist-by-adding-times.patch [bz#1004175]
- kvm-block-add-bdrv_write_zeroes.patch [bz#921465]
- kvm-block-raw-add-bdrv_co_write_zeroes.patch [bz#921465]
- kvm-rdma-export-qemu_fflush.patch [bz#921465]
- kvm-block-migration-efficiently-encode-zero-blocks.patch [bz#921465]
- kvm-Fix-real-mode-guest-migration.patch [bz#921465]
- kvm-Fix-real-mode-guest-segments-dpl-value-in-savevm.patch [bz#921465]
- kvm-migration-add-autoconvergence-documentation.patch [bz#921465]
- kvm-migration-send-total-time-in-QMP-at-completed-stage.patch [bz#921465]
- kvm-migration-don-t-use-uninitialized-variables.patch [bz#921465]
- kvm-pc-drop-external-DSDT-loading.patch [bz#921465]
- kvm-hda-codec-refactor-common-definitions-into-a-header-.patch [bz#954195]
- kvm-hda-codec-make-mixemu-selectable-at-runtime.patch [bz#954195]
- kvm-audio-remove-CONFIG_MIXEMU-configure-option.patch [bz#954195]
- kvm-pc_piix-disable-mixer-for-6.4.0-machine-types-and-be.patch [bz#954195]
- kvm-spec-mixemu-config-option-is-no-longer-supported-and.patch [bz#954195]
- Resolves: bz#1001604
  (usb hub doesn't work properly (win7 sees downstream port #1 only).)
- Resolves: bz#1004175
  ('-sandbox on'  option  cause  qemu-kvm process hang)
- Resolves: bz#1004290
  (Use model 6 for qemu64 and intel cpus)
- Resolves: bz#1009285
  (-device usb-storage,serial=... crashes with SCSI generic drive)
- Resolves: bz#918907
  (provide backwards-compatible RHEL specific machine types in QEMU - CPU features)
- Resolves: bz#921465
  (Migration can not finished even the "remaining ram" is already 0 kb)
- Resolves: bz#954195
  (RHEL machines <=6.4 should not use mixemu)

* Thu Oct 10 2013 Miroslav Rezanina <mrezanin@redhat.com> - 1.5.3-9.el7
- kvm-qxl-fix-local-renderer.patch [bz#1005036]
- kvm-spec-include-userspace-iSCSI-initiator-in-block-driv.patch [bz#923843]
- kvm-linux-headers-update-to-kernel-3.10.0-26.el7.patch [bz#1008987]
- kvm-target-i386-add-feature-kvm_pv_unhalt.patch [bz#1008987]
- kvm-warn-if-num-cpus-is-greater-than-num-recommended.patch [bz#1010881]
- kvm-char-move-backends-io-watch-tag-to-CharDriverState.patch [bz#1007222]
- kvm-char-use-common-function-to-disable-callbacks-on-cha.patch [bz#1007222]
- kvm-char-remove-watch-callback-on-chardev-detach-from-fr.patch [bz#1007222]
- kvm-block-don-t-lose-data-from-last-incomplete-sector.patch [bz#1017049]
- kvm-vmdk-fix-cluster-size-check-for-flat-extents.patch [bz#1017049]
- kvm-qemu-iotests-add-monolithicFlat-creation-test-to-059.patch [bz#1017049]
- Resolves: bz#1005036
  (When using “-vga qxl” together with “-display vnc=:5” or “-display  sdl” qemu displays  pixel garbage)
- Resolves: bz#1007222
  (QEMU core dumped when do hot-unplug virtio serial port during transfer file between host to guest with virtio serial through TCP socket)
- Resolves: bz#1008987
  (pvticketlocks: add kvm feature kvm_pv_unhalt)
- Resolves: bz#1010881
  (backport vcpu soft limit warning)
- Resolves: bz#1017049
  (qemu-img refuses to open the vmdk format image its created)
- Resolves: bz#923843
  (include userspace iSCSI initiator in block driver whitelist)

* Wed Oct 09 2013 Miroslav Rezanina <mrezanin@redhat.com> - qemu-kvm-1.5.3-8.el7
- kvm-vmdk-Make-VMDK3Header-and-VmdkGrainMarker-QEMU_PACKE.patch [bz#995866]
- kvm-vmdk-use-unsigned-values-for-on-disk-header-fields.patch [bz#995866]
- kvm-qemu-iotests-add-poke_file-utility-function.patch [bz#995866]
- kvm-qemu-iotests-add-empty-test-case-for-vmdk.patch [bz#995866]
- kvm-vmdk-check-granularity-field-in-opening.patch [bz#995866]
- kvm-vmdk-check-l2-table-size-when-opening.patch [bz#995866]
- kvm-vmdk-check-l1-size-before-opening-image.patch [bz#995866]
- kvm-vmdk-use-heap-allocation-for-whole_grain.patch [bz#995866]
- kvm-vmdk-rename-num_gtes_per_gte-to-num_gtes_per_gt.patch [bz#995866]
- kvm-vmdk-Move-l1_size-check-into-vmdk_add_extent.patch [bz#995866]
- kvm-vmdk-fix-L1-and-L2-table-size-in-vmdk3-open.patch [bz#995866]
- kvm-vmdk-support-vmfsSparse-files.patch [bz#995866]
- kvm-vmdk-support-vmfs-files.patch [bz#995866]
- Resolves: bz#995866
  (fix vmdk support to ESX images)

* Thu Sep 26 2013 Miroslav Rezanina <mrezanin@redhat.com> - qemu-kvm-1.5.3-7.el7
- kvm-spice-fix-display-initialization.patch [bz#974887]
- kvm-Remove-i82550-network-card-emulation.patch [bz#921983]
- kvm-Remove-usb-wacom-tablet.patch [bz#903914]
- kvm-Disable-usb-uas.patch [bz#903914]
- kvm-Disable-vhost-scsi.patch [bz#994642]
- kvm-Remove-no-hpet-option.patch [bz#947441]
- kvm-Disable-isa-parallel.patch [bz#1002286]
- kvm-xhci-implement-warm-port-reset.patch [bz#949514]
- kvm-usb-add-serial-bus-property.patch [bz#953304]
- kvm-rhel6-compat-usb-serial-numbers.patch [bz#953304]
- kvm-vmdk-fix-comment-for-vmdk_co_write_zeroes.patch [bz#995866]
- kvm-gluster-Add-image-resize-support.patch [bz#1007226]
- kvm-block-Introduce-bs-zero_beyond_eof.patch [bz#1007226]
- kvm-block-Produce-zeros-when-protocols-reading-beyond-en.patch [bz#1007226]
- kvm-gluster-Abort-on-AIO-completion-failure.patch [bz#1007226]
- kvm-Preparation-for-usb-bt-dongle-conditional-build.patch [bz#1001131]
- kvm-Remove-dev-bluetooth.c-dependency-from-vl.c.patch [bz#1001131]
- kvm-exec-Fix-Xen-RAM-allocation-with-unusual-options.patch [bz#1009328]
- kvm-exec-Clean-up-fall-back-when-mem-path-allocation-fai.patch [bz#1009328]
- kvm-exec-Reduce-ifdeffery-around-mem-path.patch [bz#1009328]
- kvm-exec-Simplify-the-guest-physical-memory-allocation-h.patch [bz#1009328]
- kvm-exec-Drop-incorrect-dead-S390-code-in-qemu_ram_remap.patch [bz#1009328]
- kvm-exec-Clean-up-unnecessary-S390-ifdeffery.patch [bz#1009328]
- kvm-exec-Don-t-abort-when-we-can-t-allocate-guest-memory.patch [bz#1009328]
- kvm-pc_sysfw-Fix-ISA-BIOS-init-for-ridiculously-big-flas.patch [bz#1009328]
- kvm-virtio-scsi-Make-type-virtio-scsi-common-abstract.patch [bz#903918]
- kvm-qga-move-logfiles-to-new-directory-for-easier-SELinu.patch [bz#1009491]
- kvm-target-i386-add-cpu64-rhel6-CPU-model.patch [bz#918907]
- kvm-fix-steal-time-MSR-vmsd-callback-to-proper-opaque-ty.patch [bz#903889]
- Resolves: bz#1001131
  (Disable or remove device usb-bt-dongle)
- Resolves: bz#1002286
  (Disable or remove device isa-parallel)
- Resolves: bz#1007226
  (Introduce bs->zero_beyond_eof)
- Resolves: bz#1009328
  ([RFE] Nicer error report when qemu-kvm can't allocate guest RAM)
- Resolves: bz#1009491
  (move qga logfiles to new /var/log/qemu-ga/ directory [RHEL-7])
- Resolves: bz#903889
  (The value of steal time in "top" command always is "0.0% st" after guest migration)
- Resolves: bz#903914
  (Disable or remove usb related devices that we will not support)
- Resolves: bz#903918
  (Disable or remove emulated SCSI devices we will not support)
- Resolves: bz#918907
  (provide backwards-compatible RHEL specific machine types in QEMU - CPU features)
- Resolves: bz#921983
  (Disable or remove emulated network devices that we will not support)
- Resolves: bz#947441
  (HPET device must be disabled)
- Resolves: bz#949514
  (fail to passthrough the USB3.0 stick to windows guest with xHCI controller under pc-i440fx-1.4)
- Resolves: bz#953304
  (Serial number of some USB devices must be fixed for older RHEL machine types)
- Resolves: bz#974887
  (the screen of guest fail to display correctly when use spice + qxl driver)
- Resolves: bz#994642
  (should disable vhost-scsi)
- Resolves: bz#995866
  (fix vmdk support to ESX images)

* Mon Sep 23 2013 Paolo Bonzini <pbonzini@redhat.com> - qemu-kvm-1.5.3-6.el7
- re-enable spice
- Related: #979953

* Mon Sep 23 2013 Paolo Bonzini <pbonzini@redhat.com> - qemu-kvm-1.5.3-5.el7
- temporarily disable spice until libiscsi rebase is complete
- Related: #979953

* Thu Sep 19 2013 Michal Novotny <minovotn@redhat.com> - qemu-kvm-1.5.3-4.el7
- kvm-block-package-preparation-code-in-qmp_transaction.patch [bz#1005818]
- kvm-block-move-input-parsing-code-in-qmp_transaction.patch [bz#1005818]
- kvm-block-package-committing-code-in-qmp_transaction.patch [bz#1005818]
- kvm-block-package-rollback-code-in-qmp_transaction.patch [bz#1005818]
- kvm-block-make-all-steps-in-qmp_transaction-as-callback.patch [bz#1005818]
- kvm-blockdev-drop-redundant-proto_drv-check.patch [bz#1005818]
- kvm-block-Don-t-parse-protocol-from-file.filename.patch [bz#1005818]
- kvm-Revert-block-Disable-driver-specific-options-for-1.5.patch [bz#1005818]
- kvm-qcow2-Add-refcount-update-reason-to-all-callers.patch [bz#1005818]
- kvm-qcow2-Options-to-enable-discard-for-freed-clusters.patch [bz#1005818]
- kvm-qcow2-Batch-discards.patch [bz#1005818]
- kvm-block-Always-enable-discard-on-the-protocol-level.patch [bz#1005818]
- kvm-qapi.py-Avoid-code-duplication.patch [bz#1005818]
- kvm-qapi.py-Allow-top-level-type-reference-for-command-d.patch [bz#1005818]
- kvm-qapi-schema-Use-BlockdevSnapshot-type-for-blockdev-s.patch [bz#1005818]
- kvm-qapi-types.py-Implement-base-for-unions.patch [bz#1005818]
- kvm-qapi-visit.py-Split-off-generate_visit_struct_fields.patch [bz#1005818]
- kvm-qapi-visit.py-Implement-base-for-unions.patch [bz#1005818]
- kvm-docs-Document-QAPI-union-types.patch [bz#1005818]
- kvm-qapi-Add-visitor-for-implicit-structs.patch [bz#1005818]
- kvm-qapi-Flat-unions-with-arbitrary-discriminator.patch [bz#1005818]
- kvm-qapi-Add-consume-argument-to-qmp_input_get_object.patch [bz#1005818]
- kvm-qapi.py-Maintain-a-list-of-union-types.patch [bz#1005818]
- kvm-qapi-qapi-types.py-native-list-support.patch [bz#1005818]
- kvm-qapi-Anonymous-unions.patch [bz#1005818]
- kvm-block-Allow-driver-option-on-the-top-level.patch [bz#1005818]
- kvm-QemuOpts-Add-qemu_opt_unset.patch [bz#1005818]
- kvm-blockdev-Rename-I-O-throttling-options-for-QMP.patch [bz#1005818]
- kvm-qemu-iotests-Update-051-reference-output.patch [bz#1005818]
- kvm-blockdev-Rename-readonly-option-to-read-only.patch [bz#1005818]
- kvm-blockdev-Split-up-cache-option.patch [bz#1005818]
- kvm-qcow2-Use-dashes-instead-of-underscores-in-options.patch [bz#1005818]
- kvm-qemu-iotests-filter-QEMU-version-in-monitor-banner.patch [bz#1006959]
- kvm-tests-set-MALLOC_PERTURB_-to-expose-memory-bugs.patch [bz#1006959]
- kvm-qemu-iotests-Whitespace-cleanup.patch [bz#1006959]
- kvm-qemu-iotests-Fixed-test-case-026.patch [bz#1006959]
- kvm-qemu-iotests-Fix-test-038.patch [bz#1006959]
- kvm-qemu-iotests-Remove-lsi53c895a-tests-from-051.patch [bz#1006959]
- Resolves: bz#1005818
  (qcow2: Backport discard command line options)
- Resolves: bz#1006959
  (qemu-iotests false positives)

* Thu Aug 29 2013 Miroslav Rezanina <mrezanin@redhat.com> - qemu-kvm-1.5.3-3.el7
- Fix rhel/rhev split

* Thu Aug 29 2013 Miroslav Rezanina <mrezanin@redhat.com> - qemu-kvm-1.5.3-2.el7
- kvm-osdep-add-qemu_get_local_state_pathname.patch [bz#964304]
- kvm-qga-determine-default-state-dir-and-pidfile-dynamica.patch [bz#964304]
- kvm-configure-don-t-save-any-fixed-local_statedir-for-wi.patch [bz#964304]
- kvm-qga-create-state-directory-on-win32.patch [bz#964304]
- kvm-qga-save-state-directory-in-ga_install_service-RHEL-.patch [bz#964304]
- kvm-Makefile-create-.-var-run-when-installing-the-POSIX-.patch [bz#964304]
- kvm-qemu-option-Fix-qemu_opts_find-for-null-id-arguments.patch [bz#980782]
- kvm-qemu-option-Fix-qemu_opts_set_defaults-for-corner-ca.patch [bz#980782]
- kvm-vl-New-qemu_get_machine_opts.patch [bz#980782]
- kvm-Fix-machine-options-accel-kernel_irqchip-kvm_shadow_.patch [bz#980782]
- kvm-microblaze-Fix-latent-bug-with-default-DTB-lookup.patch [bz#980782]
- kvm-Simplify-machine-option-queries-with-qemu_get_machin.patch [bz#980782]
- kvm-pci-add-VMSTATE_MSIX.patch [bz#838170]
- kvm-xhci-add-XHCISlot-addressed.patch [bz#838170]
- kvm-xhci-add-xhci_alloc_epctx.patch [bz#838170]
- kvm-xhci-add-xhci_init_epctx.patch [bz#838170]
- kvm-xhci-add-live-migration-support.patch [bz#838170]
- kvm-pc-set-level-xlevel-correctly-on-486-qemu32-CPU-mode.patch [bz#918907]
- kvm-pc-Remove-incorrect-rhel6.x-compat-model-value-for-C.patch [bz#918907]
- kvm-pc-rhel6.x-has-x2apic-present-on-Conroe-Penryn-Nehal.patch [bz#918907]
- kvm-pc-set-compat-CPUID-0x80000001-.EDX-bits-on-Westmere.patch [bz#918907]
- kvm-pc-Remove-PCLMULQDQ-from-Westmere-on-rhel6.x-machine.patch [bz#918907]
- kvm-pc-SandyBridge-rhel6.x-compat-fixes.patch [bz#918907]
- kvm-pc-Haswell-doesn-t-have-rdtscp-on-rhel6.x.patch [bz#918907]
- kvm-i386-fix-LAPIC-TSC-deadline-timer-save-restore.patch [bz#972433]
- kvm-all.c-max_cpus-should-not-exceed-KVM-vcpu-limit.patch [bz#996258]
- kvm-add-timestamp-to-error_report.patch [bz#906937]
- kvm-Convert-stderr-message-calling-error_get_pretty-to-e.patch [bz#906937]
- Resolves: bz#838170
  (Add live migration support for USB [xhci, usb-uas])
- Resolves: bz#906937
  ([Hitachi 7.0 FEAT][QEMU]Add a time stamp to error message (*))
- Resolves: bz#918907
  (provide backwards-compatible RHEL specific machine types in QEMU - CPU features)
- Resolves: bz#964304
  (Windows guest agent service failed to be started)
- Resolves: bz#972433
  ("INFO: rcu_sched detected stalls" after RHEL7 kvm vm migrated)
- Resolves: bz#980782
  (kernel_irqchip defaults to off instead of on without -machine)
- Resolves: bz#996258
  (boot guest with maxcpu=255 successfully but actually max number of vcpu is 160)

* Wed Aug 28 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.3-1
- Rebase to qemu 1.5.3

* Tue Aug 20 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.2-4
- qemu: guest agent creates files with insecure permissions in deamon mode [rhel-7.0] (rhbz 974444)
- update qemu-ga config & init script in RHEL7 wrt. fsfreeze hook (rhbz 969942)
- RHEL7 does not have equivalent functionality for __com.redhat_qxl_screendump (rhbz 903910)
- SEP flag behavior for CPU models of RHEL6 machine types should be compatible (rhbz 960216)
- crash command can not read the dump-guest-memory file when paging=false [RHEL-7] (rhbz 981582)
- RHEL 7 qemu-kvm fails to build on F19 host due to libusb deprecated API (rhbz 996469)
- Live migration support in virtio-blk-data-plane (rhbz 995030)
- qemu-img resize can execute successfully even input invalid syntax (rhbz 992935)

* Fri Aug 09 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.2-3
- query mem info from monitor would cause qemu-kvm hang [RHEL-7] (rhbz #970047)
- Throttle-down guest to help with live migration convergence (backport to RHEL7.0) (rhbz #985958)
- disable (for now) EFI-enabled roms (rhbz #962563)
- qemu-kvm "vPMU passthrough" mode breaks migration, shouldn't be enabled by default (rhbz #853101)
- Remove pending watches after virtserialport unplug (rhbz #992900)
- Containment of error when an SR-IOV device encounters an error... (rhbz #984604)

* Wed Jul 31 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.2-2
- SPEC file prepared for RHEL/RHEV split (rhbz #987165)
- RHEL guest( sata disk ) can not boot up (rhbz #981723)
- Kill the "use flash device for BIOS unless KVM" misfeature (rhbz #963280)
- Provide RHEL-6 machine types (rhbz #983991)
- Change s3/s4 default to "disable". (rhbz #980840)  
- Support Virtual Memory Disk Format in qemu (rhbz #836675)
- Glusterfs backend for QEMU (rhbz #805139)

* Tue Jul 02 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.2-1
- Rebase to 1.5.2

* Tue Jul 02 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.1-2
- Fix package package version info (bz #952996)
- pc: Replace upstream machine types by RHEL-7 types (bz #977864)
- target-i386: Update model values on Conroe/Penryn/Nehalem CPU model (bz #861210)
- target-i386: Set level=4 on Conroe/Penryn/Nehalem (bz #861210)

* Fri Jun 28 2013 Miroslav Rezanina <mrezanin@redhat.com> - 10:1.5.1-1
- Rebase to 1.5.1
- Change epoch to 10 to obsolete RHEL-6 qemu-kvm-rhev package (bz #818626)

* Fri May 24 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.5.0-2
- Enable werror (bz #948290)
- Enable nbd driver (bz #875871)
- Fix udev rules file location (bz #958860)
- Remove +x bit from systemd unit files (bz #965000)
- Drop unneeded kvm.modules on x86 (bz #963642)
- Fix build flags
- Enable libusb

* Thu May 23 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.5.0-1
- Rebase to 1.5.0

* Tue Apr 23 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.4.0-4
- Enable build of libcacard subpackage for non-x86_64 archs (bz #873174)
- Enable build of qemu-img subpackage for non-x86_64 archs (bz #873174)
- Enable build of qemu-guest-agent subpackage for non-x86_64 archs (bz #873174)

* Tue Apr 23 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.4.0-3
- Enable/disable features supported by rhel7
- Use qemu-kvm instead of qemu in filenames and pathes

* Fri Apr 19 2013 Daniel Mach <dmach@redhat.com> - 3:1.4.0-2.1
- Rebuild for cyrus-sasl

* Fri Apr 05 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.4.0-2
- Synchronization with Fedora 19 package version 2:1.4.0-8

* Wed Apr 03 2013 Daniel Mach <dmach@redhat.com> - 3:1.4.0-1.1
- Rebuild for libseccomp

* Thu Mar 07 2013 Miroslav Rezanina <mrezanin@redhat.com> - 3:1.4.0-1
- Rebase to 1.4.0

* Mon Feb 25 2013 Michal Novotny <minovotn@redhat.com> - 3:1.3.0-8
- Missing package qemu-system-x86 in hardware certification kvm testing (bz#912433)
- Resolves: bz#912433
  (Missing package qemu-system-x86 in hardware certification kvm testing)

* Fri Feb 22 2013 Alon Levy <alevy@redhat.com> - 3:1.3.0-6
- Bump epoch back to 3 since there has already been a 3 package release:
  3:1.2.0-20.el7 https://brewweb.devel.redhat.com/buildinfo?buildID=244866
- Mark explicit libcacard dependency on new enough qemu-img to avoid conflict
  since /usr/bin/vscclient was moved from qemu-img to libcacard subpackage.

* Wed Feb 13 2013 Michal Novotny <minovotn@redhat.com> - 2:1.3.0-5
- Fix patch contents for usb-redir (bz#895491)
- Resolves: bz#895491
  (PATCH: 0110-usb-redir-Add-flow-control-support.patch has been mangled on rebase !!)

* Wed Feb 06 2013 Alon Levy <alevy@redhat.com> - 2:1.3.0-4
- Add patch from f19 package for libcacard missing error_set symbol.
- Resolves: bz#891552

* Mon Jan 07 2013 Michal Novotny <minovotn@redhat.com> - 2:1.3.0-3
- Remove dependency on bogus qemu-kvm-kvm package [bz#870343]
- Resolves: bz#870343
  (qemu-kvm-1.2.0-16.el7 cant be installed)

* Tue Dec 18 2012 Michal Novotny <minovotn@redhat.com> - 2:1.3.0-2
- Rename qemu to qemu-kvm
- Move qemu-kvm to libexecdir

* Fri Dec 07 2012 Cole Robinson <crobinso@redhat.com> - 2:1.3.0-1
- Switch base tarball from qemu-kvm to qemu
- qemu 1.3 release
- Option to use linux VFIO driver to assign PCI devices
- Many USB3 improvements
- New paravirtualized hardware random number generator device.
- Support for Glusterfs volumes with "gluster://" -drive URI
- Block job commands for live block commit and storage migration

* Wed Nov 28 2012 Alon Levy <alevy@redhat.com> - 2:1.2.0-25
* Merge libcacard into qemu, since they both use the same sources now.

* Thu Nov 22 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-24
- Move vscclient to qemu-common, qemu-nbd to qemu-img

* Tue Nov 20 2012 Alon Levy <alevy@redhat.com> - 2:1.2.0-23
- Rewrite fix for bz #725965 based on fix for bz #867366
- Resolve bz #867366

* Fri Nov 16 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-23
- Backport --with separate_kvm support from EPEL branch

* Fri Nov 16 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-22
- Fix previous commit

* Fri Nov 16 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-21
- Backport commit 38f419f (configure: Fix CONFIG_QEMU_HELPERDIR generation,
  2012-10-17)

* Thu Nov 15 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-20
- Install qemu-bridge-helper as suid root
- Distribute a sample /etc/qemu/bridge.conf file

* Thu Nov  1 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-19
- Sync spice patches with upstream, minor bugfixes and set the qxl pci
  device revision to 4 by default, so that guests know they can use
  the new features

* Tue Oct 30 2012 Cole Robinson <crobinso@redhat.com> - 2:1.2.0-18
- Fix loading arm initrd if kernel is very large (bz #862766)
- Don't use reserved word 'function' in systemtap files (bz #870972)
- Drop assertion that was triggering when pausing guests w/ qxl (bz
  #870972)

* Sun Oct 28 2012 Cole Robinson <crobinso@redhat.com> - 2:1.2.0-17
- Pull patches queued for qemu 1.2.1

* Fri Oct 19 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-16
- add s390x KVM support
- distribute pre-built firmware or device trees for Alpha, Microblaze, S390
- add missing system targets
- add missing linux-user targets
- fix previous commit

* Thu Oct 18 2012 Dan Horák <dan[at]danny.cz> - 2:1.2.0-15
- fix build on non-kvm arches like s390(x)

* Wed Oct 17 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-14
- Change SLOF Requires for the new version number

* Thu Oct 11 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-13
- Add ppc support to kvm.modules (original patch by David Gibson)
- Replace x86only build with kvmonly build: add separate defines and
  conditionals for all packages, so that they can be chosen and
  renamed in kvmonly builds and so that qemu has the appropriate requires
- Automatically pick libfdt dependancy
- Add knob to disable spice+seccomp

* Fri Sep 28 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-12
- Call udevadm on post, fixing bug 860658

* Fri Sep 28 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-11
- Rebuild against latest spice-server and spice-protocol
- Fix non-seamless migration failing with vms with usb-redir devices,
  to allow boxes to load such vms from disk

* Tue Sep 25 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-10
- Sync Spice patchsets with upstream (rhbz#860238)
- Fix building with usbredir >= 0.5.2

* Thu Sep 20 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-9
- Sync USB and Spice patchsets with upstream

* Sun Sep 16 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.2.0-8
- Use 'global' instead of 'define', and underscore in definition name,
  n-v-r, and 'dist' tag of SLOF, all to fix RHBZ#855252.

* Fri Sep 14 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.2.0-4
- add versioned dependency from qemu-system-ppc to SLOF (BZ#855252)

* Wed Sep 12 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.2.0-3
- Fix RHBZ#853408 which causes libguestfs failure.

* Sat Sep  8 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-2
- Fix crash on (seamless) migration
- Sync usbredir live migration patches with upstream

* Fri Sep  7 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.2.0-1
- New upstream release 1.2.0 final
- Add support for Spice seamless migration
- Add support for Spice dynamic monitors
- Add support for usb-redir live migration

* Tue Sep 04 2012 Adam Jackson <ajax@redhat.com> 1.2.0-0.5.rc1
- Flip Requires: ceph >= foo to Conflicts: ceph < foo, so we pull in only the
  libraries which we need and not the rest of ceph which we don't.

* Tue Aug 28 2012 Cole Robinson <crobinso@redhat.com> 1.2.0-0.4.rc1
- Update to 1.2.0-rc1

* Mon Aug 20 2012 Richard W.M. Jones <rjones@redhat.com> - 1.2-0.3.20120806git3e430569
- Backport Bonzini's vhost-net fix (RHBZ#848400).

* Tue Aug 14 2012 Cole Robinson <crobinso@redhat.com> - 1.2-0.2.20120806git3e430569
- Bump release number, previous build forgot but the dist bump helped us out

* Tue Aug 14 2012 Cole Robinson <crobinso@redhat.com> - 1.2-0.1.20120806git3e430569
- Revive qemu-system-{ppc*, sparc*} (bz 844502)
- Enable KVM support for all targets (bz 844503)

* Mon Aug 06 2012 Cole Robinson <crobinso@redhat.com> - 1.2-0.1.20120806git3e430569.fc18
- Update to git snapshot

* Sun Jul 29 2012 Cole Robinson <crobinso@redhat.com> - 1.1.1-1
- Upstream stable release 1.1.1
- Fix systemtap tapsets (bz 831763)
- Fix VNC audio tunnelling (bz 840653)
- Don't renable ksm on update (bz 815156)
- Bump usbredir dep (bz 812097)
- Fix RPM install error on non-virt machines (bz 660629)
- Obsolete openbios to fix upgrade dependency issues (bz 694802)

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2:1.1.0-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 10 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.1.0-8
- Re-diff previous patch so that it applies and actually apply it

* Tue Jul 10 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.1.0-7
- Add patch to fix default machine options.  This fixes libvirt
  detection of qemu.
- Back out patch 1 which conflicts.

* Fri Jul  6 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.1.0-5
- Fix qemu crashing (on an assert) whenever USB-2.0 isoc transfers are used

* Thu Jul  5 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.1.0-4
- Disable tests since they hang intermittently.
- Add kvmvapic.bin (replaces vapic.bin).
- Add cpus-x86_64.conf.  qemu now creates /etc/qemu/target-x86_64.conf
  as an empty file.
- Add qemu-icon.bmp.
- Add qemu-bridge-helper.
- Build and include virtfs-proxy-helper + man page (thanks Hans de Goede).

* Wed Jul  4 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.1.0-1
- New upstream release 1.1.0
- Drop about a 100 spice + USB patches, which are all upstream

* Mon Apr 23 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.0-17
- Fix install failure due to set -e (rhbz #815272)

* Mon Apr 23 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.0-16
- Fix kvm.modules to exit successfully on non-KVM capable systems (rhbz #814932)

* Thu Apr 19 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.0-15
- Add a couple of backported QXL/Spice bugfixes
- Add spice volume control patches

* Fri Apr 6 2012 Paolo Bonzini <pbonzini@redhat.com> - 2:1.0-12
- Add back PPC and SPARC user emulators
- Update binfmt rules from upstream

* Mon Apr  2 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.0-11
- Some more USB bugfixes from upstream

* Thu Mar 29 2012 Eduardo Habkost <ehabkost@redhat.com> - 2:1.0-12
- Fix ExclusiveArch mistake that disabled all non-x86_64 builds on Fedora

* Wed Mar 28 2012 Eduardo Habkost <ehabkost@redhat.com> - 2:1.0-11
- Use --with variables for build-time settings

* Wed Mar 28 2012 Daniel P. Berrange <berrange@redhat.com> - 2:1.0-10
- Switch to use iPXE for netboot ROMs

* Thu Mar 22 2012 Daniel P. Berrange <berrange@redhat.com> - 2:1.0-9
- Remove O_NOATIME for 9p filesystems

* Mon Mar 19 2012 Daniel P. Berrange <berrange@redhat.com> - 2:1.0-8
- Move udev rules to /lib/udev/rules.d (rhbz #748207)

* Fri Mar  9 2012 Hans de Goede <hdegoede@redhat.com> - 2:1.0-7
- Add a whole bunch of USB bugfixes from upstream

* Mon Feb 13 2012 Daniel P. Berrange <berrange@redhat.com> - 2:1.0-6
- Add many more missing BRs for misc QEMU features
- Enable running of test suite during build

* Tue Feb 07 2012 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-5
- Add support for virtio-scsi

* Sun Feb  5 2012 Richard W.M. Jones <rjones@redhat.com> - 2:1.0-4
- Require updated ceph for latest librbd with rbd_flush symbol.

* Tue Jan 24 2012 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-3
- Add support for vPMU
- e1000: bounds packet size against buffer size CVE-2012-0029

* Fri Jan 13 2012 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-2
- Add patches for USB redirect bits
- Remove palcode-clipper, we don't build it

* Wed Jan 11 2012 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-1
- Add patches from 1.0.1 queue

* Fri Dec 16 2011 Justin M. Forbes <jforbes@redhat.com> - 2:1.0-1
- Update to qemu 1.0

* Tue Nov 15 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.1-3
- Enable spice for i686 users as well

* Thu Nov 03 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.1-2
- Fix POSTIN scriplet failure (#748281)

* Fri Oct 21 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.1-1
- Require seabios-bin >= 0.6.0-2 (#741992)
- Replace init scripts with systemd units (#741920)
- Update to 0.15.1 stable upstream
  
* Fri Oct 21 2011 Paul Moore <pmoore@redhat.com>
- Enable full relro and PIE (rhbz #738812)

* Wed Oct 12 2011 Daniel P. Berrange <berrange@redhat.com> - 2:0.15.0-6
- Add BR on ceph-devel to enable RBD block device

* Wed Oct  5 2011 Daniel P. Berrange <berrange@redhat.com> - 2:0.15.0-5
- Create a qemu-guest-agent sub-RPM for guest installation

* Tue Sep 13 2011 Daniel P. Berrange <berrange@redhat.com> - 2:0.15.0-4
- Enable DTrace tracing backend for SystemTAP (rhbz #737763)
- Enable build with curl (rhbz #737006)

* Thu Aug 18 2011 Hans de Goede <hdegoede@redhat.com> - 2:0.15.0-3
- Add missing BuildRequires: usbredir-devel, so that the usbredir code
  actually gets build

* Thu Aug 18 2011 Richard W.M. Jones <rjones@redhat.com> - 2:0.15.0-2
- Add upstream qemu patch 'Allow to leave type on default in -machine'
  (2645c6dcaf6ea2a51a3b6dfa407dd203004e4d11).

* Sun Aug 14 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.0-1
- Update to 0.15.0 stable release.

* Thu Aug 04 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.0-0.3.201108040af4922
- Update to 0.15.0-rc1 as we prepare for 0.15.0 release

* Thu Aug  4 2011 Daniel P. Berrange <berrange@redhat.com> - 2:0.15.0-0.3.2011072859fadcc
- Fix default accelerator for non-KVM builds (rhbz #724814)

* Thu Jul 28 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.0-0.1.2011072859fadcc
- Update to 0.15.0-rc0 as we prepare for 0.15.0 release

* Tue Jul 19 2011 Hans de Goede <hdegoede@redhat.com> - 2:0.15.0-0.2.20110718525e3df
- Add support usb redirection over the network, see:
  http://fedoraproject.org/wiki/Features/UsbNetworkRedirection
- Restore chardev flow control patches

* Mon Jul 18 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.15.0-0.1.20110718525e3df
- Update to git snapshot as we prepare for 0.15.0 release

* Wed Jun 22 2011 Richard W.M. Jones <rjones@redhat.com> - 2:0.14.0-9
- Add BR libattr-devel.  This caused the -fstype option to be disabled.
  https://www.redhat.com/archives/libvir-list/2011-June/thread.html#01017

* Mon May  2 2011 Hans de Goede <hdegoede@redhat.com> - 2:0.14.0-8
- Fix a bug in the spice flow control patches which breaks the tcp chardev

* Tue Mar 29 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-7
- Disable qemu-ppc and qemu-sparc packages (#679179)

* Mon Mar 28 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-6
- Spice fixes for flow control.

* Tue Mar 22 2011 Dan Horák <dan[at]danny.cz> - 2:0.14.0-5
- be more careful when removing the -g flag on s390

* Fri Mar 18 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-4
- Fix thinko on adding the most recent patches.

* Wed Mar 16 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-3
- Fix migration issue with vhost
- Fix qxl locking issues for spice

* Wed Mar 02 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-2
- Re-enable sparc and cris builds

* Thu Feb 24 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-1
- Update to 0.14.0 release

* Fri Feb 11 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-0.1.20110210git7aa8c46
- Update git snapshot
- Temporarily disable qemu-cris and qemu-sparc due to build errors (to be resolved shorly)

* Tue Feb 08 2011 Justin M. Forbes <jforbes@redhat.com> - 2:0.14.0-0.1.20110208git3593e6b
- Update to 0.14.0 rc git snapshot
- Add virtio-net to modules

* Wed Nov  3 2010 Daniel P. Berrange <berrange@redhat.com> - 2:0.13.0-2
- Revert previous change
- Make qemu-common own the /etc/qemu directory
- Add /etc/qemu/target-x86_64.conf to qemu-system-x86 regardless
  of host architecture.

* Wed Nov 03 2010 Dan Horák <dan[at]danny.cz> - 2:0.13.0-2
- Remove kvm config file on non-x86 arches (part of #639471)
- Own the /etc/qemu directory

* Mon Oct 18 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-1
- Update to 0.13.0 upstream release
- Fixes for vhost
- Fix mouse in certain guests (#636887)
- Fix issues with WinXP guest install (#579348)
- Resolve build issues with S390 (#639471)
- Fix Windows XP on Raw Devices (#631591)

* Tue Oct 05 2010 jkeating - 2:0.13.0-0.7.rc1.1
- Rebuilt for gcc bug 634757

* Tue Sep 21 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.7.rc1
- Flip qxl pci id from unstable to stable (#634535)
- KSM Fixes from upstream (#558281)

* Tue Sep 14 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.6.rc1
- Move away from git snapshots as 0.13 is close to release
- Updates for spice 0.6

* Tue Aug 10 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.5.20100809git25fdf4a
- Fix typo in e1000 gpxe rom requires.
- Add links to newer vgabios

* Tue Aug 10 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.4.20100809git25fdf4a
- Disable spice on 32bit, it is not supported and buildreqs don't exist.

* Mon Aug 9 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.3.20100809git25fdf4a
- Updates from upstream towards 0.13 stable
- Fix requires on gpxe
- enable spice now that buildreqs are in the repository.
- ksmtrace has moved to a separate upstream package

* Tue Jul 27 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.2.20100727gitb81fe95
- add texinfo buildreq for manpages.

* Tue Jul 27 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.13.0-0.1.20100727gitb81fe95
- Update to 0.13.0 upstream snapshot
- ksm init fixes from upstream

* Tue Jul 20 2010 Dan Horák <dan[at]danny.cz> - 2:0.12.3-8
- Add avoid-llseek patch from upstream needed for building on s390(x)
- Don't use parallel make on s390(x)

* Tue Jun 22 2010 Amit Shah <amit.shah@redhat.com> - 2:0.12.3-7
- Add vvfat hardening patch from upstream (#605202)

* Fri Apr 23 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-6
- Change requires to the noarch seabios-bin
- Add ownership of docdir to qemu-common (#572110)
- Fix "Cannot boot from non-existent NIC" error when using virt-install (#577851)

* Thu Apr 15 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-5
- Update virtio console patches from upstream

* Thu Mar 11 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-4
- Detect cdrom via ioctl (#473154)
- re add increased buffer for USB control requests (#546483)

* Wed Mar 10 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-3
- Migration clear the fd in error cases (#518032)

* Tue Mar 09 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-2
- Allow builds --with x86only
- Add libaio-devel buildreq for aio support

* Fri Feb 26 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.3-1
- Update to 0.12.3 upstream
- vhost-net migration/restart fixes
- Add F-13 machine type
- virtio-serial fixes

* Tue Feb 09 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.2-6
- Add vhost net support.

* Thu Feb 04 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.2-5
- Avoid creating too large iovecs in multiwrite merge (#559717)
- Don't try to set max_kernel_pages during ksm init on newer kernels (#558281)
- Add logfile options for ksmtuned debug.

* Wed Jan 27 2010 Amit Shah <amit.shah@redhat.com> - 2:0.12.2-4
- Remove build dependency on iasl now that we have seabios

* Wed Jan 27 2010 Amit Shah <amit.shah@redhat.com> - 2:0.12.2-3
- Remove source target for 0.12.1.2

* Wed Jan 27 2010 Amit Shah <amit.shah@redhat.com> - 2:0.12.2-2
- Add virtio-console patches from upstream for the F13 VirtioSerial feature

* Mon Jan 25 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.2-1
- Update to 0.12.2 upstream

* Sun Jan 10 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.1.2-3
- Point to seabios instead of bochs, and add a requires for seabios

* Mon Jan  4 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.1.2-2
- Remove qcow2 virtio backing file patch

* Mon Jan  4 2010 Justin M. Forbes <jforbes@redhat.com> - 2:0.12.1.2-1
- Update to 0.12.1.2 upstream
- Remove patches included in upstream

* Fri Nov 20 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-12
- Fix a use-after-free crasher in the slirp code (#539583)
- Fix overflow in the parallels image format support (#533573)

* Wed Nov  4 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-11
- Temporarily disable preadv/pwritev support to fix data corruption (#526549)

* Tue Nov  3 2009 Justin M. Forbes <jforbes@redhat.com> - 2:0.11.0-10
- Default ksm and ksmtuned services on.

* Thu Oct 29 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-9
- Fix dropped packets with non-virtio NICs (#531419)

* Wed Oct 21 2009 Glauber Costa <gcosta@redhat.com> - 2:0.11.0-8
- Properly save kvm time registers (#524229)

* Mon Oct 19 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-7
- Fix potential segfault from too small MSR_COUNT (#528901)

* Fri Oct  9 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-6
- Fix fs errors with virtio and qcow2 backing file (#524734)
- Fix ksm initscript errors on kernel missing ksm (#527653)
- Add missing Requires(post): getent, useradd, groupadd (#527087)

* Tue Oct  6 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-5
- Add 'retune' verb to ksmtuned init script

* Mon Oct  5 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-4
- Use rtl8029 PXE rom for ne2k_pci, not ne (#526777)
- Also, replace the gpxe-roms-qemu pkg requires with file-based requires

* Thu Oct  1 2009 Justin M. Forbes <jmforbes@redhat.com> - 2:0.11.0-3
- Improve error reporting on file access (#524695)

* Mon Sep 28 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-2
- Fix pci hotplug to not exit if supplied an invalid NIC model (#524022)

* Mon Sep 28 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.11.0-1
- Update to 0.11.0 release
- Drop a couple of upstreamed patches

* Wed Sep 23 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-5
- Fix issue causing NIC hotplug confusion when no model is specified (#524022)

* Wed Sep 16 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-4
- Fix for KSM patch from Justin Forbes

* Wed Sep 16 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-3
- Add ksmtuned, also from Dan Kenigsberg
- Use %%_initddir macro

* Wed Sep 16 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-2
- Add ksm control script from Dan Kenigsberg

* Mon Sep  7 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.92-1
- Update to qemu-kvm-0.11.0-rc2
- Drop upstreamed patches
- extboot install now fixed upstream
- Re-place TCG init fix (#516543) with the one gone upstream

* Mon Sep  7 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.10.rc1
- Fix MSI-X error handling on older kernels (#519787)

* Fri Sep  4 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.9.rc1
- Make pulseaudio the default audio backend (#519540, #495964, #496627)

* Thu Aug 20 2009 Richard W.M. Jones <rjones@redhat.com> - 2:0.10.91-0.8.rc1
- Fix segfault when qemu-kvm is invoked inside a VM (#516543)

* Tue Aug 18 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.7.rc1
- Fix permissions on udev rules (#517571)

* Mon Aug 17 2009 Lubomir Rintel <lkundrak@v3.sk> - 2:0.10.91-0.6.rc1
- Allow blacklisting of kvm modules (#517866)

* Fri Aug  7 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.5.rc1
- Fix virtio_net with -net user (#516022)

* Tue Aug  4 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.4.rc1
- Update to qemu-kvm-0.11-rc1; no changes from rc1-rc0

* Tue Aug  4 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.3.rc1.rc0
- Fix extboot checksum (bug #514899)

* Fri Jul 31 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.2.rc1.rc0
- Add KSM support
- Require bochs-bios >= 2.3.8-0.8 for latest kvm bios updates

* Thu Jul 30 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.91-0.1.rc1.rc0
- Update to qemu-kvm-0.11.0-rc1-rc0
- This is a pre-release of the official -rc1
- A vista installer regression is blocking the official -rc1 release
- Drop qemu-prefer-sysfs-for-usb-host-devices.patch
- Drop qemu-fix-build-for-esd-audio.patch
- Drop qemu-slirp-Fix-guestfwd-for-incoming-data.patch
- Add patch to ensure extboot.bin is installed

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2:0.10.50-14.kvm88
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul 23 2009 Glauber Costa <glommer@redhat.com> - 2:0.10.50-13.kvm88
- Fix bug 513249, -net channel option is broken

* Thu Jul 16 2009 Daniel P. Berrange <berrange@redhat.com> - 2:0.10.50-12.kvm88
- Add 'qemu' user and group accounts
- Force disable xen until it can be made to build

* Thu Jul 16 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-11.kvm88
- Update to kvm-88, see http://www.linux-kvm.org/page/ChangeLog
- Package mutiboot.bin
- Update for how extboot is built
- Fix sf.net source URL
- Drop qemu-fix-ppc-softmmu-kvm-disabled-build.patch
- Drop qemu-fix-pcspk-build-with-kvm-disabled.patch
- Cherry-pick fix for esound support build failure

* Wed Jul 15 2009 Daniel Berrange <berrange@lettuce.camlab.fab.redhat.com> - 2:0.10.50-10.kvm87
- Add udev rules to make /dev/kvm world accessible & group=kvm (rhbz #497341)
- Create a kvm group if it doesn't exist (rhbz #346151)

* Tue Jul 07 2009 Glauber Costa <glommer@redhat.com> - 2:0.10.50-9.kvm87
- use pxe roms from gpxe, instead of etherboot package.

* Fri Jul  3 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-8.kvm87
- Prefer sysfs over usbfs for usb passthrough (#508326)

* Sat Jun 27 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-7.kvm87
- Update to kvm-87
- Drop upstreamed patches
- Cherry-pick new ppc build fix from upstream
- Work around broken linux-user build on ppc
- Fix hw/pcspk.c build with --disable-kvm
- Re-enable preadv()/pwritev() since #497429 is long since fixed
- Kill petalogix-s3adsp1800.dtb, since we don't ship the microblaze target

* Fri Jun  5 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-6.kvm86
- Fix 'kernel requires an x86-64 CPU' error
- BuildRequires ncurses-devel to enable '-curses' option (#504226)

* Wed Jun  3 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-5.kvm86
- Prevent locked cdrom eject - fixes hang at end of anaconda installs (#501412)
- Avoid harmless 'unhandled wrmsr' warnings (#499712)

* Thu May 21 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-4.kvm86
- Update to kvm-86 release
- ChangeLog here: http://marc.info/?l=kvm&m=124282885729710

* Fri May  1 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-3.kvm85
- Really provide qemu-kvm as a metapackage for comps

* Tue Apr 28 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-2.kvm85
- Provide qemu-kvm as a metapackage for comps

* Mon Apr 27 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10.50-1.kvm85
- Update to qemu-kvm-devel-85
- kvm-85 is based on qemu development branch, currently version 0.10.50
- Include new qemu-io utility in qemu-img package
- Re-instate -help string for boot=on to fix virtio booting with libvirt
- Drop upstreamed patches
- Fix missing kernel/include/asm symlink in upstream tarball
- Fix target-arm build
- Fix build on ppc
- Disable preadv()/pwritev() until bug #497429 is fixed
- Kill more .kernelrelease uselessness
- Make non-kvm qemu build verbose

* Fri Apr 24 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-15
- Fix source numbering typos caused by make-release addition

* Thu Apr 23 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-14
- Improve instructions for generating the tarball

* Tue Apr 21 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-13
- Enable pulseaudio driver to fix qemu lockup at shutdown (#495964)

* Tue Apr 21 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-12
- Another qcow2 image corruption fix (#496642)

* Mon Apr 20 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-11
- Fix qcow2 image corruption (#496642)

* Sun Apr 19 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-10
- Run sysconfig.modules from %%post on x86_64 too (#494739)

* Sun Apr 19 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-9
- Align VGA ROM to 4k boundary - fixes 'qemu-kvm -std vga' (#494376)

* Tue Apr  14 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-8
- Provide qemu-kvm conditional on the architecture.

* Thu Apr  9 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-7
- Add a much cleaner fix for vga segfault (#494002)

* Sun Apr  5 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-6
- Fixed qcow2 segfault creating disks over 2TB. #491943

* Fri Apr  3 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-5
- Fix vga segfault under kvm-autotest (#494002)
- Kill kernelrelease hack; it's not needed
- Build with "make V=1" for more verbose logs

* Thu Apr 02 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-4
- Support botting gpxe roms.

* Wed Apr 01 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-2
- added missing patch. love for CVS.

* Wed Apr 01 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-1
- Include debuginfo for qemu-img
- Do not require qemu-common for qemu-img
- Explicitly own each of the firmware files
- remove firmwares for ppc and sparc. They should be provided by an external package.
  Not that the packages exists for sparc in the secondary arch repo as noarch, but they
  don't automatically get into main repos. Unfortunately it's the best we can do right
  now.
- rollback a bit in time. Snapshot from avi's maint/2.6.30
  - this requires the sasl patches to come back.
  - with-patched-kernel comes back.

* Wed Mar 25 2009 Mark McLoughlin <markmc@redhat.com> - 2:0.10-0.12.kvm20090323git
- BuildRequires pciutils-devel for device assignment (#492076)

* Mon Mar 23 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.11.kvm20090323git
- Update to snapshot kvm20090323.
- Removed patch2 (upstream).
- use upstream's new split package.
- --with-patched-kernel flag not needed anymore
- Tell how to get the sources.

* Wed Mar 18 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.10.kvm20090310git
- Added extboot to files list.

* Wed Mar 11 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.9.kvm20090310git
- Fix wrong reference to bochs bios.

* Wed Mar 11 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.8.kvm20090310git
- fix Obsolete/Provides pair
- Use kvm bios from bochs-bios package.
- Using RPM_OPT_FLAGS in configure
- Picked back audio-drv-list from kvm package

* Tue Mar 10 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.7.kvm20090310git
- modify ppc patch

* Tue Mar 10 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.6.kvm20090310git
- updated to kvm20090310git
- removed sasl patches (already in this release)

* Tue Mar 10 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.5.kvm20090303git
- kvm.modules were being wrongly mentioned at %%install.
- update description for the x86 system package to include kvm support
- build kvm's own bios. It is still necessary while kvm uses a slightly different
  irq routing mechanism

* Thu Mar 05 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.4.kvm20090303git
- seems Epoch does not go into the tags. So start back here.

* Thu Mar 05 2009 Glauber Costa <glommer@redhat.com> - 2:0.10-0.1.kvm20090303git
- Use bochs-bios instead of bochs-bios-data
- It's official: upstream set on 0.10

* Thu Mar  5 2009 Daniel P. Berrange <berrange@redhat.com> - 2:0.9.2-0.2.kvm20090303git
- Added BSD to license list, since many files are covered by BSD

* Wed Mar 04 2009 Glauber Costa <glommer@redhat.com> - 0.9.2-0.1.kvm20090303git
- missing a dot. shame on me

* Wed Mar 04 2009 Glauber Costa <glommer@redhat.com> - 0.92-0.1.kvm20090303git
- Set Epoch to 2
- Set version to 0.92. It seems upstream keep changing minds here, so pick the lowest
- Provides KVM, Obsoletes KVM
- Only install qemu-kvm in ix86 and x86_64
- Remove pkgdesc macros, as they were generating bogus output for rpm -qi.
- fix ppc and ppc64 builds

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 0.10-0.3.kvm20090303git
- only execute post scripts for user package.
- added kvm tools.

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 0.10-0.2.kvm20090303git
- put kvm.modules into cvs

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 0.10-0.1.kvm20090303git
- Set Epoch to 1
- Build KVM (basic build, no tools yet)
- Set ppc in ExcludeArch. This is temporary, just to fix one issue at a time.
  ppc users (IBM ? ;-)) please wait a little bit.

* Tue Mar  3 2009 Daniel P. Berrange <berrange@redhat.com> - 1.0-0.5.svn6666
- Support VNC SASL authentication protocol
- Fix dep on bochs-bios-data

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 1.0-0.4.svn6666
- use bios from bochs-bios package.

* Tue Mar 03 2009 Glauber Costa <glommer@redhat.com> - 1.0-0.3.svn6666
- use vgabios from vgabios package.

* Mon Mar 02 2009 Glauber Costa <glommer@redhat.com> - 1.0-0.2.svn6666
- use pxe roms from etherboot package.

* Mon Mar 02 2009 Glauber Costa <glommer@redhat.com> - 1.0-0.1.svn6666
- Updated to tip svn (release 6666). Featuring split packages for qemu.
  Unfortunately, still using binary blobs for the bioses.

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.1-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Jan 11 2009 Debarshi Ray <rishi@fedoraproject.org> - 0.9.1-12
- Updated build patch. Closes Red Hat Bugzilla bug #465041.

* Wed Dec 31 2008 Dennis Gilmore <dennis@ausil.us> - 0.9.1-11
- add sparcv9 and sparc64 support

* Fri Jul 25 2008 Bill Nottingham <notting@redhat.com>
- Fix qemu-img summary (#456344)

* Wed Jun 25 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-10.fc10
- Rebuild for GNU TLS ABI change

* Wed Jun 11 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-9.fc10
- Remove bogus wildcard from files list (rhbz #450701)

* Sat May 17 2008 Lubomir Rintel <lkundrak@v3.sk> - 0.9.1-8
- Register binary handlers also for shared libraries

* Mon May  5 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-7.fc10
- Fix text console PTYs to be in rawmode

* Sun Apr 27 2008 Lubomir Kundrak <lkundrak@redhat.com> - 0.9.1-6
- Register binary handler for SuperH-4 CPU

* Wed Mar 19 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-5.fc9
- Split qemu-img tool into sub-package for smaller footprint installs

* Wed Feb 27 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-4.fc9
- Fix block device checks for extendable disk formats (rhbz #435139)

* Sat Feb 23 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-3.fc9
- Fix block device extents check (rhbz #433560)

* Mon Feb 18 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.9.1-2
- Autorebuild for GCC 4.3

* Tue Jan  8 2008 Daniel P. Berrange <berrange@redhat.com> - 0.9.1-1.fc9
- Updated to 0.9.1 release
- Fix license tag syntax
- Don't mark init script as a config file

* Wed Sep 26 2007 Daniel P. Berrange <berrange@redhat.com> - 0.9.0-5.fc8
- Fix rtl8139 checksum calculation for Vista (rhbz #308201)

* Tue Aug 28 2007 Daniel P. Berrange <berrange@redhat.com> - 0.9.0-4.fc8
- Fix debuginfo by passing -Wl,--build-id to linker

* Tue Aug 28 2007 David Woodhouse <dwmw2@infradead.org> 0.9.0-4
- Update licence
- Fix CDROM emulation (#253542)

* Tue Aug 28 2007 Daniel P. Berrange <berrange@redhat.com> - 0.9.0-3.fc8
- Added backport of VNC password auth, and TLS+x509 cert auth
- Switch to rtl8139 NIC by default for linkstate reporting
- Fix rtl8139 mmio region mappings with multiple NICs

* Sun Apr  1 2007 Hans de Goede <j.w.r.degoede@hhs.nl> 0.9.0-2
- Fix direct loading of a linux kernel with -kernel & -initrd (bz 234681)
- Remove spurious execute bits from manpages (bz 222573)

* Tue Feb  6 2007 David Woodhouse <dwmw2@infradead.org> 0.9.0-1
- Update to 0.9.0

* Wed Jan 31 2007 David Woodhouse <dwmw2@infradead.org> 0.8.2-5
- Include licences

* Mon Nov 13 2006 Hans de Goede <j.w.r.degoede@hhs.nl> 0.8.2-4
- Backport patch to make FC6 guests work by Kevin Kofler
  <Kevin@tigcc.ticalc.org> (bz 207843).

* Mon Sep 11 2006 David Woodhouse <dwmw2@infradead.org> 0.8.2-3
- Rebuild

* Thu Aug 24 2006 Matthias Saou <http://freshrpms.net/> 0.8.2-2
- Remove the target-list iteration for x86_64 since they all build again.
- Make gcc32 vs. gcc34 conditional on %%{fedora} to share the same spec for
  FC5 and FC6.

* Wed Aug 23 2006 Matthias Saou <http://freshrpms.net/> 0.8.2-1
- Update to 0.8.2 (#200065).
- Drop upstreamed syscall-macros patch2.
- Put correct scriplet dependencies.
- Force install mode for the init script to avoid umask problems.
- Add %%postun condrestart for changes to the init script to be applied if any.
- Update description with the latest "about" from the web page (more current).
- Update URL to qemu.org one like the Source.
- Add which build requirement.
- Don't include texi files in %%doc since we ship them in html.
- Switch to using gcc34 on devel, FC5 still has gcc32.
- Add kernheaders patch to fix linux/compiler.h inclusion.
- Add target-sparc patch to fix compiling on ppc (some int32 to float).

* Thu Jun  8 2006 David Woodhouse <dwmw2@infradead.org> 0.8.1-3
- More header abuse in modify_ldt(), change BuildRoot:

* Wed Jun  7 2006 David Woodhouse <dwmw2@infradead.org> 0.8.1-2
- Fix up kernel header abuse

* Tue May 30 2006 David Woodhouse <dwmw2@infradead.org> 0.8.1-1
- Update to 0.8.1

* Sat Mar 18 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-6
- Update linker script for PPC

* Sat Mar 18 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-5
- Just drop $RPM_OPT_FLAGS. They're too much of a PITA

* Sat Mar 18 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-4
- Disable stack-protector options which gcc 3.2 doesn't like

* Fri Mar 17 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-3
- Use -mcpu= instead of -mtune= on x86_64 too
- Disable SPARC targets on x86_64, because dyngen doesn't like fnegs

* Fri Mar 17 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-2
- Don't use -mtune=pentium4 on i386. GCC 3.2 doesn't like it

* Fri Mar 17 2006 David Woodhouse <dwmw2@infradead.org> 0.8.0-1
- Update to 0.8.0
- Resort to using compat-gcc-32
- Enable ALSA

* Mon May 16 2005 David Woodhouse <dwmw2@infradead.org> 0.7.0-2
- Proper fix for GCC 4 putting 'blr' or 'ret' in the middle of the function,
  for i386, x86_64 and PPC.

* Sat Apr 30 2005 David Woodhouse <dwmw2@infradead.org> 0.7.0-1
- Update to 0.7.0
- Fix dyngen for PPC functions which end in unconditional branch

* Thu Apr  7 2005 Michael Schwendt <mschwendt[AT]users.sf.net>
- rebuilt

* Sun Feb 13 2005 David Woodhouse <dwmw2@infradead.org> 0.6.1-2
- Package cleanup

* Sun Nov 21 2004 David Woodhouse <dwmw2@redhat.com> 0.6.1-1
- Update to 0.6.1

* Tue Jul 20 2004 David Woodhouse <dwmw2@redhat.com> 0.6.0-2
- Compile fix from qemu CVS, add x86_64 host support

* Wed May 12 2004 David Woodhouse <dwmw2@redhat.com> 0.6.0-1
- Update to 0.6.0.

* Sat May 8 2004 David Woodhouse <dwmw2@redhat.com> 0.5.5-1
- Update to 0.5.5.

* Sun May 2 2004 David Woodhouse <dwmw2@redhat.com> 0.5.4-1
- Update to 0.5.4.

* Thu Apr 22 2004 David Woodhouse <dwmw2@redhat.com> 0.5.3-1
- Update to 0.5.3. Add init script.

* Thu Jul 17 2003 Jeff Johnson <jbj@redhat.com> 0.4.3-1
- Create.
