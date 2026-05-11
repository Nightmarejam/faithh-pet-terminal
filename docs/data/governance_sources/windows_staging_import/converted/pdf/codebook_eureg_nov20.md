# codebook_eureg_nov20.pdf

## Page 1

THE QOG EU REGIONAL DATASET
2020
CODEBOOK
Scholars who wish to use this dataset in their research are kindly requested to cite both the
original source (as stated in this codebook) and also use the following citation:
Charron, Nicholas, Stefan Dahlberg, Aksel Sundstr¨ om, S¨ oren Holmberg, Bo
Rothstein, Natalia Alvarado Pachon & Cem Mert Dalli. 2020. The Quality of
Government EU Regional Dataset, version Nov20. University of Gothenburg: The
Quality of Government Institute, https://www.gu.se/en/quality-government
https://www.gu.se/en/quality-government
The QoG Institute
P.O. Box 711
405 30 Gothenburg
Sweden
infoqog@pol.gu.se

## Page 2

Contents
1 Introduction 13
1.1 The Quality of Government Institute . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
1.2 The QoG EU Regional Data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 13
2 Data Structure 14
2.1 Data Structure . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 14
3 Variables by Category 16
3.1 Demographics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 16
3.2 Digital Society and Economy . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17
3.3 Economy . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 17
3.4 Education . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 18
3.5 Environment . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
3.6 Health . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 19
3.7 Labor Market Statistics . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 20
3.8 Poverty and Social Exclusion . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
3.9 Quality of Government . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
3.10 Science and Technology . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 22
3.11 Tourism . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
3.12 Transport . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
4 Variables by Original Source 26
4.1 Identication Variables . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26
4.1.1 Code of NUTS0 level region (nuts0) . . . . . . . . . . . . . . . . . . . . . . . 26
4.1.2 Code of NUTS1 level region (nuts1) . . . . . . . . . . . . . . . . . . . . . . . 26
4.1.3 Code of NUTS2 level region (nuts2) . . . . . . . . . . . . . . . . . . . . . . . 26
4.1.4 The Nomenclature of Territorial Units for Statistics (NUTS) level (level) . . 26
4.1.5 NUTS code of region (region code) . . . . . . . . . . . . . . . . . . . . . . . . 26
4.1.6 Name of the region (region name) . . . . . . . . . . . . . . . . . . . . . . . . 26
4.1.7 Name of the country in English (cname) . . . . . . . . . . . . . . . . . . . . . 26
4.1.8 Version of the Dataset (version) . . . . . . . . . . . . . . . . . . . . . . . . . . 26
4.1.9 Year (year) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26
4.2 European Quality of Government Index: European Quality of Government Index . . 27
4.2.1 EQI Index Score (eqi score) . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28
4.2.2 Quality pillar, country centered and z-score standardized (eqi zquality) . . . 28
4.2.3 Impartiality pillar, country centered and z-score standardized (eqi zimpar-
tiality) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 29
4.2.4 Corruption pillar, country centered and z-score standardized (eqi zcorruption) 30
4.2.5 Corruption perceptions index (corruption sub-pillar) z-score stand. (2017
only) (eqi zcorruptper) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30
4.2.6 Corruption experiences index (corruption sub-pillar) z-score stand. (2017
only) (eqi zcorruptexp) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 31
4.2.7 EQI index, min-max (0-100) standardized (eqi norm eqi) . . . . . . . . . . . 31
4.2.8 Quality pillar, country centered and min-max (0-100) standardized (eqi -
norm qual) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32
1

## Page 3

4.2.9 Impartiality pillar, country centered and min-max (0-100) standardized (eqi -
norm impart) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 32
4.2.10 Corruption pillar, country centered and min-max (0-100) standardized (eqi -
norm corrupt) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33
4.2.11 Corruption perceptions index (corruption sub-pillar) min-max (0-100)(2017)
(eqi norm corruptper) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 33
4.2.12 Corruption experiences index (corruption sub-pillar) min-max (0-100) (2017)
(eqi norm corruptexp) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 34
4.3 Corruption Risks Indicators: The Corruption Risks Indicators dataset . . . . . . . . 35
4.3.1 Number of awarded contracts above 130,000 EUR (cri contr) . . . . . . . . . 36
4.3.2 Final value of awarded tenders of over 130,000 EUR (cri cvalue) . . . . . . . 36
4.3.3 Share of contracts with only one bid in total (cri singleb) . . . . . . . . . . . 37
4.3.4 Share of contracts with no published call for tender redag (cri nocall) . . . 37
4.3.5 Share of contracts with non-open procedure redag (cri nonopen) . . . . . . 38
4.3.6 Share of contracts with tax haven redag (cri taxhav) . . . . . . . . . . . . . 38
4.4 Eurostat: Regional statistics by NUTS classication . . . . . . . . . . . . . . . . . . 39
4.4.1 Population at 1st January, female (eu d2jan f) . . . . . . . . . . . . . . . . . 40
4.4.2 Population at 1st January, male (eu d2jan m) . . . . . . . . . . . . . . . . . . 40
4.4.3 Population at 1st January, total (eu d2jan t) . . . . . . . . . . . . . . . . . . 41
4.4.4 Crude rate of net migration plus statistical adjustment (eu cnmigratrt) . . . 42
4.4.5 Crude rate of total population change (eu growrt) . . . . . . . . . . . . . . . 43
4.4.6 Crude rate of natural change of population (eu natgrowrt) . . . . . . . . . . . 43
4.4.7 Area of a region, land area total, sq km (eu d3area lat) . . . . . . . . . . . . 44
4.4.8 Area of a region, total, sq km (eu d3area t) . . . . . . . . . . . . . . . . . . . 44
4.4.9 Population density, average population per square km (eu per km2) . . . . . 45
4.4.10 Number of deaths of females, all ages (eu death totalf) . . . . . . . . . . . . . 45
4.4.11 Number of deaths of males, all ages (eu death totalm) . . . . . . . . . . . . . 46
4.4.12 Number of deaths, total all ages (eu death totalt) . . . . . . . . . . . . . . . 46
4.4.13 Number of deaths of females, at 1 year old (eu death y1f) . . . . . . . . . . . 47
4.4.14 Number of deaths of males, at 1 year old (eu death y1m) . . . . . . . . . . . 48
4.4.15 Number of deaths, total at 1 year old (eu death y1t) . . . . . . . . . . . . . . 48
4.4.16 Number of deaths of females, at 20 years old (eu death y20f) . . . . . . . . . 49
4.4.17 Number of deaths of males, at 20 years old (eu death y20m) . . . . . . . . . 49
4.4.18 Number of deaths, total at 20 years old (eu death y20t) . . . . . . . . . . . . 50
4.4.19 Number of deaths of females, at 50 years old (eu death y50f) . . . . . . . . . 50
4.4.20 Number of deaths of males, at 50 years old (eu death y50m) . . . . . . . . . 51
4.4.21 Number of deaths, total at 50 years old (eu death y50t) . . . . . . . . . . . . 51
4.4.22 Number of deaths of females, at 70 years old (eu death y70f) . . . . . . . . . 52
4.4.23 Number of deaths of males, at 70 years old (eu death y70m) . . . . . . . . . 52
4.4.24 Number of deaths, total at 70 years old (eu death y70t) . . . . . . . . . . . . 53
4.4.25 Fertility rate, total (eu frate total) . . . . . . . . . . . . . . . . . . . . . . . . 53
4.4.26 Fertility rate, at age 15 (eu frate y15) . . . . . . . . . . . . . . . . . . . . . . 54
4.4.27 Fertility rate, at age 30 (eu frate y30) . . . . . . . . . . . . . . . . . . . . . . 54
4.4.28 Fertility rate, at age 35 (eu frate y35) . . . . . . . . . . . . . . . . . . . . . . 55
4.4.29 Proportion of live births outside marriage (eu agemoth) . . . . . . . . . . . . 55
4.4.30 Total fertility rate (eu agemoth1) . . . . . . . . . . . . . . . . . . . . . . . . . 56
2

## Page 4

