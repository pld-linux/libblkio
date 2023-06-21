#
# Conditional build:
%bcond_without	apidocs		# API documentation
#
Summary:	Block device I/O library
Summary(pl.UTF-8):	Bibliotek we/wy urządzeń blokowych
Name:		libblkio
Version:	1.3.0
Release:	1
License:	MIT or Apache v2.0 (+crates: Apache v2.0 or BSD, MIT, BSD, Unicode DFS 2016)
Group:		Libraries
#Source0Download: https://gitlab.com/libblkio/libblkio/tags
Source0:	https://gitlab.com/libblkio/libblkio/-/archive/v%{version}/%{name}-%{version}.tar.bz2
# Source0-md5:	34397d6a333eb05b82d3388194d237be
Source1:	%{name}-%{version}-vendor.tar.xz
# Source1-md5:	6b44c3d7fc4fd5a2d411da95e89f28b3
URL:		https://gitlab.com/libblkio/libblkio
BuildRequires:	cargo
# rst2man
BuildRequires:	docutils
BuildRequires:	meson
BuildRequires:	ninja >= 1.5
BuildRequires:	python3
BuildRequires:	rpm-build >= 4.6
BuildRequires:	rpmbuild(macros) >= 1.736
BuildRequires:	rust >= 1.56
%{?with_apidocs:BuildRequires:	sphinx-pdg-3}
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
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
%setup -q -n %{name}-v%{version}-f64bb10aa28ba2d30d1803eeb54179ef0ee0ba80 -b1

%{__sed} -i -e '/^args=/ a args+=( --offline -v )' src/cargo-build.sh
%ifarch x32
%{__sed} -i -e '/^args=/ a args+=( --target x86_64-unknown-linux-gnux32 )' src/cargo-build.sh
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

%meson build

%ninja_build -C build

%if %{with apidocs}
sphinx-build-3 -b html docs docs/_build/html
%endif

%install
rm -rf $RPM_BUILD_ROOT
export CARGO_HOME="$(pwd)/.cargo"

%ninja_install -C build

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
