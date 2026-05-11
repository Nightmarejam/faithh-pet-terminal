# codebook_ei_sept21_august2023.pdf

## Page 1

QoG Environmental
Indicators Dataset
2021
The QoG Institute
P.O. Box 711
405 30 Gothenburg, Sweden
infoqog@pol.gu.se
P R E P A R E D B Y

## Page 2

THE QOG ENVIRONMENTAL
INDICATORS DATASET 2021
CODEBOOK
The dataset users are kindly requested to cite both the original source of the variables (as stated
in this codebook) and use the following citation:
Povitkina, Marina, Natalia Alvarado Pachon & Cem Mert Dalli. 2021. The Quality
of Government Environmental Indicators Dataset, version Sep21. University of
Gothenburg: The Quality of Government Institute,
https://www.gu.se/en/quality-government
https://www.gu.se/en/quality-government
The QoG Institute
P.O. Box 711
405 30 Gothenburg
Sweden
infoqog@pol.gu.se

## Page 3

We would like to thank Morgan Young, David Nese, Jan-Georg Knappe, Salima Ismayilzada, Erik
Brinde, Valeria Caras, Mie Sørensen, Felix Backstedt, and Laurisa Dohm for their excellent research
assistance in the preparation of this codebook.
1

## Page 4

Contents
1 Introduction 21
1.1 The Quality of Government Institute . . . . . . . . . . . . . . . . . . . . . . . . . . . 21
1.2 The Environmental Indicators Dataset . . . . . . . . . . . . . . . . . . . . . . . . . . 22
2 Data Structure 24
2.1 Data Structure . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 24
3 Variables by Original Source 26
3.1 Identiﬁcation Variables . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26
3.1.1 cname_qog QoG Country Name . . . . . . . . . . . . . . . . . . . . . . . . . 26
3.1.2 ccode_qog QoG Country code . . . . . . . . . . . . . . . . . . . . . . . . . . 26
3.1.3 year Year . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26
3.1.4 cname_wb Country Name . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26
3.1.5 ccode_wb Country Code . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 26
3.1.6 ccodealp 3-letter Country Code . . . . . . . . . . . . . . . . . . . . . . . . . . 26
3.1.7 ccodealp_year 3-letter Country Code and Year . . . . . . . . . . . . . . . . . 27
3.1.8 ccodecow Country Code COW . . . . . . . . . . . . . . . . . . . . . . . . . . 27
3.1.9 ccodevdem Country Code V-Dem . . . . . . . . . . . . . . . . . . . . . . . . . 27
3.1.10 cname_year Country Name and Year . . . . . . . . . . . . . . . . . . . . . . 27
3.1.11 version Version of the Dataset . . . . . . . . . . . . . . . . . . . . . . . . . . . 27
3.2 Accountable Climate Targets . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 28
3.2.1 Accountable Climate Target (act_act) . . . . . . . . . . . . . . . . . . . . . 28
3.3 Aquastat . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 30
3.3.1 Renewable internal freshwater resources (bln m3) (as_rifr) . . . . . . . . . . 30
2

## Page 5

3.3.2 Water stress: freshwater withdrawal, proportion of available freshwater (as_-
ws) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 31
3.4 Bertelsmann Transformation Index . . . . . . . . . . . . . . . . . . . . . . . . . . . 32
3.4.1 Environmental concerns taken into account (bti_envc) . . . . . . . . . . . . 32
3.5 Climate Change Knowledge Portal . . . . . . . . . . . . . . . . . . . . . . . . . . . 34
3.5.1 Annual average rainfall (cckp_rain) . . . . . . . . . . . . . . . . . . . . . . 34
3.5.2 Annual average temperature (cckp_temp) . . . . . . . . . . . . . . . . . . . 35
3.6 Climate Change Laws of the World . . . . . . . . . . . . . . . . . . . . . . . . . . . 36
3.6.1 Climate change policy/executive provision in place (ccl_exepp) . . . . . . . 36
3.6.2 Climate change law in place (ccl_leglp) . . . . . . . . . . . . . . . . . . . . 37
3.6.3 Climate change law or policy in place (ccl_lpp) . . . . . . . . . . . . . . . . 37
3.6.4 Climate change mitigation law or policy in place (ccl_mitlpp) . . . . . . . . 38
3.6.5 Number of climate change policies/executive provisions (ccl_nexep) . . . . 39
3.6.6 Number of climate change laws (ccl_nlegl) . . . . . . . . . . . . . . . . . . . 39
3.6.7 Number of climate change laws and policies (ccl_nlp) . . . . . . . . . . . . 40
3.6.8 Number of climate change mitigation laws and policies (ccl_nmitlp) . . . . 40
3.7 Cooperation in International Climate Change Regime . . . . . . . . . . . . . . . . . 42
3.7.1 Cooperation in International Climate Change Regime Index (ccci_coop) . . 42
3.7.2 Emission Indicator (ccci_em) . . . . . . . . . . . . . . . . . . . . . . . . . . 43
3.7.3 Finance Indicator (ccci_ﬁn) . . . . . . . . . . . . . . . . . . . . . . . . . . . 43
3.7.4 Kyoto Protocol Indicator (ccci_kyoto) . . . . . . . . . . . . . . . . . . . . . 44
3.7.5 Reporting Indicator (ccci_rep) . . . . . . . . . . . . . . . . . . . . . . . . . 44
3.7.6 UNFCCC Indicator (ccci_unfccc) . . . . . . . . . . . . . . . . . . . . . . . . 45
3.8 EDGAR - Fossil CO2 Emissions of All World Countries . . . . . . . . . . . . . . . 46
3.8.1 CO2 emissions per GDP (edgar_co2gdp) . . . . . . . . . . . . . . . . . . . 46
3.8.2 CO2 emissions per capita (edgar_co2pc) . . . . . . . . . . . . . . . . . . . . 47
3

## Page 6

3.8.3 CO2 emissions total (edgar_co2t) . . . . . . . . . . . . . . . . . . . . . . . . 47
3.9 EDGAR - Global Air Pollutant Emissions . . . . . . . . . . . . . . . . . . . . . . . 49
3.9.1 BC emissions (edgar_bc) . . . . . . . . . . . . . . . . . . . . . . . . . . . . 50
3.9.2 CH4 emissions (edgar_ch4) . . . . . . . . . . . . . . . . . . . . . . . . . . . 50
3.9.3 CO emissions (edgar_co) . . . . . . . . . . . . . . . . . . . . . . . . . . . . 51
3.9.4 N2O emissions (edgar_n2o) . . . . . . . . . . . . . . . . . . . . . . . . . . . 51
3.9.5 NH3 emissions (edgar_nh3) . . . . . . . . . . . . . . . . . . . . . . . . . . . 52
3.9.6 NMVOC emissions (edgar_nmvoc) . . . . . . . . . . . . . . . . . . . . . . . 52
3.9.7 NOx emissions (edgar_nox) . . . . . . . . . . . . . . . . . . . . . . . . . . . 53
3.9.8 OC emissions (edgar_oc) . . . . . . . . . . . . . . . . . . . . . . . . . . . . 53
3.9.9 PM10 emissions (edgar_pm10) . . . . . . . . . . . . . . . . . . . . . . . . . 54
3.9.10 PM2.5 emissions (edgar_pm25) . . . . . . . . . . . . . . . . . . . . . . . . . 54
3.9.11 SO2 emissions (edgar_so2) . . . . . . . . . . . . . . . . . . . . . . . . . . . 55
3.10 ENVIPOLCON . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 56
3.10.1 Policy instruments for quality of bathing water (epc_bath) . . . . . . . . . 56
3.10.2 Policy instruments for exhaust emissions from cars (epc_car) . . . . . . . . 57
3.10.3 Policy instruments for reduction of CO2 emissions from heavy industry
(epc_co2) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 58
3.10.4 Policy instruments for hazardous substances in detergents (epc_dete) . . . 59
3.10.5 Policy instruments for energy eﬃciency of refrigerators (epc_enef) . . . . . 60
3.10.6 Policy instruments for electricity from renewable sources (epc_ener) . . . . 61
3.10.7 Policy instruments for forest protection policy (epc_fors) . . . . . . . . . . 62
3.10.8 Policy instruments for lead emissions from vehicles (epc_lead) . . . . . . . 63
3.10.9 Policy instruments for noise emissions from lorries (epc_nois) . . . . . . . . 64
3.10.10 Policy instruments to promote reﬁllable beverage containers (epc_pawa) . . 65
3.10.11 Policy instruments for contaminated sites (epc_soil) . . . . . . . . . . . . . 66
4

## Page 7

3.10.12 Policy instruments for water protection related to industrial discharges (epc_-
watp) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 67
3.11 ENVIPOLCONCHANGE . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 69
3.11.1 Change in eco audit policy (epcc_audi_ch2) . . . . . . . . . . . . . . . . . 69
3.11.2 Eco audit policy introduction (epcc_audi_in2) . . . . . . . . . . . . . . . . 70
3.11.3 Change in coliforms in bathing water policy (epcc_bath_ch2) . . . . . . . . 70
3.11.4 Coliforms in bathing water policy introduction (epcc_bath_in2) . . . . . . 71
3.11.5 Passenger car emissions CO regulatory level (epcc_car_co) . . . . . . . . . 71
3.11.6 Passenger car emissions HC regulatory level (epcc_car_hc) . . . . . . . . . 72
3.11.7 Passenger car emissions NOx regulatory level (epcc_car_nox) . . . . . . . . 72
3.11.8 Change in passenger car emissions policy (epcc_care_ch2) . . . . . . . . . . 73
3.11.9 Passenger car emissions policy introduction (epcc_care_in2) . . . . . . . . 73
3.11.10 Sum of downward changes in all 17 standards (epcc_cd_dwsum) . . . . . . 74
3.11.11 Sum of upward changes in all 17 standards (epcc_cd_upsum) . . . . . . . . 74
3.11.12 Sum of all changes in policy (epcc_ch2) . . . . . . . . . . . . . . . . . . . . 75
3.11.13 Cumulative sum of all policy-in-place items (epcc_ch_kum) . . . . . . . . . 75
3.11.14 Change in contaminated sites policy (epcc_cont_ch2) . . . . . . . . . . . . 76
3.11.15 Contaminated sites policy introduction (epcc_cont_in2) . . . . . . . . . . . 76
3.11.16 Change in recycling of construction waste policy (epcc_cowa_ch2) . . . . . 77
3.11.17 Recycling of construction waste policy introduction (epcc_cowa_in2) . . . 77
3.11.18 Change in detergents regulation policy (epcc_dete_ch2) . . . . . . . . . . . 78
3.11.19 Detergents regulation policy introduction (epcc_dete_in2) . . . . . . . . . 78
3.11.20 Change in ecolabel policy (epcc_ecol_ch2) . . . . . . . . . . . . . . . . . . 79
3.11.21 Ecolabel policy introduction (epcc_ecol_in2) . . . . . . . . . . . . . . . . . 79
3.11.22 Change in environmental impact assessment (epcc_eias_ch2) . . . . . . . . 80
3.11.23 Environmental impact assessment introduction (epcc_eias_in2) . . . . . . . 80
5

## Page 8

3.11.24 Change in energy eﬃciency of refrigerators policy (epcc_enef_ch2) . . . . . 81
3.11.25 Energy eﬃciency of refrigerators policy introduction (epcc_enef_in2) . . . 81
3.11.26 Glass recycling target in regulations, % (epcc_glas2_s) . . . . . . . . . . . 82
3.11.27 Change in glass recycling target in regulation (epcc_glas_ch2) . . . . . . . 82
3.11.28 Glass recycling target in regulation introduction (epcc_glas_in2) . . . . . . 83
3.11.29 Sum ofﬁrst policy introductions (epcc_intro_kum) . . . . . . . . . . . . . 83
3.11.30 Change in landﬁll target in regulations (epcc_land_ch2) . . . . . . . . . . . 84
3.11.31 Landﬁll target in regulations introduction (epcc_lanr_in2) . . . . . . . . . 84
3.11.32 Large combustion plants regulatory level DUST (epcc_lcp_dust) . . . . . . 85
3.11.33 Large combustion plants regulatory level NOX (epcc_lcp_nox) . . . . . . . 85
3.11.34 Large combustion plants regulatory level SO2 (epcc_lcp_so2) . . . . . . . . 86
3.11.35 Change in large combustion plants policy (epcc_lcpt_ch2) . . . . . . . . . 86
3.11.36 Large combustion plants policy introduction (epcc_lcpt_in2) . . . . . . . . 87
3.11.37 Change lead content in petrol policy (epcc_lead_ch2) . . . . . . . . . . . . 87
3.11.38 Lead content in petrol policy introduction (epcc_lead_in2) . . . . . . . . . 88
3.11.39 Lead content in petrol regulatory level (epcc_lead_s) . . . . . . . . . . . . 88
3.11.40 Change in motorway noise emissions policy (epcc_moto_ch2) . . . . . . . . 89
3.11.41 Motorway noise emissions policy introduction (epcc_moto_in2) . . . . . . . 89
3.11.42 Motorway noise emissions regulatory level (epcc_moto_s) . . . . . . . . . . 90
3.11.43 Change in noise emissions from lorries policy (epcc_nois_ch2) . . . . . . . 90
3.11.44 Noise emissions from lorries policy introduction (epcc_nois_in2) . . . . . . 91
3.11.45 Noise emissions from lorries regulatory level (epcc_nois_s) . . . . . . . . . 91
3.11.46 Change in packaging waste recycling target (epcc_pact_ch2) . . . . . . . . 92
3.11.47 Packaging waste recycling target introduction (epcc_pact_in2) . . . . . . . 92
3.11.48 Paper recycling target in regulations, % (epcc_pape2_s) . . . . . . . . . . . 93
6

## Page 9

3.11.49 Change in paper recycling target in regulation (epcc_pape_ch2) . . . . . . 93
3.11.50 Paper recycling target in regulation introduction (epcc_pape_in2) . . . . . 94
3.11.51 Change in soil policy (epcc_soil_ch2) . . . . . . . . . . . . . . . . . . . . . 94
3.11.52 Soil policy introduction (epcc_soil_in2) . . . . . . . . . . . . . . . . . . . . 95
3.11.53 Change in sulphur content gas oil policy (epcc_sulp_ch2) . . . . . . . . . . 95
3.11.54 Sulphur content gas oil policy introduction (epcc_sulp_in2) . . . . . . . . . 96
3.11.55 Sulphur content in gas oil regulatory level (epcc_sulp_s) . . . . . . . . . . 96
3.11.56 Change in National environmental policy/Sustainable development plan (epcc_-
susp_ch2) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 97
3.11.57 National environmental policy/Sustainable development plan introduction
(epcc_susp_in2) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 97
3.11.58 Water protection - BOD in industrial discharges (epcc_wabo_s) . . . . . . 98
3.11.59 Water protection - Copper in industrial discharges (epcc_waco_s) . . . . . 98
3.11.60 Water protection - Chromium in industrial discharges (epcc_wacr_s) . . . 99
3.11.61 Change in eﬃcient use of water in industry policy (epcc_waef_ch2) . . . . 99
3.11.62 Eﬃcient use of water in industry policy introduction (epcc_waef_in2) . . . 100
3.11.63 Water protection - Lead in industrial discharges (epcc_wale_s) . . . . . . . 100
3.11.64 Change in water protection policy - industrial discharges (epcc_wapr_ch2) 101
3.11.65 Water protection - industrial discharges introduction (epcc_wapr_in2) . . . 101
3.11.66 Water protection - Zinc in industrial discharges (epcc_wazi_s) . . . . . . . 102
3.12 Emergency Events Database . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 103
3.12.1 Total damage from natural disasters in USD (emdat_damage) . . . . . . . 104
3.12.2 Number of people aﬀected by natural disasters (emdat_naﬀect) . . . . . . . 104
3.12.3 Number of people killed by natural disasters (emdat_ndeath) . . . . . . . . 105
3.12.4 Number of natural disasters (emdat_ndis) . . . . . . . . . . . . . . . . . . . 105
3.12.5 Number of homeless people after natural disaster (emdat_nhome) . . . . . 106
7

## Page 10

3.12.6 Number of people injured in natural disasters (emdat_ninj) . . . . . . . . . 106
3.12.7 Number of aﬀected (total) by natural disasters (emdat_ntotaﬀ) . . . . . . . 106
3.13 Environmental Land Use Data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 108
3.13.1 Agricultural land (% of Land area) (fao_luagr) . . . . . . . . . . . . . . . . 108
3.13.2 Arable land (% of Agricultural land) (fao_luagrara) . . . . . . . . . . . . . 109
3.13.3 Cropland (% of Agricultural land) (fao_luagrcrop) . . . . . . . . . . . . . . 109
3.13.4 Agriculture area actually irrigated (% of Agricultural land) (fao_luagrirrac) 109
3.13.5 Land area equipped for irrigation (% of Agricultural land) (fao_luagrirreq) 110
3.13.6 Land area equipped for irrigation (% of Cropland) (fao_luagrirreqcrop) . . 110
3.13.7 Agriculture area under organic agric. (% of Agricultural land) (fao_luagrorg) 111
3.13.8 Land under perm meadows and pastures (% of Agricultural land) (fao_-
luagrpas) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 111
3.13.9 Land under permanent crops (% of Agricultural land) (fao_luagrpcrop) . . 112
3.13.10 Cropland (% of Land area) (fao_lucrop) . . . . . . . . . . . . . . . . . . . . 112
3.13.11 Forest land (% of Land area) (fao_luforest) . . . . . . . . . . . . . . . . . . 113
3.13.12 Planted forest (% of Forest area) (fao_luforplant) . . . . . . . . . . . . . . . 113
3.13.13 Other naturally regenerated forest (% of Forest area) (fao_luforreg) . . . . 114
3.13.14 Land under perm meadows and pastures (% of Land area) (fao_lupas) . . . 114
3.14 Environmental Ministries . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 116
3.14.1 Environmental ministry establishment (em_envmin) . . . . . . . . . . . . . 116
3.15 Environmental Non-Governmental Organizations . . . . . . . . . . . . . . . . . . . 118
3.15.1 Number of national ENGOs (engo_nengo) . . . . . . . . . . . . . . . . . . . 118
3.16 Environmental Performance Index Data 2020 . . . . . . . . . . . . . . . . . . . . . 120
3.16.1 Agriculture Issue Category (epi_agr) . . . . . . . . . . . . . . . . . . . . . . 120
3.16.2 Air Quality Issue Category (epi_air) . . . . . . . . . . . . . . . . . . . . . . 121
3.16.3 Pollution Emissions Issue Category (epi_ape) . . . . . . . . . . . . . . . . . 122
8

## Page 11

3.16.4 Black carbon growth rate (epi_bca) . . . . . . . . . . . . . . . . . . . . . . 123
3.16.5 Biodiversity and Habitat Issue Category (epi_bdh) . . . . . . . . . . . . . . 123
3.16.6 Biodiversity habitat index (epi_bhv) . . . . . . . . . . . . . . . . . . . . . . 125
3.16.7 Climate Change Issue Category (epi_cch) . . . . . . . . . . . . . . . . . . . 125
3.16.8 CO2 growth rate (epi_cda) . . . . . . . . . . . . . . . . . . . . . . . . . . . 127
3.16.9 CH4 growth rate (epi_cha) . . . . . . . . . . . . . . . . . . . . . . . . . . . 128
3.16.10 Ecosystem Services Issue Category (epi_ecs) . . . . . . . . . . . . . . . . . 128
3.16.11 Environmental Health Policy Objective (epi_eh) . . . . . . . . . . . . . . . 129
3.16.12 Environmental Performance Index (epi_epi) . . . . . . . . . . . . . . . . . . 129
3.16.13 Ecosystem Vitality Policy Objective (epi_ev) . . . . . . . . . . . . . . . . . 130
3.16.14 Fish caught by trawling (epi_fct) . . . . . . . . . . . . . . . . . . . . . . . . 131
3.16.15 F-gas growth rate (epi_fga) . . . . . . . . . . . . . . . . . . . . . . . . . . . 132
3.16.16 Fisheries Issue Category (epi_fsh) . . . . . . . . . . . . . . . . . . . . . . . 132
3.16.17 Fish stock status (epi_fss) . . . . . . . . . . . . . . . . . . . . . . . . . . . . 133
3.16.18 GHG emissions per capita (epi_ghp) . . . . . . . . . . . . . . . . . . . . . . 134
3.16.19 GHG intensity trend (epi_gib) . . . . . . . . . . . . . . . . . . . . . . . . . 134
3.16.20 Grassland loss (epi_grl) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 135
3.16.21 Sanitation and Drinking Water Issue Category (epi_h2o) . . . . . . . . . . 135
3.16.22 Household solid fuels (epi_had) . . . . . . . . . . . . . . . . . . . . . . . . . 136
3.16.23 Heavy Metals Issue Category (epi_hmt) . . . . . . . . . . . . . . . . . . . . 137
3.16.24 CO2 from land cover (epi_lcb) . . . . . . . . . . . . . . . . . . . . . . . . . 137
3.16.25 Marine protected areas (epi_mpa) . . . . . . . . . . . . . . . . . . . . . . . 138
3.16.26 Controlled solid waste (epi_msw) . . . . . . . . . . . . . . . . . . . . . . . . 139
3.16.27 Marine trophic index (epi_mti) . . . . . . . . . . . . . . . . . . . . . . . . . 139
3.16.28 N2O growth rate (epi_noa) . . . . . . . . . . . . . . . . . . . . . . . . . . . 140
9

## Page 12

3.16.29 NOx growth rate (epi_nxa) . . . . . . . . . . . . . . . . . . . . . . . . . . . 141
3.16.30 Ozone exposure (epi_ozd) . . . . . . . . . . . . . . . . . . . . . . . . . . . . 141
3.16.31 Protected areas representativeness index (epi_par) . . . . . . . . . . . . . . 142
3.16.32 Lead exposure (epi_pbd) . . . . . . . . . . . . . . . . . . . . . . . . . . . . 143
3.16.33 PM2.5 exposure (epi_pmd) . . . . . . . . . . . . . . . . . . . . . . . . . . . 143
3.16.34 SO2 growth rate (epi_sda) . . . . . . . . . . . . . . . . . . . . . . . . . . . 144
3.16.35 Species habitat index (epi_shi) . . . . . . . . . . . . . . . . . . . . . . . . . 144
3.16.36 Sustainable nitrogen management index (epi_snm) . . . . . . . . . . . . . . 145
3.16.37 Species protection index (epi_spi) . . . . . . . . . . . . . . . . . . . . . . . 146
3.16.38 Terrestrial biome protection (Global weights) (epi_tbg) . . . . . . . . . . . 147
3.16.39 Terrestrial biome protection (National weights) (epi_tbn) . . . . . . . . . . 147
3.16.40 Tree cover loss (epi_tcl) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 148
3.16.41 Unsafe sanitation (epi_usd) . . . . . . . . . . . . . . . . . . . . . . . . . . . 148
3.16.42 Unsafe drinking water (epi_uwd) . . . . . . . . . . . . . . . . . . . . . . . . 149
3.16.43 Waste Management Issue Category (epi_wmg) . . . . . . . . . . . . . . . . 150
3.16.44 Water Resources Issue Category (epi_wrs) . . . . . . . . . . . . . . . . . . . 150
3.16.45 Wetland loss (epi_wtl) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 151
3.16.46 Wastewater treatment (epi_wwt) . . . . . . . . . . . . . . . . . . . . . . . . 151
3.17 Environmental Policy Stringency Index . . . . . . . . . . . . . . . . . . . . . . . . . 153
3.17.1 Environmental Policy Stringency Index (oecd_eps) . . . . . . . . . . . . . . 153
3.18 Environmental Protection Expenditure Accounts (EPEA) . . . . . . . . . . . . . . 155
3.18.1 Environmnnetal Protection Expenditure Accounts (EPEA) (oecd_epea) . . 155
3.19 Environmentally Adjusted Multifactor Productivity . . . . . . . . . . . . . . . . . . 157
3.19.1 Environmentally adjusted multifactor productivity growth (oecd_eampg) . 157
3.19.2 Pollution-adjusted GDP growth (oecd_polagdpg) . . . . . . . . . . . . . . . 158
10

## Page 13

3.20 European Social Survey - Wave 1-9 . . . . . . . . . . . . . . . . . . . . . . . . . . . 159
3.20.1 Climate policy support: bans (mean) (ess_banhhap_m) . . . . . . . . . . . 159
3.20.2 Belief that climate change is natural (%) (ess_ccnthum_p) . . . . . . . . . 160
3.20.3 Personal responsibility to reduce climate change (mean) (ess_ccrdprs_m) . 161
3.20.4 Climate change denial (%) (ess_clmchng_p) . . . . . . . . . . . . . . . . . 161
3.20.5 Thinking about climate change (mean) (ess_clmthgt_m) . . . . . . . . . . 162
3.20.6 Belief in climate action: governments (mean) (ess_gvsrdcc_m) . . . . . . . 163
3.20.7 Important to care for the environment (mean) (ess_impenv_m) . . . . . . 163
3.20.8 Climate policy support: taxes (mean) (ess_inctxﬀ_m) . . . . . . . . . . . . 164
3.20.9 Belief in climate action: individuals (mean) (ess_lklmten_m) . . . . . . . . 164
3.20.10 Climate policy support: subsidies (mean) (ess_sbsrnen_m) . . . . . . . . . 165
3.20.11 Worry about climate change (mean) (ess_wrclmch_m) . . . . . . . . . . . . 166
3.21 Exposure to PM2.5 in Countries and Regions . . . . . . . . . . . . . . . . . . . . . 167
3.21.1 Percentage of population exposed to more than 15µg/m3 of PM2.5 (oecd_-
pm25ex15p) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 168
3.21.2 Percentage of population exposed to more than 25µg/m3 of PM2.5 (oecd_-
pm25ex25p) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 168
3.22 Global Footprint Data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 170
3.22.1 Total Biocapacity (gha per capita) (ef_bcpc) . . . . . . . . . . . . . . . . . 170
3.22.2 Total Biocapacity (total gha) (ef_bct) . . . . . . . . . . . . . . . . . . . . . 171
3.22.3 Built-up land footprint of consumption (gha per person) (ef_bul) . . . . . . 171
3.22.4 Built-up land biocapacity per capita (ef_bul_bc) . . . . . . . . . . . . . . . 172
3.22.5 Built-up land footprint of production (gha per person) (ef_bulp) . . . . . . 172
3.22.6 Carbon footprint of consumption (gha per person) (ef_carb) . . . . . . . . 173
3.22.7 Carbon biocapacity per capita (ef_carb_bc) . . . . . . . . . . . . . . . . . 173
3.22.8 Carbon footprint of production (gha per person) (ef_carbp) . . . . . . . . . 174
11

## Page 14

3.22.9 Cropland footprint of consumption (gha per person) (ef_crop) . . . . . . . 174
3.22.10 Cropland biocapacity per capita (ef_crop_bc) . . . . . . . . . . . . . . . . 175
3.22.11 Cropland footprint of production (gha per person) (ef_cropp) . . . . . . . . 175
3.22.12 Total Ecological Footprint of Consumption (gha per person) (ef_ef) . . . . 176
3.22.13 Total Ecological Footprint of Production (gha per person) (ef_efp) . . . . . 176
3.22.14 Total Ecological Footprint of Consumption (total area) (ef_eft) . . . . . . . 177
3.22.15 Total Ecological Footprint of Production (total area) (ef_eftp) . . . . . . . 177
3.22.16 Fish footprint of consumption (gha per person) (ef_fg) . . . . . . . . . . . . 178
3.22.17 Fishing ground biocapacity per capita (ef_fg_bc) . . . . . . . . . . . . . . . 178
3.22.18 Fish footprint of production (gha per person) (ef_fgp) . . . . . . . . . . . . 179
3.22.19 Forest product footprint of consumption (gha per person) (ef_for) . . . . . 179
3.22.20 Forest land biocapacity per capita (ef_for_bc) . . . . . . . . . . . . . . . . 180
3.22.21 Forest product footprint of production (gha per person) (ef_forp) . . . . . . 180
3.22.22 Grazing footprint of consumption (gha per person) (ef_gl) . . . . . . . . . . 181
3.22.23 Grazing land biocapacity per capita (ef_gl_bc) . . . . . . . . . . . . . . . . 181
3.22.24 Grazing footprint of production (gha per person) (ef_glp) . . . . . . . . . . 182
3.23 Green Growth . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 183
3.23.1 Population connected to public sewerage, % total population (gg_asew_pop) 183
3.23.2 Population connected to sewerage with primary treatment, % total popula-
tion (gg_asewp) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 184
3.23.3 Population connected to sewerage with secondary treatment, % total popu-
lation (gg_asews) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 184
3.23.4 Population connected to sewerage with tertiary treatment, % total popula-
tion (gg_asewt) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 185
3.23.5 Built up area per capita (gg_buapc) . . . . . . . . . . . . . . . . . . . . . . 185
3.23.6 Built up area, % total land (gg_buapt) . . . . . . . . . . . . . . . . . . . . 186
3.23.7 Energy intensity, TPES per capita (gg_ei) . . . . . . . . . . . . . . . . . . . 186
12

## Page 15

3.23.8 Environmentally related government R&D budget, % total government R&D
(gg_envrd_gbaord) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 187
3.23.9 Environmentally related R&D expenditure, % GDP (gg_envrd_gdp) . . . . 187
3.23.10 Environmentally related ODA, % total ODA (gg_eoda) . . . . . . . . . . . 188
3.23.11 Energy public RD&D budget, % GDP (gg_erdgdp) . . . . . . . . . . . . . 188
3.23.12 Development of environment-related technologies, % all technologies (gg_-
etp) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 189
3.23.13 Development of environment-related technologies, % inventions worldwide
(gg_etpw) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 190
3.23.14 Fossil fuel public RD&D budget (excluding CCS), % total energy public
RD&D (gg_ﬀrd) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 190
3.23.15 Forest resource stocks (gg_frs) . . . . . . . . . . . . . . . . . . . . . . . . . 191
3.23.16 Forests under sustainable management certiﬁcation FSC, % total forest area
(gg_fsmc) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 191
3.23.17 Intensity of use of forest resources (gg_iufr) . . . . . . . . . . . . . . . . . . 192
3.23.18 Mortality from exposure to ambient ozone (gg_mao) . . . . . . . . . . . . . 192
3.23.19 Mortality from exposure to lead (gg_ml) . . . . . . . . . . . . . . . . . . . . 193
3.23.20 Mortality from exposure to ambient PM2.5 (gg_mpm) . . . . . . . . . . . . 193
3.23.21 Mortality from exposure to residential radon (gg_mr) . . . . . . . . . . . . 194
3.23.22 Municipal waste generated, kg per capita (gg_mwgpc) . . . . . . . . . . . . 194
3.23.23 Municipal waste incinerated, % treated waste (gg_mwipt) . . . . . . . . . . 195
3.23.24 Municipal waste disposed to landﬁlls, % treated waste (gg_mwlpt) . . . . . 195
3.23.25 Municipal waste recycled or composted, % treated waste (gg_mwrpt) . . . 196
3.23.26 ODA - all sectors - climate change mitigation, % total ODA (gg_oda_ccm) 196
3.23.27 Percentage of population exposed to more than 10µg/m3 of PM2.5 (gg_-
pm25ex10p) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 197
3.23.28 Percentage of population exposed to more than 35µg/m3 of PM2.5 (gg_-
pm25ex35p) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 198
3.23.29 Mean population exposure to PM2.5 (gg_pm25exm) . . . . . . . . . . . . . 198
13

## Page 16

3.23.30 Petrol tax, USD per litre (gg_pt) . . . . . . . . . . . . . . . . . . . . . . . . 199
3.23.31 Renewable energy supply, % TPES (gg_re_tpes) . . . . . . . . . . . . . . . 199
3.23.32 Renewable electricity, % total electricity generation (gg_reperegen) . . . . . 200
3.23.33 Renewable energy public RD&D budget, % total energy public RD&D (gg_-
rerd_erd) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 200
3.23.34 Threatened bird species, % total known species (gg_tbs) . . . . . . . . . . . 201
3.23.35 Threatened mammal species, % total known species (gg_tms) . . . . . . . . 201
3.23.36 Threatened vascular plant species, % total known species (gg_tps) . . . . . 202
3.23.37 Water stress, total freshwater abstraction as % total available renewable
resources (gg_wsa) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 202
3.23.38 Water stress, total freshwater abstraction as % total internal renewable re-
sources (gg_wsi) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 203
3.24 International Environmental Agreements Database Project . . . . . . . . . . . . . . 204
3.24.1 Number of IEAs entered into force for theﬁrst time (iead_eif1) . . . . . . . 205
3.24.2 Number of IEAs entered into force for the second time (iead_eif2) . . . . . 205
3.24.3 Number of IEAs entered into force for the third time (iead_eif3) . . . . . . 206
3.24.4 Number of IEAs in force, counting terminated IEAs (iead_inforce) . . . . . 206
3.24.5 Number of IEAs in force, not counting terminated IEAs (iead_inforce_-
noterm) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 207
3.24.6 Number of IEAs ratiﬁed per year (iead_rat) . . . . . . . . . . . . . . . . . . 207
3.24.7 Number of IEAs signed per year (iead_sig) . . . . . . . . . . . . . . . . . . 208
3.24.8 Number of terminated IEAs per year (iead_term) . . . . . . . . . . . . . . 208
3.24.9 Number ofﬁrst withdrawals from IEAs per year (iead_withdraw1) . . . . . 209
3.24.10 Number of second withdrawals from IEAs per year (iead_withdraw2) . . . 209
3.25 Natural Resource Management Index Data . . . . . . . . . . . . . . . . . . . . . . . 210
3.25.1 Natural Resource Protection Indicator (nrmi_nrpi) . . . . . . . . . . . . . . 210
3.26 Oil and Gas Data, 1932-2014 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 212
14

## Page 17

3.26.1 Gas exports, billion cubic feet per year (ross_gas_exp) . . . . . . . . . . . 212
3.26.2 Net gas exports value, constant 2000 dollars (ross_gas_netexp) . . . . . . . 213
3.26.3 Gas production, million barrels oil equiv. (ross_gas_prod) . . . . . . . . . 213
3.26.4 Gas production value in 2014 dollars (ross_gas_value_2014) . . . . . . . . 214
3.26.5 Oil exports, thousands of barrels per day (ross_oil_exp) . . . . . . . . . . . 214
3.26.6 Net oil exports value, constant 2000 dollars (ross_oil_netexp) . . . . . . . . 215
3.26.7 Oil production in metric tons (ross_oil_prod) . . . . . . . . . . . . . . . . . 215
3.26.8 Oil production value in 2014 dollars (ross_oil_value_2014) . . . . . . . . . 216
3.27 Policy Instruments for the Environment . . . . . . . . . . . . . . . . . . . . . . . . 217
3.27.1 Climate change related tax revenue (% of GDP) (oecd_cctr_gdp) . . . . . 217
3.27.2 Climate change related tax revenue (% of total tax revenue) (oecd_cctr_tot) 218
3.27.3 Environmentally related tax revenue (% of GDP) (oecd_etr_gdp) . . . . . 218
3.27.4 Environmentally related tax revenue (% total tax revenue) (oecd_etr_tot) 219
3.28 Stock of Climate Laws and Policies . . . . . . . . . . . . . . . . . . . . . . . . . . . 221
3.28.1 Stock of executive orders/policies on mitigation for the past 3 years (slaws_-
mit_ex_l3) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 221
3.28.2 Stock of older executive orders/policies on mitigation (slaws_mit_ex_lt) . 222
3.28.3 Stock of mitigation laws and policies for the past 3 years (slaws_mit_l3) . 222
3.28.4 Stock of legislative mitigation laws for the past 3 years (slaws_mit_leg_l3) 223
3.28.5 Stock of older legislative mitigation laws (slaws_mit_leg_lt) . . . . . . . . 223
3.28.6 Stock of older mitigation laws and policies (slaws_mit_lt) . . . . . . . . . . 224
3.29 Sustainable Governance Indicators . . . . . . . . . . . . . . . . . . . . . . . . . . . 225
3.29.1 Environmental Policy Performance Index (sgi_en) . . . . . . . . . . . . . . 225
3.29.2 Environmental Policy Performance - Environment (sgi_enen) . . . . . . . . 226
3.29.3 Environmental Policy Performance - Global Environmental Protection (sgi_-
enge) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 226
15

## Page 18

