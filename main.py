import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
# Project information
project_name = "THEMATIC MAPPING PROJECT"
print("================================")
print(project_name)
print("Automatic Thematic Map Production System")
print("================================")
print("System initialized successfully")
# Create project folder
data_folder = "data"
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
print("Data foider created successfully!")
# Create output folder for thematic maps
output_folder = "output"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
print("Output folder created successfully!")
# Define input file paths
csv_file = os.path.join(data_folder, "district_data.csv")
excel_file = os.path.join(data_folder, "district_data.xlsx")
print("Input file paths configured successfully!")
print("CSV file: " , csv_file)
print("Excel file: " , excel_file)
# Function to load statistical data from CSV
def load_csv_data(file_path):
    if os.path.exists(file_path):
        data = pd.read_csv(file_path)
        print("CSV file loaded successfully!")
        return data
    else:
        print("CSV file not found!")
        return None
# Function to load statistical data from Excel
def load_excel_data(file_path):
    if os.path.exists(file_path):
        data = pd.read_excel(file_path)
        print("Excel data loaded successfully!")
        return data
    else:
        print("Excel file not found!")
        return None
# Function to clean statistical data
def clean_data(data):
    data = data.dropna()
    data = data.drop_duplicates()
    print("Statistical data cleaned successfully!")
    return data
# Function to validate statistical data
def validate_data(data):
    required_columns = ["District","Population"]
    for column in required_columns:
        if column not in data.columns:
            print(f"Missing required column: {column}")
            return False
    print("Data validation completed successfully!")
    return True
# Function to select the data source
def load_statistical_data(file_type):
    if file_type == "csv":
        data = load_csv_data(csv_file)
    elif file_type == "excel":
        data = load_excel_data(excel_file)
    else:
        print("Unsupported file format!")
        return None
    return data
# Function to load geographical boundary data
def load_boundary_data(file_path):
    if os.path.exists(file_path):
     try:
         boundaries = gpd.read_file(file_path)
         print("Coordinate Reference System:", boundaries.crs)
         print("KAMPALA NAME IN BOUNDARY FILE:")
         print(boundaries.loc[boundaries["NAME"].str.contains("kampala", case=False), "NAME"].tolist())
         print("BOUNDARY DISTRICT NAMES:")
         print(boundaries["NAME"].tolist())
         print("BOUNDARY FILE COLUMNS:")
         print(boundaries.columns.tolist())
         if boundaries.empty:
             print("The boundary file is empty!")
             return None
         print("Geographical boundaries loaded successfully!")
         print("Number of geographical features:", len(boundaries))
         print("Coordinate Reference System:", boundaries.crs)
         print("Available columns:", list(boundaries.columns))
         return boundaries
     except Exception as e:
         print("Error loading geographical boundaries:", e)
         return None
    else:
        print("Boundary file not found!")
        return None
def check_boundary_data(boundaries):
    if boundaries is not None:
        print("Boundary data is ready for mapping!")
        print("Number of geographical features:", len(boundaries))
    else:
        print("No geographical boundary data available!")
# Function to link statistical data with geographical boundaries
def join_project_data(statistical_data, boundaries):
    if statistical_data is None or boundaries is None:
        print("Cannot join data. Required datasets are missing!")
        return None
    if "District" not in statistical_data.columns:
        print("District column is missing from CSV!")
        return None
    if "NAME" not in boundaries.columns:
        print("NAME column is missing from boundary data!")
        return None
    statistical_data = statistical_data.copy()
    boundaries = boundaries.copy()
    statistical_data["_district_key"] = (statistical_data["District"].astype(str).str.strip().str.casefold())
    boundaries["_district_key"] = (boundaries["NAME"].astype(str).str.strip().str.casefold())
    merged_data = boundaries.merge(statistical_data, on="_district_key", how="left")
    matched = merged_data["Population"].notna().sum()
    print("Statistical and geographical data linked successfully!")
    print("Number of matched districts:", matched)
    return merged_data

# Define geographical boundary file path
boundary_file = os.path.join(data_folder, "UGA_District_Boundaries_2024.geojson")
print("Boundary file path configured successfully!")
print("Boundary file:" , boundary_file)
# Function to validate geographical boundaries
def validate_boundaries(boundaries):
    if "District" in boundaries.columns:
        print("District column found successfully!")
        return True
    else:
        print("District column is missing!")
        return False
