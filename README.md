# Hughes
Hughes Repo

usage: Kentik-Hughes-Dev.py [-h]
                            {delete-all-populators,create-populators,validate-data}
                            ...

positional arguments:
  {delete-all-populators,create-populators,validate-data}
    delete-all-populators
                        Deletes all populators for a given custom dimension
    create-populators   Creates populators for a given existing custom
                        dimension.
    validate-data       Validates the input data for building populators.


Delete All Populators: 

optional arguments:
  -h, --help            show this help message and exit
  
  usage: Kentik-Hughes-Dev.py delete-all-populators [-h] [--quiet]
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
                        
Create Populators:

usage: Kentik-Hughes-Dev.py create-populators [-h] [--quiet]
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
  
  Validate Date (CSV):
  
  usage: Kentik-Hughes-Dev.py validate-data [-h] [--quiet]
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