4.4.31 Mean age of women at childbirth (eu nmarpct) . . . . . . . . . . . . . . . . . 56
4.4.32 Mean age of women at birth ofrst child (eu totferrt) . . . . . . . . . . . . . 57
4.4.33 Life expectancy in years at 1 year old, female (eu mlifexp f) . . . . . . . . . . 57
4.4.34 Life expectancy in years at 1 year old, male (eu mlifexp m) . . . . . . . . . . 58
4.4.35 Life expectancy in years at 1 year old, total (eu mlifexp t) . . . . . . . . . . . 58
4.4.36 Business enterprise sector intramural expenditure in R&D, euro per inhabi-
tant (eu rdexp bes) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 59
4.4.37 Government sector intramural expenditure in R&D, euro per inhabitant (eu -
rdexp gov) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 59
4.4.38 Higher education sector intramural expenditure in R&D, euro per inhabitant
(eu rdexp hes) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 60
4.4.39 Private non-prot sector intramural expenditure in R&D, euro per inhabitant
(eu rdexp pnp) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 61
4.4.40 All sectors intramural expenditure in R&D, euro per inhabitant (eu rdexp total) 61
4.4.41 Total R&D employees in business enterprise sector, female, full-time equiva-
lent (eu prd bes f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 62
4.4.42 Total R&D employees in business enterprise sector, total, full-time equivalent
(eu prd bes t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 63
4.4.43 Total R&D employees in government sector, female, full-time equivalent (eu -
prd gov f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 64
4.4.44 Total R&D employees in government sector, total, full-time equivalent (eu -
prd gov t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 65
4.4.45 Total R&D employees in higher education sector, female, full-time equivalent
(eu prd hes f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 66
4.4.46 Total R&D employees in higher education sector, total, full-time equivalent
(eu prd hes t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 67
4.4.47 Total R&D employees in private non-prot sector, female, full-time equivalent
(eu prd pnp f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 68
4.4.48 Total R&D employees in private non-prot sector, total, full-time equivalent
(eu prd pnp t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 69
4.4.49 Total R&D employees in all sectors, female, full-time equivalent (eu prd -
total f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 70
4.4.50 Total R&D employees in all sectors, total, full-time equivalent (eu prd total t) 71
4.4.51 Employment in agriculture, forestry andshing; mining and quarrying, as
percentage of total employment, female (eu emtk ab f) . . . . . . . . . . . . . 72
4.4.52 Employment in agriculture, forestry andshing; mining and quarrying, as
percentage of total employment, male (eu emtk ab m) . . . . . . . . . . . . . 72
4.4.53 Employment in agriculture, forestry andshing; mining and quarrying, as
percentage of total employment, total (eu emtk ab t) . . . . . . . . . . . . . . 73
4.4.54 Employment in manufacturing, as percentage of total employment, female
(eu emtk c f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 74
4.4.55 Employment in manufacturing, as percentage of total employment, male (eu -
emtk c m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 74
4.4.56 Employment in manufacturing, as percentage of total employment, total (eu -
emtk c t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 75
3

## Page 5

4.4.57 Employment in high-technology manufacturing, as percentage of total em-
ployment, female (eu emtk chtc f) . . . . . . . . . . . . . . . . . . . . . . . . 76
4.4.58 Employment in high-technology manufacturing, as percentage of total em-
ployment, male (eu emtk chtc m) . . . . . . . . . . . . . . . . . . . . . . . . . 76
4.4.59 Employment in high-technology manufacturing, as percentage of total em-
ployment, total (eu emtk chtc t) . . . . . . . . . . . . . . . . . . . . . . . . . 77
4.4.60 Employment in electricity, gas, steam and air conditioning supply; water
supply and construction, as percentage of total employment, female (eu -
emtk df f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 78
4.4.61 Employment in electricity, gas, steam and air conditioning supply; water
supply and construction, as percentage of total employment, male (eu emtk -
df m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 78
4.4.62 Employment in electricity, gas, steam and air conditioning supply; water
supply and construction, as percentage of total employment, total (eu emtk -
df t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 79
4.4.63 Employment in services, as percentage of total employment, female (eu emtk -
gu f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 80
4.4.64 Employment in services, as percentage of total employment, male (eu emtk -
gu m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 80
4.4.65 Employment in services, as percentage of total employment, total (eu emtk -
gu t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 81
4.4.66 Employment in high-technology sectors (high-technology manufacturing and
knowledge-intensive high-technology services), as percentage of total employ-
ment, female (eu emtk htc f) . . . . . . . . . . . . . . . . . . . . . . . . . . . 82
4.4.67 Employment in high-technology sectors (high-technology manufacturing and
knowledge-intensive high-technology services), as percentage of total employ-
ment, male (eu emtk htc m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . 82
4.4.68 Employment in high-technology sectors (high-technology manufacturing and
knowledge-intensive high-technology services), as percentage of total employ-
ment, total (eu emtk htc t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . 83
4.4.69 Employment in information and communication, as percentage of total em-
ployment, female (eu emtk j f) . . . . . . . . . . . . . . . . . . . . . . . . . . 84
4.4.70 Employment in information and communication, as percentage of total em-
ployment, male (eu emtk j m) . . . . . . . . . . . . . . . . . . . . . . . . . . . 85
4.4.71 Employment in information and communication, as percentage of total em-
ployment, total (eu emtk j t) . . . . . . . . . . . . . . . . . . . . . . . . . . . 85
4.4.72 Employment innancial and insurance activities, as percentage of total em-
ployment, female (eu emtk k f) . . . . . . . . . . . . . . . . . . . . . . . . . . 86
4.4.73 Employment innancial and insurance activities, as percentage of total em-
ployment, male (eu emtk k m) . . . . . . . . . . . . . . . . . . . . . . . . . . 87
4.4.74 Employment innancial and insurance activities, as percentage of total em-
ployment, total (eu emtk k t) . . . . . . . . . . . . . . . . . . . . . . . . . . . 87
4.4.75 Employment in total knowledge-intensive services, as percentage of total em-
ployment, female (eu emtk kis f) . . . . . . . . . . . . . . . . . . . . . . . . . 88
4.4.76 Employment in total knowledge-intensive services, as percentage of total em-
ployment, male (eu emtk kis m) . . . . . . . . . . . . . . . . . . . . . . . . . 89
4

## Page 6

4.4.77 Employment in total knowledge-intensive services, as percentage of total em-
ployment, total (eu emtk kis t) . . . . . . . . . . . . . . . . . . . . . . . . . . 89
4.4.78 Employment innancial and insurance activities; real estate activities, as
percentage of total employment, female (eu emtk kl f) . . . . . . . . . . . . . 90
4.4.79 Employment innancial and insurance activities; real estate activities, as
percentage of total employment, male (eu emtk kl m) . . . . . . . . . . . . . 91
4.4.80 Employment innancial and insurance activities; real estate activities, as
percentage of total employment, total (eu emtk kl t) . . . . . . . . . . . . . . 91
4.4.81 Employment in professional, scientic and technical activities, as percentage
of total employment, female (eu emtk m f) . . . . . . . . . . . . . . . . . . . 92
4.4.82 Employment in professional, scientic and technical activities, as percentage
of total employment, male (eu emtk m m) . . . . . . . . . . . . . . . . . . . . 93
4.4.83 Employment in professional, scientic and technical activities, as percentage
of total employment, total (eu emtk m t) . . . . . . . . . . . . . . . . . . . . 93
4.4.84 Employment in administrative and support service activities, as percentage
of total employment, female (eu emtk n f) . . . . . . . . . . . . . . . . . . . . 94
4.4.85 Employment in administrative and support service activities, as percentage
of total employment, male (eu emtk n m) . . . . . . . . . . . . . . . . . . . . 95
4.4.86 Employment in administrative and support service activities, as percentage
of total employment, total (eu emtk n t) . . . . . . . . . . . . . . . . . . . . . 95
4.4.87 Employment in public administration; activities of extraterritorial organisa-
tions and bodies, as percentage of total employment, female (eu emtk ou f) . 96
4.4.88 Employment in public administration; activities of extraterritorial organisa-
tions and bodies, as percentage of total employment, male (eu emtk ou m) . 97
4.4.89 Employment in public administration; activities of extraterritorial organisa-
tions and bodies, as percentage of total employment, total (eu emtk ou t) . . 97
4.4.90 Employment in education, as percentage of total employment, female (eu -
emtk p f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 98
4.4.91 Employment in education, as percentage of total employment, male (eu -
emtk p m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 99
4.4.92 Employment in education, as percentage of total employment, total (eu -
emtk p t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 99
4.4.93 Employment in human health and social work activities, as percentage of
total employment, female (eu emtk q f) . . . . . . . . . . . . . . . . . . . . . 100
4.4.94 Employment in human health and social work activities, as percentage of
total employment, male (eu emtk q m) . . . . . . . . . . . . . . . . . . . . . . 101
4.4.95 Employment in human health and social work activities, as percentage of
total employment, total (eu emtk q t) . . . . . . . . . . . . . . . . . . . . . . 101
4.4.96 Employment in arts, entertainment and recreation, as percentage of total
employment, female (eu emtk r f) . . . . . . . . . . . . . . . . . . . . . . . . 102
4.4.97 Employment in arts, entertainment and recreation, as percentage of total
employment, male (eu emtk r m) . . . . . . . . . . . . . . . . . . . . . . . . . 103
4.4.98 Employment in arts, entertainment and recreation, as percentage of total
employment, total (eu emtk r t) . . . . . . . . . . . . . . . . . . . . . . . . . 103
4.4.99 Employment in other service activities, as percentage of total employment,
female (eu emtk s f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 104
5

## Page 7

4.4.100 Employment in other service activities, as percentage of total employment,
male (eu emtk s m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 105
4.4.101 Employment in other service activities, as percentage of total employment,
total (eu emtk s t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 105
4.4.102 Navigable canals, in kilometers (eu troad cnl) . . . . . . . . . . . . . . . . . . 106
4.4.103 Motorways, in kilometers (eu troad mway) . . . . . . . . . . . . . . . . . . . 106
4.4.104 Other roads, in kilometers (eu troad rd oth) . . . . . . . . . . . . . . . . . . . 107
4.4.105 Navigable rivers, in kilometers (eu troad riv) . . . . . . . . . . . . . . . . . . 107
4.4.106 Total railway lines, in kilometers (eu troad rl) . . . . . . . . . . . . . . . . . . 108
4.4.107 Electried railway lines, in kilometers (eu troad rl elc) . . . . . . . . . . . . . 108
4.4.108 Railway lines with double and more tracks, in kilometers (eu troad rl tge2) . 109
4.4.109 Total number of motor coaches, buses and trolley buses (eu vs bus tot) . . . 109
4.4.110 Total number of passenger cars (eu vs car) . . . . . . . . . . . . . . . . . . . 110
4.4.111 Total number of lorries (eu vs lor) . . . . . . . . . . . . . . . . . . . . . . . . 111
4.4.112 Total number of motorcycles (eu vs moto) . . . . . . . . . . . . . . . . . . . . 111
4.4.113 Total number of special vehicles (eu vs spe) . . . . . . . . . . . . . . . . . . . 112
4.4.114 Total number of all vehicles (except trailers and motorcycles) (eu vs tot x tm) 113
4.4.115 Total number of road tractors (eu vs trc) . . . . . . . . . . . . . . . . . . . . 113
4.4.116 Total number of trailers and semi-trailers (eu vs trl strl) . . . . . . . . . . . . 114
4.4.117 Total number of total utility vehicles (eu vs utl) . . . . . . . . . . . . . . . . 114
4.4.118 Injured victims in road accidents, per million inhabitants (eu rac inj) . . . . . 115
4.4.119 Killed victims in road accidents, per million inhabitants (eu rac kil) . . . . . 115
4.4.120 Maritime transport of freight loaded, in thousand tonnes (eu mtf fr ld) . . . 116
4.4.121 Maritime transport of freight loaded and unloaded, in thousand tonnes (eu -
mtf fr ld nld) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 117
4.4.122 Maritime transport of freight unloaded, in thousand tonnes (eu mtf fr nld) . 117
4.4.123 Maritime transport of passengers embarked and disembarked, in thousand
passengers (eu mtp pas) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 118
4.4.124 Maritime transport of passengers disembarked, in thousand passengers (eu -
mtp pas demb) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 119
4.4.125 Maritime transport of passengers embarked, in thousand passengers (eu mtp -
pas emb) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 119
4.4.126 Air transport of freight and mail loaded, in thousand tonnes (eu atf frm ld) . 120
4.4.127 Air transport of freight and mail loaded and unloaded, in thousand tonnes
(eu atf frm ld nld) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 121
4.4.128 Air transport of freight and mail unloaded, in thousand tonnes (eu atf frm nld)121
4.4.129 Air transport of passengers carried, in thousand passengers (eu mtp pas crd) 122
4.4.130 Air transport of passengers carried (arrival), in thousand passengers (eu -
mtp pas crd arr) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 123
4.4.131 Air transport of passengers carried (departures), in thousand passengers (eu -
mtp pas crd dep) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 123
4.4.132 Number of nights spent at camping grounds, recreational vehicle parks and
trailer parks (eu tour nscamp) . . . . . . . . . . . . . . . . . . . . . . . . . . 124
4.4.133 Number of nights spent at hotels and similar accommodation (eu tour nshotel)125
4.4.134 Number of nights spent at holiday and other short-stay accommodation (eu -
tour nssa) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 126
6

## Page 8

4.4.135 Number of nights spent at tourist accommodations (eu tour nstour) . . . . . 127
4.4.136 Net occupancy rate of bed-places in hotels and similar (eu tour bedpl) . . . . 128
4.4.137 Net occupancy rate of bedrooms in hotels and similar (eu tour bedrm) . . . . 129
4.4.138 Number of bed-places in hotels, camping places and other (eu tour nstour -
bedpl) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 130
4.4.139 Number of establishments in hotels, camping places and other (eu tour ns-
tour estbl) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 130
4.4.140 Reported number of cases of robbery (eu cri rob) . . . . . . . . . . . . . . . . 131
4.4.141 Reported number of cases of intentional homicide (eu cri inthom) . . . . . . . 131
4.4.142 Reported number of cases of burglary of private premises (eu cri bur) . . . . 132
4.4.143 Regional gross domestic product by NUTS 2 regions - million EUR (eu mio eur)133
4.4.144 Regional gross domestic product (million PPS) by NUTS 2 regions (eu gdp -
mio pps) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 133
4.4.145 Regional gross domestic product (PPS per inhabitant) by NUTS 2 regions
(eu gdp pps hab) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 134
4.4.146 Regional gross domestic product (PPS per inhabitant in % of the EU27 (from
2020) average) by NUTS 2 regions (eu gdp pps hab eu27 2020) . . . . . . . . 135
4.4.147 Disposable income of private households by NUTS 2 regions (eu dinc pps hab)135
4.4.148 Primary income of private households by NUTS 2 regions (eu pinc pps hab) . 136
4.4.149 Real growth rate of regional gross value added (GV A) at basic prices by NUTS
2 regions (eu rgva pch pre) . . . . . . . . . . . . . . . . . . . . . . . . . . . . 137
4.4.150 Income of households (balance), euro per inhabitant (eu b5n eur hab) . . . . 137
4.4.151 Income of households (balance), million euro (eu b5n mio eur) . . . . . . . . 138
4.4.152 Income of households (balance), million national currency (eu b5n mio nac) . 139
4.4.153 Income of households (balance), million PPS (eu b5n mio pps) . . . . . . . . 139
4.4.154 Income of households (disposable income), euro per inhabitant (eu b6n eur -
hab) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 140
4.4.155 Income of households (disposable income), million euro (eu b6n mio eur) . . 141
4.4.156 Income of households (disposable income), million national currency (eu -
b6n mio nac) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141
4.4.157 Income of households (disposable income), million PPS (eu b6n mio pps) . . 142
4.4.158 Income of households (Adjusted disposable income, net), million euro (eu -
b7n mio eur) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 143
4.4.159 Income of households (Adjusted disposable income, net), million national
currency (eu b7n mio nac) . . . . . . . . . . . . . . . . . . . . . . . . . . . . 143
4.4.160 At-risk-of-poverty rate by NUTS regions, percentage (eu povrisk pc) . . . . . 144
4.4.161 Severe material deprivation rate by NUTS regions, percentage (eu matdep pc) 144
4.4.162 People living in households with very low work intensity by NUTS regions
(population aged 0 to 59 years), percentage (eu lwoin pc) . . . . . . . . . . . 145
4.4.163 People living in households with very low work intensity by NUTS regions
(population aged 0 to 59 years), percentage of total population aged less than
60 (eu lwoin pc y lt60) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 146
4.4.164 People at risk of poverty or social exclusion by NUTS regions, percentage
(eu povr pc) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 147
4.4.165 Educational attaintment for ages 25 to 64, primary education, female (eu -
edatt ed02 y2564f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 147
7

## Page 9

4.4.166 Educational attaintment for ages 25 to 64, primary education, male (eu -
edatt ed02 y2564m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 148
4.4.167 Educational attaintment for ages 25 to 64, primary education, total (eu -
edatt ed02 y2564t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 149
4.4.168 Educational attaintment for ages 25 to 64, secondary education, female (eu -
edatt ed34 y2564f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 149
4.4.169 Educational attaintment for ages 25 to 64, secondary education, male (eu -
edatt ed34 y2564m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 150
4.4.170 Educational attaintment for ages 25 to 64, secondary education, total (eu -
edatt ed34 y2564t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 151
4.4.171 Educational attaintment for ages 25 to 64, tertiary education, female (eu -
edatt ed58 y2564f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 151
4.4.172 Educational attaintment for ages 25 to 64, tertiary education, male (eu -
edatt ed58 y2564m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 152
4.4.173 Educational attaintment for ages 25 to 64, tertiary education, total (eu -
edatt ed58 y2564t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 153
4.4.174 Educational attaintment for ages 30 to 34, primary education, female (eu -
edatt ed02 y3034f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 153
4.4.175 Educational attaintment for ages 30 to 34, primary education, male (eu -
edatt ed02 y3034m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 154
4.4.176 Educational attaintment for ages 30 to 34, primary education, total (eu -
edatt ed02 y3034t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 155
4.4.177 Educational attaintment for ages 30 to 34, secondary education, female (eu -
edatt ed34 y3034f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 155
4.4.178 Educational attaintment for ages 30 to 34, secondary education, male (eu -
edatt ed34 y3034m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 156
4.4.179 Educational attaintment for ages 30 to 34, secondary education, total (eu -
edatt ed34 y3034t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 157
4.4.180 Educational attaintment for ages 30 to 34, tertiary education, female (eu -
edatt ed58 y3034f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 157
4.4.181 Educational attaintment for ages 30 to 34, tertiary education, male (eu -
edatt ed58 y3034m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 158
4.4.182 Educational attaintment for ages 30 to 34, tertiary education, total (eu -
edatt ed58 y3034t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 159
4.4.183 Early leavers from education and training as a percentage, females (eu ed-
uleave f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 159
4.4.184 Early leavers from education and training as a percentage, males (eu ed-
uleave m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 160
4.4.185 Early leavers from education and training as a percentage, total (eu eduleave t)161
4.4.186 15-24 year old people neither in employment nor in education as percentage,
females (eu neet y1524f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 161
4.4.187 15-24 year old people neither in employment nor in education as percentage,
males (eu neet y1524m) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 162
4.4.188 15-24 year old people neither in employment nor in education as percentage,
total (eu neet y1524t) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 163
8

## Page 10

4.4.189 Employment rate for people between 15 and 34 years, total duration since
education (eu empl durtotal) . . . . . . . . . . . . . . . . . . . . . . . . . . . 163
4.4.190 Employment rate for people between 15 and 34 years, over 3 years since
education (eu empl dury gt3) . . . . . . . . . . . . . . . . . . . . . . . . . . . 164
4.4.191 Employment rate for people between 15 and 34 years, 1 to 3 years since
education (eu empl dury13) . . . . . . . . . . . . . . . . . . . . . . . . . . . . 165
4.4.192 Employment rate for people between 15 and 34 years, education levels 0-2
(eu empl edled02) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 165
4.4.193 Employment rate for people between 15 and 34 years, education levels 3-4
(eu empl edled34) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 166
4.4.194 Employment rate for people between 15 and 34 years, education levels 5-8
(eu empl edled58) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 167
4.4.195 Employment rate for people between 15 and 34 years, all education levels
(eu empl edltotal) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 167
4.4.196 Participation rate in education and training (last 4 weeks), females (eu -
epry2564f) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 168
4.4.197 Participation rate in education and training (last 4 weeks), males (eu epry2564m)169
4.4.198 Participation rate in education and training (last 4 weeks), total (eu epry2564t)170
4.4.199 Participation rate in primary and lower secondary education (eu epred12) . . 171
4.4.200 Participation rate in tertiary education (eu epred58) . . . . . . . . . . . . . . 171
4.4.201 Municipal waste disposal - incineration in thousand tonnes (eu env wasdsp i) 172
4.4.202 Municipal waste generated in thousand tonnes (eu env wasgen) . . . . . . . . 173
4.4.203 Municipal waste recovery - energy recovery in thousand tonnes (eu env was-
rcv e) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 174
4.4.204 Municipal waste recycling in thousand tonnes (eu env wasrcy c d) . . . . . . 174
4.4.205 Number of cooling degree days (eu eng cdd) . . . . . . . . . . . . . . . . . . . 175
4.4.206 Number of heating degree days (eu eng hdd) . . . . . . . . . . . . . . . . . . 176
4.4.207 Dentists per hundred thousand inhabitants (eu hea dent) . . . . . . . . . . . 176
4.4.208 Medical doctors per hundred thousand inhabitants (eu hea mdoc) . . . . . . 177
4.4.209 Nurses and midwives per hundred thousand inhabitants (eu hea nurs) . . . . 178
4.4.210 Pharmacists per hundred thousand inhabitants (eu hea pharm) . . . . . . . . 179
4.4.211 Physiotherapists per hundred thousand inhabitants (eu hea phys) . . . . . . 180
4.4.212 Available beds in hospitals (HP.1) per hundred thousand inhabitants (eu -
hea bed) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 181
4.4.213 Curative care beds in hospitals (HP.1) per hundred thousand inhabitants
(eu hea bedcur) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 182
4.4.214 Long-term care beds in hospitals (HP.1) per hundred thousand inhabitants
(eu hea bedlt) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 182
4.4.215 Other beds in hospitals (HP.1) per hundred thousand inhabitants (eu hea -
bedoth) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 183
4.4.216 Psychiatric care beds in hospitals (HP.1) per hundred thousand inhabitants
(eu hea bedpsy) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 184
4.4.217 Rehabilitative care beds in hospitals (HP.1) per hundred thousand inhabitants
(eu hea bedreh) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 184
4.4.218 Number of deaths by circulatory system diseases, female (eu hea cs f) . . . . 185
4.4.219 Number of deaths by circulatory system diseases, male (eu hea cs m) . . . . 186
9

## Page 11

4.4.220 Number of deaths by circulatory system diseases, total (eu hea cs t) . . . . . 186
4.4.221 Number of deaths by HIV, female (eu hea hiv f) . . . . . . . . . . . . . . . . 187
4.4.222 Number of deaths by HIV, male (eu hea hiv m) . . . . . . . . . . . . . . . . . 188
4.4.223 Number of deaths by HIV, total (eu hea hiv t) . . . . . . . . . . . . . . . . . 188
4.4.224 Number of deaths by infectious and parasitic diseases, female (eu hea ipd f) . 189
4.4.225 Number of deaths by infectious and parasitic diseases, male (eu hea ipd m) . 190
4.4.226 Number of deaths by infectious and parasitic diseases, total (eu hea ipd t) . . 190
4.4.227 Number of deaths by malignant neoplasms, female (eu hea np f) . . . . . . . 191
4.4.228 Number of deaths by malignant neoplasms, male (eu hea np m) . . . . . . . 192
4.4.229 Number of deaths by malignant neoplasms, total (eu hea np t) . . . . . . . . 192
4.4.230 Number of deaths by nervous system diseases, female (eu hea ns f) . . . . . . 193
4.4.231 Number of deaths by nervous system diseases, male (eu hea ns m) . . . . . . 194
4.4.232 Number of deaths by nervous system diseases, total (eu hea ns t) . . . . . . . 194
4.4.233 Number of deaths by pregnancy, childbirth and puerperium (eu hea pr f) . . 195
4.4.234 Number of deaths by self-harm, female (eu hea sh f) . . . . . . . . . . . . . . 196
4.4.235 Number of deaths by self-harm, male (eu hea sh m) . . . . . . . . . . . . . . 196
4.4.236 Number of deaths by self-harm, total (eu hea sh t) . . . . . . . . . . . . . . . 197
4.4.237 Number of deaths by drug dependence, female (eu hea tox f) . . . . . . . . . 198
4.4.238 Number of deaths by drug dependence, male (eu hea tox m) . . . . . . . . . 198
4.4.239 Number of deaths by drug dependence, total (eu hea tox t) . . . . . . . . . . 199
4.4.240 Percentage of households with internet access (eu is iacc) . . . . . . . . . . . 200
4.4.241 Percentage of households with broadband internet access (eu is bacc) . . . . 200
4.4.242 Percentage of individuals who have never used a computer (eu iu never) . . . 201
4.4.243 Percentage of individuals who accessed the internet away from home or work
(eu iu ohw) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 202
4.4.244 Percentage of individuals who accessed the internet away from home or work,
last 3 months (eu iu ohw3) . . . . . . . . . . . . . . . . . . . . . . . . . . . . 203
4.4.245 Percentage of individuals using internet to interact with public authorities
(eu iu govform) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 204
4.4.246 Percentage of individuals using internet to submit forms to authorities (eu -
iu govint) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 205
4.4.247 Frequency of internet access: daily (eu iu iday) . . . . . . . . . . . . . . . . . 206
4.4.248 Last internet use: in the last 12 months (eu iu ilt12) . . . . . . . . . . . . . . 207
4.4.249 Last internet use: in last 3 months (eu iu iu3) . . . . . . . . . . . . . . . . . . 208
4.4.250 Internet use: internet banking (eu iu iubk) . . . . . . . . . . . . . . . . . . . 209
4.4.251 Internet use: civic or political participation (eu iu iucpp) . . . . . . . . . . . 210
4.4.252 Frequency of internet access: once a week (including every day) (eu iu iuse) . 211
4.4.253 Internet use: selling goods or services (eu iu iusell) . . . . . . . . . . . . . . . 212
4.4.254 Internet use: participating in social networks (eu iu iusnet) . . . . . . . . . . 213
4.4.255 Internet use: never (eu iu iux) . . . . . . . . . . . . . . . . . . . . . . . . . . 214
4.4.256 Last online purchase: between 3 and 12 months ago (eu igs b3 12) . . . . . . 215
4.4.257 Online purchases: from sellers from other EU countries (eu igs bfeu) . . . . . 216
4.4.258 Online purchases: travel and holiday accommodation (eu igs bhols) . . . . . . 217
4.4.259 Last online purchase: in the 12 months (eu igs blt12) . . . . . . . . . . . . . 218
4.4.260 Individuals who ordered goods or services in internet more than a year ago
or never (eu igs bumt12x) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 219
10

## Page 12

4.4.261 Last online purchase: in the last 3 months (eu igs buy3) . . . . . . . . . . . . 220
4.4.262 Employment rate for 15-24 years old, female (eu emp 1524f) . . . . . . . . . 221
4.4.263 Employment rate for 15-24 years old, male (eu emp 1524m) . . . . . . . . . . 222
4.4.264 Employment rate for 15-24 years old, total (eu emp 1524t) . . . . . . . . . . 222
4.4.265 Employment rate for 20-64 years old, female (eu emp 2064f) . . . . . . . . . 223
4.4.266 Employment rate for 20-64 years old, male (eu emp 2064m) . . . . . . . . . . 224
4.4.267 Employment rate for 20-64 years old, total (eu emp 2064t) . . . . . . . . . . 224
4.4.268 Employment rate for 25-34 years old, female (eu emp 2534f) . . . . . . . . . 225
4.4.269 Employment rate for 25-34 years old, male (eu emp 2534m) . . . . . . . . . . 226
4.4.270 Employment rate for 25-34 years old, total (eu emp 2534t) . . . . . . . . . . 226
4.4.271 Employment rate for +25 years, female (eu emp ge25f) . . . . . . . . . . . . 227
4.4.272 Employment rate for +25 years, male (eu emp ge25m) . . . . . . . . . . . . . 228
4.4.273 Employment rate for +25 years, total (eu emp ge25t) . . . . . . . . . . . . . 228
4.4.274 Employment rate for +65 years, female (eu emp ge65f) . . . . . . . . . . . . 229
4.4.275 Employment rate for +65 years, male (eu emp ge65m) . . . . . . . . . . . . . 230
4.4.276 Employment rate for +65 years, total (eu emp ge65t) . . . . . . . . . . . . . 230
4.4.277 Employment in agriculture, forestry andshing, in thousands (eu emp a) . . 231
4.4.278 Employment in industry (except construction), in thousands (eu emp be) . . 232
4.4.279 Employment in construction, in thousands (eu emp f) . . . . . . . . . . . . . 232
4.4.280 Employment in wholesale and retail trade, transport, accommodation and
food service activities, in thousands (eu emp gi) . . . . . . . . . . . . . . . . 233
4.4.281 Employment in information and communication, in thousands (eu emp j) . . 234
4.4.282 Employment innancial and insurance activities, in thousands (eu emp k) . 234
4.4.283 Employment in real estate activities, in thousands (eu emp l) . . . . . . . . . 235
4.4.284 Employment in professional, scientic and technical activities, in thousands
(eu emp m n) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 236
4.4.285 Employment in public administration, defence, education, human health and
social work activities, in thousands (eu emp oq) . . . . . . . . . . . . . . . . 236
4.4.286 Employment in arts, entertainment and recreation, in thousands (eu emp ru) 237
4.4.287 Employment in total - all NACE activities, in thousands (eu emp total) . . . 238
4.4.288 Full-time employment, female, in thousands (eu emp ft f) . . . . . . . . . . . 238
4.4.289 Full-time employment, male, in thousands (eu emp ft m) . . . . . . . . . . . 239
4.4.290 Full-time employment, total, in thousands (eu emp ft t) . . . . . . . . . . . . 240
4.4.291 Part-time employment, female, in thousands (eu emp pt f) . . . . . . . . . . 240
4.4.292 Part-time employment, male, in thousands (eu emp pt m) . . . . . . . . . . . 241
4.4.293 Part-time employment, total, in thousands (eu emp pt t) . . . . . . . . . . . 242
4.4.294 Long-term unemployment as percentage of active population (eu ltu pc act) . 242
4.4.295 Long-term unemployment as percentage of unemployment (eu ltu pc une) . . 243
4.4.296 Long-term unemployment in thousands (eu ltu ths) . . . . . . . . . . . . . . 244
4.4.297 Unemployment rate for 15-24 years old, female (eu unemp 1524f) . . . . . . . 245
4.4.298 Unemployment rate for 15-24 years old, male (eu unemp 1524m) . . . . . . . 246
4.4.299 Unemployment rate for 15-24 years old, total (eu unemp 1524t) . . . . . . . . 246
4.4.300 Unemployment rate for 15-74 years old, female (eu unemp 1574f) . . . . . . . 247
4.4.301 Unemployment rate for 15-74 years old, male (eu unemp 1574m) . . . . . . . 248
4.4.302 Unemployment rate for 15-74 years old, total (eu unemp 1574t) . . . . . . . . 248
4.4.303 Unemployment rate for 20-64 years old, female (eu unemp 2064f) . . . . . . . 249
11

## Page 13

4.4.304 Unemployment rate for 20-64 years old, male (eu unemp 2064m) . . . . . . . 250
4.4.305 Unemployment rate for 20-64 years old, total (eu unemp 2064t) . . . . . . . . 250
4.4.306 Unemployment rate for + 15 years, female (eu unemp ge15f) . . . . . . . . . 251
4.4.307 Unemployment rate for +15 years, male (eu unemp ge15m) . . . . . . . . . . 252
4.4.308 Unemployment rate for +15 years, total (eu unemp ge15t) . . . . . . . . . . . 252
4.4.309 Unemployment rate for +25 years, female (eu unemp ge25f) . . . . . . . . . . 253
4.4.310 Unemployment rate for +25 years, male (eu unemp ge25m) . . . . . . . . . . 254
4.4.311 Unemployment rate for +25 years, total (eu unemp ge25t) . . . . . . . . . . . 254
12

## Page 14

1 Introduction
1.1 The Quality of Government Institute
The QoG Institute was founded in 2004 by Professor Bo Rothstein and Professor S¨ oren Holmberg.
It is an independent research institute within the Department of Political Science at the Univer-
sity of Gothenburg. The institute conducts research on the causes, consequences and nature of
Good Governance and the Quality of Government (QoG) - that is, trustworthy, reliable, impartial,
uncorrupted, and competent government institutions.
The main objective of the research is to address the theoretical and empirical problems of how
political institutions of high quality can be created and maintained. A second objective is to study
the eects of Quality of Government on a number of policy areas, such as health, environment,
social policy, and poverty. While Quality of Government is the common intellectual focal point of
the research institute, a variety of theoretical and methodological perspectives are applied.
1.2 The QoG EU Regional Data
One aim of the QoG Institute is to make comparative data on QoG and its correlates publicly
available. To accomplish this, we have compiled several datasets that draw on a number of freely
available data sources, including aggregated individual-level data. The QoG datasets are available
in severalle formats making them usable in most statistical software as well as in Excel.
The QoG EU Regional dataset is a dataset consisting of more than 350 variables covering
three levels of European regions - Nomenclature of Territorial Units for Statistics (NUTS): NUTS0
(country), NUTS1 and NUTS2.The data is presented in time-series (TS) version, the unit of analysis
is region-year (e.g. Stockholm-2013, Bremen-2005 and so on).
On the QoG website we provide four more datasets. The QoG Standard dataset is our largest
dataset consisting of approximately 2500 variables. For those who prefer a smaller dataset, we
provide the QoG Basic dataset, consisting of approximately the 300 most used variables. We also
provide a dataset called the QoG OECD dataset which covers OECD member countries and has
high data coverage in terms of geography and time.
The Standard, Basic, and OECD datasets are all available in both time-series (TS) and cross-
sectional (CS) versions, as separate datasets. In the TS datasets, the unit of analysis is country-year
(e.g. Sweden-1984, Sweden-1985 and so on). The CS datasets, unlike the TS dataset, does not
include multiple years for a particular country and the unit of analysis is therefore countries. Many
of the variables are available in both TS and CS, but some are not.
One more dataset is The QoG Expert Survey. It is a unique dataset, consisting of two waves,
with information on the structure and behaviour of public administration in a range of dierent
countries. The dataset covers dierent dimensions of the Quality of Government, such as, politiciza-
tion, professionalization, openness, and impartiality. The QoG Expert Survey I (2008-2011) covers
135 countries and is based on a web survey of 1053 experts, for The QoG Expert Survey II (2015)
coverage was improved and reached 159 countries and based on a web survey of 1294 experts.
13

## Page 15

2 Data Structure
2.1 Data Structure
The QoG Regional Data is presented in three dierent forms available in separate datasets. All
datasets are available in time-series format. First one (The QoG Regional Data - Long Form) is a
dataset where data is presented in the long form. The list of units of analysis contains regions of
all NUTS levels.
Table 1: The QoG Regional Data - Long Form (example of structure)
region -
code
region name year level nuts0 nuts1 nuts2 var example
SE SVERIGE 1990 0 SE 50
SE SVERIGE 1991 0 SE 60
SE SVERIGE 2014 0 SE 90
SE SVERIGE 2015 0 SE 110
SE1 ¨OSTRA SVERIGE 1990 1 SE SE1 15
SE1 ¨OSTRA SVERIGE 1991 1 SE SE1 17
SE1 ¨OSTRA SVERIGE 2014 1 SE SE1 25
SE1 ¨OSTRA SVERIGE 2015 1 SE SE1 28
SE11 Stockholm 1990 2 SE SE1 SE11 9
SE11 Stockholm 1991 2 SE SE1 SE11 11
SE11 Stockholm 2014 2 SE SE1 SE11 19
SE11 Stockholm 2015 2 SE SE1 SE11 21
Two other datasets are presented in the wide form for multilevel analysis. In the second dataset
(The QoG Regional Data - Wide Form NUTS1) includes NUTS1 level as the unit of analysis and
variables represent the values for this level and corresponding lower level – NUTS0. As an example,
in this dataset the data is presented only for East Sweden ( ¨Ostra Sverige SE1), as a unit of analysis
and have values for lower level of this region - Sweden (SE).
Table 2: The QoG Regional Data - Wide Form NUTS1 (example of structure)
region -
code
region name year level nuts0 var example
nuts1
var example
nuts0
SE1 ¨OSTRA SVERIGE 1990 1 SE 15 50
SE1 ¨OSTRA SVERIGE 1991 1 SE 17 60
SE1 ¨OSTRA SVERIGE 2014 1 SE 25 90
SE1 ¨OSTRA SVERIGE 2015 1 SE 28 110
The third dataset (The QoG Regional Data - Wide Form NUTS2) the unit of analysis is NUTS2
level regions and variables provide values as for every unit of analysis, as well as for corresponding
lower NUTS levels: NUTS1 and NUTS0. One example of unit of analysis in this dataset is Stock-
holm (SE11) and data for every variable will be for Stockholm, as well as for lower levels region -
14

## Page 16

East Sweden ( ¨Ostra Sverige SE1) and Sweden (SE).
Table 3: The QoG Regional Data - Wide Form NUTS2 (example of structure)
region
code
region
name year level nuts0 nuts1 var example
nuts2
var example
nuts1
var example
nuts0
SE11 Stockholm 1990 2 SE SE1 9 15 50
SE11 Stockholm 1991 2 SE SE1 11 17 60
SE11 Stockholm 2014 2 SE SE1 19 25 90
SE11 Stockholm 2015 2 SE SE1 21 28 110
15

## Page 17

3 Variables by Category
3.1 Demographics
Proportion of live births outside marriage (eu agemoth) 55
Total fertility rate (eu agemoth1) 56
Crude rate of net migration plus statistical adjustment (eu cnmigratrt) 42
Reported number of cases of burglary of private premises (eu cri bur) 132
Reported number of cases of intentional homicide (eu cri inthom) 131
Reported number of cases of robbery (eu cri rob) 131
Population at 1st January, female (eu d2jan f) 40
Population at 1st January, male (eu d2jan m) 40
Population at 1st January, total (eu d2jan t) 41
Area of a region, land area total, sq km (eu d3area lat) 44
Area of a region, total, sq km (eu d3area t) 44
Number of deaths of females, all ages (eu death totalf) 45
Number of deaths of males, all ages (eu death totalm) 46
Number of deaths, total all ages (eu death totalt) 46
Number of deaths of females, at 1 year old (eu death y1f) 47
Number of deaths of males, at 1 year old (eu death y1m) 48
Number of deaths, total at 1 year old (eu death y1t) 48
Number of deaths of females, at 20 years old (eu death y20f) 49
Number of deaths of males, at 20 years old (eu death y20m) 49
Number of deaths, total at 20 years old (eu death y20t) 50
Number of deaths of females, at 50 years old (eu death y50f) 50
Number of deaths of males, at 50 years old (eu death y50m) 51
Number of deaths, total at 50 years old (eu death y50t) 51
Number of deaths of females, at 70 years old (eu death y70f) 52
Number of deaths of males, at 70 years old (eu death y70m) 52
Number of deaths, total at 70 years old (eu death y70t) 53
Fertility rate, total (eu frate total) 53
Fertility rate, at age 15 (eu frate y15) 54
Fertility rate, at age 30 (eu frate y30) 54
Fertility rate, at age 35 (eu frate y35) 55
Crude rate of total population change (eu growrt) 43
Life expectancy in years at 1 year old, female (eu mlifexp f) 57
Life expectancy in years at 1 year old, male (eu mlifexp m) 58
Life expectancy in years at 1 year old, total (eu mlifexp t) 58
Crude rate of natural change of population (eu natgrowrt) 43
Mean age of women at childbirth (eu nmarpct) 56
Population density, average population per square km (eu per km2) 45
Mean age of women at birth ofrst child (eu totferrt) 57
16

## Page 18

3.2 Digital Society and Economy
Last online purchase: between 3 and 12 months ago (eu igs b3 12) 215
Online purchases: from sellers from other EU countries (eu igs bfeu) 216
Online purchases: travel and holiday accommodation (eu igs bhols) 217
Last online purchase: in the 12 months (eu igs blt12) 218
Individuals who ordered goods or services in internet more than a year ago or never (eu igs bumt12x)
219
Last online purchase: in the last 3 months (eu igs buy3) 220
Percentage of households with broadband internet access (eu is bacc) 200
Percentage of households with internet access (eu is iacc) 200
Percentage of individuals using internet to interact with public authorities (eu iu govform) 204
Percentage of individuals using internet to submit forms to authorities (eu iu govint) 205
Frequency of internet access: daily (eu iu iday) 206
Last internet use: in the last 12 months (eu iu ilt12) 207
Last internet use: in last 3 months (eu iu iu3) 208
Internet use: internet banking (eu iu iubk) 209
Internet use: civic or political participation (eu iu iucpp) 210
Frequency of internet access: once a week (including every day) (eu iu iuse) 211
Internet use: selling goods or services (eu iu iusell) 212
Internet use: participating in social networks (eu iu iusnet) 213
Internet use: never (eu iu iux) 214
Percentage of individuals who have never used a computer (eu iu never) 201
Percentage of individuals who accessed the internet away from home or work (eu iu ohw) 202
Percentage of individuals who accessed the internet away from home or work, last 3 months (eu -
iu ohw3) 203
3.3 Economy
Income of households (balance), euro per inhabitant (eu b5n eur hab) 137
Income of households (balance), million euro (eu b5n mio eur) 138
Income of households (balance), million national currency (eu b5n mio nac) 139
Income of households (balance), million PPS (eu b5n mio pps) 139
Income of households (disposable income), euro per inhabitant (eu b6n eur hab) 140
Income of households (disposable income), million euro (eu b6n mio eur) 141
Income of households (disposable income), million national currency (eu b6n mio nac) 141
Income of households (disposable income), million PPS (eu b6n mio pps) 142
Income of households (Adjusted disposable income, net), million euro (eu b7n mio eur) 143
Income of households (Adjusted disposable income, net), million national currency (eu b7n mio -
nac) 143
Disposable income of private households by NUTS 2 regions (eu dinc pps hab) 135
Regional gross domestic product (million PPS) by NUTS 2 regions (eu gdp mio pps) 133
Regional gross domestic product (PPS per inhabitant) by NUTS 2 regions (eu gdp pps hab) 134
Regional gross domestic product (PPS per inhabitant in % of the EU27 (from 2020) average) by
NUTS 2 regions (eu gdp pps hab eu27 2020) 135
Regional gross domestic product by NUTS 2 regions - million EUR (eu mio eur) 133
17

## Page 19

Primary income of private households by NUTS 2 regions (eu pinc pps hab) 136
Real growth rate of regional gross value added (GV A) at basic prices by NUTS 2 regions (eu rgva -
pch pre) 137
3.4 Education
Educational attaintment for ages 25 to 64, primary education, female (eu edatt ed02 y2564f) 147
Educational attaintment for ages 25 to 64, primary education, male (eu edatt ed02 y2564m) 148
Educational attaintment for ages 25 to 64, primary education, total (eu edatt ed02 y2564t) 149
Educational attaintment for ages 30 to 34, primary education, female (eu edatt ed02 y3034f) 153
Educational attaintment for ages 30 to 34, primary education, male (eu edatt ed02 y3034m) 154
Educational attaintment for ages 30 to 34, primary education, total (eu edatt ed02 y3034t) 155
Educational attaintment for ages 25 to 64, secondary education, female (eu edatt ed34 y2564f) 149
Educational attaintment for ages 25 to 64, secondary education, male (eu edatt ed34 y2564m) 150
Educational attaintment for ages 25 to 64, secondary education, total (eu edatt ed34 y2564t) 151
Educational attaintment for ages 30 to 34, secondary education, female (eu edatt ed34 y3034f) 155
Educational attaintment for ages 30 to 34, secondary education, male (eu edatt ed34 y3034m) 156
Educational attaintment for ages 30 to 34, secondary education, total (eu edatt ed34 y3034t) 157
Educational attaintment for ages 25 to 64, tertiary education, female (eu edatt ed58 y2564f) 151
Educational attaintment for ages 25 to 64, tertiary education, male (eu edatt ed58 y2564m) 152
Educational attaintment for ages 25 to 64, tertiary education, total (eu edatt ed58 y2564t) 153
Educational attaintment for ages 30 to 34, tertiary education, female (eu edatt ed58 y3034f) 157
Educational attaintment for ages 30 to 34, tertiary education, male (eu edatt ed58 y3034m) 158
Educational attaintment for ages 30 to 34, tertiary education, total (eu edatt ed58 y3034t) 159
Early leavers from education and training as a percentage, females (eu eduleave f) 159
Early leavers from education and training as a percentage, males (eu eduleave m) 160
Early leavers from education and training as a percentage, total (eu eduleave t) 161
Employment rate for people between 15 and 34 years, total duration since education (eu empl -
durtotal) 163
Employment rate for people between 15 and 34 years, over 3 years since education (eu empl dury -
gt3) 164
Employment rate for people between 15 and 34 years, 1 to 3 years since education (eu empl dury13)
165
Employment rate for people between 15 and 34 years, education levels 0-2 (eu empl edled02) 165
Employment rate for people between 15 and 34 years, education levels 3-4 (eu empl edled34) 166
Employment rate for people between 15 and 34 years, education levels 5-8 (eu empl edled58) 167
Employment rate for people between 15 and 34 years, all education levels (eu empl edltotal) 167
Participation rate in primary and lower secondary education (eu epred12) 171
Participation rate in tertiary education (eu epred58) 171
Participation rate in education and training (last 4 weeks), females (eu epry2564f) 168
Participation rate in education and training (last 4 weeks), males (eu epry2564m) 169
Participation rate in education and training (last 4 weeks), total (eu epry2564t) 170
15-24 year old people neither in employment nor in education as percentage, females (eu neet -
y1524f) 161
15-24 year old people neither in employment nor in education as percentage, males (eu neet y1524m)
18

## Page 20

162
15-24 year old people neither in employment nor in education as percentage, total (eu neet y1524t)
163
3.5 Environment
Number of cooling degree days (eu eng cdd) 175
Number of heating degree days (eu eng hdd) 176
Municipal waste disposal - incineration in thousand tonnes (eu env wasdsp i) 172
Municipal waste generated in thousand tonnes (eu env wasgen) 173
Municipal waste recovery - energy recovery in thousand tonnes (eu env wasrcv e) 174
Municipal waste recycling in thousand tonnes (eu env wasrcy c d) 174
3.6 Health
Available beds in hospitals (HP.1) per hundred thousand inhabitants (eu hea bed) 181
Curative care beds in hospitals (HP.1) per hundred thousand inhabitants (eu hea bedcur) 182
Long-term care beds in hospitals (HP.1) per hundred thousand inhabitants (eu hea bedlt) 182
Other beds in hospitals (HP.1) per hundred thousand inhabitants (eu hea bedoth) 183
Psychiatric care beds in hospitals (HP.1) per hundred thousand inhabitants (eu hea bedpsy) 184
Rehabilitative care beds in hospitals (HP.1) per hundred thousand inhabitants (eu hea bedreh) 184
Number of deaths by circulatory system diseases, female (eu hea cs f) 185
Number of deaths by circulatory system diseases, male (eu hea cs m) 186
Number of deaths by circulatory system diseases, total (eu hea cs t) 186
Dentists per hundred thousand inhabitants (eu hea dent) 176
Number of deaths by HIV, female (eu hea hiv f) 187
Number of deaths by HIV, male (eu hea hiv m) 188
Number of deaths by HIV, total (eu hea hiv t) 188
Number of deaths by infectious and parasitic diseases, female (eu hea ipd f) 189
Number of deaths by infectious and parasitic diseases, male (eu hea ipd m) 190
Number of deaths by infectious and parasitic diseases, total (eu hea ipd t) 190
Medical doctors per hundred thousand inhabitants (eu hea mdoc) 177
Number of deaths by malignant neoplasms, female (eu hea np f) 191
Number of deaths by malignant neoplasms, male (eu hea np m) 192
Number of deaths by malignant neoplasms, total (eu hea np t) 192
Number of deaths by nervous system diseases, female (eu hea ns f) 193
Number of deaths by nervous system diseases, male (eu hea ns m) 194
Number of deaths by nervous system diseases, total (eu hea ns t) 194
Nurses and midwives per hundred thousand inhabitants (eu hea nurs) 178
Pharmacists per hundred thousand inhabitants (eu hea pharm) 179
Physiotherapists per hundred thousand inhabitants (eu hea phys) 180
Number of deaths by pregnancy, childbirth and puerperium (eu hea pr f) 195
Number of deaths by self-harm, female (eu hea sh f) 196
Number of deaths by self-harm, male (eu hea sh m) 196
19

## Page 21

Number of deaths by self-harm, total (eu hea sh t) 197
Number of deaths by drug dependence, female (eu hea tox f) 198
Number of deaths by drug dependence, male (eu hea tox m) 198
Number of deaths by drug dependence, total (eu hea tox t) 199
3.7 Labor Market Statistics
Employment rate for 15-24 years old, female (eu emp 1524f) 221
Employment rate for 15-24 years old, male (eu emp 1524m) 222
Employment rate for 15-24 years old, total (eu emp 1524t) 222
Employment rate for 20-64 years old, female (eu emp 2064f) 223
Employment rate for 20-64 years old, male (eu emp 2064m) 224
Employment rate for 20-64 years old, total (eu emp 2064t) 224
Employment rate for 25-34 years old, female (eu emp 2534f) 225
Employment rate for 25-34 years old, male (eu emp 2534m) 226
Employment rate for 25-34 years old, total (eu emp 2534t) 226
Employment in agriculture, forestry andshing, in thousands (eu emp a) 231
Employment in industry (except construction), in thousands (eu emp be) 232
Employment in construction, in thousands (eu emp f) 232
Full-time employment, female, in thousands (eu emp ft f) 238
Full-time employment, male, in thousands (eu emp ft m) 239
Full-time employment, total, in thousands (eu emp ft t) 240
Employment rate for +25 years, female (eu emp ge25f) 227
Employment rate for +25 years, male (eu emp ge25m) 228
Employment rate for +25 years, total (eu emp ge25t) 228
Employment rate for +65 years, female (eu emp ge65f) 229
Employment rate for +65 years, male (eu emp ge65m) 230
Employment rate for +65 years, total (eu emp ge65t) 230
Employment in wholesale and retail trade, transport, accommodation and food service activities,
in thousands (eu emp gi) 233
Employment in information and communication, in thousands (eu emp j) 234
Employment innancial and insurance activities, in thousands (eu emp k) 234
Employment in real estate activities, in thousands (eu emp l) 235
Employment in professional, scientic and technical activities, in thousands (eu emp m n) 236
Employment in public administration, defence, education, human health and social work activities,
in thousands (eu emp oq) 236
Part-time employment, female, in thousands (eu emp pt f) 240
Part-time employment, male, in thousands (eu emp pt m) 241
Part-time employment, total, in thousands (eu emp pt t) 242
Employment in arts, entertainment and recreation, in thousands (eu emp ru) 237
Employment in total - all NACE activities, in thousands (eu emp total) 238
Long-term unemployment as percentage of active population (eu ltu pc act) 242
Long-term unemployment as percentage of unemployment (eu ltu pc une) 243
Long-term unemployment in thousands (eu ltu ths) 244
Unemployment rate for 15-24 years old, female (eu unemp 1524f) 245
20

## Page 22

Unemployment rate for 15-24 years old, male (eu unemp 1524m) 246
Unemployment rate for 15-24 years old, total (eu unemp 1524t) 246
Unemployment rate for 15-74 years old, female (eu unemp 1574f) 247
Unemployment rate for 15-74 years old, male (eu unemp 1574m) 248
Unemployment rate for 15-74 years old, total (eu unemp 1574t) 248
Unemployment rate for 20-64 years old, female (eu unemp 2064f) 249
Unemployment rate for 20-64 years old, male (eu unemp 2064m) 250
Unemployment rate for 20-64 years old, total (eu unemp 2064t) 250
Unemployment rate for + 15 years, female (eu unemp ge15f) 251
Unemployment rate for +15 years, male (eu unemp ge15m) 252
Unemployment rate for +15 years, total (eu unemp ge15t) 252
Unemployment rate for +25 years, female (eu unemp ge25f) 253
Unemployment rate for +25 years, male (eu unemp ge25m) 254
Unemployment rate for +25 years, total (eu unemp ge25t) 254
3.8 Poverty and Social Exclusion
People living in households with very low work intensity by NUTS regions (population aged 0 to
59 years), percentage (eu lwoin pc) 145
People living in households with very low work intensity by NUTS regions (population aged 0 to
59 years), percentage of total population aged less than 60 (eu lwoin pc y lt60) 146
Severe material deprivation rate by NUTS regions, percentage (eu matdep pc) 144
People at risk of poverty or social exclusion by NUTS regions, percentage (eu povr pc) 147
At-risk-of-poverty rate by NUTS regions, percentage (eu povrisk pc) 144
3.9 Quality of Government
Number of awarded contracts above 130,000 EUR (cri contr) 36
Final value of awarded tenders of over 130,000 EUR (cri cvalue) 36
Share of contracts with no published call for tender redag (cri nocall) 37
Share of contracts with non-open procedure redag (cri nonopen) 38
Share of contracts with only one bid in total (cri singleb) 37
Share of contracts with tax haven redag (cri taxhav) 38
Corruption pillar, country centered and min-max (0-100) standardized (eqi norm corrupt) 33
Corruption experiences index (corruption sub-pillar) min-max (0-100) (2017) (eqi norm corruptexp)
34
Corruption perceptions index (corruption sub-pillar) min-max (0-100)(2017) (eqi norm corruptper)
33
EQI index, min-max (0-100) standardized (eqi norm eqi) 31
Impartiality pillar, country centered and min-max (0-100) standardized (eqi norm impart) 32
Quality pillar, country centered and min-max (0-100) standardized (eqi norm qual) 32
EQI Index Score (eqi score) 28
Corruption experiences index (corruption sub-pillar) z-score stand. (2017 only) (eqi zcorruptexp)
31
21

## Page 23

Corruption pillar, country centered and z-score standardized (eqi zcorruption) 30
Corruption perceptions index (corruption sub-pillar) z-score stand. (2017 only) (eqi zcorruptper)
30
Impartiality pillar, country centered and z-score standardized (eqi zimpartiality) 29
Quality pillar, country centered and z-score standardized (eqi zquality) 28
3.10 Science and Technology
Employment in agriculture, forestry andshing; mining and quarrying, as percentage of total em-
ployment, female (eu emtk ab f) 72
Employment in agriculture, forestry andshing; mining and quarrying, as percentage of total em-
ployment, male (eu emtk ab m) 72
Employment in agriculture, forestry andshing; mining and quarrying, as percentage of total em-
ployment, total (eu emtk ab t) 73
Employment in manufacturing, as percentage of total employment, female (eu emtk c f) 74
Employment in manufacturing, as percentage of total employment, male (eu emtk c m) 74
Employment in manufacturing, as percentage of total employment, total (eu emtk c t) 75
Employment in high-technology manufacturing, as percentage of total employment, female (eu -
emtk chtc f) 76
Employment in high-technology manufacturing, as percentage of total employment, male (eu emtk -
chtc m) 76
Employment in high-technology manufacturing, as percentage of total employment, total (eu emtk -
chtc t) 77
Employment in electricity, gas, steam and air conditioning supply; water supply and construction,
as percentage of total employment, female (eu emtk df f) 78
Employment in electricity, gas, steam and air conditioning supply; water supply and construction,
as percentage of total employment, male (eu emtk df m) 78
Employment in electricity, gas, steam and air conditioning supply; water supply and construction,
as percentage of total employment, total (eu emtk df t) 79
Employment in services, as percentage of total employment, female (eu emtk gu f) 80
Employment in services, as percentage of total employment, male (eu emtk gu m) 80
Employment in services, as percentage of total employment, total (eu emtk gu t) 81
Employment in high-technology sectors (high-technology manufacturing and knowledge-intensive
high-technology services), as percentage of total employment, female (eu emtk htc f) 82
Employment in high-technology sectors (high-technology manufacturing and knowledge-intensive
high-technology services), as percentage of total employment, male (eu emtk htc m) 82
Employment in high-technology sectors (high-technology manufacturing and knowledge-intensive
high-technology services), as percentage of total employment, total (eu emtk htc t) 83
Employment in information and communication, as percentage of total employment, female (eu -
emtk j f) 84
Employment in information and communication, as percentage of total employment, male (eu -
emtk j m) 85
Employment in information and communication, as percentage of total employment, total (eu -
emtk j t) 85
Employment innancial and insurance activities, as percentage of total employment, female (eu -
22

## Page 24

emtk k f) 86
Employment innancial and insurance activities, as percentage of total employment, male (eu -
emtk k m) 87
Employment innancial and insurance activities, as percentage of total employment, total (eu -
emtk k t) 87
Employment in total knowledge-intensive services, as percentage of total employment, female (eu -
emtk kis f) 88
Employment in total knowledge-intensive services, as percentage of total employment, male (eu -
emtk kis m) 89
Employment in total knowledge-intensive services, as percentage of total employment, total (eu -
emtk kis t) 89
Employment innancial and insurance activities; real estate activities, as percentage of total em-
ployment, female (eu emtk kl f) 90
Employment innancial and insurance activities; real estate activities, as percentage of total em-
ployment, male (eu emtk kl m) 91
Employment innancial and insurance activities; real estate activities, as percentage of total em-
ployment, total (eu emtk kl t) 91
Employment in professional, scientic and technical activities, as percentage of total employment,
female (eu emtk m f) 92
Employment in professional, scientic and technical activities, as percentage of total employment,
male (eu emtk m m) 93
Employment in professional, scientic and technical activities, as percentage of total employment,
total (eu emtk m t) 93
Employment in administrative and support service activities, as percentage of total employment,
female (eu emtk n f) 94
Employment in administrative and support service activities, as percentage of total employment,
male (eu emtk n m) 95
Employment in administrative and support service activities, as percentage of total employment,
total (eu emtk n t) 95
Employment in public administration; activities of extraterritorial organisations and bodies, as per-
centage of total employment, female (eu emtk ou f) 96
Employment in public administration; activities of extraterritorial organisations and bodies, as per-
centage of total employment, male (eu emtk ou m) 97
Employment in public administration; activities of extraterritorial organisations and bodies, as per-
centage of total employment, total (eu emtk ou t) 97
Employment in education, as percentage of total employment, female (eu emtk p f) 98
Employment in education, as percentage of total employment, male (eu emtk p m) 99
Employment in education, as percentage of total employment, total (eu emtk p t) 99
Employment in human health and social work activities, as percentage of total employment, female
(eu emtk q f) 100
Employment in human health and social work activities, as percentage of total employment, male
(eu emtk q m) 101
Employment in human health and social work activities, as percentage of total employment, total
(eu emtk q t) 101
Employment in arts, entertainment and recreation, as percentage of total employment, female (eu -
emtk r f) 102
23

## Page 25

Employment in arts, entertainment and recreation, as percentage of total employment, male (eu -
emtk r m) 103
Employment in arts, entertainment and recreation, as percentage of total employment, total (eu -
emtk r t) 103
Employment in other service activities, as percentage of total employment, female (eu emtk s f)
104
Employment in other service activities, as percentage of total employment, male (eu emtk s m) 105
Employment in other service activities, as percentage of total employment, total (eu emtk s t) 105
Total R&D employees in business enterprise sector, female, full-time equivalent (eu prd bes f) 62
Total R&D employees in business enterprise sector, total, full-time equivalent (eu prd bes t) 63
Total R&D employees in government sector, female, full-time equivalent (eu prd gov f) 64
Total R&D employees in government sector, total, full-time equivalent (eu prd gov t) 65
Total R&D employees in higher education sector, female, full-time equivalent (eu prd hes f) 66
Total R&D employees in higher education sector, total, full-time equivalent (eu prd hes t) 67
Total R&D employees in private non-prot sector, female, full-time equivalent (eu prd pnp f) 68
Total R&D employees in private non-prot sector, total, full-time equivalent (eu prd pnp t) 69
Total R&D employees in all sectors, female, full-time equivalent (eu prd total f) 70
Total R&D employees in all sectors, total, full-time equivalent (eu prd total t) 71
Business enterprise sector intramural expenditure in R&D, euro per inhabitant (eu rdexp bes) 59
Government sector intramural expenditure in R&D, euro per inhabitant (eu rdexp gov) 59
Higher education sector intramural expenditure in R&D, euro per inhabitant (eu rdexp hes) 60
Private non-prot sector intramural expenditure in R&D, euro per inhabitant (eu rdexp pnp) 61
All sectors intramural expenditure in R&D, euro per inhabitant (eu rdexp total) 61
3.11 Tourism
Net occupancy rate of bed-places in hotels and similar (eu tour bedpl) 128
Net occupancy rate of bedrooms in hotels and similar (eu tour bedrm) 129
Number of nights spent at camping grounds, recreational vehicle parks and trailer parks (eu tour -
nscamp) 124
Number of nights spent at hotels and similar accommodation (eu tour nshotel) 125
Number of nights spent at holiday and other short-stay accommodation (eu tour nssa) 126
Number of nights spent at tourist accommodations (eu tour nstour) 127
Number of bed-places in hotels, camping places and other (eu tour nstour bedpl) 130
Number of establishments in hotels, camping places and other (eu tour nstour estbl) 130
3.12 Transport
Air transport of freight and mail loaded, in thousand tonnes (eu atf frm ld) 120
Air transport of freight and mail loaded and unloaded, in thousand tonnes (eu atf frm ld nld) 121
Air transport of freight and mail unloaded, in thousand tonnes (eu atf frm nld) 121
Maritime transport of freight loaded, in thousand tonnes (eu mtf fr ld) 116
Maritime transport of freight loaded and unloaded, in thousand tonnes (eu mtf fr ld nld) 117
Maritime transport of freight unloaded, in thousand tonnes (eu mtf fr nld) 117
24

## Page 26

Maritime transport of passengers embarked and disembarked, in thousand passengers (eu mtp pas)
118
Air transport of passengers carried, in thousand passengers (eu mtp pas crd) 122
Air transport of passengers carried (arrival), in thousand passengers (eu mtp pas crd arr) 123
Air transport of passengers carried (departures), in thousand passengers (eu mtp pas crd dep) 123
Maritime transport of passengers disembarked, in thousand passengers (eu mtp pas demb) 119
Maritime transport of passengers embarked, in thousand passengers (eu mtp pas emb) 119
Injured victims in road accidents, per million inhabitants (eu rac inj) 115
Killed victims in road accidents, per million inhabitants (eu rac kil) 115
Navigable canals, in kilometers (eu troad cnl) 106
Motorways, in kilometers (eu troad mway) 106
Other roads, in kilometers (eu troad rd oth) 107
Navigable rivers, in kilometers (eu troad riv) 107
Total railway lines, in kilometers (eu troad rl) 108
Electried railway lines, in kilometers (eu troad rl elc) 108
Railway lines with double and more tracks, in kilometers (eu troad rl tge2) 109
Total number of motor coaches, buses and trolley buses (eu vs bus tot) 109
Total number of passenger cars (eu vs car) 110
Total number of lorries (eu vs lor) 111
Total number of motorcycles (eu vs moto) 111
Total number of special vehicles (eu vs spe) 112
Total number of all vehicles (except trailers and motorcycles) (eu vs tot x tm) 113
Total number of road tractors (eu vs trc) 113
Total number of trailers and semi-trailers (eu vs trl strl) 114
Total number of total utility vehicles (eu vs utl) 114
25

## Page 27

4 Variables by Original Source
4.1 Identication Variables
4.1.1 Code of NUTS0 level region (nuts0)
Code of NUTS0 level region to which the observation belongs. The Nomenclature of Territorial
Units for Statistics, (NUTS), is a geocode standard for referencing the administrative divisions of
countries for statistical purposes. NUTS 0: country level.
4.1.2 Code of NUTS1 level region (nuts1)
Code of NUTS1 level region to which the observation belongs. The Nomenclature of Territorial
Units for Statistics, (NUTS), is a geocode standard for referencing the administrative divisions of
countries for statistical purposes. NUTS 1: major socio-economic regions.
4.1.3 Code of NUTS2 level region (nuts2)
Code of NUTS2 level region to which the observation belongs. The Nomenclature of Territorial
Units for Statistics, (NUTS), is a geocode standard for referencing the administrative divisions of
countries for statistical purposes. NUTS 2: basic regions for the application of regional policies.
4.1.4 The Nomenclature of Territorial Units for Statistics (NUTS) level (level)
To what level of NUTS belong observation. The Nomenclature of Territorial Units for Statistics,
(NUTS), is a geocode standard for referencing the administrative divisions of countries for statistical
purposes.
(0) Country level;
(1) Major socio-economic regions;
(2) Basic regions for the application of regional policies.
4.1.5 NUTS code of region (region code)
NUTS code of region. The Nomenclature of Territorial Units for Statistics, (NUTS), is a geocode
standard for referencing the administrative divisions of countries for statistical purposes.
4.1.6 Name of the region (region name)
Name of the region in the language of the country.
4.1.7 Name of the country in English (cname)
Name of the country where the region is located in English.
4.1.8 Version of the Dataset (version)
4.1.9 Year (year)
Year of observation.
26

## Page 28

4.2 European Quality of Government Index: European Quality of Gov-
ernment Index
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Nicholas Charron, Victor Lapuente, and Paola Annoni.Measuring quality of government
in EU regions across space and time. 2019.Papers in Regional Science. 98. 5.url:
https://rsaiconnect.onlinelibrary.wiley.com/doi/abs/10.1111/pirs.12437
Nicholas Charron, Lewis Dijkstra, and Victor Lapuente.Mapping the regional divide in
Europe: A measure for assessing quality of government in 206 European regions. 2015.Social
Indicators Research, 122(2), 315-346.122. 2.url:https://doi.org/10.1007/s11205-014-
0702-y
Nicholas Charron, Lewis Dijkstra, and Victor Lapuente.Regional Governance Matters: Qual-
ity of Government within European Union Member States. 2014.Regional Studies. 48. 1.
url:https://doi.org/10.1080/00343404.2013.770141
Dataset found at:https://qog.pol.gu.se/data/datadownloads/qog-eqi-data
The European Quality of Government Index (EQI) is the result of novel survey data regional
(e.g. sub-national) level governance within the EU. The data wasrst gathered and published in
2010 and then repeated in 2013 and 2017, with the next round expected in 2020. The index is
based on a large citizen survey where respondents are asked about perceptions and experiences
with public sector corruption, along with the extent to which citizens believe various public sector
services are impartially allocated and of good quality. It is therst source of data to date that
allows researchers to compare QoG within and across countries in a multi-country context. It aims
to provide researchers and policy makers a tool to better understand how governance varies within
countries and now, over time. It covers all 28 member states and two accession countries (Serbia
and Turkey are also included in the 2013 round). The sub-national regions are at the NUTS 1
or NUTS 2 level, depending on the country. Currently, it provides data for up to 206 regions,
depending on the year in question. In the three years of the EQI survey, it has roughly 200,000
respondents in total. Here, it provides both the regional level data, as well as the underlying mi-
cro data free of charge for researchers and practitioners interested in regional governance in Europe.
27

## Page 29

4.2.1 EQI Index Score (eqi score)
Final score of European Quality Index (centered around WGI), all units. Detailed information on
its calculation method and indicators used for this aggregation can be found inEuropean Quality
of Government Index 2017 Codebook.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 39
NUTS 2 155
4.2.2 Quality pillar, country centered and z-score standardized (eqi zquality)
EQI quality pillar, country centered and z-score standardized. For its calculation, they aggregate
the individual scores (’survey question’) to the corresponding regional level, so that each of question
on the quality of public services is now a regional ’indicator’. After normalizing each of quality
indicators (through z-score standardization) so that they share a common range, the quality indi-
cators are aggregated into ’quality pillar’.
28

## Page 30

NUTS Level N
NUTS 0 (Country) 14
NUTS 1 39
NUTS 2 154
4.2.3 Impartiality pillar, country centered and z-score standardized (eqi zimpartial-
ity)
EQI impartiality pillar, country centered and z-score standardized. For its calculation, they aggre-
gate the individual scores (’survey question’) to the corresponding regional level, so that each of
question assessing impartiality in the provision of public services is now a regional ’indicator’. After
normalizing each of impartiality indicators (through z-score standardization) so that they share a
common range, the impartiality indicators are aggregated into ’impartiality pillar’.
NUTS Level N
NUTS 0 (Country) 14
NUTS 1 39
NUTS 2 154
29

## Page 31

4.2.4 Corruption pillar, country centered and z-score standardized (eqi zcorruption)
EQI corruption pillar, country centered and z-score standardized. For its calculation, they aggre-
gate the individual scores (’survey question’) to the corresponding regional level, so that each of
question assessing corruption in the provision of public services is now a regional ’indicator’. After
normalizing each of corruption indicators (through z-score standardization) so that they share a
common range, the corruption indicators are aggregated into two sub-pillars, called ’experience’
and ’perceptions. They respectively represent question items reecting personal experience with
petty corruption versus perception of corruption in various other areas. These two sub-pillars are
aggregated using equal weighting.
NUTS Level N
NUTS 0 (Country) 14
NUTS 1 39
NUTS 2 154
4.2.5 Corruption perceptions index (corruption sub-pillar) z-score stand. (2017 only)
(eqi zcorruptper)
EQI corruption perceptions index, z-score standardized. It constitutes one of the sub-pillars of
corruption pillar.
30

## Page 32

NUTS Level N
NUTS 0 (Country) NA
NUTS 1 39
NUTS 2 154
4.2.6 Corruption experiences index (corruption sub-pillar) z-score stand. (2017 only)
(eqi zcorruptexp)
EQI corruption experiences index, z-score standardized. It constitutes one of the sub-pillars of
corruption pillar.
NUTS Level N
NUTS 0 (Country) NA
NUTS 1 39
NUTS 2 154
4.2.7 EQI index, min-max (0-100) standardized (eqi norm eqi)
EQI index, min-max (0-100) standardized. Detailed information on its calculation method and
indicators used for this aggregation can be found inEuropean Quality of Government Index 2017
Codebook.
31

## Page 33

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 39
NUTS 2 155
4.2.8 Quality pillar, country centered and min-max (0-100) standardized (eqi norm -
qual)
Quality pillar, country centered and min-max (0-100) standardized.
NUTS Level N
NUTS 0 (Country) 14
NUTS 1 39
NUTS 2 154
4.2.9 Impartiality pillar, country centered and min-max (0-100) standardized (eqi -
norm impart)
Impartiality pillar, country centered and min-max (0-100) standardized.
32

## Page 34

NUTS Level N
NUTS 0 (Country) 14
NUTS 1 39
NUTS 2 154
4.2.10 Corruption pillar, country centered and min-max (0-100) standardized (eqi -
norm corrupt)
Corruption pillar, country centered and min-max (0-100) standardized.
NUTS Level N
NUTS 0 (Country) 14
NUTS 1 39
NUTS 2 154
4.2.11 Corruption perceptions index (corruption sub-pillar) min-max (0-100)(2017)
(eqi norm corruptper)
Corruption perceptions index (corruption sub-pillar), min-max (0-100) standardized.
33

## Page 35

NUTS Level N
NUTS 0 (Country) NA
NUTS 1 39
NUTS 2 154
4.2.12 Corruption experiences index (corruption sub-pillar) min-max (0-100) (2017)
(eqi norm corruptexp)
Corruption experiences index (corruption sub-pillar) min-max (0-100) standardized.
NUTS Level N
NUTS 0 (Country) NA
NUTS 1 39
NUTS 2 154
34

## Page 36

4.3 Corruption Risks Indicators: The Corruption Risks Indicators dataset
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Mihaly Fazekas and Gabor Kocsis.Uncovering High-Level Corruption: Cross-National Ob-
jective Corruption Risk Indicators Using Public Procurement Data. 2017
Dataset found at:https://opentender.eu/download
Measuring high-level corruption is subject to extensive scholarly and policy interest, which has
achieved moderate progress in the last decade. This dataset presents four objective proxy measures
of high-level corruption in public procurement: single bidding in competitive markets, the share of
contracts withno published call for tenderredag, theshare of contracts with non-open pro-
cedureredag, andshare of contracts with tax havenredag. Using ocial government data
on 4 million contracts in thirty-two European countries from 2011 to 2019, the authors directly op-
erationalize a common denition of corruption: unjustied restriction of access to public contracts
to favour a selected bidder. Corruption indicators are calculated at the contract level, but produce
aggregate indices consistent with well-established country-level indicators, and are also validated
by micro-level tests. The regional sample diers from the country-level sample, because the authors
haveltered out central government buying entities for the regional analysis. The denition the
authors use is based on TED’s buyer type variable. They consider the following types as ’local
entities’: ’REGIONALAUTHORITY’, ’REGIONALAGENCY’, ’UTILITIES’.
35

## Page 37

4.3.1 Number of awarded contracts above 130,000 EUR (cri contr)
Number of successfully awarded contracts within tenders published on TED above 130k EUR thresh-
old.
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 100
NUTS 2 260
4.3.2 Final value of awarded tenders of over 130,000 EUR (cri cvalue)
Sum of thenal value of successfully awarded tenders published on TED above 130k EUR threshold.
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 100
NUTS 2 260
36

## Page 38

4.3.3 Share of contracts with only one bid in total (cri singleb)
Share of contracts with only one bid in total.
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 100
NUTS 2 259
4.3.4 Share of contracts with no published call for tender redag (cri nocall)
Share of contracts withno published call for tenderredag. Contract is considered to haveno
call for tenderredag if two conditions are met: i) sum of prior information notices and contract
notices equals 0 and ii) country of a buyer is not on the list of countries in whichno call for tender
publicationis not a risk factor. These countries are BG, DK, EE, ES, LT.
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 100
NUTS 2 260
37

## Page 39

4.3.5 Share of contracts with non-open procedure redag (cri nonopen)
Share of contracts withnon-open procedureredag. Whether procedure is considered non-open
depends on procedure type as well as specic country regulation. Please refer to theNon-open
procedure detailssheet to search for country-procedure combinations.
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 100
NUTS 2 260
4.3.6 Share of contracts with tax haven redag (cri taxhav)
Share of contracts withtax havenredag. Contract hastax havenredag in case two con-
ditions are met: i) buyer and supplier are from dierent countries and ii) according to Financial
Secrecy Index (https://www.nancialsecrecyindex.com/en/) supplier country was classied as tax
haven.
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 100
NUTS 2 260
38

## Page 40

4.4 Eurostat: Regional statistics by NUTS classication
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
European Commission.Eurostat. 2020.url:http : / / ec . europa . eu / eurostat / data /
database
Dataset found at:https://ec.europa.eu/eurostat/web/regions/data/database
Eurostat is the statistical oce of the European Union. It produces European statistics in partner-
ship with National Statistical Institutes and other national authorities in the EU Member States.
This partnership is known as the European Statistical System (ESS). It also includes the statistical
authorities of the European Economic Area (EEA) countries and Switzerland. Nationalgures
alone cannot reveal the full and sometimes complex picture of what is happening at a more detailed
level within the European Union (EU). In this respect, statistical information at a subnational level
is an important tool for highlighting specic regional and territorial aspects. It helps in analysing
changing patterns and the impact that policy decisions can have on our daily life. In order to
provide a detailed picture of the diverse EU territories and to monitor EU regional policy targets,
Eurostat has developed a range of statistics based on dierent classications and typologies. At
the heart of regional statistics is the NUTS classication - the classication of territorial units
for statistics. This is a regional classication for the EU Member States providing a harmonised
hierarchy of regions: the NUTS classication subdivides each Member State into regions at three
dierent levels, covering NUTS 1, 2 and 3 from larger to smaller areas. Regions have also been
dened and agreed with the EFTA and candidate countries on a bilateral basis; these are called
statistical regions and follow exactly the same rules as the NUTS regions in the EU, although they
have no legal basis.
39

## Page 41

4.4.1 Population at 1st January, female (eu d2jan f )
Female population as of 1st January of the year indicated. It is based on concept of usual resident
population, i.e. the number of inhabitants of a given area on 1 January of the year in question
(or, in some cases, on 31 December of the previous year). The populationgures can be based on
data from the most recent census adjusted by the components of population change produced since
the last census, or based on population registers. Usually resident population means all persons
having usual residence in a country at the reference time. Usual residence means the place where
a person normally spends the daily period of rest, regardless of temporary absences for purposes
of recreation, holidays, visits to friends and relatives, business, medical treatment or religious pil-
grimage. The following persons alone are considered to be usual residents of the geographical area
in question: a) those who have lived in their place of usual residence for a continuous period of at
least 12 months before the reference time; or b) those who arrived in their place of usual residence
during the 12 months before the reference time with the intention of staying there for at least one
year.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 108
NUTS 2 262
4.4.2 Population at 1st January, male (eu d2jan m)
Male population as of 1st January of the year indicated. It is based on concept of usual resident
population, i.e. the number of inhabitants of a given area on 1 January of the year in question
(or, in some cases, on 31 December of the previous year). The populationgures can be based on
data from the most recent census adjusted by the components of population change produced since
the last census, or based on population registers. Usually resident population means all persons
having usual residence in a country at the reference time. Usual residence means the place where
a person normally spends the daily period of rest, regardless of temporary absences for purposes
of recreation, holidays, visits to friends and relatives, business, medical treatment or religious pil-
grimage. The following persons alone are considered to be usual residents of the geographical area
in question: a) those who have lived in their place of usual residence for a continuous period of at
least 12 months before the reference time; or b) those who arrived in their place of usual residence
40

## Page 42

during the 12 months before the reference time with the intention of staying there for at least one
year.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 108
NUTS 2 262
4.4.3 Population at 1st January, total (eu d2jan t)
Total population as of 1st January of the year indicated. It is based on concept of usual resident
population, i.e. the number of inhabitants of a given area on 1 January of the year in question
(or, in some cases, on 31 December of the previous year). The populationgures can be based on
data from the most recent census adjusted by the components of population change produced since
the last census, or based on population registers. Usually resident population means all persons
having usual residence in a country at the reference time. Usual residence means the place where
a person normally spends the daily period of rest, regardless of temporary absences for purposes
of recreation, holidays, visits to friends and relatives, business, medical treatment or religious pil-
grimage. The following persons alone are considered to be usual residents of the geographical area
in question: a) those who have lived in their place of usual residence for a continuous period of at
least 12 months before the reference time; or b) those who arrived in their place of usual residence
during the 12 months before the reference time with the intention of staying there for at least one
year.
41

## Page 43

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 108
NUTS 2 262
4.4.4 Crude rate of net migration plus statistical adjustment (eu cnmigratrt)
Crude rate of net migration plus statistical adjustment. Net migration including statistical ad-
justments the ratio of the net migration including statistical adjustment during the year to the
average population in that year. The value is expressed per 1000 inhabitants. The crude rate of
net migration is equal to the dierence between the crude rate of population change and the crude
rate of natural change (that is, net migration is considered as the part of population change not
attributable to births and deaths). It is calculated in this way because immigration or emigration
ows are either not available or thegures are not reliable.
NUTS Level N
NUTS 0 (Country) NA
NUTS 1 1
NUTS 2 275
42

## Page 44

4.4.5 Crude rate of total population change (eu growrt)
Crude rate of total population change. It is the ratio of the total population change during the
year to the average population of the area in question in that year. The value is expressed per 1000
inhabitants.
NUTS Level N
NUTS 0 (Country) NA
NUTS 1 1
NUTS 2 279
4.4.6 Crude rate of natural change of population (eu natgrowrt)
Crude rate of natural change. It is the ratio of natural change over a period to the average popu-
lation of the area in question during that period. The value is expressed per 1000 inhabitants.
NUTS Level N
NUTS 0 (Country) NA
NUTS 1 1
NUTS 2 275
43

## Page 45

4.4.7 Area of a region, land area total, sq km (eu d3area lat)
Total land area of a region as square kilometer. Total Land Area (TLA) is dened as total surface
area excluding lakes, rivers, transitional and coastal waters. Mountainous regions, glaciers, forests,
wetlands and other temporarily or permanently uninhabitable regions are included in TLA.
NUTS Level N
NUTS 0 (Country) 19
NUTS 1 51
NUTS 2 153
4.4.8 Area of a region, total, sq km (eu d3area t)
Total surface area of a region as square kilometer. Total Surface Area (TSA) is dened as the area
of any given statistical area and includes land area and inland waters (lakes, rivers etc.). The sub-
national areas (e.g. LAU and NUTS areas) dened by statistical and/or administrative boundaries
are the building blocks for calculating both concepts. By denition Total Surface Area does not
cover areas that are not statistical areas.
44

## Page 46

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 89
NUTS 2 247
4.4.9 Population density, average population per square km (eu per km2)
Average population density per square km. Population density is the ratio of the (annual average)
population of a region to the (land) area of the region; total area (including inland waters) is used
when land area is not available.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 248
4.4.10 Number of deaths of females, all ages (eu death totalf )
Number of deaths of females, all ages. Death means the permanent disappearance of all evidence
of life at any time after life birth has taken place (postnatal cessation of vital functions without
capability of resuscitation).
45

## Page 47

NUTS Level N
NUTS 0 (Country) 26
NUTS 1 NA
NUTS 2 NA
4.4.11 Number of deaths of males, all ages (eu death totalm)
Number of deaths of males, all ages. Death means the permanent disappearance of all evidence
of life at any time after life birth has taken place (postnatal cessation of vital functions without
capability of resuscitation).
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 NA
NUTS 2 NA
4.4.12 Number of deaths, total all ages (eu death totalt)
Number of deaths, all ages. Death means the permanent disappearance of all evidence of life at
any time after life birth has taken place (postnatal cessation of vital functions without capability
46

## Page 48

of resuscitation).
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 NA
NUTS 2 NA
4.4.13 Number of deaths of females, at 1 year old (eu death y1f )
Number of deaths of females, at 1 year old. Death means the permanent disappearance of all
evidence of life at any time after life birth has taken place (postnatal cessation of vital functions
without capability of resuscitation).
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 NA
NUTS 2 NA
47

## Page 49

4.4.14 Number of deaths of males, at 1 year old (eu death y1m)
Number of deaths of males, at 1 year old. Death means the permanent disappearance of all evidence
of life at any time after life birth has taken place (postnatal cessation of vital functions without
capability of resuscitation).
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 NA
NUTS 2 NA
4.4.15 Number of deaths, total at 1 year old (eu death y1t)
Number of deaths, total at 1 year old. Death means the permanent disappearance of all evidence
of life at any time after life birth has taken place (postnatal cessation of vital functions without
capability of resuscitation).
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 NA
NUTS 2 NA
48

## Page 50

4.4.16 Number of deaths of females, at 20 years old (eu death y20f )
Number of deaths of females, at 20 years old. Death means the permanent disappearance of all
evidence of life at any time after life birth has taken place (postnatal cessation of vital functions
without capability of resuscitation).
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 NA
NUTS 2 NA
4.4.17 Number of deaths of males, at 20 years old (eu death y20m)
Number of deaths of males, at 20 years old. Death means the permanent disappearance of all
evidence of life at any time after life birth has taken place (postnatal cessation of vital functions
without capability of resuscitation).
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 NA
NUTS 2 NA
49

## Page 51

4.4.18 Number of deaths, total at 20 years old (eu death y20t)
Number of deaths, total at 20 years old. Death means the permanent disappearance of all evidence
of life at any time after life birth has taken place (postnatal cessation of vital functions without
capability of resuscitation).
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 NA
NUTS 2 NA
4.4.19 Number of deaths of females, at 50 years old (eu death y50f )
Number of deaths of females, at 50 years old. Death means the permanent disappearance of all
evidence of life at any time after life birth has taken place (postnatal cessation of vital functions
without capability of resuscitation).
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 NA
NUTS 2 NA
50

## Page 52

4.4.20 Number of deaths of males, at 50 years old (eu death y50m)
Number of deaths of males, at 50 years old. Death means the permanent disappearance of all
evidence of life at any time after life birth has taken place (postnatal cessation of vital functions
without capability of resuscitation).
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 NA
NUTS 2 NA
4.4.21 Number of deaths, total at 50 years old (eu death y50t)
Number of deaths, total at 50 years old. Death means the permanent disappearance of all evidence
of life at any time after life birth has taken place (postnatal cessation of vital functions without
capability of resuscitation).
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 NA
NUTS 2 NA
51

## Page 53

4.4.22 Number of deaths of females, at 70 years old (eu death y70f )
Number of deaths of females, at 70 years old. Death means the permanent disappearance of all
evidence of life at any time after life birth has taken place (postnatal cessation of vital functions
without capability of resuscitation).
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 NA
NUTS 2 NA
4.4.23 Number of deaths of males, at 70 years old (eu death y70m)
Number of deaths of males, at 70 years old. Death means the permanent disappearance of all
evidence of life at any time after life birth has taken place (postnatal cessation of vital functions
without capability of resuscitation).
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 NA
NUTS 2 NA
52

## Page 54

4.4.24 Number of deaths, total at 70 years old (eu death y70t)
Number of deaths, total at 70 years old. Death means the permanent disappearance of all evidence
of life at any time after life birth has taken place (postnatal cessation of vital functions without
capability of resuscitation).
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 NA
NUTS 2 NA
4.4.25 Fertility rate, total (eu frate total)
Total fertility rate. It is the mean number of children that would be born alive to a woman during
her lifetime if she were to pass through her childbearing years conforming to the fertility rates by
age of a given year.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 94
NUTS 2 227
53

## Page 55

4.4.26 Fertility rate, at age 15 (eu frate y15)
Fertility rate, at age 15. This age-specic fertility rate is calculated by dividing the number of
births of mothers of age 15 to the average female population of age 15.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 85
NUTS 2 201
4.4.27 Fertility rate, at age 30 (eu frate y30)
Fertility rate, at age 30. This age-specic fertility rate is calculated by dividing the number of
births of mothers of age 30 to the average female population of age 30.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 93
NUTS 2 225
54

## Page 56

4.4.28 Fertility rate, at age 35 (eu frate y35)
Fertility rate, at age 35. This age-specic fertility rate is calculated by dividing the number of
births of mothers of age 35 to the average female population of age 35.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 93
NUTS 2 225
4.4.29 Proportion of live births outside marriage (eu agemoth)
Proportion of live births outside marriage. A live birth outside marriage is dened as a live birth
where the mother’s marital status at the time of birth is other than married.
NUTS Level N
NUTS 0 (Country) 23
NUTS 1 NA
NUTS 2 NA
55

## Page 57

4.4.30 Total fertility rate (eu agemoth1)
Total fertility rate. It is dened as the mean number of children who would be born to a woman
during her lifetime, if she were to spend her childbearing years conforming to the age-specic fer-
tility rates, that have been measured in a given year.
NUTS Level N
NUTS 0 (Country) 13
NUTS 1 NA
NUTS 2 NA
4.4.31 Mean age of women at childbirth (eu nmarpct)
Mean age of women at childbirth. It is calculated as the mean age of women when their children
are born.
NUTS Level N
NUTS 0 (Country) 25
NUTS 1 NA
NUTS 2 NA
56

## Page 58

4.4.32 Mean age of women at birth ofrst child (eu totferrt)
Mean age of women at birth ofrst child. It is calculated as the mean age of women when their
rst children are born.
NUTS Level N
NUTS 0 (Country) 23
NUTS 1 NA
NUTS 2 NA
4.4.33 Life expectancy in years at 1 year old, female (eu mlifexp f )
Life expectancy in years at 1 year old, female. Life expectancy at given exact age is the mean number
of years still to be lived by a person who has reached a certain exact age, if subjected through-
out the rest of his or her life to the current mortality conditions (age-specic probabilities of dying).
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 94
NUTS 2 227
57

## Page 59

4.4.34 Life expectancy in years at 1 year old, male (eu mlifexp m)
Life expectancy in years at 1 year old, male. Life expectancy at given exact age is the mean number
of years still to be lived by a person who has reached a certain exact age, if subjected through-
out the rest of his or her life to the current mortality conditions (age-specic probabilities of dying).
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 94
NUTS 2 227
4.4.35 Life expectancy in years at 1 year old, total (eu mlifexp t)
Life expectancy in years at 1 year old, total. Life expectancy at given exact age is the mean number
of years still to be lived by a person who has reached a certain exact age, if subjected through-
out the rest of his or her life to the current mortality conditions (age-specic probabilities of dying).
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 94
NUTS 2 227
58

## Page 60

4.4.36 Business enterprise sector intramural expenditure in R&D, euro per inhabitant
(eu rdexp bes)
Business enterprise sector intramural expenditure in R&D, euro per inhabitant. Intramural R&D
expenditures are all current expenditures plus grossxed expenditure for R&D performed within a
statistical unit during a specic period, whatever the source of funds. Further information on the
concepts and denitions used for the production of R&D statistics can be found in Frascati Manual
(OECD 2015).
NUTS Level N
NUTS 0 (Country) 21
NUTS 1 65
NUTS 2 148
4.4.37 Government sector intramural expenditure in R&D, euro per inhabitant (eu -
rdexp gov)
Government sector intramural expenditure in R&D, euro per inhabitant. Intramural R&D ex-
penditures are all current expenditures plus grossxed expenditure for R&D performed within a
statistical unit during a specic period, whatever the source of funds. Further information on the
concepts and denitions used for the production of R&D statistics can be found in Frascati Manual
(OECD 2015).
59

## Page 61

NUTS Level N
NUTS 0 (Country) 21
NUTS 1 68
NUTS 2 151
4.4.38 Higher education sector intramural expenditure in R&D, euro per inhabitant
(eu rdexp hes)
Higher education sector intramural expenditure in R&D, euro per inhabitant. Intramural R&D
expenditures are all current expenditures plus grossxed expenditure for R&D performed within a
statistical unit during a specic period, whatever the source of funds. Further information on the
concepts and denitions used for the production of R&D statistics can be found in Frascati Manual
(OECD 2015).
NUTS Level N
NUTS 0 (Country) 21
NUTS 1 66
NUTS 2 149
60

## Page 62

4.4.39 Private non-prot sector intramural expenditure in R&D, euro per inhabitant
(eu rdexp pnp)
Private non-prot sector intramural expenditure in R&D, euro per inhabitant. Intramural R&D
expenditures are all current expenditures plus grossxed expenditure for R&D performed within a
statistical unit during a specic period, whatever the source of funds. Further information on the
concepts and denitions used for the production of R&D statistics can be found in Frascati Manual
(OECD 2015).
NUTS Level N
NUTS 0 (Country) 15
NUTS 1 33
NUTS 2 67
4.4.40 All sectors intramural expenditure in R&D, euro per inhabitant (eu rdexp -
total)
All sectors intramural expenditure in R&D, euro per inhabitant. Intramural R&D expenditures are
all current expenditures plus grossxed expenditure for R&D performed within a statistical unit
during a specic period, whatever the source of funds. Further information on the concepts and
denitions used for the production of R&D statistics can be found in Frascati Manual (OECD 2015).
61

## Page 63

NUTS Level N
NUTS 0 (Country) 22
NUTS 1 61
NUTS 2 148
4.4.41 Total R&D employees in business enterprise sector, female, full-time equiva-
lent (eu prd bes f )
Female R&D employees in business enterprise sector, full-time equivalent. R&D personnel in a
statistical unit include all persons engaged directly in R&D, whether employed by the statistical
unit or external contributors fully integrated into the statistical unit’s R&D activities, as well as
those providing direct services for the R&D activities (such as R&D managers, administrators,
technicians and clerical stra). Persons providing indirect support and ancillary services, such
as canteen, maintenance, administrative and security sta, has been excluded, even though their
wages and salaries are included inother current costswhen measuring R&D expenditure. Further
information on the concepts and denitions used for the production of R&D statistics can be found
in Frascati Manual (OECD 2015).
62

## Page 64

NUTS Level N
NUTS 0 (Country) 16
NUTS 1 7
NUTS 2 5
4.4.42 Total R&D employees in business enterprise sector, total, full-time equivalent
(eu prd bes t)
Total R&D employees in business enterprise sector, full-time equivalent. R&D personnel in a sta-
tistical unit include all persons engaged directly in R&D, whether employed by the statistical unit
or external contributors fully integrated into the statistical unit’s R&D activities, as well as those
providing direct services for the R&D activities (such as R&D managers, administrators, techni-
cians and clerical stra). Persons providing indirect support and ancillary services, such as canteen,
maintenance, administrative and security sta, has been excluded, even though their wages and
salaries are included inother current costswhen measuring R&D expenditure. Further infor-
mation on the concepts and denitions used for the production of R&D statistics can be found in
Frascati Manual (OECD 2015).
63

## Page 65

NUTS Level N
NUTS 0 (Country) 21
NUTS 1 55
NUTS 2 134
4.4.43 Total R&D employees in government sector, female, full-time equivalent (eu -
prd gov f )
Female R&D employees in government sector, full-time equivalent. R&D personnel in a statisti-
cal unit include all persons engaged directly in R&D, whether employed by the statistical unit or
external contributors fully integrated into the statistical unit’s R&D activities, as well as those pro-
viding direct services for the R&D activities (such as R&D managers, administrators, technicians
and clerical stra). Persons providing indirect support and ancillary services, such as canteen,
maintenance, administrative and security sta, has been excluded, even though their wages and
salaries are included inother current costswhen measuring R&D expenditure. Further infor-
mation on the concepts and denitions used for the production of R&D statistics can be found in
Frascati Manual (OECD 2015).
64

## Page 66

NUTS Level N
NUTS 0 (Country) 17
NUTS 1 7
NUTS 2 6
4.4.44 Total R&D employees in government sector, total, full-time equivalent (eu -
prd gov t)
Total R&D employees in government sector, full-time equivalent. R&D personnel in a statistical
unit include all persons engaged directly in R&D, whether employed by the statistical unit or exter-
nal contributors fully integrated into the statistical unit’s R&D activities, as well as those providing
direct services for the R&D activities (such as R&D managers, administrators, technicians and cler-
ical stra). Persons providing indirect support and ancillary services, such as canteen, maintenance,
administrative and security sta, has been excluded, even though their wages and salaries are in-
cluded inother current costswhen measuring R&D expenditure. Further information on the
concepts and denitions used for the production of R&D statistics can be found in Frascati Manual
(OECD 2015).
65

## Page 67

NUTS Level N
NUTS 0 (Country) 21
NUTS 1 57
NUTS 2 134
4.4.45 Total R&D employees in higher education sector, female, full-time equivalent
(eu prd hes f )
Female R&D employees in higher education sector, full-time equivalent. R&D personnel in a sta-
tistical unit include all persons engaged directly in R&D, whether employed by the statistical unit
or external contributors fully integrated into the statistical unit’s R&D activities, as well as those
providing direct services for the R&D activities (such as R&D managers, administrators, techni-
cians and clerical stra). Persons providing indirect support and ancillary services, such as canteen,
maintenance, administrative and security sta, has been excluded, even though their wages and
salaries are included inother current costswhen measuring R&D expenditure. Further infor-
mation on the concepts and denitions used for the production of R&D statistics can be found in
Frascati Manual (OECD 2015).
66

## Page 68

NUTS Level N
NUTS 0 (Country) 17
NUTS 1 7
NUTS 2 6
4.4.46 Total R&D employees in higher education sector, total, full-time equivalent
(eu prd hes t)
Total R&D employees in higher education sector, full-time equivalent. R&D personnel in a statis-
tical unit include all persons engaged directly in R&D, whether employed by the statistical unit
or external contributors fully integrated into the statistical unit’s R&D activities, as well as those
providing direct services for the R&D activities (such as R&D managers, administrators, techni-
cians and clerical stra). Persons providing indirect support and ancillary services, such as canteen,
maintenance, administrative and security sta, has been excluded, even though their wages and
salaries are included inother current costswhen measuring R&D expenditure. Further infor-
mation on the concepts and denitions used for the production of R&D statistics can be found in
Frascati Manual (OECD 2015).
67

## Page 69

NUTS Level N
NUTS 0 (Country) 21
NUTS 1 51
NUTS 2 126
4.4.47 Total R&D employees in private non-prot sector, female, full-time equivalent
(eu prd pnp f )
Female R&D employees in private non-prot sector, full-time equivalent. R&D personnel in a sta-
tistical unit include all persons engaged directly in R&D, whether employed by the statistical unit
or external contributors fully integrated into the statistical unit’s R&D activities, as well as those
providing direct services for the R&D activities (such as R&D managers, administrators, techni-
cians and clerical stra). Persons providing indirect support and ancillary services, such as canteen,
maintenance, administrative and security sta, has been excluded, even though their wages and
salaries are included inother current costswhen measuring R&D expenditure. Further infor-
mation on the concepts and denitions used for the production of R&D statistics can be found in
Frascati Manual (OECD 2015).
68

## Page 70

NUTS Level N
NUTS 0 (Country) 12
NUTS 1 4
NUTS 2 3
4.4.48 Total R&D employees in private non-prot sector, total, full-time equivalent
(eu prd pnp t)
Total R&D employees in private non-prot sector, full-time equivalent. R&D personnel in a sta-
tistical unit include all persons engaged directly in R&D, whether employed by the statistical unit
or external contributors fully integrated into the statistical unit’s R&D activities, as well as those
providing direct services for the R&D activities (such as R&D managers, administrators, techni-
cians and clerical stra). Persons providing indirect support and ancillary services, such as canteen,
maintenance, administrative and security sta, has been excluded, even though their wages and
salaries are included inother current costswhen measuring R&D expenditure. Further infor-
mation on the concepts and denitions used for the production of R&D statistics can be found in
Frascati Manual (OECD 2015).
69

## Page 71

NUTS Level N
NUTS 0 (Country) 16
NUTS 1 29
NUTS 2 65
4.4.49 Total R&D employees in all sectors, female, full-time equivalent (eu prd total -
f )
Female R&D employees in all sectors, full-time equivalent. R&D personnel in a statistical unit
include all persons engaged directly in R&D, whether employed by the statistical unit or external
contributors fully integrated into the statistical unit’s R&D activities, as well as those providing
direct services for the R&D activities (such as R&D managers, administrators, technicians and
clerical stra). Persons providing indirect support and ancillary services, such as canteen, mainte-
nance, administrative and security sta, has been excluded, even though their wages and salaries
are included inother current costswhen measuring R&D expenditure. Further information on
the concepts and denitions used for the production of R&D statistics can be found in Frascati
Manual (OECD 2015).
70

## Page 72

NUTS Level N
NUTS 0 (Country) 15
NUTS 1 6
NUTS 2 4
4.4.50 Total R&D employees in all sectors, total, full-time equivalent (eu prd total t)
Total R&D employees in all sectors, full-time equivalent. R&D personnel in a statistical unit in-
clude all persons engaged directly in R&D, whether employed by the statistical unit or external
contributors fully integrated into the statistical unit’s R&D activities, as well as those providing
direct services for the R&D activities (such as R&D managers, administrators, technicians and
clerical stra). Persons providing indirect support and ancillary services, such as canteen, mainte-
nance, administrative and security sta, has been excluded, even though their wages and salaries
are included inother current costswhen measuring R&D expenditure. Further information on
the concepts and denitions used for the production of R&D statistics can be found in Frascati
Manual (OECD 2015).
NUTS Level N
NUTS 0 (Country) 20
NUTS 1 48
NUTS 2 130
71

## Page 73

4.4.51 Employment in agriculture, forestry andshing; mining and quarrying, as
percentage of total employment, female (eu emtk ab f )
Female employment in agriculture, forestry andshing; mining and quarrying, as percentage of
total female employment. Data come from EU Labour force survey (LFS). Employed people are
dened as persons aged 15 years and over who during the reference week performed work, even for
just one hour a week, for pay, prot or family gain or were not at work but had a job or business
from which they were temporarily absent because of, e.g., illness, holidays, industrial dispute and
education and training. In high-tech statistics the population excludes anyone below the age of 15
or over the age of 74. The data are aggregated based on the statistical classication of economic
activities in the European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 91
NUTS 2 188
4.4.52 Employment in agriculture, forestry andshing; mining and quarrying, as
percentage of total employment, male (eu emtk ab m)
Male employment in agriculture, forestry andshing; mining and quarrying, as percentage of total
male employment. Data come from EU Labour force survey (LFS). Employed people are dened
as persons aged 15 years and over who during the reference week performed work, even for just one
hour a week, for pay, prot or family gain or were not at work but had a job or business from which
they were temporarily absent because of, e.g., illness, holidays, industrial dispute and education
and training. In high-tech statistics the population excludes anyone below the age of 15 or over the
age of 74. The data are aggregated based on the statistical classication of economic activities in
the European Community (NACE) at 2-digit level.
72

## Page 74

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 251
4.4.53 Employment in agriculture, forestry andshing; mining and quarrying, as
percentage of total employment, total (eu emtk ab t)
Employment in agriculture, forestry andshing; mining and quarrying, as percentage of total em-
ployment. Data come from EU Labour force survey (LFS). Employed people are dened as persons
aged 15 years and over who during the reference week performed work, even for just one hour a
week, for pay, prot or family gain or were not at work but had a job or business from which they
were temporarily absent because of, e.g., illness, holidays, industrial dispute and education and
training. In high-tech statistics the population excludes anyone below the age of 15 or over the age
of 74. The data are aggregated based on the statistical classication of economic activities in the
European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 260
73

## Page 75

4.4.54 Employment in manufacturing, as percentage of total employment, female
(eu emtk c f )
Female employment in manufacturing, as percentage of total female employment. Data come from
EU Labour force survey (LFS). Employed people are dened as persons aged 15 years and over who
during the reference week performed work, even for just one hour a week, for pay, prot or family
gain or were not at work but had a job or business from which they were temporarily absent because
of, e.g., illness, holidays, industrial dispute and education and training. In high-tech statistics the
population excludes anyone below the age of 15 or over the age of 74. The data are aggregated
based on the statistical classication of economic activities in the European Community (NACE)
at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 263
4.4.55 Employment in manufacturing, as percentage of total employment, male (eu -
emtk c m)
Male employment in manufacturing, as percentage of total male employment. Data come from EU
Labour force survey (LFS). Employed people are dened as persons aged 15 years and over who
during the reference week performed work, even for just one hour a week, for pay, prot or family
gain or were not at work but had a job or business from which they were temporarily absent because
of, e.g., illness, holidays, industrial dispute and education and training. In high-tech statistics the
population excludes anyone below the age of 15 or over the age of 74. The data are aggregated
based on the statistical classication of economic activities in the European Community (NACE)
at 2-digit level.
74

## Page 76

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 101
NUTS 2 270
4.4.56 Employment in manufacturing, as percentage of total employment, total (eu -
emtk c t)
Employment in manufacturing, as percentage of total employment. Data come from EU Labour
force survey (LFS). Employed people are dened as persons aged 15 years and over who during
the reference week performed work, even for just one hour a week, for pay, prot or family gain
or were not at work but had a job or business from which they were temporarily absent because
of, e.g., illness, holidays, industrial dispute and education and training. In high-tech statistics the
population excludes anyone below the age of 15 or over the age of 74. The data are aggregated
based on the statistical classication of economic activities in the European Community (NACE)
at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 102
NUTS 2 272
75

## Page 77

4.4.57 Employment in high-technology manufacturing, as percentage of total employ-
ment, female (eu emtk chtc f )
Female employment in high-technology manufacturing, as percentage of total female employment.
Data come from EU Labour force survey (LFS). Employed people are dened as persons aged 15
years and over who during the reference week performed work, even for just one hour a week, for
pay, prot or family gain or were not at work but had a job or business from which they were
temporarily absent because of, e.g., illness, holidays, industrial dispute and education and training.
In high-tech statistics the population excludes anyone below the age of 15 or over the age of 74. The
data are aggregated based on the statistical classication of economic activities in the European
Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 75
NUTS 2 106
4.4.58 Employment in high-technology manufacturing, as percentage of total employ-
ment, male (eu emtk chtc m)
Male employment in high-technology manufacturing, as percentage of total male employment. Data
come from EU Labour force survey (LFS). Employed people are dened as persons aged 15 years
and over who during the reference week performed work, even for just one hour a week, for pay,
prot or family gain or were not at work but had a job or business from which they were temporarily
absent because of, e.g., illness, holidays, industrial dispute and education and training. In high-tech
statistics the population excludes anyone below the age of 15 or over the age of 74. The data are
aggregated based on the statistical classication of economic activities in the European Community
(NACE) at 2-digit level.
76

## Page 78

NUTS Level N
NUTS 0 (Country) 26
NUTS 1 86
NUTS 2 155
4.4.59 Employment in high-technology manufacturing, as percentage of total employ-
ment, total (eu emtk chtc t)
Employment in high-technology manufacturing, as percentage of total employment. Data come
from EU Labour force survey (LFS). Employed people are dened as persons aged 15 years and
over who during the reference week performed work, even for just one hour a week, for pay, prot
or family gain or were not at work but had a job or business from which they were temporarily
absent because of, e.g., illness, holidays, industrial dispute and education and training. In high-tech
statistics the population excludes anyone below the age of 15 or over the age of 74. The data are
aggregated based on the statistical classication of economic activities in the European Community
(NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 92
NUTS 2 190
77

## Page 79

4.4.60 Employment in electricity, gas, steam and air conditioning supply; water sup-
ply and construction, as percentage of total employment, female (eu emtk -
df f )
Female employment in electricity, gas, steam and air conditioning supply; water supply and con-
struction, as percentage of total female employment. Data come from EU Labour force survey
(LFS). Employed people are dened as persons aged 15 years and over who during the reference
week performed work, even for just one hour a week, for pay, prot or family gain or were not at
work but had a job or business from which they were temporarily absent because of, e.g., illness,
holidays, industrial dispute and education and training. In high-tech statistics the population ex-
cludes anyone below the age of 15 or over the age of 74. The data are aggregated based on the
statistical classication of economic activities in the European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 223
4.4.61 Employment in electricity, gas, steam and air conditioning supply; water sup-
ply and construction, as percentage of total employment, male (eu emtk df m)
Male employment in electricity, gas, steam and air conditioning supply; water supply and construc-
tion, as percentage of total male employment. Data come from EU Labour force survey (LFS).
Employed people are dened as persons aged 15 years and over who during the reference week
performed work, even for just one hour a week, for pay, prot or family gain or were not at work
but had a job or business from which they were temporarily absent because of, e.g., illness, holi-
days, industrial dispute and education and training. In high-tech statistics the population excludes
anyone below the age of 15 or over the age of 74. The data are aggregated based on the statistical
classication of economic activities in the European Community (NACE) at 2-digit level.
78

## Page 80

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 275
4.4.62 Employment in electricity, gas, steam and air conditioning supply; water sup-
ply and construction, as percentage of total employment, total (eu emtk df t)
Employment in electricity, gas, steam and air conditioning supply; water supply and construction,
as percentage of total employment. Data come from EU Labour force survey (LFS). Employed
people are dened as persons aged 15 years and over who during the reference week performed
work, even for just one hour a week, for pay, prot or family gain or were not at work but had a job
or business from which they were temporarily absent because of, e.g., illness, holidays, industrial
dispute and education and training. In high-tech statistics the population excludes anyone below
the age of 15 or over the age of 74. The data are aggregated based on the statistical classication
of economic activities in the European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 276
79

## Page 81

4.4.63 Employment in services, as percentage of total employment, female (eu emtk -
gu f )
Female employment in services, as percentage of total female employment. Data come from EU
Labour force survey (LFS). Employed people are dened as persons aged 15 years and over who
during the reference week performed work, even for just one hour a week, for pay, prot or family
gain or were not at work but had a job or business from which they were temporarily absent because
of, e.g., illness, holidays, industrial dispute and education and training. In high-tech statistics the
population excludes anyone below the age of 15 or over the age of 74. The data are aggregated
based on the statistical classication of economic activities in the European Community (NACE)
at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 104
NUTS 2 277
4.4.64 Employment in services, as percentage of total employment, male (eu emtk -
gu m)
Male employment in services, as percentage of total male employment. Data come from EU Labour
force survey (LFS). Employed people are dened as persons aged 15 years and over who during
the reference week performed work, even for just one hour a week, for pay, prot or family gain
or were not at work but had a job or business from which they were temporarily absent because
of, e.g., illness, holidays, industrial dispute and education and training. In high-tech statistics the
population excludes anyone below the age of 15 or over the age of 74. The data are aggregated
based on the statistical classication of economic activities in the European Community (NACE)
at 2-digit level.
80

## Page 82

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 104
NUTS 2 277
4.4.65 Employment in services, as percentage of total employment, total (eu emtk -
gu t)
Employment in services, as percentage of total employment. Data come from EU Labour force
survey (LFS). Employed people are dened as persons aged 15 years and over who during the ref-
erence week performed work, even for just one hour a week, for pay, prot or family gain or were
not at work but had a job or business from which they were temporarily absent because of, e.g.,
illness, holidays, industrial dispute and education and training. In high-tech statistics the popula-
tion excludes anyone below the age of 15 or over the age of 74. The data are aggregated based on
the statistical classication of economic activities in the European Community (NACE) at 2-digit
level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 104
NUTS 2 277
81

## Page 83

4.4.66 Employment in high-technology sectors (high-technology manufacturing and
knowledge-intensive high-technology services), as percentage of total employ-
ment, female (eu emtk htc f )
Female employment in high-technology sectors (high-technology manufacturing and knowledge-
intensive high-technology services), as percentage of total female employment. Data come from EU
Labour force survey (LFS). Employed people are dened as persons aged 15 years and over who
during the reference week performed work, even for just one hour a week, for pay, prot or family
gain or were not at work but had a job or business from which they were temporarily absent because
of, e.g., illness, holidays, industrial dispute and education and training. In high-tech statistics the
population excludes anyone below the age of 15 or over the age of 74. The data are aggregated
based on the statistical classication of economic activities in the European Community (NACE)
at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 97
NUTS 2 208
4.4.67 Employment in high-technology sectors (high-technology manufacturing and
knowledge-intensive high-technology services), as percentage of total employ-
ment, male (eu emtk htc m)
Male employment in high-technology sectors (high-technology manufacturing and knowledge-intensive
high-technology services), as percentage of total male employment. Data come from EU Labour
force survey (LFS). Employed people are dened as persons aged 15 years and over who during
the reference week performed work, even for just one hour a week, for pay, prot or family gain
or were not at work but had a job or business from which they were temporarily absent because
of, e.g., illness, holidays, industrial dispute and education and training. In high-tech statistics the
population excludes anyone below the age of 15 or over the age of 74. The data are aggregated
based on the statistical classication of economic activities in the European Community (NACE)
at 2-digit level.
82

## Page 84

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 242
4.4.68 Employment in high-technology sectors (high-technology manufacturing and
knowledge-intensive high-technology services), as percentage of total employ-
ment, total (eu emtk htc t)
Employment in high-technology sectors (high-technology manufacturing and knowledge-intensive
high-technology services), as percentage of total employment. Data come from EU Labour force
survey (LFS). Employed people are dened as persons aged 15 years and over who during the ref-
erence week performed work, even for just one hour a week, for pay, prot or family gain or were
not at work but had a job or business from which they were temporarily absent because of, e.g.,
illness, holidays, industrial dispute and education and training. In high-tech statistics the popula-
tion excludes anyone below the age of 15 or over the age of 74. The data are aggregated based on
the statistical classication of economic activities in the European Community (NACE) at 2-digit
level.
83

## Page 85

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 256
4.4.69 Employment in information and communication, as percentage of total em-
ployment, female (eu emtk j f )
Female employment in information and communication, as percentage of total female employment.
Data come from EU Labour force survey (LFS). Employed people are dened as persons aged 15
years and over who during the reference week performed work, even for just one hour a week, for
pay, prot or family gain or were not at work but had a job or business from which they were
temporarily absent because of, e.g., illness, holidays, industrial dispute and education and training.
In high-tech statistics the population excludes anyone below the age of 15 or over the age of 74. The
data are aggregated based on the statistical classication of economic activities in the European
Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 93
NUTS 2 176
84

## Page 86

4.4.70 Employment in information and communication, as percentage of total em-
ployment, male (eu emtk j m)
Male employment in information and communication, as percentage of total male employment.
Data come from EU Labour force survey (LFS). Employed people are dened as persons aged 15
years and over who during the reference week performed work, even for just one hour a week, for
pay, prot or family gain or were not at work but had a job or business from which they were
temporarily absent because of, e.g., illness, holidays, industrial dispute and education and training.
In high-tech statistics the population excludes anyone below the age of 15 or over the age of 74. The
data are aggregated based on the statistical classication of economic activities in the European
Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 229
4.4.71 Employment in information and communication, as percentage of total em-
ployment, total (eu emtk j t)
Employment in information and communication, as percentage of total employment. Data come
from EU Labour force survey (LFS). Employed people are dened as persons aged 15 years and
over who during the reference week performed work, even for just one hour a week, for pay, prot
or family gain or were not at work but had a job or business from which they were temporarily
absent because of, e.g., illness, holidays, industrial dispute and education and training. In high-tech
statistics the population excludes anyone below the age of 15 or over the age of 74. The data are
aggregated based on the statistical classication of economic activities in the European Community
(NACE) at 2-digit level.
85

## Page 87

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 248
4.4.72 Employment innancial and insurance activities, as percentage of total em-
ployment, female (eu emtk k f )
Female employment innancial and insurance activities, as percentage of total female employment.
Data come from EU Labour force survey (LFS). Employed people are dened as persons aged 15
years and over who during the reference week performed work, even for just one hour a week, for
pay, prot or family gain or were not at work but had a job or business from which they were
temporarily absent because of, e.g., illness, holidays, industrial dispute and education and training.
In high-tech statistics the population excludes anyone below the age of 15 or over the age of 74. The
data are aggregated based on the statistical classication of economic activities in the European
Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 99
NUTS 2 237
86

## Page 88

4.4.73 Employment innancial and insurance activities, as percentage of total em-
ployment, male (eu emtk k m)
Male employment innancial and insurance activities, as percentage of total male employment.
Data come from EU Labour force survey (LFS). Employed people are dened as persons aged 15
years and over who during the reference week performed work, even for just one hour a week, for
pay, prot or family gain or were not at work but had a job or business from which they were
temporarily absent because of, e.g., illness, holidays, industrial dispute and education and training.
In high-tech statistics the population excludes anyone below the age of 15 or over the age of 74. The
data are aggregated based on the statistical classication of economic activities in the European
Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 97
NUTS 2 215
4.4.74 Employment innancial and insurance activities, as percentage of total em-
ployment, total (eu emtk k t)
Employment innancial and insurance activities, as percentage of total employment. Data come
from EU Labour force survey (LFS). Employed people are dened as persons aged 15 years and
over who during the reference week performed work, even for just one hour a week, for pay, prot
or family gain or were not at work but had a job or business from which they were temporarily
absent because of, e.g., illness, holidays, industrial dispute and education and training. In high-tech
statistics the population excludes anyone below the age of 15 or over the age of 74. The data are
aggregated based on the statistical classication of economic activities in the European Community
(NACE) at 2-digit level.
87

## Page 89

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 259
4.4.75 Employment in total knowledge-intensive services, as percentage of total em-
ployment, female (eu emtk kis f )
Female employment in total knowledge-intensive services, as percentage of total female employ-
ment. Data come from EU Labour force survey (LFS). Employed people are dened as persons
aged 15 years and over who during the reference week performed work, even for just one hour a
week, for pay, prot or family gain or were not at work but had a job or business from which they
were temporarily absent because of, e.g., illness, holidays, industrial dispute and education and
training. In high-tech statistics the population excludes anyone below the age of 15 or over the age
of 74. The data are aggregated based on the statistical classication of economic activities in the
European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 104
NUTS 2 277
88

## Page 90

4.4.76 Employment in total knowledge-intensive services, as percentage of total em-
ployment, male (eu emtk kis m)
Male employment in total knowledge-intensive services, as percentage of total male employment.
Data come from EU Labour force survey (LFS). Employed people are dened as persons aged 15
years and over who during the reference week performed work, even for just one hour a week, for
pay, prot or family gain or were not at work but had a job or business from which they were
temporarily absent because of, e.g., illness, holidays, industrial dispute and education and training.
In high-tech statistics the population excludes anyone below the age of 15 or over the age of 74. The
data are aggregated based on the statistical classication of economic activities in the European
Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 104
NUTS 2 277
4.4.77 Employment in total knowledge-intensive services, as percentage of total em-
ployment, total (eu emtk kis t)
Employment in total knowledge-intensive services, as percentage of total employment. Data come
from EU Labour force survey (LFS). Employed people are dened as persons aged 15 years and
over who during the reference week performed work, even for just one hour a week, for pay, prot
or family gain or were not at work but had a job or business from which they were temporarily
absent because of, e.g., illness, holidays, industrial dispute and education and training. In high-tech
statistics the population excludes anyone below the age of 15 or over the age of 74. The data are
aggregated based on the statistical classication of economic activities in the European Community
(NACE) at 2-digit level.
89

## Page 91

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 104
NUTS 2 277
4.4.78 Employment innancial and insurance activities; real estate activities, as
percentage of total employment, female (eu emtk kl f )
Female employment innancial and insurance activities; real estate activities, as percentage of
total female employment. Data come from EU Labour force survey (LFS). Employed people are
dened as persons aged 15 years and over who during the reference week performed work, even for
just one hour a week, for pay, prot or family gain or were not at work but had a job or business
from which they were temporarily absent because of, e.g., illness, holidays, industrial dispute and
education and training. In high-tech statistics the population excludes anyone below the age of 15
or over the age of 74. The data are aggregated based on the statistical classication of economic
activities in the European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 99
NUTS 2 247
90

## Page 92

4.4.79 Employment innancial and insurance activities; real estate activities, as
percentage of total employment, male (eu emtk kl m)
Male employment innancial and insurance activities; real estate activities, as percentage of total
male employment. Data come from EU Labour force survey (LFS). Employed people are dened
as persons aged 15 years and over who during the reference week performed work, even for just one
hour a week, for pay, prot or family gain or were not at work but had a job or business from which
they were temporarily absent because of, e.g., illness, holidays, industrial dispute and education
and training. In high-tech statistics the population excludes anyone below the age of 15 or over the
age of 74. The data are aggregated based on the statistical classication of economic activities in
the European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 231
4.4.80 Employment innancial and insurance activities; real estate activities, as
percentage of total employment, total (eu emtk kl t)
Employment innancial and insurance activities; real estate activities, as percentage of total em-
ployment. Data come from EU Labour force survey (LFS). Employed people are dened as persons
aged 15 years and over who during the reference week performed work, even for just one hour a
week, for pay, prot or family gain or were not at work but had a job or business from which they
were temporarily absent because of, e.g., illness, holidays, industrial dispute and education and
training. In high-tech statistics the population excludes anyone below the age of 15 or over the age
of 74. The data are aggregated based on the statistical classication of economic activities in the
European Community (NACE) at 2-digit level.
91

## Page 93

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 266
4.4.81 Employment in professional, scientic and technical activities, as percentage
of total employment, female (eu emtk m f )
Female employment in professional, scientic and technical activities, as percentage of total female
employment. Data come from EU Labour force survey (LFS). Employed people are dened as
persons aged 15 years and over who during the reference week performed work, even for just one
hour a week, for pay, prot or family gain or were not at work but had a job or business from which
they were temporarily absent because of, e.g., illness, holidays, industrial dispute and education
and training. In high-tech statistics the population excludes anyone below the age of 15 or over the
age of 74. The data are aggregated based on the statistical classication of economic activities in
the European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 253
92

## Page 94

4.4.82 Employment in professional, scientic and technical activities, as percentage
of total employment, male (eu emtk m m)
Male employment in professional, scientic and technical activities, as percentage of total male em-
ployment. Data come from EU Labour force survey (LFS). Employed people are dened as persons
aged 15 years and over who during the reference week performed work, even for just one hour a
week, for pay, prot or family gain or were not at work but had a job or business from which they
were temporarily absent because of, e.g., illness, holidays, industrial dispute and education and
training. In high-tech statistics the population excludes anyone below the age of 15 or over the age
of 74. The data are aggregated based on the statistical classication of economic activities in the
European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 253
4.4.83 Employment in professional, scientic and technical activities, as percentage
of total employment, total (eu emtk m t)
Employment in professional, scientic and technical activities, as percentage of total employment.
Data come from EU Labour force survey (LFS). Employed people are dened as persons aged 15
years and over who during the reference week performed work, even for just one hour a week, for
pay, prot or family gain or were not at work but had a job or business from which they were
temporarily absent because of, e.g., illness, holidays, industrial dispute and education and training.
In high-tech statistics the population excludes anyone below the age of 15 or over the age of 74. The
data are aggregated based on the statistical classication of economic activities in the European
Community (NACE) at 2-digit level.
93

## Page 95

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 101
NUTS 2 270
4.4.84 Employment in administrative and support service activities, as percentage of
total employment, female (eu emtk n f )
Female employment in administrative and support service activities, as percentage of total female
employment. Data come from EU Labour force survey (LFS). Employed people are dened as
persons aged 15 years and over who during the reference week performed work, even for just one
hour a week, for pay, prot or family gain or were not at work but had a job or business from which
they were temporarily absent because of, e.g., illness, holidays, industrial dispute and education
and training. In high-tech statistics the population excludes anyone below the age of 15 or over the
age of 74. The data are aggregated based on the statistical classication of economic activities in
the European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 241
94

## Page 96

4.4.85 Employment in administrative and support service activities, as percentage of
total employment, male (eu emtk n m)
Male employment in administrative and support service activities, as percentage of total male em-
ployment. Data come from EU Labour force survey (LFS). Employed people are dened as persons
aged 15 years and over who during the reference week performed work, even for just one hour a
week, for pay, prot or family gain or were not at work but had a job or business from which they
were temporarily absent because of, e.g., illness, holidays, industrial dispute and education and
training. In high-tech statistics the population excludes anyone below the age of 15 or over the age
of 74. The data are aggregated based on the statistical classication of economic activities in the
European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 253
4.4.86 Employment in administrative and support service activities, as percentage of
total employment, total (eu emtk n t)
Employment in administrative and support service activities, as percentage of total employment.
Data come from EU Labour force survey (LFS). Employed people are dened as persons aged 15
years and over who during the reference week performed work, even for just one hour a week, for
pay, prot or family gain or were not at work but had a job or business from which they were
temporarily absent because of, e.g., illness, holidays, industrial dispute and education and training.
In high-tech statistics the population excludes anyone below the age of 15 or over the age of 74. The
data are aggregated based on the statistical classication of economic activities in the European
Community (NACE) at 2-digit level.
95

## Page 97

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 101
NUTS 2 271
4.4.87 Employment in public administration; activities of extraterritorial organisa-
tions and bodies, as percentage of total employment, female (eu emtk ou f )
Female employment in public administration; activities of extraterritorial organisations and bod-
ies, as percentage of total female employment. Data come from EU Labour force survey (LFS).
Employed people are dened as persons aged 15 years and over who during the reference week
performed work, even for just one hour a week, for pay, prot or family gain or were not at work
but had a job or business from which they were temporarily absent because of, e.g., illness, holi-
days, industrial dispute and education and training. In high-tech statistics the population excludes
anyone below the age of 15 or over the age of 74. The data are aggregated based on the statistical
classication of economic activities in the European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 102
NUTS 2 275
96

## Page 98

4.4.88 Employment in public administration; activities of extraterritorial organisa-
tions and bodies, as percentage of total employment, male (eu emtk ou m)
Male employment in public administration; activities of extraterritorial organisations and bodies, as
percentage of total male employment. Data come from EU Labour force survey (LFS). Employed
people are dened as persons aged 15 years and over who during the reference week performed
work, even for just one hour a week, for pay, prot or family gain or were not at work but had a job
or business from which they were temporarily absent because of, e.g., illness, holidays, industrial
dispute and education and training. In high-tech statistics the population excludes anyone below
the age of 15 or over the age of 74. The data are aggregated based on the statistical classication
of economic activities in the European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 275
4.4.89 Employment in public administration; activities of extraterritorial organisa-
tions and bodies, as percentage of total employment, total (eu emtk ou t)
Employment in public administration; activities of extraterritorial organisations and bodies, as per-
centage of total employment. Data come from EU Labour force survey (LFS). Employed people are
dened as persons aged 15 years and over who during the reference week performed work, even for
just one hour a week, for pay, prot or family gain or were not at work but had a job or business
from which they were temporarily absent because of, e.g., illness, holidays, industrial dispute and
education and training. In high-tech statistics the population excludes anyone below the age of 15
or over the age of 74. The data are aggregated based on the statistical classication of economic
activities in the European Community (NACE) at 2-digit level.
97

## Page 99

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 276
4.4.90 Employment in education, as percentage of total employment, female (eu -
emtk p f )
Female employment in education, as percentage of total female employment. Data come from EU
Labour force survey (LFS). Employed people are dened as persons aged 15 years and over who
during the reference week performed work, even for just one hour a week, for pay, prot or family
gain or were not at work but had a job or business from which they were temporarily absent because
of, e.g., illness, holidays, industrial dispute and education and training. In high-tech statistics the
population excludes anyone below the age of 15 or over the age of 74. The data are aggregated
based on the statistical classication of economic activities in the European Community (NACE)
at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 102
NUTS 2 275
98

## Page 100

4.4.91 Employment in education, as percentage of total employment, male (eu emtk -
p m)
Male employment in education, as percentage of total male employment. Data come from EU
Labour force survey (LFS). Employed people are dened as persons aged 15 years and over who
during the reference week performed work, even for just one hour a week, for pay, prot or family
gain or were not at work but had a job or business from which they were temporarily absent because
of, e.g., illness, holidays, industrial dispute and education and training. In high-tech statistics the
population excludes anyone below the age of 15 or over the age of 74. The data are aggregated
based on the statistical classication of economic activities in the European Community (NACE)
at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 265
4.4.92 Employment in education, as percentage of total employment, total (eu emtk -
p t)
Employment in education, as percentage of total employment. Data come from EU Labour force
survey (LFS). Employed people are dened as persons aged 15 years and over who during the ref-
erence week performed work, even for just one hour a week, for pay, prot or family gain or were
not at work but had a job or business from which they were temporarily absent because of, e.g.,
illness, holidays, industrial dispute and education and training. In high-tech statistics the popula-
tion excludes anyone below the age of 15 or over the age of 74. The data are aggregated based on
the statistical classication of economic activities in the European Community (NACE) at 2-digit
level.
99

## Page 101

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 276
4.4.93 Employment in human health and social work activities, as percentage of total
employment, female (eu emtk q f )
Female employment in human health and social work activities, as percentage of total female em-
ployment. Data come from EU Labour force survey (LFS). Employed people are dened as persons
aged 15 years and over who during the reference week performed work, even for just one hour a
week, for pay, prot or family gain or were not at work but had a job or business from which they
were temporarily absent because of, e.g., illness, holidays, industrial dispute and education and
training. In high-tech statistics the population excludes anyone below the age of 15 or over the age
of 74. The data are aggregated based on the statistical classication of economic activities in the
European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 104
NUTS 2 276
100

## Page 102

4.4.94 Employment in human health and social work activities, as percentage of total
employment, male (eu emtk q m)
Male employment in human health and social work activities, as percentage of total male employ-
ment. Data come from EU Labour force survey (LFS). Employed people are dened as persons
aged 15 years and over who during the reference week performed work, even for just one hour a
week, for pay, prot or family gain or were not at work but had a job or business from which they
were temporarily absent because of, e.g., illness, holidays, industrial dispute and education and
training. In high-tech statistics the population excludes anyone below the age of 15 or over the age
of 74. The data are aggregated based on the statistical classication of economic activities in the
European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 259
4.4.95 Employment in human health and social work activities, as percentage of total
employment, total (eu emtk q t)
Employment in human health and social work activities, as percentage of total employment. Data
come from EU Labour force survey (LFS). Employed people are dened as persons aged 15 years
and over who during the reference week performed work, even for just one hour a week, for pay,
prot or family gain or were not at work but had a job or business from which they were temporarily
absent because of, e.g., illness, holidays, industrial dispute and education and training. In high-tech
statistics the population excludes anyone below the age of 15 or over the age of 74. The data are
aggregated based on the statistical classication of economic activities in the European Community
(NACE) at 2-digit level.
101

## Page 103

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 104
NUTS 2 277
4.4.96 Employment in arts, entertainment and recreation, as percentage of total em-
ployment, female (eu emtk r f )
Female employment in arts, entertainment and recreation, as percentage of total female employ-
ment. Data come from EU Labour force survey (LFS). Employed people are dened as persons
aged 15 years and over who during the reference week performed work, even for just one hour a
week, for pay, prot or family gain or were not at work but had a job or business from which they
were temporarily absent because of, e.g., illness, holidays, industrial dispute and education and
training. In high-tech statistics the population excludes anyone below the age of 15 or over the age
of 74. The data are aggregated based on the statistical classication of economic activities in the
European Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 93
NUTS 2 190
102

## Page 104

4.4.97 Employment in arts, entertainment and recreation, as percentage of total em-
ployment, male (eu emtk r m)
Male employment in arts, entertainment and recreation, as percentage of total male employment.
Data come from EU Labour force survey (LFS). Employed people are dened as persons aged 15
years and over who during the reference week performed work, even for just one hour a week, for
pay, prot or family gain or were not at work but had a job or business from which they were
temporarily absent because of, e.g., illness, holidays, industrial dispute and education and training.
In high-tech statistics the population excludes anyone below the age of 15 or over the age of 74. The
data are aggregated based on the statistical classication of economic activities in the European
Community (NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 93
NUTS 2 188
4.4.98 Employment in arts, entertainment and recreation, as percentage of total em-
ployment, total (eu emtk r t)
Employment in arts, entertainment and recreation, as percentage of total employment. Data come
from EU Labour force survey (LFS). Employed people are dened as persons aged 15 years and
over who during the reference week performed work, even for just one hour a week, for pay, prot
or family gain or were not at work but had a job or business from which they were temporarily
absent because of, e.g., illness, holidays, industrial dispute and education and training. In high-tech
statistics the population excludes anyone below the age of 15 or over the age of 74. The data are
aggregated based on the statistical classication of economic activities in the European Community
(NACE) at 2-digit level.
103

## Page 105

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 99
NUTS 2 243
4.4.99 Employment in other service activities, as percentage of total employment,
female (eu emtk s f )
Female employment in other service activities, as percentage of total female employment. Data
come from EU Labour force survey (LFS). Employed people are dened as persons aged 15 years
and over who during the reference week performed work, even for just one hour a week, for pay,
prot or family gain or were not at work but had a job or business from which they were temporarily
absent because of, e.g., illness, holidays, industrial dispute and education and training. In high-tech
statistics the population excludes anyone below the age of 15 or over the age of 74. The data are
aggregated based on the statistical classication of economic activities in the European Community
(NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 247
104

## Page 106

4.4.100 Employment in other service activities, as percentage of total employment,
male (eu emtk s m)
Male employment in other service activities, as percentage of total male employment. Data come
from EU Labour force survey (LFS). Employed people are dened as persons aged 15 years and
over who during the reference week performed work, even for just one hour a week, for pay, prot
or family gain or were not at work but had a job or business from which they were temporarily
absent because of, e.g., illness, holidays, industrial dispute and education and training. In high-tech
statistics the population excludes anyone below the age of 15 or over the age of 74. The data are
aggregated based on the statistical classication of economic activities in the European Community
(NACE) at 2-digit level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 205
4.4.101 Employment in other service activities, as percentage of total employment,
total (eu emtk s t)
Employment in other service activities, as percentage of total employment. Data come from EU
Labour force survey (LFS). Employed people are dened as persons aged 15 years and over who
during the reference week performed work, even for just one hour a week, for pay, prot or family
gain or were not at work but had a job or business from which they were temporarily absent because
of, e.g., illness, holidays, industrial dispute and education and training. In high-tech statistics the
population excludes anyone below the age of 15 or over the age of 74. The data are aggregated
based on the statistical classication of economic activities in the European Community (NACE)
at 2-digit level.
105

## Page 107

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 266
4.4.102 Navigable canals, in kilometers (eu troad cnl)
Navigable canal - waterway built primarily for navigation.
NUTS Level N
NUTS 0 (Country) 14
NUTS 1 48
NUTS 2 81
4.4.103 Motorways, in kilometers (eu troad mway)
Motorway / freeway - road, specially designed and built for motor trac, which does not serve
properties bordering on it, and which: i) is provided, except at special points or temporarily, with
separate carriageways for trac in two directions, separated from each other, either by a dividing
strip not intended for trac, or exceptionally by other means; ii) has no crossings at the same
level with any road, railway or tramway track, or footpath; and iii) is especially sign-posted as a
106

## Page 108

motorway and is reserved for specic categories of road motor vehicles.
NUTS Level N
NUTS 0 (Country) 25
NUTS 1 96
NUTS 2 180
4.4.104 Other roads, in kilometers (eu troad rd oth)
Other roads, in kilometers.
NUTS Level N
NUTS 0 (Country) 24
NUTS 1 90
NUTS 2 167
4.4.105 Navigable rivers, in kilometers (eu troad riv)
Navigable river - natural waterway open for navigation, irrespective of whether it has been improved
for that purpose.
107

## Page 109

NUTS Level N
NUTS 0 (Country) 17
NUTS 1 54
NUTS 2 63
4.4.106 Total railway lines, in kilometers (eu troad rl)
Railway line - line of communication made up by rail exclusively for the use of railway vehicles.
Line of communication is an area equipped for the performance of rail transport.
NUTS Level N
NUTS 0 (Country) 25
NUTS 1 69
NUTS 2 141
4.4.107 Electried railway lines, in kilometers (eu troad rl elc)
Electried railway lines in kilometers.
108

## Page 110

NUTS Level N
NUTS 0 (Country) 24
NUTS 1 61
NUTS 2 129
4.4.108 Railway lines with double and more tracks, in kilometers (eu troad rl tge2)
Railway lines with double and more tracks in kilometers.
NUTS Level N
NUTS 0 (Country) 23
NUTS 1 58
NUTS 2 130
4.4.109 Total number of motor coaches, buses and trolley buses (eu vs bus tot)
Total number of motor coaches, buses and trolley buses. Motor coach is passenger road motor
vehicle designed to seat 24 or more persons (including the driver) and constructed exclusively for
the carriage of seated passengers. Bus is dened as passenger road motor vehicle designed to carry
more than 24 persons (including the driver), and with provision to carry seated as well as standing
passengers. Trolleybus is passenger road vehicle designed to seat more than nine persons (including
109

## Page 111

the driver), which is connected to electric conductors and which is not rail-borne. This term covers
vehicles which may be used either as trolleybuses or as buses, if they have a motor independent of
the main electric power supply.
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 94
NUTS 2 227
4.4.110 Total number of passenger cars (eu vs car)
Total number of passenger cars. Passenger car is a road motor vehicle, other than a moped or a
motor cycle, intended for the carriage of passengers and designed to seat no more than nine persons
(including the driver). Included are: passenger cars, vans designed and used primarily for transport
of passengers, taxis, hire cars, ambulances, motor homes. Excluded are light goods road vehicles,
as well as motor-coaches and buses, and mini-buses/mini-coaches.Passenger carincludes micro
cars (needing no permit to be driven), taxis and passenger hire cars, provided that they have fewer
than ten seats.
110

## Page 112

NUTS Level N
NUTS 0 (Country) 26
NUTS 1 94
NUTS 2 229
4.4.111 Total number of lorries (eu vs lor)
Total number of lorries. Lorry / truck is rigid road motor vehicle designed, exclusively or primarily,
to carry goods.
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 94
NUTS 2 229
4.4.112 Total number of motorcycles (eu vs moto)
Total number of motorcycles. Motorcycle is dened as two-, three- or four-wheeled road motor
vehicle not exceeding 400 kg (900 lb) of unladen weight. All such vehicles with a cylinder capac-
ity of 50 cc or over are included, as are those under 50 cc which do not meet the denition of moped.
111

## Page 113

NUTS Level N
NUTS 0 (Country) 25
NUTS 1 87
NUTS 2 215
4.4.113 Total number of special vehicles (eu vs spe)
Total number of special vehicles. Special purpose road motor vehicle is road motor vehicle designed
for purposes other than the carriage of passengers or goods. This category includes:re brigade
vehicles, mobile cranes, self-propelled rollers, bulldozers with metallic wheels or track, vehicles for
recordinglm, radio and TV broadcasting, mobile library vehicles, towing vehicles for vehicles in
need of repair, other special purpose road motor vehicles.
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 86
NUTS 2 218
112

## Page 114

4.4.114 Total number of all vehicles (except trailers and motorcycles) (eu vs tot x -
tm)
Total number of all vehicles except trailers and motorcycles.
NUTS Level N
NUTS 0 (Country) 21
NUTS 1 87
NUTS 2 210
4.4.115 Total number of road tractors (eu vs trc)
Total number of road tractors. Road tractor is road motor vehicle designed, exclusively or primarily,
to haul other road vehicles which are not power-driven (mainly semi-trailers). Agricultural tractors
are excluded.
NUTS Level N
NUTS 0 (Country) 23
NUTS 1 91
NUTS 2 223
113

## Page 115

4.4.116 Total number of trailers and semi-trailers (eu vs trl strl)
Total number of trailers and semi-trailers. Trailer is goods road vehicle designed to be hauled by a
road motor vehicle. This category excludes agricultural trailers and caravans. Semi-trailer describes
goods road vehicle with no front axle designed in such way that part of the vehicle and a substantial
part of its loaded weight rests on a road tractor.
NUTS Level N
NUTS 0 (Country) 21
NUTS 1 76
NUTS 2 181
4.4.117 Total number of total utility vehicles (eu vs utl)
Total number of total utility vehicles.
NUTS Level N
NUTS 0 (Country) 21
NUTS 1 88
NUTS 2 212
114

## Page 116

4.4.118 Injured victims in road accidents, per million inhabitants (eu rac inj)
Injured victims in road accidents, per million inhabitants. It includes any person who as result of
an injury accident was not killed immediately or not dying within 30 days, but sustained an injury,
normally needing medical treatment, excluding attempted suicides. Persons with lesser wounds,
such as minor cuts and bruises are not normally recorded as injured. An injured person is excluded
if the competent authority declares the cause of the injury to be attempted suicide by that person,
i.e. a deliberate act to injure oneself resulting in injury, but not in death.
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 93
NUTS 2 225
4.4.119 Killed victims in road accidents, per million inhabitants (eu rac kil)
Killed victims in road accidents, per million inhabitants. It includes any person killed immediately
or dying within 30 days as a result of an injury accident, excluding suicides. A killed person is
excluded if the competent authority declares the cause of death to be suicide, i.e. a deliberate act to
injure oneself resulting in death. For countries that do not apply the threshold of 30 days, conver-
sion coecients are estimated so that comparisons on the basis of the 30 day-denition can be made.
115

## Page 117

NUTS Level N
NUTS 0 (Country) 27
NUTS 1 95
NUTS 2 229
4.4.120 Maritime transport of freight loaded, in thousand tonnes (eu mtf fr ld)
Maritime transport of freight loaded in thousand tonnes. The maritime transport regional data have
been calculated using data collected at the port level in the frame of Council Directive 2009/42/EC
(6.5.2009). They are aggregated at regional level (NUTS 1 and NUTS 2) and also at national level
(NUTS0), excluding double counting within each region.
NUTS Level N
NUTS 0 (Country) 20
NUTS 1 65
NUTS 2 125
116

## Page 118

4.4.121 Maritime transport of freight loaded and unloaded, in thousand tonnes (eu -
mtf fr ld nld)
Maritime transport of freight loaded and unloaded in thousand tonnes. The maritime transport
regional data have been calculated using data collected at the port level in the frame of Council
Directive 2009/42/EC (6.5.2009). They are aggregated at regional level (NUTS 1 and NUTS 2)
and also at national level (NUTS0), excluding double counting within each region.
NUTS Level N
NUTS 0 (Country) 20
NUTS 1 66
NUTS 2 126
4.4.122 Maritime transport of freight unloaded, in thousand tonnes (eu mtf fr nld)
Maritime transport of freight unloaded in thousand tonnes. The maritime transport regional data
have been calculated using data collected at the port level in the frame of Council Directive
2009/42/EC (6.5.2009). They are aggregated at regional level (NUTS 1 and NUTS 2) and also
at national level (NUTS0), excluding double counting within each region.
117

## Page 119

NUTS Level N
NUTS 0 (Country) 20
NUTS 1 65
NUTS 2 126
4.4.123 Maritime transport of passengers embarked and disembarked, in thousand
passengers (eu mtp pas)
Maritime transport of passengers embarked and disembarked in thousand passengers. The mar-
itime transport regional data have been calculated using data collected at the port level in the
frame of Council Directive 2009/42/EC (6.5.2009). They are aggregated at regional level (NUTS 1
and NUTS 2) and also at national level (NUTS0), excluding double counting within each region.
NUTS Level N
NUTS 0 (Country) 20
NUTS 1 58
NUTS 2 100
118

## Page 120

4.4.124 Maritime transport of passengers disembarked, in thousand passengers (eu -
mtp pas demb)
Maritime transport of passengers disembarked in thousand passengers. The maritime transport
regional data have been calculated using data collected at the port level in the frame of Council
Directive 2009/42/EC (6.5.2009). They are aggregated at regional level (NUTS 1 and NUTS 2)
and also at national level (NUTS0), excluding double counting within each region.
NUTS Level N
NUTS 0 (Country) 20
NUTS 1 58
NUTS 2 100
4.4.125 Maritime transport of passengers embarked, in thousand passengers (eu -
mtp pas emb)
Maritime transport of passengers embarked in thousand passengers. The maritime transport re-
gional data have been calculated using data collected at the port level in the frame of Council
Directive 2009/42/EC (6.5.2009). They are aggregated at regional level (NUTS 1 and NUTS 2)
and also at national level (NUTS0), excluding double counting within each region.
119

## Page 121

NUTS Level N
NUTS 0 (Country) 20
NUTS 1 57
NUTS 2 98
4.4.126 Air transport of freight and mail loaded, in thousand tonnes (eu atf frm ld)
Air transport of freight and mail loaded in thousand tonnes. The air transport regional data have
been calculated using data collected at the airport level in the frame of Commission Regulation
(EC) No 1358/2003. They are aggregated at regional level (NUTS 1 and NUTS 2) and also at
national level (NUTS0), excluding double counting within each region.
NUTS Level N
NUTS 0 (Country) 20
NUTS 1 77
NUTS 2 156
120

## Page 122

4.4.127 Air transport of freight and mail loaded and unloaded, in thousand tonnes
(eu atf frm ld nld)
Air transport of freight and mail loaded and unloaded in thousand tonnes. The air transport re-
gional data have been calculated using data collected at the airport level in the frame of Commission
Regulation (EC) No 1358/2003. They are aggregated at regional level (NUTS 1 and NUTS 2) and
also at national level (NUTS0), excluding double counting within each region.
NUTS Level N
NUTS 0 (Country) 20
NUTS 1 78
NUTS 2 158
4.4.128 Air transport of freight and mail unloaded, in thousand tonnes (eu atf frm -
nld)
Air transport of freight and mail unloaded in thousand tonnes. The air transport regional data have
been calculated using data collected at the airport level in the frame of Commission Regulation
(EC) No 1358/2003. They are aggregated at regional level (NUTS 1 and NUTS 2) and also at
national level (NUTS0), excluding double counting within each region.
121

## Page 123

NUTS Level N
NUTS 0 (Country) 20
NUTS 1 77
NUTS 2 156
4.4.129 Air transport of passengers carried, in thousand passengers (eu mtp pas crd)
Air transport of passengers carried in thousand passengers. The air transport regional data have
been calculated using data collected at the airport level in the frame of Commission Regulation
(EC) No 1358/2003. They are aggregated at regional level (NUTS 1 and NUTS 2) and also at
national level (NUTS0), excluding double counting within each region.
NUTS Level N
NUTS 0 (Country) 21
NUTS 1 83
NUTS 2 170
122

## Page 124

4.4.130 Air transport of passengers carried (arrival), in thousand passengers (eu -
mtp pas crd arr)
Air transport of passengers carried (arrival) in thousand passengers. The air transport regional
data have been calculated using data collected at the airport level in the frame of Commission
Regulation (EC) No 1358/2003. They are aggregated at regional level (NUTS 1 and NUTS 2) and
also at national level (NUTS0), excluding double counting within each region.
NUTS Level N
NUTS 0 (Country) 20
NUTS 1 82
NUTS 2 167
4.4.131 Air transport of passengers carried (departures), in thousand passengers (eu -
mtp pas crd dep)
Air transport of passengers carried (departures), in thousand passengers. The air transport regional
data have been calculated using data collected at the airport level in the frame of Commission Reg-
ulation (EC) No 1358/2003. They are aggregated at regional level (NUTS 1 and NUTS 2) and also
at national level (NUTS0), excluding double counting within each region.
123

## Page 125

NUTS Level N
NUTS 0 (Country) 21
NUTS 1 82
NUTS 2 169
4.4.132 Number of nights spent at camping grounds, recreational vehicle parks and
trailer parks (eu tour nscamp)
Number of nights spent at camping grounds, recreational vehicle parks and trailer parks. A night
spent (or overnight stay) is each night a guest / tourist (resident or non-resident) actually spends
(sleeps or stays) in a tourist accommodation establishment or non-rented accommodation. Nor-
mally the date of arrival is dierent from the date of departure but persons arriving after midnight
and leaving on the same day are included in overnight stays. A person should not be registered
in two or more accommodation establishments at the same time. From reference period 2012 on-
wards, tourism occupancy statistics consist of harmonised data collected by the Member States in
the frame of the Regulation (EU) 692/2011 of the European Parliament and of the Council. Up
to reference period 2011, tourism occupancy statistics consist of harmonised data collected by the
Member States in the frame of the Council Directive on tourism statistics 95/57/EC .
124

## Page 126

NUTS Level N
NUTS 0 (Country) 25
NUTS 1 74
NUTS 2 196
4.4.133 Number of nights spent at hotels and similar accommodation (eu tour -
nshotel)
Number of nights spent at hotels and similar accommodations. A night spent (or overnight stay) is
each night a guest / tourist (resident or non-resident) actually spends (sleeps or stays) in a tourist
accommodation establishment or non-rented accommodation. Normally the date of arrival is dif-
ferent from the date of departure but persons arriving after midnight and leaving on the same day
are included in overnight stays. A person should not be registered in two or more accommodation
establishments at the same time. From reference period 2012 onwards, tourism occupancy statistics
consist of harmonised data collected by the Member States in the frame of the Regulation (EU)
692/2011 of the European Parliament and of the Council. Up to reference period 2011, tourism
occupancy statistics consist of harmonised data collected by the Member States in the frame of the
Council Directive on tourism statistics 95/57/EC .
125

## Page 127

NUTS Level N
NUTS 0 (Country) 26
NUTS 1 84
NUTS 2 220
4.4.134 Number of nights spent at holiday and other short-stay accommodation (eu -
tour nssa)
Number of nights spent at holiday and other short-stay accommodation. A night spent (or overnight
stay) is each night a guest / tourist (resident or non-resident) actually spends (sleeps or stays) in
a tourist accommodation establishment or non-rented accommodation. Normally the date of ar-
rival is dierent from the date of departure but persons arriving after midnight and leaving on
the same day are included in overnight stays. A person should not be registered in two or more
accommodation establishments at the same time. From reference period 2012 onwards, tourism
occupancy statistics consist of harmonised data collected by the Member States in the frame of the
Regulation (EU) 692/2011 of the European Parliament and of the Council. Up to reference period
2011, tourism occupancy statistics consist of harmonised data collected by the Member States in
the frame of the Council Directive on tourism statistics 95/57/EC .
126

## Page 128

NUTS Level N
NUTS 0 (Country) 23
NUTS 1 70
NUTS 2 180
4.4.135 Number of nights spent at tourist accommodations (eu tour nstour)
Number of nights spent at tourist accommodations. A night spent (or overnight stay) is each night
a guest / tourist (resident or non-resident) actually spends (sleeps or stays) in a tourist accommo-
dation establishment or non-rented accommodation. Normally the date of arrival is dierent from
the date of departure but persons arriving after midnight and leaving on the same day are included
in overnight stays. A person should not be registered in two or more accommodation establish-
ments at the same time. From reference period 2012 onwards, tourism occupancy statistics consist
of harmonised data collected by the Member States in the frame of the Regulation (EU) 692/2011
of the European Parliament and of the Council. Up to reference period 2011, tourism occupancy
statistics consist of harmonised data collected by the Member States in the frame of the Council
Directive on tourism statistics 95/57/EC .
127

## Page 129

NUTS Level N
NUTS 0 (Country) 26
NUTS 1 79
NUTS 2 205
4.4.136 Net occupancy rate of bed-places in hotels and similar (eu tour bedpl)
Net occupancy rate of bed-places in hotels and similar. The occupancy rate of bed-places in ref-
erence period is obtained by dividing the total number of overnight stays by the number of the
bed-places on oer (excluding extra beds) and the number of days when the bed-places are actually
available for use (net of seasonal closures and other temporary closures for decoration, by police
order, etc.). The result is multiplied by 100 to express the occupancy rate as a percentage. From
reference period 2012 onwards, tourism occupancy statistics consist of harmonised data collected
by the Member States in the frame of the Regulation (EU) 692/2011 of the European Parliament
and of the Council. Up to reference period 2011, tourism occupancy statistics consist of harmonised
data collected by the Member States in the frame of the Council Directive on tourism statistics
95/57/EC .
128

## Page 130

NUTS Level N
NUTS 0 (Country) 27
NUTS 1 94
NUTS 2 251
4.4.137 Net occupancy rate of bedrooms in hotels and similar (eu tour bedrm)
Net occupancy rate of bedrooms in hotels and similar. The net occupancy rate of bedrooms in
reference period is obtained by dividing the total number of bedrooms used during the reference
period (i.e. the sum of the bedrooms in use per day) by the total number of bedrooms available
for the reference period (i.e. the sum of bedrooms available per day). The result is multiplied by
100 to express the occupancy rate as a percentage. From reference period 2012 onwards, tourism
occupancy statistics consist of harmonised data collected by the Member States in the frame of the
Regulation (EU) 692/2011 of the European Parliament and of the Council. Up to reference period
2011, tourism occupancy statistics consist of harmonised data collected by the Member States in
the frame of the Council Directive on tourism statistics 95/57/EC .
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 92
NUTS 2 245
129

## Page 131

4.4.138 Number of bed-places in hotels, camping places and other (eu tour nstour -
bedpl)
Number of bed-places in hotels, camping places and other. The number of bed-places in an estab-
lishment or dwelling is determined by the number of persons who can stay overnight in the beds
set up in the establishment (dwelling), ignoring any extra beds that may be set up by customer
request. The term bed place applies to a single bed, double beds are counted as two bed-places.
The unit serves to measure the capacity of any type of accommodation. A bed place is also a place
on a pitch or in a boat on a mooring to accommodate one person. One camping pitch should equal
four bed-places if the actual number of bed-places is not known.
NUTS Level N
NUTS 0 (Country) 25
NUTS 1 75
NUTS 2 196
4.4.139 Number of establishments in hotels, camping places and other (eu tour -
nstour estbl)
Number of establishments in hotels, camping places and other. A tourist accommodation establish-
ment is dened as any facility that regularly or occasionally provides short-term accommodation
for tourists as a paid service (although the price might be partially or fully subsidised). Data is
reported at the level of a local kind-of-activity unit. The local unit is an enterprise or part thereof
situated in a geographically identied place. At or from this place economic activity is carried out
for which - save for certain exceptions - one or more persons work (even if only part-time) for one
and the same enterprise. The accommodation establishment conforms to the denition of local unit
as the production unit. This is irrespective of whether the accommodation of tourists is the main or
secondary activity. This means that all establishments are classied in the accommodation sector
if their capacity exceeds the national minimum even if the major part of turnover may come from
restaurant or other services.
130

## Page 132

NUTS Level N
NUTS 0 (Country) 26
NUTS 1 76
NUTS 2 200
4.4.140 Reported number of cases of robbery (eu cri rob)
Reported number of cases of robbery. Robbery is a sub-set of violent crime (see above). It is
dened as stealing from a person with force or threat of force, including muggings (bag-snatching)
and theft with violence. Pick-pocketing, extortion and blackmailing are generally not included.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 80
NUTS 2 175
4.4.141 Reported number of cases of intentional homicide (eu cri inthom)
Reported number of cases of intentional homicide. It is dened as intentional killing of a person,
including murder, manslaughter, euthanasia and infanticide. Causing death by dangerous driving
is excluded, as are abortion and help with suicide. Attempted (uncompleted) homicide is also ex-
131

## Page 133

cluded. The counting unit for homicide is normally the victim (rather than the case).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 74
NUTS 2 158
4.4.142 Reported number of cases of burglary of private premises (eu cri bur)
Reported number of cases of burglary of private premises. Domestic burglary is dened as gaining
access to a dwelling by the use of force to steal goods.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 80
NUTS 2 175
132

## Page 134

4.4.143 Regional gross domestic product by NUTS 2 regions - million EUR (eu mio -
eur)
Regional gross domestic product (GDP) by NUTS 2 regions in Million euro. GDP is an indicator
of the output of a country or a region. It reects the total value of all goods and services produced
less the value of goods and services used for intermediate consumption in their production. Ex-
pressing GDP in PPS (purchasing power standards) eliminates dierences in price levels between
countries. Calculations on a per inhabitant basis allow for the comparison of economies and regions
signicantly dierent in absolute size. GDP per inhabitant in PPS is the key variable for deter-
mining the eligibility of NUTS 2 regions in the framework of the European Union’s structural policy.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 106
NUTS 2 272
4.4.144 Regional gross domestic product (million PPS) by NUTS 2 regions (eu gdp -
mio pps)
Regional gross domestic product (GDP) by NUTS 2 regions in Million PPS (purchasing power
standards). GDP is an indicator of the output of a country or a region. It reects the total value of
all goods and services produced less the value of goods and services used for intermediate consump-
tion in their production. Expressing GDP in PPS eliminates dierences in price levels between
countries. Calculations on a per inhabitant basis allow for the comparison of economies and regions
signicantly dierent in absolute size. GDP per inhabitant in PPS is the key variable for deter-
mining the eligibility of NUTS 2 regions in the framework of the European Union’s structural policy.
133

## Page 135

NUTS Level N
NUTS 0 (Country) NA
NUTS 1 NA
NUTS 2 272
4.4.145 Regional gross domestic product (PPS per inhabitant) by NUTS 2 regions
(eu gdp pps hab)
Regional gross domestic product (GDP) by NUTS 2 regions in PPS (purchasing power standards)
per inhabitant. GDP is an indicator of the output of a country or a region. It reects the total value
of all goods and services produced less the value of goods and services used for intermediate con-
sumption in their production. Expressing GDP in PPS eliminates dierences in price levels between
countries. Calculations on a per inhabitant basis allow for the comparison of economies and regions
signicantly dierent in absolute size. GDP per inhabitant in PPS is the key variable for deter-
mining the eligibility of NUTS 2 regions in the framework of the European Union’s structural policy.
NUTS Level N
NUTS 0 (Country) NA
NUTS 1 NA
NUTS 2 259
134

## Page 136

4.4.146 Regional gross domestic product (PPS per inhabitant in % of the EU27 (from
2020) average) by NUTS 2 regions (eu gdp pps hab eu27 2020)
Regional gross domestic product (GDP) by NUTS 2 regions in PPS (purchasing power standards)
per inhabitant, as % of EU27 (from 2020) average. GDP is an indicator of the output of a country
or a region. It reects the total value of all goods and services produced less the value of goods and
services used for intermediate consumption in their production. Expressing GDP in PPS eliminates
dierences in price levels between countries. Calculations on a per inhabitant basis allow for the
comparison of economies and regions signicantly dierent in absolute size. GDP per inhabitant in
PPS is the key variable for determining the eligibility of NUTS 2 regions in the framework of the
European Union’s structural policy.
NUTS Level N
NUTS 0 (Country) NA
NUTS 1 NA
NUTS 2 259
4.4.147 Disposable income of private households by NUTS 2 regions (eu dinc pps -
hab)
Disposable income of private households by NUTS 2 regions in PPS (purchasing power standards)
based onnal consumption per inhabitant. The disposable income of private households is the
balance of primary income (operating surplus/mixed income plus compensation of employees plus
property income received minus property income paid) and the redistribution of income in cash.
These transactions comprise social contributions paid, social benets in cash received, current taxes
on income and wealth paid, as well as other current transfers. Disposable income does not include
social transfers in kind coming from public administrations or non-prot institutions serving house-
holds. The data for NUTS 1 and NUTS 0 regions has been calculated by computing a mean of the
NUTS 2 values within each region.
135

## Page 137

NUTS Level N
NUTS 0 (Country) 24
NUTS 1 84
NUTS 2 235
4.4.148 Primary income of private households by NUTS 2 regions (eu pinc pps hab)
Primary income of private households by NUTS 2 regions in PPS (purchasing power standards)
based onnal consumption per inhabitant. The disposable income of private households is the
balance of primary income (operating surplus/mixed income plus compensation of employees plus
property income received minus property income paid) and the redistribution of income in cash.
These transactions comprise social contributions paid, social benets in cash received, current taxes
on income and wealth paid, as well as other current transfers. Disposable income does not include
social transfers in kind coming from public administrations or non-prot institutions serving house-
holds.
NUTS Level N
NUTS 0 (Country) NA
NUTS 1 NA
NUTS 2 235
136

## Page 138

4.4.149 Real growth rate of regional gross value added (GV A) at basic prices by
NUTS 2 regions (eu rgva pch pre)
Real growth rate of regional gross value added (GV A) at basic prices by NUTS 2 regions, percentage
change on previous year. GV A is an indicator of the economic activity of a country or a region. It
reects the total value of all goods and services produced less the value of goods and services used
for intermediate consumption in their production. Several years ago Eurostat has started to collect
real growth rates of regional GV A at NUTS level 2 from those Member States which calculate this
already. The indicator is part of the ESA 2010 data transmission programme, but the transmission
will be obligatory only as from the end of 2017.
NUTS Level N
NUTS 0 (Country) NA
NUTS 1 NA
NUTS 2 261
4.4.150 Income of households (balance), euro per inhabitant (eu b5n eur hab)
Income of households (balance), Euro per inhabitant. The disposable income of private households
is the balance of primary income (operating surplus/mixed income plus compensation of employees
plus property income received minus property income paid) and the redistribution of income in
cash. These transactions comprise social contributions paid, social benets in cash received, cur-
rent taxes on income and wealth paid, as well as other current transfers. Disposable income does
not include social transfers in kind coming from public administrations or non-prot institutions
serving households.
137

## Page 139

NUTS Level N
NUTS 0 (Country) 24
NUTS 1 83
NUTS 2 235
4.4.151 Income of households (balance), million euro (eu b5n mio eur)
Income of households (balance), million Euro. The disposable income of private households is the
balance of primary income (operating surplus/mixed income plus compensation of employees plus
property income received minus property income paid) and the redistribution of income in cash.
These transactions comprise social contributions paid, social benets in cash received, current taxes
on income and wealth paid, as well as other current transfers. Disposable income does not include
social transfers in kind coming from public administrations or non-prot institutions serving house-
holds.
NUTS Level N
NUTS 0 (Country) 21
NUTS 1 81
NUTS 2 214
138

## Page 140

4.4.152 Income of households (balance), million national currency (eu b5n mio nac)
Income of households (balance), million national currency. The disposable income of private house-
holds is the balance of primary income (operating surplus/mixed income plus compensation of
employees plus property income received minus property income paid) and the redistribution of
income in cash. These transactions comprise social contributions paid, social benets in cash re-
ceived, current taxes on income and wealth paid, as well as other current transfers. Disposable
income does not include social transfers in kind coming from public administrations or non-prot
institutions serving households.
NUTS Level N
NUTS 0 (Country) 21
NUTS 1 81
NUTS 2 214
4.4.153 Income of households (balance), million PPS (eu b5n mio pps)
Income of households (balance), million PPS. The disposable income of private households is the
balance of primary income (operating surplus/mixed income plus compensation of employees plus
property income received minus property income paid) and the redistribution of income in cash.
These transactions comprise social contributions paid, social benets in cash received, current taxes
on income and wealth paid, as well as other current transfers. Disposable income does not include
social transfers in kind coming from public administrations or non-prot institutions serving house-
holds.
139

## Page 141

NUTS Level N
NUTS 0 (Country) 21
NUTS 1 81
NUTS 2 214
4.4.154 Income of households (disposable income), euro per inhabitant (eu b6n eur -
hab)
Income of households (disposable income), Euro per inhabitant. The disposable income of private
households is the balance of primary income (operating surplus/mixed income plus compensation
of employees plus property income received minus property income paid) and the redistribution
of income in cash. These transactions comprise social contributions paid, social benets in cash
received, current taxes on income and wealth paid, as well as other current transfers. Disposable
income does not include social transfers in kind coming from public administrations or non-prot
institutions serving households.
NUTS Level N
NUTS 0 (Country) 24
NUTS 1 83
NUTS 2 235
140

## Page 142

4.4.155 Income of households (disposable income), million euro (eu b6n mio eur)
Income of households (disposable income), million Euro. The disposable income of private house-
holds is the balance of primary income (operating surplus/mixed income plus compensation of
employees plus property income received minus property income paid) and the redistribution of
income in cash. These transactions comprise social contributions paid, social benets in cash re-
ceived, current taxes on income and wealth paid, as well as other current transfers. Disposable
income does not include social transfers in kind coming from public administrations or non-prot
institutions serving households.
NUTS Level N
NUTS 0 (Country) 21
NUTS 1 81
NUTS 2 214
4.4.156 Income of households (disposable income), million national currency (eu -
b6n mio nac)
Income of households (disposable income), million national currency. The disposable income of pri-
vate households is the balance of primary income (operating surplus/mixed income plus compensa-
tion of employees plus property income received minus property income paid) and the redistribution
of income in cash. These transactions comprise social contributions paid, social benets in cash
received, current taxes on income and wealth paid, as well as other current transfers. Disposable
income does not include social transfers in kind coming from public administrations or non-prot
institutions serving households.
141

## Page 143

NUTS Level N
NUTS 0 (Country) 21
NUTS 1 81
NUTS 2 214
4.4.157 Income of households (disposable income), million PPS (eu b6n mio pps)
Income of households (disposable income), million PPS. The disposable income of private house-
holds is the balance of primary income (operating surplus/mixed income plus compensation of
employees plus property income received minus property income paid) and the redistribution of
income in cash. These transactions comprise social contributions paid, social benets in cash re-
ceived, current taxes on income and wealth paid, as well as other current transfers. Disposable
income does not include social transfers in kind coming from public administrations or non-prot
institutions serving households.
NUTS Level N
NUTS 0 (Country) 21
NUTS 1 81
NUTS 2 214
142

## Page 144

4.4.158 Income of households (Adjusted disposable income, net), million euro (eu -
b7n mio eur)
Income of households (net adjusted disposable income), million euro. The disposable income of pri-
vate households is the balance of primary income (operating surplus/mixed income plus compensa-
tion of employees plus property income received minus property income paid) and the redistribution
of income in cash. These transactions comprise social contributions paid, social benets in cash
received, current taxes on income and wealth paid, as well as other current transfers. Disposable
income does not include social transfers in kind coming from public administrations or non-prot
institutions serving households. Net signies that depreciation costs have been subtracted from the
income presented, and regional data are adjusted to the national values by Eurostat.
NUTS Level N
NUTS 0 (Country) 3
NUTS 1 9
NUTS 2 18
4.4.159 Income of households (Adjusted disposable income, net), million national
currency (eu b7n mio nac)
Income of households (net adjusted disposable income), million national currency. The disposable
income of private households is the balance of primary income (operating surplus/mixed income
plus compensation of employees plus property income received minus property income paid) and
the redistribution of income in cash. These transactions comprise social contributions paid, so-
cial benets in cash received, current taxes on income and wealth paid, as well as other current
transfers. Disposable income does not include social transfers in kind coming from public admin-
istrations or non-prot institutions serving households. Net signies that depreciation costs have
been subtracted from the income presented, and regional data are adjusted to the national values
by Eurostat.
143

## Page 145

NUTS Level N
NUTS 0 (Country) 3
NUTS 1 9
NUTS 2 18
4.4.160 At-risk-of-poverty rate by NUTS regions, percentage (eu povrisk pc)
Percentage of total population at-risk-of-poverty rate by NUTS 2 regions. The persons with an
equivalised disposable income below the risk-of-poverty threshold, which is set at 60 % of the na-
tional median equivalised disposable income (after social transfers).
NUTS Level N
NUTS 0 (Country) 24
NUTS 1 30
NUTS 2 81
4.4.161 Severe material deprivation rate by NUTS regions, percentage (eu matdep -
pc)
Percentage of total population living in conditions of severe material deprivation by NUTS 2 re-
gions. The collectionmaterial deprivationcovers indicators relating to economic strain, durables,
144

## Page 146

housing and environment of the dwelling. Severely materially deprived persons have living con-
ditions severely constrained by a lack of resources, they experience at least 4 out of 9 following
deprivations items: they cannot aord i) to pay rent or utility bills, ii) keep home adequately
warm, iii) face unexpected expenses, iv) eat meat,sh or a protein equivalent every second day, v)
a week holiday away from home, vi) a car, vii) a washing machine, viii) a colour TV, ix) a telephone.
NUTS Level N
NUTS 0 (Country) 24
NUTS 1 30
NUTS 2 81
4.4.162 People living in households with very low work intensity by NUTS regions
(population aged 0 to 59 years), percentage (eu lwoin pc)
Population aged 0-59 living in households with very low work intensity by NUTS regions, as a
percentage of total population. People living in households with very low work intensity are people
aged 0-59 living in households where the adults work less than 20% of their total work potential
during the past year.
145

## Page 147

NUTS Level N
NUTS 0 (Country) 1
NUTS 1 NA
NUTS 2 9
4.4.163 People living in households with very low work intensity by NUTS regions
(population aged 0 to 59 years), percentage of total population aged less than
60 (eu lwoin pc y lt60)
Population aged 0-59 living in households with very low work intensity by NUTS regions, as a
percentage of total population aged less than 60. People living in households with very low work
intensity are people aged 0-59 living in households where the adults work less than 20% of their
total work potential during the past year.
NUTS Level N
NUTS 0 (Country) 24
NUTS 1 30
NUTS 2 81
146

## Page 148

4.4.164 People at risk of poverty or social exclusion by NUTS regions, percentage
(eu povr pc)
People at risk of poverty or social exclusion by NUTS 2 regions, percentage of total population.
Persons who are at risk of poverty or severely materially deprived or living in households with very
low work intensity. Persons are only counted once even if they are present in several sub-indicators.
At risk-of-poverty are persons with an equivalised disposable income below the risk-of-poverty
threshold, which is set at 60 % of the national median equivalised disposable income (after social
transfers). Material deprivation covers indicators relating to economic strain and durables. Severely
materially deprived persons have living conditions severely constrained by a lack of resources, they
experience at least 4 out of 9 following deprivations items: cannot aord i) to pay rent or utility
bills, ii) keep home adequately warm, iii) face unexpected expenses, iv) eat meat,sh or a protein
equivalent every second day, v) a week holiday away from home, vi) a car, vii) a washing machine,
viii) a colour TV, or ix) a telephone. People living in households with very low work intensity are
those aged 0-59 living in households where the adults (aged 18-59) work less than 20% of their total
work potential during the past year.
NUTS Level N
NUTS 0 (Country) 24
NUTS 1 30
NUTS 2 86
4.4.165 Educational attaintment for ages 25 to 64, primary education, female (eu -
edatt ed02 y2564f )
Percentage of 25-64 years old females whose the highest level of education successfully completed
is less than primary, primary and lower secondary education (levels 0-2). This aggregate refers
to levels 0, 1 and 2 of the ISCED 2011 (online code ED0-2). Data up to 2013 refer to ISCED
1997 levels 0, 1 and 2 but also include level 3C short (educational attainment from ISCED level 3
programmes of less than two years).
147

## Page 149

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 102
NUTS 2 265
4.4.166 Educational attaintment for ages 25 to 64, primary education, male (eu -
edatt ed02 y2564m)
Percentage of 25-64 years old males whose the highest level of education successfully completed
is less than primary, primary and lower secondary education (levels 0-2). This aggregate refers
to levels 0, 1 and 2 of the ISCED 2011 (online code ED0-2). Data up to 2013 refer to ISCED
1997 levels 0, 1 and 2 but also include level 3C short (educational attainment from ISCED level 3
programmes of less than two years).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 102
NUTS 2 265
148

## Page 150

4.4.167 Educational attaintment for ages 25 to 64, primary education, total (eu -
edatt ed02 y2564t)
Percentage of 25-64 years old population whose the highest level of education successfully com-
pleted is less than primary, primary and lower secondary education (levels 0-2). This aggregate
refers to levels 0, 1 and 2 of the ISCED 2011 (online code ED0-2). Data up to 2013 refer to ISCED
1997 levels 0, 1 and 2 but also include level 3C short (educational attainment from ISCED level 3
programmes of less than two years).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 265
4.4.168 Educational attaintment for ages 25 to 64, secondary education, female (eu -
edatt ed34 y2564f )
Percentage of 25-64 years old females whose the highest level of education successfully completed
is upper secondary and post-secondary non-tertiary education (levels 3 and 4). This aggregate
corresponds to ISCED 2011 levels 3 and 4 (online code ED3 4). ISCED 2011 level 3 programmes
of partial level completion are considered within ISCED level 3. Data up to 2013 refer to ISCED
1997 levels 3C long, 3A, 3B and 4.
149

## Page 151

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 265
4.4.169 Educational attaintment for ages 25 to 64, secondary education, male (eu -
edatt ed34 y2564m)
Percentage of 25-64 years old males whose the highest level of education successfully completed
is upper secondary and post-secondary non-tertiary education (levels 3 and 4). This aggregate
corresponds to ISCED 2011 levels 3 and 4 (online code ED3 4). ISCED 2011 level 3 programmes
of partial level completion are considered within ISCED level 3. Data up to 2013 refer to ISCED
1997 levels 3C long, 3A, 3B and 4.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 265
150

## Page 152

4.4.170 Educational attaintment for ages 25 to 64, secondary education, total (eu -
edatt ed34 y2564t)
Percentage of 25-64 years old population whose the highest level of education successfully completed
is upper secondary and post-secondary non-tertiary education (levels 3 and 4). This aggregate cor-
responds to ISCED 2011 levels 3 and 4 (online code ED3 4). ISCED 2011 level 3 programmes of
partial level completion are considered within ISCED level 3. Data up to 2013 refer to ISCED 1997
levels 3C long, 3A, 3B and 4.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 265
4.4.171 Educational attaintment for ages 25 to 64, tertiary education, female (eu -
edatt ed58 y2564f )
Percentage of 25-64 years old females whose the highest level of education successfully completed is
tertiary education (levels 5-8). This aggregate covers ISCED 2011 levels 5, 6, 7 and 8 (short-cycle
tertiary education, bachelor’s or equivalent level, master’s or equivalent level, doctoral or equivalent
level, online code ED5-8 ’tertiary education’). Data up to 2013 refer to ISCED 1997 levels 5 and 6.
151

## Page 153

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 102
NUTS 2 265
4.4.172 Educational attaintment for ages 25 to 64, tertiary education, male (eu -
edatt ed58 y2564m)
Percentage of 25-64 years old males whose the highest level of education successfully completed is
tertiary education (levels 5-8). This aggregate covers ISCED 2011 levels 5, 6, 7 and 8 (short-cycle
tertiary education, bachelor’s or equivalent level, master’s or equivalent level, doctoral or equivalent
level, online code ED5-8 ’tertiary education’). Data up to 2013 refer to ISCED 1997 levels 5 and 6.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 101
NUTS 2 264
152

## Page 154

4.4.173 Educational attaintment for ages 25 to 64, tertiary education, total (eu -
edatt ed58 y2564t)
Percentage of 25-64 years old population whose the highest level of education successfully completed
is tertiary education (levels 5-8). This aggregate covers ISCED 2011 levels 5, 6, 7 and 8 (short-cycle
tertiary education, bachelor’s or equivalent level, master’s or equivalent level, doctoral or equivalent
level, online code ED5-8 ’tertiary education’). Data up to 2013 refer to ISCED 1997 levels 5 and 6.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 265
4.4.174 Educational attaintment for ages 30 to 34, primary education, female (eu -
edatt ed02 y3034f )
Percentage of 30-34 years old females whose the highest level of education successfully completed
is less than primary, primary and lower secondary education (levels 0-2). This aggregate refers
to levels 0, 1 and 2 of the ISCED 2011 (online code ED0-2). Data up to 2013 refer to ISCED
1997 levels 0, 1 and 2 but also include level 3C short (educational attainment from ISCED level 3
programmes of less than two years).
153

## Page 155

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 95
NUTS 2 219
4.4.175 Educational attaintment for ages 30 to 34, primary education, male (eu -
edatt ed02 y3034m)
Percentage of 30-34 years old males whose the highest level of education successfully completed
is less than primary, primary and lower secondary education (levels 0-2). This aggregate refers
to levels 0, 1 and 2 of the ISCED 2011 (online code ED0-2). Data up to 2013 refer to ISCED
1997 levels 0, 1 and 2 but also include level 3C short (educational attainment from ISCED level 3
programmes of less than two years).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 228
154

## Page 156

4.4.176 Educational attaintment for ages 30 to 34, primary education, total (eu -
edatt ed02 y3034t)
Percentage of 30-34 years old population whose the highest level of education successfully com-
pleted is less than primary, primary and lower secondary education (levels 0-2). This aggregate
refers to levels 0, 1 and 2 of the ISCED 2011 (online code ED0-2). Data up to 2013 refer to ISCED
1997 levels 0, 1 and 2 but also include level 3C short (educational attainment from ISCED level 3
programmes of less than two years).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 101
NUTS 2 254
4.4.177 Educational attaintment for ages 30 to 34, secondary education, female (eu -
edatt ed34 y3034f )
Percentage of 30-34 years old females whose the highest level of education successfully completed
is upper secondary and post-secondary non-tertiary education (levels 3 and 4). This aggregate
corresponds to ISCED 2011 levels 3 and 4 (online code ED3 4). ISCED 2011 level 3 programmes
of partial level completion are considered within ISCED level 3. Data up to 2013 refer to ISCED
1997 levels 3C long, 3A, 3B and 4.
155

## Page 157

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 99
NUTS 2 258
4.4.178 Educational attaintment for ages 30 to 34, secondary education, male (eu -
edatt ed34 y3034m)
Percentage of 30-34 years old males whose the highest level of education successfully completed
is upper secondary and post-secondary non-tertiary education (levels 3 and 4). This aggregate
corresponds to ISCED 2011 levels 3 and 4 (online code ED3 4). ISCED 2011 level 3 programmes
of partial level completion are considered within ISCED level 3. Data up to 2013 refer to ISCED
1997 levels 3C long, 3A, 3B and 4.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 99
NUTS 2 258
156

## Page 158

4.4.179 Educational attaintment for ages 30 to 34, secondary education, total (eu -
edatt ed34 y3034t)
Percentage of 30-34 years old population whose the highest level of education successfully completed
is upper secondary and post-secondary non-tertiary education (levels 3 and 4). This aggregate cor-
responds to ISCED 2011 levels 3 and 4 (online code ED3 4). ISCED 2011 level 3 programmes of
partial level completion are considered within ISCED level 3. Data up to 2013 refer to ISCED 1997
levels 3C long, 3A, 3B and 4.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 262
4.4.180 Educational attaintment for ages 30 to 34, tertiary education, female (eu -
edatt ed58 y3034f )
Percentage of 30-34 years old females whose the highest level of education successfully completed is
tertiary education (levels 5-8). This aggregate covers ISCED 2011 levels 5, 6, 7 and 8 (short-cycle
tertiary education, bachelor’s or equivalent level, master’s or equivalent level, doctoral or equivalent
level, online code ED5-8 ’tertiary education’). Data up to 2013 refer to ISCED 1997 levels 5 and 6.
157

## Page 159

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 99
NUTS 2 252
4.4.181 Educational attaintment for ages 30 to 34, tertiary education, male (eu -
edatt ed58 y3034m)
Percentage of 30-34 years old males whose the highest level of education successfully completed is
tertiary education (levels 5-8). This aggregate covers ISCED 2011 levels 5, 6, 7 and 8 (short-cycle
tertiary education, bachelor’s or equivalent level, master’s or equivalent level, doctoral or equivalent
level, online code ED5-8 ’tertiary education’). Data up to 2013 refer to ISCED 1997 levels 5 and 6.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 246
158

## Page 160

4.4.182 Educational attaintment for ages 30 to 34, tertiary education, total (eu -
edatt ed58 y3034t)
Percentage of 30-34 years old population whose the highest level of education successfully completed
is tertiary education (levels 5-8). This aggregate covers ISCED 2011 levels 5, 6, 7 and 8 (short-cycle
tertiary education, bachelor’s or equivalent level, master’s or equivalent level, doctoral or equivalent
level, online code ED5-8 ’tertiary education’). Data up to 2013 refer to ISCED 1997 levels 5 and 6.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 260
4.4.183 Early leavers from education and training as a percentage, females (eu -
eduleave f )
Female early leavers from education and training as a percentage of the population aged 18-24
with at most lower secondary education and not in further education or training. The indicator
is dened as the percentage of the population aged 18-24 with at most lower secondary education
and who were not in further education or training during the last four weeks preceding the survey.
Lower secondary education refers to ISCED (International Standard Classication of Education)
2011 level 0-2 for data from 2014 onwards and to ISCED 1997 level 0-3C short for data up to 2013.
The indicator is based on the EU Labour Force Survey.
159

## Page 161

NUTS Level N
NUTS 0 (Country) 27
NUTS 1 95
NUTS 2 199
4.4.184 Early leavers from education and training as a percentage, males (eu ed-
uleave m)
Male early leavers from education and training as a percentage of the population aged 18-24 with at
most lower secondary education and not in further education or training. The indicator is dened
as the percentage of the population aged 18-24 with at most lower secondary education and who
were not in further education or training during the last four weeks preceding the survey. Lower
secondary education refers to ISCED (International Standard Classication of Education) 2011
level 0-2 for data from 2014 onwards and to ISCED 1997 level 0-3C short for data up to 2013. The
indicator is based on the EU Labour Force Survey.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 98
NUTS 2 225
160

## Page 162

4.4.185 Early leavers from education and training as a percentage, total (eu ed-
uleave t)
Early leavers from education and training as a percentage of the population aged 18-24 with at most
lower secondary education and not in further education or training. The indicator is dened as the
percentage of the population aged 18-24 with at most lower secondary education and who were not
in further education or training during the last four weeks preceding the survey. Lower secondary
education refers to ISCED (International Standard Classication of Education) 2011 level 0-2 for
data from 2014 onwards and to ISCED 1997 level 0-3C short for data up to 2013. The indicator is
based on the EU Labour Force Survey.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 100
NUTS 2 250
4.4.186 15-24 year old people neither in employment nor in education as percentage,
females (eu neet y1524f )
15-24 year old females neither in employment nor in education as percentage. The indicator on
young people neither in employment nor in education and training (NEET) provides information
on young people aged 15 to 24 who meet the following two conditions: (a) they are not employed
(i.e. unemployed or inactive according to the International Labour Organisation denition) and
(b) they have not received any education or training in the four weeks preceding the survey. Data
are expressed as a percentage of the total population in the same age group and sex, excluding the
respondents who have not answered the question ’participation to education and training’. Data
come from the European Union Labour Force Survey.
161

## Page 163

NUTS Level N
NUTS 0 (Country) 27
NUTS 1 97
NUTS 2 234
4.4.187 15-24 year old people neither in employment nor in education as percentage,
males (eu neet y1524m)
15-24 year old males neither in employment nor in education as percentage. The indicator on
young people neither in employment nor in education and training (NEET) provides information
on young people aged 15 to 24 who meet the following two conditions: (a) they are not employed
(i.e. unemployed or inactive according to the International Labour Organisation denition) and
(b) they have not received any education or training in the four weeks preceding the survey. Data
are expressed as a percentage of the total population in the same age group and sex, excluding the
respondents who have not answered the question ’participation to education and training’. Data
come from the European Union Labour Force Survey.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 96
NUTS 2 225
162

## Page 164

4.4.188 15-24 year old people neither in employment nor in education as percentage,
total (eu neet y1524t)
15-24 year old population neither in employment nor in education as percentage. The indicator on
young people neither in employment nor in education and training (NEET) provides information
on young people aged 15 to 24 who meet the following two conditions: (a) they are not employed
(i.e. unemployed or inactive according to the International Labour Organisation denition) and
(b) they have not received any education or training in the four weeks preceding the survey. Data
are expressed as a percentage of the total population in the same age group and sex, excluding the
respondents who have not answered the question ’participation to education and training’. Data
come from the European Union Labour Force Survey.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 100
NUTS 2 256
4.4.189 Employment rate for people between 15 and 34 years, total duration since
education (eu empl durtotal)
Employment rate for people between 15 and 34 years, total duration since completion of highest
level of education. The indicator is dened as the percentage of the population aged 15-34, who
were employed (ILO denition), not in further education or training (i.e. neither formal nor non-
formal) during the last four weeks preceding the survey.
163

## Page 165

NUTS Level N
NUTS 0 (Country) 27
NUTS 1 101
NUTS 2 262
4.4.190 Employment rate for people between 15 and 34 years, over 3 years since
education (eu empl dury gt3)
Employment rate for people between 15 and 34 years, over 3 years since completion of highest level
of education. The indicator is dened as the percentage of the population aged 15-34, who were
employed (ILO denition), not in further education or training (i.e. neither formal nor non-formal)
during the last four weeks preceding the survey.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 97
NUTS 2 253
164

## Page 166

4.4.191 Employment rate for people between 15 and 34 years, 1 to 3 years since
education (eu empl dury13)
Employment rate for people between 15 and 34 years, 1 to 3 years since completion of highest level
of education. The indicator is dened as the percentage of the population aged 15-34, who were
employed (ILO denition), not in further education or training (i.e. neither formal nor non-formal)
during the last four weeks preceding the survey.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 94
NUTS 2 235
4.4.192 Employment rate for people between 15 and 34 years, education levels 0-2
(eu empl edled02)
Employment rate for people between 15 and 34 years, whose the highest level of education suc-
cessfully completed is less than primary, primary and lower secondary education (levels 0-2). The
indicator is dened as the percentage of the population aged 15-34, who were employed (ILO def-
inition), not in further education or training (i.e. neither formal nor non-formal) during the last
four weeks preceding the survey.
165

## Page 167

NUTS Level N
NUTS 0 (Country) 27
NUTS 1 97
NUTS 2 238
4.4.193 Employment rate for people between 15 and 34 years, education levels 3-4
(eu empl edled34)
Employment rate for people between 15 and 34 years, whose the highest level of education suc-
cessfully completed is upper secondary and post-secondary non-tertiary education (levels 3 and 4).
The indicator is dened as the percentage of the population aged 15-34, who were employed (ILO
denition), not in further education or training (i.e. neither formal nor non-formal) during the last
four weeks preceding the survey.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 99
NUTS 2 258
166

## Page 168

4.4.194 Employment rate for people between 15 and 34 years, education levels 5-8
(eu empl edled58)
Employment rate for people between 15 and 34 years, whose the highest level of education success-
fully completed is tertiary education (levels 5-8). The indicator is dened as the percentage of the
population aged 15-34, who were employed (ILO denition), not in further education or training
(i.e. neither formal nor non-formal) during the last four weeks preceding the survey.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 97
NUTS 2 248
4.4.195 Employment rate for people between 15 and 34 years, all education levels
(eu empl edltotal)
Total employment rate for people between 15 and 34 years for all education levels. The indicator
is dened as the percentage of the population aged 15-34, who were employed (ILO denition),
not in further education or training (i.e. neither formal nor non-formal) during the last four weeks
preceding the survey.
167

## Page 169

NUTS Level N
NUTS 0 (Country) 27
NUTS 1 101
NUTS 2 262
4.4.196 Participation rate in education and training (last 4 weeks), females (eu -
epry2564f )
Female participation rate in education and training during the last four weeks preceding the sur-
vey. The participation rate in education and training covers participation in formal and non-formal
education and training. The reference period for the participation in education and training is
the four weeks prior to the interview. Formal education is dened by ISCED as ’education that
is institutionalised, intentional and planned through public organisations and recognised private
bodies, and - in their totality - constitute the formal education system of a country. Formal ed-
ucation programmes are thus recognised as such by the relevant national education or equivalent
authorities, e.g. any other institution in cooperation with the national or sub-national education
authorities.’ Non-formal education and training is dened as any institutionalised, intentional and
organised/planned learning activities outside the formal education system. According to the clas-
sication of learning activities (CLA 2016), non-formal education and training comprises courses,
seminars and workshops, private lessons or instructions and guided-on-the-job training. However,
non-formal education as measured in the EU-LFS excludes guided-on-the-job training. The in-
formation collected covers both job-related (professional) and non-job related (personal, social,
’leisure’) education and training activities.
168

## Page 170

NUTS Level N
NUTS 0 (Country) 27
NUTS 1 99
NUTS 2 251
4.4.197 Participation rate in education and training (last 4 weeks), males (eu epry2564m)
Male participation rate in education and training during the last four weeks preceding the survey.
The participation rate in education and training covers participation in formal and non-formal
education and training. The reference period for the participation in education and training is
the four weeks prior to the interview. Formal education is dened by ISCED as ’education that
is institutionalised, intentional and planned through public organisations and recognised private
bodies, and - in their totality - constitute the formal education system of a country. Formal ed-
ucation programmes are thus recognised as such by the relevant national education or equivalent
authorities, e.g. any other institution in cooperation with the national or sub-national education
authorities.’ Non-formal education and training is dened as any institutionalised, intentional and
organised/planned learning activities outside the formal education system. According to the clas-
sication of learning activities (CLA 2016), non-formal education and training comprises courses,
seminars and workshops, private lessons or instructions and guided-on-the-job training. However,
non-formal education as measured in the EU-LFS excludes guided-on-the-job training. The in-
formation collected covers both job-related (professional) and non-job related (personal, social,
’leisure’) education and training activities.
169

## Page 171

NUTS Level N
NUTS 0 (Country) 27
NUTS 1 99
NUTS 2 248
4.4.198 Participation rate in education and training (last 4 weeks), total (eu epry2564t)
Participation rate in education and training during the last four weeks preceding the survey. The
participation rate in education and training covers participation in formal and non-formal education
and training. The reference period for the participation in education and training is the four weeks
prior to the interview. Formal education is dened by ISCED as ’education that is institutionalised,
intentional and planned through public organisations and recognised private bodies, and - in their
totality - constitute the formal education system of a country. Formal education programmes are
thus recognised as such by the relevant national education or equivalent authorities, e.g. any other
institution in cooperation with the national or sub-national education authorities.’ Non-formal ed-
ucation and training is dened as any institutionalised, intentional and organised/planned learning
activities outside the formal education system. According to the classication of learning activi-
ties (CLA 2016), non-formal education and training comprises courses, seminars and workshops,
private lessons or instructions and guided-on-the-job training. However, non-formal education as
measured in the EU-LFS excludes guided-on-the-job training. The information collected covers
both job-related (professional) and non-job related (personal, social, ’leisure’) education and train-
ing activities.
170

## Page 172

NUTS Level N
NUTS 0 (Country) 27
NUTS 1 100
NUTS 2 258
4.4.199 Participation rate in primary and lower secondary education (eu epred12)
Participation rate in primary and lower secondary education (levels 1-2). Countries participating
in this collection are compiling their data according to the concepts and denitions of the UOE
data collection manuals on education systems statistics. This aggregate refers to levels 1 and 2 of
the ISCED 2011 (online code ED1-2).
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 79
NUTS 2 171
4.4.200 Participation rate in tertiary education (eu epred58)
Participation rate in tertiary education (level 5-8). Countries participating in this collection are
compiling their data according to the concepts and denitions of the UOE data collection manuals
171

## Page 173

on education systems statistics. This aggregate covers ISCED 2011 levels 5, 6, 7 and 8 (short-cycle
tertiary education, bachelor’s or equivalent level, master’s or equivalent level, doctoral or equivalent
level, online code ED5-8 ’tertiary education’).
NUTS Level N
NUTS 0 (Country) 21
NUTS 1 72
NUTS 2 172
4.4.201 Municipal waste disposal - incineration in thousand tonnes (eu env wasdsp i)
Municipal waste disposal, incineration in thousand tonnes. Municipal waste is mainly produced
by households, similar wastes from sources such as commerce, oces and public institutions are
included. The amount of municipal waste generated consists of waste collected by or on behalf
of municipal authorities and disposed of through the waste management system. The amount of
municipal waste treatment is reported for the treatment operations incineration (with and without
energy recovery), recycling, composting and landlling. Data are available in thousand tonnes and
kilograms per person. Wastes from agriculture and from industries are not included.
172

## Page 174

NUTS Level N
NUTS 0 (Country) 16
NUTS 1 1
NUTS 2 84
4.4.202 Municipal waste generated in thousand tonnes (eu env wasgen)
Municipal waste generated in thousand tonnes. Municipal waste is mainly produced by households,
similar wastes from sources such as commerce, oces and public institutions are included. The
amount of municipal waste generated consists of waste collected by or on behalf of municipal au-
thorities and disposed of through the waste management system. The amount of municipal waste
treatment is reported for the treatment operations incineration (with and without energy recov-
ery), recycling, composting and landlling. Data are available in thousand tonnes and kilograms
per person. Wastes from agriculture and from industries are not included.
NUTS Level N
NUTS 0 (Country) 20
NUTS 1 1
NUTS 2 151
173

## Page 175

4.4.203 Municipal waste recovery - energy recovery in thousand tonnes (eu env -
wasrcv e)
Municipal waste energy recovery in thousand tonnes. Energy recovery is dened as the incineration
that fulls the energy eciency criteria laid down in the Waste Framework Directive (2008/98/EC),
Annex II (recovery operation R1). Municipal waste is mainly produced by households, similar
wastes from sources such as commerce, oces and public institutions are included. The amount
of municipal waste generated consists of waste collected by or on behalf of municipal authorities
and disposed of through the waste management system. The amount of municipal waste treatment
is reported for the treatment operations incineration (with and without energy recovery), recy-
cling, composting and landlling. Data are available in thousand tonnes and kilograms per person.
Wastes from agriculture and from industries are not included.
NUTS Level N
NUTS 0 (Country) 16
NUTS 1 1
NUTS 2 78
4.4.204 Municipal waste recycling in thousand tonnes (eu env wasrcy c d)
Municipal waste recycling in thousand tonnes. Recycling means any recovery operation by which
waste materials are reprocessed into products, materials or substances whether for the original or
other purposes. It includes the reprocessing of organic material but does not include energy recov-
ery and the reprocessing into materials that are to be used as fuels or for backlling operations.
Municipal waste is mainly produced by households, similar wastes from sources such as commerce,
oces and public institutions are included. The amount of municipal waste generated consists of
waste collected by or on behalf of municipal authorities and disposed of through the waste manage-
ment system. The amount of municipal waste treatment is reported for the treatment operations
incineration (with and without energy recovery), recycling, composting and landlling. Data are
available in thousand tonnes and kilograms per person. Wastes from agriculture and from industries
are not included.
174

## Page 176

NUTS Level N
NUTS 0 (Country) 17
NUTS 1 1
NUTS 2 113
4.4.205 Number of cooling degree days (eu eng cdd)
Number of cooling degree days (CDD). Cooling degree day (CDD) index is a weather-based techni-
cal index designed to describe the need for the cooling (air-conditioning) requirements of buildings.
CDD is derived from meteorological observations of air temperature, interpolated to regular grids
at 25 km resolution for Europe. Calculated gridded CDD is aggregated and subsequently presented
on NUTS-2 level, for 2017 and 2018 also on NUTS-3 level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 96
NUTS 2 263
175

## Page 177

4.4.206 Number of heating degree days (eu eng hdd)
Number of heating degree days (HDD). Heating degree day (HDD) index is a weather-based tech-
nical index designed to describe the need for the heating energy requirements of buildings. HDD
is derived from meteorological observations of air temperature, interpolated to regular grids at 25
km resolution for Europe. Calculated gridded HDD is aggregated and subsequently presented on
NUTS-2 level, for 2017 and 2018 also on NUTS-3 level.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 96
NUTS 2 263
4.4.207 Dentists per hundred thousand inhabitants (eu hea dent)
Dentists, per hundred thousand inhabitants. Health care stadata refer to human resources avail-
able for providing health care services in the country, irrespective of the sector of employment
(i.e. whether they are independent, employed by a hospital or any other health care provider).
’Manpower’ categories focus on health care professionals (physicians, dentists, nursing and car-
ing professionals, pharmacists, physiotherapists). Three dierent concepts are used to present the
number of health care professionals: i) ’practising’, i.e. health care professionals providing services
directly to patients; ii) ’professionally active’, i.e. ’practising’ health care professionals plus health
care professionals for whom their medical education is a prerequisite for the execution of the job;
iii) ’licensed to practice’, i.e. health care professionals who are registered and entitled to practice
as health care professionals.
176

## Page 178

NUTS Level N
NUTS 0 (Country) 25
NUTS 1 17
NUTS 2 153
4.4.208 Medical doctors per hundred thousand inhabitants (eu hea mdoc)
Medical doctors, per hundred thousand inhabitants. Health care stadata refer to human resources
available for providing health care services in the country, irrespective of the sector of employment
(i.e. whether they are independent, employed by a hospital or any other health care provider).
’Manpower’ categories focus on health care professionals (physicians, dentists, nursing and car-
ing professionals, pharmacists, physiotherapists). Three dierent concepts are used to present the
number of health care professionals: i) ’practising’, i.e. health care professionals providing services
directly to patients; ii) ’professionally active’, i.e. ’practising’ health care professionals plus health
care professionals for whom their medical education is a prerequisite for the execution of the job;
iii) ’licensed to practice’, i.e. health care professionals who are registered and entitled to practice
as health care professionals.
177

## Page 179

NUTS Level N
NUTS 0 (Country) 26
NUTS 1 17
NUTS 2 161
4.4.209 Nurses and midwives per hundred thousand inhabitants (eu hea nurs)
Nurses and midwives, per hundred thousand inhabitants. Health care stadata refer to human
resources available for providing health care services in the country, irrespective of the sector of
employment (i.e. whether they are independent, employed by a hospital or any other health care
provider). ’Manpower’ categories focus on health care professionals (physicians, dentists, nurs-
ing and caring professionals, pharmacists, physiotherapists). Three dierent concepts are used to
present the number of health care professionals: i) ’practising’, i.e. health care professionals provid-
ing services directly to patients; ii) ’professionally active’, i.e. ’practising’ health care professionals
plus health care professionals for whom their medical education is a prerequisite for the execution
of the job; iii) ’licensed to practice’, i.e. health care professionals who are registered and entitled
to practice as health care professionals.
178

## Page 180

NUTS Level N
NUTS 0 (Country) 19
NUTS 1 1
NUTS 2 107
4.4.210 Pharmacists per hundred thousand inhabitants (eu hea pharm)
Pharmacists per hundred thousand inhabitants. Health care stadata refer to human resources
available for providing health care services in the country, irrespective of the sector of employment
(i.e. whether they are independent, employed by a hospital or any other health care provider).
’Manpower’ categories focus on health care professionals (physicians, dentists, nursing and car-
ing professionals, pharmacists, physiotherapists). Three dierent concepts are used to present the
number of health care professionals: i) ’practising’, i.e. health care professionals providing services
directly to patients; ii) ’professionally active’, i.e. ’practising’ health care professionals plus health
care professionals for whom their medical education is a prerequisite for the execution of the job;
iii) ’licensed to practice’, i.e. health care professionals who are registered and entitled to practice
as health care professionals.
179

## Page 181

NUTS Level N
NUTS 0 (Country) 23
NUTS 1 17
NUTS 2 133
4.4.211 Physiotherapists per hundred thousand inhabitants (eu hea phys)
Physiotherapists per hundred thousand inhabitants. Health care stadata refer to human resources
available for providing health care services in the country, irrespective of the sector of employment
(i.e. whether they are independent, employed by a hospital or any other health care provider).
’Manpower’ categories focus on health care professionals (physicians, dentists, nursing and car-
ing professionals, pharmacists, physiotherapists). Three dierent concepts are used to present the
number of health care professionals: i) ’practising’, i.e. health care professionals providing services
directly to patients; ii) ’professionally active’, i.e. ’practising’ health care professionals plus health
care professionals for whom their medical education is a prerequisite for the execution of the job;
iii) ’licensed to practice’, i.e. health care professionals who are registered and entitled to practice
as health care professionals.
180

## Page 182

NUTS Level N
NUTS 0 (Country) 20
NUTS 1 1
NUTS 2 98
4.4.212 Available beds in hospitals (HP.1) per hundred thousand inhabitants (eu -
hea bed)
Available beds in hospitals (HP.1) per hundred thousand inhabitants. Health care facilities data
refer to available beds in hospitals (HP.1) and subcategories (such as curative care beds, rehabilita-
tive care beds, etc.). Total hospital beds (HP.1) are all hospital beds which are regularly maintained
and staed and immediately available for the care of admitted patients. Total hospital beds are
broken down as follows: i) curative care (acute care) beds; ii) rehabilitative care beds; iii) long-term
care beds (excluding psychiatric care beds) and iv) other hospital beds. The denition of health
care facilities follows the International Classication for Health Accounts - Providers of health care
(ICHA-HP) of the System of Health Accounts (SHA).
NUTS Level N
NUTS 0 (Country) 25
NUTS 1 17
NUTS 2 164
181

## Page 183

4.4.213 Curative care beds in hospitals (HP.1) per hundred thousand inhabitants
(eu hea bedcur)
Curative care beds in hospitals (HP.1) per hundred thousand inhabitants. Health care facilities
data refer to available beds in hospitals (HP.1) and subcategories (such as curative care beds, re-
habilitative care beds, etc.). Total hospital beds (HP.1) are all hospital beds which are regularly
maintained and staed and immediately available for the care of admitted patients. Total hospital
beds are broken down as follows: i) curative care (acute care) beds; ii) rehabilitative care beds; iii)
long-term care beds (excluding psychiatric care beds) and iv) other hospital beds. The denition
of health care facilities follows the International Classication for Health Accounts - Providers of
health care (ICHA-HP) of the System of Health Accounts (SHA).
NUTS Level N
NUTS 0 (Country) 24
NUTS 1 17
NUTS 2 154
4.4.214 Long-term care beds in hospitals (HP.1) per hundred thousand inhabitants
(eu hea bedlt)
Long-term care beds in hospitals (HP.1) per hundred thousand inhabitants. Health care facilities
data refer to available beds in hospitals (HP.1) and subcategories (such as curative care beds, re-
habilitative care beds, etc.). Total hospital beds (HP.1) are all hospital beds which are regularly
maintained and staed and immediately available for the care of admitted patients. Total hospital
beds are broken down as follows: i) curative care (acute care) beds; ii) rehabilitative care beds; iii)
long-term care beds (excluding psychiatric care beds) and iv) other hospital beds. The denition
of health care facilities follows the International Classication for Health Accounts - Providers of
health care (ICHA-HP) of the System of Health Accounts (SHA).
182

