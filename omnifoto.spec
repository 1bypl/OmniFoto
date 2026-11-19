Name:           omnifoto
Version:        1.0.0
Release:        1%{?dist}
Summary:        Lokalna, prywatna przeglądarka i wyszukiwarka tapet

License:        GPL-3.0-or-later
URL:            https://github.com/1bypl
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel
Requires:       python3
Requires:       python3-pyside6
Recommends:     python3-pysocks

%description
OmniFoto to działająca lokalnie przeglądarka tapet z wyszukiwaniem w wielu
źródłach, podglądem, pokazem slajdów, ulubionymi, motywami i trybem prywatnym.
Nie śledzi użytkownika, nie wyświetla reklam i jest udostępniana na GPL-3.0.

%prep
%setup -q

%build
%{__python3} -m compileall -q omnifoto || :

%install
mkdir -p %{buildroot}%{python3_sitelib}
cp -a omnifoto %{buildroot}%{python3_sitelib}/

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/omnifoto <<'EOF'
#!/usr/bin/python3
from omnifoto.app import main
raise SystemExit(main())
EOF
chmod 0755 %{buildroot}%{_bindir}/omnifoto

install -Dm644 packaging/omnifoto.desktop \
    %{buildroot}%{_datadir}/applications/omnifoto.desktop
install -Dm644 omnifoto/assets/app_icon.svg \
    %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/omnifoto.svg

%files
%license LICENSE
%doc README.md info.txt
%{python3_sitelib}/omnifoto/
%{_bindir}/omnifoto
%{_datadir}/applications/omnifoto.desktop
%{_datadir}/icons/hicolor/scalable/apps/omnifoto.svg

%changelog
* Thu Nov 19 2026 1bypl <1bypl@users.noreply.github.com> - 1.0.0-1
- Pierwsze wydanie OmniFoto
