# Data Dictionary

The joined MesoWest dataset includes the variables below. Each entry lists the variable name, data type, and a concise description (including units when provided by MesoWest).

| Column | Type | Description |
| --- | --- | --- |
| ALR | float | Unknown variable (no units provided). |
| ALTI | float | Altimeter pressure (inches Hg / mb). |
| BLKC | float | Black carbon concentration (ug/m3). |
| CHC1 | string | Cloud layer 1 height/coverage (categorical/encoded). |
| CHC2 | string | Cloud layer 2 height/coverage (categorical/encoded). |
| CHC3 | string | Cloud layer 3 height/coverage (categorical/encoded). |
| CIG | float | Ceiling height (feet / meters). |
| CSLR | float | Clear sky solar radiation (W/m*m). |
| CSYH | string | High cloud symbol (categorical/encoded). |
| CSYL | string | Low cloud symbol (categorical/encoded). |
| CSYM | string | Mid cloud symbol (categorical/encoded). |
| DABL | float | Derived aerosol boundary layer depth (feet / meters). |
| DIRS | float | Sonic wind direction (degrees). |
| DRCT | float | Wind direction (degrees). |
| DWPF | float | Dewpoint temperature (°F / °C). |
| ECON | float | Electric conductivity (dS/m). |
| ERRR | string | Sensor error code. |
| ESNR | float | Estimated snowfall rate (in/hr / cm/hr). |
| EVAP | float | Evapotranspiration (in / mm). |
| FFWI | float | Fosberg Fire Weather Index (unitless). |
| FILT | float | Filter percentage (%). |
| FLOW | float | Air flow rate (liters/min). |
| FM | float | Fuel moisture (gm). |
| FT | float | Fuel temperature (°F / °C). |
| GRIP | string | Grip 2 level of grip (categorical/encoded). |
| GUST | float | Wind gust (mph / m/s). |
| HFLX | float | Vertical heat flux (m/s C). |
| HI24 | float | 24-hour high temperature (°F / °C). |
| HI6 | float | 6-hour high temperature (°F / °C). |
| HSUN | float | Hours of sun. |
| IFRC | string | Grip 1 ice friction code (categorical/encoded). |
| INLW | float | Incoming longwave radiation (W/m*m). |
| INRH | float | Internal relative humidity (%). |
| ITMP | float | Air flow temperature (°F / °C). |
| LO24 | float | 24-hour low temperature (°F / °C). |
| LO6 | float | 6-hour low temperature (°F / °C). |
| MDIR | float | Wind direction (degrees). |
| MDWP | float | Dew point (°F / °C). |
| MELV | float | Elevation (ft / m). |
| MFLX | float | Vertical moisture flux (m/s g/m**3). |
| MGPH | float | Geopotential height (m). |
| MGST | float | Wind gust (mph / m/s). |
| MLAT | float | Latitude (degrees). |
| MLON | float | Longitude (degrees). |
| MPRS | float | Pressure (in °F / mb). |
| MRH | float | Relative humidity (%). |
| MSKT | float | Wind speed (mph / m/s). |
| MSO2 | float | Soil moisture 2 (%). |
| MSOI | float | Soil moisture (%). |
| MSTD | float | Moisture standard deviation (g/m**3). |
| MTMP | float | Temperature (°F / °C). |
| MTVR | float | Virtual temperature (ft / °C). |
| NETL | float | Net longwave radiation (W/m*m). |
| NETR | float | Net radiation (W/m*m). |
| NETS | float | Net shortwave radiation (W/m*m). |
| OTOT | float | Sonic obs total (unitless). |
| OUTL | float | Outgoing longwave radiation (W/m*m). |
| OUTS | float | Outgoing shortwave radiation (W/m*m). |
| OZNE | float | Ozone concentration (ppb). |
| P00Z | float | Precipitation since 00 UTC (in / cm). |
| P01I | float | 1-hour precipitation (in / cm). |
| P01M | float | 1-hour precipitation (manual) (in / cm). |
| P03D | float | Pressure tendency (in / mb). |
| P03I | float | 3-hour precipitation (in / cm). |
| P03M | float | 3-hour precipitation (manual) (in / cm). |
| P05I | float | 5-minute precipitation (in / cm). |
| P05M | float | 5-minute precipitation (manual) (in / cm). |
| P06I | float | 6-hour precipitation (in / cm). |
| P06M | float | 6-hour precipitation (manual) (in / cm). |
| P10I | float | 10-minute precipitation (in / cm). |
| P10M | float | 10-minute precipitation (manual) (in / cm). |
| P15I | float | 15-minute precipitation (in / cm). |
| P15M | float | 15-minute precipitation (manual) (in / cm). |
| P1MI | float | 1-minute precipitation (in / cm). |
| P24I | float | 24-hour precipitation (in / cm). |
| P24M | float | 24-hour precipitation (manual) (in / cm). |
| P30I | float | 30-minute precipitation (in / cm). |
| PACM | float | Precipitation smoothed (in / cm). |
| PCHA | float | Pressure change (units not provided). |
| PCPR | float | Precipitation rate (in/hr / cm/hr). |
| PDIR | float | Peak wind direction (degrees). |
| PEAK | float | Peak wind speed (mph / m/s). |
| PERM | float | Permittivity (unitless). |
| PLDR | float | Platform true direction (degrees). |
| PLSP | float | Platform true speed (mph / m/s). |
| PM25 | float | PM2.5 concentration (ug/m3). |
| PMCN | float | Particulate concentration (ug/m3). |
| PMID | float | Precipitation since local midnight (in / cm). |
| PMSL | float | Sea level pressure (in / mb). |
| PREC | float | Precipitation accumulated (in / cm). |
| PREM | float | Precipitation manual (in / cm). |
| PRES | float | Pressure (in / mb). |
| PSTM | string | Precipitation storm (categorical/encoded). |
| PSWD | float | Primary swell wave direction (degrees). |
| PSWH | float | Primary swell wave height (ft / m). |
| PSWP | float | Primary swell wave period (sec). |
| PWVP | float | Precipitable water vapor (in / cm). |
| QFLG | string | Quality check flag. |
| RELH | float | Relative humidity (%). |
| RNUM | int | Road sensor number. |
| RNWG | float | Precipitation (weighing gauge) (in / cm). |
| RSS | string | Road surface conditions (categorical/encoded). |
| SACM | float | Snow smoothed (in / cm). |
| SINT | float | Snow interval (in / cm). |
| SKNT | float | Wind speed (mph / m/s). |
| SLVL | float | Surface level (in / cm). |
| SNOM | float | Snow manual (in / cm). |
| SNOW | float | Snow depth (in / cm). |
| SOLR | float | Solar radiation (W/m*m). |
| SPAR | float | Photosynthetically active radiation (umo). |
| SPDS | float | Sonic wind speed (mph / m/s). |
| SSTM | float | Snowfall (in / cm). |
| SSWD | float | Secondary swell wave direction (degrees). |
| SSWH | float | Secondary swell wave height (ft / m). |
| SSWP | float | Secondary swell wave period (sec). |
| STEN | float | Soil moisture tension (centibar). |
| T10M | float | Air temperature at 10 meters (°F / °C). |
| T182 | float | 18-inch soil temperature 2 (°F / °C). |
| T18I | float | 18-inch soil temperature (°F / °C). |
| T20I | float | 20-inch soil temperature (°F / °C). |
| T2M | float | Air temperature at 2 meters (°F / °C). |
| TFZ | float | Road freezing temperature (°F / °C). |
| TGND | float | Surface temperature (°F / °C). |
| TIC | float | Temperature in case (°F / °C). |
| TIDN | string | Tide indicator (categorical/encoded). |
| TIDP | float | Tide departure (ft / m). |
| TIR | float | IR soil temperature (°F / °C). |
| TLKE | float | Water temperature (°F / °C). |
| TLRW | float | Water temperature (°F / °C). |
| TMPF | float | Temperature (°F / °C). |
| TRD | float | Road temperature (°F / °C). |
| TSNC | float | Sonic temperature (°F / °C). |
| TSO2 | float | Soil temperature 2 (°F / °C). |
| TSO3 | float | Soil temperature 3 (°F / °C). |
| TSO4 | float | Soil temperature 4 (°F / °C). |
| TSOI | float | Soil temperature (°F / °C). |
| TSRD | float | Road subsurface temperature (°F / °C). |
| TSTD | float | Temperature standard deviation (°C). |
| USTD | float | Zonal wind standard deviation (m/s). |
| USTR | float | Friction velocity (m/s). |
| UVIN | float | Incoming UV radiation (W/m*m). |
| UVOT | float | Outgoing UV radiation (W/m*m). |
| VOLT | float | Battery voltage (volt). |
| VSBY | float | Visibility (miles / km). |
| VSTD | float | Meridional wind standard deviation (m/s). |
| WARN | string | Sonic warnings. |
| WEQS | float | Snow water equivalent (in / cm). |
| WHGT | float | Wave height (ft / m). |
| WNUM | string | Weather conditions (categorical/encoded). |
| WPER | float | Wave period (sec). |
| WRAT | float | SIGW/USTR (unitless). |
| WSNC | float | Vertical velocity (m/s). |
| WSTD | float | Vertical wind standard deviation (m/s). |

## U.S. Federal Holidays Dataset (`us_federal_holidays_2015_2026.csv`)

This dataset contains one row per U.S. federal holiday occurrence, including both the statutory holiday date and the observed federal holiday date when a weekend shift applies.

| Column | Type | Description |
| --- | --- | --- |
| year | int | Calendar year associated with the holiday occurrence. |
| holiday_name | string | Official holiday name (for example, `Memorial Day` or `Juneteenth National Independence Day`). |
| actual_date | date (`YYYY-MM-DD`) | The holiday’s calendar (statutory) date. |
| actual_day_of_week | string | Day of week for `actual_date`. |
| observed_date | date (`YYYY-MM-DD`) | Federal observed holiday date used for closures/time-off rules. May differ from `actual_date` when the holiday falls on a weekend. |
| observed_day_of_week | string | Day of week for `observed_date`. |
| observed_shifted | boolean | `True` when `observed_date` differs from `actual_date`; otherwise `False`. |