## Page 184

NUTS Level N
NUTS 0 (Country) 21
NUTS 1 17
NUTS 2 135
4.4.215 Other beds in hospitals (HP.1) per hundred thousand inhabitants (eu hea -
bedoth)
Other beds in hospitals (HP.1) per hundred thousand inhabitants. Health care facilities data refer
to available beds in hospitals (HP.1) and subcategories (such as curative care beds, rehabilitative
care beds, etc.). Total hospital beds (HP.1) are all hospital beds which are regularly maintained
and staed and immediately available for the care of admitted patients. Total hospital beds are
broken down as follows: i) curative care (acute care) beds; ii) rehabilitative care beds; iii) long-term
care beds (excluding psychiatric care beds) and iv) other hospital beds. The denition of health
care facilities follows the International Classication for Health Accounts - Providers of health care
(ICHA-HP) of the System of Health Accounts (SHA).
NUTS Level N
NUTS 0 (Country) 21
NUTS 1 17
NUTS 2 119
183

## Page 185

4.4.216 Psychiatric care beds in hospitals (HP.1) per hundred thousand inhabitants
(eu hea bedpsy)
Psychiatric care beds in hospitals (HP.1) per hundred thousand inhabitants. Health care facilities
data refer to available beds in hospitals (HP.1) and subcategories (such as curative care beds, re-
habilitative care beds, etc.). Total hospital beds (HP.1) are all hospital beds which are regularly
maintained and staed and immediately available for the care of admitted patients. Total hospital
beds are broken down as follows: i) curative care (acute care) beds; ii) rehabilitative care beds; iii)
long-term care beds (excluding psychiatric care beds) and iv) other hospital beds. The denition
of health care facilities follows the International Classication for Health Accounts - Providers of
health care (ICHA-HP) of the System of Health Accounts (SHA).
NUTS Level N
NUTS 0 (Country) 24
NUTS 1 17
NUTS 2 149
4.4.217 Rehabilitative care beds in hospitals (HP.1) per hundred thousand inhabi-
tants (eu hea bedreh)
Rehabilitative care beds in hospitals (HP.1) per hundred thousand inhabitants. Health care facili-
ties data refer to available beds in hospitals (HP.1) and subcategories (such as curative care beds,
rehabilitative care beds, etc.). Total hospital beds (HP.1) are all hospital beds which are regularly
maintained and staed and immediately available for the care of admitted patients. Total hospital
beds are broken down as follows: i) curative care (acute care) beds; ii) rehabilitative care beds; iii)
long-term care beds (excluding psychiatric care beds) and iv) other hospital beds. The denition
of health care facilities follows the International Classication for Health Accounts - Providers of
health care (ICHA-HP) of the System of Health Accounts (SHA).
184

