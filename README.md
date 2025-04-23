# Chicago H3 Geospatial Dashboard

This project aims to build an interactive dashboard using Python, Plotly, and H3 to visualize geospatial variables (like pollution or population density) for the city of Chicago as a hexagonal heatmap.

## Project Approach

1.  **Environment Setup:**
    *   Set up a Python environment (e.g., using `venv` or `conda`).
    *   Install necessary libraries: `plotly`, `dash` (for the dashboard), `h3-py`, `geopandas`, `pandas`, `shapely`.

2.  **Data Acquisition:**
    *   Obtain the boundary shapefile for the city of Chicago. (e.g., from the Chicago Data Portal).
    *   **(Initial Phase):** Generate random data associated with H3 hexagons within the Chicago boundary as a placeholder. Real data integration will follow.

3.  **Data Preprocessing:**
    *   Load the Chicago boundary shapefile using `geopandas`.
    *   Ensure all data uses a consistent Coordinate Reference System (CRS), likely WGS84 (EPSG:4326) for H3 compatibility.
    *   Data cleaning steps will apply when real data is integrated.

4.  **H3 Indexing:**
    *   Start with a fixed **H3 resolution of 8**. This can be made configurable later. (Average hexagon area: ~0.74 sq km).
    *   Use the Chicago boundary shapefile's geometry to find all H3 hexagons that cover the city area at the chosen resolution (`h3.polyfill`).

5.  **H3 Aggregation:**
    *   **(Initial Phase):** Assign randomly generated values to each H3 cell within the Chicago boundary.
    *   Store the results in a structure mapping H3 indexes to aggregated values (e.g., a Pandas DataFrame).

6.  **Visualization with Plotly:**
    *   Convert H3 hexagon boundaries to a format Plotly understands (e.g., GeoJSON). The `h3-py` library provides functions for this (`h3.h3_set_to_multi_polygon`).
    *   Create a Plotly figure (likely `plotly.graph_objects.Choroplethmapbox` or `plotly.express.choropleth_mapbox`).
    *   Map the aggregated data values to the hexagon colors.
    *   Configure map layout, color scales, tooltips (hover information).
    *   Select a suitable **basemap** (e.g., `'carto-positron'`, see notes below).

7.  **Dashboard Creation (Dash):**
    *   Set up a basic Dash application structure.
    *   Embed the Plotly H3 map visualization into the Dash layout.
    *   Add interactive components (e.g., dropdowns to select variables, sliders for H3 resolution, date pickers if applicable).
    *   **(Requirement):** Include controls to filter data based on demographic groups (e.g., total population, Hispanic population, African-American population) once real population data is integrated.
    *   Implement callbacks in Dash to update the map based on user interactions.

## Open Questions

*   **Data Sources:** **Deferred.** Initial development will use random data.
*   **H3 Resolution:** **Decision:** Start with resolution 8. Will be made configurable later.
*   **Dashboard Features:** **Clarification:** Demographic filtering is required. Other features TBD.
*   **Update Frequency:** **Clarification:** Real data will require daily updates. The initial build will be static.
*   **Basemap:** **Decision:** Start with `'carto-positron'`. See options below.

## Basemap Options (`mapbox_style` in Plotly)

*   `'carto-positron'`: Light, minimalist (Good default).
*   `'carto-darkmatter'`: Dark, minimalist.
*   `'open-street-map'`: Detailed street map.
*   `'stamen-terrain'`: Shows terrain/topography.
*   `'stamen-toner'`: High-contrast B&W.
*   `'stamen-watercolor'`: Artistic watercolor style.
*   Mapbox basic styles (`'basic'`, `'streets'`, `'light'`, `'dark'`, `'satellite'`, etc.): Require a Mapbox access token.
*   Custom Mapbox styles: Require a Mapbox access token and style URL.

## Potential Challenges & Pitfalls

*   **H3 Resolution Selection:** Too high a resolution can lead to performance issues (too many polygons for Plotly to render smoothly) and sparse data in many hexagons. Too low a resolution might oversimplify the spatial patterns.
*   **Plotly Performance:** Rendering a very large number of shapes (hexagons) in Plotly/Mapbox can be slow in the browser, especially with complex interactions. Data aggregation and potentially server-side rendering might be needed for very large datasets/high resolutions.
*   **Data Alignment:** Ensuring accurate spatial alignment between the Chicago boundary, the data points/areas, and the H3 grid is crucial. CRS issues are common pitfalls.
*   **Edge Cases:** How to handle data points exactly on hexagon boundaries? The `h3-py` library handles this, but understanding the assignment logic is important.
*   **Data Sparsity:** Some hexagons might have very little or no data, requiring careful handling in aggregation (e.g., assigning NaN, zero, or using imputation) and visualization (e.g., deciding whether to display empty hexagons).
*   **Dependencies:** Geospatial libraries can sometimes have complex dependencies. Using a package manager like `conda` can help manage this.
*   **H3 Limitations:** H3 is a global grid system. While excellent for aggregation and spatial indexing, the hexagons are not equal area (though the area difference is small within a limited region like a city). This is usually acceptable for visualization but should be noted.

This plan provides a roadmap. We can refine it as we answer the open questions and begin implementation. 