3.29.4 Environmental policy eﬀectiveness (sgi_epe) . . . . . . . . . . . . . . . . . . 227
3.29.5 Participation in global environmental regimes (sgi_ger) . . . . . . . . . . . 228
3.30 The Environmental Democracy Index . . . . . . . . . . . . . . . . . . . . . . . . . . 230
3.30.1 Environmental Democracy Index (edi_edi) . . . . . . . . . . . . . . . . . . 230
3.30.2 Aﬀordable access to relief and remedy (Guideline 20) (edi_gaarr) . . . . . . 231
3.30.3 Alternative dispute resolution for environmental issues (Guideline 26) (edi_-
gadrei) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 232
3.30.4 Awareness and education about remedies and relief (Guideline 23) (edi_-
gaerr) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 233
3.30.5 Accessibility of information requests (Guideline 1) (edi_gair) . . . . . . . . 234
3.30.6 Due account of public comments (Guideline 11) (edi_gapc) . . . . . . . . . 234
3.30.7 Broad standing (Guideline 18) (edi_gbs) . . . . . . . . . . . . . . . . . . . . 235
3.30.8 Eﬀective enforcement (Guideline 22) (edi_gee) . . . . . . . . . . . . . . . . 236
3.30.9 Environmental information in the public domain (Guideline 2) (edi_gepd) . 236
3.30.10 Early public participation (Guideline 8) (edi_gepp) . . . . . . . . . . . . . . 237
3.30.11 Early warning information (Guideline 6) (edi_gewi) . . . . . . . . . . . . . 238
3.30.12 Fair, timely, and independent review (Guideline 19) (edi_gftir) . . . . . . . 239
3.30.13 Grounds for refusal (Guideline 3) (edi_ggr) . . . . . . . . . . . . . . . . . . 239
3.30.14 Information collection and management (Guideline 4) (edi_gicm) . . . . . . 240
3.30.15 Informed participation (Guideline 10) (edi_gip) . . . . . . . . . . . . . . . . 241
3.30.16 Integrating public input for rule-making (Guideline 13) (edi_gipirm) . . . . 242
3.30.17 Information request appeals (Guideline 15) (edi_gira) . . . . . . . . . . . . 243
3.30.18 Public access to judicial and administrative decisions (Guideline 24) (edi_-
gpajad) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 244
3.30.19 Prompt, eﬀective remedies (Guideline 21) (edi_gper) . . . . . . . . . . . . . 245
3.30.20 Public participation appeals (Guideline 16) (edi_gppa) . . . . . . . . . . . . 245
3.30.21 Proactive public consultation (Guideline 9) (edi_gppc) . . . . . . . . . . . . 246
16

## Page 19

3.30.22 Public participation review (Guideline 12) (edi_gppr) . . . . . . . . . . . . 247
3.30.23 Right of public to challenge state or private actors (Guideline 17) (edi_-
grpcspa) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 248
3.30.24 State of the environment report (Guideline 5) (edi_gser) . . . . . . . . . . . 248
3.30.25 Justice Pillar Score (edi_jp) . . . . . . . . . . . . . . . . . . . . . . . . . . . 249
3.30.26 Access to Information Pillar Score (edi_pati) . . . . . . . . . . . . . . . . . 250
3.30.27 Participation Pillar Score (edi_pp) . . . . . . . . . . . . . . . . . . . . . . . 250
3.31 The International Social Survey Programme. Environment Module . . . . . . . . . 252
3.31.1 Worry about environment vs jobs (mean) (issp_10am) . . . . . . . . . . . . 252
3.31.2 Unwillingness to pay higher prices (%) (issp_12ap) . . . . . . . . . . . . . . 253
3.31.3 Unwillingness to pay higher taxes (%) (issp_12bp) . . . . . . . . . . . . . . 254
3.31.4 Unwillingness to cut in standard of living (%) (issp_12cp) . . . . . . . . . . 255
3.31.5 Individual action is insuﬃcient (mean) (issp_13am) . . . . . . . . . . . . . 255
3.31.6 Environmental behavior (mean) (issp_13bm) . . . . . . . . . . . . . . . . . 256
3.31.7 Claims about environmental threats are exaggerated (mean) (issp_13em) . 257
3.31.8 Perceived vulnerability to environmental problems (mean) (issp_13gm) . . 258
3.31.9 Support for government action to make people comply (%) (issp_15ap) . . 258
3.31.10 Priority of future energy sources - fossil fuels (%) (issp_18p) . . . . . . . . 259
3.31.11 Attitudes on international environmental agreements (mean) (issp_19am) . 260
3.31.12 Attitudes towards global environmental justice (mean) (issp_19bm) . . . . 260
3.31.13 Environment is most or next most important issue (%) (issp_1ap) . . . . . 261
3.31.14 Reported extent of recycling (mean) (issp_20am) . . . . . . . . . . . . . . . 262
3.31.15 Recycling not available (%) (issp_20ap) . . . . . . . . . . . . . . . . . . . . 263
3.31.16 Reducing energy use for the environment (mean) (issp_20dm) . . . . . . . . 263
3.31.17 Membership in environmental groups (%) (issp_21p) . . . . . . . . . . . . . 264
3.31.18 Signed petitions about environmental issues (%) (issp_22ap) . . . . . . . . 265
17

## Page 20

3.31.19 Given money to an environmental group (%) (issp_22bp) . . . . . . . . . . 265
3.31.20 Taken part in a protest/demonstration about environmental issues (%) (issp_-
22cp) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 266
3.31.21 Environmental concern (mean) (issp_6m) . . . . . . . . . . . . . . . . . . . 267
3.31.22 Knowledge about causes of environmental problems (mean) (issp_8am) . . 267
3.31.23 Knowledge about solutions to environmental problems (mean) (issp_8bm) . 268
3.31.24 Belief in science (mean) (issp_9am) . . . . . . . . . . . . . . . . . . . . . . 269
3.32 The Ocean Health Index Data . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 270
3.32.1 Fisheries management eﬀectiveness and opportunity (ohi_aoacc) . . . . . . 270
3.32.2 Ocean acidiﬁcation (ohi_caacid) . . . . . . . . . . . . . . . . . . . . . . . . 271
3.32.3 Coastal human population as a proxy for trend in trash (ohi_chp) . . . . . 272
3.32.4 Sea level rise (ohi_csslr) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 273
3.32.5 Sea surface temperature (SST) anomalies (ohi_csst) . . . . . . . . . . . . . 273
3.32.6 UV radiation (ohi_cuv) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 274
3.32.7 High bycatch caused by artisanalﬁshing (ohi_fah) . . . . . . . . . . . . . . 275
3.32.8 High bycatch caused by commercialﬁshing (ohi_fchb) . . . . . . . . . . . . 275
3.32.9 Low bycatch caused by commercialﬁshing (ohi_fclb) . . . . . . . . . . . . . 276
3.32.10 CBD survey: habitat (ohi_hab) . . . . . . . . . . . . . . . . . . . . . . . . . 277
3.32.11 CBD survey: coastal habitat (ohi_habcom) . . . . . . . . . . . . . . . . . . 278
3.32.12 CBD survey: ocean habitat (ohi_habeez) . . . . . . . . . . . . . . . . . . . 278
3.32.13 Coastal population density as a proxy for intertidal habitat destruction
(ohi_hdinter) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 279
3.32.14 Bycatch by artisanalﬁshing - hard bottom habitat destruction (ohi_hshb) . 280
3.32.15 Demersal destructiveﬁshing - soft bottom habitat destruction (ohi_hssb) . 280
3.32.16 Coastal protected areas inland 1km (ohi_lpai) . . . . . . . . . . . . . . . . 281
3.32.17 Coastal marine protected areas oﬀshore 3km (ohi_lpao) . . . . . . . . . . . 282
18

## Page 21

3.32.18 CBD Survey: Mariculture (ohi_maricul) . . . . . . . . . . . . . . . . . . . . 282
3.32.19 Areas of observed blast (dynamite)ﬁshing (ohi_npblast) . . . . . . . . . . . 284
3.32.20 Areas of observed poisonﬁshing (ohi_npcyan) . . . . . . . . . . . . . . . . 284
3.32.21 The Ocean Health Index (ohi_ohi) . . . . . . . . . . . . . . . . . . . . . . . 285
3.32.22 Coastal chemical pollution within 3 nm oﬀshore (ohi_pc3) . . . . . . . . . . 286
3.32.23 Chemical pollution (ohi_pchem) . . . . . . . . . . . . . . . . . . . . . . . . 286
3.32.24 Coastal fertilizer pollution (ohi_pn3) . . . . . . . . . . . . . . . . . . . . . . 287
3.32.25 Fertilizer pollution as a proxy for nutrient pollution (ohi_pnutrient) . . . . 288
3.32.26 Trash pollution (ohi_ptrash) . . . . . . . . . . . . . . . . . . . . . . . . . . 288
3.32.27 Alien Species (ohi_saali) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 289
3.32.28 Percent direct employment in tourism (ohi_tjpt) . . . . . . . . . . . . . . . 290
3.32.29 CBD Survey: Tourism (ohi_tour) . . . . . . . . . . . . . . . . . . . . . . . . 290
3.32.30 Sustainability index (ohi_trsust) . . . . . . . . . . . . . . . . . . . . . . . . 291
3.32.31 CBD Survey: Water (ohi_water) . . . . . . . . . . . . . . . . . . . . . . . . 292
3.33 V-Party Dataset . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 294
3.33.1 Environmental parties: share of seats (vparty_envseat) . . . . . . . . . . . 294
3.33.2 Environmental parties: share of votes (vparty_envvote) . . . . . . . . . . . 295
3.34 World Development Indicators . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 296
3.34.1 Agricultural irrigated land (% of total agricultural land) (wdi_agrland) . . 296
3.34.2 Arable land (% of land area) (wdi_araland) . . . . . . . . . . . . . . . . . . 297
3.34.3 Land area (sq. km) (wdi_area) . . . . . . . . . . . . . . . . . . . . . . . . . 297
3.34.4 Land area where elevation is below 5 meters (% of total land area) (wdi_-
areabelow) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 298
3.34.5 CO2 emissions (metric tons per capita) (wdi_co2) . . . . . . . . . . . . . . 298
3.34.6 Forest area (% of land area) (wdi_forest) . . . . . . . . . . . . . . . . . . . 299
3.34.7 Fossil fuel energy consumption (% of total) (wdi_fossil) . . . . . . . . . . . 299
19

## Page 22

3.34.8 Internally displaced persons, new displacement-disasters (number) (wdi_-
idpdis) . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 300
3.34.9 Policy and institutions for environmental sustainability (wdi_piesr) . . . . . 301
3.34.10 A verage precipitation in depth (mm per year) (wdi_precip) . . . . . . . . . 301
3.34.11 Terrestrial protected areas (% of total land area) (wdi_tpa) . . . . . . . . . 302
3.35 World Values Survey . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 303
3.35.1 Active memberships in environmental organizations (%) (wvs_ameop) . . . 304
3.35.2 Conﬁdence in environmental organizations (mean) (wvs_ceom) . . . . . . . 304
3.35.3 Donations to ecological organizations (%) (wvs_deop) . . . . . . . . . . . . 305
3.35.4 Protecting environment vs economic growth (%) (wvs_epmip) . . . . . . . 305
3.35.5 Environment is the most serious problem (%) (wvs_epmpp) . . . . . . . . . 306
3.35.6 Inactive memberships in environmental organizations (%) (wvs_imeop) . . 307
3.35.7 Participation in environmental protests (%) (wvs_pedp) . . . . . . . . . . . 307
3.35.8 Important to look after the environment (mean) (wvs_ploem) . . . . . . . . 308
4 Appendix 309
20

## Page 23

1 Introduction
1.1 The Quality of Government Institute
The Quality of Government Institute (QoG) was founded in 2004 by Professor Bo Rothstein and
Professor Sören Holmberg. It is an independent research institute within the Department of Po-
litical Science at the University of Gothenburg. The institute conducts research on the causes,
consequences and nature of Good Governance and the Quality of Government, that is, trustworthy,
reliable, impartial, uncorrupted, and competent government institutions.
The main objective of the research is to address the theoretical and empirical problems of how
political institutions of high quality can be created and maintained. A second objective is to study
the eﬀects of Quality of Government on a number of policy areas, such as health, environment,
social policy, and poverty. While Quality of Government is the common intellectual focal point of
the research institute, a variety of theoretical and methodological perspectives are applied.
21

## Page 24

1.2 The Environmental Indicators Dataset
The Quality of Government Environmental Indicators Dataset (QoG-EI) is a compilation of ma-
jor freely available indicators measuring environmental performance of countries over time. These
indicators include the presence and stringency of environmental policies, the level of pressure on
the environment (such as ecological footprint and emission levels), and public opinion on the en-
vironmental matters. The dataset also includes background geographical data such as the annual
average rainfall and the size of land area, among others. The users can merge the dataset with
other major compilations of political and social science data by using country codes from the World
Bank, Correlates of War, Quality of Government, or Varieties of Democracy datasets.
The information about all the variables included in this dataset is also available online through
the Quality of Government Data Finder - https://dataﬁnder.qog.gu.se/ . The dataﬁnder can be
treated as an online version of this Codebook.
Most of the indicators are available for several years, however, some are only available for a single
year. When using these indicators, the users are encouraged toﬁlter the dataset on that year.
Other sources that are for various reasons not included into this compilation and that can be useful
for time-series cross-sectional analysis of environmental performance are:
•ECOLEX - a database of environmental laws;
•F AOLEX - a database of laws related to the focus ares of the Food and Agriculture Organi-
zation of the United Nations;
•GRACE - a continuation of the ENVIPOLCONCHANGE dataset of environmental policy
presence and stringency;
•IUCN - detailed biodiversity measures from Red Lists of threatened species by the Interna-
tional Union for Conservation of Nature;
•Climate Change Performance Index - an expert assessment of countries’ performance in ad-
dressing climate change;
•Global Climate Risk Index - an expert assessment of the extent to which countries have been
aﬀected by the impacts of weather-related events;
•Climate Action Tracker - an expert evaluation of climate action by the governments;
•Climate Policy Tracker - overview of climate policies by country and industry;
•Questions related to climate change perceptions and environmental attitudes from Afrobarom-
eter, Latinobarometer, and some other major regional surveys.
If the users would like to make suggestions of other environmental indicators for future editions of
the dataset, please contact us at marina.povitkina@gu.se.
22

## Page 25

In 2023, we have uploaded a new version of the data that has dropped all the observations that are
empty for content variables (meaning variables that are not used for identiﬁcation). In August, 2023
we changed the name of the variables ccode and cname to ccode_wb and cname_wb respectively.
The data’s content has not changed otherwise.
23

## Page 26

2 Data Structure
2.1 Data Structure
The Environmental Indicators dataset is presented in a time-series long-form format with country-
year (identiﬁed as cname, year) observations as units; please be aware that the original source may
have a diﬀerent data structure.
When deciding which countries to include in the datasets, we have relied on the following reasoning:
We have included current members of the United Nations (UN) as well as previous members,
provided that their de facto sovereignty has not changed since they were members. This means
that we, for example, have included Taiwan.
Using UN membership to decide whether to include a country in the dataset works well for cases
from around 1955. Afterwards, states, in general, joined the UN following independence. This raises
an important question of what to do with countries that might be said to have been independent
some time during the period from 1946 to around 1955, but were not independent after that period
(such as Tibet). We decided to include data for Tibet from 1946 to 1950, making it possible for
users to decide for themselves whether to include Tibet in their analysis. It is worth noting that
we do not use the date when a country gained membership in the UN as a date when a country
came into being, but we use it to determine which countries to include in the dataset.
In this time-series dataset, we include 194 nations together with additional 17 historical coun-
tries that did not exist in 2014: Tibet, Pakistan pre 1971 (including East Pakistan, presently
Bangladesh), North and South Vietnam, North and South Yemen, East and West Germany,
Yugoslavia pre 1992 (the Peoples Republic of Yugoslavia), Serbia and Montenegro, the USSR,
Czechoslovakia, Ethiopia pre 1993 (including Eritrea), France pre 1962 (including Algeria), Malaysia
pre 1965 (including Singapore), Cyprus pre 1974 (including the later Turkish occupied north
Cyprus) and Sudan pre 2012 (including South Sudan). This makes a total of 211 countries. The
Appendix provides the full list of countries and a short note on each country. This country-name
convention is under the variable cname_qog.
Since there is no established international standard on how historical cases resulting either from
country mergers or country splits, should be treated in a time-series setting, we have applied the
following principles:
After a merger of two countries, the new country is considered to be a new case, even if the newly
formed state could be considered as a continuation of one of the merging states. This rule applies
to: (1) Vietnam, which is a result of the merger between North and South Vietnam in 1976; (2)
Yemen, which is a result of the merger between North and South Yemen in 1990; and (3) Germany,
which is a result of the merger between East and West Germany in 1990.
If a country split, the new countries are considered new cases, even if one of the new countries
could be considered as a continuation of the country that split. This rule applies to: (1) Pakistan,
which split into Pakistan and Bangladesh in 1971; (2) the USSR, which split into 15 Post-Soviet
24

## Page 27

countries in 1991; (3) Yugoslavia, which split into Slovenia, Croatia, Bosnia and Herzegovina,
North Macedonia, and Serbia and Montenegro in 1991; (4) Czechoslovakia, which split into the
Czech Republic and Slovakia in 1993; (5) France which split into France and Algeria in 1962; (6)
Malaysia which split into Malaysia and Singapore in 1965; (7) Cyprus which was occupied by Turkey
in 1974, eﬀectively splitting the country into Cyprus and the internationally unrecognized northern
Cyprus; (8) Ethiopia, which split into Ethiopia and Eritrea in 1993; and (9) Sudan, which split into
Sudan and South Sudan in 2011. There is one exception to this rule: Indonesia is considered to be
a continuation of the country that existed before the independence of Timor-Leste in 2002 (while
Timor-Leste is considered to be a new country).
Since most of the original data sources treat these cases of country mergers and splits diﬀerently,
we have rearranged data in accordance with the criteria above. Consequently, if a merger or a split
has occurred and a data source does not treat the countries as diﬀerent cases, we consider them to
be diﬀerent countries and transform the data accordingly.
In order to assign the data for the year of the merger/split, we relied on the July 1st-principle. If
the merger/split or independence occurred after July 1st, the data for this year is assigned to the
historical country.
For example, if a data source treats Germany as a continuation of West Germany, we assign the
data up to and including 1990 to West Germany and leave Germany blank until and including 1990.
Another example; if a data source treats Serbia and Montenegro as a continuation of Yugoslavia,
we assign the data up to and including 1991 to Yugoslavia and from 1992 and onward to Serbia
and Montenegro (which is left blank until and including 1991), since the split occurred from June
1991 to March 1992 (before July 1st, 1992).
Finally, Cyprus (1974-) denotes the Greek part of the island after the Turkish occupation. Most
sources probably do the same with the data they refer to Cyprus, but the documentation of the
original data rarely speciﬁes this.
In 2018, we updated the name of Swaziland to Eswatini (former Swaziland) and in 2019, we updated
the name of Macedonia to North Macedonia; however, the other identiﬁcation codes remain the
same.
25

## Page 28

3 Variables by Original Source
3.1 Identiﬁcation Variables
Note: the ccode_qog-year combination is the unique identiﬁer for the observations in this dataset.
3.1.1 cname_qog QoG Country Name
Name of the country in English with a distinction of countries that have experienced merges or
splits. For more information on how these codes are assigned, please see the Appendix.
3.1.2 ccode_qog QoG Country code
Numeric country code based on the ISO-3166-1 numeric standard. All the numeric country codes
are unique and this makes it the best suited variable to use when mergingﬁles (in combination
with year for time-series data). For more information on how these codes are assigned, please see
the Appendix. (http://en.wikipedia.org/wiki/ISO_3166-1_numeric)
3.1.3 year Year
Year.
3.1.4 cname_wb Country Name
Name of the country in English based on the International Organization for Standardization (ISO).
Please be advised this standard does not have Tibet as a country name in this standard.
3.1.5 ccode_wb Country Code
Numeric country code based on the International Organization for Standardization (ISO). Please
be advised that Tibet, South and North Vietnam and the Yemen Arab Republic (North Yemen)
do not have a country code in this standard.
3.1.6 ccodealp 3-letter Country Code
A three-letter country code based on the ISO-3166-1 alpha3 standard. Please note that the ccodealp
variable does not uniquely identify all countries.
26

## Page 29

3.1.7 ccodealp_year 3-letter Country Code and Year
A three-letter country code and year.
3.1.8 ccodecow Country Code COW
Country code from the Correlates of War.
3.1.9 ccodevdem Country Code V-Dem
Country code from the Varieties of Democracy Project.
3.1.10 cname_year Country Name and Year
Country name and year.
3.1.11 version Version of the Dataset
Version of the Environmental Indicators dataset.
27

## Page 30

3.2 Accountable Climate Targets
Dataset by:Frida Borang, Simon Felgendreher, Niklas Harring, and Asa Lofgren
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Boräng, Frida et al. 2019. “Committing to the climate: a global study of accountable climate
targets”.Sustainability. 11. 7
Link to the original source:https://www.mdpi.com/2071-1050/11/7/1861/htm
Data used in the article:
Boräng, F., Felgendreher, S., Harring, N. and Löfgren, Å., 2019. Committing to the climate: a
global study of accountable climate targets. Sustainability, 11(7), p.1861.
The authors assess and compare the accountability of climate targets as outlined in the nationally
determined contributions (NDC) of the Paris Agreement.
3.2.1 Accountable Climate Target (act_act)
A binary measure of whether a country has an accountable climate target (ACT) or not. An
ACT is a precise emissions target for which other countries can hold a country - and only that
country - accountable. A country has an ACT if it fulﬁlls two criteria: 1) the country’s nationally
determined contribution (NDC) must state an economy-wide target in reference to emission levels
from a past year, a target compared to the business-as-usual scenario, or a target in terms of
the CO2 emissions per unit of gross domestic product (GDP); 2) the commitment must not be
conditional upon receivingﬁnancial support from third parties. The measure is for 2015, at the
time of theﬁrst NDCs.
28

## Page 31

Year A vailability
 Country A vailability
29

## Page 32

3.3 Aquastat
Dataset by:Food and Agricultural Organization of the United Nations (F AO)
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
F AO. 2021.AQUASTAT Database.url:http://www.fao.org/aquastat/statistics/
query/index.html
Link to the original source:http://www.fao.org/aquastat/en/
AQUASTAT is the F AO global information system on water resources and agricultural water man-
agement.
3.3.1 Renewable internal freshwater resources (bln m3) (as_rifr)
Renewable water resources (internal and external) include average annualﬂow of rivers and recharge
of aquifers generated from endogenous precipitation and those water resources that are not gener-
ated in the country, such as inﬂows from upstream countries (groundwater and surface water), and
part of the water of border lakes and/or rivers. Measured in billion cubic meters (bln m3).
Year A vailability
 Country A vailability
30

## Page 33

3.3.2 Water stress: freshwater withdrawal, proportion of available freshwater (as_-
ws)
The level of water stress: freshwater withdrawal as a proportion of available freshwater resources is
the ratio between total freshwater withdrawn by all major sectors and total renewable freshwater
resources, after taking into account environmentalﬂow requirements. Main sectors include agricul-
ture, forestry andﬁshing, manufacturing, electricity industry, and services. This indicator is also
known as water withdrawal intensity.
Year A vailability
 Country A vailability
31

## Page 34

3.4 Bertelsmann Transformation Index
Dataset by:Bertelsmann Stiftung
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Donner, Sabine, Hauke Hartmann, and Robert Schwarz. 2020.Transformation Index of the
Bertelsmann Stiftung 2020.url:http://www.bti-project.org
Link to the original source:http://www.bti-project.org/en/index/
The Bertelsmann Stiftung’s Transformation Index (BTI) analyzes and evaluates the quality of
democracy, a market economy, and political management in 137 developing and transition coun-
tries. It measures successes and setbacks on the path towards democracy based on the rule of law
and a socially responsible market economy.
In-depth country reports provide the basis for assessing the state of transformation and persistent
challenges and for evaluating the ability of policymakers to carry out consistent and targeted re-
forms. The BTI is theﬁrst cross-national comparative index that collects data to comprehensively
measure the quality of governance during processes of transition.
3.4.1 Environmental concerns taken into account (bti_envc)
Expert answer to the question "To what extent are environmental concerns eﬀectively taken into
account?"
The variable ranges from 1 to 10, where 1 is "Environmental concerns receive no consideration and
are entirely subordinated to growth eﬀorts. There is no environmental regulation", 4 is "Environ-
mental concerns receive only sporadic consideration and are often subordinated to growth eﬀorts.
Environmental regulation is weak and hardly enforced", 7 is "Environmental concerns are taken into
account but are occasionally subordinated to growth eﬀorts. Environmental regulation and incen-
tives are in place, but their enforcement at times is deﬁcient", and 10 is "Environmental concerns
are eﬀectively taken into account and are carefully balanced with growth eﬀorts. Environmental
regulation and incentives are in place and enforced".
32

## Page 35

Year A vailability
 Country A vailability
33

## Page 36

3.5 Climate Change Knowledge Portal
Dataset by:The World Bank Group
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
The World Bank Group. 2021.Climate Change Knowledge Portal.url:https://climateknowledgeportal.
worldbank.org
Harris, Ian et al. 2020. “Version 4 of the CRU TS monthly high-resolution gridded multivari-
ate climate dataset”.Scientiﬁc Data. 7. 1.url:https://doi.org/10.1038/s41597-020-
0453-3
Link to the original source:https://climateknowledgeportal.worldbank.org
The Climate Change Knowledge Portal provides global data on historical and future climate, vul-
nerabilities, and impacts.
The data on historical temperature and rainfall data included in this compilation comes from
the historical CRU dataset. The CRU TS version 4.04 gridded historical dataset is derived from
observational data and provides quality-controlled temperature and rainfall values from thousands
of weather stations worldwide, as well as derivative products including monthly climatologies and
long-term historical climatologies. The dataset is produced by the Climatic Research Unit (CRU)
of the University of East Anglia (UEA) CRU-(Gridded Product).
In order to present historical climate conditions, the World Bank Group’s Climate Change Knowl-
edge Portal (CCKP) uses the globally available observational datasets derived from CRU to quantify
changes in mean annual temperature and mean annual precipitation for the period 1901-2019 per
country.
3.5.1 Annual average rainfall (cckp_rain)
Annual average rainfall in millimeters.
34

## Page 37

Year A vailability
 Country A vailability
3.5.2 Annual average temperature (cckp_temp)
Annual average temperature in Celsius.
Year A vailability
 Country A vailability
35

## Page 38

3.6 Climate Change Laws of the World
Dataset by:Grantham Research Institute on Climate Change and the Environment
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Grantham Research Institute on Climate Change and the Environment and Sabin Center for
Climate Change Law. 2021.Climate Change Laws of the World database.url:climate-
laws.org
Link to the original source:https://climate-laws.org/
Climate change-related laws and policies refer to legal documents related to reducing energy de-
mand, promoting low carbon energy supply, low-carbon buildings, carbon pricing, lower industry
emissions, tackling deforestation and promoting sustainable land use, other mitigation eﬀorts, re-
search and development, sustainable transportation, enhancing adaptation capabilities, and natural
disaster risk management. The dataset only included laws and policies that have been passed by
legislative branches or published by executive branches, and that are no longer in draft form. The
dataset also captures major amendments to legislation. Laws that are outdated, either because
they have been repealed, replaced, or reversed, are not included.
The database distinguishes between Laws or legislative acts (e.g. acts, laws, decree-laws), which
were passed by a parliament or equivalent legislative authority, and Policies, or other executive
provisions (e.g. presidential decrees, executive orders, regulations, government policies, strategies,
or plans), which were published or decreed by the government, president, or equivalent executive
authority.
3.6.1 Climate change policy/executive provision in place (ccl_exepp)
Number of climate change-related policies or other executive provisions (e.g., presidential decrees,
executive orders, regulations, government policies, strategies, or plans), which were published or
decreed by the government, president, or equivalent executive authority, in the recorded year.
36

## Page 39

Year A vailability
 Country A vailability
3.6.2 Climate change law in place (ccl_leglp)
Number of climate change-related laws or legislative acts (e.g. acts, laws, decree-laws), which were
passed by a parliament or equivalent legislative authority, in the recorded year.
Year A vailability
 Country A vailability
3.6.3 Climate change law or policy in place (ccl_lpp)
Number of climate change-related laws (legislative acts) and policies (executive provisions) adopted
per year.
37

## Page 40

Year A vailability
 Country A vailability
3.6.4 Climate change mitigation law or policy in place (ccl_mitlpp)
Number of laws (legislative acts) or policies (executive provisions) related to climate change miti-
gation adopted per year.
Mitigation laws and policies refer to a legislative or executive disposition focused on curbing a
country’s greenhouse gases emissions in one sector or more. Measures can be directly related to
emissions reductions, such as laws establishing a national carbon budget or cap and trade system, or
indirectly related, such as laws or policies establishing relevant institutions or providing additional
funding for research and development into low carbon technologies. Laws and policies addressing
forests and land use are included as long as they explicitly support climate change mitigation
through activities that reduce emissions and increase carbon removals. General forest management
and conservation laws are not included, even if they may have implicit consequences for climate
change mitigation.
Year A vailability
 Country A vailability
38

## Page 41

3.6.5 Number of climate change policies/executive provisions (ccl_nexep)
Cumulative sum of climate change-related policies or other executive provisions (e.g. presiden-
tial decrees, executive orders, regulations, government policies, strategies, or plans), which were
published or decreed by the government, president, or equivalent executive authority.
Year A vailability
 Country A vailability
3.6.6 Number of climate change laws (ccl_nlegl)
Cumulative sum of climate change-related laws or legislative acts (e.g. acts, laws, decree-laws),
which were passed by a parliament or equivalent legislative authority.
Year A vailability
 Country A vailability
39

## Page 42

3.6.7 Number of climate change laws and policies (ccl_nlp)
Cumulative sum of laws (legislative acts) and policies (executive provisions) related to climate
change.
Year A vailability
 Country A vailability
3.6.8 Number of climate change mitigation laws and policies (ccl_nmitlp)
Cumulative sum of laws (legislative acts) and policies (executive provisions) related to climate
change mitigation.
Mitigation laws and policies refer to a legislative or executive disposition focused on curbing a
country’s greenhouse gases emissions in one sector or more. Measures can be directly related to
emissions reductions, such as laws establishing a national carbon budget or cap and trade system, or
indirectly related, such as laws or policies establishing relevant institutions or providing additional
funding for research and development into low carbon technologies. Laws and policies addressing
forests and land use are included as long as they explicitly support climate change mitigation
through activities that reduce emissions and increase carbon removals. General forest management
and conservation laws are not included, even if they may have implicit consequences for climate
change mitigation.
40

## Page 43

Year A vailability
 Country A vailability
41

## Page 44

3.7 Cooperation in International Climate Change Regime
Dataset by:Michèle B. Baettig, Simone Brander, Dieter M. Imboden
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Bättig, Michèle B, Simone Brander, and Dieter M Imboden. 2008. “Measuring countries co-
operation within the international climate change regime”.Environmental Science & Policy.
11. 6
Link to the original source:https://www.sciencedirect.com/science/article/abs/pii/S1462901108000440
The index and its components measure countries’ cooperation within the international climate
change regime. The Cooperation in International Climate Change Regime Index is an aggregate
ofﬁve indicators: The United Nations Framework Convention on Climate Change (UNFCCC) and
Kyoto Protocol Indicators, which measure countries’ commitment to common international goals,
and the Reporting, Finance, and Emission Indicators, which measure the degree to which countries
follow up on the respective commitments within the international regime.
3.7.1 Cooperation in International Climate Change Regime Index (ccci_coop)
The index aggregates the UNFCCC, Kyoto Protocol, Reporting, Finance, and Emission Indicators.
All variables are summed and have equal weight except for the Emission Indicator which is given
double weight. The index varies on a 0-6 scale.
Year A vailability
 Country A vailability
42

## Page 45

3.7.2 Emission Indicator (ccci_em)
The indicator measures the status of CO2 emissions while accounting for diﬀerences in national
population and diﬀerent paths of economic development. Countries are assessed according to the
Environmental Kuznets Curve (EKC), which indicates that the relationship between per capita
CO2 emissions and per capita GDP is positive only up to a certain point of development, after
which the relationship becomes negative. A +/- 50 percent interval is created for the EKC, and a
trend is measured for each country from 1990 to 2002. If a country’s trend is greater than the +50
percent band, the country scores 0. If a country’s trend is less than the band, it scores 1.
Year A vailability
 Country A vailability
3.7.3 Finance Indicator (ccci_ﬁn)
The indicator measures how well a country has upheld itsﬁnancial obligations to the core budget of
the UNFCCC. Countries were evaluated according to their "Status of Contributions" reports from
1996 and 2005. A score of 1 is given if the country has paid all due payments up to the present
year and at least 50 percent of the amount for the present year. The score decreases linearly to a
score of 0 if the country has paid no contributions.
43

## Page 46

Year A vailability
 Country A vailability
3.7.4 Kyoto Protocol Indicator (ccci_kyoto)
This two-part indicator equally weighs the willingness and promptness of a country in adopting the
Kyoto Protocol. Willingness is scored as either 0.5 if a country adopted the Kyoto Protocol by the
end of 2005 or 0 if it did not. Promptness is scored on a declining scale that starts at 0.5 and ends
at 0. The highest score is given if a country adopted the Kyoto Protocol at its earliest possible
ratiﬁcation in April 1998. The lowest score is given if a country had not ratiﬁed the Kyoto Protocol
by the end of 2005.
Year A vailability
 Country A vailability
3.7.5 Reporting Indicator (ccci_rep)
This two-part indicator equally measures whether and how fast a country has submitted its latest
National Communication (NC) on the state of its climate plan. The country is scored either 0.5
if it submitted the lastest required NC before the end of 2005 or 0 if it did not. The country is
44

## Page 47

given an additional 0.5 if the report was submitted before the deadline. This score decreases until
reaching 0 for a submission 6 or more months after the deadline for Annex I (AI) countries, and a
submission 36 months or more after the deadline for Non-Annex I (NAI) countries.
Year A vailability
 Country A vailability
3.7.6 UNFCCC Indicator (ccci_unfccc)
This two-part indicator equally weighs the willingness and promptness of a country in adopting the
United Nations Framework Convention on Climate Change (UNFCCC). Willingness is scored as
either 0.5 if a country adopted the UNFCCC by the end of 2005 or 0 if it did not. Promptness is
scored on a declining scale that starts at 0.5 and ends at 0. The highest score is given if the country
adopted the UNFCCC at its earliest possible ratiﬁcation date in July 1992. The lowest score is
given if a country had not ratiﬁed the UNFCC at the time of the Kyoto Conference in December
1997.
Year A vailability
 Country A vailability
45

## Page 48

3.8 EDGAR - Fossil CO2 Emissions of All World Countries
Dataset by:European Commission
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Crippa, Monica, Diego Guizzardi, Marilena Muntean, E. Schaaf, et al. 2020.Fossil CO2
emissions of all world countries - 2020 Report.url:https://edgar.jrc.ec.europa.eu/
overview.php?v=booklet2020
Link to the original source:https://edgar.jrc.ec.europa.eu/report_2020
The Emissions Database for Global Atmospheric Research (EDGAR) provides global past and
present-day anthropogenic emissions of greenhouse gases and air pollutants by country and on a
spatial grid.
Fossil CO2 emissions of all world countries from EDGAR provides an independent estimate of CO2
emissions for each world country, based on a robust and consistent methodology stemming from
the latest IPCC guidelines and most recent activity data. Fossil CO2 emission data are available
for the time period 1970-2019.
3.8.1 CO2 emissions per GDP (edgar_co2gdp)
The total CO2 (carbon dioxide) emissions per country, divided by each country’s respective GDP
(gross domestic product). Units are tonnes of CO2 per thousand US dollars of GDP.
Includes all fossil CO2 sources, such as fossil fuel combustion, non-metallic mineral processes (e.g.,
cement production), metal (ferrous and non-ferrous) production processes, urea production, agri-
cultural liming, and solvents use. Large-scale biomass burning with Savannah burning, forestﬁres,
and sources and sinks from land-use, land-use change, and forestry (LULUCF) are excluded.
46

## Page 49

Year A vailability
 Country A vailability
3.8.2 CO2 emissions per capita (edgar_co2pc)
The total CO2 (carbon dioxide) emissions per country, divided by each country’s respective popu-
lation. Units are tonnes of CO2 per capita per year.
Includes all fossil CO2 sources, such as fossil fuel combustion, non-metallic mineral processes (e.g.,
cement production), metal (ferrous and non-ferrous) production processes, urea production, agri-
cultural liming, and solvents use. Large-scale biomass burning with Savannah burning, forestﬁres,
and sources and sinks from land-use, land-use change, and forestry (LULUCF) are excluded.
Year A vailability
 Country A vailability
3.8.3 CO2 emissions total (edgar_co2t)
The total CO2 (carbon dioxide) emissions aggregated across sectors per country. Includes all
fossil CO2 sources, such as fossil fuel combustion, non-metallic mineral processes (e.g., cement
47

## Page 50

production), metal (ferrous and non-ferrous) production processes, urea production, agricultural
liming, and solvents use. Large-scale biomass burning with Savannah burning, forestﬁres, and
sources and sinks from land-use, land-use change, and forestry (LULUCF) are excluded. Units are
kilotonnes (kt) of CO2 per year.
Year A vailability
 Country A vailability
48

## Page 51