## Page 186

NUTS Level N
NUTS 0 (Country) 14
NUTS 1 16
NUTS 2 91
4.4.218 Number of deaths by circulatory system diseases, female (eu hea cs f )
Number of deaths by circulatory system diseases, female. Causes of death (COD) statistics are
based on information derived from the medical certicate of cause of death. COD target at the
underlying cause of death, in accordance with the ICD-10 denition i.e.the disease or injury
which initiated the train of morbid events leading directly to death, or the circumstances of the
accident or violence which produced the fatal injury. Expressed in deaths per 100,000 inhabitants,
it is calculated as the number of deaths recorded in the population for a given period divided by
population in the same period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 80
NUTS 2 216
185

## Page 187

4.4.219 Number of deaths by circulatory system diseases, male (eu hea cs m)
Number of deaths by circulatory system diseases, male. Causes of death (COD) statistics are based
on information derived from the medical certicate of cause of death. COD target at the underlying
cause of death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated
the train of morbid events leading directly to death, or the circumstances of the accident or violence
which produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as
the number of deaths recorded in the population for a given period divided by population in the
same period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 80
NUTS 2 217
4.4.220 Number of deaths by circulatory system diseases, total (eu hea cs t)
Number of deaths by circulatory system diseases, total. Causes of death (COD) statistics are based
on information derived from the medical certicate of cause of death. COD target at the underlying
cause of death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated
the train of morbid events leading directly to death, or the circumstances of the accident or violence
which produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as
the number of deaths recorded in the population for a given period divided by population in the
same period and then multiplied by 100,000.
186

