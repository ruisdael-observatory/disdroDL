# Guide to parsing old csv's

This file explains how convert old CSV files to netCDF files and the difference in formats between certain files. The CSV's to parse can be found here: [Parsivel](https://ruisdael.citg.tudelft.nl/parsivel) or [Thies](https://ruisdael.citg.tudelft.nl/thies/). Ideally the CSV should contain all telegrams from one 24 hour period, but it should work with less or more.


## Parsing a csv
When parsing a csv, one should be in the main directory of `python-logging-software` where `parse_disdro_csv.py` is located. For calling the script the *site config* file and a csv need to be specified, e.g. `python3 parse_disdro_csv.py -c configs_netcdf/config_008_GV.yml -i sample_data/20230116_Delft-GV_PAR008.csv`. The netCDf will then de exported to the same directory as the CSV. The script will detect what sensor is relevant from the the site config file and it also detects what format the CSV is in.

## Formats

The csv's this script can parse come in 4 different formats, 2 for Parsivel and 2 for Thies. Both formats for each respective sensor have the same difference, the values from the telegram are all saved in a bite string in a single column or each value has an own column. An matrix to illustrate in which 4 boxes a csv format can be categorized in:
|                | Thies | Parsivel   |
|----------------|-----------------------|----------------------|
| **Bitestring** |     [Example](https://ruisdael.citg.tudelft.nl/thies/Thies005_Cabauw/2021/M12/)      | [Example](https://ruisdael.citg.tudelft.nl/parsivel/PAR007_Cabauw_Tower/2023/202306/)      |
| **Seperate Columns**    |      [Example](https://ruisdael.citg.tudelft.nl/thies/Thies001_Green_Village/2021/202109/)     | [Example](https://ruisdael.citg.tudelft.nl/parsivel/PAR007_Cabauw_Tower/2023/202306/)    |


For the bitestring csv's, a row has 3 values: A datetime, a Posix timestamp, and the bitestring. The datetime differs in format between Thies and Parsivel, but convey the same information. 

In the Parsivel CSV's field 61 is never documented, although it is in the config files and the Parsivel documentation. This is due to the way the Parsivels are set up, this field needs a different configuration to be requested. 

On the website where one can find these CSV's, one might find CSV's labeled SVF (single value fields). The script isn't able to parse these CSV's.