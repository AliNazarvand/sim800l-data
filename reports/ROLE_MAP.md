# ROLE_MAP

Generated: 1405-07-18T18:12:39Z

| Dataset | Role | Depends on | Depended by | Status |
|---|---|---|---|---|
| dat_01 | Command reference | - | dat_02,03,09,10,11,12,13,17 | pending |
| dat_02 | URC reference | dat_01 | - | pending |
| dat_03 | Error codes | dat_01 | - | pending |
| dat_04 | Timings | HW PDFs | dat_05,06 | pending |
| dat_05 | State machine | HW/AT | dat_02,04,15 | pending |
| dat_06 | Init sequence | HW/AT | - | pending |
| dat_07 | Hardware | HW PDFs | dat_13,15,16 | pending |
| dat_08 | Firmware matrix | Release notes | - | pending |
| dat_09 | SMS | dat_01 | - | pending |
| dat_10 | GPRS/Data | dat_01 | dat_14 | pending |
| dat_11 | HTTP/FTP/SSL | dat_01 | dat_17 | pending |
| dat_12 | Audio | dat_01 | - | pending |
| dat_13 | SIM mgmt | dat_01, dat_07 | - | pending |
| dat_14 | MCC/MNC | external | dat_10 | deferred |
| dat_15 | Power | HW PDFs | dat_05 | pending |
| dat_16 | Board/EVB | EVB doc | dat_07 | pending |
| dat_17 | Cert/Key | dat_01, dat_11 | - | pending |
| dat_18 | Certification | external | - | pending |