## Page 188

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 80
NUTS 2 218
4.4.221 Number of deaths by HIV, female (eu hea hiv f )
Number of deaths by HIV, female. Causes of death (COD) statistics are based on information
derived from the medical certicate of cause of death. COD target at the underlying cause of
death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated the train
of morbid events leading directly to death, or the circumstances of the accident or violence which
produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as the
number of deaths recorded in the population for a given period divided by population in the same
period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 21
NUTS 1 54
NUTS 2 94
187

## Page 189

4.4.222 Number of deaths by HIV, male (eu hea hiv m)
Number of deaths by HIV, male. Causes of death (COD) statistics are based on information derived
from the medical certicate of cause of death. COD target at the underlying cause of death, in
accordance with the ICD-10 denition i.e.the disease or injury which initiated the train of morbid
events leading directly to death, or the circumstances of the accident or violence which produced
the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as the number of
deaths recorded in the population for a given period divided by population in the same period and
then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 71
NUTS 2 150
4.4.223 Number of deaths by HIV, total (eu hea hiv t)
Number of deaths by HIV, total. Causes of death (COD) statistics are based on information derived
from the medical certicate of cause of death. COD target at the underlying cause of death, in
accordance with the ICD-10 denition i.e.the disease or injury which initiated the train of morbid
events leading directly to death, or the circumstances of the accident or violence which produced
the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as the number of
deaths recorded in the population for a given period divided by population in the same period and
then multiplied by 100,000.
188

