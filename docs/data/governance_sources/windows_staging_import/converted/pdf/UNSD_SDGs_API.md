# UNSD SDGs API.pdf

## Page 1

Select a definitionunsd_api v1
unsd_api v1
United Nations Statistics Division SDG
API.
https://unstats.un.org/sdgs/UNSDGAPIV5/swagger/../swagger/v1/swagger.json
Welcome to the UNSD SDG API: In this API you will be able to explore the official SDG data reported by the
custodiam agencies.
Servers
/sdgs/UNSDGAPIV5
/sdgs/UNSDGAPIV5
ArchiveData
POSTPOST /v1/sdg/ArchiveData/GetArchiveTable
POSTPOST /v1/sdg/ArchiveData/GetArchiveTableById
CompareTrends
POSTPOST /v1/sdg/CompareTrends/
GetDisaggregatedGlobalAndRegional
POSTPOST /v1/sdg/CompareTrends/
GetSeriesDisaggregationDimensions
POSTPOST /v1/sdg/CompareTrends/
GetDataOneSeriesMultiArea
POSTPOST /v1/sdg/CompareTrends/
GetDataMultiSeriesOneArea
POSTPOST /v1/sdg/CompareTrends/
GetAreaBySeriesDisaggregationDimensions
v1OAS3
UNSD SDGs API https://unstats.un.org/sdgs/UNSDGAPIV5/swagger/index.html
1 of 9 3/30/2026, 7:06 PM

## Page 2

POSTPOST /v1/sdg/CompareTrends/
GetSeriesDisaggregationDimensionsByArea
DataAvailability
POSTPOST /v1/sdg/DataAvailability/
GetIndicatorsAllCountries
POSTPOST /v1/sdg/DataAvailability/
GetCountriesAcrossGoals
POSTPOST /v1/sdg/DataAvailability/
GetGoalsDisaggregatedData
POSTPOST /v1/sdg/DataAvailability/
GetSeriesAggregationsForMaps
POSTPOST /v1/sdg/DataAvailability/GetWorldbyGoal
POSTPOST /v1/sdg/DataAvailability/
GetCompareacrossgoalData
POSTPOST /v1/sdg/DataAvailability/
GetSeriesAndDisAggregationsForGoals
POSTPOST /v1/sdg/DataAvailability/
GetDisaggregationType
GETGET /v1/sdg/DataAvailability/CountriesList
GeoArea
GETGET /v1/sdg/GeoArea/List
GETGET /v1/sdg/GeoArea/Tree
GETGET /v1/sdg/GeoArea/{GeoAreaCode}/List
GlobalDatabase
POSTPOST /v1/sdg/GlobalDatabase/DataCount
UNSD SDGs API https://unstats.un.org/sdgs/UNSDGAPIV5/swagger/index.html
2 of 9 3/30/2026, 7:06 PM

## Page 3

POSTPOST /v1/sdg/GlobalDatabase/GetGlobalDataBase
POSTPOST /v1/sdg/GlobalDatabase/DataExcel
POSTPOST /v1/sdg/GlobalDatabase/PivotDataExcel
POSTPOST /v1/sdg/GlobalDatabase/EmailDataExcel
Goal
GETGET /v1/sdg/Goal/List
GETGET /v1/sdg/Goal/{goalCode}/Target/List
GETGET /v1/sdg/Goal/{goalCode}/GeoAreas
GETGET /v1/sdg/Goal/{goalCode}/Dimensions
GETGET /v1/sdg/Goal/{goalCode}/Attributes
GETGET /v1/sdg/Goal/Data
POSTPOST /v1/sdg/Goal/DataCSV
POSTPOST /v1/sdg/Goal/DataExcel
GETGET /v1/sdg/Goal/PivotData
Indicator
GETGET /v1/sdg/Indicator/List
GETGET /v1/sdg/Indicator/{indicatorCode}/Series/
List
UNSD SDGs API https://unstats.un.org/sdgs/UNSDGAPIV5/swagger/index.html
3 of 9 3/30/2026, 7:06 PM

## Page 4