# Function to check coordinate reference system
def check_crs(boundaries):
    if boundaries.crs is not None:
        print("Coordinate Reference System found!")
        print("CRS:", boundaries.crs)
        return True
    else:
        print("Coordinate Reference System is missing!")
        return False
# Function to reproject geographical data
def reproject_boundaries(boundaries, target_crs="EPSG:4326"):
    if boundaries.crs is None:
        print("Cannot reproject: CRS is missing!")
        return None
    boundaries = boundaries.to_crs(target_crs)
    print("Geographical data reprojected successfully!")
    print("New CRS:", boundaries.crs)
    return boundaries
# Function to calculate geographical area
def calculate_area(boundaries):
    if boundaries.crs is None:
        print("Cannot calculate area: CRS is missing!")
        return None
    projected_boundaries = boundaries.to_crs("EPSG:32636")
    projected_boundaries["Area_km2"] = (projected_boundaries.geometry.area / 1000000)
    print("Geographical areas calculated successfully!")
    return projected_boundaries
# Function to calculate geographical perimeter
def calculate_perimeter(boundaries):
    if boundaries.crs is None:
        print("Cannot calculate perimeter: CRS is missing!")
        return None
    projected_boundaries = boundaries.to_crs("EPSG:32636")
    projected_boundaries["Perimeter_km"] = (projected_boundaries.geometry.length / 1000)
    print("Geographical perimeters calculated successfully!")
    return projected_boundaries
# Function to calculate population density
def calculate_population_density(data):
    if "Population" not in data.columns:
        print("Population column is missing!")
        return None
    if "Area_km2" not in data.columns:
        print("Area_km2 column is missing!")
        return None
    data["Population_Density"] = (data["Population"] / data["Area_km2"])
    print("Population density calculated successfully!")
    return data
# Function to merge population data with district boundaries
def merge_district_data(boundaries, data):
    merged_data = boundaries.merge(data, on="District", how="left")
    print("Population data merged with boundaries successfully!")
    return merged_data
# Function to classify population density
def classify_population_density(data):
    def classify(value):
        if value < 100:
            return "Low Density"
        elif value < 300:
            return "Medium Density"
        else:
            return "High Density"
    data["Density_Class"] = data["Population_Density"].apply(classify)
    print("Population density classified successfully!")
    return data
# Function to create a population density map
def create_density_map(data):
    fig, ax = plt.subplots(figsize=(12,10))
    data.plot(column="Density_Class", categorical=True, legend=True, ax=ax, edgecolor="black", linewidth=0.5)
    ax.set_title("Population Density by District", fontsize=16)
    ax.set_axis_off()
    plt.tight_layout()
    print("Population density map created successfully!")
    return fig
# Function to save the thematic map
def save_thematic_map(fig, filename):
    file_path = os.path.join(output_folder, filename)
    fig.savefig(file_path, dpi=300, bbox_inches="tight")
    print("Thematic map saved successfully!")
    print("Saved at: ", file_path)
# Function to display the thematic map
def display_thematic_map(fig):
    plt.show()
    print("Thematic map displayed successfully!")
# Function to create a population map
def create_population_map(data):
    fig, ax = plt.subplots(figsize=(12,10))
    data.plot(column="Population", cmap="YlOrRd", legend=True, ax=ax, edgecolor="black", linewidth=0.5)
    ax.set_title("Population Distribution by District", fontsize=16)
    ax.set_axis_off()
    plt.tight_layout()
    print("Population map created successfully!")
    return fig
# Function to save the population map
def save_population_map(fig):
    file_path = os.path.join(output_folder, "Population_distribution_map.png")
    fig.save(file_path, dpi=300, bbox_inches="tight")
    print("Population map saved successfully!")
    print("Saved at:", file_path)
# Function to generate a population report
def generate_population_report(data):
    report = data[["District", "Population"]].copy()
    report = report.sort_values(by="Population", ascending=False)
    print("DISTRICT POPULATION REPORT")
    print(report)
    return report
# Function to save the population report
def save_population_report(report):
    file_path = os.path.join(output_folder, "district_population_report.csv")
    report.to_csv(file_path, index=False)
    print("Population report saved successfully!")
    print("Saved at:", file_path)
# Function to generate a population density report
def generate_density_report(data):
    report = data[["District", "Population", "Area_km2", "Population_Density"]].copy()
    report = report.sort_values(by="Population_Density", ascending=False)
    print("DISTRICT POPULATION DENSITY REPORT")
    print(report)
    return report
