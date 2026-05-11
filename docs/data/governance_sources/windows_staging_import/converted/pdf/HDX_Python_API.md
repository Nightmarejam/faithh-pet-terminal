# HDX Python API.pdf

## Page 1

The HDX Python API Library is designed to enable you to easily develop code that interacts with the
Humanitarian Data Exchange (HDX) platform. The major goal of the library is to make pushing and
pulling data from HDX as simple as possible for the end user. If you have humanitarian-related data,
please upload your datasets to HDX.
• Information
• Getting Started
• Obtaining your API Key
• Installing the Library
• Docker
• A Quick Example
• Building a Project
• Default Con�guration for Facades
• Facades
• Customising the Con�guration
• Con�guring Logging
• Operations on HDX Objects
• Dataset Speci�c Operations
• Time Period
• Expected Update Frequency
• Location
• Tags
• Maintainer
• Organization
• Custom Visualization
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
1 of 29 3/30/2026, 7:07 PM

## Page 2

• Resource Generation
• QuickCharts Generation
• Resource Speci�c Operations
• Showcase Management
• User Management
• Organization Management
• Vocabulary Management
• Pipeline State
• Working Examples
• Project Framework
• IDMC Example
For more about the purpose and design philosophy, please visit HDX Python Library.
This library is part of the Humanitarian Data Exchange (HDX) project. If you have humanitarian
related data, please upload your datasets to HDX.
The code for the library is here. The library has detailed API documentation which can be found in
the menu at the top.
From 6.6.5, removed DatasetTitleHelper class and Dataset method remove_dates_from_title
From 6.6.0, Python 3.10 or later is required
From 6.5.7, get_size_and_hash moved to HDX Python Utilities
From 6.5.2, remove unused generate_qc_resource_from_rows method.
generate_resource_from_rows, generate_resource_from_iterable and
download_and_generate_resource are deprecated. They are replaced by generate_resource and
download_generate_resource.
From 6.5.0, �les will not be uploaded to the HDX �lestore if the hash and size have not changed, but
if there are any resource metadata changes, except for last_modi�ed, they will still take place.
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
2 of 29 3/30/2026, 7:07 PM

## Page 3

From 6.4.5, �x for changes in dependency defopt 7.0.0
From 6.2.8, �x mark_data_updated which was broken due to an error in
dataset_update_�lestore_resource in which timezone information was incorrectly added to the iso
formatted string
From 6.2.7, generate_resource_from_iterator renamed to generate_resource_from_iterable with
requirement of iterable rather iterator
From 6.2.6, kwargs take preference over environment variables which take preference over
con�guration �les
From 6.2.5, environment variables take preference over kwargs which take preference over
con�guration �les
From 6.1.5, any method or parameter with "reference_period" in it is renamed to "time_period" and
any method or parameter with "�le_type" in it is renamed to "format"
From 6.0.0, generate_resource_view is renamed to generate_quickcharts
From 5.9.9, get_location_iso3s returns uppercase codes instead of lowercase
From 5.9.8, get_date_of_dataset has become get_reference_period, set_date_of_dataset has
become set_reference_period and set_dataset_year_range has become
set_reference_period_year_range
From 5.9.7, Python 3.7 no longer supported
From 5.8.2, date handling uses timezone aware dates instead of naive dates and defaults to UTC
From 5.6.0, creating and updating datastores removed
From 5.4.0, Con�guration class moved to hdx.api.con�guration and Locations class moved to
hdx.api.locations
From 5.3.0, only supports Python 3.6 and above
From 5.0.1, Dataset functions get_location_iso3s and get_location_names replace get_location
From 4.8.3, some date functions in Dataset have been deprecated: get_dataset_date_type,
get_dataset_date_as_datetime, get_dataset_end_date_as_datetime, get_dataset_date,
get_dataset_end_date, set_dataset_date_from_datetime and set_dataset_date.
From 3.9.2, the default sort order for returned results from search and getting all datasets has
changed.
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
3 of 29 3/30/2026, 7:07 PM

## Page 4

From 3.7.3, the return type for add_tag, add_tags and clean_tags is now Tuple[List[str], List[str]]
(Tuple containing list of added tags and list of deleted tags and tags not added).
From 3.7.1, the list of tags must be from a set of approved tags (see under  below).
If you just want to read data from HDX, then an API key is not necessary and you can ignore the 6
steps below. However, if you want to write data to HDX, then you need to register on the website to
obtain an API key. You can supply this key as an argument or create an API key �le. If you create an
API key �le, by default this is assumed to be called  and is located in the current user's home
directory . Assuming you are using a desktop browser, the API key is obtained by:
1. Browse to the HDX website
2. Left click on LOG IN in the top right of the web page if not logged in and log in
3. Left click on your username in the top right of the web page and select PROFILE from the drop
down menu
4. Scroll down to the bottom of the pro�le page
5. Copy the API key which will be of the form: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
�. You can either:
a. Pass this key as a parameter or within a dictionary
b. Create a JSON or YAML �le. The default path is  in the current user's
home directory. Then put in the YAML �le:
To include the HDX Python library in your project, you must  or add to your 
�le the following line:
Replace  with the latest tag available from https:/ /github.com/OCHA-DAP/hdx-python-api/
    hdx_key: "HDX API KEY"
