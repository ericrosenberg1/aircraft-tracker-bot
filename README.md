# Aircraft Flight Tracker Bot

## What is the Aicraft Flight Tracker Bot?

The Aircraft Tracker Bot is a Python application first designed to monitor and post updates about Boeing 747 flights worldwide. Utilizing data from the OpenSky Network's public API, this bot identifies when a Boeing 747 takes off or lands and shares this information on various social media platforms. Ideal for aviation enthusiasts, the tool aims to provide timely and interesting flight updates to its audience.

## Who created the Aircraft Tracker Bot?

This project was developed by Eric Rosenberg, on Github as @ericrosenberg1, an aviation enthusiast and software developer passionate about combining technology with aviation to create engaging and informative tools for the aviation community.

## What's the purpose of the project?

The initial purpose of the 747 Flight Tracker Bot is to serve the aviation enthusiast community by providing real-time updates on Boeing 747 flights. Whether for educational purposes, tracking specific flights, or simply for the love of aviation, this bot aims to deliver relevant and interesting content to its users. Based on community contributions, it can expand to cover other aircraft and data.

In addition to its primary function, the project also demonstrates the practical application of Python programming, API integration, and social media automation. It serves as a valuable tool for those looking to explore these areas further.

## Features

- Real-time tracking of Boeing 747 flights worldwide.
- Automated postings to multiple social media platforms.
- Filtering and avoidance of duplicate postings.
- Easy customization and scalability for future enhancements.

## Code Quality
[![Maintainability](https://api.codeclimate.com/v1/badges/de8f28557e1be8d7062e/maintainability)](https://codeclimate.com/github/ericrosenberg1/747-Tracker-Bot/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/de8f28557e1be8d7062e/test_coverage)](https://codeclimate.com/github/ericrosenberg1/747-Tracker-Bot/test_coverage)

## How to Use

Please refer to the [Installation](#installation) and [Usage](#usage) sections for detailed instructions on setting up and using the 747 Flight Tracker Bot.

## Installation

This app is currently only suitable for users comfortable with the command line. It requires installing a recent version of Python.
1. Clone the project to your desired directory. Use CD to go to that directory.
2. Run pip install -r requirements.txt.
3. Rename config-example.py to config.py.
4. Update config.py with your credentials for https://opensky-network.org.
5. Sign up for the X 2.0 API (formerly Twitter). Get your keys and add them to twitter_config.py.
6. Run python update_aircraft_db.py to generate a database of aircraft. Run python main.py to run the app.
7. Set up a cron job to update the aircraft list monthly and keep main.py running as desired.

## Usage

When connected to your desired social media accounts and running, it will automatically share aircraft details, such as in a Tweet.

## Contributing

I welcome contributions and suggestions! You can join the project, submit a pull request, or join as a regular contribution.
The biggest goals for the project for the future include these features:
- Simpler installation and setup for people without code knowledge
- A web GUI to run and manage the app
- More social networks
- The ability to change the aircraft based on several inputs, such as aircraft type, airport, or airline

## License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Acknowledgments

- OpenSky Network for providing the aircraft flight data.
- The Python community for the excellent documentation and libraries that made this project possible.
- Claude and ChatGPT for speeding up development and improving my code
- Codacy, Snyk, and Code Climate for automatic reviews.
