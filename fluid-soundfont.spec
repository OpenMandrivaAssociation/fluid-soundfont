%define patch_pkg_version 2

Summary:	Pro-quality GM/GS soundfont
Name:		fluid-soundfont
Version:	3.1
Release:	9
Group:		Sound
License:	MIT
Url:		http://www.hammersound.com/cgi-bin/soundlink.pl?action=view_category&category=Collections&ListStart=0&ListLength=20
# The Hammersound source gives us a soundfont in a linux-unfriendly .sfArk format. 
# In order to convert this to a linux-friendly .sf2 format one needs to use a 
# non-free utility sfarkxtc from 
#    http://www.melodymachine.com
# This page explains how this conversion is done:
#    http://vsr.informatik.tu-chemnitz.de/staff/jan/nted/doc/ch01s46.html
# Debian folks already did this and we will borrow their source tarball:
Source0:	http://ftp.de.debian.org/debian/pool/main/f/%{name}/%{name}_%{version}.orig.tar.gz
# Some information about the soundfont that can be found in the Hammersound archive:
Source1:	Fluid_R3_Readme.pdf
Source2:	timidity-fluid.cfg
BuildArch:      noarch
BuildRequires:  soundfont-utils

%define common_description \
FluidR3 is the third release of Frank Wen's pro-quality GM/GS soundfont.\
The soundfont has lots of excellent samples, including all the GM instruments\
along side with the GS instruments that are recycled and reprogrammed versions\
of the GM presets.

%description
%common_description

%package common
Summary:        Common files for FluidR3 soundfont
Group:          Sound

%description common
%common_description

This package contains common files shared among all FluidR3 soundfont packages.

%package gm
Summary:        Pro-quality General Midi soundfont
Group:          Sound
Requires:       %{name}-common = %{version}-%{release}
Provides:       soundfont2
Provides:       soundfont2-default

%description gm
%common_description

This package contains Fluid General Midi (GM) soundfont in soundfont 2.0 (.sf2)
format.

%package gs
Summary:        Pro-quality General Standard Extension soundfont
Group:          Sound
Requires:       %{name}-common = %{version}-%{release}
Requires:       %{name}-gm = %{version}-%{release}
Provides:       soundfont2


%description gs
%common_description

This package contains instruments belonging to General Midi's General Standard
(GS) Extension in soundfont 2.0 (.sf2) format.

%package -n timidity-patch-fluid
Summary:        Pro-quality General Midi soundfont in GUS patch format
Group:          Sound
Requires:       %{name}-common = %{version}-%{release}
Obsoletes:	fluid-soundfont-lite-patches
Provides:	fluid-soundfont-lite-patches
Provides:	timidity-instruments = %{patch_pkg_version}
Obsoletes:	timidity-instruments

%description -n timidity-patch-fluid
%common_description

This package contains Fluid General Midi (GM) soundfont in Gravis Ultrasound
(GUS) patch (.pat) format.


%prep
%setup -q
cp -a %{SOURCE1} .

%build
unsf -v -s -m FluidR3_GM.sf2
unsf -v -s -m FluidR3_GS.sf2

# Cut the size of the patches subpackage:
for bank in GM-B{8,9,16} Standard{1,2,3,4,5,6,7} Room{1,2,3,4,5,6,7} Power{1,2,3} Jazz{1,2,3,4} Brush{1,2}; do
   sed -i "/$bank/d" FluidR3_GM.cfg
   rm -fr *$bank*
done

echo dir /usr/share/timidity/fluid > FluidR3.cfg
cat FluidR3_GM.cfg FluidR3_GS.cfg >> FluidR3.cfg

# The gus patches get used by a lot of different programs and some need the
# path to the patches to be absolute
#sed -i 's|FluidR3_GM-|%{_datadir}/soundfonts/%{name}-lite-patches/FluidR3_GM-|g' FluidR3.cfg
#sed -i 's|FluidR3_GS-|%{_datadir}/soundfonts/%{name}-lite-patches/FluidR3_GS-|g' FluidR3.cfg

%install
# The actual soundfonts:
mkdir -p %{buildroot}%{_datadir}/soundfonts
install -p -m 644 FluidR3_GM.sf2 %{buildroot}%{_datadir}/soundfonts
install -p -m 644 FluidR3_GS.sf2 %{buildroot}%{_datadir}/soundfonts
# Create a symlink to denote that this is the Mandriva default soundfont
ln -s FluidR3_GM.sf2 %{buildroot}%{_datadir}/soundfonts/default.sf2

# Gus patches:
mkdir -p %{buildroot}%{_sysconfdir}
mkdir -p %{buildroot}%{_datadir}/timidity/fluid
cp -a FluidR3_GM-* %{buildroot}%{_datadir}/timidity/fluid
cp -a FluidR3_GS-* %{buildroot}%{_datadir}/timidity/fluid
mkdir -p %{buildroot}%{_sysconfdir}/timidity/fluid
install -p -m 644 FluidR3.cfg %{buildroot}%{_sysconfdir}/timidity/fluid/FluidR3.cfg
install -m644 %{SOURCE2} -D %{buildroot}%{_sysconfdir}/timidity/timidity-fluid.cfg

%post -n timidity-patch-fluid
%{_sbindir}/update-alternatives --install %{_sysconfdir}/timidity/timidity.cfg timidity.cfg %{_sysconfdir}/timidity/timidity-fluid.cfg 40

%postun -n timidity-patch-fluid
if [ "$1" = "0" ]; then
  %{_sbindir}/update-alternatives --remove timidity.cfg %{_sysconfdir}/timidity/timidity-fluid.cfg
fi

%triggerpostun -- TiMidity++ <= 2.13.2-1mdk
%{_sbindir}/update-alternatives --install %{_sysconfdir}/timidity/timidity.cfg timidity.cfg %{_sysconfdir}/timidity/timidity-fluid.cfg 40

%files common
%doc COPYING README *Readme*
%dir %{_datadir}/soundfonts/

%files gm
%{_datadir}/soundfonts/FluidR3_GM.sf2
%{_datadir}/soundfonts/default.sf2

%files gs
%{_datadir}/soundfonts/FluidR3_GS.sf2

%files -n timidity-patch-fluid
%config %{_sysconfdir}/timidity/fluid/FluidR3.cfg
%config %{_sysconfdir}/timidity/timidity-fluid.cfg
%{_datadir}/timidity/fluid/