## Page 190

NUTS Level N
NUTS 0 (Country) 27
NUTS 1 72
NUTS 2 160
4.4.224 Number of deaths by infectious and parasitic diseases, female (eu hea ipd f )
Number of deaths by infectious and parasitic diseases, female. Causes of death (COD) statistics
are based on information derived from the medical certicate of cause of death. COD target at
the underlying cause of death, in accordance with the ICD-10 denition i.e.the disease or injury
which initiated the train of morbid events leading directly to death, or the circumstances of the
accident or violence which produced the fatal injury. Expressed in deaths per 100,000 inhabitants,
it is calculated as the number of deaths recorded in the population for a given period divided by
population in the same period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 78
NUTS 2 212
189

## Page 191

4.4.225 Number of deaths by infectious and parasitic diseases, male (eu hea ipd m)
Number of deaths by infectious and parasitic diseases, male. Causes of death (COD) statistics
are based on information derived from the medical certicate of cause of death. COD target at
the underlying cause of death, in accordance with the ICD-10 denition i.e.the disease or injury
which initiated the train of morbid events leading directly to death, or the circumstances of the
accident or violence which produced the fatal injury. Expressed in deaths per 100,000 inhabitants,
it is calculated as the number of deaths recorded in the population for a given period divided by
population in the same period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 79
NUTS 2 214
4.4.226 Number of deaths by infectious and parasitic diseases, total (eu hea ipd t)
Number of deaths by infectious and parasitic diseases, total. Causes of death (COD) statistics
are based on information derived from the medical certicate of cause of death. COD target at
the underlying cause of death, in accordance with the ICD-10 denition i.e.the disease or injury
which initiated the train of morbid events leading directly to death, or the circumstances of the
accident or violence which produced the fatal injury. Expressed in deaths per 100,000 inhabitants,
it is calculated as the number of deaths recorded in the population for a given period divided by
population in the same period and then multiplied by 100,000.
190