hdx-python-api==VERSION latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
4 of 29 3/30/2026, 7:07 PM

## Page 5

tags.
If you get dependency errors, it is probably the dependencies of the cryptography package that are
missing eg. for Ubuntu: python-dev, lib�-dev and libssl-dev. See cryptography dependencies.
If you get import or other errors, then please either recreate your virtualenv if you are using one or
uninstall hdx-python-api, hdx-python-country and hdx-python-utilities using , then install
hdx-python-api (which will pull in the other dependencies).
The library is also available set up and ready to go in a Docker image:
A Quick Example
Let's start with a simple example that also ensures that the library is working properly. In this
tutorial, we use virtualenv, a sandbox, so that your Python install is not modi�ed.
1. If you just want to read data from HDX, then an API key is not necessary. However, if you want to
write data to HDX, then you need to register on the website to obtain an API key. Please see
above about where to �nd it on the website. Once you have it, then put it into a �le in your home
directory:
2. If you are using the Docker image, you can jump to step 6, otherwise install virtualenv if not
installed:
On some Linux distributions, you can do the following instead to install from the distribution's
o�cial repository:
docker pull public.ecr.aws∕unocha∕hdx-scraper-baseimage:stable
docker run -i -t public.ecr.aws∕unocha∕hdx-scraper-baseimage:stable python3
cd ~
echo "hdx_key: \"xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx\"" > 
.hdx_configuration.yaml
pip install virtualenv
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
5 of 29 3/30/2026, 7:07 PM

## Page 6

3. Create a Python 3 virtualenv and activate it:
On Windows (assuming the Python 3 executable is in your path):
On other OSs:
4. Install the HDX Python library:
5. If you get errors, it is probably the dependencies of the cryptography package
�. Launch python:
7. Import required classes:
�. Setup logging
9. Use con�guration defaults.
If you only want to read data, then connect to the production HDX server, making sure that you
replace MyOrg_MyProject with something that describes your organisation and project:
If you want to write data, then for experimentation, do not use the production HDX server.
Instead you can use one of the test servers. Assuming you have an API key stored in a �le
sudo apt-get install virtualenv
virtualenv test
test\Scripts\activate
virtualenv -p python3 test
source test∕bin∕activate
pip install hdx-python-api
python
from hdx.utilities.easy_logging import setup_logging
from hdx.api.configuration import Configuration
from hdx.data.dataset import Dataset
setup_logging()
Configuration.create(hdx_site="prod", user_agent="MyOrg_MyProject", 
hdx_read_only=True)
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
6 of 29 3/30/2026, 7:07 PM

## Page 7

in the current user's home directory:
10. Read this dataset Novel Coronavirus (COVID-19) Cases Data from HDX and view the date of the
dataset:
11. You can search for datasets on HDX and get their resources:
12. You can download a resource in the dataset:
13. If you have an API key, you can write to HDX. You can try it out on a test server. With a dataset to
which you have permissions, change the dataset date:
14. You can view it on HDX before changing it back (if you have an API key):
15. If you are storing your data on HDX, you can upload a new �le to a resource:
1�. Alternatively, if you are using a URL to point to data held externally from HDX, you can mark that
the data has been updated before updating the resource or parent dataset:
Configuration.create(hdx_site="stage", user_agent="MyOrg_MyProject")
dataset = Dataset.read_from_hdx("novel-coronavirus-2019-ncov-cases")
print(dataset.get_time_period())
datasets = Dataset.search_in_hdx("thailand subnational boundaries", rows=10)
print(datasets)
resources = Dataset.get_all_resources(datasets)
print(resources)
url, path = resources[0].download()
print("Resource URL %s downloaded to %s" % (url, path))
dataset = Dataset.read_from_hdx("ID OR NAME OF DATASET")
print(dataset.get_time_period())  # record this
dataset.set_time_period("2015-07-26")
print(dataset.get_time_period())
dataset.update_in_hdx()
dataset.set_time_period("PREVIOUS DATE")
dataset.update_in_hdx()
resource = dataset.get_resource(0)
resource.set_file_to_upload("PATH TO FILE")
resource.update_in_hdx() latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
7 of 29 3/30/2026, 7:07 PM

## Page 8

17. Exit and remove virtualenv:
On Windows:
On other OSs:
The easiest way to get started is to use the facades and con�guration defaults. The facades set up
both logging and HDX con�guration.
The default con�guration loads an internal HDX con�guration located within the library, and
assumes that there is an API key �le called  in the current user's home directory  and a
YAML project con�guration located relative to your working directory at 
 which you must create. The project con�guration is used for any
