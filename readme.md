## Earthquake analytics

:earth_asia: :wavy_dash: :ocean: :electric_plug: :chart:

Simple earthquake stats / analytics app using [adasher](https://pypi.org/project/adasher/)

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

Might be helpful for exploring the early earthquake detection by submarine as mentioned in [using-subsea-cables-to-detect-earthquakes by google](https://cloud.google.com/blog/products/infrastructure/using-subsea-cables-to-detect-earthquakes)


Created using :sparkling_heart: [adasher](https://pypi.org/project/adasher/).
