###################################
# Prelimilary
rm(list=ls())
pkgTest <- function(x) {
  if (!require(x, character.only = TRUE))
  {
    install.packages(x, dep = TRUE)
    if(!require(x, character.only = TRUE)) stop("Package not found")
  }
}

## These lines load the required packages
packages <- c("readxl", "data.table", "rgdal", "sp", "rgeos")
lapply(packages, pkgTest)

get_layerName <- function(shp_file_path)
{
  relative_path <- path.expand(shp_file_path)
  print(relative_path)
  return(ogrListLayers(relative_path)[1])
}
state = "MO"
tabblock = "29" 
input_points <- read.csv("/Users/Chris/Research/trulia_project/test_folder/toxic_data/reruns_2/round_3/round_3_rentals.csv")
#input_points <- LA_final
points <- input_points
points_not_na <- points[which(!is.na(points$Longitude) & !is.na(points$Latitude)),]
points_na <- points[which(is.na(points$Longitude) | is.na(points$Latitude)),]
## remove NAs for lat and lon for shapefile
points <- points[which(!is.na(points$Longitude) & !is.na(points$Latitude)),]

# step 2-2: transfer it into shapefile #
coordinates(points) <- cbind(points$Longitude, points$Latitude)
proj4string(points) <- CRS("+proj=longlat")

polygons_path <- paste0(paste("/Users/Chris/Research/trulia_project/test_folder/toxic_data/census_block/",tabblock,"/tl_2016_",tabblock,"_tabblock10.shp",sep = ""))
# step 4: preprocess for the polygons #
shpLayerName <- get_layerName(polygons_path)
shp_poly <- readOGR(path.expand(polygons_path), shpLayerName)
# step 4-1: checking for default projection #
if(is.na(proj4string(shp_poly))){
  default_projection <- CRS("+proj=longlat +datum=WGS84 +ellps=WGS84 +towgs84=0,0,0")
  proj4string(shp_poly) <- CRS(default_projection)
}

# step 5: transform the projection from points to the projection of the shapefile #dsaf
points <- spTransform(points, proj4string(shp_poly))
proj4string(points) <- proj4string(shp_poly)

# step 6: perform the over operation #
res <- over(points, shp_poly)

# step 7: Appending the polygons' information to points dataframe #
#points_res <- as.data.frame(points_raw)
points_res <- cbind(points_not_na, res)

write.csv(points_res,"/Users/Chris/Research/trulia_project/test_folder/toxic_data/reruns_2/round_3/round_3_census.csv", row.names = F)
