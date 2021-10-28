
# CC Metrics

The service responsible for calculating and serving evaluation metrics for conflict cartographer.

## Env settings

|Key                                            |Description                                     |
|-----------------------------------------------|------------------------------------------------|
|DB_HOST                                        |Database hostname                               |
|DB_USER                                        |Database username                               |
|DB_PASSWORD                                    |Database password                               |
|DB_NAME                                        |Database dbname                                 |
|GED_API_URL                                    |Url for an instance of cc_ged                   |
|PREDS_API_URL                                  |Url for an instance of cc_api                   |
|SCHEDULER_API_URL                              |Url for an instance of ccsched                  |
|BLOB_STORAGE_CONNECTION_STRING                 |Connection string to blob storage               |
|GENERAL_CACHE_CONTAINER_NAME                   |Storage container for db reflection             |

## Dependencies:

|Service name                                   |Description                                     |
|-----------------------------------------------|------------------------------------------------|
|cc_ged                                         |Retrieving GED actuals                          |
|cc_api                                         |Retrieving prediction shapes                    |
|ccsched                                        |Scheduling information for subsetting           |
|postgres                                       |Storing metrics                                 |
