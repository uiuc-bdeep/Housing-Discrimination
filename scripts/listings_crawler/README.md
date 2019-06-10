Listing Crawler
===
Listing Crawler is an application that allows user to crawl URL listings and corresponding ejscreen data.

## Table of Contents

* [Instruction](#Instruction)
* [Structure](#Structure)
* [Layout](#Layout)
* [InfoUSA](#InfoUSA)
* [Repair](#Repair)
* [Issues](#Issues)

## Instruction
### Requirements
- Python >= 2.7
- Selenium == 3.141
- fake_useragent == latest version

### To Run
just pull the project from github
```gherkin=
git pull https://github.com/uiuc-bdeep/Housing-Discrimination

cd Housing-Discrimination/scripts/listings_crawler

python crawler.py [args]
```

***If this is your first time using this crawler and you are encountering problems, please turn debug mode on!!***

### Arguments
```
usage: crawler.py [-h] [--repair REPAIR] [--debug DEBUG]
                  [--geckodriver GECKODRIVER] [--adblock ADBLOCK]
                  [--uBlock UBLOCK]
                  {U,A,L} [{U,A,L} ...] input_file output_file start end log

Crawl URL listings and ejscreen given URLs or Address (optional)

positional arguments:
  {U,A,L}               Whether the input file contains column (A)ddress or (L)atLon
  input_file            Path of input file
  output_file           Path of output file
  start                 Start of Input file
  end                   End of Input file
  log                   Name of the log

optional arguments:
  -h, --help            show this help message and exit
  --repair REPAIR       whether we try to repair the URL listings in the input_file or not.
                        output_file will be ignored if this is enabled
  --debug DEBUG         Turn on debug mode or not. Default False
  --geckodriver GECKODRIVER
                        Path of geckodriver.
                        Default ../../stores/
  --adblock ADBLOCK     Path of adblock.xpi (need ABSOLUTE PATH!!).
                        Default /home/ubuntu/Housing-Discrimination/stores/
  --uBlock UBLOCK       Path of uBlock0.xpi (need ABSOLUTE PATH!!).
                        Default /home/ubuntu/Housing-Discrimination/stores/

Note that input_file must be a CSV file that contains a column 'URL'.
It can also contain (A)ddress or (L)atLon
```

### Example Command:
```gherkin=
python crawler.py U input.csv output.csv 0 100 logfile --geckodriver /usr/bin/
```
### Restarting program or Continue the program:
First we need to locate where we left by using ```tail logfile```, then replace **start** with the **last number in logfile + 1**. For example, if the end of logfile is 57, then when you rerun the program, start at 58.

### After crawling is done:
Please run ```after_crawling_clean.R``` to clean the data. I recommend run this script line by line in RStudio in case there will be error.

Structure
---
```
|   after_crawling_clean.R
|   crawler.py
|   README.md
|   save_to_file.py
|
+---doc
|       layout.png
|       new_layout.png
|       old_layout.png
|
+---ejscreen
|       ejscreen.py
|       __init__.py
|
+---extract
|   |   extract_data.py
|   |   __init__.py
|   |
|   +---rental
|   |       extract_rental_data.py
|   |       __init__.py
|   |
|   \---sold_rental
|           extract_sold_rental_data.py
|           extract_sold_rental_data.pyc
|           __init__.py
|
+---infoUSA
|       infoUSA_step1_before_crawling_make_address.R
|       infoUSA_step2_1_clean_url.R
|       infoUSA_step2_2_append_url.R
|
+---preprocessing
|       get_url.py
|
\---util
        util.py
        __init__.py
```

InfoUSA
---
In order to crawl the listing using infoUSA data, you need to do the following:
1. Extract the addresses and coordinates `infoUSA_step1_before_crawling_make_address.R`. 
2. Crawl the url using `preprocessing/get_url.py`. 
3. Run `infoUSA_step2_1_clean_url.R` and `infoUSA_step2_2_append_url.R` to get an input file. 
4. Run the `crawler.py` with `U` and `L` mode using the input file from step 3.

Repair
---
**You must backup your data before proceeding.**

In the case where the data from previous run got corrupted, you can turn on repair mode to crawl the data again. All you need to do is to turn on repair mode on `crawler.py`.

Issues
---
**Program keeps printing 'zomming out':**

Restart the program.

**The program keeps restarting or loops at the same place:**

It is likely there are problems in the code. Run the program again with debug mode on to inspect the problem.

**NoSuchElementException: Message: Unable to locate element: //*[@id=__next]:**

It means 
its layout and therefore the program cannot locate the desired element. You just need to add the rule to locate the new element in corresponding python file given the error message. ***(remember to update this repo!!)***

**No such file or directory: '/tmp/tmpwBhpuO':**

If it only happens during debug mode, then you can safely ignore it. Otherwise, it means the disk is full and you need to clean up the system a bit. Usually a reboot will help.

**Issue regarding fake_useragent:**

Update the package by ```pip install -U fake-useragent```
