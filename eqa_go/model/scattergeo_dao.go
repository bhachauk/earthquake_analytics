package model

type ScatterGeo struct {
	Type   string     `json:"type"`
	Mode   string     `json:"mode,omitempty"`
	Lat    []float64  `json:"lat"`
	Lon    []float64  `json:"lon"`
	Marker *GeoMarker `json:"marker,omitempty"`
	Text   []string   `json:"text,omitempty"`
}

type GeoMarker struct {
	Size       interface{} `json:"size,omitempty"`  // Can be a single number or an array
	Color      interface{} `json:"color,omitempty"` // Can be a single color or an array
	Colorscale string      `json:"colorscale,omitempty"`
	Colorbar   *Colorbar   `json:"colorbar,omitempty"`
}

type Colorbar struct {
	Title string `json:"title,omitempty"`
}

type GeoLayout struct {
	Title interface{} `json:"title"`
	Geo   GeoConfig   `json:"geo"`
	//    plot_bgcolor: 'rgb(240, 240, 240)', // Light gray plot area background
	//    paper_bgcolor: 'rgb(255, 255, 255)',
	PlotBgColor  string `json:"plot_bgcolor,omitempty"`
	PaperBgColor string `json:"paper_bgcolor,omitempty"`
}

type GeoConfig struct {
	Scope        string        `json:"scope,omitempty"`
	Projection   GeoProjection `json:"projection,omitempty"`
	ShowLand     bool          `json:"showland,omitempty"`
	LandColor    string        `json:"landcolor,omitempty"`
	SubunitColor string        `json:"subunitcolor,omitempty"`
	CountryColor string        `json:"countrycolor,omitempty"`
	ShowOcean    bool          `json:"showocean,omitempty"`
	OceanColor   string        `json:"oceancolor,omitempty"`
	Lataxis      *AxisConfig   `json:"lataxis,omitempty"`
	Lonaxis      *AxisConfig   `json:"lonaxis,omitempty"`
}

type GeoProjection struct {
	Type     string       `json:"type,omitempty"`
	Rotation *GeoRotation `json:"rotation,omitempty"`
	Scale    float64      `json:"scale,omitempty"`
}

type GeoRotation struct {
	Lon float64 `json:"lon,omitempty"`
	Lat float64 `json:"lat,omitempty"`
}

type ScatterGeoJSON struct {
	Data   []ScatterGeo `json:"data"`
	Layout GeoLayout    `json:"layout"`
}
