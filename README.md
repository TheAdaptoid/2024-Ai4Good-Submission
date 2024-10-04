# 2024 AI 4 Good Submission: Adaptive Real Estate

## Team
- Marion Forrest | [GitHub](https://github.com/TheAdaptoid) | [LinkedIn](https://www.linkedin.com/in/marion-f-84232224b/)

## Problem Case: Rental Scams

Develop ways to identify, highlight, and flag rental listings by detecting nefarious actors using online
housing search sites to funnel people into a scamming pipeline. The goal is to limit financial damages
to the victims and the official landlords due to these scams while keeping users on the platform.

## What it does
Using a linear regression model in combination with some standard statistical analysis, I developed a web application that will automatically identify and flag suspicious rental listing as possible vectors of fraud.

## How I built it

### Backend

- **Data**: All the data for the listings on the webpage was sourced from the dataset provided for this problem case.

- **Fraud Detection**: A two prong approach was used to flag listings as fraudulent. The first was using the listing's price and the second was using the listing's move in date. 
    - **Pricing**: Using a linear regression the *difference* between a given listing's expected price and the actual price was calculated. The difference was then converted into a Z-Score, which was then used to flag listings as fraudulent if the Z Score fell below the mean of a 95% confidence interval for a given building type (condo, single family house, townhome, etc.).

    - **Move In Date**: If the time between the listing's move in date and the listing's listing date was less than the mean of a 95% confidence interval for a given building type, the listing was considered fraudulent.

    - **Fraud Detection Process Diagram**![Fraud Detection Process](.\Utils\Process.png)


### Frontend

- **UI Design**: The UI was made entirely using the [Nice-GUI](https://nicegui.io/documentation) python library. This library allowed me to quickly put together a ***nice*** and near fully functional webpage with out any knowledge or use of HTML, CSS, or JavaScript.

    - **Listing Page**![Listing Page](.\Utils\Listings_Page.png)

    - **Admin Page**![Admin Page](.\Utils\Admin_Page.png)

- **Images**: The images for the listings were sourced from various stock photo websites.

## Challenges I ran into

- **Time Management**: As a solo developer, managing my time wisely and effectively was a major challenge. Learing to limit my ambitous and project scope really helped me pull though and deliver on this project.

- **Limited Data**: A larger dataset with more instances would have certainly help improve model performance. And additional features for each listing would also have been nice and allowed for my final solution to be multi-modal.

## Accomplishments that we're proud of

I'm extremely proud to have been able to complete this project as a solo developer. The challenge was immense, and yet rewarding. But most importantly it was humbling. I now understand to true value of having teammates.