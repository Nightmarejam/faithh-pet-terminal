# Federal Register __ API Documentation.pdf

## Page 1

FederalRegister.gov provides multiple public API endpoints. Each endpoint is detailed below
and can be explored interactively by clicking the 'Try it out' button. At the bottom of this page in
the 'Schemas' section, valid options for various inputs such as agency names are listed in
detail.
FederalRegister.gov APIs do not require API keys; all you need is an HTTP client or browser.
Servers
/api/v1/
/api/v1/
Federal Register Documents
GETGET /documents/{document_number}.{format} Fetch a single Federal Register document
GETGET /documents/{document_numbers}.{format} Fetch multiple Federal Register documents
This site displays a prototype of a “Web 2.0” version of the daily Federal Register. It is not an o�cial legal
edition of the Federal Register, and does not replace the o�cial print version or the o�cial electronic version on
GPO’s govinfo.gov.
The documents posted on this site are XML renditions of published Federal Register documents. Each
document posted on the site includes a link to the corresponding o�cial PDF �le on govinfo.gov. This
prototype edition of the daily Federal Register on FederalRegister.gov will remain an uno�cial informational
resource until the Administrative Committee of the Federal Register (ACFR) issues a regulation granting it
o�cial legal status. For complete information about, and access to, our o�cial publications and services, go to
About the Federal Register on NARA's archives.gov.
The OFR/GPO partnership is committed to presenting accurate and reliable regulatory information on
FederalRegister.gov with the objective of establishing the XML-based Federal Register as an ACFR-sanctioned
publication in the future. While every effort has been made to ensure that the material on FederalRegister.gov is
accurately displayed, consistent with the o�cial SGML-based PDF version on govinfo.gov, those relying on it for
legal research should verify their results against an o�cial edition of the Federal Register. Until the ACFR grants
it o�cial status, the XML rendition of the daily Federal Register on FederalRegister.gov does not provide legal
notice to the public or judicial notice to the courts.
Federal Register :: API Documentation https://www.federalregister.gov/developers/documentation/api/v1
1 of 3 3/30/2026, 6:51 PM

## Page 2

GETGET /documents.{format} Search all Federal Register documents published since 1994.
GETGET /documents/facets/
{facet}
Fetch counts of matching Federal Register Documents grouped by
a facet
GETGET /issues/{publication_date}.
{format}
Fetch document table of contents based on the print
edition.
Public Inspection Documents
GETGET /public-inspection-documents/{document_number}.
{format}
Fetch a single public inspection
document.
GETGET /public-inspection-documents/{document_numbers}.
{format}
Fetch multiple public inspection
documents.
GETGET /public-inspection-documents/
current.{format}
Fetch all the public inspection documents that are
currently on public inspection.
GETGET
/public-
inspection-
documents.
{format}
Search all the public inspection documents that are currently on public
inspection; use the document search to find documents that have been
published.
Agencies
GETGET /agencies Fetch all agency details
GETGET /agencies/{slug} Fetch a particular agency's details
Images
GETGET /images/
{identifier}
Fetch the available image variants and their metadata for a single image
identifier
Suggested Searches
GETGET /suggested_searches Fetch all suggested searches or limit by FederalRegister.gov section
GETGET /suggested_searches/{slug} Fetch a particular suggested search
Federal Register :: API Documentation https://www.federalregister.gov/developers/documentation/api/v1
2 of 3 3/30/2026, 6:51 PM

## Page 3

Schemas
Agency
DocumentField
DocumentType
Facet
PublicInspectionDocumentField
President
PresidentialDocumentType
Section
SuggestedSearch
Topic
Federal Register :: API Documentation https://www.federalregister.gov/developers/documentation/api/v1
3 of 3 3/30/2026, 6:51 PM