## Page 192

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 79
NUTS 2 214
4.4.227 Number of deaths by malignant neoplasms, female (eu hea np f )
Number of deaths by malignant neoplasms, female. Causes of death (COD) statistics are based on
information derived from the medical certicate of cause of death. COD target at the underlying
cause of death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated
the train of morbid events leading directly to death, or the circumstances of the accident or violence
which produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as
the number of deaths recorded in the population for a given period divided by population in the
same period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 79
NUTS 2 215
191

## Page 193

4.4.228 Number of deaths by malignant neoplasms, male (eu hea np m)
Number of deaths by malignant neoplasms, male. Causes of death (COD) statistics are based on
information derived from the medical certicate of cause of death. COD target at the underlying
cause of death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated
the train of morbid events leading directly to death, or the circumstances of the accident or violence
which produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as
the number of deaths recorded in the population for a given period divided by population in the
same period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 80
NUTS 2 215
4.4.229 Number of deaths by malignant neoplasms, total (eu hea np t)
Number of deaths by malignant neoplasms, total. Causes of death (COD) statistics are based on
information derived from the medical certicate of cause of death. COD target at the underlying
cause of death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated
the train of morbid events leading directly to death, or the circumstances of the accident or violence
which produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as
the number of deaths recorded in the population for a given period divided by population in the
same period and then multiplied by 100,000.
192

## Page 194

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 80
NUTS 2 216
4.4.230 Number of deaths by nervous system diseases, female (eu hea ns f )
Number of deaths by nervous system diseases, female. Causes of death (COD) statistics are based
on information derived from the medical certicate of cause of death. COD target at the underlying
cause of death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated
the train of morbid events leading directly to death, or the circumstances of the accident or violence
which produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as
the number of deaths recorded in the population for a given period divided by population in the
same period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 77
NUTS 2 212
193

## Page 195

4.4.231 Number of deaths by nervous system diseases, male (eu hea ns m)
Number of deaths by nervous system diseases, male. Causes of death (COD) statistics are based on
information derived from the medical certicate of cause of death. COD target at the underlying
cause of death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated
the train of morbid events leading directly to death, or the circumstances of the accident or violence
which produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as
the number of deaths recorded in the population for a given period divided by population in the
same period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 78
NUTS 2 213
4.4.232 Number of deaths by nervous system diseases, total (eu hea ns t)
Number of deaths by nervous system diseases, total. Causes of death (COD) statistics are based on
information derived from the medical certicate of cause of death. COD target at the underlying
cause of death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated
the train of morbid events leading directly to death, or the circumstances of the accident or violence
which produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as
the number of deaths recorded in the population for a given period divided by population in the
same period and then multiplied by 100,000.
194

## Page 196

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 78
NUTS 2 213
4.4.233 Number of deaths by pregnancy, childbirth and puerperium (eu hea pr f )
Number of deaths by pregnancy, childbirth and puerperium. Causes of death (COD) statistics are
based on information derived from the medical certicate of cause of death. COD target at the
underlying cause of death, in accordance with the ICD-10 denition i.e.the disease or injury
which initiated the train of morbid events leading directly to death, or the circumstances of the
accident or violence which produced the fatal injury. Expressed in deaths per 100,000 inhabitants,
it is calculated as the number of deaths recorded in the population for a given period divided by
population in the same period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 22
NUTS 1 49
NUTS 2 43
195

## Page 197

4.4.234 Number of deaths by self-harm, female (eu hea sh f )
Number of deaths by self-harm, female. Causes of death (COD) statistics are based on informa-
tion derived from the medical certicate of cause of death. COD target at the underlying cause
of death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated the
train of morbid events leading directly to death, or the circumstances of the accident or violence
which produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as
the number of deaths recorded in the population for a given period divided by population in the
same period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 77
NUTS 2 208
4.4.235 Number of deaths by self-harm, male (eu hea sh m)
Number of deaths by self-harm, male. Causes of death (COD) statistics are based on information
derived from the medical certicate of cause of death. COD target at the underlying cause of
death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated the train
of morbid events leading directly to death, or the circumstances of the accident or violence which
produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as the
number of deaths recorded in the population for a given period divided by population in the same
period and then multiplied by 100,000.
196

## Page 198

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 79
NUTS 2 215
4.4.236 Number of deaths by self-harm, total (eu hea sh t)
Number of deaths by self-harm, total. Causes of death (COD) statistics are based on information
derived from the medical certicate of cause of death. COD target at the underlying cause of
death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated the train
of morbid events leading directly to death, or the circumstances of the accident or violence which
produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as the
number of deaths recorded in the population for a given period divided by population in the same
period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 79
NUTS 2 216
197

## Page 199

4.4.237 Number of deaths by drug dependence, female (eu hea tox f )
Number of deaths by drug dependence, female. Causes of death (COD) statistics are based on
information derived from the medical certicate of cause of death. COD target at the underlying
cause of death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated
the train of morbid events leading directly to death, or the circumstances of the accident or violence
which produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as
the number of deaths recorded in the population for a given period divided by population in the
same period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 12
NUTS 1 26
NUTS 2 27
4.4.238 Number of deaths by drug dependence, male (eu hea tox m)
Number of deaths by drug dependence, male. Causes of death (COD) statistics are based on infor-
mation derived from the medical certicate of cause of death. COD target at the underlying cause
of death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated the
train of morbid events leading directly to death, or the circumstances of the accident or violence
which produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as
the number of deaths recorded in the population for a given period divided by population in the
same period and then multiplied by 100,000.
198

## Page 200

NUTS Level N
NUTS 0 (Country) 18
NUTS 1 46
NUTS 2 84
4.4.239 Number of deaths by drug dependence, total (eu hea tox t)
Number of deaths by drug dependence, total. Causes of death (COD) statistics are based on infor-
mation derived from the medical certicate of cause of death. COD target at the underlying cause
of death, in accordance with the ICD-10 denition i.e.the disease or injury which initiated the
train of morbid events leading directly to death, or the circumstances of the accident or violence
which produced the fatal injury. Expressed in deaths per 100,000 inhabitants, it is calculated as
the number of deaths recorded in the population for a given period divided by population in the
same period and then multiplied by 100,000.
NUTS Level N
NUTS 0 (Country) 18
NUTS 1 48
NUTS 2 96
199

## Page 201

4.4.240 Percentage of households with internet access (eu is iacc)
Percentage of households with internet access. Data given in this domain are collected annually
by the National Statistical Institutes and are based on Eurostat’s annual model questionnaires on
ICT (Information and Communication Technologies) usage in households and by individuals. The
survey comprises questions at household level and individual level. The population of households
consists of all private households having at least one member in the age group 16 to 74 years.
The population of individuals consists of all individuals aged 16 to 74 (on an optional basis some
countries collect separate data on other age groups, individuals aged 15 years or less, aged 75 or
more). Regional breakdowns have been provided on a voluntary basis for 2006 and 2007 according
to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of NUTS1 breakdowns
is obligatory (regional breakdowns for all countries are available) while NUTS2 breakdowns are still
optional.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 88
NUTS 2 136
4.4.241 Percentage of households with broadband internet access (eu is bacc)
Percentage of households with broadband internet access. Data given in this domain are collected
annually by the National Statistical Institutes and are based on Eurostat’s annual model ques-
tionnaires on ICT (Information and Communication Technologies) usage in households and by
individuals. The survey comprises questions at household level and individual level. The popula-
tion of households consists of all private households having at least one member in the age group 16
to 74 years. The population of individuals consists of all individuals aged 16 to 74 (on an optional
basis some countries collect separate data on other age groups, individuals aged 15 years or less,
aged 75 or more). Regional breakdowns have been provided on a voluntary basis for 2006 and
2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of
NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available) while NUTS2
breakdowns are still optional.
200

## Page 202

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 86
NUTS 2 135
4.4.242 Percentage of individuals who have never used a computer (eu iu never)
Percentage of individuals who have never used a computer. Data given in this domain are col-
lected annually by the National Statistical Institutes and are based on Eurostat’s annual model
questionnaires on ICT (Information and Communication Technologies) usage in households and by
individuals. The survey comprises questions at household level and individual level. The population
of households consists of all private households having at least one member in the age group 16 to
74 years. The population of individuals consists of all individuals aged 16 to 74 (on an optional
basis some countries collect separate data on other age groups, individuals aged 15 years or less,
aged 75 or more). Regional breakdowns have been provided on a voluntary basis for 2006 and
2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of
NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available) while NUTS2
breakdowns are still optional.
201

## Page 203

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 81
NUTS 2 129
4.4.243 Percentage of individuals who accessed the internet away from home or work
(eu iu ohw)
Percentage of individuals who accessed the internet away from home or work. Data given in this do-
main are collected annually by the National Statistical Institutes and are based on Eurostat’s annual
model questionnaires on ICT (Information and Communication Technologies) usage in households
and by individuals. The survey comprises questions at household level and individual level. The
population of households consists of all private households having at least one member in the age
group 16 to 74 years. The population of individuals consists of all individuals aged 16 to 74 (on an
optional basis some countries collect separate data on other age groups, individuals aged 15 years
or less, aged 75 or more). Regional breakdowns have been provided on a voluntary basis for 2006
and 2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of
NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available) while NUTS2
breakdowns are still optional.
202

## Page 204

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 156
4.4.244 Percentage of individuals who accessed the internet away from home or work,
last 3 months (eu iu ohw3)
Percentage of individuals who accessed the internet away from home or work in the last 3 months.
Data given in this domain are collected annually by the National Statistical Institutes and are based
on Eurostat’s annual model questionnaires on ICT (Information and Communication Technologies)
usage in households and by individuals. The survey comprises questions at household level and
individual level. The population of households consists of all private households having at least one
member in the age group 16 to 74 years. The population of individuals consists of all individuals
aged 16 to 74 (on an optional basis some countries collect separate data on other age groups, in-
dividuals aged 15 years or less, aged 75 or more). Regional breakdowns have been provided on a
voluntary basis for 2006 and 2007 according to NUTS1 or NUTS2 by several countries. Starting
from 2008, the collection of NUTS1 breakdowns is obligatory (regional breakdowns for all countries
are available) while NUTS2 breakdowns are still optional.
203

## Page 205

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 155
4.4.245 Percentage of individuals using internet to interact with public authorities
(eu iu govform)
Percentage of individuals using the internet to interact with public authorities. Data given in
this domain are collected annually by the National Statistical Institutes and are based on Euro-
stat’s annual model questionnaires on ICT (Information and Communication Technologies) usage
in households and by individuals. The survey comprises questions at household level and individual
level. The population of households consists of all private households having at least one member
in the age group 16 to 74 years. The population of individuals consists of all individuals aged 16 to
74 (on an optional basis some countries collect separate data on other age groups, individuals aged
15 years or less, aged 75 or more). Regional breakdowns have been provided on a voluntary basis
for 2006 and 2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the
collection of NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available)
while NUTS2 breakdowns are still optional.
204

## Page 206

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 156
4.4.246 Percentage of individuals using internet to submit forms to authorities (eu -
iu govint)
Percentage of individuals using the internet to submit forms to authorities. Data given in this do-
main are collected annually by the National Statistical Institutes and are based on Eurostat’s annual
model questionnaires on ICT (Information and Communication Technologies) usage in households
and by individuals. The survey comprises questions at household level and individual level. The
population of households consists of all private households having at least one member in the age
group 16 to 74 years. The population of individuals consists of all individuals aged 16 to 74 (on an
optional basis some countries collect separate data on other age groups, individuals aged 15 years
or less, aged 75 or more). Regional breakdowns have been provided on a voluntary basis for 2006
and 2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of
NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available) while NUTS2
breakdowns are still optional.
205

