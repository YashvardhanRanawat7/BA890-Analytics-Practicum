# MBTA Transit Data Pipeline and Analytical Dashboard

## Business Problem

This project addresses a common frustration faced by users of the Massachusetts Bay Transportation Authority (MBTA) system in Boston: the uncertainty surrounding train and bus timings and delays. Many MBTA riders struggle with unreliable service information, leading to unnecessary wait times, missed connections, and general inconvenience.

The core problem we're tackling is the lack of easily accessible, accurate, and up-to-date information on MBTA's performance. This project aims to develop a solution that provides MBTA users with the information they need to navigate the system more effectively, ultimately improving their transit experience.

## Importance of the Problem

- **Economic Impact**: Transit delays lead to lost productivity and increased operational costs for businesses.
- **Recent Service Disruptions**: Frequent shutdowns and service disruptions have eroded public trust in the system's reliability.
- **Environmental Considerations**: Unreliable public transit can drive commuters towards more carbon-intensive modes of transportation.
- **Urban Development and Planning**: Transit reliability significantly impacts urban development patterns and property values.

## Data Sources

1. **Subway Performance Data**: Detailed information about each trip and stop for MBTA's rail service.
2. **GTFS (General Transit Feed Specification) Data**: Standardized format for public transportation schedules and associated geographic information.

## Methodology

1. **Data Ingestion**: Used Apache Airflow for daily scheduled tasks to fetch performance data from the MBTA API.
2. **Data Storage**: Utilized AWS S3 and Snowflake for scalable data storage and warehousing.
3. **Data Transformation**: Implemented dbt (data build tool) for processing raw data in Snowflake.
4. **Data Visualization**: Created interactive visualizations and dashboards using Plotly's Dash framework.


## Acknowledgments

- MBTA for providing the API and data
- TransitMatters for inspiration and resources
- Plotly team for the Dash framework
