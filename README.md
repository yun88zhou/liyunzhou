# Bankside Rakaia Motorkhana Mavens (BRMM) Competition Event Web Application

## Overview

This web application is designed to manage drivers, cars, courses, and runs for a single competitive Motorkhana event organized by the BRMM car club. It provides interfaces for both drivers and administrators, streamlining event organization and data management.

## Features

### Driver Interface

1. **Home Dashboard**: Access the main dashboard after login.
2. **Driver List**: View all drivers and their car details, with junior drivers highlighted.
3. **Run Details**: Check individual driver's run statistics.
4. **Overall Results**: See rankings of drivers based on performance.
5. **Top 5 Drivers Graph**: Visualize the top-performing drivers.

### Administrator Interface

1. **Junior Driver Management**: List and manage junior drivers (aged 12-24).
2. **Driver Search**: Search for drivers by name with partial text matching.
3. **Run Management**: Edit and update run records for drivers or courses.
4. **Add New Driver**: Register new drivers and assign them to existing cars.
5. **Data Filtering**: Filter driver and run data based on various criteria.

## Technical Structure

- **Framework**: Flask
- **Database**: SQL (SQLite)
- **Front-end**: HTML, CSS (Bootstrap), JavaScript
- **Data Visualization**: Plotly for graphs

## Key Routes

- `/`: Login page
- `/home`: Main dashboard
- `/listdrivers`: List of all drivers
- `/rundetails`: Detailed run statistics
- `/listoverall`: Overall rankings
- `/admin/*`: Various admin functions (e.g., /admin/editruns, /admin/adddriverform)

## Installation and Setup

1. Clone the repository
2. Install required dependencies: `pip install -r requirements.txt`
3. Set up the database: Run the SQL scripts provided in the `database_setup` folder
4. Start the Flask server: `python app.py`

## Usage

1. Access the application through a web browser
2. Log in as a driver or administrator
3. Navigate through the interface using the provided links and buttons
4. Administrators should use the Admin link on the home page to access management features

## Security Considerations

- Different routes for drivers and administrators to ensure data integrity and privacy
- Input validation to prevent data corruption
- Session management for secure login/logout

## Assumptions and Design Decisions

- Age-based form adaptations for new driver registration
- Comprehensive run editing capabilities (by course and by driver name)
- Modal dialog for adding new drivers with age confirmation
- Automatic creation of blank runs for new drivers

## Database Structure

The application uses a relational database with tables for drivers, cars, courses, and runs. Key relationships include:

- Cars linked to drivers via foreign key
- Runs associated with specific drivers and courses

## Future Enhancements

- Implement user authentication for increased security
- Expand data visualization options
- Add export functionality for event results

## Contributing

Contributions to improve the application are welcome. Please follow the standard fork-and-pull request workflow.

## License

[LU Assignment.]