3.9 EDGAR - Global Air Pollutant Emissions
Dataset by:European Commission
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Crippa, Monica, Eﬁsio Solazzo, et al. 2020. “High resolution temporal proﬁles in the Emissions
Database for Global Atmospheric Research”.Nature Scientiﬁc Data. Vol. 7. 1
European Commission, Joint Research Centre (EC-JRC)/Netherlands Environmental Assess-
ment Agency (PBL). 2020.Emissions Database for Global Atmospheric Research (EDGAR),
release EDGAR v5.0 (1970 - 2015) of April 2020.url:https://edgar.jrc.ec.europa.eu/
overview.php?v=50_AP
Crippa, Monica, Diego Guizzardi, Marilena Muntean, Edwin Schaaf, et al. 2019.EDGAR
v5.0 Global Air Pollutant Emissions.url:http://data.europa.eu/89h/377801af-b094-
4943-8fdc-f79a7c0c2d19
Link to the original source:https://edgar.jrc.ec.europa.eu/dataset_ap50
The Emissions Database for Global Atmospheric Research (EDGAR) provides global past and
present-day anthropogenic emissions of greenhouse gases and air pollutants by country and on a
spatial grid. EDGAR provides emission data for the following air pollutants:
Ozone precursor gases: Carbon Monoxide (CO), Nitrogen Oxides (NOx), Non-Methane Volatile
Organic Compounds (NMVOC) and Methane (CH4).
Acidifying gases: Ammonia (NH3), Nitrogen oxides (NOx) and Sulfur Dioxide (SO2).
Primary particulates: Fine Particulate Matter (PM10 and PM2.5 and Carbonaceous speciation
(BC, OC).
Emissions from large-scale biomass burning with Savannah burning, forestﬁres, and sources and
sinks from land-use, land-use change, and forestry (LULUCF) are excluded.
For the energy-related sectors, the activity data are mainly based on the energy balance statistics of
IEA (2017) (http://www.oecd-ilibrary.org/energy/co2-emissions-from-fuel-combustion-2017_co2_-
fuel-2017-en), whereas the activity data for the agricultural sectors originate mainly from F AO
(2018) (http://www.fao.org/faostat/en/#home). Additional information can be found in Crippa
49

## Page 52

et al. (2019).
3.9.1 BC emissions (edgar_bc)
The total BC (black carbon, particulate matter) emissions, aggregated across sectors per country.
Units are kilotonnes (kt) of black carbon per year.
Year A vailability
 Country A vailability
3.9.2 CH4 emissions (edgar_ch4)
The total CH4 (methane) emissions aggregated across sectors per country. Units are kilotonnes
(kt) of CH4 per year.
Year A vailability
 Country A vailability
50

## Page 53

3.9.3 CO emissions (edgar_co)
The total CO (carbon monoxide) emissions aggregated across sectors per country. Emissions from
large-scale biomass burning with Savannah burning, forestﬁres, and sources and sinks from land-
use, land-use change, and forestry (LULUCF) are excluded. Units are kilotonnes (kt) of CO per
year.
Year A vailability
 Country A vailability
3.9.4 N2O emissions (edgar_n2o)
The total N2O (nitrous oxide) emissions aggregated across sectors per country. Units are kilotonnes
(kt) of N2O per year.
Year A vailability
 Country A vailability
51

## Page 54

3.9.5 NH3 emissions (edgar_nh3)
The total NH3 (ammonia) emissions aggregated across sectors per country. Units are kilotonnes
(kt) of NH3 per year.
Year A vailability
 Country A vailability
3.9.6 NMVOC emissions (edgar_nmvoc)
The total NMVOC (non-methane volatile organic compounds) emissions aggregated across sectors
per country. Units are kilotonnes (kt) of NMVOC per year.
Year A vailability
 Country A vailability
52

## Page 55

3.9.7 NOx emissions (edgar_nox)
The total NOx (nitrogen oxides) emissions aggregated across sectors per country. Units are kilo-
tonnes (kt) of NOx per year.
Year A vailability
 Country A vailability
3.9.8 OC emissions (edgar_oc)
The total OC (organic carbon, particulate matter) emissions aggregated across sectors per country.
Units are kilotonnes (kt) of OC per year.
Year A vailability
 Country A vailability
53

## Page 56

3.9.9 PM10 emissions (edgar_pm10)
The total PM10 (particulate matter, 10 micrometers or smaller) emissions aggregated across sectors
per country. Units are kilotonnes (kt) of PM10 per year.
Year A vailability
 Country A vailability
3.9.10 PM2.5 emissions (edgar_pm25)
The total PM2.5 (particulate matter, 2.5 micrometers or smaller) emissions aggregated across sec-
tors per country. Units are kilotonnes (kt) of PM2.5 per year.
Year A vailability
 Country A vailability
54

## Page 57

3.9.11 SO2 emissions (edgar_so2)
The total SO2 (sulfur dioxide) emissions aggregated across sectors per country. Units are kilotonnes
(kt) of SO2 per year.
Year A vailability
 Country A vailability
55

## Page 58

3.10 ENVIPOLCON
Dataset by:Holzinger, Knill, Sommerer
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Heichel, Stephan et al. 2008. “Research design, variables and data”.url:https://www.
polver.uni- konstanz.de/en/holzinger/research/research- projects/enviromental-
policy-convergence-in-europe-envipolcon/project-deliverables/
Link to the original source:https://www.polver.uni-konstanz.de/holzinger/research/research-
projects/enviromental-policy-convergence-in-europe-envipolcon/
ENVIPOLCON is the acronym of "Environmental governance in Europe: the impact of interna-
tional institutions and trade on policy convergence". The project was carried out between 2003 and
2006 by the University of Konstanz, University of Hamburg, Germany, Free University of Berlin,
University of Salzburg, and Radboud University Nijmegen. The project was supported by the EU,
RTD programme "Improving the human research potential and the socioeconomic knowledge base",
contract no. HPSE-CT-2002-00103.
This compilation only includes data on policy instrument adoption from ENVIPOLCON. Each
of the instrument variables is coded with scores ranging from 1= obligatory standard to 10 =
voluntary instrument. 0 = no instrument because no policy was in place yet. For the variable on
the promotion of renewable energy (e.g. ener_i7) the additional instrument "legal obligation to
purchase that electricity" was coded as = 11.
Other variables from ENVIPOLCON are included into the extension of the dataset - ENVIPOL-
CONCHANGE, which is also a part of this compilation.
3.10.1 Policy instruments for quality of bathing water (epc_bath)
Policy instruments on quality of bathing water. The variable measures the presence of a policy
instrument in 1970, 1980, 1990, and 2000.
Variable coding:
0 = ’No policy’
1 = ’Obligatory standard, prohibition or ban’
56

## Page 59

2 = ’Technological prescription’
3 = ’Tax or levy’
4 = ’Subsidy or tax reduction’
5 = ’Liability scheme(s)’
6 = ’Planning instrument’
7 = ’Public investment’
8 = ’Data collection / monitoring programme(s)’
9 = ’Information based instrument’
10 = ’Voluntary instrument’ .
Year A vailability
 Country A vailability
3.10.2 Policy instruments for exhaust emissions from cars (epc_car)
Policy instruments on exhaust emissions from cars. The variable measures the presence of a policy
instrument in 1970, 1980, 1990, and 2000.
Variable coding:
0 = ’No policy’
1 = ’Obligatory standard, prohibition or ban’
2 = ’Technological prescription’
3 = ’Tax or levy’
57

## Page 60

4 = ’Subsidy or tax reduction’
5 = ’Liability scheme(s)’
6 = ’Planning instrument’
7 = ’Public investment’
8 = ’Data collection / monitoring programme(s)’
9 = ’Information based instrument’
10 = ’Voluntary instrument’ .
Year A vailability
 Country A vailability
3.10.3 Policy instruments for reduction of CO2 emissions from heavy industry (epc_-
co2)
Policy instruments on reduction of CO2 emissions from heavy industry. The variable measures the
presence of a policy instrument in 1970, 1980, 1990, and 2000.
Variable coding:
0 = ’No policy’
1 = ’Obligatory standard, prohibition or ban’
2 = ’Technological prescription’
3 = ’Tax or levy’
4 = ’Subsidy or tax reduction’
58

## Page 61

5 = ’Liability scheme(s)’
6 = ’Planning instrument’
7 = ’Public investment’
8 = ’Data collection / monitoring programme(s)’
9 = ’Information based instrument’
10 = ’Voluntary instrument’ .
Year A vailability
 Country A vailability
3.10.4 Policy instruments for hazardous substances in detergents (epc_dete)
Policy instruments on hazardous substances in detergents. The variable measures the presence of
a policy instrument in 1970, 1980, 1990, and 2000.
Variable coding:
0 = ’No policy’
1 = ’Obligatory standard, prohibition or ban’
2 = ’Technological prescription’
3 = ’Tax or levy’
4 = ’Subsidy or tax reduction’
5 = ’Liability scheme(s)’
6 = ’Planning instrument’
59

## Page 62

7 = ’Public investment’
8 = ’Data collection / monitoring programme(s)’
9 = ’Information based instrument’
10 = ’Voluntary instrument’ .
Year A vailability
 Country A vailability
3.10.5 Policy instruments for energy eﬃciency of refrigerators (epc_enef)
Policy instruments on energy eﬃciency of refrigerators. The variable measures the presence of a
policy instrument in 1970, 1980, 1990, and 2000.
Variable coding:
0 = ’No policy’
1 = ’Obligatory standard, prohibition or ban’
2 = ’Technological prescription’
3 = ’Tax or levy’
4 = ’Subsidy or tax reduction’
5 = ’Liability scheme(s)’
6 = ’Planning instrument’
7 = ’Public investment’
8 = ’Data collection / monitoring programme(s)’
60

## Page 63

9 = ’Information based instrument’
10 = ’Voluntary instrument’ .
Year A vailability
 Country A vailability
3.10.6 Policy instruments for electricity from renewable sources (epc_ener)
Policy instruments on electricity production from renewable sources. The variable measures the
presence of a policy instrument in 1970, 1980, 1990, and 2000.
Variable coding:
0 = ’No policy’
1 = ’Obligatory standard, prohibition or ban’
2 = ’Technological prescription’
3 = ’Tax or levy’
4 = ’Subsidy or tax reduction’
5 = ’Liability scheme(s)’
6 = ’Planning instrument’
7 = ’Public investment’
8 = ’Data collection / monitoring programme(s)’
9 = ’Information based instrument’
10 = ’Voluntary instrument’
61

## Page 64

11 = ’Extra instrument for energy.
Year A vailability
 Country A vailability
3.10.7 Policy instruments for forest protection policy (epc_fors)
Policy instruments on forest protection. The variable measures the presence of a policy instrument
in 1970, 1980, 1990, and 2000.
Variable coding:
0 = ’No policy’
1 = ’Obligatory standard, prohibition or ban’
2 = ’Technological prescription’
3 = ’Tax or levy’
4 = ’Subsidy or tax reduction’
5 = ’Liability scheme(s)’
6 = ’Planning instrument’
7 = ’Public investment’
8 = ’Data collection / monitoring programme(s)’
9 = ’Information based instrument’
10 = ’Voluntary instrument’ .
62

## Page 65

Year A vailability
 Country A vailability
3.10.8 Policy instruments for lead emissions from vehicles (epc_lead)
Policy instruments on lead emissions from vehicles. The variable measure the presence of a policy
instrument in 1970, 1980, 1990, and 2000.
Variable coding:
0 = ’No policy’
1 = ’Obligatory standard, prohibition or ban’
2 = ’Technological prescription’
3 = ’Tax or levy’
4 = ’Subsidy or tax reduction’
5 = ’Liability scheme(s)’
6 = ’Planning instrument’
7 = ’Public investment’
8 = ’Data collection / monitoring programme(s)’
9 = ’Information based instrument’
10 = ’Voluntary instrument’ .
63

## Page 66

Year A vailability
 Country A vailability
3.10.9 Policy instruments for noise emissions from lorries (epc_nois)
Policy instruments on noise emission from lorries. The variable measures the presence of a policy
instrument in 1970, 1980, 1990, and 2000.
Variable coding:
0 = ’No policy’
1 = ’Obligatory standard, prohibition or ban’
2 = ’Technological prescription’
3 = ’Tax or levy’
4 = ’Subsidy or tax reduction’
5 = ’Liability scheme(s)’
6 = ’Planning instrument’
7 = ’Public investment’
8 = ’Data collection / monitoring programme(s)’
9 = ’Information based instrument’
10 = ’Voluntary instrument’ .
64

## Page 67

Year A vailability
 Country A vailability
3.10.10 Policy instruments to promote reﬁllable beverage containers (epc_pawa)
Policy instruments to promote reﬁllable beverage containers. The variable measures the presence
of a policy instrument in 1970, 1980, 1990, and 2000.
Variable coding:
0 = ’No policy’
1 = ’Obligatory standard, prohibition or ban’
2 = ’Technological prescription’
3 = ’Tax or levy’
4 = ’Subsidy or tax reduction’
5 = ’Liability scheme(s)’
6 = ’Planning instrument’
7 = ’Public investment’
8 = ’Data collection / monitoring programme(s)’
9 = ’Information based instrument’
10 = ’Voluntary instrument’ .
65

## Page 68

Year A vailability
 Country A vailability
3.10.11 Policy instruments for contaminated sites (epc_soil)
Policy instruments on contaminated sites. The variable measures the presence of a policy instrument
in 1970, 1980, 1990, and 2000.
Variable coding:
0 = ’No policy’
1 = ’Obligatory standard, prohibition or ban’
2 = ’Technological prescription’
3 = ’Tax or levy’
4 = ’Subsidy or tax reduction’
5 = ’Liability scheme(s)’
6 = ’Planning instrument’
7 = ’Public investment’
8 = ’Data collection / monitoring programme(s)’
9 = ’Information based instrument’
10 = ’Voluntary instrument’ .
66

## Page 69

Year A vailability
 Country A vailability
3.10.12 Policy instruments for water protection related to industrial discharges
(epc_watp)
Policy instruments on industrial discharges into water bodies. The variable measures the presence
of a policy instrument in 1970, 1980, 1990, and 2000.
Variable coding:
0 = ’No policy’
1 = ’Obligatory standard, prohibition or ban’
2 = ’Technological prescription’
3 = ’Tax or levy’
4 = ’Subsidy or tax reduction’
5 = ’Liability scheme(s)’
6 = ’Planning instrument’
7 = ’Public investment’
8 = ’Data collection / monitoring programme(s)’
9 = ’Information based instrument’
10 = ’Voluntary instrument’ .
67

## Page 70

Year A vailability
 Country A vailability
68

## Page 71

3.11 ENVIPOLCONCHANGE
Dataset by:Holzinger, Knill, Sommerer
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Holzinger, Katharina, Christoph Knill, and Thomas Sommerer. 2011. “Is there conver-
gence of national environmental policies? An analysis of policy outputs in 24 OECD coun-
tries”.Environmental politics. 20. 1.url:https : / / www . polver . uni - konstanz . de /
holzinger/research/research-projects/policy-wandel-in-der-umweltpolitik-der-
einfluss-von-nationalen-vetospielern-und-transnationalem-policy-learning/der-
datensatz-environmental-policy-chance-envipolchange/
Link to the original source:https://www.polver.uni-konstanz.de/holzinger/research/research-
projects/policy-wandel-in-der-umweltpolitik-der-einfluss-von-nationalen-vetospielern-
und-transnationalem-policy-learning/der-datensatz-environmental-policy-chance-envipolchange/
The Dataset "ENVIPOLCONCHANGE (Environmental Policy Change). A dataset on environ-
mental regulations in 24 OECD countries from 1970 to 2005" has been collected by the ENVIPOL-
CON group at the University of Konstanz (Stephan Heichel, Katharina Holzinger, Christoph Knill,
Thomas Sommerer) in 2009. Data collection was funded by the German Research Foundation DFG
(Grant HO 1811/3-1; KN 891/1-1)."
The names of most variables follow the following structure:
epcc_*_in2 - the introduction of the policy for theﬁrst time;
epcc_*_ch2 - change in the policy, including the introduction;
epcc_*_s, epcc_car_*, and epcc_lcp_* - standards, such as limit values on emissions and similar,
where * is a code of the policy issue.
3.11.1 Change in eco audit policy (epcc_audi_ch2)
The variable measures whether there was a change in the policy for eco-audit in the recorded year.
This is a binary variable, where "1" is assigned to the year when there was a change in the policy,
including itsﬁrst introduction, and "0" is assigned to all other years.
69

## Page 72

Year A vailability
 Country A vailability
3.11.2 Eco audit policy introduction (epcc_audi_in2)
The variable measures theﬁrst introduction of the policy for eco-audit. This is a binary variable,
where "1" is assigned to the year when the policy wasﬁrst introduced and "0" is assigned to all
other years.
Year A vailability
 Country A vailability
3.11.3 Change in coliforms in bathing water policy (epcc_bath_ch2)
The variable measures whether there was a change in the policy for the quality of bathing water
in the recorded year. This is a binary variable, where "1" is assigned to the year when there was a
change in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
70

## Page 73

Year A vailability
 Country A vailability
3.11.4 Coliforms in bathing water policy introduction (epcc_bath_in2)
The variable measures theﬁrst introduction of the policy for quality of bathing water. This is a
binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and "0" is
assigned to all other years.
Year A vailability
 Country A vailability
3.11.5 Passenger car emissions CO regulatory level (epcc_car_co)
A limit value for CO emissions in g/km, adjusted.
71

## Page 74

Year A vailability
 Country A vailability
3.11.6 Passenger car emissions HC regulatory level (epcc_car_hc)
A limit value for HC emissions in g/km, adjusted.
Year A vailability
 Country A vailability
3.11.7 Passenger car emissions NOx regulatory level (epcc_car_nox)
A limit value for NOx emissions in g/km, adjusted.
72

## Page 75

Year A vailability
 Country A vailability
3.11.8 Change in passenger car emissions policy (epcc_care_ch2)
The variable measures whether there was a change in the policy for exhaust emissions from cars
in the recorded year. This is a binary variable, where "1" is assigned to the year when there was a
change in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.9 Passenger car emissions policy introduction (epcc_care_in2)
The variable measures theﬁrst introduction of the policy for exhaust emissions from cars. This is
a binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and "0" is
assigned to all other years.
73

## Page 76

Year A vailability
 Country A vailability
3.11.10 Sum of downward changes in all 17 standards (epcc_cd_dwsum)
Sum of downward changes in all 17 variables that measure standards/regulatory levels in the
recorded year. Higher score, on average, corresponds to a decrease in policy standards.
Year A vailability
 Country A vailability
3.11.11 Sum of upward changes in all 17 standards (epcc_cd_upsum)
Sum of all upward changes in the 17 variables that measure standards/regulatory levels included
in this dataset in the recorded year. Higher score corresponds to, on average, increased policy
standards.
74

## Page 77

Year A vailability
 Country A vailability
3.11.12 Sum of all changes in policy (epcc_ch2)
Sum of all changes in policies, including introductions, in the recorded year.
Year A vailability
 Country A vailability
3.11.13 Cumulative sum of all policy-in-place items (epcc_ch_kum)
Cumulative sum of all Policy-in-Place variables. Higher score corresponds to a higher number of
policies in place.
75

## Page 78

Year A vailability
 Country A vailability
3.11.14 Change in contaminated sites policy (epcc_cont_ch2)
The variable measures whether there was a change in the policy for contaminated sites in the
recorded year. This is a binary variable, where "1" is assigned to the year when there was a change
in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.15 Contaminated sites policy introduction (epcc_cont_in2)
The variable measures theﬁrst introduction of the policy for contaminated sites. This is a binary
variable, where "1" is assigned to the year when the policy wasﬁrst introduced and "0" is assigned
to all other years.
76

## Page 79

Year A vailability
 Country A vailability
3.11.16 Change in recycling of construction waste policy (epcc_cowa_ch2)
The variable measures whether there was a change in the policy for recycling construction waste
in the recorded year. This is a binary variable, where "1" is assigned to the year when there was a
change in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.17 Recycling of construction waste policy introduction (epcc_cowa_in2)
The variable measures theﬁrst introduction of the policy for recycling of construction waste. This
is a binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and "0"
is assigned to all other years.
77

## Page 80

Year A vailability
 Country A vailability
3.11.18 Change in detergents regulation policy (epcc_dete_ch2)
The variable measures whether there was a change in the policy for hazardous substances in deter-
gents in the recorded year. This is a binary variable, where "1" is assigned to the year when there
was a change in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.19 Detergents regulation policy introduction (epcc_dete_in2)
The variable measures theﬁrst introduction of the policy for hazardous substances in detergents.
This is a binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and
"0" is assigned to all other years.
78

## Page 81

Year A vailability
 Country A vailability
3.11.20 Change in ecolabel policy (epcc_ecol_ch2)
The variable measures whether there was a change in the policy for eco-labelling in the recorded
year. This is a binary variable, where "1" is assigned to the year when there was a change in the
policy, including itsﬁrst introduction, and "0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.21 Ecolabel policy introduction (epcc_ecol_in2)
The variable measures theﬁrst introduction of the policy for eco-labeling. This is a binary variable,
where "1" is assigned to the year when the policy wasﬁrst introduced and "0" is assigned to all
other years.
79

## Page 82

Year A vailability
 Country A vailability
3.11.22 Change in environmental impact assessment (epcc_eias_ch2)
The variable measures whether there was a change in the policy for environmental impact assessment
in the recorded year. This is a binary variable, where "1" is assigned to the year when there was a
change in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.23 Environmental impact assessment introduction (epcc_eias_in2)
The variable measures theﬁrst introduction of the policy for environmental impact assessment.
This is a binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and
"0" is assigned to all other years.
80

## Page 83

Year A vailability
 Country A vailability
3.11.24 Change in energy eﬃciency of refrigerators policy (epcc_enef_ch2)
The variable measures whether there was a change in the policy for the energy eﬃciency of refrig-
erators in the recorded year. This is a binary variable, where "1" is assigned to the year when there
was a change in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.25 Energy eﬃciency of refrigerators policy introduction (epcc_enef_in2)
The variable measures theﬁrst introduction of the policy for energy eﬃciency of refrigerators. This
is a binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and "0"
is assigned to all other years.
81

## Page 84

Year A vailability
 Country A vailability
3.11.26 Glass recycling target in regulations, % (epcc_glas2_s)
Glass reuse/recycling target in percent of total waste generated.
Year A vailability
 Country A vailability
3.11.27 Change in glass recycling target in regulation (epcc_glas_ch2)
The variable measures whether there was a change in the policy for glass reuse/recycling target in
the recorded year. This is a binary variable, where "1" is assigned to the year when there was a
change in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
82

## Page 85

Year A vailability
 Country A vailability
3.11.28 Glass recycling target in regulation introduction (epcc_glas_in2)
The variable measures theﬁrst introduction of the policy for glass reuse/recycling target. This is
a binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and "0" is
assigned to all other years.
Year A vailability
 Country A vailability
3.11.29 Sum ofﬁrst policy introductions (epcc_intro_kum)
Sum of all variables measuring theﬁrst introduction of a policy. Higher number corresponds to a
higher number of policies being adopted in the recorded year.
83

## Page 86

Year A vailability
 Country A vailability
3.11.30 Change in landﬁll target in regulations (epcc_land_ch2)
The variable measures whether there was a change in the policy for waste landﬁll target in the
recorded year. This is a binary variable, where "1" is assigned to the year when there was a change
in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.31 Landﬁll target in regulations introduction (epcc_lanr_in2)
The variable measures theﬁrst introduction of the policy for waste landﬁll target. This is a binary
variable, where "1" is assigned to the year when the policy wasﬁrst introduced and "0" is assigned
to all other years.
84

## Page 87

Year A vailability
 Country A vailability
3.11.32 Large combustion plants regulatory level DUST (epcc_lcp_dust)
A limit value for dust from large combustion plants in mg/m3.
Year A vailability
 Country A vailability
3.11.33 Large combustion plants regulatory level NOX (epcc_lcp_nox)
A limit value for NOx emissions from large combustion plants in mg/m3.
85

## Page 88

Year A vailability
 Country A vailability
3.11.34 Large combustion plants regulatory level SO2 (epcc_lcp_so2)
A limit value for SO2 emissions from large combustion plants in mg/m3.
Year A vailability
 Country A vailability
3.11.35 Change in large combustion plants policy (epcc_lcpt_ch2)
The variable measures whether there was a change in the policy for airborne emissions from large
combustion plants in the recorded year. This is a binary variable, where "1" is assigned to the year
when there was a change in the policy, including itsﬁrst introduction, and "0" is assigned to all
other years.
86

## Page 89

Year A vailability
 Country A vailability
3.11.36 Large combustion plants policy introduction (epcc_lcpt_in2)
The variable measures theﬁrst introduction of the policy for airborne emissions from large com-
bustion plants. This is a binary variable, where "1" is assigned to the year when the policy wasﬁrst
introduced and "0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.37 Change lead content in petrol policy (epcc_lead_ch2)
The variable measures whether there was a change in the policy for lead emissions from vehicles
in the recorded year. This is a binary variable, where "1" is assigned to the year when there was a
change in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
87

## Page 90

Year A vailability
 Country A vailability
3.11.38 Lead content in petrol policy introduction (epcc_lead_in2)
The variable measures theﬁrst introduction of the policy for lead emissions from vehicles. This is
a binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and "0" is
assigned to all other years.
Year A vailability
 Country A vailability
3.11.39 Lead content in petrol regulatory level (epcc_lead_s)
A limit value for lead content in petrol in g/l.
88

## Page 91

Year A vailability
 Country A vailability
3.11.40 Change in motorway noise emissions policy (epcc_moto_ch2)
The variable measures whether there was a change in the policy for noise level around motorways
in the recorded year. This is a binary variable, where "1" is assigned to the year when there was a
change in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.41 Motorway noise emissions policy introduction (epcc_moto_in2)
The variable measures theﬁrst introduction of the policy for noise level around motorways. This
is a binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and "0"
is assigned to all other years.
89

## Page 92

Year A vailability
 Country A vailability
3.11.42 Motorway noise emissions regulatory level (epcc_moto_s)
Motorway noise emissions standard in decibel (dB (A)).
Year A vailability
 Country A vailability
3.11.43 Change in noise emissions from lorries policy (epcc_nois_ch2)
The variable measures whether there was a change in the policy for noise emissions from lorries in
the recorded year. This is a binary variable, where "1" is assigned to the year when there was a
change in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
90

## Page 93

Year A vailability
 Country A vailability
3.11.44 Noise emissions from lorries policy introduction (epcc_nois_in2)
The variable measures theﬁrst introduction of the policy for noise emissions from lorries. This is
a binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and "0" is
assigned to all other years.
Year A vailability
 Country A vailability
3.11.45 Noise emissions from lorries regulatory level (epcc_nois_s)
Noise emissions standard from lorries in decibel (dB(a)).
91

## Page 94

Year A vailability
 Country A vailability
3.11.46 Change in packaging waste recycling target (epcc_pact_ch2)
The variable measures whether there was a change in the policy for waste packaging target in the
recorded year. This is a binary variable, where "1" is assigned to the year when there was a change
in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.47 Packaging waste recycling target introduction (epcc_pact_in2)
The variable measures theﬁrst introduction of the policy for waste packaging target. This is a
binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and "0" is
assigned to all other years.
92

## Page 95

Year A vailability
 Country A vailability
3.11.48 Paper recycling target in regulations, % (epcc_pape2_s)
Waste paper reuse/recycling target in percent of waste generated.
Year A vailability
 Country A vailability
3.11.49 Change in paper recycling target in regulation (epcc_pape_ch2)
The variable measures whether there was a change in the policy for waste paper reuse/recycling
target in the recorded year. This is a binary variable, where "1" is assigned to the year when there
was a change in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
93

## Page 96

Year A vailability
 Country A vailability
3.11.50 Paper recycling target in regulation introduction (epcc_pape_in2)
The variable measures theﬁrst introduction of the policy for waste paper reuse/recycling target.
This is a binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and
"0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.51 Change in soil policy (epcc_soil_ch2)
The variable measures whether there was a change in the soil policy in the recorded year. This is a
binary variable, where "1" is assigned to the year when there was a change in the policy, including
itsﬁrst introduction, and "0" is assigned to all other years.
94

## Page 97

Year A vailability
 Country A vailability
3.11.52 Soil policy introduction (epcc_soil_in2)
The variable measures theﬁrst introduction of the soil policy. This is a binary variable, where "1"
is assigned to the year when the policy wasﬁrst introduced and "0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.53 Change in sulphur content gas oil policy (epcc_sulp_ch2)
The variable measures whether there was a change in the policy for sulphur content in gas oil in
the recorded year. This is a binary variable, where "1" is assigned to the year when there was a
change in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
95

## Page 98

Year A vailability
 Country A vailability
3.11.54 Sulphur content gas oil policy introduction (epcc_sulp_in2)
The variable measures theﬁrst introduction of the policy for sulphur content in gas oil. This is a
binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and "0" is
assigned to all other years.
Year A vailability
 Country A vailability
3.11.55 Sulphur content in gas oil regulatory level (epcc_sulp_s)
A limit value for sulphur content in gas oil, as % per weight.
96

## Page 99

Year A vailability
 Country A vailability
3.11.56 Change in National environmental policy/Sustainable development plan
(epcc_susp_ch2)
The variable measures whether there was a change in the policy for the national environmental
policy or sustainable development plan in the recorded year. This is a binary variable, where "1" is
assigned to the year when there was a change in the policy, including itsﬁrst introduction, and "0"
is assigned to all other years.
Year A vailability
 Country A vailability
3.11.57 National environmental policy/Sustainable development plan introduction
(epcc_susp_in2)
The variable expresses theﬁrst introduction of the policy for the national environmental policy or
sustainable development plan. This is a binary variable, where "1" is assigned to the year when the
policy wasﬁrst introduced and "0" is assigned to all other years.
97

## Page 100

Year A vailability
 Country A vailability
3.11.58 Water protection - BOD in industrial discharges (epcc_wabo_s)
A limit value for biochemical oxygen demand (BOD) in industrial discharges in mg/l.
Year A vailability
 Country A vailability
3.11.59 Water protection - Copper in industrial discharges (epcc_waco_s)
A limit value for Copper in industrial discharges in mg/l.
98

## Page 101

Year A vailability
 Country A vailability
3.11.60 Water protection - Chromium in industrial discharges (epcc_wacr_s)
A limit value for Chromium in industrial discharges in mg/l.
Year A vailability
 Country A vailability
3.11.61 Change in eﬃcient use of water in industry policy (epcc_waef_ch2)
The variable measures whether there was a change in the policy for eﬃcient use of the water industry
in the recorded year. This is a binary variable, where "1" is assigned to the year when there was a
change in the policy, including itsﬁrst introduction, and "0" is assigned to all other years.
99

## Page 102

Year A vailability
 Country A vailability
3.11.62 Eﬃcient use of water in industry policy introduction (epcc_waef_in2)
The variable measures theﬁrst introduction of the policy for eﬃcient use of the water industry.
This is a binary variable, where "1" is assigned to the year when the policy wasﬁrst introduced and
"0" is assigned to all other years.
Year A vailability
 Country A vailability
3.11.63 Water protection - Lead in industrial discharges (epcc_wale_s)
A limit value for Lead in industrial discharges in mg/l.
100

## Page 103

Year A vailability
 Country A vailability
3.11.64 Change in water protection policy - industrial discharges (epcc_wapr_ch2)
The variable measures whether there was a change in the policy for water protection in industrial
discharges in the recorded year. This is a binary variable, where "1" is assigned to the year when
there was a change in the policy, including itsﬁrst introduction, and "0" is assigned to all other
years.
Year A vailability
 Country A vailability
3.11.65 Water protection - industrial discharges introduction (epcc_wapr_in2)
The variable measures theﬁrst introduction of the policy for water protection in industrial dis-
charges. This is a binary variable, where "1" is assigned to the year when the policy wasﬁrst
introduced and "0" is assigned to all other years.
101

## Page 104

Year A vailability
 Country A vailability
3.11.66 Water protection - Zinc in industrial discharges (epcc_wazi_s)
A limit value for Zinc in industrial discharges in mg/l.
Year A vailability
 Country A vailability
102

## Page 105

3.12 Emergency Events Database
Dataset by:Centre for Research on the Epidemiology of Disasters
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Guha-Sapir, Debarati. 2020. “EM-DAT, the Emergency Events Database”.url:www.emdat.
be
Link to the original source:https://www.emdat.be/
EM-DAT is a global database on natural and technological disasters, containing essential core
data on the occurrence and eﬀects of more than 21,000 disasters in the world, from 1900 to present.
EM-DAT is maintained by the Centre for Research on the Epidemiology of Disasters (CRED) at
the School of Public Health of the Université catholique de Louvain located in Brussels, Belgium.
The database is made up of information from various sources, including UN agencies, non-governmental
organizations, insurance companies, research institutes, and press agencies. Priority is given to data
from UN agencies, governments, and the International Federation of Red Cross and Red Crescent
Societies. This prioritization is not only a reﬂection of the quality or value of the data, it also
reﬂects the fact that most reporting sources do not cover all disasters or have political limitations
that could aﬀect theﬁgures. The entries are constantly reviewed for inconsistencies, redundancy,
and incompleteness. CRED consolidates and updates data on a daily basis. A further check is
made at monthly intervals, and revisions are made at the end of each calendar year.
EM-DAT distinguishes between two generic categories for disasters: natural and technological. The
natural disaster category is divided into 5 sub-groups - geophysical (e.g., earthquakes), meteorolog-
ical (e.g., extreme temperature), hydrological (e.g.,ﬂood), climatological (e.g., drought), biological
(e.g., epidemic), and extraterrestrial (e.g., asteroids). The 5 sub-groups in turn cover 15 disaster
types and more than 30 sub-types. The technological disaster category is divided into 3 sub-groups
- industrial, transport, and miscelleanous accidents, - which in turn cover 15 disaster types.
For a disaster to be entered into the database at least one of the following criteria must be fulﬁlled:
a) Ten (10) or more people reported killed;
b) Hundred (100) or more people reported aﬀected;
c) Declaration of a state of emergency;
d) Call for international assistance.
103

## Page 106

3.12.1 Total damage from natural disasters in USD (emdat_damage)
The amount of damage to property, crops, and livestock from natural disasters. The value of
estimated damage is given in thousands of US dollars. For each natural disaster, the registered
number corresponds to the damage value at the moment of the event, i.e. theﬁgures are shown
true to the year of the event (do not include expenses that extended to the following years).
Year A vailability
 Country A vailability
3.12.2 Number of people aﬀected by natural disasters (emdat_naﬀect)
The number of people requiring immediate assistance during a period of emergency after a natural
disasters, i.e. requiring basic survival needs such as food, water, shelter, sanitation, and immediate
medical assistance.
Year A vailability
 Country A vailability
104

## Page 107

3.12.3 Number of people killed by natural disasters (emdat_ndeath)
The number of people who lost their lives because the natural hazard happened and people whose
whereabouts since the natural disaster is unknown, and who are presumed dead (oﬃcialﬁgure when
available).
Year A vailability
 Country A vailability
3.12.4 Number of natural disasters (emdat_ndis)
Total number of natural disasters occurring per country per year. Natural disasters that last more
than one year or begin at the end of the year and last into the next are counted at the year of their
ﬁrst occurrence.
Year A vailability
 Country A vailability
105

## Page 108

3.12.5 Number of homeless people after natural disaster (emdat_nhome)
The number of people whose house is destroyed or heavily damaged and therefore need shelter after
a natural disaster.
Year A vailability
 Country A vailability
3.12.6 Number of people injured in natural disasters (emdat_ninj)
The number of people suﬀering from physical injuries, trauma or an illness requiring immediate
medical assistance as a direct result of a natural disaster.
Year A vailability
 Country A vailability
3.12.7 Number of aﬀected (total) by natural disasters (emdat_ntotaﬀ)
Sum of people injured, homeless, and aﬀected as a result of natural disasters.
106

## Page 109

Year A vailability
 Country A vailability
107

## Page 110

3.13 Environmental Land Use Data
Dataset by:Food and Agricultural Organization of the United Nations (F AO)
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Food and Agricultural Organization of the United Nations. 2020.Global Forest Resources
Assessments.url:http://www.fao.org/forest-resources-assessment/en/
Link to the original source:http://www.fao.org/faostat/en/#home
The F AOSTAT Land Use domain contains data on 47 categories of land use, irrigation and agricul-
tural practices, relevant to monitor agriculture, forestry, andﬁsheries activities at national, regional
and global level. Data are available by country and year, with global coverage and annual updates.
Note: Micronesia has been dropped due to duplicate cases.
3.13.1 Agricultural land (% of Land area) (fao_luagr)
Agricultural land as a share of total land area.
Year A vailability
 Country A vailability
108

## Page 111

3.13.2 Arable land (% of Agricultural land) (fao_luagrara)
Arable land as a share of total agricultural land.
Year A vailability
 Country A vailability
3.13.3 Cropland (% of Agricultural land) (fao_luagrcrop)
Cropland as a share of total agricultural land.
Year A vailability
 Country A vailability
3.13.4 Agriculture area actually irrigated (% of Agricultural land) (fao_luagrirrac)
Agriculture area actually irrigated as a share of total agricultural land.
109

## Page 112

Year A vailability
 Country A vailability
3.13.5 Land area equipped for irrigation (% of Agricultural land) (fao_luagrirreq)
Land area equipped for irrigation as a share of total agricultural land.
Year A vailability
 Country A vailability