# Function to save the population density report
def save_density_report(report):
    file_path = os.path.join(output_folder, "district_population_density_report.xlsx")
    report.to_excel(file_path, index=False)
    print("Population density report saved successfully!")
    print("Saved at:", file_path)
# Function to generate a district area report
def generate_area_report(data):
    report = data[["District", "Area_km2",]].copy()
    report = report.sort_values(by="Area_km2", ascending=False)
    print("DISTRICT AREA REPORT")
    print(report)
    return report
# Function to save the district area report
def save_area_report(report):
    file_path = os.path.join(output_folder, "district_area_report.xlsx")
    report.to_excel(file_path, index=False)
    print("District area report saved successfully!")
    print("Saved at:", file_path)
# Function to generate the mapping summery
def generate_mapping_summary(data):
    total_districts = len(data)
    total_population = data["Population"].sum()
    average_density = data["Population_Density"].maen()
    print("THEMATIC MAPPING SUMMARY")
    print("------------------------")
    print("Total districts:", total_districts)
    print("Total population:", total_population)
    print("Average population density:", average_density)
    return{"Total_Districts": total_districts, "Total_Population": total_population, "Average_Density": average_density}
# Function to save the mapping summary
def save_mapping_summary(summary):
    file_path = os.path.join(output_folder, "thematic_mapping_summary.txt")
    with open(file_path, "w") as file:
        for key, value in summary.items():
            file.write(f"{key}: {value}\n")
    print("Mapping summary saved successfully!")
    print("Saved at:", file_path)
# Main program function
def main():
 print("=========================================")
print("AUTOMATIC THEMATIC MAP PRODUCTION")
print("=========================================")
print("System is ready to process geographical data!")
print("Please prepare your district data and boundary files.")
# Function to load all project data
def load_project_data():
    print("Loading project data...")
    statistical_data = load_statistical_data("csv")
    if statistical_data is None:
        print("Unable to load statistical data!")
        return None, None
    boundaries = load_boundary_data(boundary_file)
    if boundaries is None:
        print("Unable to load geographical boundaries!")
        return None, None
    print("All project data loaded successfully!")
    return statistical_data, boundaries
# Function to validate project data
def validate_project_data(statistical_data, boundaries):
    print("Validating project data...")
    if statistical_data is None or boundaries is None:
        print("Project data is missing!")
        return False
    if statistical_data.empty:
        print("Statistical data is empty!")
        return False
    if boundaries.empty:
        print("Geographical boundaries are empty!")
        return False
    if boundaries.crs is None:
        print("Warning: Coordinate Reference System (CRS) is missing!")
        return False
    print("Project data validation completed successfully!")
    return True
# Function to display geographical boundaries
def display_boundary_map(boundaries):
    print("Displaying geographical boundaries...")
    fig, ax = plt.subplots(figsize=(12,10))
    boundaries.plot(ax=ax, edgecolor="black", facecolor="lightblue", linewidth=0.5)
    ax.set_title("Uganda District Boundary Map")
    ax.set_axis_off()
    plt.tight_layout()
    plt.show()
# Function to create an automatic thematic map
def create_thematic_map(statistical_data, boundaries):
    print("Creating automatic thematic map...")
    boundaries = boundaries.copy()
    statistical_data = statistical_data.copy()
    boundaries["join_name"] = boundaries["NAME"].astype(str).str.strip().str.lower()
    statistical_data["join_name"] = statistical_data["District"].astype(str).str.strip().str.lower()
    statistical_data["join_name"] = statistical_data["join_name"].replace({"kampala": "kampala capital city"})
    merged = boundaries.merge(statistical_data[["join_name", "Population"]], on="join_name", how="left")
    print("Merged CRS:", merged.crs)
    print("Checking district matching...")
    print("Districts in CSV:", len(statistical_data))
    print("Districts successfully matched:", merged["Population"].notna().sum())
    print("Unmatched CSV districts:")
    matched_names = set(merged.loc[merged["Population"].notna(), "join_name"])
    unmatched = statistical_data[~statistical_data["join_name"].isin(matched_names)]
    print(unmatched[["District", "Population"]])
# Convert map coordinates into metres
    merged = merged.to_crs(epsg=3857)