## Page 207

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 96
NUTS 2 154
4.4.247 Frequency of internet access: daily (eu iu iday)
Percentage of individuals using the internet on a daily basis. Data given in this domain are col-
lected annually by the National Statistical Institutes and are based on Eurostat’s annual model
questionnaires on ICT (Information and Communication Technologies) usage in households and by
individuals. The survey comprises questions at household level and individual level. The population
of households consists of all private households having at least one member in the age group 16 to
74 years. The population of individuals consists of all individuals aged 16 to 74 (on an optional
basis some countries collect separate data on other age groups, individuals aged 15 years or less,
aged 75 or more). Regional breakdowns have been provided on a voluntary basis for 2006 and
2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of
NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available) while NUTS2
breakdowns are still optional.
206

## Page 208

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 156
4.4.248 Last internet use: in the last 12 months (eu iu ilt12)
Percentage of individuals who used the internet in the last 12 months. Data given in this domain
are collected annually by the National Statistical Institutes and are based on Eurostat’s annual
model questionnaires on ICT (Information and Communication Technologies) usage in households
and by individuals. The survey comprises questions at household level and individual level. The
population of households consists of all private households having at least one member in the age
group 16 to 74 years. The population of individuals consists of all individuals aged 16 to 74 (on an
optional basis some countries collect separate data on other age groups, individuals aged 15 years
or less, aged 75 or more). Regional breakdowns have been provided on a voluntary basis for 2006
and 2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of
NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available) while NUTS2
breakdowns are still optional.
207

## Page 209

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 156
4.4.249 Last internet use: in last 3 months (eu iu iu3)
Percentage of individuals who used the internet in the last 3 months. Data given in this domain
are collected annually by the National Statistical Institutes and are based on Eurostat’s annual
model questionnaires on ICT (Information and Communication Technologies) usage in households
and by individuals. The survey comprises questions at household level and individual level. The
population of households consists of all private households having at least one member in the age
group 16 to 74 years. The population of individuals consists of all individuals aged 16 to 74 (on an
optional basis some countries collect separate data on other age groups, individuals aged 15 years
or less, aged 75 or more). Regional breakdowns have been provided on a voluntary basis for 2006
and 2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of
NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available) while NUTS2
breakdowns are still optional.
208

## Page 210

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 156
4.4.250 Internet use: internet banking (eu iu iubk)
Percentage of individuals using the internet banking. Data given in this domain are collected annu-
ally by the National Statistical Institutes and are based on Eurostat’s annual model questionnaires
on ICT (Information and Communication Technologies) usage in households and by individuals.
The survey comprises questions at household level and individual level. The population of house-
holds consists of all private households having at least one member in the age group 16 to 74 years.
The population of individuals consists of all individuals aged 16 to 74 (on an optional basis some
countries collect separate data on other age groups, individuals aged 15 years or less, aged 75 or
more). Regional breakdowns have been provided on a voluntary basis for 2006 and 2007 according
to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of NUTS1 breakdowns
is obligatory (regional breakdowns for all countries are available) while NUTS2 breakdowns are still
optional.
209

## Page 211

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 97
NUTS 2 156
4.4.251 Internet use: civic or political participation (eu iu iucpp)
Percentage of individuals using the internet for civic and political participation. Data given in
this domain are collected annually by the National Statistical Institutes and are based on Euro-
stat’s annual model questionnaires on ICT (Information and Communication Technologies) usage
in households and by individuals. The survey comprises questions at household level and individual
level. The population of households consists of all private households having at least one member
in the age group 16 to 74 years. The population of individuals consists of all individuals aged 16 to
74 (on an optional basis some countries collect separate data on other age groups, individuals aged
15 years or less, aged 75 or more). Regional breakdowns have been provided on a voluntary basis
for 2006 and 2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the
collection of NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available)
while NUTS2 breakdowns are still optional.
210

## Page 212

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 102
NUTS 2 167
4.4.252 Frequency of internet access: once a week (including every day) (eu iu iuse)
Percentage of individuals using the internet at least once a week. Data given in this domain are
collected annually by the National Statistical Institutes and are based on Eurostat’s annual model
questionnaires on ICT (Information and Communication Technologies) usage in households and by
individuals. The survey comprises questions at household level and individual level. The population
of households consists of all private households having at least one member in the age group 16 to
74 years. The population of individuals consists of all individuals aged 16 to 74 (on an optional
basis some countries collect separate data on other age groups, individuals aged 15 years or less,
aged 75 or more). Regional breakdowns have been provided on a voluntary basis for 2006 and
2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of
NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available) while NUTS2
breakdowns are still optional.
211

## Page 213

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 88
NUTS 2 136
4.4.253 Internet use: selling goods or services (eu iu iusell)
Percentage of individuals using the internet to sell goods or services. Data given in this domain
are collected annually by the National Statistical Institutes and are based on Eurostat’s annual
model questionnaires on ICT (Information and Communication Technologies) usage in households
and by individuals. The survey comprises questions at household level and individual level. The
population of households consists of all private households having at least one member in the age
group 16 to 74 years. The population of individuals consists of all individuals aged 16 to 74 (on an
optional basis some countries collect separate data on other age groups, individuals aged 15 years
or less, aged 75 or more). Regional breakdowns have been provided on a voluntary basis for 2006
and 2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of
NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available) while NUTS2
breakdowns are still optional.
212

## Page 214

NUTS Level N
NUTS 0 (Country) 27
NUTS 1 98
NUTS 2 156
4.4.254 Internet use: participating in social networks (eu iu iusnet)
Percentage of individuals using the internet to participate in social networks. Data given in this do-
main are collected annually by the National Statistical Institutes and are based on Eurostat’s annual
model questionnaires on ICT (Information and Communication Technologies) usage in households
and by individuals. The survey comprises questions at household level and individual level. The
population of households consists of all private households having at least one member in the age
group 16 to 74 years. The population of individuals consists of all individuals aged 16 to 74 (on an
optional basis some countries collect separate data on other age groups, individuals aged 15 years
or less, aged 75 or more). Regional breakdowns have been provided on a voluntary basis for 2006
and 2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of
NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available) while NUTS2
breakdowns are still optional.
213

## Page 215

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 99
NUTS 2 159
4.4.255 Internet use: never (eu iu iux)
Percentage of individuals who have never used the internet. Data given in this domain are col-
lected annually by the National Statistical Institutes and are based on Eurostat’s annual model
questionnaires on ICT (Information and Communication Technologies) usage in households and by
individuals. The survey comprises questions at household level and individual level. The population
of households consists of all private households having at least one member in the age group 16 to
74 years. The population of individuals consists of all individuals aged 16 to 74 (on an optional
basis some countries collect separate data on other age groups, individuals aged 15 years or less,
aged 75 or more). Regional breakdowns have been provided on a voluntary basis for 2006 and
2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of
NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available) while NUTS2
breakdowns are still optional.
214

## Page 216

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 94
NUTS 2 149
4.4.256 Last online purchase: between 3 and 12 months ago (eu igs b3 12)
Percentage of individuals whose last online purchase between 3 and 12 months ago. Data given in
this domain are collected annually by the National Statistical Institutes and are based on Euro-
stat’s annual model questionnaires on ICT (Information and Communication Technologies) usage
in households and by individuals. The survey comprises questions at household level and individual
level. The population of households consists of all private households having at least one member
in the age group 16 to 74 years. The population of individuals consists of all individuals aged 16 to
74 (on an optional basis some countries collect separate data on other age groups, individuals aged
15 years or less, aged 75 or more). Regional breakdowns have been provided on a voluntary basis
for 2006 and 2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the
collection of NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available)
while NUTS2 breakdowns are still optional.
215

## Page 217

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 156
4.4.257 Online purchases: from sellers from other EU countries (eu igs bfeu)
Percentage of individuals who have made online purchases from sellers in other EU countries. Data
given in this domain are collected annually by the National Statistical Institutes and are based on
Eurostat’s annual model questionnaires on ICT (Information and Communication Technologies)
usage in households and by individuals. The survey comprises questions at household level and
individual level. The population of households consists of all private households having at least one
member in the age group 16 to 74 years. The population of individuals consists of all individuals
aged 16 to 74 (on an optional basis some countries collect separate data on other age groups, in-
dividuals aged 15 years or less, aged 75 or more). Regional breakdowns have been provided on a
voluntary basis for 2006 and 2007 according to NUTS1 or NUTS2 by several countries. Starting
from 2008, the collection of NUTS1 breakdowns is obligatory (regional breakdowns for all countries
are available) while NUTS2 breakdowns are still optional.
216

## Page 218

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 156
4.4.258 Online purchases: travel and holiday accommodation (eu igs bhols)
Percentage of individuals who purchased travel and holiday accommodation online. Data given in
this domain are collected annually by the National Statistical Institutes and are based on Euro-
stat’s annual model questionnaires on ICT (Information and Communication Technologies) usage
in households and by individuals. The survey comprises questions at household level and individual
level. The population of households consists of all private households having at least one member
in the age group 16 to 74 years. The population of individuals consists of all individuals aged 16 to
74 (on an optional basis some countries collect separate data on other age groups, individuals aged
15 years or less, aged 75 or more). Regional breakdowns have been provided on a voluntary basis
for 2006 and 2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the
collection of NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available)
while NUTS2 breakdowns are still optional.
217

## Page 219

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 156
4.4.259 Last online purchase: in the 12 months (eu igs blt12)
Percentage of individuals who made an online purchase in the 12 months. Data given in this do-
main are collected annually by the National Statistical Institutes and are based on Eurostat’s annual
model questionnaires on ICT (Information and Communication Technologies) usage in households
and by individuals. The survey comprises questions at household level and individual level. The
population of households consists of all private households having at least one member in the age
group 16 to 74 years. The population of individuals consists of all individuals aged 16 to 74 (on an
optional basis some countries collect separate data on other age groups, individuals aged 15 years
or less, aged 75 or more). Regional breakdowns have been provided on a voluntary basis for 2006
and 2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of
NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available) while NUTS2
breakdowns are still optional.
218

## Page 220

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 87
NUTS 2 136
4.4.260 Individuals who ordered goods or services in internet more than a year ago
or never (eu igs bumt12x)
Percentage of individuals who ordered goods or services in internet more than a year ago or never.
Data given in this domain are collected annually by the National Statistical Institutes and are based
on Eurostat’s annual model questionnaires on ICT (Information and Communication Technologies)
usage in households and by individuals. The survey comprises questions at household level and
individual level. The population of households consists of all private households having at least one
member in the age group 16 to 74 years. The population of individuals consists of all individuals
aged 16 to 74 (on an optional basis some countries collect separate data on other age groups, in-
dividuals aged 15 years or less, aged 75 or more). Regional breakdowns have been provided on a
voluntary basis for 2006 and 2007 according to NUTS1 or NUTS2 by several countries. Starting
from 2008, the collection of NUTS1 breakdowns is obligatory (regional breakdowns for all countries
are available) while NUTS2 breakdowns are still optional.
219

## Page 221

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 156
4.4.261 Last online purchase: in the last 3 months (eu igs buy3)
Percentage of individuals who made an online purchase in the last 3 months. Data given in this do-
main are collected annually by the National Statistical Institutes and are based on Eurostat’s annual
model questionnaires on ICT (Information and Communication Technologies) usage in households
and by individuals. The survey comprises questions at household level and individual level. The
population of households consists of all private households having at least one member in the age
group 16 to 74 years. The population of individuals consists of all individuals aged 16 to 74 (on an
optional basis some countries collect separate data on other age groups, individuals aged 15 years
or less, aged 75 or more). Regional breakdowns have been provided on a voluntary basis for 2006
and 2007 according to NUTS1 or NUTS2 by several countries. Starting from 2008, the collection of
NUTS1 breakdowns is obligatory (regional breakdowns for all countries are available) while NUTS2
breakdowns are still optional.
220

## Page 222

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 156
4.4.262 Employment rate for 15-24 years old, female (eu emp 1524f )
Employment rate for women between 15-24 years old. The source for the regional labour market
information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 255
221

## Page 223

4.4.263 Employment rate for 15-24 years old, male (eu emp 1524m)
Employment rate for men between 15-24 years old. The source for the regional labour market
information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 101
NUTS 2 260
4.4.264 Employment rate for 15-24 years old, total (eu emp 1524t)
Total employment rate between 15-24 years old. The source for the regional labour market infor-
mation is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
222

## Page 224

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 102
NUTS 2 265
4.4.265 Employment rate for 20-64 years old, female (eu emp 2064f )
Employment rate for women between 20-64 years old. The source for the regional labour market
information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 267
223

## Page 225

4.4.266 Employment rate for 20-64 years old, male (eu emp 2064m)
Employment rate for men between 20-64 years old. The source for the regional labour market
information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 267
4.4.267 Employment rate for 20-64 years old, total (eu emp 2064t)
Total employment rate between 20-64 years old. The source for the regional labour market infor-
mation is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
224

## Page 226

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 267
4.4.268 Employment rate for 25-34 years old, female (eu emp 2534f )
Employment rate for women between 25-34 years old. The source for the regional labour market
information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 102
NUTS 2 265
225

## Page 227

4.4.269 Employment rate for 25-34 years old, male (eu emp 2534m)
Employment rate for men between 25-34 years old. The source for the regional labour market
information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 102
NUTS 2 265
4.4.270 Employment rate for 25-34 years old, total (eu emp 2534t)
Total employment rate between 25-34 years old. The source for the regional labour market infor-
mation is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
226

## Page 228

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 267
4.4.271 Employment rate for +25 years, female (eu emp ge25f )
Employment rate for women 25 years old and above. The source for the regional labour market
information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 267
227

## Page 229

4.4.272 Employment rate for +25 years, male (eu emp ge25m)
Employment rate for men 25 years old and above. The source for the regional labour market in-
formation is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 267
4.4.273 Employment rate for +25 years, total (eu emp ge25t)
Total employment rate for 25 years old and above. The source for the regional labour market
information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
228

## Page 230

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 267
4.4.274 Employment rate for +65 years, female (eu emp ge65f )
Employment rate for women 65 years old and above. The source for the regional labour market
information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 26
NUTS 1 79
NUTS 2 142
229

## Page 231

4.4.275 Employment rate for +65 years, male (eu emp ge65m)
Employment rate for men 65 years old and above. The source for the regional labour market in-
formation is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 27
NUTS 1 88
NUTS 2 189
4.4.276 Employment rate for +65 years, total (eu emp ge65t)
Total employment rate for 65 years old and above. The source for the regional labour market
information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
230

## Page 232

NUTS Level N
NUTS 0 (Country) 27
NUTS 1 92
NUTS 2 215
4.4.277 Employment in agriculture, forestry andshing, in thousands (eu emp a)
Employment in agriculture, forestry andshing, in thousands. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO). The denition of unemployment is further specied
in Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 97
NUTS 2 254
231

## Page 233

4.4.278 Employment in industry (except construction), in thousands (eu emp be)
Employment in industry (except construction), in thousands. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO). The denition of unemployment is further specied
in Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 274
4.4.279 Employment in construction, in thousands (eu emp f )
Employment in construction, in thousands. The source for the regional labour market information
is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey conducted
in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries (Montene-
gro, North Macedonia, Serbia and Turkey). The denitions of employment and unemployment, as
well as other survey characteristics follow the denitions and recommendations of the International
Labour Organisation (ILO). The denition of unemployment is further specied in Commission
Regulation (EC) No 1897/2000.
232

## Page 234

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 275
4.4.280 Employment in wholesale and retail trade, transport, accommodation and
food service activities, in thousands (eu emp gi)
Employment in wholesale and retail trade, transport, accommodation and food service activities, in
thousands. The source for the regional labour market information is the EU Labour Force Survey
(EU-LFS). This is a quarterly household sample survey conducted in all Member States of the EU,
the United Kingdom, EFTA and Candidate Countries (Montenegro, North Macedonia, Serbia and
Turkey). The denitions of employment and unemployment, as well as other survey characteristics
follow the denitions and recommendations of the International Labour Organisation (ILO). The
denition of unemployment is further specied in Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 104
NUTS 2 277
233

## Page 235

4.4.281 Employment in information and communication, in thousands (eu emp j)
Employment in information and communication, in thousands. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO). The denition of unemployment is further specied
in Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 248
4.4.282 Employment innancial and insurance activities, in thousands (eu emp k)
Employment innancial and insurance activities, in thousands. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO). The denition of unemployment is further specied
in Commission Regulation (EC) No 1897/2000.
234

## Page 236

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 259
4.4.283 Employment in real estate activities, in thousands (eu emp l)
Employment in real estate activities, in thousands. The source for the regional labour market in-
formation is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 92
NUTS 2 175
235

## Page 237

4.4.284 Employment in professional, scientic and technical activities, in thousands
(eu emp m n)
Employment in professional, scientic and technical activities, in thousands. The source for the
regional labour market information is the EU Labour Force Survey (EU-LFS). This is a quarterly
household sample survey conducted in all Member States of the EU, the United Kingdom, EFTA
and Candidate Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of
employment and unemployment, as well as other survey characteristics follow the denitions and
recommendations of the International Labour Organisation (ILO). The denition of unemployment
is further specied in Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 102
NUTS 2 275
4.4.285 Employment in public administration, defence, education, human health and
social work activities, in thousands (eu emp oq)
Employment in public administration, defence, education, human health and social work activities,
in thousands. The source for the regional labour market information is the EU Labour Force Survey
(EU-LFS). This is a quarterly household sample survey conducted in all Member States of the EU,
the United Kingdom, EFTA and Candidate Countries (Montenegro, North Macedonia, Serbia and
Turkey). The denitions of employment and unemployment, as well as other survey characteristics
follow the denitions and recommendations of the International Labour Organisation (ILO). The
denition of unemployment is further specied in Commission Regulation (EC) No 1897/2000.
236

## Page 238

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 104
NUTS 2 277
4.4.286 Employment in arts, entertainment and recreation, in thousands (eu emp ru)
Employment in arts, entertainment and recreation, in thousands. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO). The denition of unemployment is further specied
in Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 275
237

## Page 239

4.4.287 Employment in total - all NACE activities, in thousands (eu emp total)
Employment in total - all NACE activities, in thousands. The source for the regional labour market
information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey
conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries
(Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and unem-
ployment, as well as other survey characteristics follow the denitions and recommendations of the
International Labour Organisation (ILO). The denition of unemployment is further specied in
Commission Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 104
NUTS 2 277
4.4.288 Full-time employment, female, in thousands (eu emp ft f )
Full-time female employment, in thousands. The source for the regional labour market information
is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey conducted
in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries (Montene-
gro, North Macedonia, Serbia and Turkey). The denitions of employment and unemployment, as
well as other survey characteristics follow the denitions and recommendations of the International
Labour Organisation (ILO). The denition of unemployment is further specied in Commission
Regulation (EC) No 1897/2000.
238

## Page 240

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 267
4.4.289 Full-time employment, male, in thousands (eu emp ft m)
Full-time male employment, in thousands. The source for the regional labour market information
is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey conducted
in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries (Montene-
gro, North Macedonia, Serbia and Turkey). The denitions of employment and unemployment, as
well as other survey characteristics follow the denitions and recommendations of the International
Labour Organisation (ILO). The denition of unemployment is further specied in Commission
Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 267
239

## Page 241

4.4.290 Full-time employment, total, in thousands (eu emp ft t)
Total full-time employment, in thousands. The source for the regional labour market information
is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey conducted
in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries (Montene-
gro, North Macedonia, Serbia and Turkey). The denitions of employment and unemployment, as
well as other survey characteristics follow the denitions and recommendations of the International
Labour Organisation (ILO). The denition of unemployment is further specied in Commission
Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 267
4.4.291 Part-time employment, female, in thousands (eu emp pt f )
Part-time female employment, in thousands. The source for the regional labour market information
is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey conducted
in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries (Montene-
gro, North Macedonia, Serbia and Turkey). The denitions of employment and unemployment, as
well as other survey characteristics follow the denitions and recommendations of the International
Labour Organisation (ILO). The denition of unemployment is further specied in Commission
Regulation (EC) No 1897/2000.
240

## Page 242

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 102
NUTS 2 263
4.4.292 Part-time employment, male, in thousands (eu emp pt m)
Part-time male employment, in thousands. The source for the regional labour market information
is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey conducted
in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries (Montene-
gro, North Macedonia, Serbia and Turkey). The denitions of employment and unemployment, as
well as other survey characteristics follow the denitions and recommendations of the International
Labour Organisation (ILO). The denition of unemployment is further specied in Commission
Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 254
241

## Page 243

4.4.293 Part-time employment, total, in thousands (eu emp pt t)
Total part-time employment, in thousands. The source for the regional labour market information
is the EU Labour Force Survey (EU-LFS). This is a quarterly household sample survey conducted
in all Member States of the EU, the United Kingdom, EFTA and Candidate Countries (Montene-
gro, North Macedonia, Serbia and Turkey). The source for the regional labour market information
is the EU Labour Force Survey (EU-LFS). The denitions of employment and unemployment, as
well as other survey characteristics follow the denitions and recommendations of the International
Labour Organisation (ILO). The denition of unemployment is further specied in Commission
Regulation (EC) No 1897/2000.
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 103
NUTS 2 266
4.4.294 Long-term unemployment as percentage of active population (eu ltu pc act)
Long-term unemployment as a percentage of active population. Long-term unemployment is de-
ned as being unemployed for 12 months or longer. Unemployed persons comprise persons aged 15
to 74 who full all the three following conditions: - are without work during the reference week; -
are available to start work within the next two weeks; - have been actively seeking work in the past
four weeks or have already found a job to start within the next three months. The source for the
regional labour market information is the EU Labour Force Survey (EU-LFS). This is a quarterly
household sample survey conducted in all Member States of the EU, the United Kingdom, EFTA
and Candidate Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of
employment and unemployment, as well as other survey characteristics follow the denitions and
recommendations of the International Labour Organisation (ILO).
242

## Page 244

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 99
NUTS 2 239
4.4.295 Long-term unemployment as percentage of unemployment (eu ltu pc une)
Long-term unemployment as a percentage of unemployment. Long-term unemployment is dened
as being unemployed for 12 months or longer. Unemployed persons comprise persons aged 15 to
74 who full all the three following conditions: - are without work during the reference week; - are
available to start work within the next two weeks; - have been actively seeking work in the past
four weeks or have already found a job to start within the next three months. The source for the
regional labour market information is the EU Labour Force Survey (EU-LFS). This is a quarterly
household sample survey conducted in all Member States of the EU, the United Kingdom, EFTA
and Candidate Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of
employment and unemployment, as well as other survey characteristics follow the denitions and
recommendations of the International Labour Organisation (ILO).
243

## Page 245

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 99
NUTS 2 239
4.4.296 Long-term unemployment in thousands (eu ltu ths)
Long-term unemployment in thousands. Long-term unemployment is dened as being unemployed
for 12 months or longer. Unemployed persons comprise persons aged 15 to 74 who full all the
three following conditions: - are without work during the reference week; - are available to start
work within the next two weeks; - have been actively seeking work in the past four weeks or have
already found a job to start within the next three months. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO).
244

## Page 246

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 99
NUTS 2 239
4.4.297 Unemployment rate for 15-24 years old, female (eu unemp 1524f )
Unemployment rate for women between 15-24 years old. Unemployed persons comprise persons
who full all the three following conditions: - are without work during the reference week; - are
available to start work within the next two weeks; - have been actively seeking work in the past
four weeks or have already found a job to start within the next three months. The source for the
regional labour market information is the EU Labour Force Survey (EU-LFS). This is a quarterly
household sample survey conducted in all Member States of the EU, the United Kingdom, EFTA
and Candidate Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of
employment and unemployment, as well as other survey characteristics follow the denitions and
recommendations of the International Labour Organisation (ILO).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 91
NUTS 2 179
245

## Page 247

4.4.298 Unemployment rate for 15-24 years old, male (eu unemp 1524m)
Unemployment rate for men between 15-24 years old. Unemployed persons comprise persons who
full all the three following conditions: - are without work during the reference week; - are available
to start work within the next two weeks; - have been actively seeking work in the past four weeks or
have already found a job to start within the next three months. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 94
NUTS 2 197
4.4.299 Unemployment rate for 15-24 years old, total (eu unemp 1524t)
Total unemployment rate for 15-24 years old. Unemployed persons comprise persons who full all
the three following conditions: - are without work during the reference week; - are available to
start work within the next two weeks; - have been actively seeking work in the past four weeks or
have already found a job to start within the next three months. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO).
246

## Page 248

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 98
NUTS 2 237
4.4.300 Unemployment rate for 15-74 years old, female (eu unemp 1574f )
Unemployment rate for women between 15-74 years old. Unemployed persons comprise persons
who full all the three following conditions: - are without work during the reference week; - are
available to start work within the next two weeks; - have been actively seeking work in the past
four weeks or have already found a job to start within the next three months. The source for the
regional labour market information is the EU Labour Force Survey (EU-LFS). This is a quarterly
household sample survey conducted in all Member States of the EU, the United Kingdom, EFTA
and Candidate Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of
employment and unemployment, as well as other survey characteristics follow the denitions and
recommendations of the International Labour Organisation (ILO).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 255
247

## Page 249

4.4.301 Unemployment rate for 15-74 years old, male (eu unemp 1574m)
Unemployment rate for men between 15-74 years old. Unemployed persons comprise persons who
full all the three following conditions: - are without work during the reference week; - are available
to start work within the next two weeks; - have been actively seeking work in the past four weeks or
have already found a job to start within the next three months. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 257
4.4.302 Unemployment rate for 15-74 years old, total (eu unemp 1574t)
Total unemployment rate for 15-74 years old. Unemployed persons comprise persons who full all
the three following conditions: - are without work during the reference week; - are available to
start work within the next two weeks; - have been actively seeking work in the past four weeks or
have already found a job to start within the next three months. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO).
248

## Page 250

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 101
NUTS 2 264
4.4.303 Unemployment rate for 20-64 years old, female (eu unemp 2064f )
Unemployment rate for women between 20-64 years old. Unemployed persons comprise persons
who full all the three following conditions: - are without work during the reference week; - are
available to start work within the next two weeks; - have been actively seeking work in the past
four weeks or have already found a job to start within the next three months. The source for the
regional labour market information is the EU Labour Force Survey (EU-LFS). This is a quarterly
household sample survey conducted in all Member States of the EU, the United Kingdom, EFTA
and Candidate Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of
employment and unemployment, as well as other survey characteristics follow the denitions and
recommendations of the International Labour Organisation (ILO).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 252
249

## Page 251

4.4.304 Unemployment rate for 20-64 years old, male (eu unemp 2064m)
Unemployment rate for men between 20-64 years old. Unemployed persons comprise persons who
full all the three following conditions: - are without work during the reference week; - are available
to start work within the next two weeks; - have been actively seeking work in the past four weeks or
have already found a job to start within the next three months. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 255
4.4.305 Unemployment rate for 20-64 years old, total (eu unemp 2064t)
Total unemployment rate for 20-64 years old. Unemployed persons comprise persons who full all
the three following conditions: - are without work during the reference week; - are available to
start work within the next two weeks; - have been actively seeking work in the past four weeks or
have already found a job to start within the next three months. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO).
250

## Page 252

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 101
NUTS 2 263
4.4.306 Unemployment rate for + 15 years, female (eu unemp ge15f )
Unemployment rate for women aged 15 years and over. Unemployed persons comprise persons
who full all the three following conditions: - are without work during the reference week; - are
available to start work within the next two weeks; - have been actively seeking work in the past
four weeks or have already found a job to start within the next three months. The source for the
regional labour market information is the EU Labour Force Survey (EU-LFS). This is a quarterly
household sample survey conducted in all Member States of the EU, the United Kingdom, EFTA
and Candidate Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of
employment and unemployment, as well as other survey characteristics follow the denitions and
recommendations of the International Labour Organisation (ILO).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 255
251

## Page 253

4.4.307 Unemployment rate for +15 years, male (eu unemp ge15m)
Unemployment rate for men aged 15 years and over. Unemployed persons comprise persons who
full all the three following conditions: - are without work during the reference week; - are available
to start work within the next two weeks; - have been actively seeking work in the past four weeks or
have already found a job to start within the next three months. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 257
4.4.308 Unemployment rate for +15 years, total (eu unemp ge15t)
Total unemployment rate for people aged 15 years and over. Unemployed persons comprise persons
who full all the three following conditions: - are without work during the reference week; - are
available to start work within the next two weeks; - have been actively seeking work in the past
four weeks or have already found a job to start within the next three months. The source for the
regional labour market information is the EU Labour Force Survey (EU-LFS). This is a quarterly
household sample survey conducted in all Member States of the EU, the United Kingdom, EFTA
and Candidate Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of
employment and unemployment, as well as other survey characteristics follow the denitions and
recommendations of the International Labour Organisation (ILO).
252

## Page 254

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 101
NUTS 2 264
4.4.309 Unemployment rate for +25 years, female (eu unemp ge25f )
Unemployment rate for women aged 25 years and over. Unemployed persons comprise persons
who full all the three following conditions: - are without work during the reference week; - are
available to start work within the next two weeks; - have been actively seeking work in the past
four weeks or have already found a job to start within the next three months. The source for the
regional labour market information is the EU Labour Force Survey (EU-LFS). This is a quarterly
household sample survey conducted in all Member States of the EU, the United Kingdom, EFTA
and Candidate Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of
employment and unemployment, as well as other survey characteristics follow the denitions and
recommendations of the International Labour Organisation (ILO).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 99
NUTS 2 246
253

## Page 255

4.4.310 Unemployment rate for +25 years, male (eu unemp ge25m)
Unemployment rate for men aged 25 years and over. Unemployed persons comprise persons who
full all the three following conditions: - are without work during the reference week; - are available
to start work within the next two weeks; - have been actively seeking work in the past four weeks or
have already found a job to start within the next three months. The source for the regional labour
market information is the EU Labour Force Survey (EU-LFS). This is a quarterly household sam-
ple survey conducted in all Member States of the EU, the United Kingdom, EFTA and Candidate
Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of employment and
unemployment, as well as other survey characteristics follow the denitions and recommendations
of the International Labour Organisation (ILO).
NUTS Level N
NUTS 0 (Country) 28
NUTS 1 100
NUTS 2 250
4.4.311 Unemployment rate for +25 years, total (eu unemp ge25t)
Total unemployment rate for people aged 25 years and over. Unemployed persons comprise persons
who full all the three following conditions: - are without work during the reference week; - are
available to start work within the next two weeks; - have been actively seeking work in the past
four weeks or have already found a job to start within the next three months. The source for the
regional labour market information is the EU Labour Force Survey (EU-LFS). This is a quarterly
household sample survey conducted in all Member States of the EU, the United Kingdom, EFTA
and Candidate Countries (Montenegro, North Macedonia, Serbia and Turkey). The denitions of
employment and unemployment, as well as other survey characteristics follow the denitions and
recommendations of the International Labour Organisation (ILO).
254

## Page 256

NUTS Level N
NUTS 0 (Country) 28
NUTS 1 101
NUTS 2 261
255

## Page 257

References
[1] Nicholas Charron, Lewis Dijkstra, and Victor Lapuente.Mapping the regional divide in Eu-
rope: A measure for assessing quality of government in 206 European regions. In:Social
Indicators Research, 122(2), 315-346.122.2 (2015), pp. 315–346.doi:10.1007/s11205-014-
0702-y.url:https://doi.org/10.1007/s11205-014-0702-y.
[2] Nicholas Charron, Lewis Dijkstra, and Victor Lapuente.Regional Governance Matters: Qual-
ity of Government within European Union Member States. In:Regional Studies48.1 (2014),
pp. 68–90.doi:10 . 1080 / 00343404 . 2013 . 770141. eprint:https : / / doi . org / 10 . 1080 /
00343404.2013.770141.url:https://doi.org/10.1080/00343404.2013.770141.
[3] Nicholas Charron, Victor Lapuente, and Paola Annoni.Measuring quality of government in
EU regions across space and time. In:Papers in Regional Science98.5 (2019), pp. 1925–1953.
doi:10.1111/pirs.12437. eprint:https://rsaiconnect.onlinelibrary.wiley.com/doi/
pdf/10.1111/pirs.12437.url:https://rsaiconnect.onlinelibrary.wiley.com/doi/
abs/10.1111/pirs.12437.
[4] European Commission.Eurostat. 2020.url:http : / / ec . europa . eu / eurostat / data /
database.
[5] Mihaly Fazekas and Gabor Kocsis.Uncovering High-Level Corruption: Cross-National Objec-
tive Corruption Risk Indicators Using Public Procurement Data. 2017.doi:doi:10 .1017 /
S0007123417000461.
256
