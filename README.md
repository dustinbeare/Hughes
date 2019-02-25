# Hughes
## Kentik CD Populator script

This script was specifically created for Hughes, but can be used by anyone to upload Populators to a Custom Dimension. It uses the Kentik Tagging API, located at https://github.com/kentik/kentikapi-py/tree/master/kentikapi/v5 for Batch Uploads. By default, batch uploads are set to 'Batch=True' so the CSV file used must be updated/changed after the initial populator upload, as all values within the CSV file will be checked against the existing populators within the specified Custom Dimension, and either added, modified, or removed, depending on this.

The format of the required columns of the CSV File for this is meant to be as follows:

[HNS_COMPANY_ID],[CUSTOMER_LOCATION_ID],[Device],[LANIP1],[LANSUBNET1],[LANIP2],[LANSUBNET2],...[LANIPx],[LANSUBNETx]

The Populator Value is set to [HNS_COMPANY_ID]-[CUSTOMER_LOCATION_ID] 
Ex: [HNS_COMPANY_ID] = XXX, [CUSTOMER_LOCATION_ID] = 1234 will generate a Populator Value of XXX-1234.

The Direction of each populator will be set to EITHER, currently you will need to modify the script if you wish to change the direction to either SRC or DST.

The [Device] value is the regex value for the Device Name matching.
The [LANIPx] field is the IP address, and the [LANSUBNETx] field is the subnet mask value, in a x.x.x.x format, which will be translated within the script to a CIDR value.

## Kentik-v1.py

usage: Kentik-v1.py [-h]
                            {delete-all-populators,create-populators,validate-data}
                            ...

positional arguments:
  {delete-all-populators,create-populators,validate-data}
    delete-all-populators
                        Deletes all populators for a given custom dimension
    create-populators   Creates populators for a given existing custom
                        dimension.
    validate-data       Validates the input data for building populators.


## Delete All Populators: 

optional arguments:
  -h, --help            show this help message and exit
  
  usage: Kentik-v1.py delete-all-populators [-h] [--quiet]
                                                  [--tracelevel {error,warn,info,debug}]
                                                  [--maxops MAXOPS]
                                                  [--include INCLUDE]
                                                  [--startrow STARTROW] --name
                                                  NAME

optional arguments:
  -h, --help            show this help message and exit
  --quiet               Show only minimal output.
  --tracelevel {error,warn,info,debug}
                        Python trace logging level. Default: info
  --maxops MAXOPS       Maximum number of REST operations to perform in one
                        run.
  --include INCLUDE     Regex that filters which rows are processed. Any value
                        in any field will be matched.
  --startrow STARTROW   The data row in the CSV to start process from. The
                        first data row after the header is row 2.
  --name NAME           The name of the custom dimension from where all
                        populators will be deleted.
                        
## Create Populators:

usage: Kentik-v1.py create-populators [-h] [--quiet]
                                              [--tracelevel {error,warn,info,debug}]
                                              [--maxops MAXOPS]
                                              [--include INCLUDE]
                                              [--startrow STARTROW] --name
                                              NAME --csv CSV [--batch]

optional arguments:
  -h, --help            show this help message and exit
  --quiet               Show only minimal output.
  --tracelevel {error,warn,info,debug}
                        Python trace logging level. Default: info
  --maxops MAXOPS       Maximum number of REST operations to perform in one
                        run.
  --include INCLUDE     Regex that filters which rows are processed. Any value
                        in any field will be matched.
  --startrow STARTROW   The data row in the CSV to start process from. The
                        first data row after the header is row 2.
  --name NAME           The name of the custom dimension under which to create
                        the populators.
  --csv CSV             The full path to the CSV file containing the data
                        required to create populators.
  --batch               Create populators using batch mode.
  
  ## Validate Date (CSV):
  
  usage: Kentik-v1.py validate-data [-h] [--quiet]
                                          [--tracelevel {error,warn,info,debug}]
                                          [--maxops MAXOPS]
                                          [--include INCLUDE]
                                          [--startrow STARTROW] --csv CSV

optional arguments:
  -h, --help            show this help message and exit
  --quiet               Show only minimal output.
  --tracelevel {error,warn,info,debug}
                        Python trace logging level. Default: info
  --maxops MAXOPS       Maximum number of REST operations to perform in one
                        run.
  --include INCLUDE     Regex that filters which rows are processed. Any value
                        in any field will be matched.
  --startrow STARTROW   The data row in the CSV to start process from. The
                        first data row after the header is row 2.
  --csv CSV             The full path to the CSV file containing the data
                        required to create populators.
