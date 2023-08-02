# CleanDat
Python functions to facilitate the pre-processing of data to prepare them for ML tasks, especially suitable for data in a clinical context.

---

Major functionalities include heuristic based data cleaning and feature engineering like:
- Automatic detection of encoding strings (e.g. 1=m) and application of the corresponding encoding to un-encoded data of the corresponding column
- Automatic detection of date strings of different formats (e.g. 2019-01-01, 01/01/2019, January 2022) and conversion to a unified format
- Encoding of date strings into decomposed date features (e.g. year, month, day, weekday, etc.)
- Heuristics for unification of different number formats, e.g. 1,000.00 vs. 1.000,00 or exponential notations like 1e3 vs 10x10^2
- Detection and replacement of inconsistent data values

# Setup

Install via pip:

    pip install cleandat
