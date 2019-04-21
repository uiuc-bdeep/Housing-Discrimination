import os
import csv

def save_rental(d, url, name):
	has_csv = os.path.isfile(name)

	if has_csv:
		fd = open(name, "ab")
	else:
		fd = open(name, "wb")

	header = ["Address", "City", "State", "Zip_Code", "Rent_Per_Month", "Year", "Days_on_Trulia", "Type", "Sqft", "Phone_Number"]
	header = header + ["Bedroom_min", "Bedroom_max","Bathroom_min", "Bathroom_max"]
	header = header + ["Assault", "Arrest", "Theft", "Vandalism", "Burglary", "Crime_Other"]
	header = header + ["Elementary_School_Count", "Elementary_School_Avg_Score", 
	"Middle_School_Count", "Middle_School_Avg_Score", 
	"High_School_Count", "High_School_Avg_Score", "Driving", "Transit", "Walking", "Cycling", 
	"Restaurant", "Groceries", "Nightlife", "Cafe", "Shopping", "Entertainment", "Beauty", "Active_life"]

	header = header + ["Latitude", "Longitude",
	"EPA_Region", "Population", "Input_area(sq. miles)",
	"Particulate_Matter", "Ozone", "NATA*_Diesel_PM",
	"NATA*_Air_Toxics_Cancer_Risk", "NATA*_Respiratory_Hazard_Index", "Traffic_Proximity_and_Volume",
	"Lead_Paint_Indicator", "Superfund_Proximity", "RMP_Proximity",
	"Hazardous_Waste_Proximity", "Wastewater_Discharge_Indicator", "Demographic_Index%",
	"Minority_Population%", "Low_Income_Population%", "Linguistically_Isolated_Population%",
	"Population_with_Less_Than_High_School_Education%", "Population_under_Age_5%", "Population_over_Age_64%",
	"URL", "Short_form_ID"]

	value = [d.get("address", "NA"), d.get("city", "NA"), d.get("state", "NA"), 
	d.get("zip code", "NA"), d.get("rent_per_month", "NA"), d.get("year", "NA"), 
	d.get("days", "NA"), d.get("type", "NA"), d.get("sqft", "NA"), d.get("phone_number", "NA")]

	value = value + [d.get("bedroom_min", "NA"), d.get("bedroom_max", "NA"), d.get("bathroom_min", "NA"), d.get("bathroom_max", "NA")]
	value = value + [d.get("assault", "NA"), d.get("arrest", "NA"), d.get("theft", "NA"), 
	d.get("vandalism", "NA"), d.get("burglary", "NA"), d.get("crime_other", "NA")]
	value = value + [d.get("elementary_school_count", "NA"), d.get("elementary_school_average_score", "NA"), 
	d.get("middle_school_count", "NA"), d.get("middle_school_average_score", "NA"),
	d.get("high_school_count", "NA"), d.get("high_school_average_score", "NA"), 
	d.get("driving", "NA"), d.get("transit", "NA"), d.get("walking", "NA"), d.get("cycling", "NA"), d.get("restaurant", "NA"),
	d.get("groceries", "NA"), d.get("nightlife", "NA"), d.get("cafe", "NA"), d.get("shopping", "NA"), d.get("entertainment", "NA"),
	d.get("beauty", "NA"), d.get("active_life", "NA")]

	value = value + [d.get("lat", "NA"), d.get("lon", "NA"),
	d.get("epa_region", "NA"), d.get("population", "NA"), d.get("input area(sq. miles)", "NA"),
	d.get("Particulate Matter", "NA"), d.get("Ozone", "NA"), d.get("NATA* Diesel PM", "NA"),
	d.get("NATA* Air Toxics Cancer Risk", "NA"), d.get("NATA* Respiratory Hazard Index", "NA"), d.get("Traffic Proximity and Volume", "NA"),
	d.get("Lead Paint Indicator", "NA"), d.get("Superfund Proximity", "NA"), d.get("RMP Proximity", "NA"),
	d.get("Hazardous Waste Proximity", "NA"), d.get("Wastewater Discharge Indicator", "NA"), d.get("Demographic Index", "NA"),
	d.get("Minority Population", "NA"), d.get("Low Income Population", "NA"), d.get("Linguistically Isolated Population", "NA"),
	d.get("Population with Less Than High School Education", "NA"), d.get("Population under Age 5", "NA"), d.get("Population over Age 64", "NA"),
	url, d.get("short_form_id", "NA")]

	with fd as csvfile:
		filewriter = csv.writer(csvfile, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
		if has_csv == False:
			filewriter.writerow(header)
		filewriter.writerow(value)

def save_data(d, url, name, crawl_type):
	has_csv = os.path.isfile(name)

	if has_csv:
		fd = open(name, "ab")
	else:
		fd = open(name, "wb")

	header = ["Address", "City", "State", "Zip_Code", "Price", "Year", "Days_on_Trulia", "Type"]
	if crawl_type != "sold":
		header.append("Bedrooms")
		header.append("Agent_Name")

	header += ["Bathrooms", "Sqft"]
	if crawl_type != "sold":
		header.append("Dollars_per_Sqft") 
	header.append("Lot_Size")
	if crawl_type == "sold":
		header.append("Lot_Size_Unit")
		header.append("Sales_Day")
		header.append("Last_Listed_Date")
		header.append("Last_Listed_Price")
		header += ["Prior_Sales_Date"]
		header += ["Prior_Sales_Price"]
	if crawl_type != "sold":
		header.append("Number_of_views")

	header = header + ["Principal_and_Interest", 
	"Property_Taxes", "Home_Insurance", "HOA", 
	"Mortgage Ins. & other", "Theft", "Assault", 
	"Arrest", "Elementary_School_Score", "Elementary_School_Name", 
	"Middle_School_Score", "Middle_School_Name", "High_Schol_Score", 
	"High_Schol_Name", "Latitude", "Longitude",
	"EPA_Region", "Population", "Input_area(sq. miles)",
	"Particulate_Matter", "Ozone", "NATA*_Diesel_PM",
	"NATA*_Air_Toxics_Cancer_Risk", "NATA*_Respiratory_Hazard_Index", "Traffic_Proximity_and_Volume",
	"Lead_Paint_Indicator", "Superfund_Proximity", "RMP_Proximity",
	"Hazardous_Waste_Proximity", "Wastewater_Discharge_Indicator", "Demographic_Index%",
	"Minority_Population%", "Low_Income_Population%", "Linguistically_Isolated_Population%",
	"Population_with_Less_Than_High_School_Education%", "Population_under_Age_5%", "Population_over_Age_64%",
	"URL"]

	value = [d.get("address", "NA"), d.get("city", "NA"), d.get("state", "NA"), 
	d.get("zip code", "NA"), d.get("price", "NA"), d.get("year", "NA"), 
	d.get("days", "NA"), d.get("type", "NA")]

	if crawl_type != "sold":
		value.append(d.get("bedroom", "NA"))
		value.append(d.get("agent_name", "NA"))

	value = value + [d.get("bathroom", "NA"), d.get("sqft", "NA")]
	
	if crawl_type != "sold":
		value.append(d.get("dolloar_per_sqft", "NA"))

	value.append(d.get("lot_size", "NA"))

	if crawl_type == "sold":
		value.append(d.get("lot_size_unit", "NA"))
		value.append(d.get("sold_on", "NA"))
		value.append(d.get("last_listed_date", "NA"))
		value.append(d.get("last_listed_price", "NA"))
		value += [d.get("prior_sales_date")]
		value += [d.get("prior_sales_price")]

	if crawl_type != "sold":
		value.append(d.get("views", "NA"))
	
	value = value + [d.get("Principal & interest", "NA"), 
	d.get("Property taxes", "NA"), d.get("Home insurance", "NA"), d.get("HOA", "NA"), 
	d.get("Mortgage Ins. & other", "NA"), d.get("Theft", "NA"), d.get("Assault", "NA"), 
	d.get("Arrest", "NA"), d.get("elementary", "NA"), d.get("elementary_name", "NA"), 
	d.get("middle", "NA"), d.get("middle_name", "NA"), d.get("high school", "NA"), 
	d.get("high_school_name", "NA"), d.get("lat", "NA"), d.get("lon", "NA"),
	d.get("epa_region", "NA"), d.get("population", "NA"), d.get("input area(sq. miles)", "NA"),
	d.get("Particulate Matter", "NA"), d.get("Ozone", "NA"), d.get("NATA* Diesel PM", "NA"),
	d.get("NATA* Air Toxics Cancer Risk", "NA"), d.get("NATA* Respiratory Hazard Index", "NA"), d.get("Traffic Proximity and Volume", "NA"),
	d.get("Lead Paint Indicator", "NA"), d.get("Superfund Proximity", "NA"), d.get("RMP Proximity", "NA"),
	d.get("Hazardous Waste Proximity", "NA"), d.get("Wastewater Discharge Indicator", "NA"), d.get("Demographic Index", "NA"),
	d.get("Minority Population", "NA"), d.get("Low Income Population", "NA"), d.get("Linguistically Isolated Population", "NA"),
	d.get("Population with Less Than High School Education", "NA"), d.get("Population under Age 5", "NA"), d.get("Population over Age 64", "NA"),
	url]

	with fd as csvfile:
		filewriter = csv.writer(csvfile, delimiter = ',', quoting = csv.QUOTE_MINIMAL)
		if has_csv == False:
			filewriter.writerow(header)
		filewriter.writerow(value)