3.13.6 Land area equipped for irrigation (% of Cropland) (fao_luagrirreqcrop)
Land area equipped for irrigation as a share of total cropland.
110

## Page 113

Year A vailability
 Country A vailability
3.13.7 Agriculture area under organic agric. (% of Agricultural land) (fao_luagrorg)
Agriculture area under organic agriculture as a share of total agricultural land.
Year A vailability
 Country A vailability
3.13.8 Land under perm meadows and pastures (% of Agricultural land) (fao_-
luagrpas)
Land under perm meadows and pastures as a share of total agricultural land.
111

## Page 114

Year A vailability
 Country A vailability
3.13.9 Land under permanent crops (% of Agricultural land) (fao_luagrpcrop)
Land under permanent crops as a share of total agricultural land.
Year A vailability
 Country A vailability
3.13.10 Cropland (% of Land area) (fao_lucrop)
Cropland as a share of total land area.
112

## Page 115

Year A vailability
 Country A vailability
3.13.11 Forest land (% of Land area) (fao_luforest)
Forest land as a share of total land area.
Year A vailability
 Country A vailability
3.13.12 Planted forest (% of Forest area) (fao_luforplant)
Planted forest as a share of total forest area.
113

## Page 116

Year A vailability
 Country A vailability
3.13.13 Other naturally regenerated forest (% of Forest area) (fao_luforreg)
Other naturally regenerated forest as a share of total forest area.
Year A vailability
 Country A vailability
3.13.14 Land under perm meadows and pastures (% of Land area) (fao_lupas)
Land under perm meadows and pastures as a share of total land area.
114

## Page 117

Year A vailability
 Country A vailability
115

## Page 118

3.14 Environmental Ministries
Dataset by:Michaël Aklin and Johannes Urpelainen
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Aklin, Michaël and Johannes Urpelainen. 2014. “The global spread of environmental min-
istries: domestic–international interactions”.International Studies Quarterly. 58. 4
Link to the original source:https://academic.oup.com/isq/article/58/4/764/1815756?login=
true
Data on the establishment of environmental ministries from the article:
Aklin, M. and Urpelainen, J., 2014. The global spread of environmental ministries: domesticinter-
national interactions. International Studies Quarterly, 58(4), pp.764-780.
3.14.1 Environmental ministry establishment (em_envmin)
Environmental ministry onset. The variable is coded "1" on the year when a national environmental
ministry got established. For the rest of the years, the variable is coded "0". The authors expanded
temporal and spatial coverage of the data initially published in the article:
Busch, P.O. and Jörgens, H., 2005. The international sources of policy convergence: explaining the
spread of environmental policy innovations. Journal of European public policy, 12(5), pp.860-884.
116

## Page 119

Year A vailability
 Country A vailability
117

## Page 120

3.15 Environmental Non-Governmental Organizations
Dataset by:Thomas Bernauer, Tobias Böhmelt, and Vally Koubi
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Bernauer, Thomas, Tobias Böhmelt, and Vally Koubi. 2013. “Is there a democracy–civil
society paradox in global environmental governance?”Global Environmental Politics. 13. 1
Link to the original source:https://ib.ethz.ch/data/civilsoc.html
Data on environmental non-governmental organizations used in the article:
Bernauer, T., Böhmelt, T. and Koubi, V., 2013. Is there a democracycivil society paradox in global
environmental governance? Global Environmental Politics, 13(1), pp.88-107.
3.15.1 Number of national ENGOs (engo_nengo)
National environmental non-governmental organizations (ENGOs) registered in a country.
The data on registered national ENGOs comes from the archives of the International Union for
Conservationof Nature (IUCN) for the time period 1973-2006 from 181 countries. While the IUCN
covers most countries, it is an umbrella organization where membership is not mandatory and
ENGOs do not have to register. As a result, some ENGOs that have not registered with the IUCN
may have been omitted. Therefore the variable becomes a proxy for the political leverage of ENGOs.
118

## Page 121

Year A vailability
 Country A vailability
119

## Page 122

3.16 Environmental Performance Index Data 2020
Dataset by:Environmental Performance Index
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Wendling, Z.A. et al. 2020. “2020 Environmental Performance Index”.New Haven, CT: Yale
Center for Environmental Law and Policy.url:https://epi.envirocenter.yale.edu/
Link to the original source:https://epi.envirocenter.yale.edu/epi-downloads
The Environmental Performance Index provides a ranking that shines light on how each coun-
try manages environmental issues. The Environmental Performance Index (EPI) ranks how well
countries perform on high-priority environmental issues in two broad policy areas: protection of
human health from environmental harm and protection of ecosystems. Within these two policy ob-
jectives the EPI scores country performance in 11 issue areas comprised of 32 indicators. Indicators
in the EPI measure how close countries are to meeting internationally established targets or, in the
absence of agreed-upon targets, how they compare to the range of observed countries.
Note: In many cases the EPI variables lack actual observations and rely on imputation. Please
refer to the original documentation on more information about this. Also, some values (usually the
value 0) are very unlikely, please use your judgement whether to treat these as the value 0 or as
"Data missing".
The values on the EPI, Policy Objectives, and Issue Categories are not comparable over time, there-
fore, this compilation only includes data on these variables from the latest release. The raw data
on the 32 indicators, however, are comparable over time and, therefore, time-series are included.
3.16.1 Agriculture Issue Category (epi_agr)
Agriculture Issue Category consists of the Sustainable Nitrogen Management Index, which measures
the Euclidean distance from an ideal point with optimal nitrogen use eﬃciency (NUE) and crop
yield. The issue category varies from 0 to 100.
120

## Page 123

Year A vailability
 Country A vailability
3.16.2 Air Quality Issue Category (epi_air)
Air Quality Issue Category consists of three indicators:
1) Household air pollution (HAP), measured with the number of age-standardized disability-adjusted
life-years (DALYs) lost per 100,000 persons due to the health risk posed by the incomplete com-
bustion of solid fuels. It is log-transformed and given 40% weight in the aggregation.
2) Ambient particulate matter pollution, measured as the PM2.5 exposure using the number of age-
standardized disability-adjusted life-years lost per 100,000 persons (DALY rate) due to exposure to
ﬁne air particulate matter smaller than 2.5 micrometers (PM2.5). It is log-transformed and given
55% weight in the aggregation.
3) Ozone exposure, measured by the number of age-standardized disability-adjusted life-years lost
per 100,000 persons (DALY rate) due to exposure to ground-level ozone pollution. It is log-
transformed and given 5% weight in the aggregation.
The issue category varies from 0 to 100.
121

## Page 124

Year A vailability
 Country A vailability
3.16.3 Pollution Emissions Issue Category (epi_ape)
Pollution Emissions Issue Category consists of 2 indicators:
1) The SO2 growth rate, calculated as the average annual rate of increase or decrease in SO2
over the years 2005-2014. It is then adjusted for economic trends to isolate change due to policy
rather than economicﬂuctuation. First, the EPI team calculates Spearman’s correlation coeﬃcient
between SO2 emissions and GDP over a ten-year period. Second, they regress logged SO2 emissions
over ten years toﬁnd a slope. Third, they calculate an unadjusted average annual growth rate in
SO2 emissions. Fourth, they adjust the negative growth rates by a factor of 1 - the correlation
coeﬃcient.
2) The NOX growth rate, calculated as the average annual rate of increase or decrease in NOX over
the years 2005-2014. It is then adjusted for economic trends to isolate change due to policy rather
than economicﬂuctuation. First, the EPI team calculates Spearman’s correlation coeﬃcient be-
tween NOX emissions and GDP over a ten-year period. Second, they regress logged NOX emissions
over ten years toﬁnd a slope. Third, they calculate an unadjusted average annual growth rate in
NOX emissions. Fourth, they adjust the negative growth rates by a factor of 1 - the correlation
coeﬃcient.
Both indicators are given equal weight in the aggregation. The issue category varies from 0 to 100.
122

## Page 125

Year A vailability
 Country A vailability
3.16.4 Black carbon growth rate (epi_bca)
The black carbon growth rate, which makes up 5% of the Climate Change Issue Category, is
calculated as the average annual rate of increase or decrease in black carbon over the years 2005-
2014. It is then adjusted for economic trends to isolate change due to policy rather than economic
ﬂuctuation.
Original source: Community Emissions Data Systems.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.5 Biodiversity and Habitat Issue Category (epi_bdh)
Biodiversity and Habitat Issue Category consists of 7 indicators:
123

## Page 126

1) The terrestrial biome protection (national weights) indicator. It is calculated byﬁrst taking
proportions of the area of each of a countrys biome types that are covered by protected areas and
then constructing a weighted sum of the protection percentages for all biomes within that country.
The protection percentages are weighted according to the prevalence of each biome type within
that country. This indicator evaluates a country’s eﬀorts to achieve 17% protection for all biomes
within its borders, as per Aichi Target 11. It is given 20% weight in the aggregation.
2) The terrestrial biome protection (global weights) indicator, where protection percentages are
weighted according to the global prevalence of each biome type. This indicator evaluates a countrys
contribution toward the global 17% protection goal. It is given 20% weight in the aggregation.
3) The marine protected areas indicator, measured as a percentage of a countrys total exclusive
economic zone (EEZ) designated as marine protected areas (MPAs). Because each country may
have multiple EEZs, the summed area of MPAs is divided by the summed EEZ. It is given 20%
weight in the aggregation.
4) The Protected Areas Representativeness Index (PARI), which measures ecological representa-
tiveness as the proportion of biologically scaled environmental diversity included in a country’s
terrestrial protected areas. The measure relies on remote sensing, biodiversity informatics, and
global modeling ofﬁne-scaled variation in biodiversity composition for plant, vertebrate, and inver-
tebrate species. It is given 10% weight in the aggregation.
5) Species Habitat Index (SHI) estimates potential population losses, as well as regional and global
extinction risks of individual species, using habitat loss as a proxy. The SHI indicator measures the
proportion of suitable habitat within a country that remains intact for each species in that country
relative to a baseline set in the year 2001. It is given 10% weight in the aggregation.
6) Species Protection Index (SPI) evaluates the species-level ecological representativeness of each
country’s protected area network. The SPI metric uses remote sensing data, global biodiversity
informatics, and integrative models to map suitable habitat for over 30,000 terrestrial vertebrate,
invertebrate, and plant species at high resolutions. It is given 10% weight in the aggregation.
7) The Biodiversity Habitat Index (BHI), which estimates the eﬀects of habitat loss, degradation,
and fragmentation on the expected retention of terrestrial biodiversity. It is given 10% weight in
the aggregation.
The issue category varies from 0 to 100.
124

## Page 127

Year A vailability
 Country A vailability
3.16.6 Biodiversity habitat index (epi_bhv)
Biodiversity Habitat Index (BHI) estimates the eﬀects of habitat loss, degradation, and fragmen-
tation on the expected retention of terrestrial biodiversity.
Original source: Commonwealth Scientiﬁc and Industrial Research Organization.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.7 Climate Change Issue Category (epi_cch)
Climate Change Issue Category consists of 8 indicators:
1) The CO2 growth rate, calculated as the average annual rate of increase or decrease in raw carbon
125

## Page 128

dioxide emissions over the years 2008-2017. It is then adjusted for economic trends to isolate change
due to policy rather than economicﬂuctuation. It is given 55% weight in the aggregation.
2) The CH4 growth rate, calculated as the average annual rate of increase or decrease in raw
methane emissions over the years 2008-2017. It is then adjusted for economic trends to isolate
change due to policy rather than economicﬂuctuation. It is given 15% weight in the aggregation.
3) The F-gas growth rate, calculated as the average annual rate of increase or decrease in raw
ﬂuorinated gas emissions over the years 2008-2017. It is then adjusted for economic trends to isolate
change due to policy rather than economicﬂuctuation. It is given 10% weight in the aggregation.
4) The N2O growth rate, calculated as the average annual rate of increase or decrease in raw nitrous
oxide emissions over the years 2008-2017. It is then adjusted for economic trends to isolate change
due to policy rather than economicﬂuctuation. It is given 5% weight in the aggregation.
5) The black carbon growth rate, calculated as the average annual rate of increase or decrease in
black carbon over the years 2005-2014. It is then adjusted for economic trends to isolate change
due to policy rather than economicﬂuctuation. It is given 5% weight in the aggregation.
6) Greenhouse gas (GHG) emissions per capita in the year 2017. First, the EPI team calculates
total greenhouse gas emissions, applying Global Warming Potentials to convert all units to Gg of
CO2-equivalents. Second, they calculate GHG emissions per capita (GHP) as the GHG emissions
divided by population (POP). It is log-transformed and given 2.5% weight in the aggregation.
7) CO2 emissions from land cover change, calculated over the years 2001-2015. First, the EPI team
regresses logged CO2 emissions from land cover change (LULC) over 15 years toﬁnd a slope. Then,
they calculate an unadjusted average annual growth rate in these CO2 emissions. It is given 2.5%
weight in the aggregation.
8) The greenhouse gas (GHG) intensity growth rate indicator, which serves as a signal of countries’
progress in decoupling emissions from economic growth. The EPI team calculates an annual average
growth rate in GHG emissions per unit of GDP over the years 2008-2017. This indicator highlights
the need for action on climate change mitigation in countries at all income levels. It is given 5%
weight in the aggregation.
The issue category varies from 0 to 100.
126

## Page 129

Year A vailability
 Country A vailability
3.16.8 CO2 growth rate (epi_cda)
The CO2 (carbon dioxide) growth rate, which makes up 55% of the Climate Change Issue Category,
is calculated as the average annual rate of increase or decrease in raw carbon dioxide emissions over
the years 2008-2017. It is then adjusted for economic trends to isolate change due to policy rather
than economicﬂuctuation.
Original source: Potsdam Institute for Climate Impact Research.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
127

## Page 130

3.16.9 CH4 growth rate (epi_cha)
The CH4 (methane) growth rate, which makes up 15% of the Climate Change Issue Category, is
calculated as the average annual rate of increase or decrease in raw methane emissions over the
years 2008-2017. It is then adjusted for economic trends to isolate change due to policy rather than
economicﬂuctuation.
Original source: Potsdam Institute for Climate Impact Research.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.10 Ecosystem Services Issue Category (epi_ecs)
Ecosystem Services Issue Category consists of 3 indicators:
1) Tree cover loss, measured as aﬁve-year moving average of the percentage of forest lost from the
extent of forest cover in the reference year 2000. They deﬁne a forest as any land area with over
30% canopy cover. It is log-transformed, ln(x +α),α= 9.70E-07, and given 90% weight in the
aggregation.
2) Grassland loss, measured as aﬁve-year moving average of percentage of gross losses in grassland
areas compared to the 1992 reference year. It is log-transformed, ln(x +α),α= 4.45E-06, and
given 5% weight in the aggregation.
3) Wetland loss, measured as aﬁve-year moving average of percentage of gross losses in wetland
areas compared to the 1992 reference year. It is log-transformed, ln(x +α),α= 2.47E-06, and
given 5% weight in the aggregation.
The issue category varies from 0 to 100.
128

## Page 131

Year A vailability
 Country A vailability
3.16.11 Environmental Health Policy Objective (epi_eh)
Environmental Health Policy Objective measures how well countries are protecting their populations
from environmental health risks. It comprises 40% of the total EPI score and consists of 4 issue
categories: Air Quality (50%), Sanitation and Drinking Water (40%), Heavy Metals (5%), and
Waste Management (5%). The policy objective varies from 0 to 100.
Year A vailability
 Country A vailability
3.16.12 Environmental Performance Index (epi_epi)
The 2020 Environmental Performance Index (EPI) scores 180 countries on 32 performance indicators
across 11 issue categories related to environmental health and ecosystem vitality. The 2020 EPI
is a composite index. The EPI researchers begin by gathering data on 32 individual metrics of
environmental performance. These metrics are aggregated into a hierarchy beginning with 11
issue categories: Air Quality, Sanitation and Drinking Water, Heavy Metals, Waste Management,
129

## Page 132

Biodiversity and Habitat, Ecosystem Services, Fisheries, Climate Change, Pollution Emissions,
Water Resources, and Agriculture.
These issue categories are then combined into 2 policy objectives, Environmental Health and Ecosys-
tem Vitality, and thenﬁnally consolidated into the overall EPI. To allow for meaningful comparisons,
before aggregation the EPI researchers construct scores for each of the 32 indicators, placing them
onto a common scale where 0 indicates worst performance and 100 indicates best performance. How
far a country is from achieving international targets of sustainability determines its placement on
this scale.
Note: The EPI scores are not comparable over time, therefore, this dataset only includes the EPI
scores from the latest release.
Year A vailability
 Country A vailability
3.16.13 Ecosystem Vitality Policy Objective (epi_ev)
Ecosystem Vitality Policy Objective measures how well countries are preserving, protecting, and
enhancing ecosystems and the services they provide. It comprises 60% of the total EPI score and
consists of 7 issue categories: Biodiversity and Habitat (25%), Ecosystem Services (10%), Fisheries
(10%), Climate Change (40%), Pollution Emissions (5%), Agriculture (5%), and Water Resources
(5%). The policy objective varies from 0 to 100.
130

## Page 133

Year A vailability
 Country A vailability
3.16.14 Fish caught by trawling (epi_fct)
Fish caught by trawling measures the percentage of a country’sﬁsh caught by bottom or pelagic
trawling, where aﬁshing net is pulled through the water behind a boat. This practice is indiscrim-
inate and wasteful and can severely damage marine ecosystems. The variable is log-transformed
according to the formula ln(x+α), whereα= 8.40E-08.
Original source: Sea Around Us.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
131

## Page 134

3.16.15 F-gas growth rate (epi_fga)
The F-gas growth rate, which makes up 10% of the Climate Change Issue Category, is calculated
as the average annual rate of increase or decrease in rawﬂuorinated gas emissions over the years
2008-2017. It is then adjusted for economic trends to isolate change due to policy rather than
economicﬂuctuation.
Original source: Potsdam Institute for Climate Impact Research.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.16 Fisheries Issue Category (epi_fsh)
Fisheries Issue Category consists of 3 indicators:
1) Fish stock status, measured as the percentage of a country’s total catch that comes from overex-
ploited or collapsed stocks, considering allﬁsh stocks within a country’s EEZs. Because continued
and increased stock exploitation leads to smaller catches, this indicator sheds light on the impact of
a country’sﬁshing practices. The metric is calculated as an average percentage weighted by catch
and summed across classes of concern. It is log-transformed, ln(x +α),α= 1.13E-05, and given
35% weight in the aggregation.
2) Marine Trophic Index (MTI), which measures the health of a country’sﬁshing stock based on
expected catch and changes over time. The MTI describes the degree to which a country is depleting
species at higher trophic levels andﬁshing down the food web. It is log-transformed, ln(x +α),α
= 9.51E-07, and given 35% weight in the aggregation.
3) Fish caught by trawling, measured as the percentage of a country’sﬁsh caught by bottom or
pelagic trawling, where aﬁshing net is pulled through the water behind a boat. It is log-transformed,
ln(x +α),α= 8.40E-08, and given 30% weight in the aggregation.
132

## Page 135

The issue category varies from 0 to 100.
Year A vailability
 Country A vailability
3.16.17 Fish stock status (epi_fss)
Fish stock status measures the percentage of a country’s total catch that comes from overexploited
or collapsed stocks, considering allﬁsh stocks within a country’s EEZs. Because continued and
increased stock exploitation leads to smaller catches, this indicator sheds light on the impact of
a country’sﬁshing practices. The variable is log-transformed according to the formula ln(x+α),
whereα= 1.13E-05.
Original source: Sea Around Us.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
133

## Page 136

3.16.18 GHG emissions per capita (epi_ghp)
EPI calculates greenhouse gas (GHG) emissions per capita for each country in the year 2017. The
variable is log-transformed. The unit of measurement is gigagrams (Gg) of CO2-equivalent per
person.
Original source: Potsdam Institute for Climate Impact Research.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.19 GHG intensity trend (epi_gib)
The greenhouse gas (GHG) intensity growth rate indicator serves as a signal of countries’ progress
in decoupling emissions from economic growth. EPI calculates an annual average growth rate in
GHG emissions per unit of GDP over the years 2008-2017. This indicator highlights the need for
action on climate change mitigation in countries at all income levels.
Original source: Potsdam Institute for Climate Impact Research.
When using this variable, please cite both EPI and the original source.
134

## Page 137

Year A vailability
 Country A vailability
3.16.20 Grassland loss (epi_grl)
Grassland loss is measured using aﬁve-year moving average of percentage of gross losses in grassland
areas compared to the 1992 reference year. The variable is log-transformed according to the formula
ln(x+α), whereα= 4.45E-06.
Original source: European Space Agency.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.21 Sanitation and Drinking Water Issue Category (epi_h2o)
Sanitation and Drinking Water Issue Category consists of two indicators:
135

## Page 138

1) Unsafe sanitation, measured as the proportion of a country’s population exposed to health risks
from their access to sanitation, deﬁned by the primary toilet type used by households. It is log-
transformed and given 40% weight in the aggregation.
2) Unsafe drinking water, measured as the proportion of a country’s population exposed to health
risks from their access to drinking water, deﬁned by the primary water source used by households
and the household water treatment, or the treatment that happens at the point of water collection.
It is log-transformed and given 60% weight in the aggregation.
Both indicators are measured using the number of age-standardized disability-adjusted life-years
(DALYs) lost per 100,000 persons. The issue category varies from 0 to 100.
Year A vailability
 Country A vailability
3.16.22 Household solid fuels (epi_had)
EPI measures household solid fuels using the number of age-standardized disability-adjusted life-
years lost per 100,000 persons (DALY rate) due to exposure to household air pollution (HAP) from
the use of household solid fuels. The variable is log-transformed.
Original source: Institute for Health Metrics and Evaluation.
When using this variable, please cite both EPI and the original source.
136

## Page 139

Year A vailability
 Country A vailability
3.16.23 Heavy Metals Issue Category (epi_hmt)
Heavy Metals Issue Category consists of the indicator Lead Exposure, which measures the number
of age-standardized disability-adjusted life-years (DALYs) lost per 100,000 persons due to this risk.
It is log-transformed. The issue category varies from 0 to 100.
Year A vailability
 Country A vailability
3.16.24 CO2 from land cover (epi_lcb)
This indicator measures CO2 emissions from land cover change and is calculated over the years
2001-2015. The unit of measurement is proportion.
Original source: Mullion Group.
When using this variable, please cite both EPI and the original source.
137

## Page 140

Year A vailability
 Country A vailability
3.16.25 Marine protected areas (epi_mpa)
Marine protected areas indicator is measured as the percentage of a country’s total exclusive eco-
nomic zone (EEZ) designated as marine protected areas (MPAs). MPAs represent a critical tool
for protecting marine ecosystems from unsustainableﬁshing practices, pollution, and human dis-
turbance. Because each country may have multiple EEZs, the summed area of MPAs is divided by
the summed EEZ.
Original source: World Database on Protected Areas.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
138

## Page 141

3.16.26 Controlled solid waste (epi_msw)
Controlled solid waste refers to the proportion of household and commercial waste generated in
a country that is collected and treated in a manner that controls environmental risks. This met-
ric counts waste as controlled if it is treated through recycling, composting, anaerobic digestion,
incineration, or disposed of in a sanitary landﬁll.
Original source: Wiedinmyer et al. 2014 & Kaza et al. 2018.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.27 Marine trophic index (epi_mti)
Marine Trophic Index (MTI) measures the health of a country’sﬁshing stock based on expected
catch and changes over time. The MTI measures the degree to which a country is depleting species
at higher trophic levels andﬁshing down the food web. The variable is log-transformed according
to the formula ln(x+α), whereα= 9.51E-07.
Original source: Sea Around Us.
When using this variable, please cite both EPI and the original source.
139

## Page 142

Year A vailability
 Country A vailability
3.16.28 N2O growth rate (epi_noa)
The N2O growth rate, which makes up 5% of the Climate Change issue category, is calculated as
the average annual rate of increase or decrease in raw nitrous oxide emissions over the years 2008-
2017. It is then adjusted for economic trends to isolate change due to policy rather than economic
ﬂuctuation.
Original source: Potsdam Institute for Climate Impact Research.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
140

## Page 143

3.16.29 NOx growth rate (epi_nxa)
The NOX growth rate is calculated as the average annual rate of increase or decrease in NOX over
the years 2005-2014. It is then adjusted for economic trends to isolate change due to policy rather
than economicﬂuctuation.
Original source: Community Emissions Data Systems.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.30 Ozone exposure (epi_ozd)
EPI measures ozone exposure using the number of age-standardized disability-adjusted life-years
lost per 100,000 persons (DALY rate) due to exposure to ground-level ozone pollution. The variable
is log-transformed.
Original source: Institute for Health Metrics and Evaluation.
When using this variable, please cite both EPI and the original source.
141

## Page 144

Year A vailability
 Country A vailability
3.16.31 Protected areas representativeness index (epi_par)
The PARI indicator measures ecological representativeness as the proportion of biologically scaled
environmental diversity included in a country’s terrestrial protected areas. The measure relies on
remote sensing, biodiversity informatics, and global modeling ofﬁne-scaled variation in biodiversity
composition for plant, vertebrate, and invertebrate species.
Original source: Commonwealth Scientiﬁc and Industrial Research Organization.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
142

## Page 145

3.16.32 Lead exposure (epi_pbd)
EPI measures lead exposure using the number of age-standardized disability-adjusted life-years lost
per 100,000 persons (DALY rate) due to lead contamination in the environment. The variable is
log-transformed.
Original source: Institute for Health Metrics and Evaluation.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.33 PM2.5 exposure (epi_pmd)
Ambient particulate matter pollution measured with the number of age-standardized disability-
adjusted life-years lost per 100,000 persons (DALY rate) due to exposure toﬁne air particulate
matter smaller than 2.5 micrometers (PM2.5). The variable is log-transformed.
Original source: Institute for Health Metrics and Evaluation Transformation.
When using this variable, please cite both EPI and the original source.
143

## Page 146

Year A vailability
 Country A vailability
3.16.34 SO2 growth rate (epi_sda)
The SO2 growth rate is calculated as the average annual rate of increase or decrease in SO2 over
the years 2005-2014. It is then adjusted for economic trends to isolate change due to policy rather
than economicﬂuctuation.
Original source: Community Emissions Data Systems.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.35 Species habitat index (epi_shi)
Species Habitat Index (SHI) estimates potential population losses, as well as regional and global
extinction risks of individual species, using habitat loss as a proxy. The SHI indicator measures the
144

## Page 147

proportion of suitable habitat within a country that remains intact for each species in that country
relative to a baseline set in the year 2001.
Original source: Map of Life.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.36 Sustainable nitrogen management index (epi_snm)
The Sustainable Nitrogen Management Index (SNMI) seeks to balance eﬃcient application of nitro-
gen fertilizer with maximum crop yields as a measure of the environmental performance of agricul-
tural production. The 2020 EPI uses the SNMI as a proxy for agricultural drivers of environmental
damage.
Original source: UMCES.
When using this variable, please cite both EPI and the original source.
145

## Page 148

Year A vailability
 Country A vailability
3.16.37 Species protection index (epi_spi)
Species Protection Index (SPI) evaluates the species-level ecological representativeness of each
country’s protected area network. The SPI metric uses remote sensing data, global biodiversity
informatics, and integrative models to map suitable habitat for over 30,000 terrestrial vertebrate,
invertebrate, and plant species at high resolutions. The unit of measurement is percentage.
Original source: Map of Life.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
146

## Page 149

3.16.38 Terrestrial biome protection (Global weights) (epi_tbg)
EPI derives the terrestrial biome protection indicators byﬁrst calculating the proportions of the
area of each of a country’s biome types that are covered by protected areas and then constructing
a weighted sum of the protection percentages for all biomes within that country. For the terrestrial
biome protection (global weights) indicator, protection percentages are weighted according to the
global prevalence of each biome type. This indicator evaluates a country’s contribution toward the
global 17% protection goal.
Original source: World Database on Protected Areas.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.39 Terrestrial biome protection (National weights) (epi_tbn)
EPI derives the terrestrial biome protection indicators byﬁrst calculating the proportions of the
area of each of a country’s biome types that are covered by protected areas and then constructing
a weighted sum of the protection percentages for all biomes within that country. For the terrestrial
biome protection (national weights) indicator, protection percentages are weighted according to the
prevalence of each biome type within that country. This indicator evaluates a country’s eﬀorts to
achieve 17% protection for all biomes within its borders, as per Aichi Target 11.
Original source: World Database on Protected Areas.
When using this variable, please cite both EPI and the original source.
147

## Page 150

Year A vailability
 Country A vailability
3.16.40 Tree cover loss (epi_tcl)
EPI quantiﬁes tree cover loss by constructing aﬁve-year moving average of the percentage of forest
lost from the extent of forest cover in the reference year 2000. A forest is deﬁned as any land area
with over 30% canopy cover. The variable is log-transformed.
Original source: Global Forest Watch.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.41 Unsafe sanitation (epi_usd)
EPI measures unsafe sanitation using the number of age-standardized disability-adjusted life-years
lost per 100,000 persons (DALY rate) due to their exposure to inadequate sanitation facilities. The
148

## Page 151

variable is log-transformed.
Original source: Institute for Health Metrics and Evaluation.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.42 Unsafe drinking water (epi_uwd)
EPI measures unsafe drinking water using the number of age-standardized disability-adjusted life-
years lost per 100,000 persons (DALY rate) due to exposure to unsafe drinking water. The variable
is log-transformed.
Original source: Institute for Health Metrics and Evaluation.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
149

## Page 152

3.16.43 Waste Management Issue Category (epi_wmg)
Waste Management Issue Category consists of the indicator Controlled Solid Waste, which refers
to the proportion of household and commercial waste generated in a country that is collected and
treated in a manner that controls environmental risks. This metric counts waste as "controlled" if
it is treated through recycling, composting, anaerobic digestion, incineration, or disposed of in a
sanitary landﬁll. The issue category varies from 0 to 100.
Year A vailability
 Country A vailability
3.16.44 Water Resources Issue Category (epi_wrs)
Water Resources Issue Category consists of the indicator Wastewater Treatment, which measures
the percentage of wastewater that undergoes at least primary treatment, normalized by the pro-
portion of the population connected to a municipal wastewater collection system. It is calculated
through a straightforward product of wastewater treatment level and sewerage connection rate.
The issue category varies from 0 to 100.
Year A vailability
 Country A vailability
150

## Page 153

3.16.45 Wetland loss (epi_wtl)
Wetland loss is quantiﬁed using aﬁve-year moving average of percentage of gross losses in wetland
areas compared to the 1992 reference year. The variable is log-transformed according to the formula
ln(x+α), whereα= 2.47E-06.
Original source: European Space Agency.
When using this variable, please cite both EPI and the original source.
Year A vailability
 Country A vailability
3.16.46 Wastewater treatment (epi_wwt)
The percentage of wastewater that undergoes at least primary treatment in each country, normalized
by the proportion of the population connected to a municipal wastewater collection system.
Original source: UNSD, OECD, Eurostat, etc.
When using this variable, please cite both EPI and the original source.
151

## Page 154

Year A vailability
 Country A vailability
152

## Page 155

3.17 Environmental Policy Stringency Index
Dataset by:Organisation for Economic Co-operation and Development
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Botta, Enrico and Tomasz Kozluk. 2014. “Measuring environmental policy stringency in
OECD countries: A composite index approach”.OECD Economics Department Working Pa-
pers, No. 1177, OECD Publishing
Link to the original source:https://www.oecd.org/economy/growth/Do-environmental-policies-
matter-for-productivity-growth.htm
The OECD Environmental Policy Stringency Index (EPS) is a country-speciﬁc and internationally-
comparable measure of the stringency of environmental policy.
3.17.1 Environmental Policy Stringency Index (oecd_eps)
The index measures the degree to which environmental policies put an explicit or implicit price
on polluting or environmentally harmful behaviour. The index ranges from 0 (not stringent) to
6 (highest degree of stringency) and is based on the degree of stringency of 14 environmental
policy instruments, both market-based and non-market-based, primarily related to climate and
air pollution. These policy instruments include environmental taxes on SOx, NOx, diesel, and
CO2; trading schemes in CO2; renewable energy and energy eﬃciency certiﬁcates; feed-in tariﬀs on
solar and wind energy; deposit and refund schemes; emission limit values on NOx, SOx, PMx and
sulphur content limits in diesel, as well as government expenditure on research and development
within renewable energy.
153

## Page 156

Year A vailability
 Country A vailability
154

## Page 157

3.18 Environmental Protection Expenditure Accounts (EPEA)
Dataset by:Organisation for Economic Co-operation and Development
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Organisation for Economic Co-operation and Development (OECD). 2020.Environmen-
tal protection expenditure account (EPEA).url:https://ec.europa.eu/eurostat/web/
products-manuals-and-guidelines/-/KS-GQ-17-004
Link to the original source:https://ec.europa.eu/eurostat/web/products-manuals-and-guidelines/-
/KS-GQ-17-004
The Environmental Protection Expenditure Account (EPEA) is a monetary description of environ-
mental protection activities in accordance with the System of Environmental-Economic Accounting
(SEEA) central framework. It is coherent with the European System of Accounts (ESA 2010) which
applies to national accounts and related satellite accounts.
3.18.1 Environmnnetal Protection Expenditure Accounts (EPEA) (oecd_epea)
National environmental protection activities in terms of millions in national currency expenditure.
This includes all activities with the main purpose of preventing, reducing, or eliminating pollution
as well as any other form of environmental degradation.
The EPEA aim to describe all national transactions related to environmental protection, with the
purpose of constructing a measure of the national environmental protection expenditure which can
be related to, for instance, gross domestic product, in order to assess the importance of these
activities as a share of total production. The EPEA show which economic sectors contribute to
environmental protection expenditure, both from the producers’ side, as from the users’ and the
ﬁnancing side.
This data focuses on the production and uses of environmental protection services. Output of these
services can be output of market, non-market, and ancillary activities. EPEA is directly linked to
the three deﬁnitions of GDP: the production measure, the expenditure measure, and the income
measure.
EPEA covers (1) expenditure on environmental protection (EP) products by resident units; (2)
expenditure related to the production of EP products, including the gross capital formation, and
(3) transactions related to theﬁnancing of EP expenditure.
155

## Page 158

Year A vailability
 Country A vailability
156

## Page 159

3.19 Environmentally Adjusted Multifactor Productivity
Dataset by:Organisation for Economic Co-operation and Development
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Organisation for Economic Co-operation and Development (OECD). 2020.Environmentally
adjusted multifactor productivity.url:oe.cd/eamfp
Rodríguez, Miguel Cárdenas, Ivan Hai, and Martin Souchier. 2018. “Environmentally adjusted
multifactor productivity: methodology and empirical results for OECD and G20 countries”.
Ecological Economics. 153
Link to the original source:https://www.oecd.org/environment/indicators-modelling-outlooks/
greening-productivity-measurement.htm
Environmentally adjusted multifactor productivity (EAMFP) takes into account the reliance of
national economies on natural resources and national eﬀorts to mitigate environmental damage.
3.19.1 Environmentally adjusted multifactor productivity growth (oecd_eampg)
EAMFP measures a country’s ability to generate income from a given set of inputs, while accounting
for the consumption of natural resources and production of undesirable environmental by-products.
It corresponds to the share of pollution-adjusted output growth that is not explained by changes
in the use of inputs (residual growth).
EAMFP growth therefore measures the residual growth in the joint production of both the desirable
and the undesirable outputs that cannot be explained by changes in the consumption of factor inputs
(including labour, produced capital, and natural capital). Therefore, for a given growth of input
use, EAMFP increases when GDP increases or when pollution decreases.
157

## Page 160

Year A vailability
 Country A vailability
3.19.2 Pollution-adjusted GDP growth (oecd_polagdpg)
Pollution-adjusted GDP growth measures to what extent a country’s GDP growth should be cor-
rected for pollution abatement eﬀorts - adding what has been undervalued due to resources being
diverted to pollution abatement, or deducing the "excess" growth which is generated at the expense
of environmental quality.
Year A vailability
 Country A vailability
158

## Page 161

3.20 European Social Survey - Wave 1-9
Dataset by:European Social Survey
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
NSD - Norwegian Centre for Research Data. 2020.European Social Survey Cumulative File,
ESS 1-9.Dataﬁle edition 1.0.url:http://www.europeansocialsurvey.org/
Link to the original source:http://www.europeansocialsurvey.org/data/round-index.html
The European Social Survey (ESS) is an academically-driven multi-country survey, which has been
administered in over 30 countries to date. Its three aims are:ﬁrst - to monitor and interpret chang-
ing public attitudes and values within Europe and to investigate how they interact with Europe’s
changing institutions; second - to advance and consolidate improved methods of cross-national
survey measurement in Europe and beyond; and third - to develop a series of European social
indicators, including attitudinal indicators.
This dataset includes two types of variables: 1) percentage of respondents choosing a particular
response option, and 2) average response per country, weighted using design weights (dweight), as
recommended by the ESS.
3.20.1 Climate policy support: bans (mean) (ess_banhhap_m)
A verage reply to D30-32: "To what extent are you in favour or against the following policies in
[country] to reduce climate change? A law banning the sale of the least energy-eﬃcient household
appliances". (1) Strongly in favor, (2) Somewhat in favor, (3) Neither in favor nor against, (4)
Somewhat against, (5) Strongly against. Answers (7) Refusal and (8) Don’t know are deleted.
A higher score means that there is a higher aversion towards the proposed ban in the general
population. A lower score means that there is a higher support towards the ban in the general
population.
159

