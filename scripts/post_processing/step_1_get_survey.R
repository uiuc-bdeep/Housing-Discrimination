library(jsonlite)
library(dplyr)

print("Pulling responses from Ona...")

URL <- "https://api.ona.io/api/v1/data?owner=chkim12"

options(timeout=1000000)

json <- fromJSON(URL)

response <- list()

for (i in 1:nrow(json)) {
	id <- strtoi(substr(json[i, "url"], 32, 38))
	# grabs GA inquiries and ignores one csv
	if ((317952 <= id) && (id <= 322765) && (id != 319742)) {
		response[[length(response) + 1]] <- fromJSON(json[i,"url"])
	}
}

df <- bind_rows(response)
df$`_notes` <- NULL
df$`_tags` <- NULL
df$`_geolocation` <- NULL
df$`_attachments` <- NULL

setwd("input")
write.csv(df, "responses_concatenated.csv", row.names = F)
print("responses_concatenated.csv has been written.")