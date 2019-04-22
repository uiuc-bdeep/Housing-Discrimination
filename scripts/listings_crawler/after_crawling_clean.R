# Please run this script line by line instead of sourcing the whole file...

library(stringr)

clean <- function(df, Address = NULL, original = NULL){
  df$Short_form_ID <- NULL
  
  df$Rent_Per_Month <- gsub('\\$|,', '', df$Rent_Per_Month)
  
  df[,c("Price_min", "Price_max")] <- str_split_fixed(df$Rent_Per_Month, " - ", 2)
  
  df$Price_min <- gsub("[^0-9]", "", df$Price_min)
  df$Price_max <- gsub("[^0-9]", "", df$Price_max)
  if (length(df[df$Price_max == "",]$Price_max) > 0){
    df[df$Price_max == "",]$Price_max <- NA
  }
  if (length(df[df$Price_min == "",]$Price_min) > 0){
    df[df$Price_min == "",]$Price_min <- NA
  }
  
  df$Price_max <- as.numeric(df$Price_max)
  df$Price_min <- as.numeric(df$Price_min)
  
  df$Rent_Per_Month <- NULL
  
  df$Sqft <- gsub('\\$|,', '', df$Sqft)
  df[,c("Sqft_min", "Sqft_max")] <- str_split_fixed(df$Sqft, "-", 2)
  df$Sqft_min <- gsub("[^0-9]", "", df$Sqft_min)
  df$Sqft_max <- gsub("[^0-9]", "", df$Sqft_max)
  if (length(df[df$Sqft_min == "",]$Sqft_min) > 0){
    df[df$Sqft_min == "",]$Sqft_min <- NA
  }
  if (length(df[df$Sqft_max == "",]$Sqft_max) > 0){
    df[df$Sqft_max == "",]$Sqft_max <- NA
  }
  
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
  
  df$Price_max <- ifelse(is.na(df$Price_max), df$Price_min, df$Price_max)
  df$Sqft_max <- ifelse(is.na(df$Sqft_max), df$Sqft_min, df$Sqft_max)
  
  df$index <- NULL
  
  if (!is.null(Address) & !is.null(original)){
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
  }

  return (df)
}

is_infoUSA <- F

if (is_infoUSA){
  # Address is a CSV contains two columns: full address and LatLon
  Address_file <- "stores/Philadelphia/Philadelphia_PA_2017_address.csv"
  Address <- read.csv(Address_file, stringsAsFactors = F)
  
  # Original infoUSA data
  original_file <- "stores/Philadelphia/Philadelphia_PHA_metro_2017_newrenter_listings.rds"
  original <- readRDS(original_file)
  
  # Crawled data
  crawled_df <- "stores/Philadelphia/Philadelphia_PA_2017_rental_listings_sample1.csv"
  df <- read.csv(crawled_df, stringsAsFactors = F)
  
  # URL for crawled data
  url_df <- "stores/Philadelphia/Philadelphia_PA_2017_urls.csv"
  url <- read.csv(url_df, stringsAsFactors = F)
  
  is_sampled <- T
  if (is_sampled){
    index <- which(url$sampled == T)
  } else {
    index <- 1:nrow(url)
  }
} else {
  crawled_df <- "stores/Philadelphia/Philadelphia_PA_2017_rental_listings_sample1.csv"
  df <- read.csv(crawled_df, stringsAsFactors = F)
  Address <- NULL
  original <- NULL
}

df <- clean(df, Address, original)

rownames(df) <- NULL
out_name <- "stores/Philadelphia/Philadelphia_PA_2017_rental_listings_sample1.rds"
write_rds(df, out_name)