con�guration speci�c to your project.
The default logging con�guration reads a con�guration �le internal to the library that sets up an
coloured console handler outputting at INFO level and a �le handler writing to errors.log at ERROR
level.
The simple facade makes it easier to get up and running:
resource = dataset.get_resource(2)
resource.mark_data_updated()
dataset.update_in_hdx()
exit()
deactivate
rd ∕s ∕q test
rm -rf test
from hdx.facades.simple import facade
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
8 of 29 3/30/2026, 7:07 PM

## Page 9

The keyword arguments facade is similar but passes through keyword arguments:
The infer arguments facade infers the possible command line from the type hints and docstring
describing the parameters of the function you give (such as main). It is possible to pass additional
parameters to the facade which will be overridden by any parameters provided on the command line
with the same name.
It is necessary to pass con�guration parameters in the facade call eg.
def main():
    ***YOUR CODE HERE***
if __name__ == "__main__":
    facade(main, CONFIGURATION_KWARGS)
from hdx.facades.keyword_arguments import facade
def main(kwparam1, kwparam2, ...,**ignore):
    ***YOUR CODE HERE***
if __name__ == "__main__":
    facade(main, CONFIGURATION_AND_OTHER_KWARGS)
from hdx.facades.infer_arguments import facade
def main(kwparam1: bool, kwparam2: str):
    """Generate dataset and create it in HDX
    Args:
        kwparam1 (bool): Help text for this command line argument
        kwparam2 (str): Help text for this command line argument
    Returns:
        None
    """
    ***YOUR CODE HERE***
if __name__ == "__main__":
    facade(main, kwparam3="lala")
facade(main, user_agent=USER_AGENT, hdx_site = HDX_SITE_TO_USE, hdx_read_only = 
ONLY_READ_NOT_WRITE, hdx_key_file = LOCATION_OF_HDX_KEY_FILE, 
hdx_config_yaml=PATH_TO_HDX_YAML_CONFIGURATION, project_config_dict = 
{"MY_PARAMETER", "MY_VALUE"})
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
9 of 29 3/30/2026, 7:07 PM

## Page 10

If you do not use the facade, you can use the  method of the  class directly,
passing in appropriate keyword arguments ie.
You must supply a user agent using one of the following approaches:
1. Populate parameter  (which should be the name of your organisation and project)
2. Supply  which should point to a YAML �le which contains a parameter
3. Supply  which should point to a YAML �le and populate
 which is a key to look up in the YAML �le which should be of form:
4. Include  in one of the con�guration dictionaries or �les outlined in the table below eg.
 or .
 can be:
hdx_site Optional[str] HDX site to use eg.
prod, feature
test
hdx_read_only bool Read only or read/
write access to
HDX
False
hdx_key Optional[str] HDX key (not
needed for read
only)
from hdx.api.configuration import Configuration
...
Configuration.create([configuration], [user_agent], [user_agent_config_yaml], 
[remoteckan], KEYWORD ARGUMENTS)
myproject:
    user_agent: test
myproject2:
    user_agent: test2
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
10 of 29 3/30/2026, 7:07 PM

## Page 11

Above or
one of:
hdx_con�g_dict dict Dictionary with
hdx_site,
hdx_read_only,
hdx_key
or hdx_con�g_json str Path to JSON
con�guration with
values as above
or hdx_con�g_yaml str Path to YAML
con�guration with
values as above
Zero or one
of:
project_con�g_dict dict Project speci�c
con�guration
dictionary
or project_con�g_json str Path to JSON
Project
To access the con�guration, you use the  method of the  class as follows:
For more advanced users, there are methods to allow you to pass in your own con�guration object,
remote CKAN object and list of valid locations. See the API documentation for more information.
This global con�guration is used by default by the library but can be replaced by Con�guration
instances passed to the constructors of HDX objects like Dataset eg.
Configuration.read()
configuration = Configuration(KEYWORD ARGUMENTS)
configuration.setup_remoteckan(REMOTE CKAN OBJECT)
configuration.setup_validlocations(LIST OF VALID LOCATIONS)
dataset = Dataset(configuration=configuration)
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
11 of 29 3/30/2026, 7:07 PM

## Page 12

If you use a facade from , then logging will go to console and errors to �le. If you are not
using a facade, you can call  which takes an argument error_�le which is False by
default. If set to True, errors will be written to a �le.
If not using facade:
To use logging in your �les, simply add the line below to the top of each Python �le:
Then use the logger like this:
You can read an existing HDX object with the static  method which takes an identi�er
parameter and returns the an object of the appropriate HDX object type eg.  or 
depending upon whether the object was read eg.
You can search for datasets and resources in HDX using the  method which takes a
query parameter and returns the a list of objects of the appropriate HDX object type eg.
. Here is an example:
The query parameter takes a different format depending upon whether it is for a dataset or a
resource. The resource level search is limited to �elds in the resource, so in most cases, it is
preferable to search for datasets and then get their resources.
from hdx.utilities.easy_logging import setup_logging
...
logger = logging.getLogger(__name__)
setup_logging(console_log_level="DEBUG", log_file="output.log",
file_log_level="INFO")
logger = logging.getLogger(__name__)
logger.debug("DEBUG message")
logger.info("INFORMATION message")
logger.warning("WARNING message")
logger.error("ERROR message")
logger.critical("CRITICAL error message")
dataset = Dataset.read_from_hdx("DATASET_ID_OR_NAME")
datasets = Dataset.search_in_hdx("QUERY", **kwargs)
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
12 of 29 3/30/2026, 7:07 PM

