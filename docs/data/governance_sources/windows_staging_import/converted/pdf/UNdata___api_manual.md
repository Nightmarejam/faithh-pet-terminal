# UNdata _ api manual.pdf

## Page 1

API Manual
About UNdata
About us
Country links to UNdata
FAQ
Partners
Site usage
Terms & Conditions of Use
UNdata in the blogosphere
Update calendar
UN21 Award
Visualization and tools
API
Datamarts Update CalendarGlossary API More
Search
Using UNdata API
About UNdata API
UNdata API provides dynamic, programmatic access to data within the
UNdata  platform.  Developers can  use  the  API to dynamically query
UNdata to obtain the latest data and display the result on a Web page,
download to local storage for further processing, etc.
UNdata API is powered by Eurostat’s SDMX Reference Infrastructure
(SDMX-RI). The API is implemented as a REST and SOAP Web Service
that can be used to query the datamarts using the SDMX standard. The
API is governed by UNdata Terms of Use.
How To Use UNdata API
If you want to query data from UNData API we have two options for
you. You can use REST API or the SOAP web service. In any of these
cases it is recommended that you get familiarized with the main SDMX
artifacts such as DataFlow, Codelist, Agency, Structure, etc. You can find
definitions for these concepts further bellow in  this same page FAQ
section.
▪ Querying data from the REST Webservice:
The SDMX REST service is located at http://data.un.org/ws/rest/.
The queries for the REST services are build using normal Rest
parametrization in the path, indicating the object and objectID
as  follow  :  http://data.un.org/ws/rest/{artifact}/{artifactId}/
{parameters} In order to be able to query data, usually you will
need to follow the following steps:
▪ Query to all the available DataFlows/DataMarts and select
the one that you are interested on.
▪ Once you have selected your dataflow you can query for
structure using AgencyID and StructureID. These are some
sample queries to get specific DataStructure, All
DataStructures, specific Codelist, All Codelist, specific
ConceptScheme, All ConceptScheme, Series Keys.
▪ When querying for a DataFlowID. You can apply filters by
providing codes for one or many dimension. Sequencing of
Dimension can be found from Data Structure query, All
UNdata | api manual https://data.un.org/Host.aspx?Content=API
1 of 3 3/30/2026, 7:06 PM

## Page 2

dimensions are listed under DataStrucures/
DataStrurureComponents/DimentionList node. To get all the
codes for certain Dimensions leave the value blank. +
operator can be used for multiple codes
API supports XML, Json and CSV data formats. Check FAQ
section below for more details.
Sample Queries:
▪ Data from selected dataflow
▪ Data filtered with selected code per dimension
▪ Data filtered with one code from single dimension
▪ Data filtered from specific time period
▪ SOAP Webservice
▪ To use UNdata API, you first need to create an SDMX Query.
This is an XML document that defines query parameters in
accordance with the dataset you intend to retrieve. Queries
can be easily created with SDMX Browser. Use this tool to
browse available dataflows and define a query, then use the
Download Query link to obtain the query as an XML file.
▪ To retrieve the data, use HTTP POST to submit SDMX query
created at step 1 to the UNdata SOAP Web Service at http://
data.un.org/ws/NSIStdV20Service.asmx. In most cases, you
can use GetCompactData or GetGenericData methods to
query the datamarts. The Web service supports CORS and
can be used in JavaScript.
▪ Results will be returned in an XML document structured in
accordance with selected dataset’s Data Structure Definition.
FAQ
Where can I get more information about SDMX?
▪ SDMX Web Site: http://www.sdmx.org
▪ SDMX Tool Repository: http://www.sdmxtools.org
▪ Tutorials, trainings, tools (Eurostat): https://webgate.ec.europa.eu/
fpfis/mwikis/sdmx
What formats are supported by REST API?
▪ XML
▪ Generic DataSet (Default): application/
vnd.sdmx.genericdata+xml;version=2.1
▪ Structure Specific Data: Use "Accept: application/
vnd.sdmx.structurespecificdata+xml;version=2.1"
▪ Json
▪ Use “Accept: text/json” header when querying for Data.
Structure message is attached at the end of Data message
▪ Csv (Data Only)
▪ Use “Accept: text/csv” header when querying.
How do I create an SDMX query for SOAP?
UNdata | api manual https://data.un.org/Host.aspx?Content=API
2 of 3 3/30/2026, 7:06 PM

## Page 3

▪ The easiest way to create an SDMX query is to use the SDMX
Browser to view available dataflows and define a query, then use
the Download Query link to get the query as SDMX-ML.
Why is API not available for all UNdata datamarts?
▪ To be exposed through SDMX API, each datamart requires an
SDMX Data Structure Definition (DSD). We are in the process of
mapping UNdata datamarts to available DSDs, as well as developing
new DSD where required. API support will be gradually extended to
further UNdata datamarts as DSDs and mappings are completed.
What is Data Structure Definition?
▪ In SDMX, dataset structure and codes are defined prior to data
exchange, just like a relational database structure needs to be
defined before the database can be used. These structures are
stored in a document called Data Structure Definition (DSD). To
establish data dissemination, each UNdata datamart requires one or
more DSDs which, as much as possible, should be internationally
standardized. API is already provided for some datamarts for which
DSDs are available. As more DSDs are developed, SDMX API will be
enabled for other UNdata datamarts.
How do  I get a Data Structure Definition associated with a
dataflow?
▪ Submit a RegistryInterface SDMX message to the QueryStructure
method of the Web service to retrieve a DSD. Alternatively, you can
use SDMX Browser: prepare a query, click Download SDMX-ML, and
select SDMX-ML Structure file to return the DSD and partial
codelists matching your query.
How is the data returned?
▪ Datasets are returned as structured XML documents. Specific
structure of each dataset is determined by its DSD as well as
selected SDMX format (Compact, Cross-Sectional, or Generic).
Home  | About Us  | FAQ  | Feedback  | Site usage
Copyright © 2026 - Conditions of Use
United Nations Statistics Division
Version
UNdata | api manual https://data.un.org/Host.aspx?Content=API
3 of 3 3/30/2026, 7:06 PM