# Calculate map statistics
    population_values = merged["Population"].dropna()
    print("\n========MAP INFORMATION=========")
    print("Total geographical districts:", len(merged))
    print("Districts with population data:", len(population_values))
    print("Highest population:", population_values.max())
    print("Lowest population:", population_values.min())
    print("Average population:", population_values.mean())
    print("============================================")


    fig, ax = plt.subplots(figsize=(14,10))
    merged.plot(column="Population", cmap="YlOrRd", edgecolor="black", linewidth=0.4, legend=False, missing_kwds={"color": "lightgrey", "label":"No population data"}, ax=ax)
# Add map scale bar
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    bar_length = 100000 # 100 kilometres
    x_start = x_min + (x_max - x_min) * 0.08
    y_start = y_min - (y_max - y_min) * 0.08
    ax.plot([x_start, x_start + bar_length], [y_start, y_start], color="black", linewidth=3)
    ax.text(x_start + bar_length / 2, y_start + (y_max - y_min) * 0.015, "100km", ha="center", fontsize=10)
    ax.set_title("Uganda District Population Thematic Map")
# Add North Arrow
    ax.annotate("N", xy=(0.93,0.95), xytext=(0.93,0.85), xycoords="axes fraction", arrowprops=dict(facecolor="black", width=3, headwidth=10), ha="center", va="center", fontsize=14, fontweight="bold")
    ax.set_axis_off()
# Create custom district population legend
    from matplotlib.patches import Patch
    from matplotlib.colors import Normalize
    legend_items = []
    valid_data = merged.dropna(subset=["Population"])
    norm = Normalize(vmin=valid_data["Population"].min(), vmax=valid_data["Population"].max())
    for idx, row in valid_data.iterrows():
        district_name = str(row["NAME"])
        population = row["Population"]
        district_color = plt.cm.YlOrRd(norm(population))

        legend_items.append(Patch(facecolor=district_color, edgecolor="black", label=f"{district_name}: {int(population):,}"))
    legend_items.append(Patch(facecolor="lightgrey", edgecolor="black", label="Other districts(not analyzed)"))
    ax.set_position([0.05,0.12,0.58,0.78])
    legend_ax = fig.add_axes([0.79,0.20,0.22,0.60])
    legend_ax.axis("off")
    legend_ax.legend(handles=legend_items, title="District / Population", loc="center left", fontsize=9, title_fontsize=11, frameon=True)
    frame = Rectangle((0,0), 1, 1, transform=fig.transFigure, fill=False, edgecolor="black", linewidth=2, zorder=1000)
    fig.add_artist(frame)
# Save thematic map as PNG
    plt.savefig("output/population_thematic_map.png", dpi=300, bbox_inches="tight")
# Export thematic map as PDF
    plt.savefig("output/population_thematic_map.pdf", format="pdf", bbox_inches="tight")
    plt.show()
statistical_data, boundaries = load_project_data()
if validate_project_data(statistical_data, boundaries):
    print("Project is ready for thematic map production!")
    create_thematic_map(statistical_data, boundaries)
else:
    print("Project data validation failed!")
# District population ranking
print("\nDISTRICT POPULATION RANKING")
print("===============================")
ranked_districts = statistical_data.sort_values(by="Population", ascending=False).reset_index(drop=True)
for index, row in ranked_districts.iterrows():
    print(f"{index + 1}.{row['District']} -" f"{row['Population']:,.0f}")
# MOST AND LEAST POPULATED DISTRICTS
most_populated = statistical_data.loc[statistical_data["Population"].idxmax()]
least_populated = statistical_data.loc[statistical_data["Population"].idxmin()]
print("\nPOPULATION EXTREMES")
print("======================")
print(f"Most populated district:" f"{most_populated['District']}" f"({most_populated['Population']:,.0f})")
print(f"Least populated district:" f"{least_populated['District']}" f"({least_populated['Population']:,.0f})")
# District population percentages
total_population = statistical_data["Population"].sum()
print("\nDISTRICT POPULATION PERCENTAGES")
print("===================================")
for index, row in statistical_data.iterrows():
    percentage = (row["Population"] / total_population) * 100
    print(f"{row['District']}: {percentage:.2f}%")