## Page 13

Various additional arguments (**kwargs) can be supplied. These are detailed in the API
documentation. The rows parameter for datasets (limit for resources) is the maximum number of
matches returned and is by default everything.
You can create an HDX Object, such as a dataset, resource, showcase, organization or user by calling
the constructor with an optional dictionary containing metadata. For example:
The dataset name should not contain special characters and hence if there is any chance of that,
then it needs to be slugi�ed. Slugifying is way of making a string valid within a URL (eg.  replaces
). There are various packages that can do this eg. python-slugify.
You can add metadata using the standard Python dictionary square brackets eg.
You can also do so by the standard dictionary  method, which takes a dictionary eg.
Larger amounts of static metadata are best added from �les. YAML is very human readable and
recommended, while JSON is also accepted eg.
The default path if unspeci�ed is  for YAML and 
 for JSON where TYPE is an HDX object's type like dataset or resource eg.
. The YAML �le takes the following form:
from hdx.data.dataset import Dataset
dataset = Dataset({
    "name": slugified_name,
    "title": title
})
dataset["name"] = "My Dataset"
dataset.update({"name": "My Dataset"})
dataset.update_from_yaml([path])
dataset.update_from_json([path])
owner_org: "acled"
maintainer: "acled"
...
tags:
    - name: "violence and conflict"
resources:
    -
      description: "Resource1"
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
13 of 29 3/30/2026, 7:07 PM

## Page 14

Notice how you can de�ne resources (each resource starts with a dash "-") within the �le as shown
above.
You can check if all the �elds required by HDX are populated by calling . This
will throw an exception if any �elds are missing. Before the library posts data to HDX, it will call this
method automatically. You can provide a list of �elds to ignore in the check. An example usage:
Once the HDX object is ready ie. it has all the required metadata, you simply call  eg.
If the object already exists, it will be updated. You can also update explicitly by calling 
eg.
You can delete HDX objects using  and update an object that already exists in HDX
with the method . These take various boolean parameters that all have defaults and
are documented in the API docs. They do not return anything and they throw exceptions for failures
like the object to update not existing.
A dataset can have resources and can be in a showcase.
If you wish to add a resource, you can create a resource dictionary and set the format then call the
 function, for example:
      url: "http:∕∕resource1.xlsx"
      format: "xlsx"
...
resource.check_required_fields([ignore_fields])
dataset.create_in_hdx(allow_no_resources, update_resources,
                      update_resources_by_name,
                      remove_additional_resources)
dataset.update_in_hdx(update_resources, update_resources_by_name,
                      remove_additional_resources)
resource = Resource({
    "name": "myfile.xlsx",
    "description": "description",
})
resource.set_format("xlsx")
resource.set_file_to_upload(PATH_TO_FILE)
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
14 of 29 3/30/2026, 7:07 PM

## Page 15

It is also possible to supply a resource id string or dictionary to the  function. A
url can be given instead of uploading a �le to the HDX �lestore (although using the �lestore is
preferred):
You can delete a Resource object from the dataset using the  function, for example:
 creates a list of HDX Resource objects in a dataset:
To see the list of resources, you use the  function eg.
You can get all the resources from a list of datasets as follows:
To see the list of showcases a dataset is in, you use the  function eg.
If you wish to add the dataset to a showcase, you must �rst create the showcase in HDX if it does
not already exist:
dataset.add_update_resource(resource)
resource = Resource({
    "name": "myfile.xlsx",
    "description": "description",
    "url": "https:∕∕www.blah.com∕myfile.xlsx"
})
resource.set_format("xlsx")
dataset.add_update_resource(resource)
dataset.delete_resource(resource)
dataset.add_update_resources(resources)
resources = dataset.get_resources()
resources = Dataset.get_all_resources(datasets)
showcases = dataset.get_showcases()
showcase = Showcase({"name": "new-showcase-1",
                     "title": "MyShowcase1",
                     "notes": "My Showcase",
                     "package_id": "6f36a41c-f126-4b18-aaaf-6c2ddfbc5d4d",
                     "image_display_url": "http:∕∕myvisual∕visual.png",
                     "url": "http:∕∕visualisation∕url∕"})
showcase.create_in_hdx()
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
15 of 29 3/30/2026, 7:07 PM

