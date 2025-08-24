#
# Conditional build:
%bcond_without	apidocs		# API documentation
#
Summary:	Block device I/O library
Summary(pl.UTF-8):	Bibliotek we/wy urządzeń blokowych
Name:		libblkio
Version:	1.5.0
Release:	1
License:	MIT or Apache v2.0 (+crates: Apache v2.0 or BSD, MIT, BSD, Unicode DFS 2016)
Group:		Libraries
#Source0Download: https://gitlab.com/libblkio/libblkio/tags
Source0:	https://gitlab.com/libblkio/libblkio/-/archive/v%{version}/%{name}-%{version}.tar.bz2
# Source0-md5:	7e8b856a816ac455412e8cfcb84208f8
Source1:	%{name}-%{version}-vendor.tar.xz
# Source1-md5:	edb2442b5a2659ae5d938feaf191d411
URL:		https://gitlab.com/libblkio/libblkio
BuildRequires:	cargo
# rst2man
BuildRequires:	docutils
BuildRequires:	meson >= 0.61.0
BuildRequires:	ninja >= 1.5
BuildRequires:	python3
BuildRequires:	python3-tomli
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 2.042
BuildRequires:	rust >= 1.63
%{?with_apidocs:BuildRequires:	sphinx-pdg-3}
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
ExclusiveArch:	%{x8664} %{ix86} x32 aarch64 armv6hl armv7hl armv7hnl
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
libblkio is a library for high-performance block device I/O with
support for multi-queue devices. A C API is provided so that
applications can use the library from most programming languages.

%description -l pl.UTF-8
libblkio to biblioteka do wysoko wydajnego we/wy urządzeń blokowych z
obsługą urządzeń wielokolejkowych. Udostępnia API C, dzięki czemu
aplikacje mogą używać biblioteki z większości języków.

%package devel
Summary:	Header files for libblkio library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki libblkio
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Header files for libblkio library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki libblkio.

%package apidocs
Summary:	API documentation for libblkio library
Summary(pl.UTF-8):	Dokumentacja API biblioteki libblkio
Group:		Documentation
BuildArch:	noarch

%description apidocs
API documentation for libblkio library.

%description apidocs -l pl.UTF-8
Dokumentacja API biblioteki libblkio.

%prep
%setup -q -n %{name}-v%{version}-6635473bb919c8ff9446cfd3d96517b31410f4f8 -b1

%{__sed} -i -e '/^args=/ a args+=( --offline -v )' src/cargo-build.sh
%{__sed} -i -e 's/ -C debuginfo=. / %{rpmrustflags} /' src/cargo-build.sh
%ifarch x32
%{__sed} -i -e '/^args=/ a args+=( --target x86_64-unknown-linux-gnux32 )' src/cargo-build.sh
%{__sed} -i -e 's,/\${profile}/,/x86_64-unknown-linux-gnux32/\${profile}/,' src/cargo-build.sh
%endif

# use offline registry
export CARGO_HOME="$(pwd)/.cargo"
mkdir -p "$CARGO_HOME"
cat >.cargo/config <<EOF
[source.crates-io]
registry = 'https://github.com/rust-lang/crates.io-index'
replace-with = 'vendored-sources'

[source.vendored-sources]
directory = '$PWD/vendor'
EOF

%build
export CARGO_HOME="$(pwd)/.cargo"

%meson \
	--default-library=shared

%meson_build

%if %{with apidocs}
sphinx-build-3 -b html docs docs/_build/html
%endif

%install
rm -rf $RPM_BUILD_ROOT
export CARGO_HOME="$(pwd)/.cargo"

%meson_install

install -d $RPM_BUILD_ROOT%{_examplesdir}
cp -pr examples $RPM_BUILD_ROOT%{_examplesdir}/%{name}-%{version}

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc LICENSE-MIT LICENSE.crosvm README.rst
%attr(755,root,root) %{_libdir}/libblkio.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libblkio.so.1

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libblkio.so
%{_includedir}/blkio.h
%{_pkgconfigdir}/blkio.pc
%{_mandir}/man3/blkio.3*
%{_examplesdir}/%{name}-%{version}

%if %{with apidocs}
%files apidocs
%defattr(644,root,root,755)
%doc docs/_build/html/{_static,*.html,*.js}
%endif
