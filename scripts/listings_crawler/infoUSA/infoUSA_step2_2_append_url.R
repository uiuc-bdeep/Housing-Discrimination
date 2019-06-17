path <- "stores/Philadelphia/"
Name <- paste0(path, "Philadelphia_PA_2017")
re <- "/p/pa|/c/pa"
  
df <- read.csv(paste0(Name, "_address.csv"), stringsAsFactors = F)

df$address <- df$full
df$full <- NULL

urls <- read.csv(paste0(Name, "_urls_only.csv"), stringsAsFactors = F)

df <- df[1:nrow(urls),]
urls <- urls$urls
df <- cbind(df, urls)

colnames(df) <- c("LatLon", "Address", "Rent_url")

df$is_rent_valid <- str_count(df$Rent_url, re)

write.csv(df, paste0(Name, "_urls.csv"), row.names = F)

df$sampled <- F

valid <- df[df$is_rent_valid == 1 & df$sampled == F,]

valid <- valid[sample(nrow(valid), 25000, replace = F), ]
valid$sampled <- NULL
valid <- valid[order(as.numeric(row.names(valid))),]

df[rownames(valid), "sampled"] <- T

write.csv(df, paste0(Name, "_urls.csv"), row.names = F)

write.csv(valid, paste0(Name, "_urls_sample1_backup.csv"))

write.csv(valid, paste0(Name, "_urls_sample1.csv"), row.names = F)