## Page 16

Then you can supply an id, dictionary or Showcase object and call the  function, for
example:
You can remove the dataset from a showcase using the  function, for example:
Time Period
Time Period is a mandatory �eld in HDX. It is the earliest start date and latest end date across all
the resources included in the dataset. The time period may be of any length: a year, a month, or even
a day. It should not to be confused with when data was last added/changed in the dataset. It can be
a single date or a range.
To get the time period, you can do as shown below. It returns a dictionary containing keys "startdate"
(start date as datetime), "enddate" (end date as datetime), "startdate_str" (start date as string),
"enddate_str" (end date as string) and ongoing (whether the end date is a rolls forward every day).
You can supply a date format. If you do not, the output format will be an ISO 8601 date eg.
2007-01-25.
To set the time period, you must pass either datetime.datetime objects or strings to the function
below. It accepts a start date and an optional end date which if not supplied is assumed to be the
same as the start date. Instead of the end date, the �ag "ongoing" which by default is False can be
set to True which indicates that the end date rolls forward every day.
The method below allows you to set the time period using a year range. The start and end year can
be supplied as integers or strings. If no end year is supplied then the range will be from the
beginning of the start year to the end of that year.
Expected Update Frequency
HDX datasets have a mandatory �eld, the expected update frequency. This is your best guess of how
dataset.add_showcase(showcase)
dataset.remove_showcase(showcase)
time_period = dataset.get_time_period("OPTIONAL FORMAT")
dataset.set_time_period("START DATE", "END DATE")
dataset.set_time_period_year_range(START YEAR, END YEAR)
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
16 of 29 3/30/2026, 7:07 PM

## Page 17

often the dataset will be updated.
The HDX web interface uses set frequencies:
Although the API allows much greater granularity (a number of days), you are encouraged to use the
options above (avoiding using  and  if possible as this �eld helps determine how up
to date datasets are). To assist with this, you can use certain Dataset methods outlined below.
The following method will return a textual expected update frequency corresponding to what would
be shown in the HDX web interface.
The method below allows you to set the dataset's expected update frequency using one of the set
frequencies above. (It also allows you to pass a number of days as a string or integer, but this is
discouraged.)
A list of valid update frequencies can be found using:
Transforming backwards and forwards between representations can be achieved with this function:
Location
Each HDX dataset must have at least one location associated with it.
If you wish to get the current location(s) as ISO 3 country codes, you can call the method below:
Every day
Every week
Every two weeks
Every month
Every three months
Every six months
Every year
As needed
Never
update_frequency = dataset.get_expected_update_frequency()
dataset.set_expected_update_frequency("UPDATE_FREQUENCY")
Dataset.list_valid_update_frequencies()
update_frequency = Dataset.transform_update_frequency("UPDATE_FREQUENCY")
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
17 of 29 3/30/2026, 7:07 PM

## Page 18

If you wish to get the current location name(s), you can call the method below:
If you want to add a country, you do as shown below. If you don't provide an ISO 3 country code, the
text you give will be parsed and converted to an ISO 3 code if it is a valid country name.
If you want to add a list of countries, the following method enables you to do it. If you don"t provide
ISO 3 country codes, conversion will take place where valid country names are found.
If you want to add a region, you do it as follows. If you don't provide a three digit UNStats M49 region
code, then parsing and conversion will occur if a valid region name is supplied.
 accepts regions, intermediate regions or subregions as speci�ed on the
UNStats M49 website.
If you want to add any other kind of location (which must be in this list of valid locations), you do as
shown below.
Tags
HDX datasets can have tags which help people to �nd them eg. "common operational dataset - cod",
"refugees". These tags come from a prede�ned set of approved tags. If you add tags that are not in
the approved list, the library attempts to map them to approved tags based on a spreadsheet of tag
mappings.
If you wish to get the current tags, you can use this method:
If you want to add a tag, you do it like this:
locations = dataset.get_location_iso3s()
locations = dataset.get_location_names()
dataset.add_country_location("ISO 3 COUNTRY CODE")
dataset.add_country_locations(["ISO 3","ISO 3","ISO 3"...])
dataset.add_region_location("M49 REGION CODE")
dataset.add_other_location("LOCATION")
tags = dataset.get_tags()
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
18 of 29 3/30/2026, 7:07 PM

## Page 19

If you want to add a list of tags, you do it as follows:
To obtain the prede�ned set of approved tags:
Maintainer
HDX datasets must have a maintainer.
If you wish to get the current maintainer, you can do this:
If you want to set the maintainer, you do it like this:
USER is either a string id, dictionary or a User object.
Organization
HDX datasets must be part of an organization.
If you wish to get the current organization, you can do this:
If you want to set the organization, you do it like this:
ORGANIZATION is either a string id, dictionary or an Organization object.
Custom Visualization
dataset.add_tag("TAG")
dataset.add_tags(["TAG","TAG","TAG"...])
approved_tags = Vocabulary.approved_tags()
maintainer = dataset.get_maintainer()
dataset.set_maintainer(USER)
organization = dataset.get_organization()
dataset.set_organization(ORGANIZATION)
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
19 of 29 3/30/2026, 7:07 PM