# Generate population analysis report
analysis_report = statistical_data.copy()
analysis_report["Population_Percentage"] = (analysis_report["Population"] / analysis_report["Population"].sum()) * 100
analysis_report["Population_Rank"] = (analysis_report["Population"].rank(method="min", ascending=False).astype(int))
analysis_report = analysis_report.sort_values(by="Population_Rank")
analysis_report.to_csv("district_population_analysis.csv", index=False)
print("\nPopulation analysis report generated successfully!")
print("File:district_population_analysis.csv")
# Population category classification
def classify_population(population):
    if population >= 1500000:
        return "High Population"
    elif population >= 700000:
        return "Medium Population"
    else:
        return "Low Population"
statistical_data["Population_Category"] = (statistical_data["Population"].apply(classify_population))
print("\nDISTRICT POPULATION CLASSIFICATION")
print("======================================")
for index, row in statistical_data.iterrows():
    print(f"{row['District']}:" f"{row['Population_Category']}")
# District population comparison chart
print("\nGenerating District Population Comparison Chart...")
plt.figure(figsize=(12,7))
plt.bar(statistical_data["District"], statistical_data["Population"])
plt.title("District Population Comparison")
plt.xlabel("Districts")
plt.ylabel("Population")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("output/district_population_chart.png")
plt.show()
print("Population comparison chart generated successfully!")
# Automatic PDF Report generation
print("\nGenerating Final Population Report...")
report_path = "output/District_Population_Final_Report.pdf"
with PdfPages(report_path) as pdf:
# Page 1: Statistical Summary
    fig, ax = plt.subplots(figsize=(14,10))
    ax.axis("off")
    fig.suptitle("DISTRICT POPULATION ANALYSIS REPORT", fontsize=20, fontweight="bold")
    total = statistical_data["Population"].sum()
    average = statistical_data["Population"].mean()
    ranked = statistical_data.sort_values(by="Population", ascending=False)
    summary = [f"Total Population: {total:,.0f}", f"Average Population: {average:,.0f}", f"Highest Population District: {ranked.iloc[0]['District']}", f"Lowest Population District: {ranked.iloc[-1]['District']}"]
    for i, item in enumerate(summary):
        ax.text(0.1,0.8 - i * 0.08, item, fontsize=13)
    table_data = [[row["District"], f"{row['Population']:,.0f}"] for _, row in ranked.iterrows()]
    ax.table(cellText=table_data, colLabels=["District", "Population"], cellLoc="center", loc="lower center", bbox=[0.1,0.05,0.8,0.35])
    pdf.savefig(fig)
    plt.close(fig)
# Page 2: Thematic Map
    map_image = plt.imread("output/population_thematic_map.png")
    fig, ax = plt.subplots(figsize=(11,8.5))
    ax.imshow(map_image)
    ax.axis("off")
    ax.set_title("DISTRICT POPULATION THEMATIC MAP")
    fig.text(0.5,0.02, "Coordinate Reference System: WGS84 (EPSG:4326)", ha="center", fontsize=9)
    pdf.savefig(fig)
    plt.close(fig)
# Page 3: Population Comparison Chart
    chart_image = plt.imread("output/district_population_chart.png")
    fig, ax = plt.subplots(figsize=(11,8.5))
    ax.imshow(chart_image)
    ax.axis('off')
    ax.set_title("DISTRICT POPULATION COMPARISON")
    pdf.savefig(fig)
    plt.close(fig)
# Page 4: Project Conclusions and recommendations
    fig, ax = plt.subplots(figsize=(11,8.5))
    ax.axis("off")
    ax.set_title("PROJECT CONCLUSIONS AND RECOMMENDATIONS", fontsize=17, fontweight="bold", pad=30)
    conclusions = ["PROJECT CONCLUSIONS", f"1. The total population of the selected districts" f"is{total:,.0f}.", f"2. The average district population is {average:,.0f}.", f"3. {ranked.iloc[0]['District']} has the highest" f"population.", f"4. {ranked.iloc[-1]['District']} has the lowest" f"population.", "RECOMMENDATIONS", "1. Use population data to guide public service planning.", "2. Consider population differences when allocating resources.", "3. Regularly update geographical and population data.", "4. Use thematic maps to support informed planning decisions."]
    for i, item in enumerate(conclusions):
        ax.text(0.05,0.90 - i * 0.085, item, fontsize=11, transform=ax.transAxes, wrap=True)
    pdf.savefig(fig)
    plt.close(fig)
print("Project conclusions page generated successfully!")
print("Complete PDF report generated successfully!")
print("Report saved at:", report_path)












