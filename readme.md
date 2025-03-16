<h1><img src="./eqa_fe/public/white_beard_icon.png" width="50px"/> Earthquake analytics</h1>

:earth_asia: :wavy_dash: :ocean: :electric_plug: :chart:

- Backend API deployed using Vercel - [https://earthquake-analytics.vercel.app/](https://earthquake-analytics.vercel.app/)
- Frontend deployed using Github pages - [https://bhachauk.github.io/earthquake_analytics/](https://bhachauk.github.io/earthquake_analytics/)

**Features (Migration Work in progress)**


| Todo                                            | Status  |
|:------------------------------------------------|:--------|
| Backend API for charts                          | &check; |
| Reactjs frontend analytics                      | &check; |
| Backend API for submarine cables and earthquake | &cross; |
| Reactjs frontend for cables and area charts     | &cross; |

Deprecated - Python application
----

Simple earthquake stats / analytics app using [adasher](https://pypi.org/project/adasher/)

![Demo](eq_analytics.gif)

### Analytics

- [x] Area
    > Collection of earthquake stats from the geologically divided rectangle areas (step sizes lat: 20, lon: 10)
- [ ] Submarine-1
    > Earthquakes with nearby (within 2000 km) submarine optical cables stats collection.
- [x] Submarine-2
    > Search recent earthquakes and nearby submarine cable details.

### Data

- Earthquake data fetched from [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/) Data range : (90 days)
- Submarine optical cables data fetched from [telegeography/www.submarinecablemap.com](https://github.com/telegeography/www.submarinecablemap.com)
  under [Creative Commons License: Attribution-NonCommercial-ShareAlike 3.0 Unported (CC BY-NC-SA 3.0)](https://creativecommons.org/licenses/by-nc-sa/3.0/)
  

**Why submarine optical cables ?**

Might be helpful for exploring the early earthquake detection by submarine optical cables as mentioned here : [using-subsea-cables-to-detect-earthquakes by google](https://cloud.google.com/blog/products/infrastructure/using-subsea-cables-to-detect-earthquakes)


Created using :sparkling_heart: [adasher](https://pypi.org/project/adasher/).