## Page 20

If you want to add a custom visualization to a dataset, you can do this:
URL is a string containing the url of your visualization.
You can get any existing visualization like this:
The return value is a string if a visualization has been set on the dataset, otherwise it is None.
Resource Generation
There are a range of helpful functions to generate resources. In the following examples, RESOURCE
DATA takes the form {"name": NAME, "description": DESCRIPTION} and ENCODING is a �le encoding
like "utf-8".
A resource can be generated from ROWS which is a list of list, tuple or dictionary. HEADERS is either
a row number (rows start counting at 1), or the actual headers de�ned as a list of strings. If not set,
all rows will be treated as containing values:
The �rst 4 parameters are mandatory, the rest are optional. A resource can be generated from a
given list or tuple or other iterable. The method returns a tuple with a bool True is the resource was
addeed and a dictionary of information. FOLDER and FILENAME specify where the �le will be
generated for upload to the �lestore. The dataset time period can optionally be set by supplying
DATECOL for looking up dates or YEARCOL for looking up years. DATECOl and YEARCOL can be a
column name or the index of a column. Note that any timezone information is ignored and UTC is
assumed.
Alternatively, DATE_FUNCTION can be supplied to handle any dates in a row. It should accept a row
and should return None to ignore the row or a dictionary which can either be empty if there are no
dates in the row or can be populated with keys startdate and/or enddate which are of type
timezone-aware datetime. The lowest start date and highest end date are used to set the time
period and are returned in the results dictionary in keys startdate and enddate.
download_generate_resource builds on generate_resource. It uses a DOWNLOADER, an object of
class Download, Retrieve or other class that implements BaseDownload to download from a URL.
    dataset.set_custom_viz(URL)
    url = dataset.get_custom_viz()
dataset.generate_resource("FOLDER", "FILENAME", ROWS, RESOURCE DATA, HEADERS,
                          COLUMNS, "FORMAT", "ENCODING", DATECOL or YEARCOL or
                          DATE_FUNCTION)
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
20 of 29 3/30/2026, 7:07 PM

## Page 21

Additional arguments in **KWARGS are passed to the get_tabular_rows method of the
DOWNLOADER.
Optionally, headers can be inserted at speci�c positions. This is achieved using
HEADER_INSERTIONS. If supplied, it is a list of tuples of the form (position, header) to be inserted. A
function, ROW_FUNCTION, is called for each row. If supplied, it takes as arguments: headers (prior to
any insertions) and row (which will be in dict or list form depending upon the dict_rows argument)
and outputs a modi�ed row.
The rest of the arguments are the same as for generate_resource.
QuickCharts Generation
QuickCharts can be generated for datasets using the call below. RESOURCE is a a resource id or
name, or resource metadata from a Resource object or a dictionary, or the position of the resource in
the dataset. It defaults to the position 0. PATH points to con�guration which if not supplied, defaults
to the internal indicators resource view template. You can disable speci�c bites by providing
BITES_DISABLED, a list of 3 bools where True indicates a speci�c bite is disabled and False indicates
leave enabled.
The parameter INDICATORS is only for use with the built-in con�guration and is a list with 3
dictionaries of form:
Optionally, the following defaults can be overridden in INDICATORS:
The built-in con�guration assumes data will be of form similar to below:
dataset.download_generate_resource(DOWNLOADER, "URL", "FOLDER", "FILENAME",
                                   RESOURCE_DATA, HEADER_INSERTIONS, ROW_FUNCTION,
                                   DATECOL or YEARCOL or DATE_FUNCTION, **KWARGS)
datasets.generate_quickcharts(RESOURCE, "PATH", BITES_DISABLED, INDICATORS,
                              FIND_REPLACE)
    {"code": "MY_INDICATOR_CODE", "title": "MY_INDICATOR_TITLE",
    "unit": "MY_INDICATOR_UNIT"}.
{"code_col": "#indicator+code", "value_col": "#indicator+value+num",
 "date_col": "#date+year", "date_format": "%Y", "aggregate_col": "null"}.
GHO (CODE),ENDYEAR,Numeric
#indicator+code,#date+year+end,#indicator+value+num
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
21 of 29 3/30/2026, 7:07 PM

## Page 22

