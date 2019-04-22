# Please run this script line by line instead of sourcing the whole file...

library(stringr)

clean <- function(df, Address, original){
  df$Short_form_ID <- NULL
  
  df$Rent_Per_Month <- gsub('\\$|,', '', df$Rent_Per_Month)
  
  df[,c("Price_min", "Price_max")] <- str_split_fixed(df$Rent_Per_Month, " - ", 2)
  
  df$Price_min <- gsub("[^0-9]", "", df$Price_min)
  df$Price_max <- gsub("[^0-9]", "", df$Price_max)
  df[df$Price_max == "",]$Price_max <- NA
  df[df$Price_min == "",]$Price_min <- NA
  df$Price_max <- as.numeric(df$Price_max)
  df$Price_min <- as.numeric(df$Price_min)
  
  df$Rent_Per_Month <- NULL
  
  df$Sqft <- gsub('\\$|,', '', df$Sqft)
  df[,c("Sqft_min", "Sqft_max")] <- str_split_fixed(df$Sqft, "-", 2)
  df$Sqft_min <- gsub("[^0-9]", "", df$Sqft_min)
  df$Sqft_max <- gsub("[^0-9]", "", df$Sqft_max)
  df[df$Sqft_min == "",]$Sqft_min <- NA
  df[df$Sqft_max == "",]$Sqft_max <- NA
  df$Sqft_max <- as.numeric(df$Sqft_max)
  df$Sqft_min <- as.numeric(df$Sqft_min)
  
  df$Sqft <- NULL
  df$Phone_Number <- NULL
  
  df$Elementary_School_Avg_Score <- ifelse(df$Elementary_School_Count == 0 | df$Elementary_School_Avg_Score == 0, NA, df$Elementary_School_Avg_Score)
  df$Middle_School_Avg_Score <- ifelse(df$Middle_School_Count == 0 | df$Middle_School_Avg_Score == 0, NA, df$Middle_School_Avg_Score)
  df$High_School_Avg_Score <- ifelse(df$High_School_Count == 0 | df$High_School_Avg_Score == 0, NA, df$High_School_Avg_Score)
  
  df$Assault <- ifelse(df$Assault == 0, NA, df$Assault)
  df$Arrest <- ifelse(df$Arrest == 0, NA, df$Arrest)
  df$Theft <- ifelse(df$Theft == 0, NA, df$Theft)
  df$Vandalism <- ifelse(df$Vandalism == 0, NA, df$Vandalism)
  df$Burglary <- ifelse(df$Burglary == 0, NA, df$Burglary)
  df$Crime_Other <- ifelse(df$Crime_Other == 0, NA, df$Crime_Other)
  
  Address$latlon <- NULL
  Address <- Address[index,]
  original <- original[index,]
  # Address <- Address[start:end,]
  # original <- original[start:end,]
  df <- cbind(Address, df)
  df[,2] <- NULL
  df <- cbind(original, df)
  df$City <- NULL
  df$State <- NULL
  df$Zip_Code <- NULL
  
  df$Price_max <- ifelse(is.na(df$Price_max), df$Price_min, df$Price_max)
  df$Sqft_max <- ifelse(is.na(df$Sqft_max), df$Sqft_min, df$Sqft_max)
  
  df$index <- NULL
  
  return (df)
}

Address <- read.csv("stores/Philadelphia/Philadelphia_PA_2017_address.csv", stringsAsFactors = F)
original <- readRDS("stores/Philadelphia/Philadelphia_PHA_metro_2017_newrenter_listings.rds")
df <- read.csv("stores/Philadelphia/Philadelphia_PA_2017_rental_listings_sample1.csv", stringsAsFactors = F)
url <- read.csv("stores/Philadelphia/Philadelphia_PA_2017_urls.csv", stringsAsFactors = F)
index <- which(url$sampled == T)

df <- clean(df, Address, original)

rownames(df) <- NULL
out_name <- "stores/Philadelphia/Philadelphia_PA_2017_rental_listings_sample1.rds"
write_rds(df, out_name)