## Page 162

Year A vailability
 Country A vailability
3.20.2 Belief that climate change is natural (%) (ess_ccnthum_p)
Percent of replies "(1) Entirely by natural processes" and "(2) Mainly by natural processes" to
D22: "Do you think that climate change is caused by natural processes, human activity, or both?".
(1) Entirely by natural processes, (2) Mainly by natural processes, (3) About equally by natural
processes and human activity, (4) Mainly by human activity, (5) Entirely by human activity, (55)
I don’t think climate change is happening, (77) Refusal, (88) Don’t know. A higher score means
that there are more people who believe that climate change is happening due to natural rather than
human-induced causes. A lower score means that there are fewer people who believe that these are
natural processes that are behind climate change.
Year A vailability
 Country A vailability
160

## Page 163

3.20.3 Personal responsibility to reduce climate change (mean) (ess_ccrdprs_m)
A verage reply to D23: "To what extent do you feel a personal responsibility to try to reduce climate
change?". (00) Not at all - (10) A great deal. Answers (77) Refusal and (88) Don’t know are deleted.
The higher the score the more people feel personal responsibility for reducing climate change. The
lower the score the fewer people feel personal responsibility for reducing climate change.
Year A vailability
 Country A vailability
3.20.4 Climate change denial (%) (ess_clmchng_p)
Percent of replies "(3) Probably not changing" and "(4) Deﬁnitely not changing" to D19: "You
may have heard the idea that the world’s climate is changing due to increases in temperature over
the past 100 years. What is your personal opinion on this? Do you think the world’s climate
is changing?". (1) Deﬁnitely changing, (2) Probably changing, (3) Probably not changing, (4)
Deﬁnitely not changing, (7) Refusal, (8) Don’t know. A higher score means that more people
believe that the climate is not changing. A lower score means that more people believe that the
climate is changing.
161

## Page 164

Year A vailability
 Country A vailability
3.20.5 Thinking about climate change (mean) (ess_clmthgt_m)
A verage reply to D20 and D21: "How much have you thought about climate change before today?".
(1) Not at all, (2) Very little, (3) Some, (4) A lot, (5) A great deal. Answers (7) Refusal and (8)
Don’t know are deleted.
D20 was only asked to those who replied "(4) Deﬁnitely not changing" to question D19 "Do you
think climate is changing?". D21 is the same question but was asked to everyone else. In this
dataset, we combined the replies for D20 and D21 before taking an average. A higher score means
that a larger part of the population thought about climate change prior to the survey. A lower score
means that a smaller part of the population thought about climate change prior to the survey.
Year A vailability
 Country A vailability
162

## Page 165

3.20.6 Belief in climate action: governments (mean) (ess_gvsrdcc_m)
A verage reply to D28: "And how likely do you think it is that governments in enough countries will
take action that reduces climate change?". (00) Not likely at all - (10) Extremely likely. Answers
(77) Refusal and (88) Don’t know are deleted. A higher score means that larger parts of the
population believe that enough governments will take action towards climate change. A lower score
means that fewer people believe that enough governments will take action towards climate change.
Year A vailability
 Country A vailability
3.20.7 Important to care for the environment (mean) (ess_impenv_m)
A verage reply to CARD 76: "Now I will brieﬂy describe some people. Please listen to each descrip-
tion and tell me how much each person is or is not like you. Use this card for your answer;
She/he strongly believes that people should care for nature. Looking after the environment is
important to her/him".
(1) Very much like me
(2) Like me
(3) Somewhat like me
(4) A little like me
(5) Not like me
(6) Not like me at all
Answers "Don’t know" are deleted. A higher score means that fewer people think that it is important
to care about nature/environment. A lower score means that more people think that it is important
to care about nature/environment.
163

## Page 166

Year A vailability
 Country A vailability
3.20.8 Climate policy support: taxes (mean) (ess_inctxﬀ_m)
A verage reply to D30-32: "To what extent are you in favour or against the following policies in
[country] to reduce climate change? Increasing taxes on fossil fuels, such as oil, gas and coal".(1)
Strongly in favor, (2) Somewhat in favor, (3) Neither in favor nor against, (4) Somewhat against,
(5) Strongly against. Answers (7) Refusal and (8) Don’t know are deleted. A higher score means
that the aversion towards a fossil fuel tax is higher in the population. A lower score means that
there is more support towards a fossil fuel tax in the population.
Year A vailability
 Country A vailability
3.20.9 Belief in climate action: individuals (mean) (ess_lklmten_m)
A verage reply to D27: "How likely do you think it is that large numbers of people will actually limit
their energy use to try to reduce climate change?". (00) Not likely at all - (10) Extremely likely.
Answers (77) Refusal and (88) Don’t know are deleted. A higher score means that more people
164

## Page 167

believe that a large number of people are likely to limit energy consumption to reduce climate
change. A lower score means that fewer people believe that a large number of people are likely to
reduce energy consumption to reduce climate change.
Year A vailability
 Country A vailability
3.20.10 Climate policy support: subsidies (mean) (ess_sbsrnen_m)
A verage reply to D30-32: "To what extent are you in favour or against the following policies in
[country] to reduce climate change? Using public money to subsidise renewable energy such as
wind and solar power". (1) Strongly in favor, (2) Somewhat in favor, (3) Neither in favor nor
against, (4) Somewhat against, (5) Strongly against. Answers (7) Refusal and (8) Don’t know are
deleted. A higher score means that there is more aversion in the population towards government
subsidies towards renewable energy. A lower score means that there is more support for renewable
energy subsidies.
Year A vailability
 Country A vailability
165

## Page 168

3.20.11 Worry about climate change (mean) (ess_wrclmch_m)
A verage reply to D24: "How worried are you about climate change?". (1) Not at all worried, (2)
Not very worried, (3) Somewhat worried, (4) Very worried, (5) Extremely worried. Answers (7)
Refusal and (8) Don’t know are deleted. A higher score means that there is a higher degree of
worry in the population about climate change. A lower score means that there is less worry in the
population about climate change.
Year A vailability
 Country A vailability
166

## Page 169

3.21 Exposure to PM2.5 in Countries and Regions
Dataset by:Organisation for Economic Co-operation and Development
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Organisation for Economic Co-operation and Development (OECD). 2020.Exposure to
PM2.5 in countries and regions (Edition 2018).url:https://www.oecd- ilibrary.org/
environment/data/oecd-environment-statistics_env-data-en
Shaddick, Gavin et al. 2018. “Data integration for the assessment of population exposure
to ambient air pollution for global burden of disease assessment”.Environmental Science &
Technology. 52. 16
Link to the original source:https://www.oecd-ilibrary.org/environment/data/oecd-environment-
statistics_env-data-en
The underlying PM2.5 concentration estimates are taken from the Global Burden of Disease (GBD)
2019 project. They are derived by integrating satellite observations, chemical transport models, and
measurements from ground monitoring station networks.
The concentration estimates are population-weighted using gridded population datasets from the
Joint Research Center Global Human Settlement project. These are produced by distributing
census-derived population estimates from the Gridded Population of the World, version 4 from the
NASA Socioeconomic Data and Applications Center according to the density and distribution of
built-up areas.
For political and administrative boundaries, OECD (2020) territorial grid units are used where
available, for the remaining countries, the F AO (2015) Global Administrative Unit Layers (GAUL
2014) are used (see below for details). The OECD (2020) Functional Urban Area deﬁnition is used
for cities.
The accuracy of these exposure estimates varies considerably by location. Accuracy is poorer in
areas with few monitoring stations and in areas with very high concentrations such as Africa, the
Middle-East and South Asia. Accuracy is generally good in regions with dense monitoring station
networks (such as most advanced economies). See Shaddick et al. (2018) for further details.
See Green Growth dataset for further measures of PM exposure.
167

## Page 170

3.21.1 Percentage of population exposed to more than 15µg/m3 of PM2.5 (oecd_-
pm25ex15p)
Percentage of population exposed to aﬁne particulate matter (PM2.5) concentration greater than
15 micrograms (µg) per cubic meter (m3).
The World Health Organization (WHO) provides air quality guidelines based on scientiﬁc evidence
and expert advice. 15µg/m3 is interim target-3. In addition to other health beneﬁts, these levels
reduce the mortality risk by approximately 6% [2-11%] relative to the IT-2 level (25µg/m3).
Year A vailability
 Country A vailability
3.21.2 Percentage of population exposed to more than 25µg/m3 of PM2.5 (oecd_-
pm25ex25p)
Percentage of population exposed to aﬁne particulate matter (PM2.5) concentration greater than
25 micrograms (µg) per cubic meter (m3).
WHO provides air quality guidelines based on scientiﬁc evidence and expert advice. 25µg/m3
is interim target-2: In addition to other health beneﬁts, these levels lower the risk of premature
mortality by approximately 6% [211%] relative to the IT-1 level (35µg/m3). Data on exposure to
more than 35µg/m3 is included in the Green Growth dataset.
168

## Page 171

Year A vailability
 Country A vailability
169

## Page 172

3.22 Global Footprint Data
Dataset by:Global Footprint Network
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Global Footprint Network. 2019.National Footprint and Biocapacity Accounts (1961-2016),
2019 Edition.url:https://data.footprintnetwork.org
Link to the original source:http://www.footprintnetwork.org/en/index.php/GFN/page/footprint_
data_and_results/
The National Footprint Accounts (NF As) measure the ecological resource use and resource ca-
pacity of nations over time. Based on approximately 15,000 data points per country per year, the
Accounts calculate the Footprints of 232 countries, territories, and regions from 1961 to the present,
providing the core data needed for all Ecological Footprint analysis worldwide.
3.22.1 Total Biocapacity (gha per capita) (ef_bcpc)
Total biocapacity divided by the population size. Units are global hectares (gha) per capita.
Year A vailability
 Country A vailability
170

## Page 173

3.22.2 Total Biocapacity (total gha) (ef_bct)
Biocapacity is the capacity of ecosystems to regenerate what people demand from those surfaces.
It is an aggregate measure of the amount of area available, weighted by the productivity of that
area. It represents the ability of a biosphere to produce crops, livestock (pasture), timber products
(forest) and seafood as well as the biosphere’s ability to uptake CO2 in forests. It also measures
how much of this regenerative capacity is occupied by infrastructure (built-up land). In essense,
it measures the ability of the available terrestrial and aquatic areas to provide ecological services.
The units are global hectares.
Year A vailability
 Country A vailability
3.22.3 Built-up land footprint of consumption (gha per person) (ef_bul)
The built-up land footprint is calculated based on the area of land covered by human infrastructure:
transportation, housing, and industrial structures. Built-up land may occupy what would previously
have been cropland. Measured in global hectares (gha) per person.
Year A vailability
 Country A vailability
171

## Page 174

3.22.4 Built-up land biocapacity per capita (ef_bul_bc)
Built-up land biocapacity measures how much of the regenerative capacity is occupied by infrastruc-
ture (built-up land). Regenerative capacity is an aggregate measure of the amount of area available,
weighted by the productivity of that area. It represents the ability of a biosphere to produce crops,
livestock (pasture), timber products (forest) and seafood as well as the biosphere’s ability to uptake
CO2 in forests. The measure of built-up land biocapacity is divided by the population size.
Year A vailability
 Country A vailability
3.22.5 Built-up land footprint of production (gha per person) (ef_bulp)
The countrys built-up area (roads, factories, cities), divided by the population size. The measure-
ment units are global hectares (gha) per person.
Year A vailability
 Country A vailability
172

## Page 175

3.22.6 Carbon footprint of consumption (gha per person) (ef_carb)
The carbon footprint represents the carbon dioxide emissions from burning fossil fuels in addition
to the embodied carbon in imported goods. The carbon Footprint component is represented by the
area of forest land required to sequester these carbon emissions. Currently, the carbon footprint is
the largest portion of humanity’s footprint.
Year A vailability
 Country A vailability
3.22.7 Carbon biocapacity per capita (ef_carb_bc)
The biospheres ability to uptake CO2, divided by the population size.
Year A vailability
 Country A vailability
173

## Page 176

3.22.8 Carbon footprint of production (gha per person) (ef_carbp)
The area needed to absorb all fossil fuel carbon emissions generated within the country, divided by
the population size. The measurement units are global hectares (gha) per capita.
Year A vailability
 Country A vailability
3.22.9 Cropland footprint of consumption (gha per person) (ef_crop)
Cropland is the most bioproductive of all the land-use types and consists of areas used to produce
food andﬁbre for human consumption, feed for livestock, oil crops, and rubber. The cropland
Footprint includes crop products allocated to livestock and aquaculture feed mixes, and those used
forﬁbres and materials. Due to lack of globally consistent data sets, current cropland Footprint
calculations do not yet take into account the extent to which farming techniques or unsustainable
agricultural practices may cause long-term degradation of soil.
Year A vailability
 Country A vailability
174

## Page 177

3.22.10 Cropland biocapacity per capita (ef_crop_bc)
The ability of a biosphere to produce crops (the total cropland area available, weighted by the
productivity of this area), divided by the population size.
Year A vailability
 Country A vailability
3.22.11 Cropland footprint of production (gha per person) (ef_cropp)
The area within a country necessary for supporting the harvest of primary products on the cropland.
The indicator is divided by the population size and is measured in global hectares (gha) per capita.
Year A vailability
 Country A vailability
175

## Page 178

3.22.12 Total Ecological Footprint of Consumption (gha per person) (ef_ef)
Total ecological footprint of consumption divided by the population size. Measured in global
hectares (gha) per person.
Year A vailability
 Country A vailability
3.22.13 Total Ecological Footprint of Production (gha per person) (ef_efp)
Ecological footprint of production divided by the population size. The units are global hectares
(gha) per capita.
Year A vailability
 Country A vailability
176

## Page 179

3.22.14 Total Ecological Footprint of Consumption (total area) (ef_eft)
The total ecological footprint of consumption is measured in global hectares (gha) and includes the
area needed to produce the materials consumed and the area needed to absorb the carbon dioxide
emissions. The consumption Footprint of a nation is calculated as a nation’s primary production
Footprint plus the Footprint of imports minus the Footprint of exports.
For example, if a country grows cotton for export, the ecological resources required are not included
in that country’s consumption Footprint. Rather, they are included in the consumption Footprint
of the country that imports the T-shirts. However, these ecological resources are included in the
exporting country’s primary production Footprint.
Year A vailability
 Country A vailability
3.22.15 Total Ecological Footprint of Production (total area) (ef_eftp)
A nation’s productive footprint is the sum of the footprints for all of the resources harvested and
all of the waste generated within the deﬁned geographical region. This includes all the area within
a country necessary for supporting the actual harvest of primary products (cropland, pasture land,
forestland, andﬁshing grounds), the countrys built-up area (roads, factories, cities), and the area
needed to absorb all fossil fuel carbon emissions generated within the country. If a country grows
a crop for export, it is included in the ecological footprint of production of this country and the
ecological footprint of consumption of the importing country. The indicator is measured in global
hectares (gha).
177

## Page 180

Year A vailability
 Country A vailability
3.22.16 Fish footprint of consumption (gha per person) (ef_fg)
Theﬁshing grounds Footprint is calculated based on estimates of the maximum sustainable catch
for a variety ofﬁsh species. These sustainable catch estimates are converted into an equivalent
mass of primary production based on the various species’ trophic levels. This estimate of maximum
harvestable primary production is then divided amongst the continental shelf areas of the world.
Fish caught and used in aquaculture feed mixes are included. Measured in global hectares (gha)
per person.
Year A vailability
 Country A vailability
3.22.17 Fishing ground biocapacity per capita (ef_fg_bc)
The ability of a biosphere to produce seafood (the amount ofﬁshing grounds available, weighted
by the productivity ofﬁshing grounds). The measure is divided by the population size.
178

## Page 181

Year A vailability
 Country A vailability
3.22.18 Fish footprint of production (gha per person) (ef_fgp)
The area within a country necessary for supporting the harvest of primary products onﬁshing
grounds. The indicator is divided by the population size and is measured in global hectares (gha)
per capita.
Year A vailability
 Country A vailability
3.22.19 Forest product footprint of consumption (gha per person) (ef_for)
The forest product Footprint is calculated based on the amount of lumber, pulp, timber products,
and fuel wood consumed by a population on a yearly basis. Measured in global hectares (gha) per
person.
179

## Page 182

Year A vailability
 Country A vailability
3.22.20 Forest land biocapacity per capita (ef_for_bc)
The ability of a biosphere to produce timber products (the total forest area available, weighted by
the productivity of this area), divided by the population size.
Year A vailability
 Country A vailability
3.22.21 Forest product footprint of production (gha per person) (ef_forp)
Forest Footprint represents the area necessary to regenerate all the timber harvested (hence, de-
pending on harvest rates, this area can be bigger or smaller than the forest area that exists within
the country). The indicator is divided by the population size and measured in global hectares (gha)
per person.
180

## Page 183

Year A vailability
 Country A vailability
3.22.22 Grazing footprint of consumption (gha per person) (ef_gl)
Grazing land is used to raise livestock for meat, dairy, hide, and wool products. The grazing land
Footprint is calculated by comparing the amount of livestock feed available in a country with the
amount of feed required for all livestock in that year, with the remainder of feed demand assumed
to come from grazing land. Measured in global hectares (gha) per person.
Year A vailability
 Country A vailability
3.22.23 Grazing land biocapacity per capita (ef_gl_bc)
The ability of a biosphere to produce pasture lands (the total pasture area available, weighted by
the productivity/yield of these pastures), divided by the population size.
181

## Page 184

Year A vailability
 Country A vailability
3.22.24 Grazing footprint of production (gha per person) (ef_glp)
The area within a country necessary for supporting the harvest of primary products on pastures.
The indicator is divided by the population size and measured in global hectares (gha) per person.
Year A vailability
 Country A vailability
182

## Page 185

3.23 Green Growth
Dataset by:Organisation for Economic Co-operation and Development
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Organisation for Economic Co-operation and Development (OECD). 2020.Green Growth
Indicators Database.url:https://stats.oecd.org/
Link to the original source:https://stats.oecd.org/
The OECD Green Growth database contains selected indicators for monitoring progress towards
green growth to support policy making and inform the public at large. The database synthesises
data and indicators across a wide range of domains including a range of OECD databases as well
as external data sources. The database covers OECD member and accession countries, key part-
ners (including Brazil, China, India, Indonesia and South Africa) and other selected non-OECD
countries. The indicators have been selected according to well-speciﬁed criteria and embedded in
a conceptual framework, which is structured around four groups to capture the main features of
green growth: (1) Environmental and resource productivity: indicate whether economic growth is
becoming greener with more eﬃcient use of natural capital and to capture aspects of production
which are rarely quantiﬁed in economic models and accounting frameworks; (2) The natural asset
base: indicate the risks to growth from a declining natural asset base; (3) Environmental dimension
of quality of life: indicate how environmental conditions aﬀect the quality of life and wellbeing of
people; (4) Economic opportunities and policy responses: indicate the eﬀectiveness of policies in
delivering green growth and describe the societal responses needed to secure business and employ-
ment opportunities.
3.23.1 Population connected to public sewerage, % total population (gg_asew_pop)
The percentage of the total population with access to public sewerage.
183

## Page 186

Year A vailability
 Country A vailability
3.23.2 Population connected to sewerage with primary treatment, % total population
(gg_asewp)
The percentage of the total population with access to public sewerage that includes a primary
treatment process.
Warning: this variable has some negative values, which falls outside the expected range for per-
centage variables. Check the original dataset for explanations or updates.
Year A vailability
 Country A vailability
3.23.3 Population connected to sewerage with secondary treatment, % total popu-
lation (gg_asews)
The percentage of the total population with access to public sewerage that includes a secondary
treatment process.
184

## Page 187

Year A vailability
 Country A vailability
3.23.4 Population connected to sewerage with tertiary treatment, % total population
(gg_asewt)
The percentage of the total population with access to public sewerage that includes a tertiary
treatment process.
Year A vailability
 Country A vailability
3.23.5 Built up area per capita (gg_buapc)
The number of square meters of built-up area per inhabitant (m2/person).
185

## Page 188

Year A vailability
 Country A vailability
3.23.6 Built up area, % total land (gg_buapt)
The built up area expressed as a percentage of total land area.
Year A vailability
 Country A vailability
3.23.7 Energy intensity , TPES per capita (gg_ei)
The energy intensity calculated as TPES (Total Primary Energy Supply) per capita (toe/person).
186

## Page 189

Year A vailability
 Country A vailability
3.23.8 Environmentally related government R&D budget, % total government R&D
(gg_envrd_gbaord)
Environmentally related government R&D budget measures government budget appropriations or
outlays for environmentally related research and development (R&D). It is expressed as a percentage
of total government R&D expenditure.
Year A vailability
 Country A vailability
3.23.9 Environmentally related R&D expenditure, % GDP (gg_envrd_gdp)
The environmentally related research and development (R&D) expenditure, expressed as a percent-
age of gross domestic product (GDP).
187

## Page 190

Year A vailability
 Country A vailability
3.23.10 Environmentally related ODA, % total ODA (gg_eoda)
The environmentally related Oﬃcial Development Assistance (ODA) expressed as a percentage of
total ODA.
Year A vailability
 Country A vailability
3.23.11 Energy public RD&D budget, % GDP (gg_erdgdp)
The public budget for energy related research, development, and demonstration as a percentage of
national gross domestic product (GDP).
188

## Page 191

Year A vailability
 Country A vailability
3.23.12 Development of environment-related technologies, % all technologies (gg_-
etp)
The number of environment-related inventions expressed as a percentage of all domestic inventions
(in all technologies).
Indicators of technology development are constructed by measuring inventive activity using patent
data across a wide range of environment-related technological domains (ENV-TECH, see link be-
low), including environmental management, water-related adaptation, and climate change mitiga-
tion technologies. The counts used here include only higher-value inventions (with patent family
size = 2).
Year A vailability
 Country A vailability
189

## Page 192

3.23.13 Development of environment-related technologies, % inventions worldwide
(gg_etpw)
The number of environment-related inventions expressed as a percentage of environment-related
inventions worldwide.
Indicators of technology development are constructed by measuring inventive activity using patent
data across a wide range of environment-related technological domains (ENV-TECH), including
environmental management, water-related adaptation, and climate change mitigation technologies.
The counts used here include only higher-value inventions (with patent family size = 2, meaning
inventionsﬁled in two or more jurisdictions).
Year A vailability
 Country A vailability
3.23.14 Fossil fuel public RD&D budget (excluding CCS), % total energy public
RD&D (gg_ﬀrd)
The public budget directed at research, development, and demonstration (RD&D) related to fossil
fuels, including oil, gas, and coal and excluding RD&D related to CO2 capture and storage (CCS),
expressed as a percentage of total energy RD&D public budgets (directed at all forms of energy).
190

## Page 193

Year A vailability
 Country A vailability
3.23.15 Forest resource stocks (gg_frs)
The growing stock of standing trees expressed in million cubic meters (m3).
Year A vailability
 Country A vailability
3.23.16 Forests under sustainable management certiﬁcation FSC, % total forest area
(gg_fsmc)
The share of forest area with a long-term management plan under the Forest Stewardship Council
(FSC) certiﬁcation expressed as a percentage of the total forest area.
191

## Page 194

Year A vailability
 Country A vailability
3.23.17 Intensity of use of forest resources (gg_iufr)
The intensity of use of forest resources measured as the ratio of actual fellings over annual productive
capacity (i.e. gross increment).
Year A vailability
 Country A vailability
3.23.18 Mortality from exposure to ambient ozone (gg_mao)
The mortality from exposure to ambient ozone expressed in deaths per million inhabitants.
192

## Page 195

Year A vailability
 Country A vailability
3.23.19 Mortality from exposure to lead (gg_ml)
The mortality from exposure to lead expressed in deaths per million inhabitants.
Year A vailability
 Country A vailability
3.23.20 Mortality from exposure to ambient PM2.5 (gg_mpm)
The mortality from exposure to ambient PM2.5 expressed in deaths per million inhabitants.
193

## Page 196

Year A vailability
 Country A vailability
3.23.21 Mortality from exposure to residential radon (gg_mr)
The mortality from exposure to residential radon expressed in deaths per million inhabitants.
Year A vailability
 Country A vailability
3.23.22 Municipal waste generated, kg per capita (gg_mwgpc)
The waste collected by or on behalf of municipalities expressed in kilograms (kg) per person.
194

## Page 197

Year A vailability
 Country A vailability
3.23.23 Municipal waste incinerated, % treated waste (gg_mwipt)
The municipal waste incinerated expressed as a percentage of all waste treated.
Year A vailability
 Country A vailability
3.23.24 Municipal waste disposed to landﬁlls, % treated waste (gg_mwlpt)
The municipal waste disposed to landﬁlls expressed as a percentage of all waste treated.
195

## Page 198

Year A vailability
 Country A vailability
3.23.25 Municipal waste recycled or composted, % treated waste (gg_mwrpt)
The municipal waste recycled or composted expressed as a percentage of all waste treated.
Year A vailability
 Country A vailability
3.23.26 ODA - all sectors - climate change mitigation, % total ODA (gg_oda_ccm)
The Oﬃcial Development Assistance (ODA) targeting climate change mitigation expressed as a
percentage of total ODA.
196

## Page 199

Year A vailability
 Country A vailability
3.23.27 Percentage of population exposed to more than 10µg/m3 of PM2.5 (gg_-
pm25ex10p)
The percentage of population exposed to aﬁne particulate matter (PM2.5) concentration greater
than 10 micrograms (µg) per cubic meter (m3).
The World Health Organization (WHO) provides air quality guidelines based on scientiﬁc evidence
and expert advice. 10µg/m3 is the air quality guideline (AQG): These are the lowest levels at
which total, cardiopulmonary and lung cancer mortality have been shown to increase with more
than 95% conﬁdence in response to long-term exposure to PM2.5.
Year A vailability
 Country A vailability
197

## Page 200

3.23.28 Percentage of population exposed to more than 35µg/m3 of PM2.5 (gg_-
pm25ex35p)
The percentage of population exposed to aﬁne particulate matter (PM2.5) concentration greater
than 35 micrograms (µg) per cubic meter (m3).
The World Health Organization (WHO) provides air quality guidelines based on scientiﬁc evidence
and expert advice. 35µg/m3 is interim target-1: These levels are associated with about a 15%
higher long-term mortality risk relative to the Air Quality Guideline (AQG) level, which is 10
µg/m3.
Year A vailability
 Country A vailability
3.23.29 Mean population exposure to PM2.5 (gg_pm25exm)
The average mirogram concentration ofﬁne particulate matter (PM2.5) per cubic meter exposed
to the population. This environmental and health hazard is measured by population-weighted
concentration estimates (See OECD dataset "Exposure to PM2.5 in countries and regions").
198

## Page 201

Year A vailability
 Country A vailability
3.23.30 Petrol tax, USD per litre (gg_pt)
The tax rates per litre of petrol expressed at constant 2015 US dollars using purchasing power
parity (PPP). The tax rates are calculated as the arithmetic average of the household excise tax
for the unleaded premium 95, unleaded premium 98, and unleaded regular petrol, and are deﬂated
using the Consumer Price Index.
Year A vailability
 Country A vailability
3.23.31 Renewable energy supply, % TPES (gg_re_tpes)
Renewable energy supply is deﬁned as the contribution of renewables to the total primary energy
supply (TPES).
199

## Page 202

Year A vailability
 Country A vailability
3.23.32 Renewable electricity , % total electricity generation (gg_reperegen)
The percentage of the national electrical supply generated from renewable sources.
Year A vailability
 Country A vailability
3.23.33 Renewable energy public RD&D budget, % total energy public RD&D (gg_-
rerd_erd)
The percentage of all public energy related research, development, and demonstration (RD&D)
that is directed towards renewable energy.
200

## Page 203

Year A vailability
 Country A vailability
3.23.34 Threatened bird species, % total known species (gg_tbs)
The number of threatened bird species expressed as a percentage of total known species within a
country.
Year A vailability
 Country A vailability
3.23.35 Threatened mammal species, % total known species (gg_tms)
The number of threatened mammal species expressed as a percentage of total known species within
a country.
201

## Page 204

Year A vailability
 Country A vailability
3.23.36 Threatened vascular plant species, % total known species (gg_tps)
The number of threatened vascular plant species expressed as a percentage of total known species
within a country.
Year A vailability
 Country A vailability
3.23.37 Water stress, total freshwater abstraction as % total available renewable
resources (gg_wsa)
The total freshwater abstraction as a percentage of available renewable sources, as a proxy for water
stress (scarcity). Abstraction refers to any process of water removal, extraction, or diversion for
human use. A higher percentage indicates greater water stress.
202

## Page 205

Year A vailability
 Country A vailability
3.23.38 Water stress, total freshwater abstraction as % total internal renewable
resources (gg_wsi)
The total freshwater abstraction as a percentage of available internal renewable sources, as a proxy
for water stress. Internal resources refer only to riverﬂows and groundwater from rainfall within
the country. Abstraction refers to any process of water removal, extraction, or diversion for human
use. A higher percentage, therefore, indicates greater water stress.
Year A vailability
 Country A vailability
203

## Page 206

3.24 International Environmental Agreements Database Project
Dataset by:International Environmental Agreements Database Project
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Mitchell, Ronald B. 2020.International Environmental Agreements Database Project (Version
2020.1).url:http://iea.uoregon.edu/
Mitchell, Ronald B et al. 2020. “What we know (and could know) about international envi-
ronmental agreements”.Global Environmental Politics. 20. 1
Link to the original source:https://iea.uoregon.edu/
International Environmental Agreements (IEA) include eﬀorts to regulate human interactions with
the environment that involve legally binding commitments ("agreements") among governments ("in-
ternational") that have environmental protection as a primary objective ("environmental").The IEAs
include:
- instruments designated as convention, treaty, agreement, accord, or their non-English equivalents,
and protocols and amendments to such instruments;
- instruments, regardless of designation, establishing intergovernmental commissions;
- instruments, regardless of designation, identiﬁed as binding by reliable sources (e.g., by a secre-
tariat, UNEP, or published legal analysis); or
- instruments, regardless of designation, whose textsﬁt accepted terminologies of legally-binding
agreements.
Intergovernmental "soft laws," such as action plans, agreed measures, codes of conduct, declarations,
resolutions, and similar policies that are not binding are excluded. European Union (EU) directives
are also excluded due to their unique status.
204

## Page 207

3.24.1 Number of IEAs entered into force for theﬁrst time (iead_eif1)
The number of international environmental agreements, amendments, and protocols that entered
into force for theﬁrst time (before any withdrawals), in the recorded year.
Year A vailability
 Country A vailability
3.24.2 Number of IEAs entered into force for the second time (iead_eif2)
The number of international environmental agreements, amendments, and protocols that entered
into force after theﬁrst withdrawal, in the recorded year.
Year A vailability
 Country A vailability
205

## Page 208

3.24.3 Number of IEAs entered into force for the third time (iead_eif3)
The number of international environmental agreements, amendments, and protocols that entered
into force after the second withdrawal, in the recorded year.
Year A vailability
 Country A vailability
3.24.4 Number of IEAs in force, counting terminated IEAs (iead_inforce)
The number of international environmental agreements, amendments, and protocols in force, in-
cluding international environmental agreements that have been terminated.
Year A vailability
 Country A vailability
206

## Page 209

3.24.5 Number of IEAs in force, not counting terminated IEAs (iead_inforce_-
noterm)
The number of international environmental agreements, amendments, and protocols in force, not
counting terminated international environmental agreements.
Year A vailability
 Country A vailability
3.24.6 Number of IEAs ratiﬁed per year (iead_rat)
The number of international environmental agreements, amendments, and protocols ratiﬁed in the
recorded year.
The users are encouraged to use "entry into force" instead of signatures and ratiﬁcations.
Year A vailability
 Country A vailability
207

## Page 210

3.24.7 Number of IEAs signed per year (iead_sig)
The number of international environmental agreements, amendments, and protocols signed in the
recorded year.
The data on signatures are incomplete. Signatures are fewer than ratiﬁcations or entry into force
because secretariats, e.g., the UN Treaty Series, often do not keep track of signatures. The users
are encouraged to use "entry into force" instead of signatures and ratiﬁcations.
Year A vailability
 Country A vailability
3.24.8 Number of terminated IEAs per year (iead_term)
The number of international environmental agreements, amendments, and protocols terminated in
the recorded year.
Year A vailability
 Country A vailability
208

## Page 211

3.24.9 Number ofﬁrst withdrawals from IEAs per year (iead_withdraw1)
The number ofﬁrst-time withdrawals from international environmental agreements, amendments,
and protocols in the recorded year.
Year A vailability
 Country A vailability
3.24.10 Number of second withdrawals from IEAs per year (iead_withdraw2)
The number of second-time withdrawals from international environmental agreements, amendments,
and protocols in the recorded year.
Year A vailability
 Country A vailability
209

## Page 212

3.25 Natural Resource Management Index Data
Dataset by:Natural Resource Management Index
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Center for International Earth Science Information Network - CIESIN - Columbia Univer-
sity. 2019.Natural Resource Protection and Child Health Indicators, 2019 Release.url:
https://doi.org/10.7927/r6mv-sv82
Link to the original source:http://sedac.ciesin.columbia.edu/data/collection/nrmi
The Natural Resource Protection and Child Health Indicators, 2019 Release, is produced in support
of the U.S. Millennium Challenge Corporation (MCC) as selection criteria for funding eligibility.
The Natural Resource Protection Indicator (NRPI) and Child Health Indicator (CHI) are based on
proximity-to-target scores ranging from 0 to 100 (at target). The NRPI covers 234 countries and is
calculated based on the weighted average percentage of biomes under protected status. The CHI is
a composite index for 195 countries derived from the average of three proximity-to-target scores for
access to at least basic water and sanitation, along with child mortality. The 2019 release includes
a consistent time series of NRPI scores for 2015 to 2019 and CHI scores for 2010 to 2018.
3.25.1 Natural Resource Protection Indicator (nrmi_nrpi)
Natural Resource Protection Indicator assesses whether a country is protecting at least 17% of
all of its biomes (e.g. deserts, forests, grasslands, aquatic, and tundra). It is designed to capture
the comprehensiveness of a government’s commitment to habitat preservation and biodiversity
protection. The World Wildlife Fund provides the underlying biome data, and the United Nations
Environment Program World Conservation Monitoring Center provides the underlying data on
protected areas.
210

## Page 213

Year A vailability
 Country A vailability
211

## Page 214

3.26 Oil and Gas Data, 1932-2014
Dataset by:Michael L Ross
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Ross, Michael and Paasha Mahdavi. 2015.Oil and Gas Data, 1932-2014.url:http :
//dx.doi.org/10.7910/DVN/ZTPW0Y
Link to the original source:https://dataverse.harvard.edu/dataset.xhtml?persistentId=
doi:10.7910/DVN/ZTPW0Y
Global dataset of oil and natural gas production, prices, exports, and net exports. These data
are based on the best available information about the volume and value of oil and natural gas
production in all countries from 1932 to 2014. The volumeﬁgures are from the documents listed in
the original source; to calculate the total value of production, the author multiplies the volume by
the world price for oil or gas. Since these are world prices for a single (benchmark) type of oil/gas,
they only approximate the actual price - which varies by country according to the quality, the terms
of contracts, the timing of the transactions, and other factors. Theseﬁgures do not tell how much
revenues were collected by governments or companies - only the approximate volume and value of
production. Data on oil production from 1946 to 1969, and gas production from 1955 (when itﬁrst
was reported) to 1969, are from the US Geological Survey Minerals Yearbook, for various years.
3.26.1 Gas exports, billion cubic feet per year (ross_gas_exp)
Gas exports, billion cubic feet per year.
212

## Page 215

Year A vailability
 Country A vailability
3.26.2 Net gas exports value, constant 2000 dollars (ross_gas_netexp)
Net gas exports value, measured in constant 2000 US dollars to adjust for inﬂation.
Year A vailability
 Country A vailability
3.26.3 Gas production, million barrels oil equiv. (ross_gas_prod)
Gas production measured in million barrels of oil equivalent.
213

## Page 216

Year A vailability
 Country A vailability
3.26.4 Gas production value in 2014 dollars (ross_gas_value_2014)
Gas production value in constant 2014 US dollars to adjust for inﬂation.
Year A vailability
 Country A vailability
3.26.5 Oil exports, thousands of barrels per day (ross_oil_exp)
Oil exports, thousands of barrels per day.
214

## Page 217

Year A vailability
 Country A vailability
3.26.6 Net oil exports value, constant 2000 dollars (ross_oil_netexp)
Net oil exports value measured in constant 2000 US dollars to adjust for inﬂation.
Year A vailability
 Country A vailability
3.26.7 Oil production in metric tons (ross_oil_prod)
Oil production in metric tons.
215

## Page 218

Year A vailability
 Country A vailability
3.26.8 Oil production value in 2014 dollars (ross_oil_value_2014)
Oil production value in constant 2014 US dollars to adjust for inﬂation.
Year A vailability
 Country A vailability
216

## Page 219

3.27 Policy Instruments for the Environment
Dataset by:Organisation for Economic Co-operation and Development
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Organisation for Economic Co-operation and Development (OECD). 2020.Policy Instru-
ments for the Environment (PINE).url:oe.cd/pine
Link to the original source:http://oe.cd/pine
Policy Instruments for the Environment (PINE) is originally developed by OECD in co-operation
with the European Environment Agency (EEA). The database contains detailed qualitative and
quantitative information on environmentally related taxes, fees and charges, tradable permits,
deposit-refund systems, environmentally motivated subsidies, and voluntary approaches used for
environmental policy.
The dataset covers OECD member countries, accession countries and selected non-OECD countries
since the year 1994, and it has been cross-validated and complemented with Revenue statistics from
the OECD Tax statistics database and oﬃcial national sources.
3.27.1 Climate change related tax revenue (% of GDP) (oecd_cctr_gdp)
Climate change-related tax revenue as a percentage of gross domestic product (GDP). Includes
taxes, fees and charges, tradable permits, deposit-refund systems, subsidies, and voluntary ap-
proaches related to the domain of climate change.
217

## Page 220

Year A vailability
 Country A vailability
3.27.2 Climate change related tax revenue (% of total tax revenue) (oecd_cctr_tot)
Climate change-related tax revenue as a percentage of total tax revenue. Includes taxes, fees and
charges, tradable permits, deposit-refund systems, subsidies, and voluntary approaches related to
the domain of climate change.
Year A vailability
 Country A vailability
3.27.3 Environmentally related tax revenue (% of GDP) (oecd_etr_gdp)
Total revenue gathered from environmentally-related taxes, fees, charges, tradable permits, deposit-
refund systems, environmentally motivated subsidies, and voluntary approaches used for environ-
mental policy, as a percent of gross domestic product (GDP). The tax bases covered include:
- Energy products (including vehicle fuels);
218

## Page 221

- Motor vehicles and transport services;
- Measured or estimated emissions to air and water, ozone depleting substances, certain non-point
sources of water pollution, waste management and noise, as well as management of water, land,
soil, forests, biodiversity, wildlife, andﬁsh stocks.
Year A vailability
 Country A vailability
3.27.4 Environmentally related tax revenue (% total tax revenue) (oecd_etr_tot)
Total revenue gathered from environmentally-related taxes, fees, charges, tradable permits, deposit-
refund systems, environmentally motivated subsidies, and voluntary approaches used for environ-
mental policy, as a percentage of total tax revenue.
The tax bases covered include:
- Energy products (including vehicle fuels);
- Motor vehicles and transport services;
- Measured or estimated emissions to air and water, ozone depleting substances, certain non-point
sources of water pollution, waste management and noise, as well as management of water, land,
soil, forests, biodiversity, wildlife, andﬁsh stocks.
219

## Page 222

Year A vailability
 Country A vailability
220

## Page 223

3.28 Stock of Climate Laws and Policies
Dataset by:Eskander and Fankhauser
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Eskander, S. and Fankhauser S. 2020. “Reduction in greenhouse gas emissions from national
climate legislation”.Nature Climate Change. 10.url:https://github.com/smsu1979/
Eskander-Fankhauser-NCC-2020-
Link to the original source:https://github.com/smsu1979/Eskander-Fankhauser-NCC-2020-
Data on the stock of climate change mitigation laws and policies used in the paper:
Eskander, S.M. and Fankhauser, S., 2020. Reduction in greenhouse gas emissions from national
climate legislation. Nature Climate Change, 10(8), pp.750-756.
Mitigation laws and policies refer to a legislative or executive disposition focused on curbing a
country’s greenhouse gases emissions in one sector or more. Measures can be directly related to
emissions reductions, such as laws establishing a national carbon budget or cap and trade system, or
indirectly related, such as laws or policies establishing relevant institutions or providing additional
funding for research and development into low carbon technologies. Laws and policies address-
ing forests and land use are included as long as they explicitly support climate change mitigation
through activities that reduce emissions and increase carbon removals. General forest management
and conservation laws are not included, even if they may have implicit consequences for climate
change mitigation.
3.28.1 Stock of executive orders/policies on mitigation for the past 3 years (slaws_-
mit_ex_l3)
Number of policies addressing climate mitigation that were enacted by the national executive branch
for the previous 3 years, rolling. These include presidential decrees, executive orders, or department
regulations.
221

## Page 224

Year A vailability
 Country A vailability
3.28.2 Stock of older executive orders/policies on mitigation (slaws_mit_ex_lt)
Number of policies addressing climate mitigation that were enacted by the national executive branch
until three years back, rolling. These policies include presidential decrees, executive orders, or
department regulations.
Year A vailability
 Country A vailability
3.28.3 Stock of mitigation laws and policies for the past 3 years (slaws_mit_l3)
Number of laws and policies addressing climate mitigation that were adopted by the national
government in the previous 3 years, rolling.
222

## Page 225

Year A vailability
 Country A vailability
3.28.4 Stock of legislative mitigation laws for the past 3 years (slaws_mit_leg_l3)
Number of laws addressing climate mitigation that were passed by the national legislature in the
previous three years, rolling. Laws are passed by the parliament, congress, or equivalent legislative
authority.
Year A vailability
 Country A vailability
3.28.5 Stock of older legislative mitigation laws (slaws_mit_leg_lt)
Total number of laws addressing climate mitigation that were passed by the national legislature
until three years back, rolling. Laws are passed by the parliament, congress, or equivalent legislative
authority.
223

## Page 226

Year A vailability
 Country A vailability
3.28.6 Stock of older mitigation laws and policies (slaws_mit_lt)
Total number of laws and policies addressing climate mitigation that were adopted by the national
government until three years back, rolling.
Year A vailability
 Country A vailability
224

## Page 227

3.29 Sustainable Governance Indicators
Dataset by:Bertelsmann Stiftung
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Schiller, Christof, Thorsten Hellmann, and Pia Paulini. 2020. “Sustainable Governance Indi-
cators 2020”.Bertelsmann Stiftung.url:https://www.sgi-network.org/2020/Downloads
Link to the original source:https://www.sgi-network.org/2020/
The Sustainable Governance Indicators (SGI) is a platform built on a cross-national survey of
governance that identiﬁes reform needs in 41 EU and OECD countries. SGI explores how govern-
ments target sustainable development and advocate for more sustainable governance built on three
pillars: 1) Policy Performance; 2) Democracy; and 3) Governance.
3.29.1 Environmental Policy Performance Index (sgi_en)
The index consists of two parts: Environment Index and Global Environmental Protection Index,
weighted equally. The variable varies between 0 and 10.
Year A vailability
 Country A vailability