When creating or updating a resource that doesn't have an id, if you supply a parameter dataset,
then the resource will be assigned to that dataset and it will be compared to resources in that
dataset. If a match is found, then the resource will be given the corresponding id and that resource
on HDX will be overwritten.
Alternatively, if a resource doesn't have an id, but contains a package_id, the create and update
methods will use it to load the corresponding dataset, the resource will be assigned to that dataset
and it will be compared to resources in that dataset. If a match is found, then the resource will be
given the corresponding id and that resource on HDX will be overwritten.
You can download a resource using the  function eg.
If you do not supply , then a temporary folder is used.
Before creating or updating a resource by calling  or  on the resource or
its parent dataset, it is possible to specify the path to a local �le to upload to the HDX �lestore if that
is preferred over hosting the �le externally to HDX. Rather than the url of the resource pointing to
your server or api, in this case the url will point to a location in the HDX �lestore containing a copy of
your �le.
There is a getter to read the value back:
To indicate that the data in an externally hosted resource (given by a URL) has been updated, call
 on the resource, before calling  or  on the resource
or parent dataset which will result in the resource last_modified �eld being set to now.
VIOLENCE_HOMICIDERATE,1994,123.4
MDG_0000000001,2015,123.4
resource.create_in_hdx(dataset=DATASET)
url, path = resource.download("FOLDER_TO_DOWNLOAD_TO")
resource.set_file_to_upload(file_to_upload="PATH_TO_FILE")
file_to_upload = resource.get_file_to_upload()
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
22 of 29 3/30/2026, 7:07 PM

## Page 23

