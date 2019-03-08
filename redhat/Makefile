include Makefile.common

rh-brew rh-env-prep: SRPM_NAME=$(NAME)-$(VERSION)$(RELEASE_SEPARATOR)$(RELEASE)$(DIST).$(ZRELEASE)
rh-brew: BUILD_TARGET=rhel-8.0-candidate

REDHAT:=$(shell pwd)
SCRIPTS:=$(REDHAT)/scripts
RPMBUILD:=$(REDHAT)/rpmbuild

# Hide command calls without debug option
ifeq ($(DEBUG),1)
  DS=
else
  DS=@
endif

BREW_OPTIONS:=$(BREW_FLAGS) --scratch

# Hide progress bar in scripts
ifeq ($(NOPROGRESS),1)
  BREW_OPTIONS:=$(BREW_OPTIONS) --noprogress
endif

# Do not wait for build finish
ifeq ($(NOWAIT),1)
  BREW_OPTIONS:=$(BREW_OPTIONS) --nowait
endif

# create an empty localversion file if you don't want a local buildid
ifneq ($(NOLOCALVERSION),1)
  ifeq ($(LOCALVERSION),)
    LOCALVERSION=$(shell cat ../localversion 2>/dev/null)
  endif
  ifeq ($(LOCALVERSION),)
    LOCALVERSION:=.$(shell id -u -n)$(shell date +"%Y%m%d%H%M")
  else
    LOCALVERSION:=.$(LOCALVERSION)
  endif
else
  LOCALVERSION:=
endif

.PHONY: rh-brew rh-srpm rh-prep rh-help rh-clean-sources
all: rh-help

rh-clean-sources:
	$(DS)for i in $(RPMBUILD)/SOURCES/*; do \
		rm -f $$i; \
	done; \

rh-prep: rh-clean-sources
	$(DS)if [ -n "$(SOURCES_FILELIST)" ]; then \
		echo "Copying Sources: $(SOURCES_FILELIST)"; \
		cp $(SOURCES_FILELIST) $(RPMBUILD)/SOURCES; \
	fi
	$(DS)$(SCRIPTS)/process-patches.sh "$(SCRIPTS)" "$(NAME)" "$(VERSION)" "$(RELEASE)" "$(DATE)" "$(COMMIT)" "$(TARFILE)" "$(TARURL)" "$(SPECFILE)" "$(BUILD_DIR)" "$(MARKER)" "$(LOCALVERSION)" "$(ZRELEASE)"
	$(DS)if [ -n "$(TARSHA256)" -a -e $(REDHAT)/$(TARFILE) -a "`$(SCRIPTS)/tarball_checksum.sh $(TARFILE)`" != "$(TARSHA256)" ]; then \
        echo "$(TARFILE) sha256sum does not match (expected: $(TARSHA256))"; \
		exit 1; \
    fi

rh-srpm: rh-prep
	$(DS)rpmbuild --define "_sourcedir $(RPMBUILD)/SOURCES" --define "_builddir $(RPMBUILD)/BUILD" --define "_srcrpmdir $(RPMBUILD)/SRPMS" --define "_rpmdir $(RPMBUILD)/RPMS" --define "_specdir $(RPMBUILD)/SPECS" --define "dist $(DIST)" --nodeps -bs $(RPMBUILD)/SPECS/$(SPECFILE)

rh-brew: rh-srpm
	@echo "Build $(SRPM_NAME)$(LOCALVERSION).src.rpm as $(BUILD_TARGET)"
	$(DS)brew build $(BREW_OPTIONS) $(BUILD_TARGET) $(RPMBUILD)/SRPMS/$(SRPM_NAME)$(LOCALVERSION).src.rpm
rh-env-prep: rh-prep
	$(DS)sudo dnf builddep $(RPMBUILD)/SPECS/$(SPECFILE)
	$(DS)cd ..; $(shell rpmspec -P $(RPMBUILD)/SPECS/$(SPECFILE) | scripts/extract_build_cmd.py | \
	              sed "s/--disable-git-update/--enable-git-update/g")

rh-local: rh-env-prep
	make V=1 -j8 -C $(REDHAT)/..  VL_LDFLAGS=-Wl,--build-id

rh-help:
	@echo "rh-brew: Build RHEL package on brew"
	@echo "rh-srpm: Prepare srpm package for RHEL package"
	@echo "rh-prep: Prepare sources and spec file in rpmbuild/"
	@echo "rh-help: Print this help"
	@echo "rh-env-prep: Install rpms required for redhat build and run configure"
	@echo "rh-local: Run local (non-rpm) build. Runs rh-env-prep on each call"
