city <- "Philadelphia"
input_file <- "Philadelphia_PHA_metro_2017_newrenter_listings.rds"

rds <- readRDS(paste0("stores/", city, "/", input_file))

Address <- rds[,c("STREET_NAME", "HOUSE_NUM", 
                  "STREET_SUFFIX", "STREET_POST_DIR", 
                  "UNIT_TYPE", "UNIT_NUM", 
                  "CITY", "STATE", "ZIP")]

df <- Address
df[is.na(df)] <- ""

df$street <- apply(df[,c("HOUSE_NUM", "STREET_NAME", "STREET_SUFFIX", "STREET_POST_DIR")], 1, paste, collapse = " ")

# df$apt <- apply(df[,c("UNIT_TYPE", "UNIT_NUM")], 1, paste, collapse = " ")

df$full <- apply(df[ , c("street", "CITY", "STATE", "ZIP")] , 1 , paste , collapse = ", ")

df$full <- gsub(",  ,", ",", df$full) 

lat_lon <- rds[,c("GE_LATITUDE_2010", "GE_LONGITUDE_2010")]

df$latlon <- paste(lat_lon$GE_LATITUDE_2010, ", ", lat_lon$GE_LONGITUDE_2010)

df <- df[,c("full", "latlon")]

output_file <- "Philadelphia_PA_2017_address.csv"

write.csv(df, paste0("stores/", city, "/", output_file), row.names = F)