225

## Page 228

3.29.2 Environmental Policy Performance - Environment (sgi_enen)
The Environment index consists of the "Environmental Policy" indicator (50%), based on expert
assessments of environmental policy eﬀectiveness, and nine indicators related to observable environ-
mental performance, including Energy Productivity (5,56%), Greenhouse Gas Emissions (5,56%),
Particulate Matter (5,56%), Biocapacity (5,56%), Waste Generation (5,56%), Material Recycling
(5,56%), Biodiversity (5,56%), Renewable Energy (5,56%), and Material footprint (5,56%). The
index varies from 0 to 10.
Year A vailability
 Country A vailability
3.29.3 Environmental Policy Performance - Global Environmental Protection (sgi_-
enge)
The Global Environmental Protection index consists of "Global Environmental Policy Indicator"
(50%), based on expert assessments of countries’ participation in global environmental protection
regimes, the rate of participation in Multilateral Environmental Agreements (25%), and Kyoto
Participation and Achievements indicator, measuring to what extent the Kyoto emission reduction
targets were met (25%). The index varies from 0 to 10.
226

## Page 229

Year A vailability
 Country A vailability
3.29.4 Environmental policy eﬀectiveness (sgi_epe)
The indicator measures how eﬀectively a national environmental policy protects and preserves the
sustainability of natural resources and the quality of the environment.
Eﬀective environmental policies will help promote and incentivize goal-driven technological progress
and environmentally friendly behavior and ensure suﬃcient resources are allocated for implemen-
tation. In assessing the eﬀectiveness of environmental policies, the experts were invited to draw on
the following guiding questions:
1. Are environmental policy goals ambitious (i.e., do they target more than improvements to
eﬃciency)?
2. Are environmental policies implemented with tangible impact?
3. Are environmental concerns integrated eﬀectively across relevant policy sectors (i.e., energy,
housing, transport, manufacturing industry, research and innovation, tourism,ﬁsheries, agricul-
ture)?
As environmental performance may be issue-speciﬁc, the experts were invited to provide a short
paragraph for each of the four key targets of protection: resource use (land, water, materials,
energy), environmental pollution (water, air, soil), climate and biodiversity protection."
The indicator is based on expert answers to these questions and varies from 0 to 10, where 0-1 is
"Environmental concerns have been largely abandoned" and 9-10 is "Environmental policy goals are
ambitious and eﬀectively implemented as well as monitored within and across most relevant policy
sectors that account for the largest share of resource use and emissions".
227

## Page 230

Year A vailability
 Country A vailability
3.29.5 Participation in global environmental regimes (sgi_ger)
The indicator measures the extent to which governments actively contribute to the design and
advancement of global environmental protection regimes.
Protecting the climate and preserving natural resources worldwide depends on eﬀective collective
action carried out on a global level. Examples of active contribution include demonstrating initiative
and responsibility, acting as an agenda-setter within international frameworks, and/or achieving an
alignment of purpose among conﬂicting interests in international negotiations.
The experts were invited to provide a paragraph addressing the following three aspects:
1. Which issues are treated as global common goods rather than domestic environmental problems
(e.g., chemical pollution, biodiversity conservation, forest protection, climate protection, etc.)?
2. Which of these global issues or goals does the government address, and has it formulated and
implemented action plans targeting these goals?
3. Are countries targeting the preservation of global common goods by contributing funds either
through international facilities or oﬃcial development assistance?"
The indicator is based on the expert answers to these questions and varies from 0 to 10, where 1-2
is "The government does not contribute to international eﬀorts to strengthen global environmental
protection regimes," and 9-10 is "The government actively contributes to international eﬀorts to
design and advance global environmental protection regimes. In most cases, it demonstrates com-
mitment to existing regimes, contributes to their being advanced and has introduced appropriate
reforms".
228

## Page 231

Year A vailability
 Country A vailability
229

## Page 232

3.30 The Environmental Democracy Index
Dataset by:The Access Initiative (TAI) and World Resources Institute (WRI)
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
World Resource Institute and the Access Initiative. 2015.Environmental Democracy Index.
url:https://environmentaldemocracyindex.org/
Link to the original source:https://www.environmentaldemocracyindex.org/node/12732.html
The Environmental Democracy Index measures the degree to which countries have enacted legally
binding rules that provide for environmental information collection and disclosure, public partic-
ipation across a range of environmental decisions, and fair, aﬀordable, and independent avenues
for seeking justice and challenging decisions that impact the environment. The index evaluates 70
countries across 75 legal indicators, based on objective and internationally recognized standards
established by the United Nations Environment Programmes (UNEP) Bali Guidelines. EDI also
includes a supplemental set of 24 limited practice indicators that provide insight on a country’s
performance in implementation.
3.30.1 Environmental Democracy Index (edi_edi)
EDI measures to which degree countries have enacted legally binding rules that provide for environ-
mental information collection and disclosure, public participation across a range of environmental
decisions, and fair, aﬀordable, and independent avenues for seeking justice and challenging decisions
that impact the environment.
It is an average of 3 pillars that measure:
1) the right to freely access information on environmental quality and problems (Access to infor-
mation pillar);
2) the right to participate meaningfully in decision-making (Participation pillar);
3) the right to seek enforcement of environmental laws or compensation for harm (Justice pillar).
The pillars are calculated by combining 75 legal indicators that are scored from 0 (worst) to 3
(best), producing an overall score that falls within this same range. The pillars are given equal
weight when creating an average.
230

## Page 233

Year A vailability
 Country A vailability
3.30.2 Aﬀordable access to relief and remedy (Guideline 20) (edi_gaarr)
The indicator measures to which extent states ensure that the access of members of the public
concerned to review procedures relating to the environment is not prohibitively expensive and to
which extent they consider the establishment of appropriate assistance mechanisms to remove or
reduceﬁnancial and other barriers to access to justice.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to
3 (best): (20.1) To what extent are there legal mechanisms in place to ensure that access to review
procedures relating to the environment for members of the public concerned is not prohibitively
expensive?; (20.2) To what extent does the law provide assistance mechanisms to reduceﬁnancial
barriers to access to justice?; (20.3) To what extent does the law provide assistance mechanisms to
reduce gender-related non-ﬁnancial barriers to access to justice?; (20.4) To what extent does the law
provide assistance mechanisms to reduce other non-ﬁnancial and non-gender barriers to access to
justice?; (P20.1) In the last 5 years, has a public interest case relating to the environment or natural
resources beenﬁled which was supported by government legal aid?; (P20.2) In the last 10 years, have
there been cases relating to the environment or natural resources where the costs of proceedings
was awarded against a public interest complainant/plaintiﬀ/petitioner (c/p/p)?; (P20.3) In the last
5 years have there been cases related to the environment or natural resources where the costs of
proceedings were awarded in favor of a public interest complainant/plaintiﬀ/petitioner (c/p/p)?
231

## Page 234

Year A vailability
 Country A vailability
3.30.3 Alternative dispute resolution for environmental issues (Guideline 26) (edi_-
gadrei)
The indicator measures to which extent the states encourage the development and use of alternative
dispute resolution mechanisms where these are appropriate. In scoring this indicator, alternate dis-
pute resolution mechanisms include mediation, conciliation, or arbitration adopted by institutions
as a means of resolving environmental disputes.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to
3 (best): (26.1) To what extent does the law provide for the possibility to use alternative dispute
resolution mechanisms to address violations of the right of access to environmental information,
public participation or cases of environmental harm?; (26.2) To what extent does the law provide
incentives for the use of alternative dispute resolution mechanisms where these are appropriate?;
(P26.1) In the last 5 years, has a public interest case relating to the environment or natural re-
sources been solved by an alternate conﬂict resolution method (such as mediation, arbitration and
conciliation)?
232

## Page 235

Year A vailability
 Country A vailability
3.30.4 Awareness and education about remedies and relief (Guideline 23) (edi_gaerr)
The indicator measures to which extent the states provide adequate information to the public about
the procedures operated by courts of law and other relevant bodies in relation to environmental
issues.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst)
to 3 (best): (23.1) To what extent does the law require the State or State agencies or institutions
to provide information to the public about court procedures relating to environmental issues?;
(23.2) To what extent does the law require the State or State agencies or institutions to provide
information to the public about review procedures relating to environmental issues provided by
bodies other than courts of law?; (P23.1) Is there an easily understandable explanation of court
procedures in the national language(s) on the website or oﬃce of the highest national court or the
apex national environmental agency?
Year A vailability
 Country A vailability
233

## Page 236

3.30.5 Accessibility of information requests (Guideline 1) (edi_gair)
The indicator measures the existence of a clear positive legal mandate that gives the public the
right to access environmental information upon request.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to 3
(best): (1.1) To what extent does the law mandate access to environmental information to be pro-
vided upon request?; (1.2) To what extent does the law provide for natural or legal persons’ access
to environmental information?; (1.3) To what extent does the law make access to environmental
information aﬀordable?; (1.4)To what extent does the law provide for timely access to environ-
mental information?; (1.5) To what extent does the law include public authorities under access to
environmental information provisions?; (1.6) To what extent does the law not require proof of legal
or other interest for access to environmental information?
Year A vailability
 Country A vailability
3.30.6 Due account of public comments (Guideline 11) (edi_gapc)
The indicator measures to which extent the states ensure that due account is taken of the comments
of the public in the decision-making process and that the decisions are made public.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to 3
(best): (11.1) To what extent do the laws concerning environmental impact assessments, pollution
control standards and permits, forest concessions, extractive industries, biodiversity and terrestrial
protected areas, and environmental policy-making require the State or State agencies at the national
level to take due account of the public’s comments in decision-making relating to the environment?;
(11.2) To what extent do the laws concerning environmental impact assessments, pollution control
standards and permits, forest concessions, extractive industries, biodiversity and terrestrial pro-
tected areas, and environmental policy-making require that decisions relating to the environment
are made public?; (P11.1) In the three most recent large-scale extractive or development projects,
did the relevant agency respond to public comments on the environmental impact assessment and
make the responses available to the public?
234

## Page 237

Year A vailability
 Country A vailability
3.30.7 Broad standing (Guideline 18) (edi_gbs)
The indicator measures to which extent the states provide broad interpretation of standing in
proceedings concerned with environmental matters with a view to achieving eﬀective access to
justice.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to 3
(best): (18.1) To what extent does the law recognize broad legal standing in proceedings concerned
with environmental matters?; (P18.1) In the last 5 years, have NGOs been granted legal standing
by national courts in public interest environmental cases?
Year A vailability
 Country A vailability
235

## Page 238

3.30.8 Eﬀective enforcement (Guideline 22) (edi_gee)
The indicator measures to which extent the states ensure the timely and eﬀective enforcement of
decisions in environmental matters taken by courts of law and by administrative and other relevant
bodies.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to
3 (best): (22.1) To what extent does the law provide for the eﬀective enforcement of criminal court
decisions relating to the environment?; (22.2) To what extent does the law require the enforcement
of criminal court decisions relating to the environment to be timely?; (22.3) To what extent does
the law provide for the eﬀective enforcement of civil court decisions relating to the environment?;
(22.4) To what extent does the law require the enforcement of civil court decisions relating to the
environment to be timely?; (22.5) To what extent does the law provide for eﬀective enforcement
of decisions relating to the environment taken by administrative and other relevant bodies?; (22.6)
To what extent does the law ensure the enforcement of administrative decisions relating to the
environment will be timely?
Year A vailability
 Country A vailability
3.30.9 Environmental information in the public domain (Guideline 2) (edi_gepd)
The indicator measures to which extent the states provide environmental information in the public
domain that include, among other things, information about environmental quality, environmental
impacts on health and factors that inﬂuence them, in addition to information about legislation and
policy, and advice about how to obtain information.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst)
to 3 (best): (2.1) To what extent does the law require information on environmental quality to be
made proactively available to the public?; (2.2) To what extent does the law require environmental
information on environmental factors that inﬂuence health be placed in the public domain?; (2.3)
To what extent does the law require information on environmental laws and policy be placed in the
public domain?; (2.4) To what extent does the law require publicly available information and advice
236

## Page 239

on how to obtain environmental information?; (P2.1) Are real time air quality data for the capital
city of your country made available online by the government?; (P2.2) In the last two years, has
annual drinking water quality data for water services in your capital city been proactively provided
to consumers either by mail (post) or online and do they meet the minimum standards established
by the regulatory agency?
Year A vailability
 Country A vailability
3.30.10 Early public participation (Guideline 8) (edi_gepp)
The indicator measures to which extent the states states ensure opportunities for early and eﬀective
public participation in decision-making related to the environment.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst)
to 3 (best): (8.1) To what extent does the law require the public concerned to have opportunities
to participate in decision making related to the environment?; (8.2) To what extent does the law
require public participation opportunities to be provided early in the decision-making process?; (8.3)
To what extent does the law require that the public concerned be provided with information about
its opportunities to participate early in the decision-making process?; (P8.1) Choose three recent
controversial development projects (in terms of press coverage and potential cost and/or revenue
of project) that were approved through an Environmental Impact Assessment (EIA) process under
national law. Were public notices given seeking comments on the EIA or its terms of reference?
237

## Page 240

Year A vailability
 Country A vailability
3.30.11 Early warning information (Guideline 6) (edi_gewi)
The indicator measures to which extent the states ensure that all information that would enable the
public to take measures to prevent imminent threat of harm to human health or the environment
is disseminated immediately.
This indicator is an arithmetic average of expert answers to question on a scale from 0 (worst) to
3 (best): (6.1) When there is an imminent threat of harm to human health or the environment, to
what extent does the law obligate or mandate the government agencies to immediately disseminate
information to the public that enables it to take preventive action?
Year A vailability
 Country A vailability
238

## Page 241

3.30.12 Fair, timely, and independent review (Guideline 19) (edi_gftir)
The indicator measures to which extent the states provide eﬀective procedures for timely review
by courts of law or other independent and impartial bodies, or administrative procedures, of issues
relating to the implementation and enforcement of laws and decisions pertaining to the environment.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to
3 (best): (19.1) To what extent does the law provide procedures for the review of issues relating to
the implementation and enforcement of laws and decisions pertaining to the environment by courts
or other bodies, or administrative procedures?; (19.2) To what extent does the law require review
procedures regarding the implementation and enforcement of laws and decisions pertaining to the
environment to be decided by impartial and independent courts or bodies?; (19.3) To what extent
does the law require review procedures regarding the implementation and enforcement of laws and
decisions pertaining to the environment to be timely?; (19.4) To what extent does the law require
review procedures regarding the implementation and enforcement of laws and decisions pertaining
to the environment to be fair and equitable?; (19.5) To what extent does the law require review
procedures regarding the implementation and enforcement of laws and decisions pertaining to the
environment to be open and transparent? (P19.1) In the last 5 years have there been sanctions or
corrective actions imposed by a national court of law or other independent and impartial body, for
violation of laws and decisions pertaining to the environment?
Year A vailability
 Country A vailability
3.30.13 Grounds for refusal (Guideline 3) (edi_ggr)
The indicator measures to which extent the states clearly deﬁne in their law the speciﬁc grounds
on which a request for environmental information can be refused. The grounds for refusal are to
be interpreted narrowly, taking into account the public interest served by disclosure.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to
3 (best): (3.1) To what extent does the law clearly deﬁne speciﬁc grounds on which a request for
environmental information can be refused?; (3.2) To what extent does the law require environmental
239

## Page 242

information that is covered by a ground for refusal to be severed (separated) from the rest of the
information before being released to the requester?; (3.3) To what extent does the law require
the decision-maker to take into account the public interest served by disclosure when considering
exemptions (grounds for refusal)?
Year A vailability
 Country A vailability
3.30.14 Information collection and management (Guideline 4) (edi_gicm)
The indicator measures to which extent the states ensure that their competent public authorities
regularly collect and update relevant environmental information, including information on environ-
mental performance and compliance by operators of activities potentially aﬀecting the environment.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst)
to 3 (best): (4.1) To what extent are competent public authorities mandated by law to regularly
collect and update relevant environmental information?; (4.2) To what extent does the law mandate
the public authorities to comprehensively monitor the environmental performance and compliance
by operators of activities potentially aﬀecting the environment, and to collect and update such
information?; (4.3) To what extent is there a system established by the law ensuring adequate public
information about proposed and existing activities that may signiﬁcantly aﬀect the environment?;
(P4.1) Does a national agency in your country ensure that daily air emission and waste water
discharges by large-scale industries at a facility level are proactively made publicly available either
online, through a public register or at a library; if so, is that information comparable to a national
standard?
240

## Page 243

Year A vailability
 Country A vailability
3.30.15 Informed participation (Guideline 10) (edi_gip)
The indicator measures to which extent the states ensure that all information relevant for decision-
making related to the environment is made available, in an objective, understandable, timely, and
eﬀective manner, to the members of the public concerned.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to 3
(best): (10.1) To what extent do the laws concerning: environmental impact assessments, pollution
control permits, forest concessions, extractive industries, protected areas and terrestrial biodiver-
sity, and environmental policy-making require all information relevant to decision-making processes
relating to the environment to be made available to the public concerned, without the public
having to make an oﬃcial information request?; (10.2) To what extent do the laws concerning envi-
ronmental impact assessments, pollution control permits, forest concessions, extractive industries,
protected areas and terrestrial biodiversity, and environmental policy-making require that proac-
tively released information relevant to decision-making be understandable to the public concerned?;
(10.3) To what extent do the laws concerning environmental impact assessments, pollution control
permits, forest concessions, extractive industries, biodiversity and terrestrial protected areas, and
environmental policy-making require the information relevant to decision-making to be provided in
a timely fashion to the public concerned?; (P10.1) Are the Environmental Impact Assessments for
development projects accessible to the public online or at a national government agency?; (P10.2)
Is information on wastewater discharge and air emission permit violations available to the public
online or at a government agency?; (P10.3) Are extractive industry licenses/permits available to
the public online or at a government agency?; (P10.4) During the past three years, in the process of
granting forest use contracts, has the relevant agency made publicly available information related
to such contracts?; (P10.5) Are the forest use contracts, onceﬁnalized, made available to the public
online or at a government agency?
241

## Page 244

Year A vailability
 Country A vailability
3.30.16 Integrating public input for rule-making (Guideline 13) (edi_gipirm)
The indicator measures to which extent the states consider appropriate ways of ensuring, at an
appropriate stage, public input into the preparation of legally binding rules that might have a
signiﬁcant eﬀect on the environment and into the preparation of policies, plans and programmes
relating to the environment.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to
3 (best): (13.1) To what extent does the law require opportunities for public input at an appro-
priate stage during preparation of legally binding rules (rule-making or preparation of subsidiary
legislation, regulations, etc.) that might have a signiﬁcant eﬀect on the environment?; (13.2) To
what extent do the laws concerning environmental impact assessments, pollution control standards
and permits, forest concessions, extractive industries, protected areas and terrestrial biodiversity,
and environmental policy-making require the State or state agencies to provide opportunities for
public input at an appropriate stage of the preparation of policies?; (13.3) To what extent do the
laws concerning environmental impact assessments, pollution control standards and permits, forest
concessions, extractive industries, protected areas and terrestrial biodiversity, and environmental
policy-making require there to be opportunities for public input at an appropriate stage of the
preparation of plans relating to the environment?; (13.4) To what extent does the law require there
to be opportunities for public input at an appropriate stage of the preparation of programs relating
to the environment?
242

## Page 245

Year A vailability
 Country A vailability
3.30.17 Information request appeals (Guideline 15) (edi_gira)
The indicator measures to which extent the states ensure that any natural or legal person who
considers that his or her request for environmental information has been unreasonably refused, in
part or in full, inadequately answered or ignored, or in any other way not handled in accordance
with applicable law, has access to a review procedure before a court of law or other independent
and impartial body to challenge such a decision, act or omission by the public authority in question.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to
3 (best): (15.1) To what extent do the laws concerning environmental impact assessments, pollu-
tion control standards and permits, forest concessions, extractive industries, protected areas and
terrestrial biodiversity, and environmental policy-making provide for access to a review procedure
in cases where environmental information request have been denied?; (15.2) To what extent does
the law make the review available to all natural or legal persons?; (15.3) To what extent does the
law provide access to a review procedure before a court of law or other independent and impartial
body in cases when an environmental information request has been denied?; (P15.1) Is there a
court, tribunal or other independent or impartial body at the national level with a physical oﬃce
to receive and process public complaints about the refusal of environmental information?
243

## Page 246

Year A vailability
 Country A vailability
3.30.18 Public access to judicial and administrative decisions (Guideline 24) (edi_-
gpajad)
The indicator measures to which extent the states ensure that decisions relating to the environment
taken by a court of law, other independent and impartial or administrative body, are publicly
available, as appropriate and in accordance with national law.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to
3 (best): (24.1) To what extent does the law require judicial decisions relating to the environment
to be made publicly available?; (24.2) To what extent does the law require decisions relating to the
environment taken by administrative bodies to be made publicly available?; (24.3) To what extent
does the law require decisions relating to the environment taken by other independent and impartial
bodies to be made publicly available?; (P24.1) Are the decisions of the last three environmental or
natural resource cases decided by a national court, tribunal or other judicial body available to the
public online or at the oﬃce of that court, tribunal or body?
Year A vailability
 Country A vailability
244

## Page 247

3.30.19 Prompt, eﬀective remedies (Guideline 21) (edi_gper)
The indicator measures to which extent the states provide a framework for prompt, adequate and
eﬀective remedies in cases relating to the environment, such as interim andﬁnal injunctive relief.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to 3
(best): (21.1) To what extent does the law require adequate and eﬀective remedies in cases relating
to the environment?; (21.2) To what extent does the law require remedies in cases relating to the
environment to be provided promptly?; (21.3) To what extent is interim and/orﬁnal injunctive
relief available under the law?; (21.4) To what extent is compensation available as a remedy under
the law?; (21.5) To what extent is restitution available as a remedy under the law?; (21.6) To
what extent is restoration of the environment available as a remedy under the law?; (P21.1) In the
last 5 years, have there been injunctions/stay orders/interdicts issued by a court, tribunal or other
judicial body in environmental or natural resource cases?
Year A vailability
 Country A vailability
3.30.20 Public participation appeals (Guideline 16) (edi_gppa)
The indicator measures to which extent the states ensure that the members of the public concerned
have access to a court of law or other independent and impartial body to challenge the substantive
and procedural legality of any decision, act or omission relating to public participation in decision-
making in environmental matters.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to 3
(best): (16.1) To what extent does the law entitle members of the public concerned to challenge the
substantive legality of any decision, act or omission relating to decision-making in environmental
matters which is subject to public participation?; (16.2) To what extent does the law entitle mem-
bers of the public concerned to challenge the procedural legality of any decision, act or omission
relating to decision-making in environmental matters subject to public participation?; (16.3) To
what extent does the law require that a court of law or other independent and impartial body
hear challenges to substantive and/or procedural legality?; (P16.1) In the last 5 years, have public
245

## Page 248

interest environmental or natural resource cases beenﬁled before a court, tribunal or other body?
If court records are not public information, check media reports.
Year A vailability
 Country A vailability
3.30.21 Proactive public consultation (Guideline 9) (edi_gppc)
The indicator measures to which extent the states make eﬀorts to seek proactively public partici-
pation in a transparent and consultative manner, including eﬀorts to ensure that members of the
public concerned are given an adequate opportunity to express their views.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to
3 (best): (9.1) To what extent do the laws concerning environmental impact assessments, pollution
control permits, forest concessions, extractive industries, biodiversity and terrestrial protected ar-
eas, and environmental policy-making obligate the State or state agencies at the national level to
proactively seek public participation?; (9.2) To what extent do the laws concerning: environmental
impact assessments, pollution control permits, forest concessions, extractive industries, biodiver-
sity and terrestrial protected areas, and environmental policy-making obligate the State or State
agencies at the national level to give members of the public concerned an adequate opportunity to
express their views?
246

## Page 249

Year A vailability
 Country A vailability
3.30.22 Public participation review (Guideline 12) (edi_gppr)
The indicator measures to which extent the states ensure that when a review process is carried out
where previously unconsidered environmentally signiﬁcant issues or circumstances have arisen, the
public should be able to participate in any such review process to the extent that circumstances
permit.
This indicator is an arithmetic average of expert answers to question on a scale from 0 (worst) to 3
(best): (12.1) To what extent do the laws concerning: environmental impact assessments, pollution
control standards and permits, forest concessions, extractive industries, biodiversity and terrestrial
protected areas, and environmental policy-making require the State or state agencies to provide
for a public review process for decisions relating to the environment if previously unconsidered
environmental impacts become apparent?
Year A vailability
 Country A vailability
247

## Page 250

3.30.23 Right of public to challenge state or private actors (Guideline 17) (edi_-
grpcspa)
The indicator measures to which extent the states ensure that the members of the public concerned
have access to a court of law or other independent and impartial body or administrative procedures
to challenge any decision, act or omission by public authorities or private actors that aﬀects the
environment or allegedly violates the substantive or procedural legal norms of the State related to
the environment.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to
3 (best): (17.1) To what extent does the law give rights to the public concerned to challenge any
decision, act or omission by public authorities that allegedly violates the procedural legal norms of
the state relating to the environment?; (17.2) To what extent does the law give rights to the public
concerned to challenge any decision, act or omission by private actors that allegedly violates the
substantive legal norms of the state relating to the environment?; (17.3) To what extent does the
law give rights to the public concerned to challenge any decision, act or omission by private actors
that allegedly violates the procedural legal norms of the State relating to the environment?; (17.4)
To what extent does the law require the challenges referred to in indicators 1-3 to be heard by
an independent and impartial body?; (P17.1) Have there been cases in the last 5 years when civil
societyﬁled a lawsuit against a polluter in a national court?; (P17.2) Have there been cases in the
last 5 years when civil societyﬁled a lawsuit in a national court challenging a government decision,
policy, or rule aﬀecting the environment?
Year A vailability
 Country A vailability
3.30.24 State of the environment report (Guideline 5) (edi_gser)
The indicator measures to which extent the states periodically prepare and disseminate at reasonable
intervals up-to-date information on the state of the environment, including information on its quality
and on pressures on the environment.
This indicator is an arithmetic average of expert answers to questions on a scale from 0 (worst) to 3
248

## Page 251

(best): (5.1) To what extent does the law mandate the government to publish reports on the state
of the environment (i.e. a State of the Environment report)?; (5.2) To what extent does the law
require the publication of a State of the Environment report to be periodic at reasonable intervals?;
(5.3) Does the law require the report to be comprehensive in the information that it provides?;
(5.4) To what extent does the law require the report to contain up-to date information?; (P5.1) In
the last 10 years has a national government agency regularly published State of the Environment
Reports? (Regular is atﬁxed intervals ofﬁve years or less)
Year A vailability
 Country A vailability
3.30.25 Justice Pillar Score (edi_jp)
The Justice Pillar Score combines guidelines "Information request appeals", "Public participation
appeals", "Right of public to challenge state or private actors", "Broad standing", "Fair, timely,
and independent review", "Aﬀordable access to relief and remedy", "Prompt, eﬀective remedies",
"Eﬀective enforcement", "Awareness and education about remedies and relief", "Public access to
judicial and administrative decisions", and "Alternative dispute resolution for environmental issues",
using an arithmetic average on a scale from 0 (worst) to 3 (best).
249

## Page 252

Year A vailability
 Country A vailability
3.30.26 Access to Information Pillar Score (edi_pati)
The Access to Information Pillar Score combines guidelines "Accessibility of information requests",
"Environmental information in the public domain", "Ground for refusal", "Information collection
and management", "State of the environment report", and "Early warning information", using an
arithmetic average on a scale from 0 (worst) to 3 (best).
Year A vailability
 Country A vailability
3.30.27 Participation Pillar Score (edi_pp)
The Participation Pillar Score combines guidelines "Early public participation", "Proactive public
consultation", "Informed participation", "Due account of public comments", "Public participation
review", and "Integrating public input for rule-making", using an arithmetic average on a scale from
0 (worst) to 3 (best).
250

## Page 253

Year A vailability
 Country A vailability
251

## Page 254

3.31 The International Social Survey Programme. Environment Module
Dataset by:International Social Survey Programme
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
ISSP Research Group (1995). International Social Survey Programme: Environment I - ISSP
1993. GESIS Data Archive, Cologne. ZA2450 Dataﬁle Version 1.0.0, https://doi.org/10.4232/1.2450.
ISSP Research Group (2003). International Social Survey Programme: Environment II - ISSP
2000. GESIS Data Archive, Cologne. ZA3440 Dataﬁle Version 1.0.0, https://doi.org/10.4232/1.3440.
ISSP Research Group (2019). International Social Survey Programme: Environment III - ISSP
2010. GESIS Data Archive, Cologne. ZA5500 Dataﬁle Version 3.0.0, https://doi.org/10.4232/1.13271.
Link to the original source:https://www.gesis.org/en/issp/modules
The International Social Survey Programme (ISSP) is an annual program of cross-national sur-
vey collaboration, covering a wide range of topics important for social science research. Since
1985 the ISSP provides international data sets, enabling cross-cultural and cross-temporal research.
"Environment" is one of the eleven ISSP topic modules. Central themes are attitudes towards
environment-related issues, such as environmental protection, respondents’ behavior, and respon-
dents’ preferences regarding governmental measures on environmental protection.
This dataset includes two types of variables: 1) percentage of respondents choosing a particular
response option, and 2) average response per country, unweighted, primarily because weights are
unavailable for some countries. Correlation between weighted and unweighted means for countries
that do provide weights is above .95 for most of the included variables and does not go below .89.
3.31.1 Worry about environment vs jobs (mean) (issp_10am)
A verage reply to the question: "How much do you agree or disagree with this statement? We
worry too much about the future of the environment and not enough about prices and jobs today".
(1) Agree strongly, (2) Agree, (3) Neither agree nor disagree, (4) Disagree, (5) Disagree strongly.
Replies (8) Can’t choose are deleted.
In Environment III (2010) - question 10a.
In Environment II (2000) - question 4a.
In Environment I (1993) - question 5a.
252

## Page 255

A higher score means that smaller parts of the population think that there is too much worry about
the environment. A lower score means that larger parts of the population think that there is too
much worry about the environment and too little worry about prices and jobs.
Year A vailability
 Country A vailability
3.31.2 Unwillingness to pay higher prices (%) (issp_12ap)
Percent of replies "fairly unwilling" and "very unwilling" to 12a: "How willing would you be to pay
much higher prices in order to protect the environment?". Original replies include: (1) Very willing,
(2) Fairly willing, (3) Neither willing nor unwilling, (4) Fairly unwilling, (5) Very unwilling, (8)
Can’t choose.
In Environment III (2010) - question 12a.
In Environment II (2000) - question 7a.
In Environment I (1993) - question 8a.
A higher score means that fewer people are willing to pay higher prices for environmental protection.
A lower score means that more people are willing to pay higher prices for environmental protection.
253

