url <- read.csv("stores/Philadelphia/Philadelphia_PA_2017_urls_only.csv", header = F)

url$V1 <- 1:nrow(url)

url <- url[with(url, order(V1)), ]

dataset <- url[!duplicated(url[c("V1")]),]

dataset <- dataset[with(dataset, order(V1)), ]

rownames(dataset) <- NULL

dataset$V3 <- NULL

colnames(dataset) <- c("index", "urls")

write.csv(dataset, "stores/Philadelphia/Philadelphia_PA_2017_urls_only.csv", row.names = F)
