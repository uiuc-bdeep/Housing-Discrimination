# Housing Discrimination
The choice of residential location is a critical economic decision.  By constraining the search process, housing discrimination distorts outcomes and reduces welfare.  Experimental evidence indicates that housing market discrimination continues to constrain the choices of racial minorities in the United States (Ewens et al., 2014, Carlsson and Eriksson, 2014, Hanson and Hawley, 2011, Ahmed and Hammarstedt, 2008) and steer them into disadvantaged neighborhoods (Christensen  and  Timmins,  2018).  Despite this, experimental research on discrimination in housing markets has ignored the role of housing search, making it difficult to understand the effect of discriminatory behavior on welfare and other economic outcomes.

This project collects experimental evidence on the effects of discriminatory behavior on the search outcomes of renters using a major online rental housing platform in several major markets in the United States.  We make use of racial associations based on names that are carefully chosen to represent  African American, LatinX/Hispanic, and White renters, testing for whether results are being driven by race, class or gender.   Our identification strategy estimates the within-property differences in the likelihood of a response to an inquiry across race groups. In addition we construct utility functions that are consistent with hedonic evidence on preferences for housing and neighborhood attributes, and use them to measure the welfare effects of discriminatory behavior that differentially constrains the choice sets of minority renters.

## Workflow Diagram:
![Imgur](https://i.imgur.com/IM0JEaO.jpg)

## File Hierarchy:
```
Housing-Discrimination
+--README.md
+--workflow_trulia_project.png
+--.gitignore
+--Guide.txt
+--scripts
|  +--listings_crawler
|  |  +--rhgeo_vm.py
|  +--listings_inquirer
|  |  +--trulia_rental_message_sender.py
|  |  +--trulia_rental_message_sender_data.txt
|  +--post_processing
|  |  +--adding_census_blocks_CA.R
|  |  +--mergeData.py
|  |  +--step_1_get_survey.R
|  +--pre_processing
|  |  +--trulia_rental_address_allocator.py
|  |  +--trulia_rental_address_allocator_data.txt
|  |  +--zip_url_finder.py
|  +--survey_gen
|  |  +--survey.py
|  |  +--test_template.xls
+--stores
|  +--variable_definitions.csv
|  +--atlanta_ga
|  |  +--atlanta_ga_final.csv
|  +--houston_tx
|  |  +--houston_tx_final.csv
|  +--los_angeles_ca
|  |  +--los_angeles_ca_final.csv
```
