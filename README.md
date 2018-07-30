# Housing Discrimination
This project aims to increase our understanding of the extent to which racial discrimination in the housing market affects pollution exposures across the United States. Using a randomized experiment, we will establish the causal effect of discriminatory behavior on housing search and ultimately on pollution.

It is well established that minority groups in the United States face disproportionately high rates of exposure to a number of criterion and toxic pollutants. However, it has been difficult for researchers to disentangle the role of direct discrimination in the housing market that might result in exposures from other social and income inequities that also determine housing choices.  Consequently, environmental and energy policy is often not able to target the specific mechanisms at play.  Our experimental design will allow us to determine:

The effect of discriminatory behavior on the housing search process
The effect of discriminatory behavior on the pollution exposures given constraints placed on housing search

## Workflow Diagram:
![Imgur](https://i.imgur.com/IM0JEaO.jpg)

## File Hierarchy:
```
Housing-Discrimination
+--README.md
+--workflow_trulia_project.png
+--.gitignore
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
|  +--atlanta_ga
|  |  +--atlanta_ga_final.csv
|  +--houston_tx
|  |  +--houston_tx_final.csv
|  +--los_angeles_ca
|  |  +--los_angeles_ca_final.csv
```