## Page 256

Year A vailability
 Country A vailability
3.31.3 Unwillingness to pay higher taxes (%) (issp_12bp)
Percent of replies "fairly unwilling" and "very unwilling" to 12b: "And how willing would you be
to pay much higher taxes in order to protect the environment?". Original replies include: (1) Very
willing, (2) Fairly willing, (3) Neither willing nor unwilling, (4) Fairly unwilling, (5) Very unwilling,
(8) Can’t choose.
In Environment III (2010) - question 12b.
In Environment II (2000) - question 7b.
In Environment I (1993) - question 8b.
A higher score means that fewer people are willing to pay more taxes for environmental protection.
A lower score means that more people are willing to pay higher taxes for environmental protection.
Year A vailability
 Country A vailability
254

## Page 257

3.31.4 Unwillingness to cut in standard of living (%) (issp_12cp)
Percent of replies "fairly unwilling" and "very unwilling" to 12c: "And how willing would you be
to accept cuts in your standard of living in order to protect the environment?". Original replies
include: (1) Very willing, (2) Fairly willing, (3) Neither willing nor unwilling, (4) Fairly unwilling,
(5) Very unwilling, (8) Can’t choose.
In Environment III (2010) - question 12c.
In Environment II (2000) - question 7c.
In Environment I (1993) - question 8c.
A higher score means that fewer people are willing to accept cuts in the standard of living for
environmental protection. A lower score means that more people are willing to accept cuts in the
standard of living for environmental protection.
Year A vailability
 Country A vailability
3.31.5 Individual action is insuﬃcient (mean) (issp_13am)
A verage reply to 13a: "How much do you agree or disagree with this statement? It is just too
diﬃcult for someone like me to do much about the environment". (1) Agree strongly, (2) Agree,
(3) Neither agree nor disagree, (4) Disagree, (5) Disagree strongly. Replies (8) Can’t choose are
deleted.
In Environment III (2010) - question 13a.
In Environment II (2000) - question 8a.
In Environment I (1993) - question 9a.
A higher score means that fewer people believe that it is too diﬃcult to do something about the
255

## Page 258

environment as an individual. A lower score means that more people believe that it is too diﬃcult
to do something about the environment as an individual.
Year A vailability
 Country A vailability
3.31.6 Environmental behavior (mean) (issp_13bm)
A verage reply to 13b: "How much do you agree or disagree with this statement? I do what is right
for the environment, even when it costs more money or takes more time". (1) Agree strongly, (2)
Agree, (3) Neither agree nor disagree, (4) Disagree, (5) Disagree strongly. Replies (8) Can’t choose
are deleted.
In Environment III (2010) - question 13b.
In Environment II (2000) - question 8b.
In Environment I (1993) - question 9b.
A higher score means that fewer people are willing to spend more money/time to do what is best
for the environment. A lower score means that more people are willing to spend more money/time
to do what is right for the environment.
256

## Page 259

Year A vailability
 Country A vailability
3.31.7 Claims about environmental threats are exaggerated (mean) (issp_13em)
A verage reply to 13e: "How much do you agree or disagree with this statement? Many of the claims
about environmental threats are exaggerated". (1) Agree strongly, (2) Agree, (3) Neither agree nor
disagree, (4) Disagree, (5) Disagree strongly. Answers (8) Can’t choose are deleted.
In Environment III (2010) - question 13e.
In Environment II (2000) - question 8e.
In Environment I (1993) - question not part of the survey.
A higher score means that fewer people think that environmental treats are exaggerated. A lower
score means that more people think that environmental threats are exaggerated.
Year A vailability
 Country A vailability
257

## Page 260

3.31.8 Perceived vulnerability to environmental problems (mean) (issp_13gm)
A verage reply to 13g: "How much do you agree or disagree with this statement? Environmental
problems have a direct eﬀect on my everyday life". (1) Agree strongly, (2) Agree, (3) Neither agree
nor disagree, (4) Disagree, (5) Disagree strongly. Replies (8) Can’t choose are deleted.
In Environment III (2010) - question 13g.
In Environment II (2000) - question not part of the survey.
In Environment I (1993) - question not part of the survey.
A higher score means that fewer people think that environmental problems aﬀect everyday life. A
lower score means that more people think that environmental problems aﬀect everyday life.
Year A vailability
 Country A vailability
3.31.9 Support for government action to make people comply (%) (issp_15ap)
Percent of replies for 15a: "If you had to choose, which one of the following would be closest to your
views? (2) Government should pass laws to make ordinary people protect the environment, even if
it interferes with peoples rights to make their own decisions". Other replies include (1) Government
should let ordinary people decide for themselves how to protect the environment, even if it means
they dont always do the right thing, and (8) Can’t choose.
In Environment III (2010) - question 15a.
In Environment II (2000) - question 13a.
In Environment I (1993) - question 18a.
The higher the score the higher the belief that the government should pass laws to make people
protect the environment. The lower the score the lower the belief that the government should pass
258

## Page 261

laws to make people protect the environment.
Year A vailability
 Country A vailability
3.31.10 Priority of future energy sources - fossil fuels (%) (issp_18p)
Percent of replies (1) Coal, oil and natural gas to 18: "To which of the following should [COUNTRY]
give priority in order to meet its future energy needs?". Other replies include: (2) Nuclear power,
(3) Solar, wind or water power, (4) Fuels made from crop, (5) None of them.
In Environment III (2010) - question 18.
In Environment II (2000) - question not part of the survey.
In Environment I (1993) - question not part of survey.
The higher the score the higher the percentage of people that prefers fossil fuels over other sources.
The lower the score the lower the percentage of people that prefers fossil fuels over other sources.
Year A vailability
 Country A vailability
259

## Page 262

3.31.11 Attitudes on international environmental agreements (mean) (issp_19am)
A verage reply to 19a: "How much do you agree or disagree with each of these statements? For
environmental problems, there should be international agreements that [COUNTRY] and other
countries should be made to follow". (1) Agree strongly, (2) Agree, (3) Neither agree nor disagree,
(4) Disagree, (5) Disagree strongly. Replies (8) Can’t choose are deleted.
In Environment III (2010) - question 19a.
In Environment II (2000) - question 16a.
In Environment I (1993) - question not part of the survey.
A higher score means that there is less support in the population for international agreements. A
lower score means that there is more support in the population towards international agreements.
Year A vailability
 Country A vailability
3.31.12 Attitudes towards global environmental justice (mean) (issp_19bm)
A verage reply to 19b: "How much do you agree or disagree with each of these statements? Poorer
countries should be expected to make less eﬀort than richer countries to protect the environment".
(1) Agree strongly, (2) Agree, (3) Neither agree nor disagree, (4) Disagree, (5) Disagree strongly.
Replies (8) Can’t choose are deleted.
In Environment III (2010) - question 19b.
In Environment II (2000) - question 16b.
In Environment I (1993) - question not part of the survey.
A higher score means that fewer people think that poorer countries should do less than rich countries
to protect the environment. A lower score means that more people think that poorer countries
260

## Page 263

should do less than rich countries to protect the environment.
Year A vailability
 Country A vailability
3.31.13 Environment is most or next most important issue (%) (issp_1ap)
Percent replying "The environment" to 1a: "Which of these issues is the most important for [COUN-
TRY] today?" plus percent replying "The environment" to 1b: "Which of these issues is the next
most important for [COUNTRY] today?". The issues in the list include: (1) Health care, (2) Ed-
ucation, (3) Crime, (4) The environment, (5) Immigration, (6) The economy, (7) Terrorism, (8)
Poverty, (9) None of these, (98) Can’t choose.
In Environment III (2010) - questions 1a and 1b.
In Environment II (2000) - question not part of the survey.
In Environment I (1993) - question not part of the survey.
The higher the score the higher the percentage of the population that prioritizes the environment
as the most or second most important issue. The lower the score the smaller the percentage of the
population that prioritizes the environment as the most or second most important issue.
261

## Page 264

Year A vailability
 Country A vailability
3.31.14 Reported extent of recycling (mean) (issp_20am)
A verage reply to 20a: "How often do you make a special eﬀort to sort glass or tins or plastic or
newspapers and so on for recycling?". (1) Always, (2) Often, (3) Sometimes, (4) Never. Responses
(8) Recycling not available where I live are deleted.
In Environment III (2010) - question 20a.
In Environment II (2000) - question 19a.
In Environment I (1993) - question 19a.
A higher score means that fewer people make an eﬀort to recycle correctly. A lower score means
that more people make an eﬀort to recycle correctly.
Year A vailability
 Country A vailability
262

## Page 265

3.31.15 Recycling not available (%) (issp_20ap)
Percent of replies (8) Recycling not available where I live to 20a: "How often do you make a special
eﬀort to sort glass or tins or plastic or newspapers and so on for recycling?".
In Environment III (2010) - answer not included.
In Environment II (2000) - question 19a.
In Environment I (1993) - question 19a.
A higher score means that more people have access to recycling facilities. A lower score means that
fewer people have access to recycling facilities.
Year A vailability
 Country A vailability
3.31.16 Reducing energy use for the environment (mean) (issp_20dm)
A verage reply to 20d: "How often do you reduce the energy or fuel you use at home for environmental
reasons?". (1) Always, (2) Often, (3) Sometimes, (4) Never.
In Environment III (2010) - question 20d.
In Environment II (2000) - question not part of the survey.
In Environment I (1993) - question not part of the survey.
A higher score means that fewer people make a special eﬀort to reduce energy consumption for
environmental reasons. A lower score means that more people make a special eﬀort to reduce
energy consumption for environmental reasons.
263

## Page 266

Year A vailability
 Country A vailability
3.31.17 Membership in environmental groups (%) (issp_21p)
Percent of "yes"-replies to 21: "Are you a member of any group whose main aim is to preserve or
protect the environment?".
In Environment III (2010) - question 21.
In Environment II (2000) - question 20.
In Environment I (1993) - question 20.
A higher score means that more people are members of environmental groups. A lower score means
that fewer people are members of environmental groups.
Year A vailability
 Country A vailability
264

## Page 267

3.31.18 Signed petitions about environmental issues (%) (issp_22ap)
Percent of "yes"-replies to 22a: "In the lastﬁve years, have you signed a petition about an environ-
mental issue?".
In Environment III (2010) - question 22a.
In Environment II (2000) - question 21a.
In Environment I (1993) - question 21a.
A higher score means that more people signed petitions for environmental issues in the 2 years prior
to the survey. A lower score means that fewer people signed petitions for environmental issues in
the 2 years prior to the survey.
Year A vailability
 Country A vailability
3.31.19 Given money to an environmental group (%) (issp_22bp)
Percent of "yes"-replies to 22b: "In the lastﬁve years, have you given money to an environmental
group (including NGOs and lobby groups)?".
In Environment III (2010) - question 22b.
In Environment II (2000) - question 21b.
In Environment I (1993) - question 21b.
A higher score means that more people gave money to environmental groups in the 5 years prior
to the survey. A lower score means that fewer people gave money to environmental groups in the
5 years prior to the survey.
265

## Page 268

Year A vailability
 Country A vailability
3.31.20 Taken part in a protest/demonstration about environmental issues (%)
(issp_22cp)
Percent of "yes"-replies to 22c: "In the lastﬁve years, have you taken part in a protest or demon-
stration about an environmental issue?".
In Environment III (2010) - question 22c.
In Environment II (2000) - question 21c.
In Environment I (1993) - question 21c.
A higher score means that more people participated in environmental protests in the 5 years prior
to the survey. A lower score means that fewer people participated in environmental protests in the
5 years prior to the survey.
Year A vailability
 Country A vailability
266

## Page 269

3.31.21 Environmental concern (mean) (issp_6m)
A verage reply to the question: "Generally speaking, how concerned are you about environmental
issues?". (1) Not at all concerned - (5) Very concerned. Replies (8) Can’t choose are deleted.
In Environment III (2010) - question 6.
In Environment II (2000) - question not part of the survey.
In Environment I (1993) - question not part of the survey.
A higher score means that more people are concerned about environmental issues. A lower score
means that fewer people are concerned about environmental issues.
Year A vailability
 Country A vailability
3.31.22 Knowledge about causes of environmental problems (mean) (issp_8am)
A verage reply to 8a: "How much do you feel you know about the causes of these sorts of environ-
mental problems?". (1) Know nothing at all - (5) Know a great deal. Replies (8) Can’t choose
are deleted. "These sorts of environmental problems" refer to (1) Air pollution, (2) Chemicals and
pesticides, (3) Water shortage, (4) Water pollution, (5) Nuclear waste, (6) Domestic waste disposal,
(7) Climate change, (8) Genetically modiﬁed foods, (9) Using up our natural resources.
In Environment III (2010) - question 8a.
In Environment II (2000) - question not part of the survey.
In Environment I (1993) - question not part of the survey.
A higher score means that more people feel that they know about the causes of environmental prob-
lems. A lower score means that fewer people feel that they know about the causes of environmental
problems.
267

## Page 270

Year A vailability
 Country A vailability
3.31.23 Knowledge about solutions to environmental problems (mean) (issp_8bm)
A verage reply to 8b: "And how much do you feel you know about solutions to these sorts of
environmental problems?". (1) Know nothing at all - (5) Know a great deal. Replies (8) Can’t
choose are deleted.
In Environment III (2010) - question 8b.
In Environment II (2000) - question not part of the survey.
In Environment I (1993) - question not part of the survey.
A higher score means that more people feel that they know about the solutions to environmental
problems. A lower score means that fewer people feel that they know about the solutions to
environmental problems.
Year A vailability
 Country A vailability
268

## Page 271

3.31.24 Belief in science (mean) (issp_9am)
A verage reply to 9a: "How much do you agree or disagree with this statement? We believe too
often in science, and not enough in feelings and faith". (1) Agree strongly, (2) Agree, (3) Neither
agree nor disagree, (4) Disagree, (5) Disagree strongly. Replies (8) Can’t choose are deleted.
In Environment III (2010) - question 9a.
In Environment II (2000) - question 3a.
In Environment I (1993) - question 4a.
A higher score means that there are fewer people who think that we believe in science too often
and not enough in feelings and faith. A lower score means that there are more people who think
that we believe in science too often and not enough in feelings and faith.
Year A vailability
 Country A vailability
269

## Page 272

3.32 The Ocean Health Index Data
Dataset by:The Ocean Health Index
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Halpern, Benjamine et al. 2018.Ocean Health Index.National Center for Ecological Analysis
and Synthesis, University of California, Santa Barbara.url:https : / / github . com / OHI -
Science/ohi-global/releases
Halpern, Benjamine et al. 2012. “An index to assess the health and beneﬁts of the global
ocean”.Nature. 488
Link to the original source:http://www.oceanhealthindex.org
The Ocean Health Index is a valuable tool for the ongoing assessment of ocean health. By provid-
ing a means to advance comprehensive ocean policy and compare future progress, the Index can
inform decisions about how to use or protect marine ecosystems. The Index is a collaborative eﬀort,
made possible through contributions from more than 65 scientists/ocean experts and partnerships
between organizations including the National Center for Ecological Analysis and Synthesis, Sea
Around Us, Conservation International, National Geographic, and the New England Aquarium.
The Index assesses the ocean based on 10 widely-held public goals for a healthy ocean. They are:
Food Provision, Artisanal Fishing Opportunities, Natural Products, Carbon Storage, Coastal Pro-
tection, Sense of Place, Coastal Livelihoods & Economies, Tourism & Recreation, Clean Waters,
Biodiversity.
3.32.1 Fisheries management eﬀectiveness and opportunity (ohi_aoacc)
Fisheries management eﬀectiveness and opportunity. The eﬀectiveness ofﬁsheries management in
all countries with coastal areas is assessed by using a combination of surveys, empirical data, and
enquiries toﬁsheries experts. They evaluated six aspects of each management regime: Scientiﬁc
Robustness, Policy Transparency, Implementation Capacity, Subsidies, Fishing Eﬀort, and Foreign
Fishing, scoring each category from 0 to 100.
For more details on the variable construction, see the original source:
Mora, C., Myers, R.A., Coll, M., Libralato, S., Pitcher, T.J., Sumaila, R.U., Worm, B. (2009).
270

## Page 273

Management Eﬀectiveness of the World’s Marine Fisheries. PLoS Biol, 7(6), e1000131.
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
3.32.2 Ocean acidiﬁcation (ohi_caacid)
Ocean acidiﬁcation. The Ocean acidiﬁcation layer models the diﬀerence in global distribution
changes in the aragonite saturation state (Ωarag) between pre-industrial (∼1870) and modern times
(2000-2009) as a proxy for ocean acidiﬁcation due to human inﬂuences.
For more details on the variable construction, see the original sources:
Feely, R., Doney, S. & Cooley, S. (2009) Ocean acidiﬁcation: present conditions and future changes
in a high-CO2 world. Oceanography 22:36-47.
and
J. Aﬄerbach et al. (2015). https://github.com/OHI-Science/ohiprep/tree/master/globalprep/Pressures_-
OceanAcidiﬁcation/v2015
When using this variable, please cite both the OHI project and the original sources.
271

## Page 274

Year A vailability
 Country A vailability
3.32.3 Coastal human population as a proxy for trend in trash (ohi_chp)
Coastal human population as a proxy for trend in trash. For more details on the variable construc-
tion, see the original source:
CIESIN & CIAT (Center for International Earth Science Information Network / Columbia Univer-
sity, & Centro Internacional de Agricultura Tropical) (2005). Gridded Population of the World,
Version 3 (GPWv3): Population Density Grid, Future Estimates. Palisades, NY. [NASA Socioeco-
nomic Data and Applications Center (SEDAC)].
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
272

## Page 275

3.32.4 Sea level rise (ohi_csslr)
Sea level rise. For more details on the variable construction, see the original sources:
Nicholls R. J. and Cazenave A. (2010). Sea-level rise and its impact on coastal zones. Science 328:
1517-1520.
and
A VISO Satellite Altimetry Data.
and
J. Aﬄerbach et al. (2015). (https://github.com/OHI-Science/ohiprep/tree/master/globalprep/Pressures_-
SeaLevelRise/v2015)
When using this variable, please cite both the OHI project and the original sources.
Year A vailability
 Country A vailability
3.32.5 Sea surface temperature (SST) anomalies (ohi_csst)
Sea surface temperature (SST) anomalies. SST of the ocean is indicated by measurements taken
at depths that range from 1 millimeter to 20 meters. This measurement does not indicate absolute
temperature at a location, but instead determines the number of positive temperature deviations
(anomalies) that exceed the natural range of variation for a given location, i.e. the frequency with
which a location experiences unnaturally warm temperature.
For more details on the variable construction, see the original sources:
A VHRR Pathﬁnder Version 5.0 SST data.
and
273

## Page 276

Casey, K. S., Brandon, T. B., Cornillon, P., and Evans, R. (2010). The past, present and future
of the A VHRR Pathﬁnder SST Program, Oceanography from Space: Revisited, eds. V. Barale,
J.F.R. Gower, and L. Alberotanza, Springer.
and
J. Aﬄerbach et al. (2015). (https://github.com/OHI-Science/ohiprep/tree/master/globalprep/Pressures_-
SST)
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
3.32.6 UV radiation (ohi_cuv)
UV radiation. Ultraviolet radiation (UVR) is the portion of solar radiation with wavelengths of
200-400 nanometers (nm). UV Radiation was measured as the number of times in each 1-degree cell
that the monthly average exceeded the climatological mean +1 standard deviation. These values
were summed across the 12 months to provide a single value, ranging from 0-19.
For more details on the variable construction, see the original sources:
Goddard Earth Sciences Data and Information Services Center (GES DISC).
and
J. Aﬄerbach et al. (2015). (https://github.com/OHI-Science/ohiprep/tree/master/globalprep/Pressures_-
UV)
When using this variable, please cite both the OHI project and the original sources.
274

## Page 277

Year A vailability
 Country A vailability
3.32.7 High bycatch caused by artisanalﬁshing (ohi_fah)
High bycatch caused by artisanalﬁshing. For more details on the variable construction, see the
original source:
Reefs at Risk Revisited (http://www.wri.org/publication/reefs-at-risk-revisited).
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
3.32.8 High bycatch caused by commercialﬁshing (ohi_fchb)
High bycatch caused by commercialﬁshing. For more details on the variable construction, see the
original source:
275

## Page 278

Halpern, B. S. et al. (2008) A global map of human impact on marine ecosystems. Science,
3199(5865): 948-952.
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
3.32.9 Low bycatch caused by commercialﬁshing (ohi_fclb)
Low bycatch caused by commercialﬁshing. For more details on the variable construction, see the
original source:
Halpern, B. S. et al. (2008) A global map of human impact on marine ecosystems. Science,
3199(5865): 948-952.
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
276

## Page 279

3.32.10 CBD survey: habitat (ohi_hab)
CBD survey: habitat. A resilience measure based on questions 153(a,b,c,e,g) and 158(a,b,c,f,g,h)
from The Convention on Biological Diversity country questionnaire (Third National Report to the
CBD, from 2005).
Question 153: Do your country’s strategies and action plans include the following:
a) Developing new marine and coastal protected areas;
b) Improving the management of existing marine and coastal protected areas;
c) Building capacity within the country for management of marine and coastal resources, including
through educational programmes and targeted research initiatives;
e) Protection of areas important for reproduction, such as spawning and nursery areas;
g) Controlling excessiveﬁshing and destructiveﬁshing practices?
Question 158: Which of the following statements can best describe the current status of marine
and coastal protected areas in your country:
a) Marine and coastal protected areas have been declared and gazetted;
b) Management plans for these marine and coastal protected areas have been developed with in-
volvement of all stakeholders;
c) Eﬀective management with enforcement and monitoring has been put in place;
f) The national system of marine and coastal protected areas includes areas managed for purpose
of sustainable use, which may allow extractive activities;
g) The national system of marine and coastal protected areas includes areas which exclude extractive
uses;
h) The national system of marine and coastal protected areas is surrounded by sustainable man-
agement practices over the wider marine and coastal environment?
For more details on the variable construction, see the original sources:
Convention on Biological Diversity, CBD (http://www.cbd.int/reports/search/default.shtml).
When using this variable, please cite both the OHI project and the original source.
277

## Page 280

Year A vailability
 Country A vailability
3.32.11 CBD survey: coastal habitat (ohi_habcom)
CBD survey: coastal habitat. For more details on the variable construction, see the original sources:
Convention on Biological Diversity, CBD (http://www.cbd.int/reports/search/default.shtml).
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
3.32.12 CBD survey: ocean habitat (ohi_habeez)
CBD survey: ocean habitat. For more details on the variable construction, see the original sources:
Convention on Biological Diversity, CBD (http://www.cbd.int/reports/search/default.shtml).
278

## Page 281

When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
3.32.13 Coastal population density as a proxy for intertidal habitat destruction
(ohi_hdinter)
Coastal population density as a proxy for intertidal habitat destruction. For more details on the
variable construction, see the original sources:
CIESIN & CIAT (Center for International Earth Science Information Network /Columbia University
& Centro Internacional de Agricultura Tropical) (2005). Gridded Population of the World, Version
3 (GPWv3): Population Density Grid, Future Estimates. Palisades, NY.
and
NASA Socioeconomic Data and Applications Center (SEDAC)
and
Halpern, B. S. et. al. (2008) A global map of human impact on marine ecosystems. Science,
3199(5865): 948-952.
When using this variable, please cite both the OHI project and the original sources.
279

## Page 282

Year A vailability
 Country A vailability
3.32.14 Bycatch by artisanalﬁshing - hard bottom habitat destruction (ohi_hshb)
High bycatch artisanalﬁshing practices as a proxy for subtidal hard bottom habitat destruction.
For more details on the variable construction, see the original sources:
Reefs at Risk Revisited (http://www.wri.org/publication/reefs-at-risk-revisited).
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
3.32.15 Demersal destructiveﬁshing - soft bottom habitat destruction (ohi_hssb)
Demersal destructive commercialﬁshing practices relative to soft-bottom habitat area as a proxy
for soft bottom habitat destruction. For more details on the variable construction, see the original
source:
280

## Page 283

Sea Around Us Project (http://www.seaaroundus.org/)
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
3.32.16 Coastal protected areas inland 1km (ohi_lpai)
Coastal protected areas inland 1km. For more details on the variable construction, see the original
sources:
United Nations - World Conservation Monitoring Centre’s World Database on Protected Areas
(WDPA) through [Protected Planet (http://www.protectedplanet.net)].
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
281

## Page 284

3.32.17 Coastal marine protected areas oﬀshore 3km (ohi_lpao)
Coastal marine protected areas oﬀshore 3km. For more details on the variable construction, see the
original sources:
United Nations - World Conservation Monitoring Centre’s World Database on Protected Areas
(WDPA) through [Protected Planet (http://www.protectedplanet.net)].
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
3.32.18 CBD Survey: Mariculture (ohi_maricul)
CBD Survey: Mariculture. A resilience measure based on questions 158(d) and 159(a-l) from The
Convention on Biological Diversity country questionnaire (Third National Report to the CBD, from
2005).
Question 158: Which of the following statements can best describe the current status of marine
and coastal protected areas in your country:
d) A national system or network of marine and coastal protected areas is under development?
Question 159: Is your country applying the following techniques aimed at minimizing adverse
impacts of mariculture on marine and coastal biodiversity?
a) Application of environmental impact assessments for mariculture developments;
b) Development and application of eﬀective site selection methods in the framework of integrated
marine and coastal area management;
c) development of eﬀective methods for eﬄuent and waste control;
282

## Page 285

d) Development of appropriate genetic resource management plans at the hatchery level;
e) Development of controlled hatchery and genetically sound reproduction methods in order to
avoid seed collection from nature;
f) If seed collection from nature cannot be avoided, development of environmentally sound practices
for spat collecting operations, including use of selectiveﬁshing gear to avoid by-catch;
g) Use of native species and subspecies in mariculture;
h) Implementation of eﬀective measures to prevent the inadvertent release of mariculture species
and fertile polypoids;
i) Use of proper methods of breeding and proper places of releasing in order to protect genetic
diversity;
j) Minimizing the use of antibiotics through better husbandry techniques;
k) Use of selective methods in commercialﬁshing to avoid or minimize bycatch;
l) Considering traditional knowledge, where applicable, as a source to develop sustainable maricul-
ture techniques.
For more details on the variable construction, see the original source:
Convention on Biological Diversity, CBD (http://www.cbd.int/reports/search/default.shtml)-
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
283

## Page 286

3.32.19 Areas of observed blast (dynamite)ﬁshing (ohi_npblast)
Areas of observed blast (dynamite)ﬁshing. For more details on the variable construction, see the
original source:
Reefs at Risk Revisited (http://www.wri.org/publication/reefs-at-risk-revisited)
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
3.32.20 Areas of observed poisonﬁshing (ohi_npcyan)
Areas of observed poisonﬁshing. For more details on the variable construction, see the original
source:
Reefs at Risk Revisited (http://www.wri.org/publication/reefs-at-risk-revisited)
When using this variable, please cite both the OHI project and the original source.
284

## Page 287

Year A vailability
 Country A vailability
3.32.21 The Ocean Health Index (ohi_ohi)
The Ocean Health Index establishes reference points for achieving ten widely accepted socio-
ecological objectives and scores the oceans adjacent to 171 countries and territories on how success-
fully they deliver these goals. Evaluated globally and by country, these ten public goals represent
the wide range of beneﬁts that a healthy ocean can provide; each country’s overall score is the aver-
age of its respective goal scores. The ten socio-ecological objectives are: Food Provision, Artisanal
Fishing Opportunities, Natural Products, Carbon Storage, Coastal Protection, Coastal Livelihoods
& Economies, Tourism & Recreation, Sense of Place, Clean Waters, Biodiversity. The index varies
from 0 to 100.
Year A vailability
 Country A vailability
285

## Page 288

3.32.22 Coastal chemical pollution within 3 nm oﬀshore (ohi_pc3)
Coastal chemical pollution within 3 nautical miles (nm) oﬀshore. For more details on the variable
construction, see the original sources:
Halpern, B. S. et al. (2015). Spatial and temporal changes in cumulative human impacts on the
world’s ocean. Nature Communications 6(7615).
When using this variable, please cite both the OHI project and the original sources.
and
F AO’s statistical database F AOSTAT (http://faostat3.fao.org/faostat-gateway/go/to/browse/R/*/E).
When using this variable, please cite both the OHI project and the original sources.
Year A vailability
 Country A vailability
3.32.23 Chemical pollution (ohi_pchem)
Chemical pollution is measured as the average of land-based organic pollution, land-based inorganic
pollution, and ocean-based pollution from commercial shipping and port as proxies.
For more details on the variable construction, see the original sources:
Halpern, B. S. et al. (2015). Spatial and temporal changes in cumulative human impacts on the
world’s ocean. Nature Communications 6(7615).
and
F AO’s statistical database F AOSTAT (http://faostat3.fao.org/faostat-gateway/go/to/browse/R/*/E).
When using this variable, please cite both the OHI project and the original source.
286

## Page 289

Year A vailability
 Country A vailability
3.32.24 Coastal fertilizer pollution (ohi_pn3)
Coastal fertilizer pollution as a proxy for nutrient pollution within 3 nautical miles (nm) oﬀshore.
For more details on the variable construction, see the original sources:
Halpern, B. S. et al. (2015). Spatial and temporal changes in cumulative human impacts on the
world’s ocean. Nature Communications 6(7615).
and
F AO’s statistical database F AOSTAT (http://faostat3.fao.org/faostat-gateway/go/to/browse/R/*/E).
When using this variable, please cite both the OHI project and the original sources.
Year A vailability
 Country A vailability
287

## Page 290

3.32.25 Fertilizer pollution as a proxy for nutrient pollution (ohi_pnutrient)
Fertilizer pollution as a proxy for nutrient pollution. For more details on the variable construction,
see the original sources:
Halpern, B. S. et al. (2015). Spatial and temporal changes in cumulative human impacts on the
world’s ocean. Nature Communications 6(7615).
and
F AO’s statistical database F AOSTAT (http://faostat3.fao.org/faostat-gateway/go/to/browse/R/*/E).
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
3.32.26 Trash pollution (ohi_ptrash)
Trash pollution. Estimated by the tons of litter per km of beach collected during beach cleanups
organized by the Ocean Conservancys Trash Free Seas Alliance in 96 countries and locations.
For more details on the variable construction, see the original sources:
Eriksen M., Lebreton, L. C. M., Carson, H. S., Thiel, M., Moore, C. J. and Borerro, J. C. (2014).
Plastic pollution in the world’s oceans: more than 5 trillion plastic pieces weighing over 250,000
tons aﬂoat at sea. PLoS ONE 9:e111913.
and
J. Aﬄerbach et al. (2015). [Methods](https://github.com/OHI Science/ohiprep/tree/master/globalprep/CW_-
pressure_trash)
When using this variable, please cite both the OHI project and the original sources.
288

## Page 291

Year A vailability
 Country A vailability
3.32.27 Alien Species (ohi_saali)
Alien species are non-indigenous organisms introduced into an ecosystem that is not their native
habitat either by accident or intentionally. Measured by total counts of all invasive species according
to data from the Global Invasive Species Database (GIRD).
For more details on the variable construction, see the original source:
Molnar, J. L., Gamboa, R. L., Revenga C., Spalding, M. (2008). Assessing the global threat of
invasive species to marine biodiversity. Frontiers in Ecology and the Environment 6(485).
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
289

## Page 292

3.32.28 Percent direct employment in tourism (ohi_tjpt)
Percent direct employment in tourism. For more details on the variable construction, see the original
source:
World Travel and Tourism Council, WTTC (http://www.wttc.org/research/economic-data-search-
tool/)
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
3.32.29 CBD Survey: Tourism (ohi_tour)
CBD Survey: Tourism. A resilience measure based on questions 79, 80, and 82 from The Convention
on Biological Diversity country questionnaire (Third National Report to the CBD, from 2005).
Question 79: Has your country established mechanisms to assess, monitor and measure the impact
of tourism on biodiversity?
a) No;
b) No, but mechanisms are under development;
c) Yes, mechanisms are in place (please specify below);
d) Yes, existing mechanisms are under review.
Question 80: Has your country provided educational and training programmes to the tourism
operators so as to increase their awareness of the impacts of tourism on biodiversity and upgrade
the technical capacity at the local level to minimize the impacts?
a) No;
290

## Page 293

b) No, but programmes are under development;
c) Yes, programmes are in place (please describe below).
Question 82: Does your country provide indigenous and local communities with capacity-building
andﬁnancial resources to support their participation in tourism policy-making, development plan-
ning, product development and management?
a) No;
b) No, but relevant programmes are being considered;
c) Yes, some programmes are in place;
d) Yes, comprehensive programmes are in place.
For more details on the variable construction, see the original sources:
Convention on Biological Diversity, CBD (http://www.cbd.int/reports/search/default.shtml)
When using this variable, please cite both the OHI project and the original source.
Year A vailability
 Country A vailability
3.32.30 Sustainability index (ohi_trsust)
Sustainability index. For more details on the variable construction, see the original source:
World Economic Forum (http://www.weforum.org/issues/global-competitiveness)
When using this variable, please cite both the OHI project and the original source.
291

## Page 294

Year A vailability
 Country A vailability
3.32.31 CBD Survey: Water (ohi_water)
CBD Survey: water. A resilience measure based on question 153(d,f) from The Convention on
Biological Diversity country questionnaire (Third National Report to the CBD, from 2005).
Question 153(d,f): Do your country’s strategies and action plans include the following:
d) Instituting improved integrated marine and coastal area management (including catchments
management) in order to reduce sediment and nutrient loads into the marine environment;
f) Improving sewage and other waste treatment?
For more details on the variable construction, see the original source:
Convention on Biological Diversity, CBD (http://www.cbd.int/reports/search/default.shtml)
When using this variable, please cite both the OHI project and the original source.
292

## Page 295

Year A vailability
 Country A vailability
293

## Page 296

3.33 V-Party Dataset
Dataset by:Varieties of Democracy (V-Dem) Project
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
Lührmann, Anna et al. 2020.Varieties of Party Identity and Organization (V-Party) Dataset
V1
Pemstein, Daniel et al. 2020.The V-Dem Measurement Model: Latent Variable Analysis for
Cross-National and Cross-Temporal Expert-Coded Data
Link to the original source:https://www.v-dem.net/en/data/data/v-party-dataset/
V-Party provides expert-coded assessments of party organization and identity for most parties
in most countries over 1970-2019. Using V-Dem methodology (Coppedge et al., 2020), in January
2020, 665 experts rated the policy positions and organizational capacity of political parties across
elections in a given country. Speciﬁcally, as a general rule, experts coded data for all parties that
reached more than 5% of the vote share at a given election. The expert-coded data are aggregated
using V-Dems Bayesian Item Response Theory measurement model (Pemstein et al., 2020). The
result is data on 1,955 political parties across 1,560 elections in 169 countries; in total 6,330 party-
election year units. Typically, at least 4 coders provided their assessment per observation.
3.33.1 Environmental parties: share of seats (vparty_envseat)
The variable measures the share of seats in the lower chamber taken by the parties, for which
environmental protection is relevant to gain and keep voters, as agreed on by at least half of the
coders in the V-Party dataset.
The original variable from V-Party dataset - v2pasalie - measures the share of coders who answered
"12: Environmental protection" to the multiple-choice question "Which of the following issues are
most relevant for the party’s eﬀort to gain and keep voters?". We only keep parties that score 0.5
or higher on variable v2pasalie_12 and then calculate their share of seats in a given country-year
using v2paseatshare variable - Seat share the party gained in the election to the lower chamber.
294

## Page 297

Year A vailability
 Country A vailability
3.33.2 Environmental parties: share of votes (vparty_envvote)
The variable measures the share of votes to the lower chamber received by the parties, for which
environmental protection is relevant to gain and keep voters, as agreed on by at least half of the
coders in the V-Party dataset.
The original variable from V-Party dataset - v2pasalie - reports the share of coders who answered
"12: Environmental protection" to the multiple-choice question "Which of the following issues are
most relevant for the party’s eﬀort to gain and keep voters?". We only keep parties that score 0.5
or higher on variable v2pasalie_12 and then calculate their share of votes in a given country-year
using v2pavote variable - Vote share the party gained in the election to the lower chamber.
Year A vailability
 Country A vailability
295

## Page 298

3.34 World Development Indicators
Dataset by:The World Bank Group
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
World Bank. 2020.World Development Indicators
Link to the original source:http://data.worldbank.org/data-catalog/world-development-
indicators
The primary World Bank collection of development indicators, compiled from oﬃcially-recognized
international sources.
This is an adaptation of an original work by The World Bank. Views and opinions expressed in
the adaptation are the sole responsibility of the author or authors of the adaptation and are not
endorsed by The World Bank.
3.34.1 Agricultural irrigated land (% of total agricultural land) (wdi_agrland)
Agricultural land refers to the share of land area that is arable, under permanent crops, and under
permanent pastures. Arable land includes land deﬁned by the F AO as land under temporary crops
(double-cropped areas are counted once), temporary meadows for mowing or for pasture, land under
market or kitchen gardens, and land temporarily fallow. Land abandoned as a result of shifting
cultivation is excluded. Land under permanent crops is land cultivated with crops that occupy
the land for long periods and need not be replanted after each harvest, such as cocoa, coﬀee, and
rubber. This category includes land underﬂowering shrubs, fruit trees, nut trees, and vines, but
excludes land under trees grown for wood or timber. Permanent pasture is land used forﬁve or
more years for forage, including natural and cultivated crops.
296

## Page 299

Year A vailability
 Country A vailability
3.34.2 Arable land (% of land area) (wdi_araland)
Arable land includes land deﬁned by the F AO as land under temporary crops (double-cropped areas
are counted once), temporary meadows for mowing or for pasture, land under market or kitchen
gardens, and land temporarily fallow. Land abandoned as a result of shifting cultivation is excluded.
Year A vailability
 Country A vailability
3.34.3 Land area (sq. km) (wdi_area)
Land area is a country’s total area, excluding area under inland water bodies, national claims to
continental shelf, and exclusive economic zones. In most cases the deﬁnition of inland water bodies
includes major rivers and lakes.
297

## Page 300

Year A vailability
 Country A vailability
3.34.4 Land area where elevation is below 5 meters (% of total land area) (wdi_-
areabelow)
Land area below 5m is the percentage of total land where the elevation is 5 meters or less.
Year A vailability
 Country A vailability
3.34.5 CO2 emissions (metric tons per capita) (wdi_co2)
Carbon dioxide (CO2) emissions stem from the burning of fossil fuels and the manufacture of
cement. They include carbon dioxide produced during consumption of solid, liquid, and gas fuels
and gasﬂaring.
298

## Page 301

Year A vailability
 Country A vailability
3.34.6 Forest area (% of land area) (wdi_forest)
Forest area is land under natural or planted stands of trees of at least 5 meters in situ, whether
productive or not, and excludes tree stands in agricultural production systems (for example, in fruit
plantations and agroforestry systems) and trees in urban parks and gardens.
Year A vailability
 Country A vailability
3.34.7 Fossil fuel energy consumption (% of total) (wdi_fossil)
Fossil fuel energy consumption as a percentage of total energy consumption. Fossil fuel comprises
coal, oil, petroleum, and natural gas products.
299

## Page 302

Year A vailability
 Country A vailability
3.34.8 Internally displaced persons, new displacement-disasters (number) (wdi_-
idpdis)
Internally displaced persons, new displacement associated with disasters (number of people). Inter-
nally displaced persons are deﬁned according to the 1998 Guiding Principles (http://www.internal-
displacement.org/publications/1998/ocha-guiding-principles-on-internal-displacement) as people or
groups of people who have been forced or obliged toﬂee or to leave their homes or places of habit-
ual residence, in particular as a result of armed conﬂict, or to avoid the eﬀects of armed conﬂict,
situations of generalized violence, violations of human rights, or natural or human-made disasters
and who have not crossed an international border. "New Displacement" refers to the number of
new cases or incidents of displacement recorded, rather than the number of people displaced. This
is done because people may have been displaced more than once.
Year A vailability
 Country A vailability
300

## Page 303

3.34.9 Policy and institutions for environmental sustainability (wdi_piesr)
Policy and institutions for environmental sustainability measures the extent to which environmental
policies foster the protection and sustainable use of natural resources and the management of
pollution. The indicator ranges from 1 (low) to 6 (high).
Year A vailability
 Country A vailability
3.34.10 A verage precipitation in depth (mm per year) (wdi_precip)
A verage precipitation is the long-term average in depth (over space and time) of annual precipitation
in the country in millimeters (mm). Precipitation is deﬁned as any kind of water that falls from
clouds as a liquid or a solid.
Year A vailability
 Country A vailability
301

## Page 304

3.34.11 Terrestrial protected areas (% of total land area) (wdi_tpa)
Terrestrial protected areas are totally or partially protected areas of at least 1,000 hectares that
are designated by national authorities as scientiﬁc reserves with limited public access, national
parks, natural monuments, nature reserves or wildlife sanctuaries, protected landscapes, and areas
managed mainly for sustainable use. Marine areas, unclassiﬁed areas, littoral (intertidal) areas,
and sites protected under local or provincial law are excluded. World Database on Protected Areas
(WDPA) where the compilation and management is carried out by United Nations Environment
World Conservation Monitoring Centre (UNEP-WCMC) in collaboration with governments, non-
governmental organizations, academia, and industry. The data are available online through the
Protected Planet website (https://www.protectedplanet.net/).
Year A vailability
 Country A vailability
302

## Page 305

3.35 World Values Survey
Dataset by:World Values Survey
If you use any of these variables, make sure to cite the original source and QoG Data. Our
suggested citation for this dataset is:
EVS. 2020.European Values Study 2017: Integrated Dataset (EVS 2017).url:https :
//doi.org/10.4232/1.13560
EVS. 2020.European Values Study Longitudinal Data File 1981-2008 (EVS 1981-2008).url:
https://doi.org/10.4232/1.13486
Inglehart, R. et al. 2014.World Values Survey: Round Six - Country-Pooled Dataﬁle Version.
url:www.worldvaluessurvey.org/WVSDocumentationWV6.jsp
Haerpfer, C. et al. 2020.World Values Survey: Round Seven Country-Pooled Dataﬁle.url:
http://www.worldvaluessurvey.org/WVSDocumentationWV7.jsp
Link to the original source:http://www.worldvaluessurvey.org/
The World Values Survey is a global network of social scientists studying changing values and
their impact on social and political life, led by an international team of scholars, with the WVS as-
sociation and secretariat headquartered in Stockholm, Sweden. The European Values Study started
in 1981 when a thousand citizens in the European Member States of that time were interviewed
using standardized questionnaires. Every nine years, the survey is repeated in a variable number of
countries. The fourth wave in 2008 covers no less than 47 European countries/regions, from Iceland
to Georgia and from Portugal to Norway. EVS is cooperating with WVS for the data collection in
Europe and both datasets can be integrated.
The variables are country averages calculated using the population weight provided by WVS/EVS.
303

## Page 306

3.35.1 Active memberships in environmental organizations (%) (wvs_ameop)
Percent of respondents mentioning they are active members in an environmental organization in
the question: "Now I am going to read out a list of voluntary organizations; for each one, could
you tell me whether you are a member, an active member, an inactive member, or not a member of
that type of organization?". A higher score means that more people are active members of environ-
mental organizations. A lower score means that fewer people are active members of environmental
organizations.
Year A vailability
 Country A vailability
3.35.2 Conﬁdence in environmental organizations (mean) (wvs_ceom)
A verage reply to the question: "I am going to name a number of organizations. For each one, could
you tell me how much conﬁdence you have in them: is it a great deal of conﬁdence, quite a lot of
conﬁdence, not very much conﬁdence, or none at all? - Environmental organizations":
1) A great deal;
2) Quite a lot;
3) Not very much;
4) None at all.
Answers "Don’t know" and "No answer" are deleted. The higher the score, the lower the conﬁdence
in environmental organizations.
304

