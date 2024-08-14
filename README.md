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

## Key Findings

- Significant speed differences between Green Line B and Orange Line.
- Variations in operational efficiency, dwell times, and headway consistency between lines.
- Seasonal patterns affecting average speeds.
- Recent improvements in speed and dwell times for both lines.

## Recommendations

1. Infrastructure improvements for slower lines.
2. Operational adjustments to reduce dwell times.
3. Enhanced scheduling strategies for more consistent service.
4. Seasonal adjustments to counteract weather-related slowdowns.

## Future Work

- Developing predictive models for delays and service disruptions.
- Conducting user experience studies.
- Integrating real-time transit data into broader urban planning initiatives.
- Performing longitudinal analysis to assess the impact of implemented recommendations.

## Acknowledgments

- MBTA for providing the API and data
- TransitMatters for inspiration and resources
- Plotly team for the Dash framework

For more detailed information, please refer to the full paper in the `docs/` directory.