Alternatively, when calling  or  on the resource, it is possible to supply
the parameter data_updated eg.
Using  on multiple resources in a dataset has the advantage of only requiring a
single call to HDX (by way of the dataset's  or  method). Setting
data_updated to True when using each resource's  or  method
requires a call to HDX per resource.
If you need to set a speci�c date for date of update (last_modified), you can call the following:
date can be a datetime object or string. You can retrieve the date of update (last_modified) using
the getter:
If the method  is used to supply a �le, the resource last_modified �eld is set to
now automatically regardless of the value of data_updated or whether  has
been called.
The  class enables you to manage showcases, creating, deleting and updating (as for
other HDX objects) according to your permissions.
To see the list of datasets a showcase is in, you use the  function eg.
If you wish to add a dataset to a showcase, you call the  function, for example:
You can remove the dataset from a showcase using the  function, for example:
resource.mark_data_updated()
dataset.update_in_hdx()
resource.update_in_hdx(data_updated=True)
resource.set_date_data_updated(date)
date = resource.get_date_data_updated()
datasets = showcase.get_datasets()
showcase.add_dataset(dataset) latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
23 of 29 3/30/2026, 7:07 PM

## Page 24

If you wish to get the current tags, you can use this method:
If you want to add a tag, you do it like this:
If you want to add a list of tags, you do it as follows:
The  class enables you to manage users, creating, deleting and updating (as for other HDX
objects) according to your permissions.
You can obtain the currently logged in user (which is based on the API token used in the
con�guration):
You can check that the current user has a particular permission to a speci�c organization:
For a general access check to use before running a script that creates or updates datasets:
You can email a user. First you need to set up an email server using a dictionary or �le:
Then you can email a user like this:
showcase.remove_dataset(dataset)
tags = showcase.get_tags()
showcase.add_tag("TAG")
showcase.add_tags(["TAG","TAG","TAG"...])
user = User.get_current_user()
result = User.check_current_user_organization_access("hdx", "read")
username = User.check_current_user_write_access("hdx")
email_config_dict = {"connection_type": "TYPE", "host": "HOST",
                     "port": PORT, "username": USERNAME,
                     "password": PASSWORD}
Configuration.read().setup_emailer(email_config_dict=email_config_dict)latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
24 of 29 3/30/2026, 7:07 PM

## Page 25

You can email multiple users like this:
The  class enables you to manage organizations, creating, deleting and updating (as for
other HDX objects) according to your permissions.
You can get the datasets in an organization as follows:
Various additional arguments (**kwargs) can be supplied. These are detailed in the API
documentation.
You can get the users in an organization like this:
OPTIONAL FIL TER can be member, editor, admin.
You can add or update a user in an organization as shown below:
You need to include a capacity �eld in the USER where capacity is member, editor, admin.
You can add or update multiple users in an organization as follows:
You can delete a user from an organization:
user.email("SUBJECT", "BODY", sender="SENDER EMAIL")
User.email_users(LIST_OF_USERS, "SUBJECT", "BODY", sender="SENDER EMAIL")
datasets = organization.get_datasets(**kwargs)
users = organization.get_users("OPTIONAL FILTER")
organization.add_update_user(USER)
organization.add_update_users([LIST OF USERS])
organization.delete_user("USER ID")
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
25 of 29 3/30/2026, 7:07 PM

## Page 26

The  class enables you to manage CKAN vocabularies, creating, deleting and updating
(as for other HDX objects) according to your permissions.
You can optionally initialise a Vocabulary with dictionary, name and tags:
If you wish to get the current tags, you can use this method:
If you want to add a tag, you do it like this:
If you want to add a list of tags, you do it as follows:
The HDXState class allows the reading and writing of state to a given dataset. Input and output
state transformations can be supplied in read_fn and write_fn respectively. The input state
transformation takes in a string while the output transformation outputs a string. It is used as
follows:
vocabulary = Vocabulary(name="myvocab", tags=["TAG","TAG","TAG"...])
vocabulary = Vocabulary({"name": "myvocab", tags=[{"name": TAG"}, {"name": TAG"}...])
tags = vocabulary.get_tags()
vocabulary.add_tag("TAG")
vocabulary.add_tags(["TAG","TAG","TAG"...])
    with temp_dir(folder="test_state") as tmpdir:
        statepath = join(tmpdir, statefile)
        copyfile(join(statefolder, statefile), statepath)
        date1 = datetime(2020, 9, 23, 0, 0, tzinfo=timezone.utc)
        date2 = datetime(2022, 5, 12, 10, 15, tzinfo=timezone.utc)
        with HDXState(
            "test_dataset", tmpdir, parse_date, iso_string_from_datetime
        ) as state:
            assert state.get() == date1
            state.set(date2)
        with HDXState(
            "test_dataset", tmpdir, parse_date, iso_string_from_datetime
        ) as state:
            assert state.get() == date2.replace(hour=0, minute=0)
        with HDXState(
            "test_dataset",
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
26 of 29 3/30/2026, 7:07 PM

## Page 27

For a working example of downloading data in a dataset on HDX, see this answer on StackOver�ow.
If you want to know how to create a dataset on HDX with a �le resource see this answer on
StackOver�ow.
Once you understand how to create a dataset on HDX, it is important to think about a good
structure. Below is framework for starting a project to interact with HDX that should work well.
First, pip install the library or alternatively add it to a requirements.txt �le if you are comfortable with
doing so as described above.
Next create a �le called  and copy into it the code below.
            tmpdir,
            HDXState.dates_str_to_country_date_dict,
            HDXState.country_date_dict_to_dates_str,
        ) as state:
            state_dict = state.get()
            assert state_dict == {"DEFAULT": date1}
            state_dict["AFG"] = date2
            state.set(state_dict)
        with HDXState(
            "test_dataset",
            tmpdir,
            HDXState.dates_str_to_country_date_dict,
            HDXState.country_date_dict_to_dates_str,
        ) as state:
            state_dict = state.get()
            assert state_dict == {
                "DEFAULT": date1,
                "AFG": date2.replace(hour=0, minute=0),
            }
#!∕usr∕bin∕python
# -*- coding: utf-8 -*-
"""
Calls a function that generates a dataset and creates it in HDX.
"""
import logging
from hdx.facades.simple import facade
from .my_code import generate_dataset
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
27 of 29 3/30/2026, 7:07 PM

## Page 28

The above �le will create in HDX a dataset generated by a function called  that can
be found in the �le  which we will now write.
Create a �le  and copy into it the code below:
You can then �ll out the function  as required.
A complete example can be found here: https:/ /github.com/OCHA-DAP/hdx-scraper-idmc
The IDMC scraper creates a dataset per country in HDX, populating all the required metadata. It then
creates resources with �les held on the HDX �lestore.
In particular, take a look at the �les ,  and the  folder. Do not run it unchanged as
it may overwrite the existing datasets in the IDMC organisation (although it will most probably fail as
you will not have permissions to modify anything in that organisation). You can use it as a basis for
logger = logging.getLogger(__name__)
def main():
    """Generate dataset and create it in HDX"""
    dataset = generate_dataset()
    dataset.create_in_hdx()
if __name__ == "__main__":
    facade(main, hdx_site="test")
#!∕usr∕bin∕python
# -*- coding: utf-8 -*-
"""
Generate a dataset
"""
import logging
from hdx.data.dataset import Dataset
logger = logging.getLogger(__name__)
def generate_dataset():
    """Create a dataset
    """
    logger.debug("Generating dataset!")
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
28 of 29 3/30/2026, 7:07 PM

## Page 29

your code renaming and modifying  as needed and updating metadata in 
 appropriately.
The �rst iteration of a scraper for ACLED was written without the HDX Python library and it became
clear looking at this and previous work by others that there are operations that are frequently
required and which add unnecessary complexity to the task of coding against HDX. Simplifying the
interface to HDX drove the development of the Python library and the second iteration of the scraper
was built using it. ACLED went from producing �les to creating an API, so a third iteration was
developed.
With the interface using HDX terminology and mapping directly on to datasets, resources and
showcases, the ACLED scraper was faster to develop and was much easier to understand for
someone inexperienced in how it works and what it is doing. The extensive logging and transparent
communication of errors is invaluable and enables action to be taken to resolve issues as quickly as
possible. Static metadata can be held in human readable �les so if it needs to be modi�ed, it is
straightforward.
The HDX Python library has expanded over time as needs have arisen and is used for a range of
tasks involving interaction with the HDX platform.
latest
HDX Python API https://hdx-python-api.readthedocs.io/en/latest/#obtaining-your-api-key
29 of 29 3/30/2026, 7:07 PM