## Page 307

Year A vailability
 Country A vailability
3.35.3 Donations to ecological organizations (%) (wvs_deop)
Percent of "yes"-replies to the question: "During the past two years, have you given money to an
ecological organization?". A higher score means that more people have donated money to environ-
mental organizations. A lower score means that fewer people have donated money to environmental
organizations.
Year A vailability
 Country A vailability
3.35.4 Protecting environment vs economic growth (%) (wvs_epmip)
Percent of replies mentioning "Protecting the environment should be given priority" to the question:
"Here are two statements people sometimes make when discussing the environment and economic
growth. Which of them comes closer to your own point of view?
A. Protecting the environment should be given priority, even if it causes slower economic growth
305

## Page 308

and some loss of jobs
B. Economic growth and creating jobs should be the top priority, even if the environment suﬀers
to some extent".
A higher score means that more people prioritize the environment over economic growth and jobs.
A lower score means that more people prioritize economic growth and jobs over the environment.
Year A vailability
 Country A vailability
3.35.5 Environment is the most serious problem (%) (wvs_epmpp)
Percent of replies mentioning "Environmental pollution" to the question: "I’m going to read out
some problems. Please indicate which of the following problems you consider the most serious one
for the world as a whole?". A higher score means that more people prioritize the environment over
other serious world problems. A lower score means that fewer people prioritize the environment
over other serious world problems.
Year A vailability
 Country A vailability
306

## Page 309

3.35.6 Inactive memberships in environmental organizations (%) (wvs_imeop)
Percent of respondents mentioning they are inactive members in an environmental organization in
the question: "Now I am going to read out a list of voluntary organizations; for each one, could
you tell me whether you are a member, an active member, an inactive member, or not a member
of that type of organization?". A higher score means that there are more inactive members in
environmental organizations among the general population. A lower score implies that there are
fewer inactive members in environmental organizations among the general population.
Year A vailability
 Country A vailability
3.35.7 Participation in environmental protests (%) (wvs_pedp)
Percent of "yes"-replies to the question: "During the past two years, have you participated in a
demonstration for some environmental cause?". A higher score means that there are more people
who have participated in environmental protests. A lower score means that there are fewer people
who have participated in environmental protests.
Year A vailability
 Country A vailability
307

## Page 310

3.35.8 Important to look after the environment (mean) (wvs_ploem)
A verage reply to the question: "Now I will brieﬂy describe some people. Using this card, would you
please indicate for each description whether that person is very much like you, like you, somewhat
like you, not like you, or not at all like you? - Looking after the environment is important to this
person; to care for nature and save life resources":
1) Very much like me;
2) Like me;
3) Somewhat like me;
4) A little like me;
5) Not like me;
6) Not at all like me.
Answers "Don’t know" and "No answer" are deleted. A higher score means that fewer people believe
that it is important to look after the environment. A lower score means that more people believe
that it is important to look after the environment.
Year A vailability
 Country A vailability
308

## Page 311

4 Appendix
Country name ccode ccodealp Data
from
Data
to
Comment
Afghanistan 4 AFG 1946 2020 Independence from the UK 1919
Albania 8 ALB 1946 2020 Independence recognized by the Great Powers 1913
Algeria 12 DZA 1963 2020 Independence from France 1962
Andorra 20 AND 1946 2020 Independence from the Crown of Aragon 1278
Angola 24 AGO 1976 2020 Independence from Portugal 1975
Antigua and Bar-
buda
28 ATG 1982 2020 Independence from the UK 1981
Argentina 32 ARG 1946 2020 Independence from Spain 1816
Armenia 51 ARM 1992 2020 Independence from the Soviet Union recognized 1991
Australia 36 AUS 1946 2020 Statute of Westminster Adoption Act 1942
Austria 40 AUT 1955 2020 The State Treaty signed in Vienna 1955
Azerbaijan 31 AZE 1992 2020 Independence from the Soviet Union 1991
Bahamas 44 BHS 1974 2020 Independence from the UK 1973
Bahrain 48 BHR 1972 2020 End of treaties with the UK 1971
Bangladesh 50 BGD 1971 2020 Independence from Pakistan 1971
Barbados 52 BRB 1967 2020 Independence from the UK 1966
Belarus 112 BLR 1992 2020 Independence from the Soviet Union 1991
Belgium 56 BEL 1946 2020 Independence from the Netherlands recognized 1839
Belize 84 BLZ 1982 2020 Independence from the UK 1981
Benin 204 BEN 1961 2020 Independence from France 1960
Bhutan 64 BTN 1946 2020 Monarchy established 1907
Bolivia 68 BOL 1946 2020 Independence from Spain recognized 1847
Bosnia and Herze-
govina
70 BIH 1992 2020 Independence from Yugoslavia 1992
Botswana 72 BW A 1967 2020 Independence from the UK 1966
Brazil 76 BRA 1946 2020 Independence from the UK of Portugal, Brazil & the Al-
garve 1825
Brunei 96 BRN 1984 2020 Independence from the UK 1984
Bulgaria 100 BGR 1946 2020 Independence from Ottoman Empire 1909
Burkina Faso 854 BF A 1961 2020 Independence from France 1960
Burundi 108 BDI 1963 2020 UN Trust Territory ceased to exist 1962
Cambodia 116 KHM 1954 2020 Independence from France 1953
Cameroon 120 CMR 1960 2020 Independence from France 1960
Canada 124 CAN 1946 2020 Statute of Westminster 1931
Cape Verde 132 CPV 1976 2020 Independence from Portugal 1975
309

## Page 312

Country name ccode ccodealp Data
from
Data
to
Comment
Central African Re-
public
140 CAF 1961 2020 Independence from France 1960
Chad 148 TCD 1961 2020 Independence from France 1960
Chile 152 CHL 1946 2020 Independence from Spain recognized 1844
China 156 CHN 1946 2020 Uniﬁcation of China under the Qin Dynasty 221 BC
Colombia 170 COL 1946 2020 Independence from Spain recognized 1819
Comoros 174 COM 1976 2020 Independence from France 1975
Congo, Democratic
Republic
180 COD 1960 2020 Independence from Belgium 1960
Congo, Republic of 178 COG 1961 2020 Independence from France 1960
Costa Rica 188 CRI 1946 2020 Independence from United Provinces of Central America
1847
Cote d’Ivoire 384 CIV 1961 2020 Independence from France 1960
Croatia 191 HR V 1992 2020 Independence 1991
Cuba 192 CUB 1946 2020 Independence from the United States 1902
Cyprus (-1974) 993 CYP 1961 1974 Independence from the UK 1960
Cyprus (1975-) 196 CYP 1975 2020 Division of the island 1974
Czech Republic 203 CZE 1993 2020 Dissolution of Czechoslovakia 1993
Czechoslovakia 200 CSK 1946 1992 Independence 1918, Liberation 1945
Denmark 208 DNK 1946 2020 Consolidaton 8th century
Djibouti 262 DJI 1977 2020 Independence from France 1977
Dominica 212 DMA 1979 2020 Independence from the UK 1978
Dominican Republic 214 DOM 1946 2020 Independence from Spain 1865
Ecuador 218 ECU 1946 2020 Independence from Gran Colombia 1830
Egypt 818 EGY 1946 2020 Indepencence from the UK 1922
El Salvador 222 SL V 1946 2020 Independence from the Greater Republic of Central Amer-
ica 1898
Equatorial Guinea 226 GNQ 1969 2020 Independence from Spain 1968
Eritrea 232 ERI 1993 2020 Independence from Ethiopia 1993
Estonia 233 EST 1992 2020 Independence restored 1991
Eswatini (formerly
Swaziland)
748 SWZ 1969 2020 Independence from British mandate 1968
Ethiopia (-1992) 230 ETH 1946 1992 Empire of Ethiopia 1137
Ethiopia (1993-) 231 ETH 1993 2020 Eritrean Independence 1993
Fiji 242 FJI 1971 2020 Independence from the UK 1970
Finland 246 FIN 1946 2020 Independence from Soviet Russia recognized 1918
France (-1962) 991 FRA 1946 1962 French Republic 1792
310

## Page 313

Country name ccode ccodealp Data
from
Data
to
Comment
France (1963-) 250 FRA 1963 2020 Algeria Independence from France 1962
Gabon 266 GAB 1961 2020 Independence from France 1960
Gambia 270 GMB 1965 2020 Independence from the UK 1965
Georgia 268 GEO 1992 2020 Independence from the Soviet Union 1991
Germany 276 DEU 1991 2020 Reuniﬁcation 1990
Germany, East 278 DDR 1950 1990 Established 1949
Germany, West 280 DEU 1949 1990 Established 1949
Ghana 288 GHA 1957 2020 Independence from the British Empire 1957
Greece 300 GRC 1946 2020 Independence from the Ottoman Empire recognized 1830
Grenada 308 GRD 1974 2020 Independence from the UK 1974
Guatemala 320 GTM 1946 2020 Independence from the First Mexican Empire 1823
Guinea 324 GIN 1959 2020 Independence from France 1958
Guinea-Bissau 624 GNB 1975 2020 Independence from Portugal recognized 1974
Guyana 328 GUY 1966 2020 Independence from the UK 1966
Haiti 332 HTI 1946 2020 Independence recognized 1825
Honduras 340 HND 1946 2020 Independence declared as Honduras 1838
Hungary 348 HUN 1946 2020 Secession from Austria-Hungary 1918
Iceland 352 ISL 1946 2020 Kingdom of Iceland 1918
India 356 IND 1948 2020 Independence from the UK (Dominion) 1947
Indonesia 360 IDN 1950 2020 Independence from the Netherlands recognized 1949
Iran 364 IRN 1946 2020 Safavid Empire 1501
Iraq 368 IRQ 1946 2020 Independence from the UK 1932
Ireland 372 IRL 1946 2020 The Anglo-lrish Treaty 1921
Israel 376 ISR 1948 2020 Independence from Mandatory Palestine 1948
Italy 380 ITA 1946 2020 Uniﬁcation 1861
Jamaica 388 JAM 1963 2020 Independence from the UK 1962
Japan 392 JPN 1946 2020 National Foundation Day 660 BC
Jordan 400 JOR 1946 2020 League of Nation mandate ended 1946
Kazakhstan 398 KAZ 1992 2020 Independence from the Soviet Union 1991
Kenya 404 KEN 1964 2020 Independence from the UK 1963
Kiribati 296 KIR 1980 2020 Independence from the UK 1979
Korea, North 408 PRK 1949 2020 Division of Korea 1948
Korea, South 410 KOR 1948 2020 Division of Korea 1948
Kuwait 414 KWT 1961 2020 Independence from the UK 1961
Kyrgyzstan 417 KGZ 1992 2020 Independence from the Soviet Union 1991
Laos 418 LAO 1954 2020 Independence from France 1953
311

## Page 314

Country name ccode ccodealp Data
from
Data
to
Comment
Latvia 428 L V A 1992 2020 Independence from the Soviet Union 1991
Lebanon 422 LBN 1946 2020 Independence from France 1943
Lesotho 426 LSO 1967 2020 Independence from the UK 1966
Liberia 430 LBR 1946 2020 Independence from the American Colonization Society
1847
Libya 434 LBY 1952 2020 Released from British and French oversight 1951
Liechtenstein 438 LIE 1946 2020 Independence from German Confederation 1866
Lithuania 440 LTU 1992 2020 Independence from the Soviet Union 1991
Luxembourg 442 LUX 1946 2020 End of Personal Union 1890
Madagascar 450 MDG 1960 2020 Independence from France 1960
Malawi 454 MWI 1965 2020 Independence from the UK 1964
Malaysia (-1965) 992 MYS 1964 1965 Federation of Malaya, N Bomeo, Sarawak, Singapore 1963
Malaysia (1966-) 458 MYS 1966 2020 Singapore separation from Malaysia 1965
Maldives 462 MDV 1966 2020 Independence from the UK 1965
Mali 466 MLI 1961 2020 Independence from France 1960
Malta 470 MLT 1965 2020 Independence from the UK 1964
Marshall Islands 584 MHL 1987 2020 Independence from Compact of Free Associaton 1986
Mauritania 478 MRT 1961 2020 Independence from France 1960
Mauritius 480 MUS 1968 2020 Independence from the UK 1968
Mexico 484 MEX 1946 2020 Independence from Spain recognized 1821
Micronesia 583 FSM 1987 2020 Independence from Compact of Free Associaton 1986
Moldova 498 MDA 1992 2020 Independence from the Soviet Union 1991
Monaco 492 MCO 1946 2020 Franco-Monegasque Treaty 1861
Mongolia 496 MNG 1946 2020 Independence from the Qin Dynasty 1911
Montenegro 499 MNE 2006 2020 Independence from Serbia and Montenegro 2006
Morocco 504 MAR 1956 2020 Independence from France and Spain 1956
Mozambique 508 MOZ 1975 2020 Independence from the Portuguese Republic 1975
Myanmar 104 MMR 1948 2020 Independence from the UK 1948
Namibia 516 NAM 1990 2020 Independence from South Africa 1990
Nauru 520 NRU 1968 2020 Independence from UN Trusteeship 1968
Nepal 524 NPL 1946 2020 Kingdom declared 1768
Netherlands 528 NLD 1946 2020 Independence from the Spanish Empire in 1648 with the
treaty of Munster
New Zealand 554 NZL 1948 2020 Statute of Westminster Adoption Act 1947
Nicaragua 558 NIC 1946 2020 Independence from the Federal Republic of Central Amer-
ica 1838
Niger 562 NER 1961 2020 Independence from France 1960
312

## Page 315

Country name ccode ccodealp Data
from
Data
to
Comment
Nigeria 566 NGA 1961 2020 Independence from the UK 1960
Norway 578 NOR 1946 2020 Dissolution of union with Sweden 1905
North Macedonia 807 MKD 1993 2020 Independence from Yugolsavia recognized 1993
Oman 512 OMN 1946 2020 Imamate established 751
Pakistan (-1970) 997 PAK 1948 1970 Independence from the UK 1947
Pakistan (1971-) 586 PAK 1971 2020 Bangladesh independence from Pakistan 1971
Palau 585 PL W 1995 2020 Independence from Compact of Free Association with the
US 1994
Panama 591 PAN 1946 2020 Independence from Colombia 1903
Papua New Guinea 598 PNG 1976 2020 Independence from Australia 1975
Paraguay 600 PRY 1946 2020 Independence from Spain 1811
Peru 604 PER 1946 2020 Independence from Span recognized 1824
Philippines 608 PHL 1947 2020 Independence from the United States 1946
Poland 616 POL 1946 2020 Reconstitution of Poland 1918
Portugal 620 PRT 1946 2020 Independence from Kingdom of Leon recognzed 1143
Qatar 634 QAT 1972 2020 Independence from the UK 1971
Romania 642 ROU 1946 2020 Independence from the Ottoman Empire 1878
Russia 643 RUS 1992 2020 Russian Federation 1991
Rwanda 646 R W A 1963 2020 Independence from Belgium 1962
Samoa 882 WSM 1962 2020 Independence from New Zealand 1962
San Marino 674 SMR 1946 2020 Independence from the Roman Empire 301
Sao Tome and
Principe
678 STP 1976 2020 Independence from Portugal 1975
Saudi Arabia 682 SAU 1946 2020 Kingdom founded 1932
Senegal 686 SEN 1961 2020 Withdrawal from the Mali Federation 1960
Serbia 688 SRB 2006 2020 Independent republic 2006
Serbia and Montene-
gro
891 SCG 1992 2005 Established 1992, Dissolution 2006
Seychelles 690 SYC 1976 2020 Independence from the UK 1976
Sierra Leone 694 SLE 1961 2020 Independence from the UK 1961
Singapore 702 SGP 1966 2020 Separation from Malaysia 1965
Slovakia 703 SVK 1993 2020 Independence from Czechoslovakia 1993
Slovenia 705 SVN 1991 2020 Independence from Yugoslavia 1991
Solomon Islands 90 SLB 1979 2020 Independence from the UK 1978
Somalia 706 SOM 1961 2020 Union, Independence and Constitution 1960
South Africa 710 ZAF 1946 2020 The Union of South Africa came into being 1910
South Sudan 728 SSD 2011 2020 Separation from Sudan in 2011
313

## Page 316

Country name ccode ccodealp Data
from
Data
to
Comment
Spain 724 ESP 1946 2020 Nation State 1812
Sri Lanka 144 LKA 1948 2020 Independence from the UK(Dominion) 1948
St Kitts and Nevis 659 KNA 1984 2020 Independence from the UK 1983
St Lucia 662 LCA 1979 2020 Independence from the UK 1979
St. Vincent & the
Grenadines
670 VCT 1980 2020 Independence from the UK 1979
Sudan (-2011) 736 SDN 1956 2011 Independence from the UK and Egypt 1956
Sudan (2012-) 729 SDN 2012 2020 South Sudanese independence 2011
Suriname 740 SUR 1976 2020 Independence from the Netherlands 1975
Sweden 752 SWE 1946 2020 Consolidation Middle Ages
Switzerland 756 CHE 1946 2020 Peace of Westphalia 1648
Syria 760 SYR 1946 2020 Independence from France 1946
Taiwan 158 TWN 1950 2020 Kuomintang retreat to Taiwan 1949
Tajikistan 762 TJK 1992 2020 Independence from the Soviet Union 1991
Tanzania 834 TZA 1964 2020 Merger (Tanganyika, Zanzibar and Pemba) 1964
Thailand 764 THA 1946 2020 Rattanakosin Kingdom 1782
Tibet 994 XTI 1946 1950 Independence from Qing Dynasty 1913
Timor-Leste 626 TLS 2002 2020 Independence from Indonesia 2002
Togo 768 TGO 1960 2020 Independence from France 1960
Tonga 776 TON 1970 2020 Independence from British protection 1970
Trinidad and Tobago 780 TTO 1963 2020 Independence from the UK 1962
Tunisia 788 TUN 1956 2020 Independence from France 1956
Turkey 792 TUR 1946 2020 Secession from the Ottoman Empire 1923
Turkmenistan 795 TKM 1992 2020 Independence from the Soviet Union 1991
Tuvalu 798 TUV 1979 2020 Independence from the UK 1978
Uganda 800 UGA 1963 2020 Independence from the UK 1962
Ukraine 804 UKR 1992 2020 Independence from the Soviet Union 1991
United Arab Emi-
rates
784 ARE 1972 2020 UK treaties ended 1971
United Kingdom 826 GBR 1946 2020 Acts of Union 1707
United States 840 USA 1946 2020 Independence from the Kingdom of Great Britain recog-
nized 1783
Uruguay 858 URY 1946 2020 Independence from the Empire of Brazil recognized 1828
USSR 810 SUN 1946 1991 Treaty of Creation 1922, Union dissolved 1991
Uzbekistan 860 UZB 1992 2020 Independence from the Soviet Union 1991
Vanuatu 548 VUT 1981 2020 Independence from France and the UK 1980
Venezuela 862 VEN 1946 2020 Independence from Gran Colombia recognized 1845
314

## Page 317

Country name ccode ccodealp Data
from
Data
to
Comment
Vietnam 704 VNM 1977 2020 Reuniﬁcation 1976
Vietnam, North 998 VNM 1955 1976 Geneva Accords. Partition of the County, 1954
Vietnam, South 999 VDR 1955 1976 Geneva Accords. Partition of the County, 1954
Yemen 887 YEM 1990 2020 Uniﬁcation 1990
Yemen, North 886 YEM 1946 1989 Independence from the Ottoman Empire 1918
Yemen, South 720 YMD 1968 1989 Independence from the UK 1967
Yugoslavia 890 YUG 1946 1991 The union of the State of Slovenes, Croats, Serbs & Serbia
est 1918
Zambia 894 ZMB 1965 2020 Independence from the UK 1964
Zimbabwe 716 ZWE 1966 2020 The Unilateral Declarator of Independence (UDI) of
Rhodesia 1965
315

## Page 318

References
Aklin, Michaël and Johannes Urpelainen (2014). “The global spread of environmental ministries:
domestic–international interactions”. In:International Studies Quarterly58.4, pp. 764–780.doi:
10.1111/isqu.12119.
Bättig, Michèle B, Simone Brander, and Dieter M Imboden (2008). “Measuring countries coopera-
tion within the international climate change regime”. In:Environmental Science & Policy11.6,
pp. 478–489.doi:10.1016/j.envsci.2008.04.003.
Bernauer, Thomas, Tobias Böhmelt, and Vally Koubi (2013). “Is there a democracy–civil society
paradox in global environmental governance?” In:Global Environmental Politics13.1, pp. 88–
107.doi:10.1162/GLEP_a_00155.
Boräng, Frida et al. (2019). “Committing to the climate: a global study of accountable climate
targets”. In:Sustainability11.7, p. 1861.doi:10.3390/su11071861.
Botta, Enrico and Tomasz Kozluk (2014). “Measuring environmental policy stringency in OECD
countries: A composite index approach”. In:OECD Economics Department Working Papers,
No. 1177, OECD Publishing. Date accessed: 23 August 2020.
Center for International Earth Science Information Network - CIESIN - Columbia University (2019).
Natural Resource Protection and Child Health Indicators, 2019 Release. Accessed on: 13-11-2020.
url:https://doi.org/10.7927/r6mv-sv82.
Crippa, Monica, Diego Guizzardi, Marilena Muntean, E. Schaaf, et al. (2020).Fossil CO2 emissions
of all world countries - 2020 Report. Date accessed: 16 April 2020.doi:10 . 2760 / 143674 ,
JRC121460.url:https://edgar.jrc.ec.europa.eu/overview.php?v=booklet2020.
Crippa, Monica, Diego Guizzardi, Marilena Muntean, Edwin Schaaf, et al. (2019).EDGAR v5.0
Global Air Pollutant Emissions. Date accessed: 16 April 2020.url:http://data.europa.eu/
89h/377801af-b094-4943-8fdc-f79a7c0c2d19.
Crippa, Monica, Eﬁsio Solazzo, et al. (2020). “High resolution temporal proﬁles in the Emissions
Database for Global Atmospheric Research”.
Donner, Sabine, Hauke Hartmann, and Robert Schwarz (2020).Transformation Index of the Ber-
telsmann Stiftung 2020. Bertelsmann Stiftung.url:http://www.bti-project.org.
Eskander, S. and Fankhauser S. (2020). “Reduction in greenhouse gas emissions from national
climate legislation”. In:Nature Climate Change10. Date accessed: pp. 750–756.doi:10.1038/
s41558- 020- 0831- z.url:https://github.com/smsu1979/Eskander- Fankhauser- NCC-
2020-.
European Commission, Joint Research Centre (EC-JRC)/Netherlands Environmental Assessment
Agency (PBL) (2020).Emissions Database for Global Atmospheric Research (EDGAR), release
EDGAR v5.0 (1970 - 2015) of April 2020. Date accessed: 27 February 2021.url:https :
//edgar.jrc.ec.europa.eu/overview.php?v=50_AP.
EVS (2020a).European Values Study 2017: Integrated Dataset (EVS 2017).url:https://doi.
org/10.4232/1.13560.
— (2020b).European Values Study Longitudinal Data File 1981-2008 (EVS 1981-2008).url:
https://doi.org/10.4232/1.13486.
F AO (2021).AQUASTAT Database. Date accessed: 10 June 2021.url:http://www.fao.org/
aquastat/statistics/query/index.html.
Food and Agricultural Organization of the United Nations (2020).Global Forest Resources Assess-
ments.url:http://www.fao.org/forest-resources-assessment/en/.
316

## Page 319

Global Footprint Network (2019).National Footprint and Biocapacity Accounts (1961-2016), 2019
Edition. Date accessed: 21 October 2020.url:https://data.footprintnetwork.org.
Grantham Research Institute on Climate Change and the Environment and Sabin Center for Cli-
mate Change Law (2021).Climate Change Laws of the World database. Date accessed: 7 June
2021.url:climate-laws.org.
Guha-Sapir, Debarati (2020). “EM-DAT, the Emergency Events Database”. Date accessed 23 De-
cember 2020.url:www.emdat.be.
Haerpfer, C. et al. (2020).World Values Survey: Round Seven Country-Pooled Dataﬁle.url:http:
//www.worldvaluessurvey.org/WVSDocumentationWV7.jsp.
Halpern, Benjamine et al. (Aug. 2012). “An index to assess the health and beneﬁts of the global
ocean”. In:Nature488, pp. 615–620.doi:10.1038/nature11397.
— (2018).Ocean Health Index. Date accessed: 2 October 2020.url:https://github.com/OHI-
Science/ohi-global/releases.
Harris, Ian et al. (2020). “Version 4 of the CRU TS monthly high-resolution gridded multivariate
climate dataset”. In:Scientiﬁc Data7.1, p. 109.issn: 2052-4463.doi:10.1038/s41597-020-
0453-3.url:https://doi.org/10.1038/s41597-020-0453-3.
Heichel, Stephan et al. (2008). “Research design, variables and data”. In:Environmental Policy
Convergence in Europe: The Impact of International Institutions and Trade. Ed. by Katha-
rina Holzinger, Christoph Knill, and Helge Jörgens. Date accessed: 24 March 2020. Cambridge:
Cambridge University Press, pp. 64–97.url:https : / / www . polver . uni - konstanz . de /
en / holzinger / research / research - projects / enviromental - policy - convergence - in -
europe-envipolcon/project-deliverables/.
Holzinger, Katharina, Christoph Knill, and Thomas Sommerer (2011). “Is there convergence of
national environmental policies? An analysis of policy outputs in 24 OECD countries”. In:
Environmental politics20.1. Date accessed: 23 July 2020, pp. 20–41.url:https://www.polver.
uni - konstanz . de / holzinger / research / research - projects / policy - wandel - in - der -
umweltpolitik - der - einfluss - von - nationalen - vetospielern - und - transnationalem -
policy-learning/der-datensatz-environmental-policy-chance-envipolchange/.
Inglehart, R. et al. (2014).World Values Survey: Round Six - Country-Pooled Dataﬁle Version.
url:www.worldvaluessurvey.org/WVSDocumentationWV6.jsp.
ISSP Research Group (1995).International Social Survey Programme: Environment I - ISSP 1993.
GESIS Data Archive, Cologne. ZA2450 Dataﬁle Version 1.0.0, https://doi.org/10.4232/1.2450.
Date accessed: 17 February 2016.doi:10.4232/1.2450.
— (2003).International Social Survey Programme: Environment II - ISSP 2000. GESIS Data
Archive, Cologne. ZA3440 Dataﬁle Version 1.0.0, https://doi.org/10.4232/1.3440. Date ac-
cessed: 17 February 2016.doi:10.4232/1.3440.
— (2019).International Social Survey Programme: Environment III - ISSP 2010. GESIS Data
Archive, Cologne. ZA5500 Dataﬁle Version 3.0.0, https://doi.org/10.4232/1.13271. Date ac-
cessed: 17 February 2016.doi:10.4232/1.13271.
Lührmann, Anna et al. (2020).Varieties of Party Identity and Organization (V-Party) Dataset V1.
Date accessed: 22 February 2021.doi:10.23696/vpartydsv1.
Mitchell, Ronald B et al. (2020). “What we know (and could know) about international environ-
mental agreements”. In:Global Environmental Politics20.1, pp. 103–121.
Mitchell, Ronald B. (2020).International Environmental Agreements Database Project (Version
2020.1). Date accessed: 15 November 2020.url:http://iea.uoregon.edu/.
317

## Page 320

NSD - Norwegian Centre for Research Data (2020).European Social Survey Cumulative File, ESS
1-9. Date accessed: 17 February 2021.doi:10 . 21338 / NSD - ESS - CUMULATIVE.url:http :
//www.europeansocialsurvey.org/.
Organisation for Economic Co-operation and Development (OECD) (2020a).Environmental pro-
tection expenditure account (EPEA). Date accessed: 13 May 2020.doi:10.1787/7cf875d3-en.
url:https://ec.europa.eu/eurostat/web/products-manuals-and-guidelines/-/KS-GQ-
17-004.
— (2020b).Environmentally adjusted multifactor productivity. Date accessed: 13 May 2020.doi:
10.1787/55a11744-en.url:oe.cd/eamfp.
— (2020c).Exposure to PM2.5 in countries and regions (Edition 2018). Date accessed: 13 May
2020.doi:10.1787/bbb42e4d- en.url:https://www.oecd- ilibrary.org/environment/
data/oecd-environment-statistics_env-data-en.
— (2020d).Green Growth Indicators Database. Date accessed: 23 August 2020.doi:10 . 1787 /
data-00665-en.url:https://stats.oecd.org/.
— (2020e).Policy Instruments for the Environment (PINE). Date accessed: 13 May 2020.doi:
10.1787/env-data-en.url:oe.cd/pine.
Pemstein, Daniel et al. (2020).The V-Dem Measurement Model: Latent Variable Analysis for Cross-
National and Cross-Temporal Expert-Coded Data.
Rodríguez, Miguel Cárdenas, Ivan Hai, and Martin Souchier (2018). “Environmentally adjusted
multifactor productivity: methodology and empirical results for OECD and G20 countries”. In:
Ecological Economics153, pp. 147–160.
Ross, Michael and Paasha Mahdavi (2015).Oil and Gas Data, 1932-2014.doi:10 . 7910 / DVN /
ZTPW0Y.url:http://dx.doi.org/10.7910/DVN/ZTPW0Y.
Schiller, Christof, Thorsten Hellmann, and Pia Paulini (2020). “Sustainable Governance Indicators
2020”. In:Bertelsmann Stiftung. Date accessed: 6 August 2020.url:https : / / www . sgi -
network.org/2020/Downloads.
Shaddick, Gavin et al. (2018). “Data integration for the assessment of population exposure to
ambient air pollution for global burden of disease assessment”. In:Environmental Science &
Technology52.16, pp. 9069–9078.
The World Bank Group (2021).Climate Change Knowledge Portal. Date accessed 2 June 2021.
url:https://climateknowledgeportal.worldbank.org.
Wendling, Z.A. et al. (2020). “2020 Environmental Performance Index”. In:New Haven, CT: Yale
Center for Environmental Law and Policy. Date accessed: 9 September 2021.url:https :
//epi.envirocenter.yale.edu/.
World Bank (2020).World Development Indicators.
World Resource Institute and the Access Initiative (2015).Environmental Democracy Index. Date
accessed: 8 February 2021.url:https://environmentaldemocracyindex.org/.
318