GETGET /v1/sdg/Indicator/{indicatorCode}/GeoAreas
GETGET /v1/sdg/Indicator/Data
GETGET /v1/sdg/Indicator/PivotData
SDGApiFeedback
POSTPOST /v1/sdg/Feedback/AddFeedback
SDGApiGlobalAndRegional
POSTPOST /v1/sdg/GlobalAndRegional/GetSingleSeries
POSTPOST /v1/sdg/GlobalAndRegional/GetMultiSeries
SDGApiSDMXMetadata
GETGET /v1/sdg/SDMXMetadata/GetSeries
POSTPOST /v1/sdg/SDMXMetadata/GetSDMXMetaData
GETGET /v1/sdg/SDMXMetadata/GetConceptsMasterList
GETGET /v1/sdg/SDMXMetadata/GetSdmxMSD
POSTPOST /v1/sdg/SDMXMetadata/GetSDMXFormat
Series
GETGET /v1/sdg/Series/List
GETGET /v1/sdg/Series/{serieCode}/List
UNSD SDGs API https://unstats.un.org/sdgs/UNSDGAPIV5/swagger/index.html
4 of 9 3/30/2026, 7:06 PM

## Page 5

GETGET /v1/sdg/Series/{seriesCode}/GeoAreas
GETGET /v1/sdg/Series/{seriesCode}/Dimensions
GETGET /v1/sdg/Series/{seriesCode}/Attributes
POSTPOST /v1/sdg/Series/GeoAreaCode
POSTPOST /v1/sdg/Series/TimePeriods
POSTPOST /v1/sdg/Series/DataCount
GETGET /v1/sdg/Series/{seriesCode}/GeoArea/
{geoAreaCode}/DataSlice
GETGET /v1/sdg/Series/Data
POSTPOST /v1/sdg/Series/DataCSV
POSTPOST /v1/sdg/Series/DataExcel
POSTPOST /v1/sdg/Series/PivotDataExcel
POSTPOST /v1/sdg/Series/EmailDataCSV
POSTPOST /v1/sdg/Series/EmailDataExcel
GETGET /v1/sdg/Series/PivotData
POSTPOST /v1/sdg/Series/PivotData
GETGET /v1/sdg/Series/LastUpdated
Target
UNSD SDGs API https://unstats.un.org/sdgs/UNSDGAPIV5/swagger/index.html
5 of 9 3/30/2026, 7:06 PM

## Page 6

GETGET /v1/sdg/Target/List
GETGET /v1/sdg/Target/{targetCode}/Indicator/List
GETGET /v1/sdg/Target/{targetCode}/GeoAreas
GETGET /v1/sdg/Target/Data
GETGET /v1/sdg/Target/PivotData
User
GETGET /v1/sdg/User/EmailExist
Schemas
ApiCodeList
ApiCompareIndicatorsAcrossCountries
ApiCountriesAcrossAllGoals
ApiCountrywiseData
ApiDimension
ApiDisaggregatedDimenions
UNSD SDGs API https://unstats.un.org/sdgs/UNSDGAPIV5/swagger/index.html
6 of 9 3/30/2026, 7:06 PM

## Page 7

ApiGeoArea
ApiGeoTree
ApiGoal
ApiGoalData
ApiIndicator
ApiIndicatorData
ApiIndicatorPercentage
ApiMultiSeriesData
ApiMultiSeriesOneArea
ApiObservation
ApiObservationPage
ApiObservationPivot
ApiObservationPivotPage
UNSD SDGs API https://unstats.un.org/sdgs/UNSDGAPIV5/swagger/index.html
7 of 9 3/30/2026, 7:06 PM

## Page 8

ApiOneSeriesData
ApiOneSeriesMultipleArea
ApiSerie
ApiSerieData
ApiSeriesData
ApiSliceData
ApiTarget
ApiTargetData
ApiY earWiseData
ConceptsMasterData
GoalsCountrywiseData
SDGArchiveData
SDGGoals
UNSD SDGs API https://unstats.un.org/sdgs/UNSDGAPIV5/swagger/index.html
8 of 9 3/30/2026, 7:06 PM

## Page 9

SDMXMetaDataResponse
UNSD SDGs API https://unstats.un.org/sdgs/UNSDGAPIV5/swagger/index.html
9 of 9 3/30/2026, 7:06 PM
