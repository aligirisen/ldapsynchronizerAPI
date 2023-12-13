# Active Directory'den Openldap'a senkronizasyon aracı

Uygulamanın amacı aktif dizinde yer alan kullanıcıları ve bilgisayarları aynı zamanda kullanıcılar tarafından kullanılan politikaları ve grupları openldap tarafına geçirmektir.
Politikaları ve grupları oluşturur, yetkilerini aynı şekilde oluşturamaz. Gruplara ve politikalara yetki veya kısıtlama ekleyemez.

## Yükleme
- git clone https://github.com/aligirisen/ldapsynchronizerAPI.git
- Debian için
    - cd ldapsynchronizerAPI
    - dpkg-buildpackage -us -uc
    - cd .. && sudo dpkg -i syncapi_1.0-1_all.deb
- Uygulama yüklendiğinde sistem hizmeti olarak çalışmaya başlar 8000 portunu kullanır.

## Bağlantı Konfigürasyonu

- `/etc/syncapi/config/config.ini` dosyasından aktif dizin ve openldap sunucunuzun bilgilerini ve yetkili kullanıcının girileceği yer.

- Gereken bilgileri girdikten sonra test için `python3 /usr/bin/syncapi/manage.py test` yada (sistem hizmeti aktifken/api aktifken)`/syncapp/sync/test`


## Tercih Konfigürasyonu

- `/etc/syncapi/config/pref_config.ini` dosyası tercih konfigürasyonlarının olduğu yer.
- Tercihler:
    - `sync_directory = True` | aktif dizin tarafında var olup da openldap tarafında var olmayan dizinin oluşturulması.
    - `create_group = True` | aktif dizin tarafında var olup da openldap tarafında var olmayan grupların oluşturulması. (Ör: DnsAdmins)
    - `sync_computers = True` | bilgisayarların senkronize edilmesi.
    - **`ldap_group_dn = ou=Groups,dc=example,dc=com`** | grupların olduğu dizinin DN'i.
    - `ldap_clean_mode = True` | aktif dizinden silinmiş kullanıcıların openLDAP tarafından da silinmesi.
    - `ldap_clean_search_dn = ` | aktif dizinden silinmiş kullanıcıların openldap tarafında silineceği dizini belirtme opsiyonu. Belirli bir dizinde uygulamak için. ör : `ou=Istanbul,ou=Turkey,dc=example,dc=com`
    - `ldap_spec_directory_dn = ` | aktif dizindeki tüm ağacı openldap tarafında yeni bir dizinin içine atmak için kullanılır. ör: `ou=From Active Directory,dc=example,dc=com`
    - `time_zone = Europa/Istanbul` | işlemin başlangıç ve bitiş saatini dönerken kullannılır.
    - `ad_user_search_dn = ` | aktif dizindeki belli kullanıcıları güncellemek için. ör: `ou=IT Team,dc=example,dc=com`
    - `ad_computer_search_dn = ` | aktif dizindeki belli bilgisayarları güncellemek için. ör: `ou=Poland,dc=example,dc=com`
    


## Sadece kaynak kodu çalıştırmak
`python3 manage.py source`
 
`python3 manage.py source "input_dn"`

Test için : `python3 manage.py test`

## Örnek talep ve Uç Noktalar

- Senkronizasyondan sonra aktif dizinden silinmiş kullanıcıların openLDAP tarafından da silinmesi için gönderilen istek.

### Uç Nokta I
POST /syncapp/sync
```
{
    "ad_config": {
        "ad_server": "win.ornek.local",
        "ad_port": 389,
        "ad_username": "cn=Administrator,cn=Users,dc=ornek,dc=local",
        "ad_password": "123456A.",
        "ad_base_dn": "dc=ornek,dc=local"
    },
    "ldap_config": {
        "ldap_base_dn": "dc=ldap,dc=local",
        "ldap_server": "192.168.1.150",
        "ldap_admin_username": "cn=admin,dc=ldap,dc=com",
        "ldap_admin_password": "123456",
        "ldap_port": 389
    },
    "pref_config": {
        "ldap_clean_mode": True
    }
}
```
Tüm ağaç yerine bir kullanıcıyı güncellemek için DN'i girdi olarak kullanır
```
"input_dn": "cn=Ali Riza Girisen,ou=Users,dc=example,dc=com"
```

### Uç Nokta II
POST /syncapp/test
```
{
    "ad_config": {
        "ad_server": "win.ornek.local",
        "ad_port": 389,
        "ad_username": "cn=Administrator,cn=Users,dc=ornek,dc=local",
        "ad_password": "123456A.",
        "ad_base_dn": "dc=ornek,dc=local"
    },
    "ldap_config": {
        "ldap_base_dn": "dc=ldap,dc=local",
        "ldap_server": "192.168.1.150",
        "ldap_admin_username": "cn=admin,dc=ldap,dc=com",
        "ldap_admin_password": "123456",
        "ldap_port": 389
    }
}
```

### Uç Nokta III
GET /syncapp/sync/status
```
parametresiz
```